"""CLI entry point for Komikan AI agent games.

Usage:
    komikan-cli [--north <player>] [--south <player>] [--delay <seconds>]

Player types: human, random, llm
"""

import argparse
import time

from komikan.agent.bot import RandomBot, Move
from komikan.agent.prompts import format_game_state, parse_llm_move


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        prog="komikan-cli",
        description="Play Komikan from the command line",
    )
    parser.add_argument(
        "--north",
        default="human",
        choices=["human", "random", "llm"],
        help="Player type for north (default: human)",
    )
    parser.add_argument(
        "--south",
        default="human",
        choices=["human", "random", "llm"],
        help="Player type for south (default: human)",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=0,
        help="Delay in seconds between moves (default: 0)",
    )
    return parser.parse_args(argv)


def print_banner() -> None:
    """Print the game banner."""
    print("=" * 40)
    print("  KOMIKAN - Mapuche Hunt Game")
    print("=" * 40)


def print_board(game) -> None:
    """Print the current board state."""
    width = game.board_width
    height = game.board_height

    # Build a grid
    grid = [["." for _ in range(width)] for _ in range(height)]

    for player in game.core_state.players:
        symbol = "N" if player.side.value == "pangui" else "S"
        for pos in player.positions:
            x, y = pos
            if 0 <= y < height and 0 <= x < width:
                grid[y][x] = symbol

    print()
    for y in range(height):
        row_str = " ".join(grid[y])
        print(f"  {y}: {row_str}")
    print()


def get_human_move(game) -> Move | None:
    """Get a move from human input.

    Returns:
        Move parsed from user input, or None on error.
    """
    current_player = game.core_state.current_player
    positions = current_player.positions

    prompt_parts = []
    for pos in positions:
        fx, fy = pos
        valid_moves, valid_captures = game.get_valid_moves(fx, fy)
        for m in valid_moves:
            prompt_parts.append(f"  {fx},{fy} -> {m.x},{m.y}")
        for to_pos, cap_pos in valid_captures:
            prompt_parts.append(f"  {fx},{fy} -> {to_pos.x},{to_pos.y} (capture)")

    if not prompt_parts:
        return None

    print("Available moves:")
    for part in prompt_parts:
        print(part)

    while True:
        try:
            raw = input("Your move (from_x,from_y to_x,to_y): ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return None

        if not raw:
            continue

        parts = raw.replace("->", " ").split()
        if len(parts) != 2:
            print("Invalid format. Use: from_x,from_y to_x,to_y")
            continue

        try:
            from_parts = parts[0].split(",")
            to_parts = parts[1].split(",")
            from_pos = (int(from_parts[0]), int(from_parts[1]))
            to_pos = (int(to_parts[0]), int(to_parts[1]))
        except (ValueError, IndexError):
            print("Invalid numbers. Use: from_x,from_y to_x,to_y")
            continue

        # Validate this move exists
        is_valid = False
        is_capture = False
        for m in game.get_valid_moves(from_pos[0], from_pos[1])[0]:
            if (m.x, m.y) == to_pos:
                is_valid = True
                break
        if not is_valid:
            for to_p, cap_p in game.get_valid_moves(from_pos[0], from_pos[1])[1]:
                if (to_p.x, to_p.y) == to_pos:
                    is_valid = True
                    is_capture = True
                    break

        if not is_valid:
            print("Invalid move. Check available moves and try again.")
            continue

        return Move(
            from_position=from_pos,
            to_position=to_pos,
            is_capture=is_capture,
        )


def get_random_move(game) -> Move | None:
    """Get a move from the random bot.

    Returns:
        Random Move, or None if no moves available.
    """
    bot = RandomBot()
    try:
        return bot.choose_move(game)
    except ValueError:
        return None


def get_llm_move(game, llm_provider) -> Move | None:
    """Get a move from the LLM provider with 3 retries.

    Args:
        game: GameInstance.
        llm_provider: LLM provider with chat() method.

    Returns:
        Move parsed from LLM response, or random fallback.
    """
    _current_player = game.core_state.current_player
    prompt = format_game_state(game)

    for attempt in range(3):
        try:
            response = llm_provider.chat([{"role": "user", "content": prompt}])
            valid_moves = _build_valid_moves_list(game)
            parsed = parse_llm_move(response, valid_moves)
            if parsed is not None:
                from_pos = tuple(parsed["from"])
                to_pos = tuple(parsed["to"])
                # Determine if capture
                is_capture = False
                for to_p, cap_p in game.get_valid_moves(from_pos[0], from_pos[1])[1]:
                    if (to_p.x, to_p.y) == to_pos:
                        is_capture = True
                        break
                print(
                    f"  LLM chose: ({from_pos[0]},{from_pos[1]}) -> ({to_pos[0]},{to_pos[1]})"
                )
                return Move(
                    from_position=from_pos,
                    to_position=to_pos,
                    is_capture=is_capture,
                )
        except Exception as e:
            print(f"  LLM attempt {attempt + 1} failed: {e}")

    # Fallback to random
    print("  LLM failed after 3 attempts, falling back to random")
    return get_random_move(game)


def _build_valid_moves_list(game) -> list[dict]:
    """Build a list of valid moves as dicts for parse_llm_move."""
    current_player = game.core_state.current_player
    moves = []
    for pos in current_player.positions:
        fx, fy = pos
        valid_advances, valid_captures = game.get_valid_moves(fx, fy)
        for m in valid_advances:
            moves.append(
                {"type": "advance", "to": [m.x, m.y], "description": "advance"}
            )
        for to_pos, cap_pos in valid_captures:
            moves.append(
                {
                    "type": "capture",
                    "to": [to_pos.x, to_pos.y],
                    "description": f"capture over ({cap_pos.x},{cap_pos.y})",
                }
            )
    return moves


def create_player(player_type: str, game):
    """Create a player function based on type.

    Returns:
        A callable that takes a game and returns a Move or None.
    """
    if player_type == "random":
        return get_random_move
    elif player_type == "llm":
        from komikan.llm import LLMProvider

        provider = LLMProvider("openai")
        return lambda g: get_llm_move(g, provider)
    else:
        return get_human_move


def main(argv: list[str] | None = None) -> None:
    """Main entry point for the CLI."""
    args = parse_args(argv)

    print_banner()

    # Import game setup
    from komikan.game import KomikanGame

    game = KomikanGame()

    player_factories = {
        "north": create_player(args.north, game),
        "south": create_player(args.south, game),
    }

    print(f"North: {args.north} | South: {args.south}")
    print()

    while game.status.value == "active":
        print_board(game)

        current_side = game.core_state.current_player.side.value
        if current_side == "pangui":
            player_fn = player_factories["north"]
        else:
            player_fn = player_factories["south"]

        move = player_fn(game)
        if move is None:
            print(f"No valid moves for {current_side}. Game over.")
            break

        success, msg = game.make_move(
            move.from_position[0],
            move.from_position[1],
            move.to_position[0],
            move.to_position[1],
        )

        if not success:
            print(f"Move failed: {msg}")
            continue

        if args.delay > 0:
            time.sleep(args.delay)

    # Final state
    print_board(game)
    print(f"Game over! Winner: {game.status.value}")


if __name__ == "__main__":
    main()
