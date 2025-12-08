"""
Komikan Board Game - Main Entry Point
A 5x8 node grid game where two players start on opposite sides and move orthogonally/diagonally.
"""

import pygame
import sys
from board import GameBoard
from player import GameState, PlayerSide
import os


DEBUG_MODE = os.getenv("KOMIKAN_DEBUG", "0") == "1"

# Constants
WINDOW_WIDTH = 500
WINDOW_HEIGHT = 600
BOARD_MARGIN = 100
NODE_RADIUS = 5
TOKEN_RADIUS = 15
GRID_COLOR = (100, 100, 100)
BACKGROUND_COLOR = (240, 240, 240)
SELECTED_COLOR = (255, 255, 0)
VALID_MOVE_COLOR = (100, 255, 100)
ACTIVE_PLAYER_COLOR = (255, 215, 0)

if DEBUG_MODE:
    DISABLED_NODE_COLOR = (150, 150, 150)
    DISABLED_PATH_COLOR = (90, 90, 90)
else:
    DISABLED_NODE_COLOR = BACKGROUND_COLOR
    DISABLED_PATH_COLOR = BACKGROUND_COLOR


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

    def get_board_pos_from_screen(
        self, screen_x: int, screen_y: int
    ) -> tuple[int, int]:
        """Convert screen coordinates to board coordinates (nearest node)."""
        board_x = round((screen_x - BOARD_MARGIN) / self.node_spacing_x)
        board_y = round((screen_y - BOARD_MARGIN) / self.node_spacing_y)
        return board_x, board_y

    def draw_dashed_line(self, start_pos, end_pos, color, dash_length=8):
        """Draw a dashed line between two points."""
        x1, y1 = start_pos
        x2, y2 = end_pos

        # Calculate total distance and direction
        dx = x2 - x1
        dy = y2 - y1
        distance = (dx**2 + dy**2) ** 0.5

        if distance == 0:
            return

        # Normalize direction
        dx_norm = dx / distance
        dy_norm = dy / distance

        # Draw dashes
        current_distance = 0
        while current_distance < distance:
            # Start of dash
            dash_start_x = x1 + dx_norm * current_distance
            dash_start_y = y1 + dy_norm * current_distance

            # End of dash
            dash_end_distance = min(current_distance + dash_length, distance)
            dash_end_x = x1 + dx_norm * dash_end_distance
            dash_end_y = y1 + dy_norm * dash_end_distance

            # Draw the dash
            pygame.draw.line(
                self.screen,
                color,
                (int(dash_start_x), int(dash_start_y)),
                (int(dash_end_x), int(dash_end_y)),
                2,
            )

            # Move to next dash (skip gap)
            current_distance += dash_length * 2

    def draw_grid(self):
        """Draw the game board grid."""
        # Create a temporary GameBoard instance to check disabled paths
        board = GameBoard()

        # Draw horizontal lines
        for y in range(GameBoard.HEIGHT):
            for x in range(GameBoard.WIDTH - 1):
                start_pos = self.get_node_screen_pos(x, y)
                end_pos = self.get_node_screen_pos(x + 1, y)

                if board.is_disabled_path(x, y, x + 1, y):
                    self.draw_dashed_line(start_pos, end_pos, DISABLED_PATH_COLOR)
                else:
                    pygame.draw.line(self.screen, GRID_COLOR, start_pos, end_pos, 2)

        # Draw vertical lines
        for x in range(GameBoard.WIDTH):
            for y in range(GameBoard.HEIGHT - 1):
                start_pos = self.get_node_screen_pos(x, y)
                end_pos = self.get_node_screen_pos(x, y + 1)

                if board.is_disabled_path(x, y, x, y + 1):
                    self.draw_dashed_line(start_pos, end_pos, DISABLED_PATH_COLOR)
                else:
                    pygame.draw.line(self.screen, GRID_COLOR, start_pos, end_pos, 2)

        # Draw diagonal lines
        for y in range(GameBoard.HEIGHT):
            for x in range(GameBoard.WIDTH):
                current_pos = self.get_node_screen_pos(x, y)

                # Draw diagonal line to bottom-right neighbor
                if x < GameBoard.WIDTH - 1 and y < GameBoard.HEIGHT - 1:
                    neighbor_pos = self.get_node_screen_pos(x + 1, y + 1)
                    if board.is_disabled_path(x, y, x + 1, y + 1):
                        self.draw_dashed_line(
                            current_pos, neighbor_pos, DISABLED_PATH_COLOR
                        )
                    else:
                        pygame.draw.line(
                            self.screen,
                            GRID_COLOR,
                            current_pos,
                            neighbor_pos,
                            2,
                        )

                # Draw diagonal line to bottom-left neighbor
                if x > 0 and y < GameBoard.HEIGHT - 1:
                    neighbor_pos = self.get_node_screen_pos(x - 1, y + 1)
                    if board.is_disabled_path(x, y, x - 1, y + 1):
                        self.draw_dashed_line(
                            current_pos, neighbor_pos, DISABLED_PATH_COLOR
                        )
                    else:
                        pygame.draw.line(
                            self.screen, GRID_COLOR, current_pos, neighbor_pos, 1
                        )

    def draw_nodes(
        self,
        board: GameBoard,
        game_state: GameState,
        selected_pos=None,
        valid_moves=None,
    ):
        """Draw all nodes and players."""
        for y in range(GameBoard.HEIGHT):
            for x in range(GameBoard.WIDTH):
                screen_pos = self.get_node_screen_pos(x, y)
                node = board.get_node(x, y)

                # Check if this is the active player's position
                is_active_player = (
                    node
                    and node.is_occupied()
                    and node.occupied_by == game_state.current_player
                )

                # Check if this node is disabled
                is_disabled = board.is_disabled_node(x, y)

                # Draw node circle highlights
                if is_disabled:
                    # Draw disabled node with X mark
                    pygame.draw.circle(
                        self.screen, DISABLED_NODE_COLOR, screen_pos, NODE_RADIUS, 0
                    )
                    pygame.draw.line(
                        self.screen,
                        BACKGROUND_COLOR,
                        (screen_pos[0] - 10, screen_pos[1] - 10),
                        (screen_pos[0] + 10, screen_pos[1] + 10),
                        3,
                    )
                    pygame.draw.line(
                        self.screen,
                        BACKGROUND_COLOR,
                        (screen_pos[0] - 10, screen_pos[1] + 10),
                        (screen_pos[0] + 10, screen_pos[1] - 10),
                        3,
                    )
                elif selected_pos == (x, y):
                    pygame.draw.circle(
                        self.screen, SELECTED_COLOR, screen_pos, TOKEN_RADIUS + 5
                    )
                elif valid_moves and (x, y) in valid_moves:
                    pygame.draw.circle(
                        self.screen, VALID_MOVE_COLOR, screen_pos, TOKEN_RADIUS + 3
                    )
                elif is_active_player:
                    # Highlight active player with pulsing gold ring
                    pygame.draw.circle(
                        self.screen, ACTIVE_PLAYER_COLOR, screen_pos, TOKEN_RADIUS + 4, 3
                    )

                if not is_disabled:
                    pygame.draw.circle(
                        self.screen, GRID_COLOR, screen_pos, NODE_RADIUS, 3
                    )

                    # Draw player if present
                    if node and node.is_occupied():
                        pygame.draw.circle(
                            self.screen,
                            node.occupied_by.color,
                            screen_pos,
                            TOKEN_RADIUS - 3,
                        )

                        # Draw token number
                        token_number = node.occupied_by.get_token_number(x, y)
                        if token_number > 0:
                            number_font = pygame.font.Font(None, 20)
                            number_text = str(token_number)
                            text_surface = number_font.render(number_text, True, (255, 255, 255))
                            text_rect = text_surface.get_rect(center=screen_pos)
                            self.screen.blit(text_surface, text_rect)

    def draw_coordinate_labels(self):
        """Draw coordinate labels for X and Y axes."""
        label_font = pygame.font.Font(None, 24)
        label_color = (80, 80, 80)

        # Draw X axis labels (0-4) at the top
        for x in range(GameBoard.WIDTH):
            screen_pos = self.get_node_screen_pos(x, 0)
            label_text = str(x)
            text_surface = label_font.render(label_text, True, label_color)
            text_rect = text_surface.get_rect()
            text_rect.centerx = screen_pos[0]
            text_rect.bottom = screen_pos[1] - 30
            self.screen.blit(text_surface, text_rect)

        # Draw Y axis labels (0-7) on the left
        for y in range(GameBoard.HEIGHT):
            screen_pos = self.get_node_screen_pos(0, y)
            label_text = str(y)
            text_surface = label_font.render(label_text, True, label_color)
            text_rect = text_surface.get_rect()
            text_rect.right = screen_pos[0] - 30
            text_rect.centery = screen_pos[1]
            self.screen.blit(text_surface, text_rect)

    def draw_ui(self, game_state: GameState):
        """Draw game UI elements."""
        # Current player indicator
        player_text = f"Current Player: {game_state.current_player.side.value.title()}"
        text_surface = self.font.render(
            player_text, True, game_state.current_player.color
        )
        self.screen.blit(text_surface, (10, 10))

        # Instructions
        instructions = [
            "Mouse: Click to select/move | Right-click to deselect",
            "Keyboard: WASD/Arrows to move | QE/ZC for diagonals",
            "ESC to deselect | Double ESC to exit | Auto-selects your piece on key press",
        ]
        for i, instruction in enumerate(instructions):
            text_surface = pygame.font.Font(None, 22).render(
                instruction, True, (50, 50, 50)
            )
            self.screen.blit(text_surface, (10, WINDOW_HEIGHT - 70 + i * 18))


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

        # ESC key exit tracking
        self.esc_pressed_time = None
        self.esc_timeout = 2000  # 2 seconds in milliseconds

        # Initialize player positions
        self.setup_initial_positions()

    def setup_initial_positions(self):
        """Place players at their starting positions."""
        # Place north player tokens
        north_positions = self.game_state.player_north.get_starting_positions()
        for x, y in north_positions:
            self.board.place_player(self.game_state.player_north, x, y)
            self.game_state.player_north.positions.append((x, y))

        # Place south player tokens (12 total)
        south_positions = self.game_state.player_south.get_starting_positions()
        for x, y in south_positions:
            self.board.place_player(self.game_state.player_south, x, y)
            self.game_state.player_south.positions.append((x, y))

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
                        self.selected_position[0],
                        self.selected_position[1],
                        board_x,
                        board_y,
                    )
                    if success:
                        # Update player's positions list
                        player = self.game_state.current_player
                        old_pos = (self.selected_position[0], self.selected_position[1])
                        if old_pos in player.positions:
                            player.positions.remove(old_pos)
                        player.positions.append((board_x, board_y))

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
        if (
            node
            and node.is_occupied()
            and node.occupied_by == self.game_state.current_player
        ):
            self.selected_position = (x, y)
            self.valid_moves = [
                (mx, my)
                for mx, my in self.board.get_adjacent_positions(x, y)
                if self.board.is_valid_move(x, y, mx, my)
            ]
        else:
            self.selected_position = None
            self.valid_moves = []

    def handle_keyboard(self, key):
        """Handle keyboard input for movement."""
        # Auto-select current player's first piece if nothing is selected
        if not self.selected_position:
            player = self.game_state.current_player
            if player.positions:
                # Select the first available piece
                first_pos = player.positions[0]
                self.selected_position = first_pos
                self.valid_moves = [
                    (mx, my)
                    for mx, my in self.board.get_adjacent_positions(first_pos[0], first_pos[1])
                    if self.board.is_valid_move(first_pos[0], first_pos[1], mx, my)
                ]
            return

        # Define movement directions
        move_map = {
            pygame.K_w: (0, -1),  # Up
            pygame.K_UP: (0, -1),
            pygame.K_s: (0, 1),  # Down
            pygame.K_DOWN: (0, 1),
            pygame.K_a: (-1, 0),  # Left
            pygame.K_LEFT: (-1, 0),
            pygame.K_d: (1, 0),  # Right
            pygame.K_RIGHT: (1, 0),
            pygame.K_q: (-1, -1),  # Up-Left
            pygame.K_e: (1, -1),  # Up-Right
            pygame.K_z: (-1, 1),  # Down-Left
            pygame.K_c: (1, 1),  # Down-Right
        }

        if key in move_map:
            dx, dy = move_map[key]
            current_x, current_y = self.selected_position
            target_x, target_y = current_x + dx, current_y + dy

            # Check if move is valid and in valid_moves list
            if (target_x, target_y) in self.valid_moves:
                success = self.board.move_player(
                    self.game_state.current_player,
                    current_x,
                    current_y,
                    target_x,
                    target_y,
                )
                if success:
                    # Update player's positions list
                    player = self.game_state.current_player
                    if (current_x, current_y) in player.positions:
                        player.positions.remove((current_x, current_y))
                    player.positions.append((target_x, target_y))

                    self.selected_position = None
                    self.valid_moves = []
                    self.game_state.switch_turn()

        # Escape to deselect or exit
        elif key == pygame.K_ESCAPE:
            current_time = pygame.time.get_ticks()

            if self.esc_pressed_time is None:
                # First ESC press
                self.esc_pressed_time = current_time
                self.selected_position = None
                self.valid_moves = []
            elif current_time - self.esc_pressed_time <= self.esc_timeout:
                # Second ESC press within timeout - exit game
                pygame.quit()
                sys.exit()
            else:
                # ESC pressed after timeout - reset timer
                self.esc_pressed_time = current_time
                self.selected_position = None
                self.valid_moves = []

    def run(self):
        """Main game loop."""
        running = True

        while running:
            current_time = pygame.time.get_ticks()

            # Reset ESC timer if timeout exceeded
            if (self.esc_pressed_time is not None and
                current_time - self.esc_pressed_time > self.esc_timeout):
                self.esc_pressed_time = None

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_click(event.pos, event.button)
                elif event.type == pygame.KEYDOWN:
                    self.handle_keyboard(event.key)

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


def main():
    """Entry point for the Komikan board game."""
    game = Game()
    game.run()


if __name__ == "__main__":
    main()
