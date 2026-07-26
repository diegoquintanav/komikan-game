#!/usr/bin/env python3

"""
Direct capture test - bypasses normal game flow to test capture and win condition directly.
"""

import pygame
import sys
from src.komikan.run import Game, BACKGROUND_COLOR


class DirectCaptureTest(Game):
    """Test that directly executes a capture and checks the win condition."""

    def __init__(self):
        super().__init__()
        self.auto_capture_done = False

    def setup_initial_positions(self):
        """Set up the exact scenario for testing."""
        # Clear any existing positions
        self.game_state.player_north.positions = []
        self.game_state.player_south.positions = []
        self.game_state.player_north.position_to_number.clear()
        self.game_state.player_south.position_to_number.clear()

        # North at (2,2)
        north_pos = (2, 2)
        self.game_state.player_north.positions = [north_pos]
        self.game_state.player_north.position_to_number[north_pos] = 1
        self.board.place_player(
            self.game_state.player_north, north_pos[0], north_pos[1]
        )

        # South with 4 tokens including capturable one
        south_positions = [(2, 3), (3, 6), (0, 7), (4, 7)]
        for i, pos in enumerate(south_positions):
            self.game_state.player_south.positions.append(pos)
            self.game_state.player_south.position_to_number[pos] = i + 1
            self.board.place_player(self.game_state.player_south, pos[0], pos[1])

        print("=== DIRECT CAPTURE TEST ===")
        print("Initial state:")
        print(f"  North: {self.game_state.player_north.positions}")
        print(
            f"  South: {self.game_state.player_south.positions} ({len(self.game_state.player_south.positions)} tokens)"
        )
        print("Will auto-execute capture in 2 seconds...")

    def run(self):
        """Modified run loop that auto-executes the capture."""
        running = True
        start_time = pygame.time.get_ticks()

        while running:
            current_time = pygame.time.get_ticks()

            # Auto-execute capture after 2 seconds
            if not self.auto_capture_done and current_time - start_time > 2000:
                self.execute_test_capture()
                self.auto_capture_done = True

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif self.game_state.game_over:
                        print("🔄 Restarting game...")
                        self.restart_game()
                        self.auto_capture_done = False
                        start_time = pygame.time.get_ticks()

            # Render
            self.screen.fill(BACKGROUND_COLOR)
            self.renderer.draw_grid()
            self.renderer.draw_coordinate_labels()
            self.renderer.draw_nodes(
                self.board, self.game_state, self.selected_position, self.valid_moves
            )
            self.renderer.draw_ui(self.game_state)

            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()
        sys.exit()

    def execute_test_capture(self):
        """Directly execute the capture and test win condition."""
        print("\n🚀 EXECUTING TEST CAPTURE...")

        # Check if capture is valid first
        from_x, from_y = 2, 2
        to_x, to_y = 2, 4

        is_valid = self.board.is_valid_capture(
            from_x, from_y, to_x, to_y, self.game_state.player_north
        )
        print(f"Capture valid: {is_valid}")

        if not is_valid:
            print("❌ Capture is not valid!")
            return

        # Execute the capture manually
        print("Executing capture move...")
        success, captured_player = self.board.capture_move(
            self.game_state.player_north, from_x, from_y, to_x, to_y
        )
        print(f"Capture success: {success}, captured player: {captured_player}")

        if success and captured_player:
            # Remove captured piece (at middle position 2,3)
            captured_pos = (2, 3)
            if captured_pos in self.game_state.player_south.positions:
                self.game_state.player_south.positions.remove(captured_pos)
                self.game_state.player_south.remove_token(captured_pos)
                print(f"Removed South token at {captured_pos}")

            # Move North token
            old_pos = (2, 2)
            new_pos = (2, 4)
            if old_pos in self.game_state.player_north.positions:
                self.game_state.player_north.positions.remove(old_pos)
                self.game_state.player_north.positions.append(new_pos)
                self.game_state.player_north.move_token(old_pos, new_pos)
                print(f"Moved North from {old_pos} to {new_pos}")

            print("\nAfter capture:")
            print(f"  North: {self.game_state.player_north.positions}")
            print(
                f"  South: {self.game_state.player_south.positions} ({len(self.game_state.player_south.positions)} tokens)"
            )

            # Now check win condition
            print("\n🏆 Checking win condition...")
            is_game_over, winner_message = self.game_state.check_win_condition(
                self.board
            )
            print(f"Game over: {is_game_over}")
            print(f"Winner message: '{winner_message}'")

            if is_game_over:
                print("✅ Win condition detected! Setting game over state...")
                self.game_state.game_over = True
                self.game_state.winner_message = winner_message
                print(f"Game state - game_over: {self.game_state.game_over}")
                print(
                    f"Game state - winner_message: '{self.game_state.winner_message}'"
                )
                print("🎉 POPUP SHOULD NOW BE VISIBLE! 🎉")
            else:
                print("❌ Win condition not triggered")
        else:
            print("❌ Capture failed")


def main():
    print("Starting Direct Capture Test...")
    print("This will automatically execute a capture move and show debug info.")

    test = DirectCaptureTest()
    test.run()


if __name__ == "__main__":
    main()
