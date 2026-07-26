"""Tests for the LLM-powered Komikan agent."""

from unittest.mock import MagicMock
from komikan.agent.agent import KomikanAgent
from komikan.agent.provider import LLMProvider, LLMResponse, ToolCall


class TestKomikanAgent:
    def test_import(self):
        assert KomikanAgent is not None

    def test_default_side_is_north(self):
        mock_provider = MagicMock(spec=LLMProvider)
        agent = KomikanAgent(provider=mock_provider, base_url="http://localhost:8000")
        assert agent.side == "north"

    def test_explicit_side_south(self):
        mock_provider = MagicMock(spec=LLMProvider)
        agent = KomikanAgent(provider=mock_provider, base_url="http://localhost:8000", side="south")
        assert agent.side == "south"

    def test_play_turn_fetches_game_state(self):
        mock_provider = MagicMock(spec=LLMProvider)
        mock_provider.chat.return_value = LLMResponse(tool_calls=[], text=None)
        agent = KomikanAgent(provider=mock_provider, base_url="http://localhost:8000", game_id="test-123")

        mock_api = MagicMock()
        mock_api.get.return_value.json.return_value = {
            "status": "in_progress",
            "current_player": "north",
            "move_count": 5,
            "board": {},
        }
        mock_api.get.return_value.status_code = 200
        agent._client = mock_api

        agent.play_turn()

        calls = [c for c in mock_api.method_calls if "get" in c[0]]
        assert len(calls) >= 1

    def test_play_turn_fetches_valid_moves(self):
        mock_provider = MagicMock(spec=LLMProvider)
        mock_provider.chat.return_value = LLMResponse(tool_calls=[], text=None)
        agent = KomikanAgent(provider=mock_provider, base_url="http://localhost:8000", game_id="test-123")

        mock_api = MagicMock()
        game_state_resp = MagicMock()
        game_state_resp.json.return_value = {
            "status": "in_progress",
            "current_player": "north",
            "move_count": 5,
            "board": {},
        }
        game_state_resp.status_code = 200

        valid_moves_resp = MagicMock()
        valid_moves_resp.json.return_value = {"tokens": []}
        valid_moves_resp.status_code = 200

        mock_api.get.side_effect = [game_state_resp, valid_moves_resp]
        agent._client = mock_api

        agent.play_turn()

        assert mock_api.get.call_count == 2

    def test_play_turn_calls_llm(self):
        mock_provider = MagicMock(spec=LLMProvider)
        mock_provider.chat.return_value = LLMResponse(
            tool_calls=[ToolCall(name="make_move", arguments={"from_x": 2, "from_y": 0, "to_x": 2, "to_y": 1})],
            text=None,
        )
        agent = KomikanAgent(provider=mock_provider, base_url="http://localhost:8000", game_id="test-123")

        mock_api = MagicMock()
        game_state_resp = MagicMock()
        game_state_resp.json.return_value = {
            "status": "in_progress",
            "current_player": "north",
            "move_count": 5,
            "board": {},
        }
        game_state_resp.status_code = 200

        valid_moves_resp = MagicMock()
        valid_moves_resp.json.return_value = {"tokens": [{"from": [2, 0], "moves": [[2, 1]], "captures": []}]}
        valid_moves_resp.status_code = 200

        move_resp = MagicMock()
        move_resp.json.return_value = {"status": "ok", "new_state": {"status": "in_progress", "current_player": "south"}}
        move_resp.status_code = 200

        mock_api.get.side_effect = [game_state_resp, valid_moves_resp]
        mock_api.post.return_value = move_resp
        agent._client = mock_api

        agent.play_turn()

        mock_provider.chat.assert_called_once()
        call_kwargs = mock_provider.chat.call_args
        assert "system_prompt" in call_kwargs.kwargs or len(call_kwargs.args) >= 1

    def test_play_turn_executes_valid_move(self):
        mock_provider = MagicMock(spec=LLMProvider)
        mock_provider.chat.return_value = LLMResponse(
            tool_calls=[ToolCall(name="make_move", arguments={"from_x": 2, "from_y": 0, "to_x": 2, "to_y": 1})],
            text=None,
        )
        agent = KomikanAgent(provider=mock_provider, base_url="http://localhost:8000", game_id="test-123")

        mock_api = MagicMock()
        game_state_resp = MagicMock()
        game_state_resp.json.return_value = {
            "status": "in_progress",
            "current_player": "north",
            "move_count": 5,
            "board": {},
        }
        game_state_resp.status_code = 200

        valid_moves_resp = MagicMock()
        valid_moves_resp.json.return_value = {
            "tokens": [{"from": [2, 0], "moves": [[2, 1]], "captures": []}]
        }
        valid_moves_resp.status_code = 200

        move_resp = MagicMock()
        move_resp.json.return_value = {"status": "ok", "new_state": {"status": "in_progress", "current_player": "south", "move_count": 6, "board": {}}}
        move_resp.status_code = 200

        mock_api.get.side_effect = [game_state_resp, valid_moves_resp]
        mock_api.post.return_value = move_resp
        agent._client = mock_api

        agent.play_turn()

        mock_api.post.assert_called_once()
        post_url = mock_api.post.call_args[0][0]
        assert "/moves" in post_url

    def test_play_turn_retries_invalid_move(self):
        mock_provider = MagicMock(spec=LLMProvider)
        invalid_response = LLMResponse(
            tool_calls=[ToolCall(name="make_move", arguments={"from_x": 0, "from_y": 0, "to_x": 0, "to_y": 0})],
            text=None,
        )
        valid_response = LLMResponse(
            tool_calls=[ToolCall(name="make_move", arguments={"from_x": 2, "from_y": 0, "to_x": 2, "to_y": 1})],
            text=None,
        )
        mock_provider.chat.side_effect = [invalid_response, valid_response]

        agent = KomikanAgent(provider=mock_provider, base_url="http://localhost:8000", game_id="test-123")

        valid_moves = {"tokens": [{"from": [2, 0], "moves": [[2, 1]], "captures": []}]}

        mock_api = MagicMock()
        game_state_resp = MagicMock()
        game_state_resp.json.return_value = {
            "status": "in_progress",
            "current_player": "north",
            "move_count": 5,
            "board": {},
        }
        game_state_resp.status_code = 200

        valid_moves_resp = MagicMock()
        valid_moves_resp.json.return_value = valid_moves
        valid_moves_resp.status_code = 200

        move_resp = MagicMock()
        move_resp.json.return_value = {"status": "ok", "new_state": {"status": "in_progress", "current_player": "south", "move_count": 6, "board": {}}}
        move_resp.status_code = 200

        mock_api.get.side_effect = [game_state_resp, valid_moves_resp, game_state_resp, valid_moves_resp]
        mock_api.post.return_value = move_resp
        agent._client = mock_api

        agent.play_turn()

        assert mock_provider.chat.call_count == 2

    def test_play_turn_falls_back_to_random_after_3_failures(self):
        mock_provider = MagicMock(spec=LLMProvider)
        bad_response = LLMResponse(
            tool_calls=[ToolCall(name="make_move", arguments={"from_x": 0, "from_y": 0, "to_x": 0, "to_y": 0})],
            text=None,
        )
        mock_provider.chat.return_value = bad_response

        agent = KomikanAgent(provider=mock_provider, base_url="http://localhost:8000", game_id="test-123")

        valid_moves = {"tokens": [{"from": [2, 0], "moves": [[2, 1]], "captures": []}]}

        mock_api = MagicMock()
        game_state_resp = MagicMock()
        game_state_resp.json.return_value = {
            "status": "in_progress",
            "current_player": "north",
            "move_count": 5,
            "board": {},
        }
        game_state_resp.status_code = 200

        valid_moves_resp = MagicMock()
        valid_moves_resp.json.return_value = valid_moves
        valid_moves_resp.status_code = 200

        move_resp = MagicMock()
        move_resp.json.return_value = {"status": "ok", "new_state": {"status": "in_progress", "current_player": "south", "move_count": 6, "board": {}}}
        move_resp.status_code = 200

        mock_api.get.side_effect = [game_state_resp, valid_moves_resp] * 5
        mock_api.post.return_value = move_resp
        agent._client = mock_api

        agent.play_turn()

        assert mock_api.post.call_count == 1
        post_body = mock_api.post.call_args[1].get("json") or mock_api.post.call_args[0][1] if len(mock_api.post.call_args[0]) > 1 else None
        if post_body is None:
            post_body = mock_api.post.call_args.kwargs.get("json")
        assert post_body is not None
        assert post_body["from_x"] == 2
        assert post_body["from_y"] == 0

    def test_play_turn_skips_when_not_current_player(self):
        mock_provider = MagicMock(spec=LLMProvider)
        agent = KomikanAgent(provider=mock_provider, base_url="http://localhost:8000", game_id="test-123", side="north")

        mock_api = MagicMock()
        game_state_resp = MagicMock()
        game_state_resp.json.return_value = {
            "status": "in_progress",
            "current_player": "south",
            "move_count": 5,
            "board": {},
        }
        game_state_resp.status_code = 200
        mock_api.get.return_value = game_state_resp
        agent._client = mock_api

        agent.play_turn()

        mock_provider.chat.assert_not_called()

    def test_play_turn_handles_terminal_state(self):
        mock_provider = MagicMock(spec=LLMProvider)
        agent = KomikanAgent(provider=mock_provider, base_url="http://localhost:8000", game_id="test-123")

        mock_api = MagicMock()
        game_state_resp = MagicMock()
        game_state_resp.json.return_value = {
            "status": "north_won",
            "current_player": "north",
            "move_count": 30,
            "board": {},
        }
        game_state_resp.status_code = 200
        mock_api.get.return_value = game_state_resp
        agent._client = mock_api

        result = agent.play_turn()
        assert result is not None
        assert result.get("status") == "north_won"

    def test_play_until_done_loops(self):
        mock_provider = MagicMock(spec=LLMProvider)
        mock_provider.chat.return_value = LLMResponse(
            tool_calls=[ToolCall(name="make_move", arguments={"from_x": 2, "from_y": 0, "to_x": 2, "to_y": 1})],
            text=None,
        )
        agent = KomikanAgent(provider=mock_provider, base_url="http://localhost:8000", game_id="test-123")

        call_count = 0

        def mock_get(url, **kwargs):
            nonlocal call_count
            resp = MagicMock()
            resp.status_code = 200
            if "all-valid-moves" in url:
                resp.json.return_value = {"tokens": [{"from": [2, 0], "moves": [[2, 1]], "captures": []}]}
            else:
                if call_count < 3:
                    resp.json.return_value = {
                        "status": "in_progress",
                        "current_player": "north",
                        "move_count": call_count,
                        "board": {},
                    }
                else:
                    resp.json.return_value = {
                        "status": "north_won",
                        "current_player": "north",
                        "move_count": call_count,
                        "board": {},
                    }
                call_count += 1
            return resp

        move_resp = MagicMock()
        move_resp.status_code = 200
        move_resp.json.return_value = {
            "status": "in_progress",
            "current_player": "south",
            "move_count": 1,
            "board": {},
        }

        mock_api = MagicMock()
        mock_api.get.side_effect = mock_get
        mock_api.post.return_value = move_resp
        agent._client = mock_api

        result = agent.play_until_done(max_turns=10)
        assert result is not None
