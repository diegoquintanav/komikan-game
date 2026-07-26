"""Tests for the random opponent implementation."""

from unittest.mock import MagicMock
from komikan.agent.opponent import RandomOpponent


class TestRandomOpponent:
    def test_import(self):
        assert RandomOpponent is not None

    def test_fetches_valid_moves_from_api(self):
        opponent = RandomOpponent(base_url="http://localhost:8000", game_id="test-123")

        mock_api = MagicMock()
        resp = MagicMock()
        resp.status_code = 200
        resp.json.return_value = {
            "tokens": [
                {"position": [0, 5], "moves": [{"type": "advance", "to": [0, 6], "description": "move"}]},
                {"position": [1, 5], "moves": [{"type": "advance", "to": [1, 6], "description": "move"}, {"type": "advance", "to": [0, 6], "description": "move"}]},
            ]
        }
        mock_api.get.return_value = resp

        move_resp = MagicMock()
        move_resp.status_code = 200
        move_resp.json.return_value = {"status": "ok"}
        mock_api.post.return_value = move_resp

        opponent._client = mock_api
        opponent.choose_move()

        get_calls = mock_api.get.call_args_list
        assert any("all-valid-moves" in str(c) for c in get_calls)

    def test_posts_move_to_api(self):
        opponent = RandomOpponent(base_url="http://localhost:8000", game_id="test-123")

        mock_api = MagicMock()
        resp = MagicMock()
        resp.status_code = 200
        resp.json.return_value = {
            "tokens": [
                {"position": [2, 5], "moves": [{"type": "advance", "to": [2, 6], "description": "move"}]},
            ]
        }
        mock_api.get.return_value = resp

        move_resp = MagicMock()
        move_resp.status_code = 200
        move_resp.json.return_value = {"status": "ok"}
        mock_api.post.return_value = move_resp

        opponent._client = mock_api
        opponent.choose_move()

        mock_api.post.assert_called_once()
        post_url = mock_api.post.call_args[0][0]
        assert "/moves" in post_url

    def test_chooses_from_available_moves(self):
        opponent = RandomOpponent(base_url="http://localhost:8000", game_id="test-123")

        mock_api = MagicMock()
        resp = MagicMock()
        resp.status_code = 200
        resp.json.return_value = {
            "tokens": [
                {"position": [2, 5], "moves": [{"type": "advance", "to": [2, 6], "description": "move"}, {"type": "advance", "to": [1, 6], "description": "move"}]},
            ]
        }
        mock_api.get.return_value = resp

        move_resp = MagicMock()
        move_resp.status_code = 200
        move_resp.json.return_value = {"status": "ok"}
        mock_api.post.return_value = move_resp

        opponent._client = mock_api
        result = opponent.choose_move()

        assert result is not None
        post_body = mock_api.post.call_args[1].get(
            "json"
        ) or mock_api.post.call_args.kwargs.get("json")
        assert post_body is not None
        assert post_body["from_x"] == 2
        assert post_body["from_y"] == 5
        assert post_body["to_x"] in [2, 1]
        assert post_body["to_y"] == 6

    def test_choose_move_returns_move_dict(self):
        opponent = RandomOpponent(base_url="http://localhost:8000", game_id="test-123")

        mock_api = MagicMock()
        resp = MagicMock()
        resp.status_code = 200
        resp.json.return_value = {
            "tokens": [
                {"position": [0, 6], "moves": [{"type": "advance", "to": [0, 7], "description": "move"}]},
            ]
        }
        mock_api.get.return_value = resp

        move_resp = MagicMock()
        move_resp.status_code = 200
        move_resp.json.return_value = {"status": "ok"}
        mock_api.post.return_value = move_resp

        opponent._client = mock_api
        result = opponent.choose_move()

        assert "from_x" in result
        assert "from_y" in result
        assert "to_x" in result
        assert "to_y" in result
