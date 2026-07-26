"""LLM-powered Komikan agent that plays via the REST API."""

from __future__ import annotations

import logging
import random

import httpx

from komikan.agent.prompts import format_game_state_prompt, format_move_list
from komikan.agent.provider import KOMIKAN_TOOLS, LLMProvider, ToolCall

logger = logging.getLogger(__name__)

MAX_LLM_RETRIES = 3


class KomikanAgent:
    """Agent that reads game state, queries an LLM with tool definitions, and executes moves via the REST API."""

    def __init__(
        self,
        provider: LLMProvider,
        base_url: str,
        game_id: str = "",
        side: str = "north",
    ) -> None:
        self._provider = provider
        self._base_url = base_url.rstrip("/")
        self._game_id = game_id
        self.side = side
        self._client: httpx.Client | None = None

    def _get_client(self) -> httpx.Client:
        if self._client is None:
            self._client = httpx.Client(base_url=self._base_url, timeout=10.0)
        return self._client

    def _fetch_game_state(self) -> dict[str, object]:
        client = self._get_client()
        resp = client.get(f"/api/games/{self._game_id}")
        resp.raise_for_status()
        return resp.json()

    def _fetch_valid_moves(self) -> list[dict[str, object]]:
        client = self._get_client()
        resp = client.get(f"/api/games/{self._game_id}/all-valid-moves")
        resp.raise_for_status()
        return resp.json().get("tokens", [])

    def _execute_move(self, move: dict[str, int]) -> dict[str, object]:
        client = self._get_client()
        resp = client.post(f"/api/games/{self._game_id}/moves", json=move)
        resp.raise_for_status()
        return resp.json()

    def _is_valid_move(self, tool_call: ToolCall, valid_moves: list[dict[str, object]]) -> bool:
        args = tool_call.arguments
        from_x = args.get("from_x")
        from_y = args.get("from_y")
        to_x = args.get("to_x")
        to_y = args.get("to_y")

        if None in (from_x, from_y, to_x, to_y):
            return False

        for token in valid_moves:
            if token["from"] == [from_x, from_y]:
                if [to_x, to_y] in token.get("moves", []):
                    return True
                for capture in token.get("captures", []):
                    if capture[0] == [to_x, to_y]:
                        return True
        return False

    def play_turn(self) -> dict[str, object] | None:
        """Execute one turn for the agent's side. Returns the new game state or None if not agent's turn."""
        game_state = self._fetch_game_state()
        status = game_state.get("status", "")

        if status != "in_progress":
            return {"status": status}

        current_player = game_state.get("current_player", "")
        if current_player != self.side:
            return None

        valid_moves = self._fetch_valid_moves()

        if not valid_moves:
            return {"status": game_state.get("status")}

        prompt = format_game_state_prompt(game_state)
        move_list = format_move_list(valid_moves)
        user_prompt = f"{prompt}\n\n{move_list}\n\nChoose a move using the make_move tool."

        for attempt in range(MAX_LLM_RETRIES):
            response = self._provider.chat(
                system_prompt="You are a Komikan game agent. You play by selecting moves using the make_move tool. Always use the tool — do not respond with text.",
                user_prompt=user_prompt,
                tools=KOMIKAN_TOOLS,
            )

            if response.tool_calls:
                tool_call = response.tool_calls[0]
                if self._is_valid_move(tool_call, valid_moves):
                    move = {
                        "from_x": tool_call.arguments["from_x"],
                        "from_y": tool_call.arguments["from_y"],
                        "to_x": tool_call.arguments["to_x"],
                        "to_y": tool_call.arguments["to_y"],
                    }
                    result = self._execute_move(move)
                    return result.get("new_state", result)

                logger.warning("LLM returned invalid move (attempt %d/%d): %s", attempt + 1, MAX_LLM_RETRIES, tool_call.arguments)
                user_prompt += f"\n\nThe move {tool_call.arguments} is not valid. Here are the valid moves:\n{move_list}\n\nTry again."

        logger.warning("LLM failed %d times, falling back to random legal move", MAX_LLM_RETRIES)
        return self._play_random_move(valid_moves)

    def _play_random_move(self, valid_moves: list[dict[str, object]]) -> dict[str, object] | None:
        """Execute a random legal move as fallback."""
        all_moves: list[dict[str, int]] = []
        for token in valid_moves:
            from_x, from_y = token["from"]
            for m in token.get("moves", []):
                all_moves.append({"from_x": from_x, "from_y": from_y, "to_x": m[0], "to_y": m[1]})
            for capture in token.get("captures", []):
                to_pos = capture[0]
                all_moves.append({"from_x": from_x, "from_y": from_y, "to_x": to_pos[0], "to_y": to_pos[1]})

        if not all_moves:
            return None

        move = random.choice(all_moves)
        result = self._execute_move(move)
        return result.get("new_state", result)

    def play_until_done(self, max_turns: int = 200) -> str:
        """Run the agent's game loop until a terminal state or max turns."""
        for _ in range(max_turns):
            game_state = self._fetch_game_state()
            status = game_state.get("status", "")

            if status != "in_progress":
                return str(status)

            current_player = game_state.get("current_player", "")
            if current_player == self.side:
                self.play_turn()
            else:
                break

        game_state = self._fetch_game_state()
        return str(game_state.get("status", "unknown"))
