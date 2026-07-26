#!/usr/bin/env python3

"""
Demo script: Launch game right before South wins.
Sets up a scenario where North has no valid moves, triggering South's win.
"""

import sys
from src.komikan.run import Game


class SouthWinDemoGame(Game):
    """Modified game class that starts with South about to win."""

    def setup_initial_positions(self):
        """Set up a scenario where South wins due to North having no moves."""
        # Clear any existing positions
        self.game_state.player_north.positions = []
        self.game_state.player_south.positions = []
        self.game_state.player_north.position_to_number.clear()
        self.game_state.player_south.position_to_number.clear()

        # Set up North player - in a corner with limited options
        north_pos = (0, 1)  # Corner-ish position
        self.game_state.player_north.positions = [north_pos]
        self.game_state.player_north.position_to_number[north_pos] = 1
        self.board.place_player(
            self.game_state.player_north, north_pos[0], north_pos[1]
        )

        # Set up South player - many tokens positioned to potentially block North
        # Keep more than 3 tokens so the win condition is "no valid moves" not "few tokens"
        south_positions = [
            # Positions that could block North's movement
            (1, 0),
            (0, 2),
            (1, 2),  # Adjacent to North
            (2, 0),
            (2, 1),
            (2, 2),  # Nearby positions
            # Additional tokens to keep count above 3
            (3, 6),
            (4, 6),
            (0, 7),
            (1, 7),
            (2, 7),
            (3, 7),
        ]

        # Assign positions and token numbers to South
        for i, pos in enumerate(south_positions):
            self.game_state.player_south.positions.append(pos)
            self.game_state.player_south.position_to_number[pos] = i + 1
            self.board.place_player(self.game_state.player_south, pos[0], pos[1])

        # Make it South's turn so they can make moves to block North
        self.game_state.current_player = self.game_state.player_south

        print("=== SOUTH WIN DEMO SCENARIO ===")
        print("South (blue) can win by blocking North's moves!")
        print(f"North position: {north_pos}")
        print(f"South positions: {south_positions}")
        print(f"South has {len(south_positions)} tokens (more than 3)")
        print("\nInstructions:")
        print("- It's South's turn - move South tokens to block North")
        print("- Try to surround North so it has no valid moves")
        print("- When North can't move, South wins!")
        print("- After game ends, press any key to restart")
        print("\nNote:")
        print("- This scenario is complex - you might need to play several moves")
        print("- The goal is to demonstrate the 'no valid moves' win condition")
        print("- Click South tokens to move them strategically")
        print("=" * 50)


class FullEndgameDemoGame(Game):
    """Demo that sets up both win conditions for comparison."""

    def setup_initial_positions(self):
        """Set up a scenario where either win condition could be demonstrated."""
        # Clear any existing positions
        self.game_state.player_north.positions = []
        self.game_state.player_south.positions = []
        self.game_state.player_north.position_to_number.clear()
        self.game_state.player_south.position_to_number.clear()

        # Set up North player in a good position to capture
        north_pos = (2, 3)  # Central position
        self.game_state.player_north.positions = [north_pos]
        self.game_state.player_north.position_to_number[north_pos] = 1
        self.board.place_player(
            self.game_state.player_north, north_pos[0], north_pos[1]
        )

        # Set up South player - exactly 4 tokens, some capturable
        south_positions = [
            (1, 4),  # Can be captured by North (2,3) -> (0,5)
            (3, 2),  # Can be captured by North (2,3) -> (4,1)
            (2, 5),  # Can be captured by North (2,3) -> (2,7)
            (0, 0),  # Safe distant position
        ]

        # Assign positions and token numbers to South
        for i, pos in enumerate(south_positions):
            self.game_state.player_south.positions.append(pos)
            self.game_state.player_south.position_to_number[pos] = i + 1
            self.board.place_player(self.game_state.player_south, pos[0], pos[1])

        print("=== FULL ENDGAME DEMO SCENARIO ===")
        print("Multiple win condition scenarios!")
        print(f"North position: {north_pos}")
        print(f"South positions: {south_positions}")
        print("South has 4 tokens - North can win by capturing any one!")
        print("\nMultiple capture options for North:")
        print("- Capture (1,4) by moving to (0,5)")
        print("- Capture (3,2) by moving to (4,1)")
        print("- Capture (2,5) by moving to (2,7)")
        print("\nTry different captures to see the win animation!")
        print("=" * 50)


def main():
    """Launch endgame demos with user choice."""
    print("Komikan Endgame Demo Launcher")
    print("Choose a demo scenario:")
    print("1. North wins (token count) - Easy win demo")
    print("2. South wins (no moves) - Strategic blocking demo")
    print("3. Multiple options - Full endgame demo")
    print("4. Exit")

    while True:
        try:
            choice = input("\nEnter choice (1-4): ").strip()

            if choice == "1":
                print("\nLaunching: North Win Demo...")
                from endgame_demo import EndgameDemoGame

                demo = EndgameDemoGame()
                demo.run()
                break
            elif choice == "2":
                print("\nLaunching: South Win Demo...")
                demo = SouthWinDemoGame()
                demo.run()
                break
            elif choice == "3":
                print("\nLaunching: Full Endgame Demo...")
                demo = FullEndgameDemoGame()
                demo.run()
                break
            elif choice == "4":
                print("Goodbye!")
                sys.exit(0)
            else:
                print("Invalid choice. Please enter 1, 2, 3, or 4.")
        except (KeyboardInterrupt, EOFError):
            print("\nGoodbye!")
            sys.exit(0)


if __name__ == "__main__":
    main()
