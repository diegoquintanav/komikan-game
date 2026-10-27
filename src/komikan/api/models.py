"""Pydantic models for API request/response schemas."""

from datetime import datetime
from enum import Enum
from typing import Optional, List, Tuple
from pydantic import BaseModel, Field


class PlayerSideModel(str, Enum):
    """Player side enumeration."""

    NORTH = "pangui"
    SOUTH = "pu trewa"


class TokenPosition(BaseModel):
    """Position of a token on the board."""

    x: int = Field(..., ge=0, lt=5, description="X coordinate (0-4)")
    y: int = Field(..., ge=0, lt=8, description="Y coordinate (0-7)")


class MoveRequest(BaseModel):
    """Request to make a move."""

    from_x: int = Field(..., ge=0, lt=5)
    from_y: int = Field(..., ge=0, lt=8)
    to_x: int = Field(..., ge=0, lt=5)
    to_y: int = Field(..., ge=0, lt=8)


class CustomGameRequest(BaseModel):
    """Request to create a game with custom starting positions."""

    north_positions: List[TokenPosition]
    south_positions: List[TokenPosition]
    starting_player: PlayerSideModel = PlayerSideModel.NORTH


class MoveRecord(BaseModel):
    """Record of a single move in the game."""

    move_number: int
    player: PlayerSideModel
    from_position: TokenPosition
    to_position: TokenPosition
    timestamp: datetime
    success: bool
    is_capture: bool = False
    captured_position: Optional[TokenPosition] = None
    duration_ms: Optional[float] = None


class PlayerState(BaseModel):
    """State of a player."""

    side: PlayerSideModel
    positions: List[Tuple[int, int]]
    token_count: int


class GameStatus(str, Enum):
    """Game status."""

    ACTIVE = "active"
    NORTH_WON = "north_won"
    SOUTH_WON = "south_won"
    STALEMATE = "stalemate"


class GameState(BaseModel):
    """Current state of the game."""

    game_id: str
    status: GameStatus
    current_player: PlayerSideModel
    north_player: PlayerState
    south_player: PlayerState
    move_count: int
    created_at: datetime
    last_move_at: Optional[datetime] = None


class GameResponse(BaseModel):
    """Response when creating or getting a game."""

    game: GameState
    message: str = "Game state retrieved successfully"


class MoveResponse(BaseModel):
    """Response after making a move."""

    success: bool
    game: GameState
    move: MoveRecord
    message: str


class ValidMovesResponse(BaseModel):
    """Response with valid moves for a token."""

    from_position: TokenPosition
    valid_moves: List[TokenPosition]
    valid_captures: List[Tuple[TokenPosition, TokenPosition]]  # (to, captured)


class MoveData(BaseModel):
    """A single move option for a token."""

    type: str = Field(..., description="Move type: 'advance' or 'capture'")
    to: List[int] = Field(..., description="Target position [column, row]")
    description: str = Field(..., description="Human-readable move description")
    captures_from: Optional[List[List[int]]] = Field(
        None, description="Path of captured positions (capture only)"
    )


class TokenMoves(BaseModel):
    """All available moves for a single token."""

    position: List[int] = Field(..., description="Token position [column, row]")
    moves: List[MoveData] = Field(..., description="Available moves")


class AllValidMovesResponse(BaseModel):
    """Response with all valid moves for every token of the current player."""

    current_player: str = Field(..., description="Current player side")
    tokens: List[TokenMoves] = Field(..., description="Moves per token")


class ErrorResponse(BaseModel):
    """Error response."""

    error: str
    detail: Optional[str] = None
