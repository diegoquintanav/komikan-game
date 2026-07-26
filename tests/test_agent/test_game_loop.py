"""Tests for the agent game loop orchestrator."""

from unittest.mock import MagicMock
from komikan.agent.game_loop import agent_game_loop


def _make_game_state(status: str = "active", current_player: str = "north", **extra):
    """Build a mock game state dict-like object."""
    state = {
        "status": status,
        "current_player": current_player,
        "move_count": 0,
        "board": {},
    }
    state.update(extra)
    mock = MagicMock()
    mock.get = lambda key, default=None: state.get(key, default)
    mock.__getitem__ = lambda self, key: state[key]
    mock.__contains__ = lambda self, key: key in state
    mock.keys = state.keys
    mock.values = state.values
    mock.items = state.items
    mock.__str__ = lambda self: str(state)
    return mock, state


class TestAgentGameLoop:
    def test_import(self):
        assert agent_game_loop is not None

    def test_runs_until_terminal_state(self):
        mock_agent = MagicMock()
        mock_agent.side = "north"
        mock_opponent = MagicMock()

        call_count = 0

        def agent_play():
            nonlocal call_count
            call_count += 1
            if call_count >= 4:
                return {"status": "north_won"}
            return None

        mock_agent.play_turn.side_effect = agent_play
        mock_opponent.choose_move.return_value = {
            "from_x": 0,
            "from_y": 5,
            "to_x": 0,
            "to_y": 6,
        }

        def make_state(s):
            mock = MagicMock()
            mock.get = lambda key, default=None: s.get(key, default)
            mock.__getitem__ = lambda self, key: s[key]
            mock.__contains__ = lambda self, key: key in s
            mock.keys = s.keys
            return mock

        mock_agent._fetch_game_state.side_effect = [
            make_state({"status": "active", "current_player": "north"}),
            make_state({"status": "active", "current_player": "north"}),
            make_state({"status": "active", "current_player": "north"}),
            make_state({"status": "active", "current_player": "north"}),
        ]

        result = agent_game_loop(mock_agent, mock_opponent, max_turns=10)
        assert result is not None

    def test_agent_plays_first_when_north(self):
        mock_agent = MagicMock()
        mock_agent.side = "north"
        mock_agent.play_turn.return_value = None

        mock_opponent = MagicMock()
        mock_opponent.choose_move.return_value = {
            "from_x": 0,
            "from_y": 5,
            "to_x": 0,
            "to_y": 6,
        }

        call_order = []

        def track_agent():
            call_order.append("agent")
            return None

        def track_opponent():
            call_order.append("opponent")
            return {"from_x": 0, "from_y": 5, "to_x": 0, "to_y": 6}

        mock_agent.play_turn.side_effect = track_agent
        mock_opponent.choose_move.side_effect = track_opponent

        game_states = [
            {"status": "active", "current_player": "north"},
            {"status": "active", "current_player": "south"},
        ]

        def make_state(s):
            mock = MagicMock()
            mock.get = lambda key, default=None: s.get(key, default)
            mock.__getitem__ = lambda self, key: s[key]
            mock.__contains__ = lambda self, key: key in s
            mock.keys = s.keys
            return mock

        mock_agent._fetch_game_state.side_effect = [make_state(s) for s in game_states]

        agent_game_loop(mock_agent, mock_opponent, max_turns=2)
        assert call_order[0] == "agent"

    def test_respects_max_turns(self):
        mock_agent = MagicMock()
        mock_agent.play_turn.return_value = None

        mock_opponent = MagicMock()
        mock_opponent.choose_move.return_value = {
            "from_x": 0,
            "from_y": 5,
            "to_x": 0,
            "to_y": 6,
        }

        def make_state(s):
            mock = MagicMock()
            mock.get = lambda key, default=None: s.get(key, default)
            mock.__getitem__ = lambda self, key: s[key]
            mock.__contains__ = lambda self, key: key in s
            mock.keys = s.keys
            return mock

        mock_agent._fetch_game_state.side_effect = [
            make_state({"status": "active", "current_player": "north"}),
            make_state({"status": "active", "current_player": "north"}),
            make_state({"status": "active", "current_player": "north"}),
            make_state({"status": "active", "current_player": "north"}),
            make_state({"status": "active", "current_player": "north"}),
            make_state({"status": "active", "current_player": "north"}),
        ]

        agent_game_loop(mock_agent, mock_opponent, max_turns=3)

        assert mock_agent.play_turn.call_count <= 3

    def test_returns_terminal_status(self):
        mock_agent = MagicMock()
        mock_agent.side = "north"

        turn = 0

        def play():
            nonlocal turn
            turn += 1
            if turn >= 2:
                return {"status": "south_won"}
            return None

        mock_agent.play_turn.side_effect = play
        mock_opponent = MagicMock()
        mock_opponent.choose_move.return_value = {
            "from_x": 0,
            "from_y": 5,
            "to_x": 0,
            "to_y": 6,
        }

        def make_state(s):
            mock = MagicMock()
            mock.get = lambda key, default=None: s.get(key, default)
            mock.__getitem__ = lambda self, key: s[key]
            mock.__contains__ = lambda self, key: key in s
            mock.keys = s.keys
            return mock

        mock_agent._fetch_game_state.side_effect = [
            make_state({"status": "active", "current_player": "north"}),
            make_state({"status": "active", "current_player": "south"}),
            make_state({"status": "active", "current_player": "north"}),
        ]

        result = agent_game_loop(mock_agent, mock_opponent, max_turns=10)
        assert result == "south_won"

    def test_stops_on_stalemate(self):
        mock_agent = MagicMock()
        mock_agent.side = "north"
        mock_agent.play_turn.return_value = {"status": "stalemate"}

        mock_opponent = MagicMock()

        def make_state(s):
            mock = MagicMock()
            mock.get = lambda key, default=None: s.get(key, default)
            mock.__getitem__ = lambda self, key: s[key]
            mock.__contains__ = lambda self, key: key in s
            mock.keys = s.keys
            return mock

        mock_agent._fetch_game_state.side_effect = [
            make_state({"status": "active", "current_player": "north"}),
        ]

        result = agent_game_loop(mock_agent, mock_opponent, max_turns=10)
        assert result == "stalemate"
        mock_opponent.choose_move.assert_not_called()
