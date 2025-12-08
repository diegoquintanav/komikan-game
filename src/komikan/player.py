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
            # Top row (y=0) - single token
            return [(2, 0)]
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
