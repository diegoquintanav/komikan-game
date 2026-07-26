"""Prompt formatting for LLM game state and move lists."""

from __future__ import annotations

import re
from typing import Any


def format_game_state_prompt(game_state: dict[str, object]) -> str:
    """Format game state as a structured prompt for the LLM."""
    board = game_state.get("board", {})
    current_player = game_state.get("current_player", "unknown")
    move_count = game_state.get("move_count", 0)
    status = game_state.get("status", "unknown")
    north_captures = game_state.get("north_captures", 0)
    south_tokens = game_state.get("south_tokens_remaining", 12)

    lines = [
        f"Current player: {current_player}",
        f"Move count: {move_count}",
        f"Game status: {status}",
        f"North captures: {north_captures}",
        f"South tokens remaining: {south_tokens}",
        "",
        "Board positions (x,y -> side):",
    ]

    if board:
        for pos, side in sorted(
            board.items(),
            key=lambda item: (int(item[0].split(",")[1]), int(item[0].split(",")[0])),
        ):
            lines.append(f"  {pos} -> {side}")
    else:
        lines.append("  (empty board)")

    return "\n".join(lines)


def format_move_list(tokens: list[dict[str, object]]) -> str:
    """Format the valid moves list for the LLM prompt."""
    if not tokens:
        return "No valid moves available."

    lines = ["Valid moves:"]

    for token in tokens:
        from_pos = token["position"]
        from_str = f"({from_pos[0]},{from_pos[1]})"

        moves = token.get("moves", [])

        if moves:
            lines.append(f"  Token at {from_str}:")
            for m in moves:
                to = m["to"]
                if m["type"] == "capture":
                    lines.append(f"    -> capture land on ({to[0]},{to[1]})")
                else:
                    lines.append(f"    -> move to ({to[0]},{to[1]})")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Backward-compat aliases (used by old cli.py; removed in Phase 4)
# ---------------------------------------------------------------------------


def format_game_state(game: Any) -> str:
    """Legacy: format an in-memory GameInstance for the LLM (cli.py compat)."""
    board_width = getattr(game, "board_width", 5)
    board_height = getattr(game, "board_height", 8)
    current_player = game.core_state.current_player
    side_label = current_player.side.value

    lines = [
        f"Current player: {side_label}",
        f"Move count: {getattr(game.core_state, 'move_count', 0)}",
        f"Game status: {getattr(getattr(game, 'status', None), 'value', 'unknown')}",
        "",
        "Board:",
    ]

    grid = [["." for _ in range(board_width)] for _ in range(board_height)]
    for player in game.core_state.players:
        symbol = "N" if player.side.value == "pangui" else "S"
        for pos in player.positions:
            x, y = pos
            if 0 <= y < board_height and 0 <= x < board_width:
                grid[y][x] = symbol

    for y in range(board_height):
        lines.append(" ".join(grid[y]))

    lines.append("")
    lines.append("Valid moves (from position -> to position):")

    for pos in current_player.positions:
        fx, fy = pos
        valid_moves, valid_captures = game.get_valid_moves(fx, fy)
        for m in valid_moves:
            lines.append(f"  {fx},{fy} -> {m.x},{m.y}")
        for to_pos, _cap_pos in valid_captures:
            lines.append(f"  {fx},{fy} -> {to_pos.x},{to_pos.y} (capture)")

    return "\n".join(lines)


def parse_llm_move(
    response: str, valid_moves: list[dict[str, object]]
) -> dict[str, list[int]] | None:
    """Legacy: parse an LLM text response into a move dict (cli.py compat)."""
    if not response:
        return None

    # Try JSON format first: {"from": [2, 0], "to": [2, 1]}
    import json

    try:
        data = json.loads(response)
        if isinstance(data, dict) and "from" in data and "to" in data:
            from_pos = data["from"]
            to_pos = data["to"]
            if isinstance(from_pos, list) and isinstance(to_pos, list):
                for move in valid_moves:
                    if move.get("to") == to_pos:
                        return {"from": from_pos, "to": to_pos}
    except (json.JSONDecodeError, TypeError):
        pass

    # Try text formats: "from (2,0) to (2,1)" or "2,0 -> 2,1" or "2,0 to 2,1"
    pattern = r"(?:from\s*\(\s*)?(\d+)\s*,\s*(\d+)\s*\)?\s*(?:->|to)\s*(?:\(\s*)?(\d+)\s*,\s*(\d+)\s*\)?"
    match = re.search(pattern, response)
    if not match:
        return None

    from_x, from_y = int(match.group(1)), int(match.group(2))
    to_x, to_y = int(match.group(3)), int(match.group(4))

    for move in valid_moves:
        if move.get("to") == [to_x, to_y]:
            return {"from": [from_x, from_y], "to": [to_x, to_y]}

    return None
