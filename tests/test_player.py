"""
Tests for Player and GameState classes.
"""

from komikan.player import Player, PlayerSide


class TestPlayerSide:
    """Test PlayerSide enum."""

    def test_player_side_values(self):
        """Test player side enum values."""
        assert PlayerSide.NORTH.value == "pangui"
        assert PlayerSide.SOUTH.value == "pu trewa"


class TestPlayer:
    """Test Player class."""

    def test_player_creation(self):
        """Test player initialization."""
        color = (255, 0, 0)
        player = Player(PlayerSide.NORTH, color)

        assert player.side == PlayerSide.NORTH
        assert player.color == color
        assert player.positions == []

    def test_north_starting_positions(self, north_player):
        """Test north player starting positions."""
        positions = north_player.get_starting_positions()
        assert positions == [(2, 1)]

    def test_south_starting_positions(self, south_player):
        """Test south player starting positions."""
        positions = south_player.get_starting_positions()

        # Should have exactly 12 positions
        assert len(positions) == 12

        # Check expected positions
        expected = []
        # First and last column (x=0, x=4) and fifth row
        for x in [0, 4]:
            expected.append((x, 5))
        # Bottom two rows (y=6,7)
        for y in [6, 7]:
            for x in range(5):
                expected.append((x, y))

        expected = expected[:12]  # Take exactly 12
        for pos in expected:
            assert pos in positions

    def test_get_token_number(self, south_player):
        """Test token number calculation."""
        # Set up some positions
        south_player.positions = [(0, 6), (1, 6), (2, 6)]

        assert south_player.get_token_number(0, 6) == 1
        assert south_player.get_token_number(1, 6) == 2
        assert south_player.get_token_number(2, 6) == 3
        assert south_player.get_token_number(3, 6) == 0  # Not found

    def test_player_repr(self, north_player):
        """Test player string representation."""
        north_player.positions = [(2, 0)]
        expected = "Player(pangui, positions=[(2, 0)])"
        assert str(north_player) == expected


class TestGameState:
    """Test GameState class."""

    def test_game_state_initialization(self, game_state):
        """Test game state creation."""
        assert game_state.player_north.side == PlayerSide.NORTH
        assert game_state.player_south.side == PlayerSide.SOUTH
        assert game_state.current_player == game_state.player_north  # North starts
        assert game_state.selected_player is None
        assert not game_state.game_over

    def test_switch_turn(self, game_state):
        """Test turn switching."""
        # Initially north player's turn
        assert game_state.current_player == game_state.player_north

        # Switch to south
        game_state.switch_turn()
        assert game_state.current_player == game_state.player_south

        # Switch back to north
        game_state.switch_turn()
        assert game_state.current_player == game_state.player_north

    def test_get_other_player(self, game_state):
        """Test getting the non-current player."""
        # Current player is north
        assert game_state.current_player == game_state.player_north
        assert game_state.get_other_player() == game_state.player_south

        # Switch and test again
        game_state.switch_turn()
        assert game_state.current_player == game_state.player_south
        assert game_state.get_other_player() == game_state.player_north

    def test_player_colors(self, game_state):
        """Test that players have different colors."""
        north_color = game_state.player_north.color
        south_color = game_state.player_south.color
        assert north_color != south_color

        # Check colors are RGB tuples
        assert len(north_color) == 3
        assert len(south_color) == 3
        assert all(0 <= c <= 255 for c in north_color)
        assert all(0 <= c <= 255 for c in south_color)
