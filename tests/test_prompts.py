"""Tests for prompt formatting and LLM response parsing."""

from unittest.mock import MagicMock


class TestFormatGameState:
    """Test format_game_state prompt builder."""

    def test_format_includes_current_player(self):
        """Prompt must include the current player side."""
        from komikan.agent.prompts import format_game_state

        mock_game = MagicMock()
        mock_game.core_state.current_player.side.value = "pangui"
        mock_game.core_state.current_player.positions = [(2, 0)]
        mock_game.status.value = "active"
        mock_game.get_valid_moves.return_value = (
            [MagicMock(x=2, y=1)],
            [],
        )

        prompt = format_game_state(mock_game)
        assert "pangui" in prompt.lower() or "north" in prompt.lower()

    def test_format_includes_token_count(self):
        """Prompt must include how many tokens the player has."""
        from komikan.agent.prompts import format_game_state

        mock_game = MagicMock()
        mock_game.core_state.current_player.side.value = "pangui"
        mock_game.core_state.current_player.positions = [(2, 0)]
        mock_game.status.value = "active"
        mock_game.get_valid_moves.return_value = (
            [MagicMock(x=2, y=1)],
            [],
        )

        prompt = format_game_state(mock_game)
        assert "1" in prompt  # 1 token

    def test_format_includes_valid_moves(self):
        """Prompt must list available moves."""
        from komikan.agent.prompts import format_game_state

        mock_game = MagicMock()
        mock_game.core_state.current_player.side.value = "pangui"
        mock_game.core_state.current_player.positions = [(2, 0)]
        mock_game.status.value = "active"
        mock_game.get_valid_moves.return_value = (
            [MagicMock(x=2, y=1)],
            [],
        )

        prompt = format_game_state(mock_game)
        assert "2,1" in prompt or "(2, 1)" in prompt or "2, 1" in prompt

    def test_format_includes_game_status(self):
        """Prompt must include game status."""
        from komikan.agent.prompts import format_game_state

        mock_game = MagicMock()
        mock_game.core_state.current_player.side.value = "pangui"
        mock_game.core_state.current_player.positions = [(2, 0)]
        mock_game.status.value = "active"
        mock_game.get_valid_moves.return_value = (
            [MagicMock(x=2, y=1)],
            [],
        )

        prompt = format_game_state(mock_game)
        assert "active" in prompt.lower()

    def test_format_includes_instructions(self):
        """Prompt must tell the LLM what output format to use."""
        from komikan.agent.prompts import format_game_state

        mock_game = MagicMock()
        mock_game.core_state.current_player.side.value = "pangui"
        mock_game.core_state.current_player.positions = [(2, 0)]
        mock_game.status.value = "active"
        mock_game.get_valid_moves.return_value = (
            [MagicMock(x=2, y=1)],
            [],
        )

        prompt = format_game_state(mock_game)
        # Should mention the expected response format
        assert "from" in prompt.lower() and "to" in prompt.lower()


class TestParseLLMMove:
    """Test parse_llm_move response parser."""

    def test_parse_valid_move(self):
        """parse_llm_move must parse a well-formed LLM response."""
        from komikan.agent.prompts import parse_llm_move

        response = "from (2,0) to (2,1)"
        valid_moves = [
            {"type": "advance", "to": [2, 1], "description": "advance"},
        ]

        move = parse_llm_move(response, valid_moves)
        assert move is not None
        assert move["from"] == [2, 0]
        assert move["to"] == [2, 1]

    def test_parse_json_format(self):
        """parse_llm_move must handle JSON-formatted responses."""
        from komikan.agent.prompts import parse_llm_move

        response = '{"from": [2, 0], "to": [2, 1]}'
        valid_moves = [
            {"type": "advance", "to": [2, 1], "description": "advance"},
        ]

        move = parse_llm_move(response, valid_moves)
        assert move is not None
        assert move["from"] == [2, 0]
        assert move["to"] == [2, 1]

    def test_parse_returns_none_for_invalid(self):
        """parse_llm_move must return None for unparseable responses."""
        from komikan.agent.prompts import parse_llm_move

        response = "I don't know what to do"
        valid_moves = [
            {"type": "advance", "to": [2, 1], "description": "advance"},
        ]

        move = parse_llm_move(response, valid_moves)
        assert move is None

    def test_parse_validates_move_exists(self):
        """parse_llm_move must verify the parsed move is in valid_moves."""
        from komikan.agent.prompts import parse_llm_move

        response = "from (2,0) to (3,3)"
        valid_moves = [
            {"type": "advance", "to": [2, 1], "description": "advance"},
        ]

        move = parse_llm_move(response, valid_moves)
        # (3,3) is not in valid_moves, so should return None
        assert move is None

    def test_parse_with_capture_move(self):
        """parse_llm_move must handle capture move responses."""
        from komikan.agent.prompts import parse_llm_move

        response = "from (2,0) to (2,2) capture"
        valid_moves = [
            {"type": "capture", "to": [2, 2], "description": "capture over (2,1)"},
        ]

        move = parse_llm_move(response, valid_moves)
        assert move is not None
        assert move["to"] == [2, 2]
