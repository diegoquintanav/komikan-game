"""
Tests for the GameBoard class.
"""

import pytest
from board import GameBoard, Node
from player import Player, PlayerSide


class TestNode:
    """Test the Node class."""

    def test_node_creation(self):
        """Test node initialization."""
        node = Node(2, 3)
        assert node.x == 2
        assert node.y == 3
        assert node.occupied_by is None
        assert not node.is_occupied()

    def test_node_occupation(self, north_player):
        """Test node occupation mechanics."""
        node = Node(1, 1)
        assert not node.is_occupied()

        node.occupied_by = north_player
        assert node.is_occupied()
        assert node.occupied_by == north_player

    def test_node_repr(self):
        """Test node string representation."""
        node = Node(3, 4)
        assert str(node) == "Node(3, 4)"


class TestGameBoard:
    """Test the GameBoard class."""

    def test_board_initialization(self, empty_board):
        """Test board creation."""
        assert empty_board.WIDTH == 5
        assert empty_board.HEIGHT == 8
        assert len(empty_board.nodes) == 8  # 8 rows
        assert len(empty_board.nodes[0]) == 5  # 5 columns

    def test_disabled_nodes(self, empty_board):
        """Test disabled node checking."""
        assert empty_board.is_disabled_node(0, 2)
        assert empty_board.is_disabled_node(4, 2)
        assert not empty_board.is_disabled_node(2, 2)
        assert not empty_board.is_disabled_node(1, 1)

    def test_get_node_valid(self, empty_board):
        """Test getting valid nodes."""
        node = empty_board.get_node(2, 3)
        assert node is not None
        assert node.x == 2
        assert node.y == 3

    def test_get_node_invalid(self, empty_board):
        """Test getting nodes outside bounds."""
        assert empty_board.get_node(-1, 0) is None
        assert empty_board.get_node(5, 0) is None
        assert empty_board.get_node(0, -1) is None
        assert empty_board.get_node(0, 8) is None

    def test_is_valid_position(self, empty_board):
        """Test position validation."""
        assert empty_board.is_valid_position(0, 0)
        assert empty_board.is_valid_position(4, 7)
        assert empty_board.is_valid_position(2, 4)
        assert not empty_board.is_valid_position(-1, 0)
        assert not empty_board.is_valid_position(5, 0)
        assert not empty_board.is_valid_position(0, 8)

    def test_get_adjacent_positions(self, empty_board):
        """Test getting adjacent positions."""
        # Test center position
        adjacent = empty_board.get_adjacent_positions(2, 2)
        expected = [(1, 1), (2, 1), (3, 1), (1, 2), (3, 2), (1, 3), (2, 3), (3, 3)]
        assert len(adjacent) == 8
        for pos in expected:
            assert pos in adjacent

        # Test corner position
        adjacent = empty_board.get_adjacent_positions(0, 0)
        expected = [(1, 0), (0, 1), (1, 1)]
        assert len(adjacent) == 3
        for pos in expected:
            assert pos in adjacent

    def test_disabled_paths(self, empty_board):
        """Test disabled path checking."""
        # Test some known disabled paths
        assert empty_board.is_disabled_path(0, 2, 0, 1)  # From disabled node
        assert empty_board.is_disabled_path(4, 2, 4, 1)  # From disabled node
        assert empty_board.is_disabled_path(1, 2, 1, 3)  # Triangle path

        # Test bidirectional paths
        assert empty_board.is_disabled_path(0, 1, 0, 2) == empty_board.is_disabled_path(0, 2, 0, 1)

    def test_place_player(self, empty_board, north_player):
        """Test placing a player on the board."""
        success = empty_board.place_player(north_player, 2, 3)
        assert success

        node = empty_board.get_node(2, 3)
        assert node.occupied_by == north_player
        assert node.is_occupied()

    def test_place_player_occupied_position(self, empty_board, north_player, south_player):
        """Test placing player on occupied position."""
        empty_board.place_player(north_player, 2, 3)
        success = empty_board.place_player(south_player, 2, 3)
        assert not success

    def test_place_player_invalid_position(self, empty_board, north_player):
        """Test placing player on invalid position."""
        success = empty_board.place_player(north_player, -1, 0)
        assert not success

        success = empty_board.place_player(north_player, 5, 0)
        assert not success


class TestBoardMovement:
    """Test board movement validation."""

    def test_is_valid_move_adjacent_empty(self, empty_board, north_player):
        """Test valid adjacent move to empty position."""
        empty_board.place_player(north_player, 3, 4)
        assert empty_board.is_valid_move(3, 4, 3, 5)  # Move south
        assert empty_board.is_valid_move(3, 4, 2, 4)  # Move west
        assert empty_board.is_valid_move(3, 4, 2, 5)  # Move diagonal (should be valid)

    def test_is_valid_move_non_adjacent(self, empty_board, north_player):
        """Test invalid non-adjacent move."""
        empty_board.place_player(north_player, 2, 2)
        assert not empty_board.is_valid_move(2, 2, 2, 4)  # Two steps south
        assert not empty_board.is_valid_move(2, 2, 4, 4)  # Far diagonal

    def test_is_valid_move_occupied_target(self, empty_board, north_player, south_player):
        """Test move to occupied position."""
        empty_board.place_player(north_player, 2, 2)
        empty_board.place_player(south_player, 2, 3)
        assert not empty_board.is_valid_move(2, 2, 2, 3)

    def test_is_valid_move_disabled_node(self, empty_board, north_player):
        """Test move to disabled node."""
        empty_board.place_player(north_player, 1, 2)
        assert not empty_board.is_valid_move(1, 2, 0, 2)  # Move to disabled node

    def test_is_valid_move_disabled_path(self, empty_board, north_player):
        """Test move on disabled path."""
        empty_board.place_player(north_player, 1, 2)
        assert not empty_board.is_valid_move(1, 2, 1, 3)  # Disabled triangle path

    def test_move_player_success(self, empty_board, north_player):
        """Test successful player movement."""
        empty_board.place_player(north_player, 2, 2)
        success = empty_board.move_player(north_player, 2, 2, 2, 3)
        assert success

        # Check old position is empty
        old_node = empty_board.get_node(2, 2)
        assert not old_node.is_occupied()

        # Check new position is occupied
        new_node = empty_board.get_node(2, 3)
        assert new_node.occupied_by == north_player

    def test_move_player_invalid(self, empty_board, north_player):
        """Test invalid player movement."""
        empty_board.place_player(north_player, 2, 2)
        success = empty_board.move_player(north_player, 2, 2, 2, 4)  # Non-adjacent
        assert not success

        # Player should still be at original position
        node = empty_board.get_node(2, 2)
        assert node.occupied_by == north_player


class TestBoardCapture:
    """Test board capture mechanics."""

    def test_is_valid_capture_basic(self, capture_scenario_board):
        """Test basic valid capture."""
        board, north_player, south_player = capture_scenario_board
        # North at (2,2), South at (2,3), empty at (2,4)
        assert board.is_valid_capture(2, 2, 2, 4, north_player)

    def test_is_valid_capture_no_enemy(self, empty_board, north_player):
        """Test capture with no enemy in middle."""
        empty_board.place_player(north_player, 2, 2)
        # No piece at (2, 3) to capture
        assert not empty_board.is_valid_capture(2, 2, 2, 4, north_player)

    def test_is_valid_capture_wrong_distance(self, capture_scenario_board):
        """Test capture with wrong distance."""
        board, north_player, south_player = capture_scenario_board
        # Wrong distance - should be exactly 2 steps
        assert not board.is_valid_capture(2, 2, 2, 3, north_player)  # 1 step
        assert not board.is_valid_capture(2, 2, 2, 5, north_player)  # 3 steps

    def test_is_valid_capture_occupied_target(self, capture_scenario_board, south_player):
        """Test capture to occupied position."""
        board, north_player, _ = capture_scenario_board

        # Place another south player at target position
        board.place_player(south_player, 2, 4)
        assert not board.is_valid_capture(2, 2, 2, 4, north_player)

    def test_is_valid_capture_own_piece(self, empty_board, north_player):
        """Test capture over own piece."""
        empty_board.place_player(north_player, 2, 2)

        # Place another north piece (same side) in middle
        north_player2 = Player(PlayerSide.NORTH, (255, 100, 100))
        empty_board.place_player(north_player2, 2, 3)

        # Should not be able to capture own piece
        assert not empty_board.is_valid_capture(2, 2, 2, 4, north_player)

    def test_is_valid_capture_diagonal(self, empty_board, north_player, south_player):
        """Test diagonal capture."""
        empty_board.place_player(north_player, 1, 4)
        empty_board.place_player(south_player, 2, 5)
        # Position (3, 6) should be empty for capture
        assert empty_board.is_valid_capture(1, 4, 3, 6, north_player)

    def test_capture_move_success(self, capture_scenario_board):
        """Test successful capture execution."""
        board, north_player, south_player = capture_scenario_board

        success, captured_player = board.capture_move(north_player, 2, 2, 2, 4)
        assert success
        assert captured_player == south_player

        # Check positions after capture
        assert not board.get_node(2, 2).is_occupied()  # Old position empty
        assert not board.get_node(2, 3).is_occupied()  # Captured piece removed
        assert board.get_node(2, 4).occupied_by == north_player  # New position occupied

    def test_capture_move_invalid(self, capture_scenario_board):
        """Test invalid capture execution."""
        board, north_player, south_player = capture_scenario_board

        success, captured_player = board.capture_move(north_player, 2, 2, 2, 3)  # Wrong distance
        assert not success
        assert captured_player is None

        # Board should be unchanged
        assert board.get_node(2, 2).occupied_by == north_player
        assert board.get_node(2, 3).occupied_by == south_player