"""
Tests for turn order mechanics in the Komikan game.

Covers: ALMUD-259 — turn order bug tests
Validates that North (Pangui) always goes first, players alternate turns,
and turn switching works correctly through both GameState and the GameInstance API.
"""

from komikan.api.game_manager import GameManager
from komikan.api.models import PlayerSideModel
from komikan.player import PlayerSide, GameState


class TestInitialTurnOrder:
    """Verify that the initial game state sets North as the first player."""

    def test_north_goes_first(self):
        """A new GameState must have North (Pangui) as the current player."""
        state = GameState()
        assert state.current_player.side == PlayerSide.NORTH

    def test_switch_turn_changes_player(self):
        """After one switch_turn(), the current player must be South."""
        state = GameState()
        state.switch_turn()
        assert state.current_player.side == PlayerSide.SOUTH

    def test_double_switch_restores_original(self):
        """Two consecutive switch_turn() calls must return to North."""
        state = GameState()
        state.switch_turn()
        state.switch_turn()
        assert state.current_player.side == PlayerSide.NORTH


class TestMakeMoveTurnEnforcement:
    """Verify that GameInstance.make_move enforces correct turn order."""

    def test_make_move_validates_current_player(self):
        """Moving a South token on North's turn must fail."""
        manager = GameManager()
        game = manager.create_game()

        south_token = game.core_state.player_south.positions[0]
        from_x, from_y = south_token

        # Determine a valid target for this South token
        adjacent = game.board.get_adjacent_positions(from_x, from_y)
        to_x, to_y = next(
            (ax, ay)
            for ax, ay in adjacent
            if game.board.is_valid_move(from_x, from_y, ax, ay)
        )

        success, record = game.make_move(from_x, from_y, to_x, to_y)

        assert success is False
        assert record is None
        assert game.get_current_player_side() == PlayerSideModel.NORTH

    def test_make_move_switches_turn_after_success(self):
        """A valid move must switch the turn to the other player."""
        manager = GameManager()
        game = manager.create_game()

        # North (2, 0) → (2, 1)
        success, record = game.make_move(2, 0, 2, 1)

        assert success is True
        assert record is not None
        assert game.get_current_player_side() == PlayerSideModel.SOUTH

    def test_make_move_does_not_switch_on_failure(self):
        """An invalid move must leave the current player unchanged."""
        manager = GameManager()
        game = manager.create_game()

        # (0, 0) is empty — no token there
        success, record = game.make_move(0, 0, 0, 1)

        assert success is False
        assert record is None
        assert game.get_current_player_side() == PlayerSideModel.NORTH

    def test_alternating_turns_sequence(self):
        """Four valid moves must alternate N→S→N→S."""
        manager = GameManager()
        game = manager.create_game()

        # 1. North (2,0) → (2,1)
        ok, _ = game.make_move(2, 0, 2, 1)
        assert ok
        assert game.get_current_player_side() == PlayerSideModel.SOUTH

        # 2. South (0,5) → (0,4)
        ok, _ = game.make_move(0, 5, 0, 4)
        assert ok
        assert game.get_current_player_side() == PlayerSideModel.NORTH

        # 3. North (2,1) → (2,2)
        ok, _ = game.make_move(2, 1, 2, 2)
        assert ok
        assert game.get_current_player_side() == PlayerSideModel.SOUTH

        # 4. South (0,4) → (0,3)
        ok, _ = game.make_move(0, 4, 0, 3)
        assert ok
        assert game.get_current_player_side() == PlayerSideModel.NORTH


class TestTurnOrderAfterCapture:
    """Verify that turn order holds after capture moves."""

    def test_turn_switches_after_capture(self):
        """After North captures a South token, the turn must switch to South."""
        manager = GameManager()
        game = manager.create_custom_game(
            north_positions=[(2, 2)],
            south_positions=[(2, 3)],
        )

        # North captures (2,2) → (2,4), jumping over (2,3)
        success, record = game.make_move(2, 2, 2, 4)

        assert success is True
        assert record.is_capture is True
        assert game.get_current_player_side() == PlayerSideModel.SOUTH

    def test_south_can_move_after_north_capture(self):
        """South must be able to move after North completes a capture."""
        manager = GameManager()
        game = manager.create_custom_game(
            north_positions=[(2, 2)],
            south_positions=[(2, 3), (0, 5)],
        )

        # North captures (2,2) → (2,4)
        ok, _ = game.make_move(2, 2, 2, 4)
        assert ok
        assert game.get_current_player_side() == PlayerSideModel.SOUTH

        # South (0,5) → (0,4)
        ok, _ = game.make_move(0, 5, 0, 4)
        assert ok
        assert game.get_current_player_side() == PlayerSideModel.NORTH


class TestTurnOrderWithAPI:
    """Verify turn order enforcement through the GameInstance / GameManager API layer."""

    def test_api_enforces_turn_order(self):
        """The API must reject a move that uses the wrong player's token."""
        manager = GameManager()
        game = manager.create_game()

        # Try to move a South token on North's first turn
        south_pos = game.core_state.player_south.positions[0]
        sx, sy = south_pos
        adjacent = game.board.get_adjacent_positions(sx, sy)
        tx, ty = next(
            (ax, ay)
            for ax, ay in adjacent
            if game.board.is_valid_move(sx, sy, ax, ay)
        )

        success, _ = game.make_move(sx, sy, tx, ty)

        assert success is False
        model = game.to_api_model()
        assert model.current_player == PlayerSideModel.NORTH

    def test_api_move_switches_turn(self):
        """A successful API move must be reflected in the game state model."""
        manager = GameManager()
        game = manager.create_game()

        ok, _ = game.make_move(2, 0, 2, 1)
        assert ok

        model = game.to_api_model()
        assert model.current_player == PlayerSideModel.SOUTH
        assert model.move_count == 1

    def test_api_cannot_move_same_player_twice(self):
        """Two consecutive moves by the same player must fail on the second attempt."""
        manager = GameManager()
        game = manager.create_game()

        # First move — North (2,0) → (2,1) — succeeds
        ok1, _ = game.make_move(2, 0, 2, 1)
        assert ok1
        assert game.get_current_player_side() == PlayerSideModel.SOUTH

        # Second move — try North (1,0) → (1,1) — must fail (now South's turn)
        # (1,0) is not a North position after the move; only (2,1) is North's position now
        ok2, _ = game.make_move(1, 0, 1, 1)
        assert ok2 is False
        assert game.get_current_player_side() == PlayerSideModel.SOUTH
