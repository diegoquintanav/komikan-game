"""Tests for the game_loop orchestrator."""

from unittest.mock import MagicMock


class TestGameLoop:
    """Test the game_loop function."""

    def test_game_loop_returns_result_dict(self):
        """game_loop must return a dict with winner, moves_played, reason."""
        from komikan.agent.game_loop import game_loop

        game = MagicMock()
        game.status.value = "active"

        call_count = 0

        def make_move_side_effect(*args):
            nonlocal call_count
            call_count += 1
            if call_count >= 1:
                game.status.value = "north_won"
            return True, ""

        game.make_move.side_effect = make_move_side_effect

        bot = MagicMock()
        bot.choose_move.return_value = MagicMock(
            from_position=(2, 0), to_position=(2, 1)
        )

        result = game_loop(game, bot, max_turns=10)
        assert "winner" in result
        assert "moves_played" in result
        assert "reason" in result

    def test_game_loop_stops_on_game_over(self):
        """game_loop must stop when the game ends."""
        from komikan.agent.game_loop import game_loop

        game = MagicMock()
        game.status.value = "north_won"  # already over

        bot = MagicMock()

        result = game_loop(game, bot)
        assert result["moves_played"] == 0
        assert result["winner"] == "north_won"
        bot.choose_move.assert_not_called()

    def test_game_loop_stops_on_no_moves(self):
        """game_loop must stop when bot raises ValueError."""
        from komikan.agent.game_loop import game_loop

        game = MagicMock()
        game.status.value = "active"

        bot = MagicMock()
        bot.choose_move.side_effect = ValueError("No valid moves available")

        result = game_loop(game, bot)
        assert result["moves_played"] == 0

    def test_game_loop_counts_moves(self):
        """game_loop must count moves played."""
        from komikan.agent.game_loop import game_loop

        game = MagicMock()
        game.status.value = "active"
        game.make_move.return_value = (True, "")

        turn = 0

        def advance_turn(*args):
            nonlocal turn
            turn += 1
            if turn >= 3:
                game.status.value = "north_won"
            return True, ""

        game.make_move.side_effect = advance_turn

        bot = MagicMock()
        bot.choose_move.return_value = MagicMock(
            from_position=(2, 0), to_position=(2, 1)
        )

        result = game_loop(game, bot, max_turns=10)
        assert result["moves_played"] == 3

    def test_game_loop_respects_max_turns(self):
        """game_loop must respect the max_turns safety limit."""
        from komikan.agent.game_loop import game_loop

        game = MagicMock()
        game.status.value = "active"
        game.make_move.return_value = (True, "")

        bot = MagicMock()
        bot.choose_move.return_value = MagicMock(
            from_position=(2, 0), to_position=(2, 1)
        )

        result = game_loop(game, bot, max_turns=5)
        assert result["moves_played"] == 5
        assert result["winner"] == "active"
        assert result["reason"] == "max_turns_reached"

    def test_game_loop_stops_on_failed_move(self):
        """game_loop must stop when make_move returns False."""
        from komikan.agent.game_loop import game_loop

        game = MagicMock()
        game.status.value = "active"
        game.make_move.return_value = (False, "Invalid move")

        bot = MagicMock()
        bot.choose_move.return_value = MagicMock(
            from_position=(2, 0), to_position=(2, 1)
        )

        result = game_loop(game, bot)
        assert result["moves_played"] == 0
