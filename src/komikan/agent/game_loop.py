"""Game loop for Komikan AI agent.

Orchestrates turns between LLM-based or random-bot players.
"""

from komikan.agent.bot import BotProtocol, Move


def game_loop(game, bot: BotProtocol, max_turns: int = 200) -> dict:
    """Run a complete game with a bot making moves.

    Args:
        game: GameInstance with initial state.
        bot: Bot implementation that chooses moves.
        max_turns: Safety limit to prevent infinite games.

    Returns:
        Dict with 'winner', 'moves_played', and 'reason' keys.
    """
    moves_played = 0

    for _ in range(max_turns):
        # Check if game is over
        if game.status.value != "active":
            break

        try:
            move: Move = bot.choose_move(game)
        except ValueError:
            # No valid moves — game over
            break

        # Execute the move via the game manager
        success, _ = game.make_move(
            move.from_position[0],
            move.from_position[1],
            move.to_position[0],
            move.to_position[1],
        )

        if not success:
            break

        moves_played += 1

    return {
        "winner": game.status.value,
        "moves_played": moves_played,
        "reason": _resolve_reason(game),
    }


def _resolve_reason(game) -> str:
    """Determine why the game ended."""
    status = game.status.value
    if status == "active":
        return "max_turns_reached"
    elif status == "north_won":
        return "north_captured_enough"
    elif status == "south_won":
        return "south_trapped_north"
    elif status == "stalemate":
        return "stalemate"
    return "unknown"
