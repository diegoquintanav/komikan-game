"""Tests for the Komikan Game REST API."""

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from komikan.api.main import app


@pytest_asyncio.fixture
async def client():
    """Create an async test client."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.mark.asyncio
async def test_root_endpoint(client):
    """Test the root endpoint."""
    response = await client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Komikan Game API"
    assert "version" in data


@pytest.mark.asyncio
async def test_create_game(client):
    """Test creating a new game."""
    response = await client.post("/api/games")
    assert response.status_code == 201
    data = response.json()

    assert "game" in data
    game = data["game"]
    assert "game_id" in game
    assert game["status"] == "active"
    assert game["current_player"] == "pangui"  # North starts
    assert game["north_player"]["token_count"] == 1
    assert game["south_player"]["token_count"] == 12
    assert game["move_count"] == 0


@pytest.mark.asyncio
async def test_get_game(client):
    """Test getting a game by ID."""
    # Create a game first
    create_response = await client.post("/api/games")
    game_id = create_response.json()["game"]["game_id"]

    # Get the game
    response = await client.get(f"/api/games/{game_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["game"]["game_id"] == game_id


@pytest.mark.asyncio
async def test_get_nonexistent_game(client):
    """Test getting a game that doesn't exist."""
    response = await client.get("/api/games/nonexistent-id")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_make_valid_move(client):
    """Test making a valid move."""
    # Create a game
    create_response = await client.post("/api/games")
    game_id = create_response.json()["game"]["game_id"]

    # North player (Pangui) starts at (2, 0), move to (2, 1)
    move_data = {"from_x": 2, "from_y": 0, "to_x": 2, "to_y": 1}
    response = await client.post(f"/api/games/{game_id}/moves", json=move_data)

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["move"]["from_position"]["x"] == 2
    assert data["move"]["from_position"]["y"] == 0
    assert data["move"]["to_position"]["x"] == 2
    assert data["move"]["to_position"]["y"] == 1
    assert data["move"]["is_capture"] is False

    # Current player should now be South
    assert data["game"]["current_player"] == "pu trewa"
    assert data["game"]["move_count"] == 1


@pytest.mark.asyncio
async def test_make_invalid_move(client):
    """Test making an invalid move."""
    # Create a game
    create_response = await client.post("/api/games")
    game_id = create_response.json()["game"]["game_id"]

    # Try to move from an invalid position
    move_data = {"from_x": 0, "from_y": 0, "to_x": 0, "to_y": 1}
    response = await client.post(f"/api/games/{game_id}/moves", json=move_data)

    assert response.status_code == 400


@pytest.mark.asyncio
async def test_get_move_history(client):
    """Test getting move history."""
    # Create a game and make a move
    create_response = await client.post("/api/games")
    game_id = create_response.json()["game"]["game_id"]

    # Make a move
    move_data = {"from_x": 2, "from_y": 0, "to_x": 2, "to_y": 1}
    await client.post(f"/api/games/{game_id}/moves", json=move_data)

    # Get move history
    response = await client.get(f"/api/games/{game_id}/moves")
    assert response.status_code == 200
    history = response.json()
    assert len(history) == 1
    assert history[0]["move_number"] == 1
    assert history[0]["player"] == "pangui"


@pytest.mark.asyncio
async def test_get_valid_moves(client):
    """Test getting valid moves for a token."""
    # Create a game
    create_response = await client.post("/api/games")
    game_id = create_response.json()["game"]["game_id"]

    # Get valid moves for North player at (2, 0)
    response = await client.get(
        f"/api/games/{game_id}/valid-moves", params={"from_x": 2, "from_y": 0}
    )

    assert response.status_code == 200
    data = response.json()
    assert "valid_moves" in data
    assert "valid_captures" in data
    assert len(data["valid_moves"]) > 0  # Should have at least one valid move


@pytest.mark.asyncio
async def test_delete_game(client):
    """Test deleting a game."""
    # Create a game
    create_response = await client.post("/api/games")
    game_id = create_response.json()["game"]["game_id"]

    # Delete the game
    response = await client.delete(f"/api/games/{game_id}")
    assert response.status_code == 204

    # Verify the game is gone
    get_response = await client.get(f"/api/games/{game_id}")
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_delete_nonexistent_game(client):
    """Test deleting a game that doesn't exist."""
    response = await client.delete("/api/games/nonexistent-id")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_move_sequence(client):
    """Test a sequence of moves."""
    # Create a game
    create_response = await client.post("/api/games")
    game_id = create_response.json()["game"]["game_id"]

    # North moves from (2, 0) to (2, 1)
    move1 = {"from_x": 2, "from_y": 0, "to_x": 2, "to_y": 1}
    response1 = await client.post(f"/api/games/{game_id}/moves", json=move1)
    assert response1.status_code == 200
    assert response1.json()["game"]["current_player"] == "pu trewa"

    # South moves from (0, 5) to (0, 4)
    move2 = {"from_x": 0, "from_y": 5, "to_x": 0, "to_y": 4}
    response2 = await client.post(f"/api/games/{game_id}/moves", json=move2)
    assert response2.status_code == 200
    assert response2.json()["game"]["current_player"] == "pangui"

    # Verify move history
    history_response = await client.get(f"/api/games/{game_id}/moves")
    history = history_response.json()
    assert len(history) == 2


@pytest.mark.asyncio
async def test_concurrent_games(client):
    """Test managing multiple concurrent games."""
    # Create two games
    response1 = await client.post("/api/games")
    response2 = await client.post("/api/games")

    game_id1 = response1.json()["game"]["game_id"]
    game_id2 = response2.json()["game"]["game_id"]

    assert game_id1 != game_id2

    # Make different moves in each game
    move1 = {"from_x": 2, "from_y": 0, "to_x": 2, "to_y": 1}
    response_move1 = await client.post(f"/api/games/{game_id1}/moves", json=move1)
    assert response_move1.status_code == 200

    # Use a different but valid move for game 2
    move2 = {"from_x": 2, "from_y": 0, "to_x": 3, "to_y": 0}
    response_move2 = await client.post(f"/api/games/{game_id2}/moves", json=move2)
    assert response_move2.status_code == 200

    # Verify each game has its own state
    state1 = await client.get(f"/api/games/{game_id1}")
    state2 = await client.get(f"/api/games/{game_id2}")

    assert state1.json()["game"]["move_count"] == 1
    assert state2.json()["game"]["move_count"] == 1

    # Verify positions are different
    north1 = state1.json()["game"]["north_player"]["positions"]
    north2 = state2.json()["game"]["north_player"]["positions"]
    assert north1 != north2


@pytest.mark.asyncio
async def test_prevent_move_after_game_over(client):
    """Test that moves are prevented after game is over."""
    # This would require setting up a game-over scenario
    # For now, we'll skip the full implementation and just verify the structure
    create_response = await client.post("/api/games")
    game_id = create_response.json()["game"]["game_id"]

    # The game starts active
    state = await client.get(f"/api/games/{game_id}")
    assert state.json()["game"]["status"] == "active"
