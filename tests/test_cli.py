"""Tests for the komikan-agent command-line interface."""

from unittest.mock import MagicMock, patch

import httpx


class TestCLIParseArgs:
    """Test CLI argument parsing."""

    def test_main_is_callable(self):
        from komikan.cli import main

        assert callable(main)

    def test_defaults(self):
        from komikan.cli import parse_args

        args = parse_args([])
        assert args.provider == "openai"
        assert args.model is None
        assert args.side == "north"
        assert args.opponent == "random"
        assert args.delay == 0.5
        assert args.base_url == "http://localhost:8000"

    def test_provider_openai(self):
        from komikan.cli import parse_args

        args = parse_args(["--provider", "openai"])
        assert args.provider == "openai"

    def test_provider_anthropic(self):
        from komikan.cli import parse_args

        args = parse_args(["--provider", "anthropic"])
        assert args.provider == "anthropic"

    def test_model_override(self):
        from komikan.cli import parse_args

        args = parse_args(["--model", "gpt-4o-mini"])
        assert args.model == "gpt-4o-mini"

    def test_side_north(self):
        from komikan.cli import parse_args

        args = parse_args(["--side", "north"])
        assert args.side == "north"

    def test_side_south(self):
        from komikan.cli import parse_args

        args = parse_args(["--side", "south"])
        assert args.side == "south"

    def test_opponent_random(self):
        from komikan.cli import parse_args

        args = parse_args(["--opponent", "random"])
        assert args.opponent == "random"

    def test_opponent_human(self):
        from komikan.cli import parse_args

        args = parse_args(["--opponent", "human"])
        assert args.opponent == "human"

    def test_delay_custom(self):
        from komikan.cli import parse_args

        args = parse_args(["--delay", "1.5"])
        assert args.delay == 1.5

    def test_base_url_custom(self):
        from komikan.cli import parse_args

        args = parse_args(["--base-url", "http://myhost:9000"])
        assert args.base_url == "http://myhost:9000"

    def test_all_flags_combined(self):
        from komikan.cli import parse_args

        args = parse_args(
            [
                "--provider",
                "anthropic",
                "--model",
                "claude-opus-4-20250514",
                "--side",
                "south",
                "--opponent",
                "human",
                "--delay",
                "2.0",
                "--base-url",
                "http://prod:8080",
            ]
        )
        assert args.provider == "anthropic"
        assert args.model == "claude-opus-4-20250514"
        assert args.side == "south"
        assert args.opponent == "human"
        assert args.delay == 2.0
        assert args.base_url == "http://prod:8080"


class TestCLIBanner:
    """Test CLI banner and display functions."""

    def test_print_banner(self, capsys):
        from komikan.cli import print_banner

        print_banner()
        captured = capsys.readouterr()
        assert "KOMIKAN" in captured.out
        assert "LLM Agent Mode" in captured.out

    def test_print_board_shows_tokens(self, capsys):
        from komikan.cli import print_board

        state = {
            "north_player": {"positions": [[2, 0]], "token_count": 1},
            "south_player": {"positions": [[0, 5], [1, 5]], "token_count": 2},
        }
        print_board(state)
        captured = capsys.readouterr()
        assert "N" in captured.out
        assert "S" in captured.out
        assert "." in captured.out

    def test_print_board_empty(self, capsys):
        from komikan.cli import print_board

        state = {
            "north_player": {"positions": [], "token_count": 0},
            "south_player": {"positions": [], "token_count": 0},
        }
        print_board(state)
        captured = capsys.readouterr()
        # Should print 8 rows of dots
        assert captured.out.count(".") >= 40

    def test_print_game_info(self, capsys):
        from komikan.cli import print_game_info

        state = {
            "status": "in_progress",
            "current_player": "north",
            "move_count": 5,
            "north_player": {"token_count": 3},
            "south_player": {"token_count": 8},
        }
        print_game_info(state)
        captured = capsys.readouterr()
        assert "in_progress" in captured.out
        assert "north" in captured.out
        assert "Move #5" in captured.out


class TestCLIFetchGameState:
    """Test API communication helpers."""

    def test_create_game(self):
        from komikan.cli import create_game

        mock_client = MagicMock(spec=httpx.Client)
        mock_resp = MagicMock()
        mock_resp.json.return_value = {"game": {"game_id": "test-123"}}
        mock_resp.raise_for_status = MagicMock()
        mock_client.post.return_value = mock_resp

        game_id = create_game(mock_client)
        assert game_id == "test-123"
        mock_client.post.assert_called_once_with("/api/games")

    def test_fetch_game_state(self):
        from komikan.cli import fetch_game_state

        mock_client = MagicMock(spec=httpx.Client)
        mock_resp = MagicMock()
        mock_resp.json.return_value = {
            "game": {"status": "in_progress", "game_id": "x"}
        }
        mock_resp.raise_for_status = MagicMock()
        mock_client.get.return_value = mock_resp

        state = fetch_game_state(mock_client, "x")
        assert state["status"] == "in_progress"


class TestCLIRandomMove:
    """Test random move execution."""

    def test_play_random_move(self):
        from komikan.cli import play_random_move

        mock_client = MagicMock(spec=httpx.Client)

        # all-valid-moves response
        moves_resp = MagicMock()
        moves_resp.json.return_value = {
            "tokens": [
                {
                    "position": [2, 0],
                    "moves": [{"to": [2, 1], "type": "advance"}],
                }
            ]
        }
        moves_resp.raise_for_status = MagicMock()

        # move execution response
        move_resp = MagicMock()
        move_resp.json.return_value = {"game": {"status": "in_progress"}}
        move_resp.raise_for_status = MagicMock()

        mock_client.get.return_value = moves_resp
        mock_client.post.return_value = move_resp

        result = play_random_move(mock_client, "test-id")
        assert result is not None
        mock_client.post.assert_called_once()


class TestCLIMainFlow:
    """Test the main CLI flow with mocked dependencies."""

    def test_main_exits_without_api_key(self, capsys):
        from komikan.cli import main

        with patch.dict("os.environ", {}, clear=True):
            main(["--provider", "openai"])

        captured = capsys.readouterr()
        assert "OPENAI_API_KEY" in captured.out

    def test_main_exits_without_connection(self, capsys):
        from komikan.cli import main

        with patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"}):
            with patch("httpx.Client") as MockClient:
                client_instance = MagicMock()
                client_instance.get.side_effect = httpx.ConnectError("refused")
                MockClient.return_value = client_instance

                main(["--provider", "openai", "--base-url", "http://localhost:19999"])

        captured = capsys.readouterr()
        assert "Cannot connect" in captured.out

    def test_main_runs_agent_vs_random(self, capsys):
        """Full game loop: agent (mocked LLM) vs random opponent."""
        from komikan.cli import main

        game_id = "test-game-001"

        call_count = 0

        def mock_get(url, **kwargs):
            nonlocal call_count
            call_count += 1
            if url == "/":
                return MagicMock(status_code=200)
            if url == f"/api/games/{game_id}":
                return _make_game_state_response(
                    game_id, "in_progress", "north", call_count
                )
            if "/all-valid-moves" in url:
                return _make_valid_moves_response()
            return MagicMock(status_code=200)

        move_call_count = 0

        def mock_post(url, **kwargs):
            nonlocal move_call_count
            move_call_count += 1
            if "/api/games" in url and "moves" not in url:
                # create game
                resp = MagicMock()
                resp.json.return_value = {"game": {"game_id": game_id}}
                resp.raise_for_status = MagicMock()
                return resp
            # execute move
            resp = MagicMock()
            resp.json.return_value = {
                "game": _make_game_state_dict(
                    game_id, "in_progress", "south", move_call_count
                )
            }
            resp.raise_for_status = MagicMock()
            return resp

        mock_provider = MagicMock()
        mock_provider.chat.return_value = MagicMock(
            tool_calls=[
                MagicMock(
                    name="make_move",
                    arguments={"from_x": 2, "from_y": 0, "to_x": 2, "to_y": 1},
                )
            ],
            text=None,
        )

        with patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"}):
            with patch("komikan.agent.agent.KomikanAgent.play_turn") as mock_play:
                mock_play.return_value = {"status": "in_progress"}
                with patch("httpx.Client") as MockClient:
                    client_instance = MagicMock()
                    client_instance.get.side_effect = mock_get
                    client_instance.post.side_effect = mock_post
                    client_instance.close = MagicMock()
                    MockClient.return_value = client_instance

                    main(
                        [
                            "--provider",
                            "openai",
                            "--side",
                            "north",
                            "--opponent",
                            "random",
                            "--delay",
                            "0",
                        ]
                    )

        captured = capsys.readouterr()
        assert "KOMIKAN" in captured.out
        assert "Game created" in captured.out


def _make_game_state_dict(
    game_id: str, status: str, current_player: str, move_count: int
) -> dict:
    return {
        "game_id": game_id,
        "status": status,
        "current_player": current_player,
        "move_count": move_count,
        "north_player": {"positions": [[2, 0]], "token_count": 1},
        "south_player": {"positions": [[0, 5]], "token_count": 1},
    }


def _make_game_state_response(
    game_id: str, status: str, current_player: str, move_count: int
):
    resp = MagicMock()
    resp.json.return_value = {
        "game": _make_game_state_dict(game_id, status, current_player, move_count)
    }
    resp.raise_for_status = MagicMock()
    return resp


def _make_valid_moves_response():
    resp = MagicMock()
    resp.json.return_value = {
        "tokens": [
            {
                "position": [2, 0],
                "moves": [{"to": [2, 1], "type": "advance"}],
            }
        ]
    }
    resp.raise_for_status = MagicMock()
    return resp
