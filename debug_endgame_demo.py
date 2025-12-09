#!/usr/bin/env python3

"""
Debug version of endgame demo to track win condition checking.
"""

import pygame
from src.komikan.run import Game


class DebugEndgameDemoGame(Game):
    """Debug version with extra logging."""

    def check_win_condition(self):
        """Debug version of win condition checking."""
        print("\n🔍 DEBUG: Checking win condition...")
        print(f"  North tokens: {len(self.game_state.player_north.positions)}")
        print(f"  South tokens: {len(self.game_state.player_south.positions)}")
        print(f"  Current game_over state: {self.game_state.game_over}")

        is_game_over, winner_message = self.game_state.check_win_condition(self.board)
        print(
            f"  Win check result: game_over={is_game_over}, message='{winner_message}'"
        )

        if is_game_over and not self.game_state.game_over:
            print("🎉 DEBUG: Setting game over state!")
            self.game_state.game_over = True
            self.game_state.winner_message = winner_message
            print(f"  Game state updated: game_over={self.game_state.game_over}")
            print(f"  Winner message set: '{self.game_state.winner_message}'")
        elif is_game_over and self.game_state.game_over:
            print("ℹ️ DEBUG: Game was already over")
        else:
            print("ℹ️ DEBUG: Game continues...")

    def handle_keyboard(self, key):
        """Debug version of keyboard handler."""
        print(f"\n⌨️ DEBUG: Key pressed: {pygame.key.name(key)}")

        # Call the parent method
        super().handle_keyboard(key)

        # Print state after handling
        print("  After handling key:")
        print(f"  - Game over: {self.game_state.game_over}")
        print(f"  - Selected position: {self.selected_position}")

    def handle_click(self, pos, button):
        """Debug version of mouse handler."""
        print(f"\n🖱️ DEBUG: Mouse clicked at {pos}, button {button}")

        # Call the parent method
        super().handle_click(pos, button)

        # Print state after handling
        print("  After handling click:")
        print(f"  - Game over: {self.game_state.game_over}")
        print(f"  - Selected position: {self.selected_position}")

    def setup_initial_positions(self):
        """Set up the debug endgame scenario."""
        # Clear any existing positions
        self.game_state.player_north.positions = []
        self.game_state.player_south.positions = []
        self.game_state.player_north.position_to_number.clear()
        self.game_state.player_south.position_to_number.clear()

        # Set up North player - positioned to capture a South token
        north_pos = (2, 2)  # Position where North can make a valid capture
        self.game_state.player_north.positions = [north_pos]
        self.game_state.player_north.position_to_number[north_pos] = 1
        self.board.place_player(
            self.game_state.player_north, north_pos[0], north_pos[1]
        )

        # Set up South player - only 4 tokens remaining
        south_positions = [
            (2, 3),  # Can be captured by North from (2, 2) -> jump to (2, 4)
            (3, 6),  # Safe position
            (0, 7),  # Safe position
            (4, 7),  # Safe position
        ]

        # Assign positions and token numbers to South
        for i, pos in enumerate(south_positions):
            self.game_state.player_south.positions.append(pos)
            self.game_state.player_south.position_to_number[pos] = i + 1
            self.board.place_player(self.game_state.player_south, pos[0], pos[1])

        print("=== DEBUG ENDGAME DEMO ===")
        print("This version includes debug output to track win condition checking")
        print(f"North position: {north_pos}")
        print(f"South positions: {south_positions}")
        print("Make the capture move and watch the debug output!")
        print("Press S key or click (2,4) to capture and win")
        print("=" * 50)


def main():
    """Launch the debug endgame demo."""
    print("Starting DEBUG Komikan Endgame Demo...")

    # Create and run the debug demo game
    demo_game = DebugEndgameDemoGame()
    demo_game.run()


if __name__ == "__main__":
    main()
