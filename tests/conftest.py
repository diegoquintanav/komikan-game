"""
Test fixtures and configuration for Komikan game tests.
"""

import pytest
import sys
import os

from komikan.board import GameBoard
from komikan.player import Player, PlayerSide, GameState

@pytest.fixture
def empty_board():
    """Create an empty game board."""
    return GameBoard()


@pytest.fixture
def board_with_players():
    """Create a board with players in starting positions."""
    board = GameBoard()
    game_state = GameState()

    # Place north player
    north_positions = game_state.player_north.get_starting_positions()
    for x, y in north_positions:
        board.place_player(game_state.player_north, x, y)
        game_state.player_north.positions.append((x, y))

    # Place south player
    south_positions = game_state.player_south.get_starting_positions()
    for x, y in south_positions:
        board.place_player(game_state.player_south, x, y)
        game_state.player_south.positions.append((x, y))

    return board, game_state


@pytest.fixture
def north_player():
    """Create a north player."""
    return Player(PlayerSide.NORTH, (255, 100, 100))


@pytest.fixture
def south_player():
    """Create a south player."""
    return Player(PlayerSide.SOUTH, (100, 100, 255))


@pytest.fixture
def game_state():
    """Create a fresh game state."""
    return GameState()


@pytest.fixture
def capture_scenario_board():
    """Create a board set up for testing capture mechanics."""
    board = GameBoard()
    north_player = Player(PlayerSide.NORTH, (255, 100, 100))
    south_player = Player(PlayerSide.SOUTH, (100, 100, 255))

    # Place north player at (2, 2)
    board.place_player(north_player, 2, 2)
    north_player.positions = [(2, 2)]

    # Place south player at (2, 3) - one step south of north
    board.place_player(south_player, 2, 3)
    south_player.positions = [(2, 3)]

    # Position (2, 4) should be empty for capture to land

    return board, north_player, south_player
