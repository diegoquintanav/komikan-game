"""Tests for multi-game concurrency and state isolation (ALMUD-261).

Verifies that GameManager stores independent GameInstance objects and that
mutations in one game never leak into another.
"""

from komikan.api.game_manager import GameManager, GameInstance
from komikan.api.models import GameStatus


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _standard_game(manager: GameManager) -> GameInstance:
    """Create a standard game and return it."""
    return manager.create_game()


def _custom_game(
    manager: GameManager,
    north: list[tuple[int, int]],
    south: list[tuple[int, int]],
    starting: str = "pangui",
) -> GameInstance:
    """Create a custom game with explicit positions."""
    return manager.create_custom_game(north, south, starting_player=starting)


def _north_token_position(game: GameInstance) -> tuple[int, int]:
    """Return the sole North token position."""
    assert len(game.core_state.player_north.positions) == 1
    return game.core_state.player_north.positions[0]


def _south_positions(game: GameInstance) -> list[tuple[int, int]]:
    """Return a sorted copy of South's positions."""
    return sorted(game.core_state.player_south.positions)


# ---------------------------------------------------------------------------
# TestGameStateIsolation
# ---------------------------------------------------------------------------


class TestGameStateIsolation:
    """Core isolation: two standard games must not share any mutable state."""

    def test_two_games_different_ids(self):
        """Two games created on the same manager must have distinct IDs."""
        mgr = GameManager()
        a = _standard_game(mgr)
        b = _standard_game(mgr)
        assert a.game_id != b.game_id

    def test_two_games_both_active(self):
        """Both freshly-created games must report ACTIVE status."""
        mgr = GameManager()
        a = _standard_game(mgr)
        b = _standard_game(mgr)
        assert a.status == GameStatus.ACTIVE
        assert b.status == GameStatus.ACTIVE

    def test_move_in_game_a_does_not_affect_game_b(self):
        """A North move in game A must not change game B's token positions."""
        mgr = GameManager()
        a = _standard_game(mgr)
        b = _standard_game(mgr)

        b_before = _south_positions(b)

        # North (2,0) -> (2,1) in game A
        ok, _ = a.make_move(2, 0, 2, 1)
        assert ok

        assert _north_token_position(b) == (2, 0)
        assert _south_positions(b) == b_before

    def test_move_in_game_a_does_not_switch_turn_in_game_b(self):
        """After a valid move in game A, game B must still be North's turn."""
        mgr = GameManager()
        a = _standard_game(mgr)
        b = _standard_game(mgr)

        assert b.get_current_player_side().value == "pangui"

        ok, _ = a.make_move(2, 0, 2, 1)
        assert ok

        # Game B: turn should still be North
        assert b.get_current_player_side().value == "pangui"

    def test_capture_in_game_a_does_not_affect_game_b_positions(self):
        """A capture in game A must not remove tokens from game B."""
        mgr = GameManager()
        # Custom setup: North can immediately capture one South token
        a = _custom_game(mgr, north=[(2, 3)], south=[(2, 4)])
        b = _standard_game(mgr)

        b_south_before = _south_positions(b)
        b_south_count_before = len(b.core_state.player_south.positions)

        # North (2,3) captures over (2,4) landing on (2,5)
        ok, record = a.make_move(2, 3, 2, 5)
        assert ok
        assert record.is_capture

        # Game B must be untouched
        assert _south_positions(b) == b_south_before
        assert len(b.core_state.player_south.positions) == b_south_count_before

    def test_delete_game_a_does_not_affect_game_b(self):
        """Deleting game A must leave game B fully operational."""
        mgr = GameManager()
        a = _standard_game(mgr)
        b = _standard_game(mgr)

        ok = mgr.delete_game(a.game_id)
        assert ok

        retrieved = mgr.get_game(b.game_id)
        assert retrieved is b

        # B must still be playable
        ok, _ = b.make_move(2, 0, 2, 1)
        assert ok

    def test_delete_game_a_removes_only_that_game(self):
        """After deleting A, list_games must contain only B's ID."""
        mgr = GameManager()
        a = _standard_game(mgr)
        b = _standard_game(mgr)

        mgr.delete_game(a.game_id)

        listed = mgr.list_games()
        assert a.game_id not in listed
        assert b.game_id in listed
        assert len(listed) == 1


# ---------------------------------------------------------------------------
# TestMultipleCustomGames
# ---------------------------------------------------------------------------


class TestMultipleCustomGames:
    """Custom games with different setups must stay independent."""

    def test_custom_games_have_independent_positions(self):
        """Two custom games with different setups must not cross-pollinate."""
        mgr = GameManager()
        a = _custom_game(mgr, north=[(0, 0)], south=[(4, 7)])
        b = _custom_game(mgr, north=[(4, 0)], south=[(0, 7)])

        assert _north_token_position(a) == (0, 0)
        assert _north_token_position(b) == (4, 0)
        assert a.core_state.player_south.positions == [(4, 7)]
        assert b.core_state.player_south.positions == [(0, 7)]

    def test_custom_game_starting_player_independent(self):
        """One game starting with North and another with South must both be correct."""
        mgr = GameManager()
        north_starts = _custom_game(
            mgr,
            north=[(2, 3)],
            south=[(2, 5)],
            starting="pangui",
        )
        south_starts = _custom_game(
            mgr,
            north=[(2, 3)],
            south=[(2, 5)],
            starting="pu trewa",
        )

        assert north_starts.get_current_player_side().value == "pangui"
        assert south_starts.get_current_player_side().value == "pu trewa"


# ---------------------------------------------------------------------------
# TestGameCounting
# ---------------------------------------------------------------------------


class TestGameCounting:
    """GameManager bookkeeping must be correct."""

    def test_list_games_returns_all_active(self):
        """list_games must return every ID that was created."""
        mgr = GameManager()
        ids = [_standard_game(mgr).game_id for _ in range(5)]
        assert sorted(mgr.list_games()) == sorted(ids)

    def test_list_games_after_deletion(self):
        """Deleting one game must reduce the count by exactly one."""
        mgr = GameManager()
        games = [_standard_game(mgr) for _ in range(3)]
        mgr.delete_game(games[0].game_id)
        listed = mgr.list_games()
        assert len(listed) == 2
        assert games[0].game_id not in listed

    def test_list_games_empty_after_all_deleted(self):
        """Deleting every game must leave an empty list."""
        mgr = GameManager()
        games = [_standard_game(mgr) for _ in range(2)]
        for g in games:
            mgr.delete_game(g.game_id)
        assert mgr.list_games() == []


# ---------------------------------------------------------------------------
# TestStateDriftAfterManyMoves
# ---------------------------------------------------------------------------


class TestStateDriftAfterManyMoves:
    """Verify independence holds after multiple rounds of play."""

    def test_many_moves_different_games(self):
        """Five moves in each game must yield independent board states."""
        mgr = GameManager()
        a = _standard_game(mgr)
        b = _standard_game(mgr)

        # Game A: 5 moves — North/South alternate
        a.make_move(2, 0, 2, 1)  # N
        a.make_move(0, 5, 0, 4)  # S
        a.make_move(2, 1, 2, 2)  # N
        a.make_move(4, 5, 4, 4)  # S
        a.make_move(2, 2, 2, 3)  # N

        # Game B: 5 different moves
        b.make_move(2, 0, 1, 0)  # N
        b.make_move(1, 6, 1, 5)  # S
        b.make_move(1, 0, 1, 1)  # N
        b.make_move(3, 6, 3, 5)  # S
        b.make_move(1, 1, 1, 2)  # N

        assert len(a.move_history) == 5
        assert len(b.move_history) == 5

        # North tokens diverged
        assert _north_token_position(a) != _north_token_position(b)
        # South tokens also diverged
        assert _south_positions(a) != _south_positions(b)

    def test_one_game_wins_other_continues(self):
        """Winning game A must not change game B's status."""
        mgr = GameManager()
        # Game A: minimal setup — one capture wins immediately
        a = _custom_game(mgr, north=[(2, 3)], south=[(2, 4)])
        # Game B: standard full game
        b = _standard_game(mgr)

        # North captures in game A
        ok, _ = a.make_move(2, 3, 2, 5)
        assert ok
        assert a.status == GameStatus.NORTH_WON

        # Game B must still be ACTIVE
        assert b.status == GameStatus.ACTIVE
        assert b.get_current_player_side().value == "pangui"


# ---------------------------------------------------------------------------
# TestGameManagerIndependence
# ---------------------------------------------------------------------------


class TestGameManagerIndependence:
    """Separate GameManager instances must not share games."""

    def test_two_managers_are_independent(self):
        """Games created on manager A must not appear on manager B."""
        mgr_a = GameManager()
        mgr_b = GameManager()

        game_a = mgr_a.create_game()
        game_b = mgr_b.create_game()

        assert mgr_a.list_games() == [game_a.game_id]
        assert mgr_b.list_games() == [game_b.game_id]

        assert mgr_a.get_game(game_b.game_id) is None
        assert mgr_b.get_game(game_a.game_id) is None
