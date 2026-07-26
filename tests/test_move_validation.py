"""
Tests for move validation edge cases (ALMUD-256).

Covers every failure path in is_valid_move, Pangui starting mobility,
disabled path comprehensiveness, capture+disabled path interactions,
and board-position sync risks.
"""

from komikan.player import Player, PlayerSide


class TestMoveValidationEdgeCases:
    """Tests for is_valid_move covering every failure path."""

    def test_move_to_out_of_bounds(self, empty_board, north_player):
        """Targets outside the 5x8 grid must be rejected."""
        empty_board.place_player(north_player, 2, 4)

        assert not empty_board.is_valid_move(2, 4, -1, 0)
        assert not empty_board.is_valid_move(2, 4, 5, 0)
        assert not empty_board.is_valid_move(2, 4, 0, -1)
        assert not empty_board.is_valid_move(2, 4, 0, 8)

    def test_move_to_disabled_node(self, empty_board, north_player):
        """Disabled nodes (0,2) and (4,2) must never be valid targets."""
        empty_board.place_player(north_player, 1, 1)
        # Both fail at the disabled node check (step 2 in is_valid_move),
        # which runs before adjacency validation.
        assert not empty_board.is_valid_move(1, 1, 0, 2)
        assert not empty_board.is_valid_move(1, 1, 4, 2)

    def test_move_on_disabled_path(self, empty_board, north_player):
        """A move along a disabled path is rejected even when both endpoints are valid nodes."""
        empty_board.place_player(north_player, 1, 2)
        # Path (1,2)->(1,3) is a disabled triangle path
        assert not empty_board.is_valid_move(1, 2, 1, 3)

    def test_move_non_adjacent(self, empty_board, north_player):
        """A move to a non-adjacent node must be rejected."""
        empty_board.place_player(north_player, 2, 4)
        # (2,6) is two steps south — not adjacent
        assert not empty_board.is_valid_move(2, 4, 2, 6)

    def test_move_to_occupied_own_piece(self, empty_board, north_player):
        """A move to a node occupied by a friendly piece must be rejected."""
        empty_board.place_player(north_player, 2, 4)
        north_player2 = Player(PlayerSide.NORTH, (255, 100, 100))
        empty_board.place_player(north_player2, 2, 5)
        assert not empty_board.is_valid_move(2, 4, 2, 5)

    def test_move_to_occupied_enemy(self, empty_board, north_player, south_player):
        """A move to a node occupied by an enemy piece must be rejected."""
        empty_board.place_player(north_player, 2, 4)
        empty_board.place_player(south_player, 2, 5)
        assert not empty_board.is_valid_move(2, 4, 2, 5)

    def test_move_to_same_position(self, empty_board, north_player):
        """Moving to the same position is rejected — not adjacent to self."""
        empty_board.place_player(north_player, 2, 4)
        assert not empty_board.is_valid_move(2, 4, 2, 4)

    def test_move_from_empty_node(self, empty_board):
        """is_valid_move does NOT validate origin occupancy — only checks target validity."""
        # No piece at (2,4), but is_valid_move does not inspect the origin node
        assert empty_board.is_valid_move(2, 4, 2, 5)

    def test_move_to_adjacent_valid(self, empty_board, north_player):
        """Baseline: a move to an adjacent empty valid node succeeds."""
        empty_board.place_player(north_player, 2, 4)
        assert empty_board.is_valid_move(2, 4, 2, 5)

    def test_disabled_node_adjacent_to_valid_node(self, empty_board, north_player):
        """A disabled node is rejected even when it is directly adjacent to the origin."""
        empty_board.place_player(north_player, 0, 3)
        # (0,2) is adjacent to (0,3) but is a disabled node
        assert not empty_board.is_valid_move(0, 3, 0, 2)

    def test_disabled_path_from_disabled_node(self, empty_board):
        """Calling is_valid_move with a disabled origin — every exit is blocked by disabled paths."""
        # All 5 paths from (0,2) are disabled, so every adjacent target returns False
        assert not empty_board.is_valid_move(0, 2, 0, 1)
        assert not empty_board.is_valid_move(0, 2, 1, 1)
        assert not empty_board.is_valid_move(0, 2, 1, 2)
        assert not empty_board.is_valid_move(0, 2, 0, 3)
        assert not empty_board.is_valid_move(0, 2, 1, 3)

    def test_move_across_disabled_path_diagonal(self, empty_board, north_player):
        """Diagonal move (0,0)->(1,1) crosses a disabled path."""
        empty_board.place_player(north_player, 0, 0)
        assert not empty_board.is_valid_move(0, 0, 1, 1)


class TestPanguiStartingMobility:
    """Tests for Pangui's starting position (2,0) — very limited mobility."""

    def test_pangui_start_valid_moves(self, empty_board, north_player):
        """From (2,0), only (1,0), (2,1), (3,0) should be valid (3 total)."""
        empty_board.place_player(north_player, 2, 0)

        # The 3 valid moves
        assert empty_board.is_valid_move(2, 0, 1, 0)
        assert empty_board.is_valid_move(2, 0, 2, 1)
        assert empty_board.is_valid_move(2, 0, 3, 0)

        # The 2 disabled diagonal paths from (2,0)
        assert not empty_board.is_valid_move(2, 0, 1, 1)
        assert not empty_board.is_valid_move(2, 0, 3, 1)

    def test_pangui_start_disabled_adjacent(self, empty_board, north_player):
        """From (2,0), (1,1) and (3,1) are adjacent but the paths are disabled."""
        empty_board.place_player(north_player, 2, 0)

        adjacent = empty_board.get_adjacent_positions(2, 0)
        assert (1, 1) in adjacent
        assert (3, 1) in adjacent

        # The paths themselves are disabled
        assert empty_board.is_disabled_path(2, 0, 1, 1)
        assert empty_board.is_disabled_path(2, 0, 3, 1)

    def test_pangui_no_captures_at_start(self, empty_board, north_player):
        """From (2,0) with no enemies on the board, all captures are invalid."""
        empty_board.place_player(north_player, 2, 0)

        # Vertical capture — no enemy at middle (2,1)
        assert not empty_board.is_valid_capture(2, 0, 2, 2, north_player)
        # Horizontal captures — no enemies at (1,0) or (3,0)
        assert not empty_board.is_valid_capture(2, 0, 0, 0, north_player)
        assert not empty_board.is_valid_capture(2, 0, 4, 0, north_player)
        # Diagonal captures — no enemies (plus some disabled paths/nodes)
        assert not empty_board.is_valid_capture(2, 0, 0, 2, north_player)
        assert not empty_board.is_valid_capture(2, 0, 4, 2, north_player)


class TestDisabledPathComprehensive:
    """Tests for all categories of disabled paths on the board."""

    def test_disabled_triangle_paths(self, empty_board):
        """The 6 triangle paths (upper board inverted triangle) are disabled."""
        triangle_paths = [
            ((1, 2), (1, 3)),
            ((2, 2), (1, 3)),
            ((1, 2), (0, 3)),
            ((3, 2), (3, 3)),
            ((2, 2), (3, 3)),
            ((3, 2), (4, 3)),
        ]
        for (fx, fy), (tx, ty) in triangle_paths:
            assert empty_board.is_disabled_path(fx, fy, tx, ty), (
                f"Path ({fx},{fy})->({tx},{ty}) should be disabled"
            )

    def test_disabled_paths_to_disabled_nodes(self, empty_board):
        """All 10 paths connecting to disabled nodes (0,2) and (4,2) are disabled."""
        paths_to_disabled = [
            # 5 paths from disabled node (0,2)
            ((0, 2), (0, 1)),
            ((0, 2), (1, 1)),
            ((0, 2), (1, 2)),
            ((0, 2), (1, 3)),
            ((0, 2), (0, 3)),
            # 5 paths from disabled node (4,2)
            ((4, 2), (4, 1)),
            ((4, 2), (3, 1)),
            ((4, 2), (3, 2)),
            ((4, 2), (3, 3)),
            ((4, 2), (4, 3)),
        ]
        for (fx, fy), (tx, ty) in paths_to_disabled:
            assert empty_board.is_disabled_path(fx, fy, tx, ty), (
                f"Path ({fx},{fy})->({tx},{ty}) should be disabled"
            )

    def test_disabled_positive_diagonal_paths(self, empty_board):
        """The 8 positive-slope diagonal paths (y>=3, x odd) are disabled."""
        pos_diagonal_paths = [
            ((1, 3), (2, 4)),
            ((2, 4), (3, 5)),
            ((3, 5), (4, 6)),
            ((3, 3), (4, 4)),
            ((0, 4), (1, 5)),
            ((1, 5), (2, 6)),
            ((2, 6), (3, 7)),
            ((0, 6), (1, 7)),
        ]
        for (fx, fy), (tx, ty) in pos_diagonal_paths:
            assert empty_board.is_disabled_path(fx, fy, tx, ty), (
                f"Positive diagonal ({fx},{fy})->({tx},{ty}) should be disabled"
            )

    def test_disabled_negative_diagonal_paths(self, empty_board):
        """The 8 negative-slope diagonal paths (y>=3, x even) are disabled."""
        neg_diagonal_paths = [
            ((1, 3), (0, 4)),
            ((3, 3), (2, 4)),
            ((2, 4), (1, 5)),
            ((1, 5), (0, 6)),
            ((4, 4), (3, 5)),
            ((3, 5), (2, 6)),
            ((2, 6), (1, 7)),
            ((4, 6), (3, 7)),
        ]
        for (fx, fy), (tx, ty) in neg_diagonal_paths:
            assert empty_board.is_disabled_path(fx, fy, tx, ty), (
                f"Negative diagonal ({fx},{fy})->({tx},{ty}) should be disabled"
            )

    def test_bidirectional_disabled_paths(self, empty_board):
        """Disabled paths are rejected in both forward and reverse directions."""
        test_cases = [
            ((1, 2), (1, 3)),  # triangle path
            ((0, 0), (1, 1)),  # y<=2 diagonal restriction
            ((1, 3), (2, 4)),  # positive diagonal
            ((3, 3), (2, 4)),  # negative diagonal
        ]
        for (fx, fy), (tx, ty) in test_cases:
            assert empty_board.is_disabled_path(fx, fy, tx, ty), (
                f"Forward ({fx},{fy})->({tx},{ty}) should be disabled"
            )
            assert empty_board.is_disabled_path(tx, ty, fx, fy), (
                f"Reverse ({tx},{ty})->({fx},{fy}) should be disabled"
            )


class TestMoveAndCaptureDisabledPathInteraction:
    """Tests for how disabled paths interact with capture mechanics."""

    def test_move_valid_but_capture_disabled(
        self, empty_board, north_player, south_player
    ):
        """A 1-step move is valid, but a 2-step capture in the same direction is disabled."""
        empty_board.place_player(north_player, 1, 1)
        # Move to (1,2) is valid — path not disabled, target empty
        assert empty_board.is_valid_move(1, 1, 1, 2)

        # Place enemy at (1,2) for capture scenario
        empty_board.place_player(south_player, 1, 2)
        # Capture (1,1)->(1,3) over (1,2) fails: path (1,2)->(1,3) is disabled
        assert not empty_board.is_valid_capture(1, 1, 1, 3, north_player)

    def test_capture_disabled_path_middle_segment(
        self, empty_board, north_player, south_player
    ):
        """Capture fails when the origin-to-middle path segment is disabled."""
        empty_board.place_player(north_player, 3, 2)
        empty_board.place_player(south_player, 3, 3)
        # Path (3,2)->(3,3) is a disabled triangle path — first segment blocked
        assert not empty_board.is_valid_capture(3, 2, 3, 4, north_player)

    def test_capture_disabled_path_landing_segment(
        self, empty_board, north_player, south_player
    ):
        """Capture fails when the middle-to-target path segment is disabled."""
        empty_board.place_player(north_player, 1, 1)
        empty_board.place_player(south_player, 1, 2)
        # Path (1,2)->(1,3) is a disabled triangle path — landing segment blocked
        assert not empty_board.is_valid_capture(1, 1, 1, 3, north_player)

    def test_capture_both_segments_disabled(
        self, empty_board, north_player, south_player
    ):
        """Capture fails when both path segments are disabled."""
        empty_board.place_player(north_player, 0, 0)
        empty_board.place_player(south_player, 1, 1)
        # Path (0,0)->(1,1) disabled (y<=2 diagonal restriction)
        # Path (1,1)->(2,2) disabled (y<=2 diagonal restriction)
        assert not empty_board.is_valid_capture(0, 0, 2, 2, north_player)


class TestBoardPositionSync:
    """Tests for board-node vs player.positions consistency risks."""

    def test_move_does_not_update_positions_list(self, empty_board, north_player):
        """board.move_player() does NOT update player.positions — known design risk."""
        empty_board.place_player(north_player, 2, 4)
        north_player.positions = [(2, 4)]

        empty_board.move_player(north_player, 2, 4, 2, 5)

        # Board node reflects the move
        assert empty_board.get_node(2, 5).occupied_by == north_player
        assert not empty_board.get_node(2, 4).is_occupied()
        # But player.positions is stale
        assert (2, 5) not in north_player.positions
        assert (2, 4) in north_player.positions

    def test_capture_does_not_update_positions_list(
        self, empty_board, north_player, south_player
    ):
        """board.capture_move() does NOT update player.positions — known design risk."""
        empty_board.place_player(north_player, 2, 2)
        empty_board.place_player(south_player, 2, 3)
        north_player.positions = [(2, 2)]

        empty_board.capture_move(north_player, 2, 2, 2, 4)

        # Board node reflects the capture
        assert empty_board.get_node(2, 4).occupied_by == north_player
        # But player.positions is stale
        assert (2, 4) not in north_player.positions
        assert (2, 2) in north_player.positions

    def test_place_player_sets_dead_attributes(self, empty_board, north_player):
        """place_player sets player.x and player.y — dead attributes unused by game logic."""
        empty_board.place_player(north_player, 3, 5)

        assert north_player.x == 3
        assert north_player.y == 5
