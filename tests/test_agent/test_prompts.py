"""Tests for game state prompt formatting for LLM consumption."""

from komikan.agent.prompts import format_game_state_prompt, format_move_list


class TestFormatGameStatePrompt:
    def test_includes_current_player(self):
        game_state = {
            "current_player": "north",
            "move_count": 5,
            "status": "in_progress",
            "board": {},
            "north_captures": 0,
            "south_tokens_remaining": 12,
        }
        prompt = format_game_state_prompt(game_state)
        assert "north" in prompt.lower()

    def test_includes_move_count(self):
        game_state = {
            "current_player": "south",
            "move_count": 42,
            "status": "in_progress",
            "board": {},
            "north_captures": 0,
            "south_tokens_remaining": 12,
        }
        prompt = format_game_state_prompt(game_state)
        assert "42" in prompt

    def test_includes_board_positions(self):
        game_state = {
            "current_player": "north",
            "move_count": 1,
            "status": "in_progress",
            "board": {"2,0": "north", "0,5": "south", "1,5": "south"},
            "north_captures": 0,
            "south_tokens_remaining": 12,
        }
        prompt = format_game_state_prompt(game_state)
        assert "2,0" in prompt or "(2,0)" in prompt

    def test_includes_status(self):
        game_state = {
            "current_player": "north",
            "move_count": 0,
            "status": "in_progress",
            "board": {},
            "north_captures": 0,
            "south_tokens_remaining": 12,
        }
        prompt = format_game_state_prompt(game_state)
        assert "in_progress" in prompt.lower() or "progress" in prompt.lower()

    def test_empty_board(self):
        game_state = {
            "current_player": "north",
            "move_count": 0,
            "status": "in_progress",
            "board": {},
            "north_captures": 0,
            "south_tokens_remaining": 12,
        }
        prompt = format_game_state_prompt(game_state)
        assert isinstance(prompt, str)
        assert len(prompt) > 0

    def test_includes_capture_info(self):
        game_state = {
            "current_player": "north",
            "move_count": 10,
            "status": "in_progress",
            "board": {},
            "north_captures": 3,
            "south_tokens_remaining": 9,
        }
        prompt = format_game_state_prompt(game_state)
        assert "3" in prompt


class TestFormatMoveList:
    def test_formats_single_move(self):
        moves = [{"from": [0, 1], "moves": [[0, 2]], "captures": []}]
        result = format_move_list(moves)
        assert "0" in result
        assert "1" in result
        assert "2" in result

    def test_formats_capture(self):
        moves = [{"from": [2, 2], "moves": [], "captures": [[[2, 4], [2, 3]]]}]
        result = format_move_list(moves)
        assert "2,2" in result or "(2,2)" in result

    def test_empty_moves(self):
        result = format_move_list([])
        assert isinstance(result, str)
        assert len(result) > 0

    def test_multiple_tokens(self):
        moves = [
            {"from": [0, 1], "moves": [[0, 2]], "captures": []},
            {"from": [2, 0], "moves": [[2, 1], [1, 1]], "captures": []},
        ]
        result = format_move_list(moves)
        assert "0,1" in result or "(0,1)" in result
        assert "2,0" in result or "(2,0)" in result

    def test_with_captures_and_moves(self):
        moves = [{"from": [1, 2], "moves": [[1, 3]], "captures": [[[1, 4], [1, 3]]]}]
        result = format_move_list(moves)
        assert isinstance(result, str)
        assert len(result) > 0
