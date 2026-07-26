"""Tests for ALMUD-258: Win condition bug tests.

Validates the three win conditions in GameInstance._check_win_condition():
  1. North wins by capturing South tokens down to <= 4
  2. South wins by trapping Pangui (no valid moves or captures)
  3. Stalemate when South has no valid moves on South's turn

Also tests priority ordering and that win checks happen after turn switches.
"""

from komikan.api.game_manager import GameManager
from komikan.api.models import GameStatus
from komikan.player import PlayerSide


class TestNorthWinByCapture:
    """North wins by reducing South tokens to the capture threshold (<= 4)."""

    def test_north_wins_when_south_has_4_tokens(self):
        """Exactly 4 remaining South tokens triggers NORTH_WON."""
        gm = GameManager()
        game = gm.create_custom_game(
            north_positions=[(2, 0)],
            south_positions=[(0, 5), (4, 5), (0, 6), (4, 6)],
        )
        assert len(game.core_state.player_south.positions) == 4
        assert game._check_win_condition() == GameStatus.NORTH_WON

    def test_north_does_not_win_when_south_has_5_tokens(self):
        """5 remaining South tokens keeps the game ACTIVE."""
        gm = GameManager()
        game = gm.create_custom_game(
            north_positions=[(2, 0)],
            south_positions=[(0, 5), (4, 5), (0, 6), (4, 6), (2, 6)],
        )
        assert len(game.core_state.player_south.positions) == 5
        assert game._check_win_condition() == GameStatus.ACTIVE

    def test_north_wins_exact_threshold(self):
        """Capture that brings South to exactly 4 tokens triggers NORTH_WON."""
        gm = GameManager()
        game = gm.create_custom_game(
            north_positions=[(2, 4)],
            south_positions=[(2, 5), (0, 7), (1, 7), (2, 7), (3, 7)],
        )
        assert game.status == GameStatus.ACTIVE
        assert len(game.core_state.player_south.positions) == 5

        success, record = game.make_move(2, 4, 2, 6)
        assert success
        assert record.is_capture
        assert len(game.core_state.player_south.positions) == 4
        assert game.status == GameStatus.NORTH_WON

    def test_north_wins_below_threshold(self):
        """3 remaining South tokens (below threshold) also triggers NORTH_WON."""
        gm = GameManager()
        game = gm.create_custom_game(
            north_positions=[(2, 0)],
            south_positions=[(0, 5), (4, 5), (0, 6)],
        )
        assert len(game.core_state.player_south.positions) == 3
        assert game._check_win_condition() == GameStatus.NORTH_WON


class TestSouthWinByTrapping:
    """South wins when Pangui has no valid moves or captures available."""

    def test_south_wins_when_north_has_no_valid_moves(self):
        """Pangui at (2,0) surrounded by South tokens and disabled diagonals — SOUTH_WON.

        Board layout at rows 0-2:
          S . S . S      row 0: South at (0,0), (1,0), (2,1), (3,0), (4,0)
          . . N . .      row 1: North at (2,0)
          . . S . .      row 2: South at (2,2)

        Disabled diagonals from (2,0): paths to (1,1) and (3,1) are blocked.
        All remaining adjacent nodes occupied or blocked by captures.
        """
        gm = GameManager()
        game = gm.create_custom_game(
            north_positions=[(2, 0)],
            south_positions=[(1, 0), (3, 0), (2, 1), (0, 0), (4, 0), (2, 2)],
        )
        assert not game._has_valid_moves(game.core_state.player_north)
        assert game._check_win_condition() == GameStatus.SOUTH_WON

    def test_south_does_not_win_when_north_has_moves(self):
        """Pangui at (2,0) with an open path to (2,1) — game remains ACTIVE.

        South has 5 tokens (> 4) so the capture threshold doesn't fire.
        Pangui can move to (2,1), so the trapping branch doesn't fire either.
        """
        gm = GameManager()
        game = gm.create_custom_game(
            north_positions=[(2, 0)],
            south_positions=[(1, 0), (3, 0), (2, 2), (0, 5), (4, 5)],
        )
        assert len(game.core_state.player_south.positions) == 5
        assert game._has_valid_moves(game.core_state.player_north)
        assert game._check_win_condition() == GameStatus.ACTIVE


class TestStalemate:
    """Stalemate when South cannot move on their turn."""

    def test_stalemate_when_south_has_no_valid_moves(self):
        """South tokens trapped in top-left corner with no valid moves — STALEMATE.

        Disabled paths trap (0,0) so it cannot move.
        (0,1) and (1,1) could move to (1,2) — blocked by North at (1,2).
        (1,1) and (2,0) could move to (2,1) — blocked by North at (2,1).
        (2,0) could move to (3,0) — blocked by North at (3,0).
        (1,0) is completely surrounded by South tokens on all reachable sides.

        Board (rows 0-2):
          S S . . .      row 0: South at (0,0), (1,0), (2,0)
          S S N . .      row 1: South at (0,1), (1,1); North at (2,1)
          . N . . .      row 2: North at (1,2)
          N . . . .      row 3: North at (3,0)

        Starting player: South (pu trewa).
        """
        gm = GameManager()
        game = gm.create_custom_game(
            north_positions=[(1, 2), (2, 1), (3, 0)],
            south_positions=[(0, 0), (1, 0), (0, 1), (1, 1), (2, 0)],
            starting_player="pu trewa",
        )
        assert game.core_state.current_player.side == PlayerSide.SOUTH
        assert len(game.core_state.player_south.positions) == 5
        assert game._check_win_condition() == GameStatus.STALEMATE

    def test_no_stalemate_on_north_turn(self):
        """North trapped on North's turn is SOUTH_WON, not stalemate.

        Same trapping setup as TestSouthWinByTrapping but explicitly verifies
        that the stalemate branch (which only fires on South's turn) is not
        the cause — it is the no-valid-moves branch for North.
        """
        gm = GameManager()
        game = gm.create_custom_game(
            north_positions=[(2, 0)],
            south_positions=[(1, 0), (3, 0), (2, 1), (0, 0), (4, 0), (2, 2)],
            starting_player="pangui",
        )
        assert game.core_state.current_player.side == PlayerSide.NORTH
        assert game._check_win_condition() == GameStatus.SOUTH_WON


class TestWinConditionOrder:
    """Priority: capture threshold > North trapped > South stalemate > ACTIVE."""

    def test_capture_threshold_checked_before_no_valid_moves(self):
        """South has 3 tokens (<= 4) AND North is trapped — NORTH_WON wins.

        North at (0,0) is surrounded: (1,0) and (0,1) occupied by South,
        (2,0) blocks the only capture landing.  Disabled diagonal (0,0)-(1,1)
        removes the third escape.  Both conditions are true but the threshold
        branch fires first and returns NORTH_WON.
        """
        gm = GameManager()
        game = gm.create_custom_game(
            north_positions=[(0, 0)],
            south_positions=[(1, 0), (0, 1), (2, 0)],
        )
        assert len(game.core_state.player_south.positions) == 3
        assert not game._has_valid_moves(game.core_state.player_north)
        assert game._check_win_condition() == GameStatus.NORTH_WON

    def test_win_check_happens_after_turn_switch(self):
        """make_move switches the turn before checking the win condition.

        North captures (2,5) → turn switches to South → win condition
        sees 4 South tokens and sets status to NORTH_WON.
        """
        gm = GameManager()
        game = gm.create_custom_game(
            north_positions=[(2, 4)],
            south_positions=[(2, 5), (0, 7), (1, 7), (2, 7), (3, 7)],
        )
        assert game.status == GameStatus.ACTIVE

        success, record = game.make_move(2, 4, 2, 6)
        assert success

        # Turn switched to South after North's move
        assert game.core_state.current_player.side == PlayerSide.SOUTH
        # Win condition evaluated post-switch
        assert game.status == GameStatus.NORTH_WON


class TestWinConditionWithCustomGame:
    """End-to-end win checks through the GameManager custom-game API."""

    def test_custom_game_can_reach_win(self):
        """Create a 5-token game, make a capture, verify NORTH_WON via make_move."""
        gm = GameManager()
        game = gm.create_custom_game(
            north_positions=[(2, 4)],
            south_positions=[(2, 5), (0, 7), (1, 7), (2, 7), (3, 7)],
        )
        assert game.status == GameStatus.ACTIVE
        assert len(game.core_state.player_south.positions) == 5

        success, _ = game.make_move(2, 4, 2, 6)
        assert success
        assert game.status == GameStatus.NORTH_WON

    def test_custom_game_no_immediate_win(self):
        """Custom game with 5 south tokens — status stays ACTIVE without moves."""
        gm = GameManager()
        game = gm.create_custom_game(
            north_positions=[(2, 0)],
            south_positions=[(0, 5), (4, 5), (0, 6), (4, 6), (2, 6)],
        )
        assert game.status == GameStatus.ACTIVE
        assert len(game.core_state.player_south.positions) == 5
        assert len(game.move_history) == 0
