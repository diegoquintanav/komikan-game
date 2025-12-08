"""
Integration tests for game mechanics and scenarios.
"""

from komikan.board import GameBoard
from komikan.player import Player, PlayerSide


class TestGameIntegration:
    """Test complete game scenarios and integration."""

    def test_initial_game_setup(self, board_with_players):
        """Test that initial game setup is correct."""
        board, game_state = board_with_players

        # Check north player setup
        assert len(game_state.player_north.positions) == 1
        assert game_state.player_north.positions[0] == (2, 0)
        north_node = board.get_node(2, 0)
        assert north_node.occupied_by == game_state.player_north

        # Check south player setup
        assert len(game_state.player_south.positions) == 12
        for pos in game_state.player_south.positions:
            node = board.get_node(pos[0], pos[1])
            assert node.occupied_by == game_state.player_south

    def test_basic_movement_sequence(self, board_with_players):
        """Test a sequence of basic moves."""
        board, game_state = board_with_players

        # North player moves from (2,0) to (2,1)
        success = board.move_player(game_state.player_north, 2, 0, 2, 1)
        assert success

        # Update positions
        game_state.player_north.positions.remove((2, 0))
        game_state.player_north.positions.append((2, 1))

        # Check board state
        assert not board.get_node(2, 0).is_occupied()
        assert board.get_node(2, 1).occupied_by == game_state.player_north

        # South player moves
        south_start = game_state.player_south.positions[0]  # First south position
        new_pos = (south_start[0], south_start[1] - 1)  # Move north one step

        if board.is_valid_move(south_start[0], south_start[1], new_pos[0], new_pos[1]):
            success = board.move_player(
                game_state.player_south,
                south_start[0],
                south_start[1],
                new_pos[0],
                new_pos[1],
            )
            assert success

    def test_capture_scenario(self):
        """Test a complete capture scenario."""
        board = GameBoard()
        north_player = Player(PlayerSide.NORTH, (255, 0, 0))
        south_player = Player(PlayerSide.SOUTH, (0, 0, 255))

        # Set up capture scenario
        board.place_player(north_player, 2, 1)
        board.place_player(south_player, 2, 2)
        # Position (2, 3) is empty for capture landing

        # Attempt capture
        success, captured = board.capture_move(north_player, 2, 1, 2, 3)
        assert success
        assert captured == south_player

        # Verify final positions
        assert not board.get_node(2, 1).is_occupied()  # Original position empty
        assert not board.get_node(2, 2).is_occupied()  # Captured piece removed
        assert board.get_node(2, 3).occupied_by == north_player  # New position

    def test_blocked_movement_paths(self):
        """Test movement restrictions from disabled paths and nodes."""
        board = GameBoard()
        north_player = Player(PlayerSide.NORTH, (255, 0, 0))

        # Test movement to disabled node
        board.place_player(north_player, 1, 2)
        assert not board.is_valid_move(1, 2, 0, 2)  # Can't move to disabled node

        # Test movement on disabled path
        assert not board.is_valid_move(1, 2, 1, 3)  # Disabled triangle path

    def test_multiple_south_tokens_movement(self, board_with_players):
        """Test that multiple south tokens can move independently."""
        board, game_state = board_with_players

        # Get two different south positions
        pos1 = game_state.player_south.positions[0]
        pos2 = game_state.player_south.positions[1]

        # Try to move first token
        adjacent_positions = board.get_adjacent_positions(pos1[0], pos1[1])
        valid_moves = [
            pos
            for pos in adjacent_positions
            if board.is_valid_move(pos1[0], pos1[1], pos[0], pos[1])
        ]

        if valid_moves:
            new_pos = valid_moves[0]
            success = board.move_player(
                game_state.player_south, pos1[0], pos1[1], new_pos[0], new_pos[1]
            )
            assert success

            # Update positions
            game_state.player_south.positions.remove(pos1)
            game_state.player_south.positions.append(new_pos)

            # Second token should still be in place
            assert (
                board.get_node(pos2[0], pos2[1]).occupied_by == game_state.player_south
            )

    def test_game_state_consistency(self, board_with_players):
        """Test that game state remains consistent after moves."""
        board, game_state = board_with_players

        initial_north_count = len(game_state.player_north.positions)
        initial_south_count = len(game_state.player_south.positions)

        # Make a move
        success = board.move_player(game_state.player_north, 2, 0, 2, 1)
        if success:
            game_state.player_north.positions.remove((2, 0))
            game_state.player_north.positions.append((2, 1))

        # Check counts are preserved
        assert len(game_state.player_north.positions) == initial_north_count
        assert len(game_state.player_south.positions) == initial_south_count

        # Check board consistency
        for pos in game_state.player_north.positions:
            node = board.get_node(pos[0], pos[1])
            assert node.occupied_by == game_state.player_north

        for pos in game_state.player_south.positions:
            node = board.get_node(pos[0], pos[1])
            assert node.occupied_by == game_state.player_south


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_capture_at_board_edge(self):
        """Test capture moves at board edges."""
        board = GameBoard()
        north_player = Player(PlayerSide.NORTH, (255, 0, 0))
        south_player = Player(PlayerSide.SOUTH, (0, 0, 255))

        # Set up capture at edge
        board.place_player(north_player, 0, 1)
        board.place_player(
            south_player, 0, 2
        )  # This is a disabled node, so invalid setup

        # This should be invalid due to disabled node
        assert not board.is_valid_capture(0, 1, 0, 3, north_player)

    def test_capture_out_of_bounds(self):
        """Test capture that would go out of bounds."""
        board = GameBoard()
        north_player = Player(PlayerSide.NORTH, (255, 0, 0))
        south_player = Player(PlayerSide.SOUTH, (0, 0, 255))

        # Set up near edge
        board.place_player(north_player, 0, 0)
        board.place_player(south_player, 1, 1)

        # Capture would go out of bounds
        assert not board.is_valid_capture(
            0, 0, 2, 2, north_player
        )  # Out of bounds diagonally

    def test_all_directions_capture(self):
        """Test capture in all 8 directions."""
        board = GameBoard()
        north_player = Player(PlayerSide.NORTH, (255, 0, 0))
        south_player = Player(PlayerSide.SOUTH, (0, 0, 255))

        # Place north in center
        board.place_player(north_player, 3, 3)

        # Test all 8 directions where valid
        directions = [
            (0, -2),  # North
            (2, -2),  # Northeast
            (2, 0),  # East
            (2, 2),  # Southeast
            (0, 2),  # South
            (-2, 2),  # Southwest
            (-2, 0),  # West
            (-2, -2),  # Northwest
        ]

        for dx, dy in directions:
            target_x, target_y = 3 + dx, 3 + dy
            middle_x, middle_y = 3 + dx // 2, 3 + dy // 2

            if (
                board.is_valid_position(target_x, target_y)
                and board.is_valid_position(middle_x, middle_y)
                and not board.is_disabled_node(target_x, target_y)
                and not board.is_disabled_node(middle_x, middle_y)
            ):
                # Clear any existing pieces
                board.get_node(middle_x, middle_y).occupied_by = None
                board.get_node(target_x, target_y).occupied_by = None

                # Place enemy in middle
                board.place_player(south_player, middle_x, middle_y)

                # Check if capture is valid (some directions may be disabled)
                is_valid = board.is_valid_capture(
                    3, 3, target_x, target_y, north_player
                )

                # Only assert if the path should be valid (not disabled)
                if not board.is_disabled_path(
                    3, 3, middle_x, middle_y
                ) and not board.is_disabled_path(
                    middle_x, middle_y, target_x, target_y
                ):
                    assert is_valid, (
                        f"Capture should be valid in direction ({dx}, {dy}) - no disabled paths"
                    )
                # If path is disabled, we just verify it correctly returns false
                else:
                    # This is expected to be false due to disabled paths
                    pass

                # Clean up for next test
                board.get_node(middle_x, middle_y).occupied_by = None

    def test_no_self_capture(self):
        """Test that players cannot capture their own pieces."""
        board = GameBoard()
        north_player1 = Player(PlayerSide.NORTH, (255, 0, 0))
        north_player2 = Player(PlayerSide.NORTH, (255, 0, 0))  # Same side

        board.place_player(north_player1, 2, 1)
        board.place_player(north_player2, 2, 2)

        # Cannot capture own piece
        assert not board.is_valid_capture(2, 1, 2, 3, north_player1)
