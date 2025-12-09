"""
Player classes for the Komikan board game.
Manages player state and rendering.
"""

from enum import Enum
from typing import Tuple


class PlayerSide(Enum):
    NORTH = "pangui"
    SOUTH = "pu trewa"


class Player:
    """Represents a player in the game."""

    def __init__(self, side: PlayerSide, color: Tuple[int, int, int]):
        self.side = side
        self.color = color
        self.positions = []  # List of (x, y) tuples for multiple tokens

    def get_starting_positions(self) -> list[Tuple[int, int]]:
        """Get valid starting positions for this player."""
        if self.side == PlayerSide.NORTH:
            # Top row (y=1), centered - single token
            return [(2, 1)]
        else:  # PlayerSide.SOUTH
            # 12 tokens: two south rows + first and last columns
            positions = []

            # First and last column (x=0, x=4) and fifth row
            for x in [0, 4]:
                positions.append((x, 5))

            # Bottom two rows (y=6,7)
            for y in [6, 7]:
                for x in range(5):
                    positions.append((x, y))
            return positions[:12]  # Take exactly 12 positions

    def get_token_number(self, x: int, y: int) -> int:
        """Get the token number for a piece at given position."""
        try:
            return self.positions.index((x, y)) + 1
        except ValueError:
            return 0  # Not found

    def __repr__(self):
        return f"Player({self.side.value}, positions={self.positions})"


class GameState:
    """Manages the overall game state and turn logic."""

    def __init__(self):
        # Create players
        self.player_north = Player(PlayerSide.NORTH, (255, 100, 100))  # Red
        self.player_south = Player(PlayerSide.SOUTH, (100, 100, 255))  # Blue

        # Game state
        self.current_player = self.player_north
        self.selected_player = None
        self.game_over = False
        self.winner_message = ""

    def switch_turn(self):
        """Switch to the other player's turn."""
        if self.current_player == self.player_north:
            self.current_player = self.player_south
        else:
            self.current_player = self.player_north

    def get_other_player(self):
        """Get the player who is not currently active."""
        if self.current_player == self.player_north:
            return self.player_south
        else:
            return self.player_north

    def restart_game(self):
        """Reset the game to initial state."""
        # Reset player positions
        self.player_north.positions = []
        self.player_south.positions = []

        # Reset game state
        self.current_player = self.player_north
        self.selected_player = None
        self.game_over = False
        self.winner_message = ""

    def check_win_condition(self, board=None) -> Tuple[bool, str]:
        """
        Check if the game has ended and return (is_game_over, winner_message).

        Win conditions:
        - North wins if South has 3 or fewer tokens remaining
        - South wins if North has no valid movements
        """
        # Check if South has 3 or fewer tokens (North wins)
        if len(self.player_south.positions) <= 3:
            return (
                True,
                f"{self.player_north.side.value.upper()} wins! South has only {len(self.player_south.positions)} tokens left.",
            )

        # Check if North has no valid movements (South wins)
        # Only check this if we have a board reference
        if board is not None and not self._has_valid_moves(self.player_north, board):
            return (
                True,
                f"{self.player_south.side.value.upper()} wins! North player has no valid moves.",
            )

        # If game is already over, return a generic message
        if self.game_over:
            return True, "Game Over!"

        return False, ""

    def _has_valid_moves(self, player, board) -> bool:
        """Check if a player has any valid moves (regular moves or captures)."""
        for pos_x, pos_y in player.positions:
            # Check for regular moves
            adjacent_positions = board.get_adjacent_positions(pos_x, pos_y)
            for adj_x, adj_y in adjacent_positions:
                if board.is_valid_move(pos_x, pos_y, adj_x, adj_y):
                    return True

            # Check for capture moves (only for North player)
            if player.side == PlayerSide.NORTH:
                # Check all positions within 2-step capture distance
                for target_x in range(board.WIDTH):
                    for target_y in range(board.HEIGHT):
                        if board.is_valid_capture(
                            pos_x, pos_y, target_x, target_y, player
                        ):
                            return True

        return False
