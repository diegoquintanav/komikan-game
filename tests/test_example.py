"""
Example test showing how to add new tests to the Komikan game test suite.
This file demonstrates testing patterns and can be used as a template.
"""

import pytest
from board import GameBoard
from player import Player, PlayerSide, GameState


class TestExample:
    """Example test class showing common testing patterns."""

    def test_example_basic_assertion(self):
        """Example of a basic assertion test."""
        board = GameBoard()
        assert board.WIDTH == 5
        assert board.HEIGHT == 8

    def test_example_with_fixture(self, empty_board):
        """Example using a fixture from conftest.py."""
        # Fixtures are defined in conftest.py and automatically available
        assert empty_board.get_node(0, 0) is not None
        assert empty_board.get_node(2, 3) is not None

    def test_example_with_multiple_fixtures(self, empty_board, north_player, south_player):
        """Example using multiple fixtures."""
        # Place players and test interaction
        empty_board.place_player(north_player, 1, 1)
        empty_board.place_player(south_player, 1, 2)

        # Test that they cannot occupy same space
        success = empty_board.place_player(north_player, 1, 2)
        assert not success

    def test_example_parametrized(self, empty_board):
        """Example of testing multiple inputs."""
        # Test multiple positions are valid
        valid_positions = [(0, 0), (4, 7), (2, 4)]
        for x, y in valid_positions:
            assert empty_board.is_valid_position(x, y)

        # Test multiple positions are invalid
        invalid_positions = [(-1, 0), (5, 0), (0, 8)]
        for x, y in invalid_positions:
            assert not empty_board.is_valid_position(x, y)

    @pytest.mark.parametrize("x,y,expected", [
        (0, 0, True),   # Valid corner
        (2, 4, True),   # Valid center
        (4, 7, True),   # Valid corner
        (-1, 0, False), # Invalid (out of bounds)
        (5, 0, False),  # Invalid (out of bounds)
        (0, 8, False),  # Invalid (out of bounds)
    ])
    def test_example_parametrize_decorator(self, empty_board, x, y, expected):
        """Example using pytest parametrize decorator."""
        assert empty_board.is_valid_position(x, y) == expected

    def test_example_exception_handling(self, empty_board):
        """Example of testing that exceptions are raised."""
        # Test that getting a node with invalid coordinates doesn't raise exception
        # (returns None instead)
        result = empty_board.get_node(-1, -1)
        assert result is None

        # If you needed to test for exceptions:
        # with pytest.raises(ValueError):
        #     some_function_that_should_raise_error()

    def test_example_setup_teardown(self, empty_board):
        """Example showing test setup and cleanup."""
        # Setup - create test data
        player = Player(PlayerSide.NORTH, (255, 0, 0))

        # Test action
        success = empty_board.place_player(player, 2, 2)
        assert success

        # Verify state
        node = empty_board.get_node(2, 2)
        assert node.occupied_by == player

        # Teardown happens automatically (new board each test)

    def test_example_game_scenario(self):
        """Example of testing a complete game scenario."""
        # Create a complete game setup
        board = GameBoard()
        game_state = GameState()

        # Set up initial positions
        north_positions = game_state.player_north.get_starting_positions()
        for x, y in north_positions:
            board.place_player(game_state.player_north, x, y)
            game_state.player_north.positions.append((x, y))

        # Test initial state
        assert len(game_state.player_north.positions) == 1
        assert game_state.current_player == game_state.player_north

        # Perform a move
        old_pos = game_state.player_north.positions[0]
        new_pos = (old_pos[0], old_pos[1] + 1)

        success = board.move_player(
            game_state.player_north,
            old_pos[0], old_pos[1],
            new_pos[0], new_pos[1]
        )

        if success:
            # Update game state
            game_state.player_north.positions.remove(old_pos)
            game_state.player_north.positions.append(new_pos)
            game_state.switch_turn()

            # Verify final state
            assert game_state.current_player == game_state.player_south
            assert new_pos in game_state.player_north.positions
            assert old_pos not in game_state.player_north.positions


# Example of how to mark tests with custom markers (defined in pytest.ini)
@pytest.mark.performance
def test_example_performance_marked():
    """Example test marked as performance test."""
    # This test can be skipped with: pytest -m "not performance"
    board = GameBoard()
    # Performance test code here
    pass


@pytest.mark.integration
def test_example_integration_marked():
    """Example test marked as integration test."""
    # This test can be run with: pytest -m integration
    # Integration test code here
    pass


# Skip a test conditionally
@pytest.mark.skip(reason="Example of skipped test")
def test_example_skipped():
    """Example of a test that will be skipped."""
    pass


# Expected failure
@pytest.mark.xfail(reason="Known issue - example")
def test_example_expected_failure():
    """Example of test expected to fail."""
    assert False  # This failure is expected


# How to add new test files:
# 1. Create file starting with test_*.py in tests/ directory
# 2. Import necessary modules and fixtures
# 3. Create test classes starting with Test*
# 4. Create test functions starting with test_*
# 5. Use fixtures from conftest.py or create local ones
# 6. Run with: uv run pytest tests/test_new_file.py -v