"""Prompt formatting and LLM response parsing for Komikan agent."""

import json
import re
from typing import Any


def format_game_state(game) -> str:
    """Format the current game state into a prompt for the LLM.

    Args:
        game: GameInstance with current game state.

    Returns:
        A string prompt describing the board and available moves.
    """
    current_player = game.core_state.current_player
    side_name = current_player.side.value
    token_count = len(current_player.positions)
    status = game.status.value

    lines = [
        f"You are playing Komikan as {side_name} ({token_count} token{'s' if token_count != 1 else ''}).",
        f"Game status: {status}.",
        "",
        "Your tokens and their available moves:",
    ]

    for pos in current_player.positions:
        from_x, from_y = pos
        valid_moves, valid_captures = game.get_valid_moves(from_x, from_y)

        move_strs = []
        for move in valid_moves:
            move_strs.append(f"advance to ({move.x},{move.y})")
        for to_pos, cap_pos in valid_captures:
            move_strs.append(
                f"capture from ({from_x},{from_y}) over ({cap_pos.x},{cap_pos.y}) to ({to_pos.x},{to_pos.y})"
            )

        if move_strs:
            lines.append(f"  Token at ({from_x},{from_y}): {'; '.join(move_strs)}")
        else:
            lines.append(f"  Token at ({from_x},{from_y}): no valid moves")

    lines.extend([
        "",
        "Choose ONE move. Respond with EXACTLY this format:",
        '  from (x1,y1) to (x2,y2)',
        "For captures, append 'capture' at the end.",
        "Do not include any other text.",
    ])

    return "\n".join(lines)


def parse_llm_move(response: str, valid_moves: list[dict[str, Any]]) -> dict[str, Any] | None:
    """Parse an LLM response string into a move dict.

    Args:
        response: Raw LLM response text.
        valid_moves: List of valid move dicts with 'to' field.

    Returns:
        A dict with 'from' and 'to' keys, or None if parsing fails.
    """
    # Try JSON format first
    try:
        data = json.loads(response.strip())
        if "from" in data and "to" in data:
            if _move_in_valid_moves(data["to"], valid_moves):
                return {"from": data["from"], "to": data["to"]}
    except (json.JSONDecodeError, TypeError):
        pass

    # Try text format: "from (x1,y1) to (x2,y2)"
    pattern = r"from\s*\(\s*(\d+)\s*,\s*(\d+)\s*\)\s*to\s*\(\s*(\d+)\s*,\s*(\d+)\s*\)"
    match = re.search(pattern, response)
    if match:
        from_pos = [int(match.group(1)), int(match.group(2))]
        to_pos = [int(match.group(3)), int(match.group(4))]
        if _move_in_valid_moves(to_pos, valid_moves):
            return {"from": from_pos, "to": to_pos}

    return None


def _move_in_valid_moves(to_pos: list[int], valid_moves: list[dict[str, Any]]) -> bool:
    """Check if a target position exists in the list of valid moves."""
    return any(m["to"] == to_pos for m in valid_moves)
