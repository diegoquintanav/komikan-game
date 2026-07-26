"""Random opponent that plays via the REST API."""

from __future__ import annotations

import random
from typing import Protocol, runtime_checkable

import httpx


@runtime_checkable
class Opponent(Protocol):
    """Protocol for agent opponents."""

    def choose_move(self) -> dict[str, int]: ...


class RandomOpponent:
    """Picks a uniformly random legal move via the REST API."""

    def __init__(self, base_url: str, game_id: str) -> None:
        self._base_url = base_url.rstrip("/")
        self._game_id = game_id
        self._client: httpx.Client | None = None

    def _get_client(self) -> httpx.Client:
        if self._client is None:
            self._client = httpx.Client(base_url=self._base_url, timeout=10.0)
        return self._client

    def choose_move(self) -> dict[str, int]:
        """Fetch valid moves and pick one at random, then execute it."""
        client = self._get_client()

        resp = client.get(f"/api/games/{self._game_id}/all-valid-moves")
        resp.raise_for_status()
        data = resp.json()

        tokens = data["tokens"]
        all_moves: list[dict[str, int]] = []

        for token in tokens:
            from_x, from_y = token["from"]
            for m in token.get("moves", []):
                all_moves.append({"from_x": from_x, "from_y": from_y, "to_x": m[0], "to_y": m[1]})
            for capture in token.get("captures", []):
                to_pos = capture[0]
                all_moves.append({"from_x": from_x, "from_y": from_y, "to_x": to_pos[0], "to_y": to_pos[1]})

        move = random.choice(all_moves)

        move_resp = client.post(f"/api/games/{self._game_id}/moves", json=move)
        move_resp.raise_for_status()

        return move
