"""
Performance tests for the Komikan game.
"""

import time
from komikan.board import GameBoard
from komikan.player import Player, PlayerSide, GameState


class TestPerformance:
    """Test game performance characteristics."""

    def test_board_creation_performance(self):
        """Test board creation is fast."""
        start_time = time.time()

        boards = [GameBoard() for _ in range(100)]

        end_time = time.time()
        elapsed = end_time - start_time

        # Should create 100 boards in less than 1 second
        assert elapsed < 1.0
        assert len(boards) == 100

    def test_movement_validation_performance(self):
        """Test movement validation performance."""
        board = GameBoard()
        north_player = Player(PlayerSide.NORTH, (255, 0, 0))
        board.place_player(north_player, 2, 2)

        start_time = time.time()

        # Test 1000 movement validations
        for _ in range(1000):
            board.is_valid_move(2, 2, 2, 3)
            board.is_valid_move(2, 2, 3, 3)
            board.is_valid_move(2, 2, 1, 1)

        end_time = time.time()
        elapsed = end_time - start_time

        # Should complete 3000 validations in less than 1 second
        assert elapsed < 1.0

    def test_capture_validation_performance(self):
        """Test capture validation performance."""
        board = GameBoard()
        north_player = Player(PlayerSide.NORTH, (255, 0, 0))
        south_player = Player(PlayerSide.SOUTH, (0, 0, 255))

        board.place_player(north_player, 2, 1)
        board.place_player(south_player, 2, 2)

        start_time = time.time()

        # Test 1000 capture validations
        for _ in range(1000):
            board.is_valid_capture(2, 1, 2, 3, north_player)
            board.is_valid_capture(2, 1, 0, 3, north_player)  # Invalid
            board.is_valid_capture(2, 1, 4, 3, north_player)  # Invalid

        end_time = time.time()
        elapsed = end_time - start_time

        # Should complete 3000 validations in less than 1 second
        assert elapsed < 1.0

    def test_large_game_state_operations(self):
        """Test operations with full game state."""
        board = GameBoard()
        game_state = GameState()

        # Set up full initial positions
        north_positions = game_state.player_north.get_starting_positions()
        for x, y in north_positions:
            board.place_player(game_state.player_north, x, y)
            game_state.player_north.positions.append((x, y))

        south_positions = game_state.player_south.get_starting_positions()
        for x, y in south_positions:
            board.place_player(game_state.player_south, x, y)
            game_state.player_south.positions.append((x, y))

        start_time = time.time()

        # Perform many game state operations
        for _ in range(100):
            # Check all positions
            for pos in game_state.player_north.positions:
                adjacent = board.get_adjacent_positions(pos[0], pos[1])
                for adj_pos in adjacent:
                    board.is_valid_move(pos[0], pos[1], adj_pos[0], adj_pos[1])

        end_time = time.time()
        elapsed = end_time - start_time

        # Should complete in reasonable time (less than 2 seconds)
        assert elapsed < 2.0


class TestMemoryUsage:
    """Test memory usage characteristics."""

    def test_board_memory_efficiency(self):
        """Test that boards don't consume excessive memory."""
        import sys

        # Create a board and measure basic size
        board = GameBoard()

        # Should be reasonable size (less than 10KB for basic board)
        # This is a rough check - actual size will vary by Python implementation
        assert sys.getsizeof(board) < 10000

    def test_no_memory_leaks_in_moves(self):
        """Test that repeated moves don't leak memory."""
        import gc

        board = GameBoard()
        north_player = Player(PlayerSide.NORTH, (255, 0, 0))
        board.place_player(north_player, 2, 2)

        # Force garbage collection
        gc.collect()
        initial_objects = len(gc.get_objects())

        # Perform many moves
        for i in range(50):
            if i % 2 == 0:
                board.move_player(north_player, 2, 2, 2, 3)
            else:
                board.move_player(north_player, 2, 3, 2, 2)

        # Force garbage collection again
        gc.collect()
        final_objects = len(gc.get_objects())

        # Should not have significantly more objects (allowing some variance)
        object_increase = final_objects - initial_objects
        assert object_increase < 100  # Allow some variance but not excessive growth
