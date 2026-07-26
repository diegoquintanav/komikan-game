"""Tests for idempotency and race-condition-like scenarios on move submission.

ALMUD-262: Verifies that duplicate moves, invalid moves, and game-over
states are handled correctly without corrupting game state.
"""

import uuid

from komikan.api.game_manager import GameManager


class TestDuplicateMoveSubmission:
    """Verify that submitting the same move twice does not corrupt state."""

    def test_same_move_twice_second_rejected(self):
        """Make a valid move, then try the exact same move again.
        Second attempt should fail because the token moved."""
        manager = GameManager()
        game = manager.create_game()

        success1, _ = game.make_move(2, 0, 2, 1)
        assert success1, "First move should succeed"

        success2, _ = game.make_move(2, 0, 2, 1)
        assert not success2, "Duplicate move should be rejected"

    def test_same_move_does_not_double_count(self):
        """Make a valid move, try the same move again.
        move_count should remain 1."""
        manager = GameManager()
        game = manager.create_game()

        game.make_move(2, 0, 2, 1)
        game.make_move(2, 0, 2, 1)

        assert game.to_api_model().move_count == 1

    def test_same_move_does_not_switch_turn_twice(self):
        """Make a valid move, try the same move.
        Current player should still be South after the failed duplicate."""
        manager = GameManager()
        game = manager.create_game()

        game.make_move(2, 0, 2, 1)
        game.make_move(2, 0, 2, 1)

        assert game.get_current_player_side().value == "pu trewa"

    def test_same_move_does_not_record_duplicate_history(self):
        """Make a valid move, try the same move.
        move_history should contain exactly 1 entry."""
        manager = GameManager()
        game = manager.create_game()

        game.make_move(2, 0, 2, 1)
        game.make_move(2, 0, 2, 1)

        assert len(game.move_history) == 1


class TestInvalidMoveThenValidMove:
    """Verify that an invalid move does not corrupt state before a valid move."""

    def test_invalid_then_valid_same_turn(self):
        """Try moving an opponent's token, then make a valid move.
        The invalid attempt should not prevent the valid move."""
        manager = GameManager()
        game = manager.create_game()

        invalid_success, _ = game.make_move(0, 5, 1, 5)
        assert not invalid_success, "Moving opponent's token should fail"

        valid_success, _ = game.make_move(2, 0, 2, 1)
        assert valid_success, "Valid move should succeed after invalid attempt"

    def test_invalid_move_does_not_corrupt_board(self):
        """Try an invalid move, verify board state is unchanged."""
        manager = GameManager()
        game = manager.create_game()

        north_before = list(game.core_state.player_north.positions)
        south_before = list(game.core_state.player_south.positions)

        game.make_move(0, 5, 1, 5)

        assert list(game.core_state.player_north.positions) == north_before
        assert list(game.core_state.player_south.positions) == south_before

    def test_invalid_move_does_not_corrupt_positions(self):
        """Try an invalid move, verify player positions lists are unchanged."""
        manager = GameManager()
        game = manager.create_game()

        north_before = list(game.core_state.player_north.positions)
        south_before = list(game.core_state.player_south.positions)

        game.make_move(0, 5, 1, 5)

        assert game.core_state.player_north.positions == north_before
        assert game.core_state.player_south.positions == south_before

    def test_invalid_move_does_not_affect_move_history(self):
        """Try an invalid move, verify move_history remains empty."""
        manager = GameManager()
        game = manager.create_game()

        game.make_move(0, 5, 1, 5)

        assert len(game.move_history) == 0


class TestDeleteGameIdempotency:
    """Verify delete operations are idempotent and leave no stale state."""

    def test_delete_twice_no_crash(self):
        """Delete a game, then delete it again.
        Second call should return False without raising."""
        manager = GameManager()
        game = manager.create_game()
        game_id = game.game_id

        assert manager.delete_game(game_id) is True
        assert manager.delete_game(game_id) is False

    def test_delete_nonexistent_game(self):
        """Try to delete a game with a random UUID.
        Should return False."""
        manager = GameManager()
        assert manager.delete_game(str(uuid.uuid4())) is False

    def test_delete_after_moves(self):
        """Make several moves, then delete the game.
        Should succeed cleanly."""
        manager = GameManager()
        game = manager.create_game()

        game.make_move(2, 0, 2, 1)
        game.make_move(0, 5, 1, 5)
        game.make_move(2, 1, 2, 2)

        assert manager.delete_game(game.game_id) is True
        assert manager.get_game(game.game_id) is None

    def test_create_after_delete_reuses_no_state(self):
        """Create game A, make moves, delete it, create game B.
        Game B should have default starting positions, not game A's state."""
        manager = GameManager()
        game_a = manager.create_game()
        game_a.make_move(2, 0, 2, 1)
        game_a.make_move(0, 5, 1, 5)

        manager.delete_game(game_a.game_id)
        game_b = manager.create_game()

        assert (2, 0) in game_b.core_state.player_north.positions
        assert len(game_b.core_state.player_south.positions) == 12
        assert len(game_b.move_history) == 0
        assert game_b.to_api_model().move_count == 0


class TestMoveAfterGameOver:
    """Verify that moves are rejected when the game has already ended."""

    def test_move_after_north_win_rejected(self):
        """Play to a North win (reduce south tokens to 4), then try to move.
        Should fail because the turn switched and the token belongs to the
        wrong player."""
        manager = GameManager()
        game = manager.create_custom_game(
            north_positions=[(2, 0)],
            south_positions=[(2, 1), (3, 1), (1, 2), (3, 2), (2, 3)],
        )

        success, _ = game.make_move(2, 0, 2, 2)
        assert success, "Capture should succeed"
        assert game.status.value == "north_won"

        result, _ = game.make_move(2, 2, 2, 3)
        assert not result, "Move after game over should be rejected"

    def test_move_after_south_win_rejected(self):
        """Play to a South win (trap Pangui so North has no valid moves),
        then try to move. Should fail because the turn switched."""
        manager = GameManager()
        game = manager.create_custom_game(
            north_positions=[(2, 0)],
            south_positions=[
                (1, 0), (3, 0), (2, 1),
                (0, 0), (4, 0), (2, 2), (2, 3),
            ],
            starting_player="pu trewa",
        )

        success, _ = game.make_move(2, 3, 3, 3)
        assert success, "South's move should succeed"
        assert game.status.value == "south_won"

        result, _ = game.make_move(1, 0, 0, 1)
        assert not result, "Move after game over should be rejected"

    def test_board_state_unchanged_after_failed_move(self):
        """After game over, a rejected move should not alter board state."""
        manager = GameManager()
        game = manager.create_custom_game(
            north_positions=[(2, 0)],
            south_positions=[(2, 1), (3, 1), (1, 2), (3, 2), (2, 3)],
        )

        game.make_move(2, 0, 2, 2)
        assert game.status.value == "north_won"

        north_before = list(game.core_state.player_north.positions)
        south_before = list(game.core_state.player_south.positions)

        game.make_move(2, 2, 2, 3)

        assert list(game.core_state.player_north.positions) == north_before
        assert list(game.core_state.player_south.positions) == south_before


class TestPositionListConsistency:
    """Verify position lists stay consistent after moves."""

    def test_positions_consistent_after_valid_move(self):
        """After a valid move, from_position is removed and to_position added."""
        manager = GameManager()
        game = manager.create_game()

        game.make_move(2, 0, 2, 1)

        north_positions = game.core_state.player_north.positions
        assert (2, 0) not in north_positions
        assert (2, 1) in north_positions

    def test_positions_list_length_after_move(self):
        """Positions list length should remain unchanged after a move."""
        manager = GameManager()
        game = manager.create_game()

        north_len_before = len(game.core_state.player_north.positions)
        game.make_move(2, 0, 2, 1)

        assert len(game.core_state.player_north.positions) == north_len_before

    def test_south_positions_unchanged_after_north_move(self):
        """South player's positions should be untouched by a North move."""
        manager = GameManager()
        game = manager.create_game()

        south_before = list(game.core_state.player_south.positions)
        game.make_move(2, 0, 2, 1)

        assert list(game.core_state.player_south.positions) == south_before

    def test_north_positions_unchanged_after_south_move(self):
        """North player's positions should be untouched by a South move."""
        manager = GameManager()
        game = manager.create_game()

        game.make_move(2, 0, 2, 1)
        north_before = list(game.core_state.player_north.positions)

        game.make_move(0, 5, 1, 5)

        assert list(game.core_state.player_north.positions) == north_before
