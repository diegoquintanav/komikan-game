"""
Player classes for the Komikan board game.
Manages player state and rendering.
"""
import pygame
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
        self.x = 0
        self.y = 0

    def get_starting_positions(self) -> list[Tuple[int, int]]:
        """Get valid starting positions for this player."""
        if self.side == PlayerSide.NORTH:
            # Top row (y=0)
            return [(x, 0) for x in range(5)]
        else:  # PlayerSide.SOUTH
            # Bottom row (y=7)
            return [(x, 7) for x in range(5)]

    def __repr__(self):
        return f"Player({self.side.value}, pos=({self.x}, {self.y}))"


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