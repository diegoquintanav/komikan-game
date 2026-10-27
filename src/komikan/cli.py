"""CLI entry point for Komikan AI agent games.

Usage:
    komikan-agent [--provider openai|anthropic] [--model MODEL] [--side north|south]
                  [--opponent human|random] [--delay SECONDS] [--base-url URL]
"""

from __future__ import annotations

import argparse
import time

import httpx


DEFAULT_MODELS = {
    "openai": "gpt-4o",
    "anthropic": "claude-sonnet-4-20250514",
}


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        prog="komikan-agent",
        description="Play Komikan with an LLM agent via the REST API",
    )
    parser.add_argument(
        "--provider",
        default="openai",
        choices=["openai", "anthropic"],
        help="LLM provider (default: openai)",
    )
    parser.add_argument(
        "--model",
        default=None,
        help="Model name (default: gpt-4o for openai, claude-sonnet-4-20250514 for anthropic)",
    )
    parser.add_argument(
        "--side",
        default="north",
        choices=["north", "south"],
        help="Side the agent plays (default: north)",
    )
    parser.add_argument(
        "--opponent",
        default="random",
        choices=["human", "random"],
        help="Opponent type (default: random)",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=0.5,
        help="Delay in seconds between moves (default: 0.5)",
    )
    parser.add_argument(
        "--base-url",
        default="http://localhost:8000",
        help="Backend server URL (default: http://localhost:8000)",
    )
    return parser.parse_args(argv)


def print_banner() -> None:
    """Print the game banner."""
    print("=" * 40)
    print("  KOMIKAN - Mapuche Hunt Game")
    print("  LLM Agent Mode")
    print("=" * 40)


def print_board(game_state: dict) -> None:
    """Print the current board state from an API game state dict."""
    north = game_state.get("north_player", {})
    south = game_state.get("south_player", {})

    north_positions = set(tuple(p) for p in north.get("positions", []))
    south_positions = set(tuple(p) for p in south.get("positions", []))

    print()
    for y in range(8):
        row = []
        for x in range(5):
            if (x, y) in north_positions:
                row.append("N")
            elif (x, y) in south_positions:
                row.append("S")
            else:
                row.append(".")
        print(f"  {y}: {' '.join(row)}")
    print()


def print_game_info(game_state: dict) -> None:
    """Print current game metadata."""
    status = game_state.get("status", "unknown")
    current = game_state.get("current_player", "unknown")
    move_count = game_state.get("move_count", 0)
    north_count = game_state.get("north_player", {}).get("token_count", 0)
    south_count = game_state.get("south_player", {}).get("token_count", 0)
    print(f"  Status: {status} | Turn: {current} | Move #{move_count}")
    print(f"  North tokens: {north_count} | South tokens: {south_count}")


def fetch_game_state(client: httpx.Client, game_id: str) -> dict:
    """Fetch the current game state from the API."""
    resp = client.get(f"/api/games/{game_id}")
    resp.raise_for_status()
    data = resp.json()
    return data.get("game", data)


def create_game(client: httpx.Client) -> str:
    """Create a new game via the API and return the game_id."""
    resp = client.post("/api/games")
    resp.raise_for_status()
    data = resp.json()
    game = data.get("game", data)
    return game["game_id"]


def play_random_move(client: httpx.Client, game_id: str) -> dict | None:
    """Pick and execute a random legal move via the API. Returns the new game state or None."""
    resp = client.get(f"/api/games/{game_id}/all-valid-moves")
    resp.raise_for_status()
    data = resp.json()

    tokens = data.get("tokens", [])
    all_moves: list[dict] = []

    for token in tokens:
        from_x, from_y = token["position"]
        for m in token.get("moves", []):
            to_x, to_y = m["to"]
            all_moves.append(
                {
                    "from_x": from_x,
                    "from_y": from_y,
                    "to_x": to_x,
                    "to_y": to_y,
                }
            )

    if not all_moves:
        return None

    import random

    move = random.choice(all_moves)
    move_resp = client.post(f"/api/games/{game_id}/moves", json=move)
    move_resp.raise_for_status()
    result = move_resp.json()
    return result.get("game", result)


def main(argv: list[str] | None = None) -> None:
    """Main entry point for the CLI."""
    args = parse_args(argv)

    print_banner()

    model = args.model or DEFAULT_MODELS[args.provider]
    print(f"  Provider: {args.provider} | Model: {model}")
    print(f"  Agent plays: {args.side} | Opponent: {args.opponent}")
    print()

    SIDE_MAP = {"north": "pangui", "south": "pu trewa"}
    api_side = SIDE_MAP[args.side]

    # Resolve API keys
    import os

    if args.provider == "openai":
        api_key = os.environ.get("OPENAI_API_KEY", "")
        if not api_key:
            print("Error: OPENAI_API_KEY environment variable is not set.")
            return
    else:
        api_key = os.environ.get("ANTHROPIC_API_KEY", "")
        if not api_key:
            print("Error: ANTHROPIC_API_KEY environment variable is not set.")
            return

    # Create provider
    from komikan.agent.factory import create_provider

    provider = create_provider(args.provider, api_key=api_key, model=model)

    # Connect to API and create game
    client = httpx.Client(base_url=args.base_url.rstrip("/"), timeout=10.0)

    try:
        client.get("/").raise_for_status()
    except httpx.ConnectError:
        print(f"Error: Cannot connect to API server at {args.base_url}")
        print("Start the server with: komikan-api")
        return

    game_id = create_game(client)
    print(f"  Game created: {game_id}")
    print()

    # Create agent
    from komikan.agent.agent import KomikanAgent

    agent = KomikanAgent(
        provider=provider,
        base_url=args.base_url,
        game_id=game_id,
        side=args.side,
    )

    # Game loop
    max_turns = 200
    for turn in range(max_turns):
        game_state = fetch_game_state(client, game_id)
        status = game_state.get("status", "unknown")

        if status != "active":
            break

        current_player = game_state.get("current_player", "")
        move_count = game_state.get("move_count", 0)

        print(f"--- Turn {move_count + 1} ---")
        print_board(game_state)
        print_game_info(game_state)

        if current_player == api_side:
            print(f"  Agent ({args.provider}/{model}) is thinking...")
            result = agent.play_turn()

            if result is None:
                print("  Agent could not play (not its turn).")
                continue

            new_status = result.get("status", status)
            if new_status != "active":
                game_state = fetch_game_state(client, game_id)
                print_board(game_state)
                print(f"  Game over: {game_state.get('status', 'unknown')}")
                break
        else:
            if args.opponent == "random":
                print("  Opponent (random) is playing...")
                play_random_move(client, game_id)
            else:
                print("  Human opponent — enter your move.")
                _play_human_turn(client, game_id)

        if args.delay > 0:
            time.sleep(args.delay)

    # Final state
    game_state = fetch_game_state(client, game_id)
    final_status = game_state.get("status", "unknown")
    print_board(game_state)
    print_game_info(game_state)
    print(f"Game over! Result: {final_status}")

    client.close()


def _play_human_turn(client: httpx.Client, game_id: str) -> None:
    """Prompt human for a move and execute it via the API."""
    resp = client.get(f"/api/games/{game_id}/all-valid-moves")
    resp.raise_for_status()
    data = resp.json()

    tokens = data.get("tokens", [])
    all_moves: list[tuple[tuple[int, int], tuple[int, int]]] = []

    print("  Available moves:")
    for token in tokens:
        from_x, from_y = token["position"]
        for m in token.get("moves", []):
            to_x, to_y = m["to"]
            print(f"    {from_x},{from_y} -> {to_x},{to_y}")
            all_moves.append(((from_x, from_y), (to_x, to_y)))

    while True:
        try:
            raw = input("  Your move (from_x,from_y to_x,to_y): ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return

        if not raw:
            continue

        parts = raw.replace("->", " ").split()
        if len(parts) != 2:
            print("  Invalid format. Use: from_x,from_y to_x,to_y")
            continue

        try:
            from_parts = parts[0].split(",")
            to_parts = parts[1].split(",")
            from_pos = (int(from_parts[0]), int(from_parts[1]))
            to_pos = (int(to_parts[0]), int(to_parts[1]))
        except (ValueError, IndexError):
            print("  Invalid numbers. Use: from_x,from_y to_x,to_y")
            continue

        if (from_pos, to_pos) in all_moves:
            move = {
                "from_x": from_pos[0],
                "from_y": from_pos[1],
                "to_x": to_pos[0],
                "to_y": to_pos[1],
            }
            move_resp = client.post(f"/api/games/{game_id}/moves", json=move)
            if move_resp.status_code == 200:
                break
            print(f"  Move rejected: {move_resp.json().get('detail', 'unknown error')}")
        else:
            print("  Invalid move. Check available moves and try again.")


if __name__ == "__main__":
    main()
