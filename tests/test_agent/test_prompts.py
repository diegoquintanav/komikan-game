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
        moves = [
            {"position": [0, 1], "moves": [{"type": "advance", "to": [0, 2], "description": "move"}]}
        ]
        result = format_move_list(moves)
        assert "0" in result
        assert "1" in result
        assert "2" in result

    def test_formats_capture(self):
        moves = [
            {
                "position": [2, 2],
                "moves": [{"type": "capture", "to": [2, 4], "description": "capture", "captures_from": [[2, 3]]}],
            }
        ]
        result = format_move_list(moves)
        assert "2,2" in result or "(2,2)" in result

    def test_empty_moves(self):
        result = format_move_list([])
        assert isinstance(result, str)
        assert len(result) > 0

    def test_multiple_tokens(self):
        moves = [
            {"position": [0, 1], "moves": [{"type": "advance", "to": [0, 2], "description": "move"}]},
            {"position": [2, 0], "moves": [{"type": "advance", "to": [2, 1], "description": "move"}, {"type": "advance", "to": [1, 1], "description": "move"}]},
        ]
        result = format_move_list(moves)
        assert "0,1" in result or "(0,1)" in result
        assert "2,0" in result or "(2,0)" in result

    def test_with_captures_and_moves(self):
        moves = [
            {
                "position": [1, 2],
                "moves": [
                    {"type": "advance", "to": [1, 3], "description": "move"},
                    {"type": "capture", "to": [1, 4], "description": "capture", "captures_from": [[1, 3]]},
                ],
            }
        ]
        result = format_move_list(moves)
        assert isinstance(result, str)
        assert len(result) > 0
