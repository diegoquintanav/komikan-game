#!/usr/bin/env python3

"""
Demo script: Launch game right before North wins.
Sets up a scenario where South has 4 tokens and North can capture one to win.
"""

from src.komikan.run import Game


class EndgameDemoGame(Game):
    """Modified game class that starts with a pre-configured endgame scenario."""

    def setup_initial_positions(self):
        """Set up a scenario where North is about to win."""
        # Clear any existing positions
        self.game_state.player_north.positions = []
        self.game_state.player_south.positions = []
        self.game_state.player_north.position_to_number.clear()
        self.game_state.player_south.position_to_number.clear()

        # Set up North player - positioned to capture a South token
        north_pos = (2, 4)  # Central position
        self.game_state.player_north.positions = [north_pos]
        self.game_state.player_north.position_to_number[north_pos] = 1
        self.board.place_player(
            self.game_state.player_north, north_pos[0], north_pos[1]
        )

        # Set up South player - only 4 tokens remaining (one capture away from North winning)
        south_positions = [
            (1, 5),  # Can be captured by North from (2, 4) -> jump to (0, 6)
            (3, 6),  # Safe position
            (0, 7),  # Safe position
            (4, 7),  # Safe position
        ]

        # Assign positions and token numbers to South
        for i, pos in enumerate(south_positions):
            self.game_state.player_south.positions.append(pos)
            self.game_state.player_south.position_to_number[pos] = i + 1
            self.board.place_player(self.game_state.player_south, pos[0], pos[1])

        print("=== ENDGAME DEMO SCENARIO ===")
        print("North (red) is positioned to win!")
        print(f"North position: {north_pos}")
        print(f"South positions: {south_positions}")
        print("South has 4 tokens - North needs to capture 1 to win!")
        print("\nInstructions:")
        print("- North can capture the South token at (1,5) by moving to (0,6)")
        print("- Use mouse click or keyboard (A key) to move North left and capture")
        print("- This will reduce South to 3 tokens and trigger North's win!")
        print("- After game ends, press any key to restart")
        print("\nControls:")
        print("- Click to select North token, then click (0,6) to capture")
        print("- Or press A key to move left and capture")
        print("- ESC twice to exit")
        print("=" * 50)


def main():
    """Launch the endgame demo."""
    print("Starting Komikan Endgame Demo...")
    print("This demo shows North about to win by reducing South to 3 tokens.")

    # Create and run the demo game
    demo_game = EndgameDemoGame()
    demo_game.run()


if __name__ == "__main__":
    main()
