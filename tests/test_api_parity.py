"""Tests verifying API response shapes match frontend TypeScript types.

ALMUD-263: Frontend/backend parity — ensures every field the React frontend
reads from the API is actually present, correctly named, and typed as expected.

We cannot run the frontend in pytest, so we validate the JSON contract directly:
- POST /api/games          → GameResponse  → frontend reads .game as GameState
- GET  /api/games/:id      → GameResponse
- POST /api/games/:id/moves → MoveResponse
- GET  /api/games/:id/moves → List[MoveRecord]
- GET  /api/games/:id/valid-moves → ValidMovesResponse
"""

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from komikan.api.main import app


@pytest_asyncio.fixture
async def client():
    """Async test client using httpx + FastAPI ASGI transport."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


# ---------------------------------------------------------------------------
# TestApiResponseShapeParity
# ---------------------------------------------------------------------------


class TestApiResponseShapeParity:
    """Verify API responses contain every field the frontend expects."""

    @pytest.mark.asyncio
    async def test_create_game_response_shape(self, client):
        """POST /api/games returns a GameState wrapped in {game, message}.

        Frontend GameAPI.createGame() reads data.game — so the outer envelope
        must have 'game' and the inner GameState must match
        frontend/src/types/game.ts GameState interface.
        """
        resp = await client.post("/api/games")
        assert resp.status_code == 201
        data = resp.json()

        # Envelope
        assert "game" in data, "Response must wrap GameState in 'game' field"
        assert "message" in data, "Response must include 'message' field"

        game = data["game"]

        # All fields the frontend GameState type declares
        required_fields = {
            "game_id",
            "status",
            "current_player",
            "north_player",
            "south_player",
            "move_count",
            "created_at",
            "last_move_at",
        }
        missing = required_fields - game.keys()
        assert not missing, f"GameState missing fields the frontend expects: {missing}"

    @pytest.mark.asyncio
    async def test_game_state_player_shape(self, client):
        """north_player and south_player must have side, positions, token_count.

        Frontend PlayerState interface:
            side: PlayerSide;
            positions: [number, number][];
            token_count: number;
        """
        resp = await client.post("/api/games")
        game = resp.json()["game"]

        for key in ("north_player", "south_player"):
            player = game[key]
            assert isinstance(player, dict), f"{key} must be an object"

            required = {"side", "positions", "token_count"}
            missing = required - player.keys()
            assert not missing, f"{key} missing fields: {missing}"

            assert isinstance(player["positions"], list), (
                f"{key}.positions must be array"
            )
            assert isinstance(player["token_count"], int), (
                f"{key}.token_count must be int"
            )

    @pytest.mark.asyncio
    async def test_valid_moves_response_shape(self, client):
        """GET /valid-moves returns from_position, valid_moves, valid_captures.

        Frontend ValidMovesResponse:
            from_position: TokenPosition;
            valid_moves: TokenPosition[];
            valid_captures: [TokenPosition, TokenPosition][];
        """
        resp = await client.post("/api/games")
        game_id = resp.json()["game"]["game_id"]

        resp = await client.get(
            f"/api/games/{game_id}/valid-moves",
            params={"from_x": 2, "from_y": 0},
        )
        assert resp.status_code == 200
        data = resp.json()

        required = {"from_position", "valid_moves", "valid_captures"}
        missing = required - data.keys()
        assert not missing, f"ValidMovesResponse missing fields: {missing}"

        # from_position must be a TokenPosition {x, y}
        fp = data["from_position"]
        assert "x" in fp and "y" in fp, "from_position must be TokenPosition {x, y}"

        # valid_moves items must be TokenPosition
        for m in data["valid_moves"]:
            assert "x" in m and "y" in m, "Each valid_move must be TokenPosition {x, y}"

        # valid_captures items must be [TokenPosition, TokenPosition] tuples
        for c in data["valid_captures"]:
            assert isinstance(c, list) and len(c) == 2, (
                "Each valid_capture must be a 2-element array"
            )
            for tp in c:
                assert "x" in tp and "y" in tp, (
                    "Capture pair must be TokenPosition {x, y}"
                )

    @pytest.mark.asyncio
    async def test_move_history_response_shape(self, client):
        """GET /moves after a move returns MoveRecord[] with expected fields.

        Frontend MoveRecord:
            move_number, player, from_position, to_position,
            timestamp, success, is_capture, captured_position, duration_ms
        """
        resp = await client.post("/api/games")
        game_id = resp.json()["game"]["game_id"]

        # Make a valid move so history is non-empty
        await client.post(
            f"/api/games/{game_id}/moves",
            json={"from_x": 2, "from_y": 0, "to_x": 2, "to_y": 1},
        )

        resp = await client.get(f"/api/games/{game_id}/moves")
        assert resp.status_code == 200
        history = resp.json()

        assert isinstance(history, list), "Move history must be an array"
        assert len(history) >= 1, "History must contain at least the move we just made"

        required = {
            "move_number",
            "player",
            "from_position",
            "to_position",
            "timestamp",
            "success",
            "is_capture",
            "captured_position",
            "duration_ms",
        }
        for entry in history:
            missing = required - entry.keys()
            assert not missing, f"MoveRecord missing fields: {missing}"
            # TokenPosition sub-objects
            for key in ("from_position", "to_position"):
                tp = entry[key]
                assert "x" in tp and "y" in tp, f"{key} must be TokenPosition {{x, y}}"


# ---------------------------------------------------------------------------
# TestApiGameStatusValues
# ---------------------------------------------------------------------------


class TestApiGameStatusValues:
    """Verify enum values match what the frontend TypeScript types declare."""

    @pytest.mark.asyncio
    async def test_game_status_enum_values(self, client):
        """status must be one of 'active', 'north_won', 'south_won', 'stalemate'.

        Frontend: type GameStatus = 'active' | 'north_won' | 'south_won' | 'stalemate'
        """
        valid_statuses = {"active", "north_won", "south_won", "stalemate"}

        resp = await client.post("/api/games")
        status = resp.json()["game"]["status"]
        assert status in valid_statuses, f"Unexpected status: {status!r}"

    @pytest.mark.asyncio
    async def test_current_player_is_north_or_south(self, client):
        """current_player must be 'pangui' or 'pu trewa'.

        Frontend: type PlayerSide = 'pangui' | 'pu trewa'
        """
        valid_sides = {"pangui", "pu trewa"}

        resp = await client.post("/api/games")
        player = resp.json()["game"]["current_player"]
        assert player in valid_sides, f"Unexpected current_player: {player!r}"


# ---------------------------------------------------------------------------
# TestApiPositionFormat
# ---------------------------------------------------------------------------


class TestApiPositionFormat:
    """Verify position encoding matches frontend expectations."""

    @pytest.mark.asyncio
    async def test_positions_are_tuples(self, client):
        """Player positions must be arrays of [int, int] pairs.

        Frontend: positions: [number, number][]
        JSON serialises Python tuples as arrays.
        """
        resp = await client.post("/api/games")
        game = resp.json()["game"]

        for key in ("north_player", "south_player"):
            positions = game[key]["positions"]
            assert isinstance(positions, list), f"{key}.positions must be array"
            for pos in positions:
                assert isinstance(pos, list) and len(pos) == 2, (
                    f"Each position in {key} must be [x, y], got {pos!r}"
                )
                assert isinstance(pos[0], int) and isinstance(pos[1], int), (
                    f"Position coordinates must be integers, got {pos!r}"
                )

    @pytest.mark.asyncio
    async def test_move_request_position_format(self, client):
        """API accepts move requests with {from_x, from_y, to_x, to_y}.

        Frontend MoveRequest interface uses flat int fields, not nested objects.
        """
        resp = await client.post("/api/games")
        game_id = resp.json()["game"]["game_id"]

        move = {"from_x": 2, "from_y": 0, "to_x": 2, "to_y": 1}
        resp = await client.post(f"/api/games/{game_id}/moves", json=move)
        assert resp.status_code == 200, (
            f"API must accept MoveRequest format {{from_x, from_y, to_x, to_y}}, "
            f"got status {resp.status_code}: {resp.text}"
        )

        data = resp.json()
        assert data["success"] is True
        assert data["move"]["from_position"]["x"] == 2
        assert data["move"]["from_position"]["y"] == 0
        assert data["move"]["to_position"]["x"] == 2
        assert data["move"]["to_position"]["y"] == 1


# ---------------------------------------------------------------------------
# TestApiErrorResponses
# ---------------------------------------------------------------------------


class TestApiErrorResponses:
    """Verify error responses include 'detail' field (frontend reads this).

    Frontend GameAPI methods do: const error = await response.json();
    throw new Error(error.detail || 'Failed to ...');
    """

    @pytest.mark.asyncio
    async def test_404_returns_detail_field(self, client):
        """GET for a non-existent game returns 404 with 'detail' field."""
        resp = await client.get("/api/games/nonexistent-uuid-000")
        assert resp.status_code == 404
        data = resp.json()
        assert "detail" in data, "404 response must include 'detail' for frontend"
        assert isinstance(data["detail"], str), "detail must be a string"

    @pytest.mark.asyncio
    async def test_400_returns_detail_field(self, client):
        """Invalid move returns 400 with 'detail' field."""
        resp = await client.post("/api/games")
        game_id = resp.json()["game"]["game_id"]

        # Move from a position that has no token
        resp = await client.post(
            f"/api/games/{game_id}/moves",
            json={"from_x": 0, "from_y": 0, "to_x": 0, "to_y": 1},
        )
        assert resp.status_code == 400
        data = resp.json()
        assert "detail" in data, "400 response must include 'detail' for frontend"
        assert isinstance(data["detail"], str), "detail must be a string"


# ---------------------------------------------------------------------------
# TestCustomGameParity
# ---------------------------------------------------------------------------


class TestCustomGameParity:
    """Verify custom game endpoint returns the same shape as standard game."""

    @pytest.mark.asyncio
    async def test_custom_game_response_matches_standard(self, client):
        """POST /api/games/custom returns identical shape to POST /api/games.

        Both must produce a GameResponse with the same GameState fields.
        """
        standard = (await client.post("/api/games")).json()["game"]

        custom = (
            await client.post(
                "/api/games/custom",
                json={
                    "north_positions": [{"x": 2, "y": 0}],
                    "south_positions": [
                        {"x": 0, "y": 5},
                        {"x": 4, "y": 5},
                        {"x": 0, "y": 6},
                        {"x": 1, "y": 6},
                        {"x": 2, "y": 6},
                        {"x": 3, "y": 6},
                        {"x": 4, "y": 6},
                        {"x": 0, "y": 7},
                        {"x": 1, "y": 7},
                        {"x": 2, "y": 7},
                        {"x": 3, "y": 7},
                        {"x": 4, "y": 7},
                    ],
                    "starting_player": "pangui",
                },
            )
        ).json()["game"]

        # Same set of keys
        assert set(standard.keys()) == set(custom.keys()), (
            f"Custom game shape differs from standard. "
            f"Extra: {set(custom.keys()) - set(standard.keys())}, "
            f"Missing: {set(standard.keys()) - set(custom.keys())}"
        )

        # Same nested shapes
        for key in ("north_player", "south_player"):
            assert set(standard[key].keys()) == set(custom[key].keys()), (
                f"{key} shape differs between standard and custom game"
            )

    @pytest.mark.asyncio
    async def test_custom_game_preserves_positions(self, client):
        """Custom game with explicit positions returns those exact positions."""
        north_positions = [{"x": 2, "y": 0}]
        south_positions = [
            {"x": 0, "y": 5},
            {"x": 4, "y": 5},
            {"x": 0, "y": 6},
            {"x": 1, "y": 6},
            {"x": 2, "y": 6},
            {"x": 3, "y": 6},
            {"x": 4, "y": 6},
            {"x": 0, "y": 7},
            {"x": 1, "y": 7},
            {"x": 2, "y": 7},
            {"x": 3, "y": 7},
            {"x": 4, "y": 7},
        ]

        resp = await client.post(
            "/api/games/custom",
            json={
                "north_positions": north_positions,
                "south_positions": south_positions,
                "starting_player": "pangui",
            },
        )
        assert resp.status_code == 201
        game = resp.json()["game"]

        # Verify via GET to ensure persistence within the session
        get_resp = await client.get(f"/api/games/{game['game_id']}")
        fetched = get_resp.json()["game"]

        # North positions (single token at (2, 0))
        actual_north = sorted(fetched["north_player"]["positions"])
        expected_north = sorted([p["x"], p["y"]] for p in north_positions)
        assert actual_north == expected_north, (
            f"North positions mismatch: {actual_north} != {expected_north}"
        )

        # South positions (12 tokens)
        actual_south = sorted(fetched["south_player"]["positions"])
        expected_south = sorted([p["x"], p["y"]] for p in south_positions)
        assert actual_south == expected_south, (
            f"South positions mismatch: {actual_south} != {expected_south}"
        )
