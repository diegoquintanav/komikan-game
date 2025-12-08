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
        self.occupied_by: Optional["Player"] = None

    def is_occupied(self) -> bool:
        return self.occupied_by is not None

    def __repr__(self):
        return f"Node({self.x}, {self.y})"


class GameBoard:
    """Manages the 5x8 grid of nodes and game logic."""

    WIDTH = 5
    HEIGHT = 8
    DISABLED_NODES = {(0, 2), (4, 2)}  # Nodes that cannot be moved to

    _DISABLED_TRIANGLE_PATHS = {
        # Paths that cannot be traversed (bidirectional)
        # force top north inverted triangle
        ((1, 2), (1, 3)),
        ((2, 2), (1, 3)),
        ((1, 2), (0, 3)),
        ((3, 2), (3, 3)),
        ((2, 2), (3, 3)),
        ((3, 2), (4, 3)),
        # All paths connecting to disabled node (0, 2)
        ((0, 2), (0, 1)),  # North
        ((0, 2), (1, 1)),  # Northeast
        ((0, 2), (1, 2)),  # East
        ((0, 2), (1, 3)),  # Southeast
        ((0, 2), (0, 3)),  # South
        # All paths connecting to disabled node (4, 2)
        ((4, 2), (4, 1)),  # North
        ((4, 2), (3, 1)),  # Northwest
        ((4, 2), (3, 2)),  # West
        ((4, 2), (3, 3)),  # Southwest
        ((4, 2), (4, 3)),  # South
        # All diagonal paths if y <= 2 and every value of x in [0,4]
        ((0, 0), (1, 1)),
        ((1, 1), (2, 2)),
        ((1, 0), (0, 1)),
        ((1, 0), (2, 1)),
        ((2, 0), (1, 1)),
        ((2, 0), (3, 1)),
        ((3, 0), (2, 1)),
        ((3, 0), (4, 1)),
        ((4, 0), (3, 1)),
        ((1, 2), (2, 1)),
        ((2, 2), (1, 1)),
        ((2, 2), (3, 1)),
        ((3, 2), (2, 1)),
    }

    _DISABLED_POS_DIAGONAL_PATHS = {
        # Full diagonal paths where y>=3 and x is odd
        # Diagonal line starting at (1,3): (1,3) -> (2,4) -> (3,5) -> (4,6)
        ((1, 3), (2, 4)),
        ((2, 4), (3, 5)),
        ((3, 5), (4, 6)),
        # Diagonal line starting at (3,3): (3,3) -> (4,4)
        ((3, 3), (4, 4)),
        # Diagonal line starting at 0,4
        ((0, 4), (1, 5)),
        ((1, 5), (2, 6)),
        ((2, 6), (3, 7)),
        # Diagonal line starting at 0,6
        ((0, 6), (1, 7)),
    }

    _DISABLED_NEG_DIAGONAL_PATHS = {
        # Full diagonal paths where y>=3 and x is even
        # Diagonal line starting at (1,3): (1,3) -> (0,4)
        ((1, 3), (0, 4)),
        # Diagonal line starting at (3,3): (3,3) -> (2,4) -> (1,5) -> (0,6)
        ((3, 3), (2, 4)),
        ((2, 4), (1, 5)),
        ((1, 5), (0, 6)),
        # Diagonal line starting at (4,4)
        ((4, 4), (3, 5)),
        ((3, 5), (2, 6)),
        ((2, 6), (1, 7)),
        # Diagonal line starting at (4,6)
        ((4, 6), (3, 7)),
    }

    DISABLED_PATHS = {
        *_DISABLED_TRIANGLE_PATHS,
        *_DISABLED_POS_DIAGONAL_PATHS,
        *_DISABLED_NEG_DIAGONAL_PATHS,
    }

    def __init__(self):
        # Create 5x8 grid of nodes
        self.nodes: List[List[Node]] = []
        for y in range(self.HEIGHT):
            row = []
            for x in range(self.WIDTH):
                row.append(Node(x, y))
            self.nodes.append(row)

    def is_disabled_node(self, x: int, y: int) -> bool:
        """Check if a node is disabled."""
        return (x, y) in self.DISABLED_NODES

    def is_disabled_path(self, from_x: int, from_y: int, to_x: int, to_y: int) -> bool:
        """Check if a path between two nodes is disabled."""
        path1 = ((from_x, from_y), (to_x, to_y))
        path2 = ((to_x, to_y), (from_x, from_y))  # Reverse path
        return path1 in self.DISABLED_PATHS or path2 in self.DISABLED_PATHS

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
            (0, -1),
            (1, -1),
            (1, 0),
            (1, 1),
            (0, 1),
            (-1, 1),
            (-1, 0),
            (-1, -1),
        ]

        for dx, dy in directions:
            new_x, new_y = x + dx, y + dy
            if self.is_valid_position(new_x, new_y):
                adjacent.append((new_x, new_y))

        return adjacent

    def is_valid_capture(self, from_x: int, from_y: int, to_x: int, to_y: int, attacker: "Player") -> bool:
        """Check if a capture move is valid (jump over enemy to land on empty space)."""
        # Calculate direction and distance
        dx = to_x - from_x
        dy = to_y - from_y

        # Must be exactly 2 steps in one of 8 directions
        if not ((abs(dx) == 2 and dy == 0) or  # Horizontal
                (dx == 0 and abs(dy) == 2) or  # Vertical
                (abs(dx) == 2 and abs(dy) == 2)):  # Diagonal
            return False

        # Calculate middle position (jumped-over piece)
        middle_x = from_x + dx // 2
        middle_y = from_y + dy // 2

        # Check bounds
        if not (self.is_valid_position(middle_x, middle_y) and self.is_valid_position(to_x, to_y)):
            return False

        # Check if positions are disabled
        if self.is_disabled_node(middle_x, middle_y) or self.is_disabled_node(to_x, to_y):
            return False

        # Check if paths are disabled
        if (self.is_disabled_path(from_x, from_y, middle_x, middle_y) or
            self.is_disabled_path(middle_x, middle_y, to_x, to_y)):
            return False

        # Get nodes
        middle_node = self.get_node(middle_x, middle_y)
        target_node = self.get_node(to_x, to_y)

        if not middle_node or not target_node:
            return False

        # Middle position must have an enemy piece
        if not middle_node.is_occupied():
            return False

        # Target position must be empty
        if target_node.is_occupied():
            return False

        # Middle piece must be enemy (different player)
        return middle_node.occupied_by != attacker

    def is_valid_move(self, from_x: int, from_y: int, to_x: int, to_y: int) -> bool:
        """Check if a move is valid (adjacent and target not occupied)."""
        # Check if target position is valid
        if not self.is_valid_position(to_x, to_y):
            return False

        # Check if target position is disabled
        if self.is_disabled_node(to_x, to_y):
            return False

        # Check if the path is disabled
        if self.is_disabled_path(from_x, from_y, to_x, to_y):
            return False

        # Check if target position is adjacent to current position
        adjacent_positions = self.get_adjacent_positions(from_x, from_y)
        if (to_x, to_y) not in adjacent_positions:
            return False

        # Check if target position is not occupied
        target_node = self.get_node(to_x, to_y)
        return target_node is not None and not target_node.is_occupied()

    def capture_move(self, player: "Player", from_x: int, from_y: int, to_x: int, to_y: int) -> tuple[bool, "Player"]:
        """Execute a capture move. Returns (success, captured_player)."""
        if not self.is_valid_capture(from_x, from_y, to_x, to_y, player):
            return False, None

        # Calculate middle position
        dx = to_x - from_x
        dy = to_y - from_y
        middle_x = from_x + dx // 2
        middle_y = from_y + dy // 2

        # Get nodes
        old_node = self.get_node(from_x, from_y)
        middle_node = self.get_node(middle_x, middle_y)
        new_node = self.get_node(to_x, to_y)

        if not old_node or not middle_node or not new_node:
            return False, None

        # Capture the middle piece
        captured_player = middle_node.occupied_by

        # Clear old position and middle position
        old_node.occupied_by = None
        middle_node.occupied_by = None

        # Set new position
        new_node.occupied_by = player

        return True, captured_player

    def move_player(
        self, player: "Player", from_x: int, from_y: int, to_x: int, to_y: int
    ) -> bool:
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
            return True

        return False

    def place_player(self, player: "Player", x: int, y: int) -> bool:
        """Place a player at initial position."""
        node = self.get_node(x, y)
        if node and not node.is_occupied():
            node.occupied_by = player
            player.x = x
            player.y = y
            return True
        return False
