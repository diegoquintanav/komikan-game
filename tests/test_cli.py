"""Tests for the komikan-cli command-line interface."""

from unittest.mock import MagicMock, patch


class TestCLIEntry:
    """Test CLI entry point and argument parsing."""

    def test_cli_has_main_function(self):
        """CLI module must expose a main function."""
        from komikan.cli import main

        assert callable(main)

    def test_cli_parses_player_args(self):
        """CLI must accept --north and --south player arguments."""
        from komikan.cli import parse_args

        args = parse_args(["--north", "random", "--south", "human"])
        assert args.north == "random"
        assert args.south == "human"

    def test_cli_default_players(self):
        """CLI must default both players to 'human'."""
        from komikan.cli import parse_args

        args = parse_args([])
        assert args.north == "human"
        assert args.south == "human"

    def test_cli_accepts_delay(self):
        """CLI must accept --delay argument."""
        from komikan.cli import parse_args

        args = parse_args(["--delay", "0.5"])
        assert args.delay == 0.5

    def test_cli_delay_default_zero(self):
        """CLI must default delay to 0."""
        from komikan.cli import parse_args

        args = parse_args([])
        assert args.delay == 0

    def test_cli_prints_banner(self, capsys):
        """CLI must print a game banner."""
        from komikan.cli import print_banner

        print_banner()
        captured = capsys.readouterr()
        assert "KOMIKAN" in captured.out

    def test_cli_prints_game_state(self, capsys):
        """CLI must be able to print current game state."""
        from komikan.cli import print_board

        game = MagicMock()
        game.board_width = 5
        game.board_height = 8

        # Mock tokens
        north_token = MagicMock()
        north_token.side.value = "pangui"
        north_token.positions = [(2, 0)]

        south_token = MagicMock()
        south_token.side.value = "pu_trewa"
        south_token.positions = [(0, 5), (1, 5), (2, 5), (3, 5), (4, 5)]

        game.core_state.players = [north_token, south_token]

        print_board(game)
        captured = capsys.readouterr()
        assert len(captured.out) > 0  # should produce some output

    def test_cli_human_player_prompts_for_input(self):
        """CLI must call input() for human players."""
        from komikan.cli import get_human_move

        game = MagicMock()
        game.core_state.current_player.positions = [(2, 0)]
        game.get_valid_moves.return_value = (
            [MagicMock(x=2, y=1)],
            [],
        )

        with patch("builtins.input", return_value="2,0 2,1"):
            move = get_human_move(game)

        assert move is not None

    def test_cli_invalid_input_reprompts(self):
        """CLI must re-prompt on invalid move input."""
        from komikan.cli import get_human_move

        game = MagicMock()
        game.core_state.current_player.positions = [(2, 0)]
        game.get_valid_moves.return_value = (
            [MagicMock(x=2, y=1)],
            [],
        )

        # First two calls return bad input, third returns valid
        with patch("builtins.input", side_effect=["bad", "also bad", "2,0 2,1"]):
            move = get_human_move(game)

        assert move is not None

    def test_cli_llm_player_uses_provider(self):
        """CLI must create LLM provider when player is 'llm'."""
        from komikan.cli import create_player

        game = MagicMock()
        game.core_state.current_player.positions = [(2, 0)]
        game.get_valid_moves.return_value = (
            [MagicMock(x=2, y=1)],
            [],
        )

        mock_llm = MagicMock()
        mock_llm.chat.return_value = "from (2,0) to (2,1)"

        with patch("komikan.llm.LLMProvider", return_value=mock_llm) as mock_factory:
            _player = create_player("llm", game)
            mock_factory.assert_called_once()
