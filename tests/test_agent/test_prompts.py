"""Tests for game state prompt formatting for LLM consumption."""

from komikan.agent.prompts import format_game_state_prompt, format_move_list


def _api_game_state(
    north_positions=None,
    south_positions=None,
    current_player="pangui",
    move_count=0,
    status="active",
):
    """Build a dict matching the API GameState response shape."""
    north_positions = north_positions or []
    south_positions = south_positions or []
    return {
        "game_id": "test-game",
        "status": status,
        "current_player": current_player,
        "move_count": move_count,
        "north_player": {
            "positions": north_positions,
            "token_count": len(north_positions),
            "side": "pangui",
        },
        "south_player": {
            "positions": south_positions,
            "token_count": len(south_positions),
            "side": "pu trewa",
        },
    }


class TestFormatGameStatePrompt:
    def test_includes_current_player(self):
        game_state = _api_game_state(current_player="pangui", move_count=5)
        prompt = format_game_state_prompt(game_state)
        assert "pangui" in prompt.lower()

    def test_includes_move_count(self):
        game_state = _api_game_state(current_player="pu trewa", move_count=42)
        prompt = format_game_state_prompt(game_state)
        assert "42" in prompt

    def test_includes_board_positions(self):
        game_state = _api_game_state(
            north_positions=[[2, 0]],
            south_positions=[[0, 5], [1, 5]],
        )
        prompt = format_game_state_prompt(game_state)
        assert "(2,0) -> pangui" in prompt
        assert "(0,5) -> pu trewa" in prompt
        assert "(1,5) -> pu trewa" in prompt

    def test_sorts_positions_by_y_then_x(self):
        game_state = _api_game_state(
            north_positions=[[3, 1], [1, 1]],
            south_positions=[[0, 0]],
        )
        prompt = format_game_state_prompt(game_state)
        assert prompt.index("(0,0) -> pu trewa") < prompt.index("(1,1) -> pangui")
        assert prompt.index("(1,1) -> pangui") < prompt.index("(3,1) -> pangui")

    def test_includes_token_counts(self):
        game_state = _api_game_state(
            north_positions=[[2, 0]],
            south_positions=[[0, 5], [1, 5]],
        )
        prompt = format_game_state_prompt(game_state)
        assert "North tokens: 1" in prompt
        assert "South tokens: 2" in prompt

    def test_includes_status(self):
        game_state = _api_game_state(status="active")
        prompt = format_game_state_prompt(game_state)
        assert "active" in prompt.lower()

    def test_empty_board(self):
        game_state = _api_game_state()
        prompt = format_game_state_prompt(game_state)
        assert isinstance(prompt, str)
        assert len(prompt) > 0
        assert "(empty board)" in prompt

    def test_missing_player_dicts_degrade_gracefully(self):
        game_state = {
            "current_player": "pangui",
            "move_count": 0,
            "status": "active",
        }
        prompt = format_game_state_prompt(game_state)
        assert "North tokens: 0" in prompt
        assert "South tokens: 0" in prompt
        assert "(empty board)" in prompt

    def test_renders_tokens_in_grid(self):
        """Regression: the LLM must see N and S tokens on the grid."""
        game_state = _api_game_state(
            north_positions=[[2, 0]],
            south_positions=[[1, 5], [2, 5]],
        )
        prompt = format_game_state_prompt(game_state)
        lines = prompt.splitlines()
        assert ". . N . ." in lines
        assert ". S S . ." in lines
        assert "(empty board)" not in prompt

    def test_out_of_bounds_positions_are_filtered(self):
        """Regression: positions outside the 5x8 board are dropped."""
        game_state = _api_game_state(
            north_positions=[[2, 0], [5, 0], [-1, 2], [0, 8]],
        )
        prompt = format_game_state_prompt(game_state)
        assert "(2,0) -> pangui" in prompt
        assert "(5,0)" not in prompt
        assert "(-1,2)" not in prompt
        assert "(0,8)" not in prompt

    def test_missing_token_count_falls_back_to_positions(self):
        """Regression: a player without token_count falls back to len(positions)."""
        game_state = {
            "current_player": "pangui",
            "move_count": 0,
            "status": "active",
            "north_player": {
                "positions": [[2, 0], [1, 1]],
                "side": "pangui",
            },
            "south_player": {
                "positions": [],
                "token_count": 0,
                "side": "pu trewa",
            },
        }
        prompt = format_game_state_prompt(game_state)
        assert "North tokens: 2" in prompt


class TestFormatMoveList:
    def test_formats_single_move(self):
        moves = [
            {
                "position": [0, 1],
                "moves": [{"type": "advance", "to": [0, 2], "description": "move"}],
            }
        ]
        result = format_move_list(moves)
        assert "0" in result
        assert "1" in result
        assert "2" in result

    def test_formats_capture(self):
        moves = [
            {
                "position": [2, 2],
                "moves": [
                    {
                        "type": "capture",
                        "to": [2, 4],
                        "description": "capture",
                        "captures_from": [[2, 3]],
                    }
                ],
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
            {
                "position": [0, 1],
                "moves": [{"type": "advance", "to": [0, 2], "description": "move"}],
            },
            {
                "position": [2, 0],
                "moves": [
                    {"type": "advance", "to": [2, 1], "description": "move"},
                    {"type": "advance", "to": [1, 1], "description": "move"},
                ],
            },
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
                    {
                        "type": "capture",
                        "to": [1, 4],
                        "description": "capture",
                        "captures_from": [[1, 3]],
                    },
                ],
            }
        ]
        result = format_move_list(moves)
        assert isinstance(result, str)
        assert len(result) > 0
