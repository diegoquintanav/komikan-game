"""FastAPI application for Komikan game REST API."""

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from typing import List
import os

from komikan.api.game_manager import GameManager
from komikan.api.models import (
    GameResponse,
    MoveRequest,
    MoveResponse,
    ValidMovesResponse,
    TokenPosition,
    ErrorResponse,
    MoveRecord,
)

# Create FastAPI app
app = FastAPI(
    title="Komikan Game API",
    description="REST API for the traditional Mapuche board game Komikan",
    version="1.0.0",
)

# Add CORS middleware for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # Vite and common dev ports
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global game manager
game_manager = GameManager()


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Komikan Game API", "version": "1.0.0"}


@app.post("/api/games", response_model=GameResponse, status_code=status.HTTP_201_CREATED)
async def create_game():
    """Create a new game and return its initial state."""
    game = game_manager.create_game()
    return GameResponse(
        game=game.to_api_model(),
        message="Game created successfully",
    )


@app.get("/api/games/{game_id}", response_model=GameResponse)
async def get_game(game_id: str):
    """Get the current state of a game."""
    game = game_manager.get_game(game_id)
    if not game:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Game {game_id} not found",
        )
    return GameResponse(game=game.to_api_model())


@app.post("/api/games/{game_id}/moves", response_model=MoveResponse)
async def make_move(game_id: str, move: MoveRequest):
    """Submit a move for a game."""
    game = game_manager.get_game(game_id)
    if not game:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Game {game_id} not found",
        )

    # Check if game is over
    if game.status != "active":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Game is already over with status: {game.status}",
        )

    # Attempt the move
    success, move_record = game.make_move(
        move.from_x, move.from_y, move.to_x, move.to_y
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid move. Check that the token belongs to the current player and the move is legal.",
        )

    message = "Move executed successfully"
    if move_record.is_capture:
        message = "Capture executed successfully"
    if game.status != "active":
        message = f"Game over: {game.status}"

    return MoveResponse(
        success=True,
        game=game.to_api_model(),
        move=move_record,
        message=message,
    )


@app.get("/api/games/{game_id}/moves", response_model=List[MoveRecord])
async def get_move_history(game_id: str):
    """Get the full move history for a game."""
    game = game_manager.get_game(game_id)
    if not game:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Game {game_id} not found",
        )
    return game.move_history


@app.get("/api/games/{game_id}/valid-moves", response_model=ValidMovesResponse)
async def get_valid_moves(game_id: str, from_x: int, from_y: int):
    """Get all valid moves for a token at the given position."""
    game = game_manager.get_game(game_id)
    if not game:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Game {game_id} not found",
        )

    # Check if game is over
    if game.status != "active":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Game is already over with status: {game.status}",
        )

    valid_moves, valid_captures = game.get_valid_moves(from_x, from_y)

    return ValidMovesResponse(
        from_position=TokenPosition(x=from_x, y=from_y),
        valid_moves=valid_moves,
        valid_captures=valid_captures,
    )


@app.delete("/api/games/{game_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_game(game_id: str):
    """Delete/forfeit a game."""
    success = game_manager.delete_game(game_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Game {game_id} not found",
        )
    return None


# Serve React frontend in production
frontend_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "frontend", "dist")
if os.path.exists(frontend_path):
    app.mount("/assets", StaticFiles(directory=os.path.join(frontend_path, "assets")), name="assets")

    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        """Serve the React frontend."""
        file_path = os.path.join(frontend_path, full_path)
        if os.path.exists(file_path) and os.path.isfile(file_path):
            return FileResponse(file_path)
        # Fallback to index.html for client-side routing
        return FileResponse(os.path.join(frontend_path, "index.html"))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
