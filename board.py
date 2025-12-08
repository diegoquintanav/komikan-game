"""
Game board for the Komikan board game.
Manages the 5x8 node grid and validates player movements.
"""
import pygame
from typing import List, Tuple, Optional


class Node:
    """Represents a single node on the game board."""

    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y
        self.occupied_by: Optional['Player'] = None

    def is_occupied(self) -> bool:
        return self.occupied_by is not None

    def __repr__(self):
        return f"Node({self.x}, {self.y})"


class GameBoard:
    """Manages the 5x8 grid of nodes and game logic."""

    WIDTH = 5
    HEIGHT = 8

    def __init__(self):
        # Create 5x8 grid of nodes
        self.nodes: List[List[Node]] = []
        for y in range(self.HEIGHT):
            row = []
            for x in range(self.WIDTH):
                row.append(Node(x, y))
            self.nodes.append(row)

    def get_node(self, x: int, y: int) -> Optional[Node]:
        """Get node at given coordinates, return None if out of bounds."""
        if 0 <= x < self.WIDTH and 0 <= y < self.HEIGHT:
            return self.nodes[y][x]
        return None

    def is_valid_position(self, x: int, y: int) -> bool:
        """Check if coordinates are within board bounds."""
        return 0 <= x < self.WIDTH and 0 <= y < self.HEIGHT

    def get_adjacent_positions(self, x: int, y: int) -> List[Tuple[int, int]]:
        """Get all valid adjacent positions (orthogonal and diagonal)."""
        adjacent = []
        # All 8 directions: N, NE, E, SE, S, SW, W, NW
        directions = [
            (0, -1), (1, -1), (1, 0), (1, 1),
            (0, 1), (-1, 1), (-1, 0), (-1, -1)
        ]

        for dx, dy in directions:
            new_x, new_y = x + dx, y + dy
            if self.is_valid_position(new_x, new_y):
                adjacent.append((new_x, new_y))

        return adjacent

    def is_valid_move(self, from_x: int, from_y: int, to_x: int, to_y: int) -> bool:
        """Check if a move is valid (adjacent and target not occupied)."""
        # Check if target position is valid
        if not self.is_valid_position(to_x, to_y):
            return False

        # Check if target position is adjacent to current position
        adjacent_positions = self.get_adjacent_positions(from_x, from_y)
        if (to_x, to_y) not in adjacent_positions:
            return False

        # Check if target position is not occupied
        target_node = self.get_node(to_x, to_y)
        return target_node is not None and not target_node.is_occupied()

    def move_player(self, player: 'Player', from_x: int, from_y: int, to_x: int, to_y: int) -> bool:
        """Move a player from one position to another. Returns True if successful."""
        if not self.is_valid_move(from_x, from_y, to_x, to_y):
            return False

        # Clear old position
        old_node = self.get_node(from_x, from_y)
        if old_node:
            old_node.occupied_by = None

        # Set new position
        new_node = self.get_node(to_x, to_y)
        if new_node:
            new_node.occupied_by = player
            player.x = to_x
            player.y = to_y
            return True

        return False

    def place_player(self, player: 'Player', x: int, y: int) -> bool:
        """Place a player at initial position."""
        node = self.get_node(x, y)
        if node and not node.is_occupied():
            node.occupied_by = player
            player.x = x
            player.y = y
            return True
        return False