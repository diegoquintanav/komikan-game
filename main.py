"""
Komikan Board Game - Main Entry Point
A 5x8 node grid game where two players start on opposite sides and move orthogonally/diagonally.
"""
import pygame
import sys
from board import GameBoard
from player import GameState, PlayerSide


# Constants
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
BOARD_MARGIN = 100
NODE_RADIUS = 20
GRID_COLOR = (100, 100, 100)
BACKGROUND_COLOR = (240, 240, 240)
SELECTED_COLOR = (255, 255, 0)
VALID_MOVE_COLOR = (100, 255, 100)


class GameRenderer:
    """Handles all game rendering."""

    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.Font(None, 36)

        # Calculate grid layout
        self.grid_width = WINDOW_WIDTH - 2 * BOARD_MARGIN
        self.grid_height = WINDOW_HEIGHT - 2 * BOARD_MARGIN
        self.node_spacing_x = self.grid_width // (GameBoard.WIDTH - 1)
        self.node_spacing_y = self.grid_height // (GameBoard.HEIGHT - 1)

    def get_node_screen_pos(self, x: int, y: int) -> tuple[int, int]:
        """Convert board coordinates to screen coordinates."""
        screen_x = BOARD_MARGIN + x * self.node_spacing_x
        screen_y = BOARD_MARGIN + y * self.node_spacing_y
        return screen_x, screen_y

    def get_board_pos_from_screen(self, screen_x: int, screen_y: int) -> tuple[int, int]:
        """Convert screen coordinates to board coordinates (nearest node)."""
        board_x = round((screen_x - BOARD_MARGIN) / self.node_spacing_x)
        board_y = round((screen_y - BOARD_MARGIN) / self.node_spacing_y)
        return board_x, board_y

    def draw_grid(self):
        """Draw the game board grid."""
        # Draw horizontal lines
        for y in range(GameBoard.HEIGHT):
            start_pos = self.get_node_screen_pos(0, y)
            end_pos = self.get_node_screen_pos(GameBoard.WIDTH - 1, y)
            pygame.draw.line(self.screen, GRID_COLOR, start_pos, end_pos, 2)

        # Draw vertical lines
        for x in range(GameBoard.WIDTH):
            start_pos = self.get_node_screen_pos(x, 0)
            end_pos = self.get_node_screen_pos(x, GameBoard.HEIGHT - 1)
            pygame.draw.line(self.screen, GRID_COLOR, start_pos, end_pos, 2)

    def draw_nodes(self, board: GameBoard, game_state: GameState, selected_pos=None, valid_moves=None):
        """Draw all nodes and players."""
        for y in range(GameBoard.HEIGHT):
            for x in range(GameBoard.WIDTH):
                screen_pos = self.get_node_screen_pos(x, y)
                node = board.get_node(x, y)

                # Draw node circle
                if selected_pos == (x, y):
                    pygame.draw.circle(self.screen, SELECTED_COLOR, screen_pos, NODE_RADIUS + 5)
                elif valid_moves and (x, y) in valid_moves:
                    pygame.draw.circle(self.screen, VALID_MOVE_COLOR, screen_pos, NODE_RADIUS + 3)

                pygame.draw.circle(self.screen, GRID_COLOR, screen_pos, NODE_RADIUS, 3)

                # Draw player if present
                if node and node.is_occupied():
                    pygame.draw.circle(self.screen, node.occupied_by.color, screen_pos, NODE_RADIUS - 3)

    def draw_ui(self, game_state: GameState):
        """Draw game UI elements."""
        # Current player indicator
        player_text = f"Current Player: {game_state.current_player.side.value.title()}"
        text_surface = self.font.render(player_text, True, game_state.current_player.color)
        self.screen.blit(text_surface, (10, 10))

        # Instructions
        instructions = [
            "Click to select your piece",
            "Click adjacent node to move",
            "Right-click to deselect"
        ]
        for i, instruction in enumerate(instructions):
            text_surface = pygame.font.Font(None, 24).render(instruction, True, (50, 50, 50))
            self.screen.blit(text_surface, (10, WINDOW_HEIGHT - 80 + i * 20))


class Game:
    """Main game controller."""

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Komikan Board Game")
        self.clock = pygame.time.Clock()

        # Game objects
        self.board = GameBoard()
        self.game_state = GameState()
        self.renderer = GameRenderer(self.screen)

        # Game state
        self.selected_position = None
        self.valid_moves = []

        # Initialize player positions
        self.setup_initial_positions()

    def setup_initial_positions(self):
        """Place players at their starting positions."""
        # Place north player at center of top row
        self.board.place_player(self.game_state.player_north, 2, 0)

        # Place south player at center of bottom row
        self.board.place_player(self.game_state.player_south, 2, 7)

    def handle_click(self, pos: tuple[int, int], button: int):
        """Handle mouse click events."""
        board_x, board_y = self.renderer.get_board_pos_from_screen(pos[0], pos[1])

        if not self.board.is_valid_position(board_x, board_y):
            return

        if button == 1:  # Left click
            if self.selected_position:
                # Try to move to clicked position
                if (board_x, board_y) in self.valid_moves:
                    success = self.board.move_player(
                        self.game_state.current_player,
                        self.selected_position[0], self.selected_position[1],
                        board_x, board_y
                    )
                    if success:
                        self.selected_position = None
                        self.valid_moves = []
                        self.game_state.switch_turn()
                else:
                    # Select new piece
                    self.try_select_piece(board_x, board_y)
            else:
                # Select piece
                self.try_select_piece(board_x, board_y)

        elif button == 3:  # Right click - deselect
            self.selected_position = None
            self.valid_moves = []

    def try_select_piece(self, x: int, y: int):
        """Try to select a piece at the given position."""
        node = self.board.get_node(x, y)
        if (node and node.is_occupied() and
            node.occupied_by == self.game_state.current_player):
            self.selected_position = (x, y)
            self.valid_moves = [
                (mx, my) for mx, my in self.board.get_adjacent_positions(x, y)
                if self.board.is_valid_move(x, y, mx, my)
            ]
        else:
            self.selected_position = None
            self.valid_moves = []

    def run(self):
        """Main game loop."""
        running = True

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_click(event.pos, event.button)

            # Render
            self.screen.fill(BACKGROUND_COLOR)
            self.renderer.draw_grid()
            self.renderer.draw_nodes(
                self.board, self.game_state,
                self.selected_position, self.valid_moves
            )
            self.renderer.draw_ui(self.game_state)

            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()
        sys.exit()


def main():
    """Entry point for the Komikan board game."""
    game = Game()
    game.run()


if __name__ == "__main__":
    main()
