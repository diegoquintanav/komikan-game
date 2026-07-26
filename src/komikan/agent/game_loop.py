"""Game loop orchestrator for LLM agent vs random opponent via REST API."""

from __future__ import annotations

import logging
from typing import Any

from komikan.agent.agent import KomikanAgent
from komikan.agent.opponent import Opponent

logger = logging.getLogger(__name__)


def agent_game_loop(
    agent: KomikanAgent,
    opponent: Opponent,
    max_turns: int = 200,
) -> str:
    """Run a game loop with the LLM agent playing against an opponent.

    Returns:
        The final game status string (e.g. "north_won", "south_won", "stalemate").
    """
    for _ in range(max_turns):
        game_state = agent._fetch_game_state()
        status = str(game_state.get("status", "unknown"))

        if status != "in_progress":
            return status

        current_player = str(game_state.get("current_player", ""))

        if current_player == agent.side:
            result = agent.play_turn()
            if result and result.get("status") and result["status"] != "in_progress":
                return str(result["status"])
        else:
            move = opponent.choose_move()
            if move:
                agent._execute_move(move)

    return status


# ---------------------------------------------------------------------------
# Backward-compat alias (used by old cli.py and tests; removed in Phase 4)
# ---------------------------------------------------------------------------


def game_loop(game: Any, bot: Any, max_turns: int = 200) -> dict[str, Any]:
    """Legacy game loop using in-memory Game objects and Bot objects."""
    moves_played = 0
    reason = "normal"

    for _ in range(max_turns):
        status_value = getattr(getattr(game, "status", None), "value", "unknown")

        if status_value != "active":
            reason = status_value
            break

        try:
            move = bot.choose_move()
            success, error_msg = game.make_move(move)
        except ValueError as e:
            reason = str(e)
            break

        if not success:
            reason = error_msg
            break

        moves_played += 1

    final_status = getattr(getattr(game, "status", None), "value", "unknown")
    if moves_played >= max_turns and final_status == "active":
        reason = "max_turns_reached"

    return {
        "winner": final_status,
        "moves_played": moves_played,
        "reason": reason,
    }
