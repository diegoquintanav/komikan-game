"""
Tests for capture mechanics edge cases (ALMUD-257).

Covers directional captures, disabled path interactions, capture execution
side effects, and board boundary conditions.
"""

from komikan.board import GameBoard
from komikan.player import Player, PlayerSide


class TestCaptureDirectionalEdgeCases:
    """Test capture validation across all 8 board directions."""

    def test_capture_horizontal_east(self):
        """Capture jumping east: origin->middle->target along same row."""
        board = GameBoard()
        north = Player(PlayerSide.NORTH, (255, 0, 0))
        south = Player(PlayerSide.SOUTH, (0, 0, 255))

        board.place_player(north, 0, 4)
        board.place_player(south, 1, 4)

        assert board.is_valid_capture(0, 4, 2, 4, north)

    def test_capture_horizontal_west(self):
        """Capture jumping west: origin->middle->target right-to-left along same row."""
        board = GameBoard()
        north = Player(PlayerSide.NORTH, (255, 0, 0))
        south = Player(PlayerSide.SOUTH, (0, 0, 255))

        board.place_player(north, 2, 4)
        board.place_player(south, 1, 4)

        assert board.is_valid_capture(2, 4, 0, 4, north)

    def test_capture_vertical_south(self):
        """Capture jumping south: origin above, target below along same column."""
        board = GameBoard()
        north = Player(PlayerSide.NORTH, (255, 0, 0))
        south = Player(PlayerSide.SOUTH, (0, 0, 255))

        board.place_player(north, 2, 3)
        board.place_player(south, 2, 4)

        assert board.is_valid_capture(2, 3, 2, 5, north)

    def test_capture_vertical_north(self):
        """Capture jumping north: origin below, target above along same column."""
        board = GameBoard()
        north = Player(PlayerSide.NORTH, (255, 0, 0))
        south = Player(PlayerSide.SOUTH, (0, 0, 255))

        board.place_player(north, 2, 5)
        board.place_player(south, 2, 4)

        assert board.is_valid_capture(2, 5, 2, 3, north)

    def test_capture_all_4_diagonal_directions(self):
        """NE, SE, SW, NW captures from board center (2,3) are all valid."""
        board = GameBoard()
        north = Player(PlayerSide.NORTH, (255, 0, 0))

        # NE: (2,3) -> (3,2) -> (4,1)
        ne_south = Player(PlayerSide.SOUTH, (0, 0, 255))
        board.place_player(north, 2, 3)
        board.place_player(ne_south, 3, 2)
        assert board.is_valid_capture(2, 3, 4, 1, north)
        board.get_node(2, 3).occupied_by = None
        board.get_node(3, 2).occupied_by = None

        # SE: (2,3) -> (3,4) -> (4,5)
        se_south = Player(PlayerSide.SOUTH, (0, 0, 255))
        board.place_player(north, 2, 3)
        board.place_player(se_south, 3, 4)
        assert board.is_valid_capture(2, 3, 4, 5, north)
        board.get_node(2, 3).occupied_by = None
        board.get_node(3, 4).occupied_by = None

        # SW: (2,3) -> (1,4) -> (0,5)
        sw_south = Player(PlayerSide.SOUTH, (0, 0, 255))
        board.place_player(north, 2, 3)
        board.place_player(sw_south, 1, 4)
        assert board.is_valid_capture(2, 3, 0, 5, north)
        board.get_node(2, 3).occupied_by = None
        board.get_node(1, 4).occupied_by = None

        # NW: (2,3) -> (1,2) -> (0,1)
        nw_south = Player(PlayerSide.SOUTH, (0, 0, 255))
        board.place_player(north, 2, 3)
        board.place_player(nw_south, 1, 2)
        assert board.is_valid_capture(2, 3, 0, 1, north)

    def test_capture_distance_1_invalid(self):
        """Capture to adjacent node (1 step) is not a valid capture."""
        board = GameBoard()
        north = Player(PlayerSide.NORTH, (255, 0, 0))
        south = Player(PlayerSide.SOUTH, (0, 0, 255))

        board.place_player(north, 2, 3)
        board.place_player(south, 2, 4)

        assert not board.is_valid_capture(2, 3, 2, 4, north)

    def test_capture_distance_3_invalid(self):
        """Capture spanning 3 steps is not valid."""
        board = GameBoard()
        north = Player(PlayerSide.NORTH, (255, 0, 0))
        south = Player(PlayerSide.SOUTH, (0, 0, 255))

        board.place_player(north, 2, 1)
        board.place_player(south, 2, 3)

        assert not board.is_valid_capture(2, 1, 2, 4, north)

    def test_capture_l_shape_invalid(self):
        """L-shaped jump (2,1 offset) is not a valid capture direction."""
        board = GameBoard()
        north = Player(PlayerSide.NORTH, (255, 0, 0))
        south = Player(PlayerSide.SOUTH, (0, 0, 255))

        board.place_player(north, 2, 3)
        board.place_player(south, 3, 4)

        assert not board.is_valid_capture(2, 3, 4, 4, north)


class TestCaptureDisabledPathInteraction:
    """Test that disabled paths and nodes correctly block captures."""

    def test_capture_across_disabled_path(self):
        """Capture rejected when middle->target path is disabled."""
        board = GameBoard()
        north = Player(PlayerSide.NORTH, (255, 0, 0))
        south = Player(PlayerSide.SOUTH, (0, 0, 255))

        # Path (3,2)->(3,3) is disabled (triangle path).
        # Origin->middle path (3,1)->(3,2) is valid.
        board.place_player(north, 3, 1)
        board.place_player(south, 3, 2)

        assert not board.is_valid_capture(3, 1, 3, 3, north)

    def test_capture_over_disabled_node_middle(self):
        """Capture rejected when jumped-over position is a disabled node."""
        board = GameBoard()
        north = Player(PlayerSide.NORTH, (255, 0, 0))
        south = Player(PlayerSide.SOUTH, (0, 0, 255))

        # (0,2) is a disabled node — place south there for testing purposes.
        board.place_player(north, 0, 0)
        board.place_player(south, 0, 2)

        assert not board.is_valid_capture(0, 0, 0, 4, north)

    def test_capture_to_disabled_node_target(self):
        """Capture rejected when landing position is a disabled node."""
        board = GameBoard()
        north = Player(PlayerSide.NORTH, (255, 0, 0))
        south = Player(PlayerSide.SOUTH, (0, 0, 255))

        board.place_player(north, 0, 0)
        board.place_player(south, 0, 1)

        assert not board.is_valid_capture(0, 0, 0, 2, north)

    def test_capture_first_segment_disabled(self):
        """Capture rejected when origin->middle path is disabled."""
        board = GameBoard()
        north = Player(PlayerSide.NORTH, (255, 0, 0))
        south = Player(PlayerSide.SOUTH, (0, 0, 255))

        # Path (1,0)->(2,1) is disabled (triangle diagonal).
        # Middle->target path (2,1)->(3,2) is valid.
        board.place_player(north, 1, 0)
        board.place_player(south, 2, 1)

        assert not board.is_valid_capture(1, 0, 3, 2, north)

    def test_capture_second_segment_disabled(self):
        """Capture rejected when middle->target path is disabled."""
        board = GameBoard()
        north = Player(PlayerSide.NORTH, (255, 0, 0))
        south = Player(PlayerSide.SOUTH, (0, 0, 255))

        # Path (1,2)->(1,3) is disabled (triangle vertical).
        # Origin->middle path (1,1)->(1,2) is valid.
        board.place_player(north, 1, 1)
        board.place_player(south, 1, 2)

        assert not board.is_valid_capture(1, 1, 1, 3, north)


class TestCaptureExecution:
    """Test side effects of executing a capture move."""

    def test_capture_removes_middle_piece(self):
        """After capture, the jumped-over node should be empty."""
        board = GameBoard()
        north = Player(PlayerSide.NORTH, (255, 0, 0))
        south = Player(PlayerSide.SOUTH, (0, 0, 255))

        board.place_player(north, 2, 2)
        board.place_player(south, 2, 3)

        board.capture_move(north, 2, 2, 2, 4)

        assert not board.get_node(2, 3).is_occupied()

    def test_capture_clears_origin(self):
        """After capture, the origin node should be empty."""
        board = GameBoard()
        north = Player(PlayerSide.NORTH, (255, 0, 0))
        south = Player(PlayerSide.SOUTH, (0, 0, 255))

        board.place_player(north, 2, 2)
        board.place_player(south, 2, 3)

        board.capture_move(north, 2, 2, 2, 4)

        assert not board.get_node(2, 2).is_occupied()

    def test_capture_sets_target(self):
        """After capture, the target node should hold the capturing player."""
        board = GameBoard()
        north = Player(PlayerSide.NORTH, (255, 0, 0))
        south = Player(PlayerSide.SOUTH, (0, 0, 255))

        board.place_player(north, 2, 2)
        board.place_player(south, 2, 3)

        board.capture_move(north, 2, 2, 2, 4)

        assert board.get_node(2, 4).occupied_by == north

    def test_capture_returns_correct_player(self):
        """capture_move should return the captured player object."""
        board = GameBoard()
        north = Player(PlayerSide.NORTH, (255, 0, 0))
        south = Player(PlayerSide.SOUTH, (0, 0, 255))

        board.place_player(north, 2, 2)
        board.place_player(south, 2, 3)

        success, captured = board.capture_move(north, 2, 2, 2, 4)

        assert success
        assert captured == south
        assert captured.side == PlayerSide.SOUTH

    def test_capture_invalid_returns_none(self):
        """Invalid capture returns (False, None) without modifying board."""
        board = GameBoard()
        north = Player(PlayerSide.NORTH, (255, 0, 0))
        south = Player(PlayerSide.SOUTH, (0, 0, 255))

        board.place_player(north, 2, 2)
        board.place_player(south, 2, 3)

        success, captured = board.capture_move(north, 2, 2, 2, 3)

        assert not success
        assert captured is None
        assert board.get_node(2, 2).occupied_by == north
        assert board.get_node(2, 3).occupied_by == south

    def test_capture_does_not_alter_positions_list(self):
        """capture_move should not modify player.positions."""
        board = GameBoard()
        north = Player(PlayerSide.NORTH, (255, 0, 0))
        south = Player(PlayerSide.SOUTH, (0, 0, 255))

        board.place_player(north, 2, 2)
        board.place_player(south, 2, 3)
        north.positions = [(2, 2)]
        south.positions = [(2, 3)]

        board.capture_move(north, 2, 2, 2, 4)

        assert north.positions == [(2, 2)]
        assert south.positions == [(2, 3)]

    def test_capture_over_own_piece_rejected(self):
        """Cannot capture over a piece belonging to the same side."""
        board = GameBoard()
        north = Player(PlayerSide.NORTH, (255, 0, 0))
        north2 = Player(PlayerSide.NORTH, (255, 0, 0))

        board.place_player(north, 2, 2)
        board.place_player(north2, 2, 3)

        assert not board.is_valid_capture(2, 2, 2, 4, north)


class TestCaptureBoundaryConditions:
    """Test captures near board edges and disabled node regions."""

    def test_capture_at_board_corners(self):
        """Captures from corners — most directions go out of bounds."""
        board = GameBoard()
        north = Player(PlayerSide.NORTH, (255, 0, 0))
        south = Player(PlayerSide.SOUTH, (0, 0, 255))

        # (0,0): east is valid
        board.place_player(north, 0, 0)
        board.place_player(south, 1, 0)
        assert board.is_valid_capture(0, 0, 2, 0, north)
        board.get_node(0, 0).occupied_by = None
        board.get_node(1, 0).occupied_by = None

        # (0,0): north and west go out of bounds
        board.place_player(north, 0, 0)
        assert not board.is_valid_capture(0, 0, 0, -2, north)
        assert not board.is_valid_capture(0, 0, -2, 0, north)
        board.get_node(0, 0).occupied_by = None

        # (4,0): west is valid
        board.place_player(north, 4, 0)
        board.place_player(south, 3, 0)
        assert board.is_valid_capture(4, 0, 2, 0, north)
        board.get_node(4, 0).occupied_by = None
        board.get_node(3, 0).occupied_by = None

        # (4,0): north and east go out of bounds
        board.place_player(north, 4, 0)
        assert not board.is_valid_capture(4, 0, 4, -2, north)
        assert not board.is_valid_capture(4, 0, 6, 0, north)
        board.get_node(4, 0).occupied_by = None

        # (0,7): north is valid
        board.place_player(north, 0, 7)
        board.place_player(south, 0, 6)
        assert board.is_valid_capture(0, 7, 0, 5, north)
        board.get_node(0, 7).occupied_by = None
        board.get_node(0, 6).occupied_by = None

        # (0,7): south and west go out of bounds
        board.place_player(north, 0, 7)
        assert not board.is_valid_capture(0, 7, 0, 9, north)
        assert not board.is_valid_capture(0, 7, -2, 7, north)
        board.get_node(0, 7).occupied_by = None

        # (4,7): north is valid
        board.place_player(north, 4, 7)
        board.place_player(south, 4, 6)
        assert board.is_valid_capture(4, 7, 4, 5, north)
        board.get_node(4, 7).occupied_by = None
        board.get_node(4, 6).occupied_by = None

        # (4,7): south and east go out of bounds
        board.place_player(north, 4, 7)
        assert not board.is_valid_capture(4, 7, 4, 9, north)
        assert not board.is_valid_capture(4, 7, 6, 7, north)

    def test_capture_near_disabled_nodes(self):
        """Captions whose jump passes through disabled nodes (0,2) or (4,2) are rejected."""
        board = GameBoard()
        north = Player(PlayerSide.NORTH, (255, 0, 0))
        south = Player(PlayerSide.SOUTH, (0, 0, 255))

        # Jump over (0,2) from (0,0) to (0,4): middle is disabled node
        board.place_player(north, 0, 0)
        board.place_player(south, 0, 2)
        assert not board.is_valid_capture(0, 0, 0, 4, north)
        board.get_node(0, 0).occupied_by = None
        board.get_node(0, 2).occupied_by = None

        # Jump to (0,2) from (0,0) over (0,1): target is disabled node
        board.place_player(north, 0, 0)
        board.place_player(south, 0, 1)
        assert not board.is_valid_capture(0, 0, 0, 2, north)
        board.get_node(0, 0).occupied_by = None
        board.get_node(0, 1).occupied_by = None

        # Jump over (4,2) from (4,0) to (4,4): middle is disabled node
        board.place_player(north, 4, 0)
        board.place_player(south, 4, 2)
        assert not board.is_valid_capture(4, 0, 4, 4, north)
        board.get_node(4, 0).occupied_by = None
        board.get_node(4, 2).occupied_by = None

        # Jump to (4,2) from (4,0) over (4,1): target is disabled node
        board.place_player(north, 4, 0)
        board.place_player(south, 4, 1)
        assert not board.is_valid_capture(4, 0, 4, 2, north)

    def test_capture_row_3_disabled_diagonals(self):
        """Row 3 diagonal paths block many captures from row 2 to row 4."""
        board = GameBoard()
        north = Player(PlayerSide.NORTH, (255, 0, 0))

        # Valid: (1,2)->(2,3)->(3,4) — no disabled paths crossed
        se_south = Player(PlayerSide.SOUTH, (0, 0, 255))
        board.place_player(north, 1, 2)
        board.place_player(se_south, 2, 3)
        assert board.is_valid_capture(1, 2, 3, 4, north)
        board.get_node(1, 2).occupied_by = None
        board.get_node(2, 3).occupied_by = None

        # Invalid: (2,2)->(3,3)->(4,4) — path (2,2)->(3,3) is disabled
        se_south2 = Player(PlayerSide.SOUTH, (0, 0, 255))
        board.place_player(north, 2, 2)
        board.place_player(se_south2, 3, 3)
        assert not board.is_valid_capture(2, 2, 4, 4, north)
        board.get_node(2, 2).occupied_by = None
        board.get_node(3, 3).occupied_by = None

        # Invalid: (1,2)->(1,3)->(1,4) — path (1,2)->(1,3) is disabled
        s_south = Player(PlayerSide.SOUTH, (0, 0, 255))
        board.place_player(north, 1, 2)
        board.place_player(s_south, 1, 3)
        assert not board.is_valid_capture(1, 2, 1, 4, north)
        board.get_node(1, 2).occupied_by = None
        board.get_node(1, 3).occupied_by = None

        # Valid: (2,2)->(2,3)->(2,4) — vertical, no disabled paths
        s_south2 = Player(PlayerSide.SOUTH, (0, 0, 255))
        board.place_player(north, 2, 2)
        board.place_player(s_south2, 2, 3)
        assert board.is_valid_capture(2, 2, 2, 4, north)
        board.get_node(2, 2).occupied_by = None
        board.get_node(2, 3).occupied_by = None

        # Invalid: (3,2)->(3,3)->(3,4) — path (3,2)->(3,3) is disabled
        s_south3 = Player(PlayerSide.SOUTH, (0, 0, 255))
        board.place_player(north, 3, 2)
        board.place_player(s_south3, 3, 3)
        assert not board.is_valid_capture(3, 2, 3, 4, north)
