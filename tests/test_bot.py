"""Tests for the RandomBot implementation."""

import pytest
from unittest.mock import MagicMock


class TestBotProtocol:
    """Test that BotProtocol defines the expected interface."""

    def test_bot_protocol_has_choose_move(self):
        """BotProtocol must define a choose_move method."""
        from komikan.agent.bot import BotProtocol

        assert hasattr(BotProtocol, "choose_move")


class TestRandomBot:
    """Test the RandomBot implementation."""

    def test_random_bot_has_choose_move(self):
        """RandomBot must implement choose_move."""
        from komikan.agent.bot import RandomBot

        bot = RandomBot()
        assert hasattr(bot, "choose_move")

    def test_random_bot_is_bot_protocol(self):
        """RandomBot must satisfy BotProtocol."""
        from komikan.agent.bot import RandomBot, BotProtocol

        bot = RandomBot()
        assert isinstance(bot, BotProtocol)

    def test_random_bot_returns_valid_move(self):
        """RandomBot.choose_move must return a Move from available options."""
        from komikan.agent.bot import RandomBot

        bot = RandomBot()

        # Mock game with north token at (2,0) that can advance to (2,1)
        mock_game = MagicMock()
        mock_game.core_state.current_player.positions = [(2, 0)]
        mock_game.get_valid_moves.return_value = (
            [MagicMock(x=2, y=1)],  # valid_moves
            [],  # valid_captures
        )

        move = bot.choose_move(mock_game)
        assert move is not None
        assert move.from_position == (2, 0)
        assert move.to_position == (2, 1)
        assert move.is_capture is False

    def test_random_bot_with_captures(self):
        """RandomBot must handle capture moves."""
        from komikan.agent.bot import RandomBot

        bot = RandomBot()

        mock_game = MagicMock()
        mock_game.core_state.current_player.positions = [(2, 0)]

        capture_to = MagicMock(x=2, y=2)
        capture_cap = MagicMock(x=2, y=1)
        mock_game.get_valid_moves.return_value = (
            [],  # no advances
            [(capture_to, capture_cap)],  # one capture
        )

        move = bot.choose_move(mock_game)
        assert move is not None
        assert move.from_position == (2, 0)
        assert move.to_position == (2, 2)
        assert move.is_capture is True
        assert move.captured_position == (2, 1)

    def test_random_bot_raises_when_no_moves(self):
        """RandomBot must raise ValueError when no moves are available."""
        from komikan.agent.bot import RandomBot

        bot = RandomBot()

        mock_game = MagicMock()
        mock_game.core_state.current_player.positions = [(2, 0)]
        mock_game.get_valid_moves.return_value = ([], [])

        with pytest.raises(ValueError, match="No valid moves"):
            bot.choose_move(mock_game)

    def test_random_bot_random_selection(self):
        """RandomBot must randomly select from multiple moves."""
        import random
        from komikan.agent.bot import RandomBot

        random.seed(42)  # deterministic for testing

        bot = RandomBot()

        mock_game = MagicMock()
        mock_game.core_state.current_player.positions = [(2, 0)]
        mock_game.get_valid_moves.return_value = (
            [MagicMock(x=1, y=1), MagicMock(x=2, y=1), MagicMock(x=3, y=1)],
            [],
        )

        # Run multiple times to verify randomness
        results = set()
        for _ in range(20):
            move = bot.choose_move(mock_game)
            results.add(move.to_position)

        # With 3 options and 20 tries, we should see more than 1 unique result
        assert len(results) > 1
