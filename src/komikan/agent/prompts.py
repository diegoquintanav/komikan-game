"""Prompt formatting for LLM game state and move lists."""

from __future__ import annotations

import re
from typing import Any


BOARD_WIDTH = 5
BOARD_HEIGHT = 8


def _player_positions(player: object) -> list[tuple[int, int]]:
    """Extract in-bounds (x, y) positions from an API player dict."""
    if not isinstance(player, dict):
        return []

    positions = player.get("positions")
    if not isinstance(positions, list):
        return []

    result: list[tuple[int, int]] = []
    for position in positions:
        if not isinstance(position, (list, tuple)) or len(position) != 2:
            continue
        x, y = position
        if isinstance(x, int) and isinstance(y, int):
            if 0 <= x < BOARD_WIDTH and 0 <= y < BOARD_HEIGHT:
                result.append((x, y))
    return result


def _player_token_count(player: object, positions: list[tuple[int, int]]) -> int:
    """Read the token count from an API player dict, falling back to positions."""
    if isinstance(player, dict):
        count = player.get("token_count")
        if isinstance(count, int):
            return count
    return len(positions)


def format_game_state_prompt(game_state: dict[str, object]) -> str:
    """Format the API game state as a structured prompt for the LLM."""
    current_player = game_state.get("current_player", "unknown")
    move_count = game_state.get("move_count", 0)
    status = game_state.get("status", "unknown")

    north_player = game_state.get("north_player") or {}
    south_player = game_state.get("south_player") or {}

    north_positions = _player_positions(north_player)
    south_positions = _player_positions(south_player)
    north_count = _player_token_count(north_player, north_positions)
    south_count = _player_token_count(south_player, south_positions)

    lines = [
        f"Current player: {current_player}",
        f"Move count: {move_count}",
        f"Game status: {status}",
        f"North tokens: {north_count}",
        f"South tokens: {south_count}",
        "",
        "Board:",
    ]

    north_set = set(north_positions)
    south_set = set(south_positions)

    for y in range(BOARD_HEIGHT):
        row: list[str] = []
        for x in range(BOARD_WIDTH):
            if (x, y) in north_set:
                row.append("N")
            elif (x, y) in south_set:
                row.append("S")
            else:
                row.append(".")
        lines.append(" ".join(row))

    lines.append("")
    lines.append("Board positions (x,y -> side):")

    occupied = [(x, y, "pangui") for x, y in north_positions]
    occupied += [(x, y, "pu trewa") for x, y in south_positions]

    if occupied:
        for x, y, side in sorted(occupied, key=lambda item: (item[1], item[0])):
            lines.append(f"  ({x},{y}) -> {side}")
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


def build_system_prompt(side: str) -> str:
    """Build a compact system prompt describing Komikan and the agent's role."""
    normalized = side.strip().lower()

    if normalized in ("south", "pu trewa"):
        role = "You are the Pu Trewa (South), the 12 dogs."
        objective = (
            "Your objective is to trap the Pangui so it has no legal move and no "
            "legal capture. You cannot capture; your tokens only advance."
        )
    else:
        role = "You are the Pangui (North), the lone puma."
        objective = (
            "Your objective is to capture South tokens by jumping over them. "
            "You win when South has 4 or fewer tokens remaining."
        )

    return "\n".join(
        [
            "Komikan is an asymmetric Mapuche hunt game on a 5x8 grid of nodes.",
            "One Pangui (North) plays against 12 Pu Trewa (South).",
            role,
            objective,
            (
                "Coordinates: x ranges 0..4 and y ranges 0..7. Disabled nodes are "
                "(0,2) and (4,2)."
            ),
            (
                "Movement: on your turn, move one token to an adjacent empty node, "
                "orthogonal or diagonal."
            ),
            (
                "Capture: only North captures, by jumping exactly two steps over an "
                "adjacent South token to an empty valid landing node."
            ),
            "Win conditions: North wins when South has 4 or fewer tokens; South "
            "wins when North has no valid moves; the game is a stalemate when South "
            "has no valid moves on its turn.",
            (
                "Output: choose exactly one move from the provided legal move list. "
                "Call make_move once with from_x, from_y, to_x, to_y. Do not reply "
                "with text."
            ),
        ]
    )


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
