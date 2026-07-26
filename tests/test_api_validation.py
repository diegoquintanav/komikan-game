"""Tests for Komikan API validation — ALMUD-260.

Covers edge-case validation across every REST endpoint: custom game creation,
move submission, valid-moves query, and game deletion.
"""

import pytest
import pytest_asyncio
import uuid
from httpx import AsyncClient, ASGITransport
from komikan.api.main import app


@pytest_asyncio.fixture
async def client():
    """Create an async test client for the FastAPI app."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


async def _create_standard_game(client: AsyncClient) -> str:
    """Create a standard game and return its game_id."""
    resp = await client.post("/api/games")
    return resp.json()["game"]["game_id"]


async def _create_capture_scenario(client: AsyncClient) -> str:
    """Create a custom game set up for an immediate North capture.

    North at (2,0), South at (2,1) — North can jump over (2,1) to (2,2).
    Returns the game_id.
    """
    resp = await client.post(
        "/api/games/custom",
        json={
            "north_positions": [{"x": 2, "y": 0}],
            "south_positions": [{"x": 2, "y": 1}],
            "starting_player": "pangui",
        },
    )
    return resp.json()["game"]["game_id"]


async def _end_game_as_north_won(client: AsyncClient) -> str:
    """Create a capture-scenario game and execute the winning capture.

    Returns the game_id of a game with status 'north_won'.
    """
    game_id = await _create_capture_scenario(client)
    # North captures South at (2,1) by jumping to (2,2)
    await client.post(
        f"/api/games/{game_id}/moves",
        json={"from_x": 2, "from_y": 0, "to_x": 2, "to_y": 2},
    )
    return game_id


# ===================================================================
# TestCreateGameValidation
# ===================================================================


class TestCreateGameValidation:
    """Validation tests for POST /api/games/custom."""

    @pytest.mark.asyncio
    async def test_create_custom_game_disabled_node_position(self, client):
        """A position on a disabled node must be rejected with 400."""
        resp = await client.post(
            "/api/games/custom",
            json={
                "north_positions": [{"x": 0, "y": 2}],
                "south_positions": [{"x": 2, "y": 5}],
            },
        )
        assert resp.status_code == 400
        assert "disabled" in resp.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_create_custom_game_out_of_bounds_position(self, client):
        """A position outside the 5×8 grid must be rejected (Pydantic 422)."""
        resp = await client.post(
            "/api/games/custom",
            json={
                "north_positions": [{"x": 5, "y": 8}],
                "south_positions": [{"x": 2, "y": 5}],
            },
        )
        # Pydantic field constraints reject out-of-bounds values with 422
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_create_custom_game_overlapping_positions(self, client):
        """Two tokens on the same node must be rejected with 400."""
        resp = await client.post(
            "/api/games/custom",
            json={
                "north_positions": [{"x": 2, "y": 0}],
                "south_positions": [{"x": 2, "y": 0}],
            },
        )
        assert resp.status_code == 400
        assert "duplicate" in resp.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_create_custom_game_valid_setup(self, client):
        """A valid custom setup must return 201 with the correct state."""
        resp = await client.post(
            "/api/games/custom",
            json={
                "north_positions": [{"x": 2, "y": 0}],
                "south_positions": [{"x": 0, "y": 5}, {"x": 4, "y": 5}],
            },
        )
        assert resp.status_code == 201
        game = resp.json()["game"]
        assert game["status"] == "active"
        assert game["north_player"]["token_count"] == 1
        assert game["south_player"]["token_count"] == 2


# ===================================================================
# TestMoveEndpointValidation
# ===================================================================


class TestMoveEndpointValidation:
    """Validation tests for POST /api/games/{game_id}/moves."""

    @pytest.mark.asyncio
    async def test_move_with_invalid_game_id(self, client):
        """A move on a non-existent game must return 404."""
        fake_id = str(uuid.uuid4())
        resp = await client.post(
            f"/api/games/{fake_id}/moves",
            json={"from_x": 2, "from_y": 0, "to_x": 2, "to_y": 1},
        )
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_move_with_out_of_bounds_target(self, client):
        """A move with a target outside the board must be rejected (Pydantic 422)."""
        game_id = await _create_standard_game(client)
        resp = await client.post(
            f"/api/games/{game_id}/moves",
            json={"from_x": 2, "from_y": 0, "to_x": 2, "to_y": 9},
        )
        # to_y=9 exceeds Field(lt=8) → Pydantic returns 422
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_move_with_disabled_node_target(self, client):
        """Moving to a disabled node must return 400."""
        # Custom game: South starts adjacent to disabled node (0,2) and goes first
        resp = await client.post(
            "/api/games/custom",
            json={
                "north_positions": [{"x": 2, "y": 0}],
                "south_positions": [{"x": 0, "y": 1}],
                "starting_player": "pu trewa",
            },
        )
        game_id = resp.json()["game"]["game_id"]

        # South at (0,1) tries to move to disabled node (0,2)
        resp = await client.post(
            f"/api/games/{game_id}/moves",
            json={"from_x": 0, "from_y": 1, "to_x": 0, "to_y": 2},
        )
        assert resp.status_code == 400

    @pytest.mark.asyncio
    async def test_move_wrong_player_token(self, client):
        """Moving an opponent's token must return 400."""
        game_id = await _create_standard_game(client)
        # North's turn — try to move a South token at (0, 5)
        resp = await client.post(
            f"/api/games/{game_id}/moves",
            json={"from_x": 0, "from_y": 5, "to_x": 0, "to_y": 4},
        )
        assert resp.status_code == 400

    @pytest.mark.asyncio
    async def test_move_after_game_over(self, client):
        """Making a move after the game has ended must return 400."""
        game_id = await _end_game_as_north_won(client)

        # Verify game is actually over
        state = await client.get(f"/api/games/{game_id}")
        assert state.json()["game"]["status"] == "north_won"

        # Attempt another move
        resp = await client.post(
            f"/api/games/{game_id}/moves",
            json={"from_x": 2, "from_y": 2, "to_x": 2, "to_y": 3},
        )
        assert resp.status_code == 400
        assert "already over" in resp.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_move_history_after_move(self, client):
        """After a valid move, GET /moves must contain the recorded move."""
        game_id = await _create_standard_game(client)

        # Make a move
        await client.post(
            f"/api/games/{game_id}/moves",
            json={"from_x": 2, "from_y": 0, "to_x": 2, "to_y": 1},
        )

        resp = await client.get(f"/api/games/{game_id}/moves")
        assert resp.status_code == 200
        history = resp.json()
        assert len(history) == 1
        assert history[0]["move_number"] == 1
        assert history[0]["player"] == "pangui"
        assert history[0]["from_position"] == {"x": 2, "y": 0}
        assert history[0]["to_position"] == {"x": 2, "y": 1}
        assert history[0]["success"] is True

    @pytest.mark.asyncio
    async def test_move_history_empty_at_start(self, client):
        """GET /moves on a fresh game must return an empty list."""
        game_id = await _create_standard_game(client)
        resp = await client.get(f"/api/games/{game_id}/moves")
        assert resp.status_code == 200
        assert resp.json() == []


# ===================================================================
# TestValidMovesEndpoint
# ===================================================================


class TestValidMovesEndpoint:
    """Validation tests for GET /api/games/{game_id}/valid-moves."""

    @pytest.mark.asyncio
    async def test_valid_moves_for_north_at_start(self, client):
        """North at (2,0) must have legal moves at game start."""
        game_id = await _create_standard_game(client)
        resp = await client.get(
            f"/api/games/{game_id}/valid-moves",
            params={"from_x": 2, "from_y": 0},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["valid_moves"]) > 0
        # North at (2,0) has adjacent empty nodes reachable via non-disabled paths
        destinations = {(m["x"], m["y"]) for m in data["valid_moves"]}
        assert (2, 1) in destinations  # straight south is always available

    @pytest.mark.asyncio
    async def test_valid_moves_for_south_turn(self, client):
        """After North moves, valid-moves must reflect South's options."""
        game_id = await _create_standard_game(client)

        # North moves (2,0) → (2,1)
        await client.post(
            f"/api/games/{game_id}/moves",
            json={"from_x": 2, "from_y": 0, "to_x": 2, "to_y": 1},
        )

        # Query valid moves for South token at (0,5)
        resp = await client.get(
            f"/api/games/{game_id}/valid-moves",
            params={"from_x": 0, "from_y": 5},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["from_position"] == {"x": 0, "y": 5}
        # (0,5) is on the left edge — should have at least one move northward
        assert len(data["valid_moves"]) > 0

    @pytest.mark.asyncio
    async def test_valid_moves_includes_captures(self, client):
        """When a capture is available, valid_captures must list it."""
        game_id = await _create_capture_scenario(client)

        resp = await client.get(
            f"/api/games/{game_id}/valid-moves",
            params={"from_x": 2, "from_y": 0},
        )
        assert resp.status_code == 200
        data = resp.json()

        # North can jump over (2,1) to land on (2,2)
        assert len(data["valid_captures"]) > 0
        capture_targets = {(c[0]["x"], c[0]["y"]) for c in data["valid_captures"]}
        assert (2, 2) in capture_targets

    @pytest.mark.asyncio
    async def test_valid_moves_no_game(self, client):
        """Querying valid-moves for a non-existent game must return 404."""
        fake_id = str(uuid.uuid4())
        resp = await client.get(
            f"/api/games/{fake_id}/valid-moves",
            params={"from_x": 2, "from_y": 0},
        )
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_valid_moves_after_game_over(self, client):
        """Querying valid-moves after the game ends must return 400."""
        game_id = await _end_game_as_north_won(client)

        resp = await client.get(
            f"/api/games/{game_id}/valid-moves",
            params={"from_x": 2, "from_y": 2},
        )
        assert resp.status_code == 400
        assert "already over" in resp.json()["detail"].lower()


# ===================================================================
# TestDeleteGame
# ===================================================================


class TestDeleteGame:
    """Validation tests for DELETE /api/games/{game_id}."""

    @pytest.mark.asyncio
    async def test_delete_game_twice(self, client):
        """Deleting the same game twice must return 404 on the second call."""
        game_id = await _create_standard_game(client)

        resp1 = await client.delete(f"/api/games/{game_id}")
        assert resp1.status_code == 204

        resp2 = await client.delete(f"/api/games/{game_id}")
        assert resp2.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_does_not_affect_other_games(self, client):
        """Deleting one game must not affect other active games."""
        game_id_a = await _create_standard_game(client)
        game_id_b = await _create_standard_game(client)

        # Delete game A
        resp = await client.delete(f"/api/games/{game_id_a}")
        assert resp.status_code == 204

        # Game B must still be accessible
        resp = await client.get(f"/api/games/{game_id_b}")
        assert resp.status_code == 200
        assert resp.json()["game"]["game_id"] == game_id_b

        # Game A must be gone
        resp = await client.get(f"/api/games/{game_id_a}")
        assert resp.status_code == 404
