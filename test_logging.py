#!/usr/bin/env python3
"""
Test script to demonstrate the debug logging functionality.
This script shows how to analyze the log files for game replay.
"""

import os
import json


def parse_game_log(log_file="komikan_game.log"):
    """Parse the game log file and extract game events."""
    if not os.path.exists(log_file):
        print(f"Log file {log_file} not found.")
        print("Run the game with KOMIKAN_DEBUG=1 to generate logs.")
        return

    print("=== KOMIKAN GAME LOG ANALYSIS ===")
    print(f"Log file: {log_file}")
    print(f"File size: {os.path.getsize(log_file)} bytes")
    print()

    game_events = []
    game_info = {}

    with open(log_file, "r") as f:
        for line in f:
            line = line.strip()

            # Parse game start info
            if "=== KOMIKAN GAME STARTED ===" in line:
                game_info["start_marker"] = line
            elif "Game start time:" in line:
                # Extract timestamp
                timestamp = line.split("Game start time: ")[1]
                game_info["start_time"] = timestamp
            elif "North player:" in line or "South player:" in line:
                game_info.setdefault("player_info", []).append(
                    line.split(" - INFO - ")[1]
                )

            # Parse game events (JSON format)
            elif "GAME_EVENT:" in line:
                try:
                    json_part = line.split("GAME_EVENT: ")[1]
                    event = json.loads(json_part)
                    game_events.append(event)
                except (IndexError, json.JSONDecodeError):
                    print(f"Warning: Could not parse event: {line}")

            # Parse move attempts and results
            elif any(
                keyword in line
                for keyword in [
                    "MOVE ATTEMPT",
                    "CAPTURE ATTEMPT",
                    "MOVE SUCCESS",
                    "CAPTURE SUCCESS",
                    "MOVE FAILED",
                ]
            ):
                # Extract readable move info
                if (
                    " - DEBUG - " in line
                    or " - INFO - " in line
                    or " - WARNING - " in line
                ):
                    timestamp = line.split(" - ")[0]
                    level = line.split(" - ")[1]
                    message = " - ".join(line.split(" - ")[2:])
                    print(f"[{timestamp}] {level}: {message}")

    # Display game information
    print("\n=== GAME INFORMATION ===")
    if "start_time" in game_info:
        print(f"Game started: {game_info['start_time']}")
    if "player_info" in game_info:
        for info in game_info["player_info"]:
            print(f"  {info}")

    # Display structured events
    if game_events:
        print(f"\n=== STRUCTURED GAME EVENTS ({len(game_events)} total) ===")
        for i, event in enumerate(game_events, 1):
            print(f"\nEvent {i}:")
            print(f"  Move #: {event.get('move_number', 'N/A')}")
            print(f"  Player: {event.get('player', 'N/A')}")
            print(f"  Action: {event.get('action_type', 'N/A')}")
            print(f"  From: {event.get('from_position', 'N/A')}")
            print(f"  To: {event.get('to_position', 'N/A')}")
            print(f"  Success: {event.get('success', 'N/A')}")
            if event.get("token_number"):
                print(f"  Token #: {event.get('token_number')}")
            if event.get("captured_token_number"):
                print(f"  Captured Token #: {event.get('captured_token_number')}")
            if event.get("failure_reason"):
                print(f"  Failure Reason: {event.get('failure_reason')}")
            print(f"  Game Time: {event.get('game_time_seconds', 0):.2f}s")
    else:
        print("\nNo structured game events found.")
        print("Play some moves in the game to generate move logs!")

    print("\n=== REPLAY INSTRUCTIONS ===")
    print("To replay the game:")
    print("1. Start with north player at (2, 0)")
    print("2. Place south player tokens at starting positions (bottom two rows)")
    print("3. Follow the moves in chronological order:")
    for i, event in enumerate(game_events, 1):
        if event.get("success"):
            action = "CAPTURE" if event.get("is_capture_attempt") else "MOVE"
            player = event.get("player", "unknown").upper()
            from_pos = event.get("from_position")
            to_pos = event.get("to_position")
            print(f"   Step {i}: {player} {action} from {from_pos} to {to_pos}")
            if event.get("captured_token_number"):
                print(
                    f"             (Captured south token #{event.get('captured_token_number')})"
                )


def main():
    """Main function to analyze game logs."""
    print("Komikan Game Log Analyzer")
    print("=" * 50)

    # Check if log file exists
    log_files = [f for f in os.listdir(".") if f.endswith(".log")]

    if not log_files:
        print("No log files found in current directory.")
        print("\nTo generate logs:")
        print("  KOMIKAN_DEBUG=1 uv run python main.py")
        print("\nThen play some moves and run this script again.")
        return

    # Analyze the most recent log file
    log_file = "komikan_game.log"  # Default log file name
    if os.path.exists(log_file):
        parse_game_log(log_file)
    else:
        # Use the first available log file
        log_file = log_files[0]
        print(f"Using log file: {log_file}")
        parse_game_log(log_file)


if __name__ == "__main__":
    main()
