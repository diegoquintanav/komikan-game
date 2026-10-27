"""Game manager for handling multiple concurrent Komikan games."""

import uuid
from datetime import datetime
from typing import Dict, Optional, List, Tuple
from komikan.board import GameBoard
from komikan.player import Player, PlayerSide, GameState as CoreGameState
from komikan.api.models import (
    GameStatus,
    PlayerSideModel,
    MoveRecord,
    TokenPosition,
    PlayerState as PlayerStateModel,
    GameState as GameStateModel,
)


class GameInstance:
    """Represents a single game instance with full state and history."""

    def __init__(self, game_id: str, custom_positions: Optional[dict] = None):
        self.game_id = game_id
        self.board = GameBoard()
        self.core_state = CoreGameState()
        self.status = GameStatus.ACTIVE
        self.created_at = datetime.now()
        self.last_move_at: Optional[datetime] = None
        self.move_history: List[MoveRecord] = []
        if custom_positions:
            self._initialize_custom_game(custom_positions)
        else:
            self._initialize_game()

    def _initialize_game(self):
        """Initialize the game with starting positions."""
        # Place north player
        north_positions = self.core_state.player_north.get_starting_positions()
        for x, y in north_positions:
            self.board.place_player(self.core_state.player_north, x, y)
            self.core_state.player_north.positions.append((x, y))

        # Place south player
        south_positions = self.core_state.player_south.get_starting_positions()
        for x, y in south_positions:
            self.board.place_player(self.core_state.player_south, x, y)
            self.core_state.player_south.positions.append((x, y))

    def _initialize_custom_game(self, custom_positions: dict):
        """Initialize the game with custom positions and starting player."""
        for x, y in custom_positions["north"]:
            self.board.place_player(self.core_state.player_north, x, y)
            self.core_state.player_north.positions.append((x, y))

        for x, y in custom_positions["south"]:
            self.board.place_player(self.core_state.player_south, x, y)
            self.core_state.player_south.positions.append((x, y))

        if custom_positions.get("starting_player") == PlayerSide.SOUTH:
            self.core_state.current_player = self.core_state.player_south

    def get_current_player_side(self) -> PlayerSideModel:
        """Get the current player's side as API model."""
        return (
            PlayerSideModel.NORTH
            if self.core_state.current_player.side == PlayerSide.NORTH
            else PlayerSideModel.SOUTH
        )

    def _check_win_condition(self) -> GameStatus:
        """Check if the game has been won or is in stalemate."""
        # Check if South has too few tokens (North wins)
        south_token_count = len(self.core_state.player_south.positions)
        if south_token_count <= 4:  # North wins if South has 4 or fewer tokens
            return GameStatus.NORTH_WON

        # Check if North has no valid moves (South wins)
        if not self._has_valid_moves(self.core_state.player_north):
            return GameStatus.SOUTH_WON

        # Check if South has no valid moves (Stalemate)
        if (
            self.core_state.current_player == self.core_state.player_south
            and not self._has_valid_moves(self.core_state.player_south)
        ):
            return GameStatus.STALEMATE

        return GameStatus.ACTIVE

    def _has_valid_moves(self, player: Player) -> bool:
        """Check if a player has any valid moves or captures."""
        for x, y in player.positions:
            # Check for regular moves
            adjacent = self.board.get_adjacent_positions(x, y)
            for to_x, to_y in adjacent:
                if self.board.is_valid_move(x, y, to_x, to_y):
                    return True

            # Check for captures (only for North player)
            if player.side == PlayerSide.NORTH:
                # Check all 8 directions for 2-step jumps
                for dx in [-2, 0, 2]:
                    for dy in [-2, 0, 2]:
                        if dx == 0 and dy == 0:
                            continue
                        to_x, to_y = x + dx, y + dy
                        if self.board.is_valid_capture(x, y, to_x, to_y, player):
                            return True

        return False

    def make_move(
        self, from_x: int, from_y: int, to_x: int, to_y: int
    ) -> Tuple[bool, Optional[MoveRecord]]:
        """
        Execute a move and return success status and move record.
        Returns (success, move_record).
        """
        start_time = datetime.now()
        current_player = self.core_state.current_player
        move_number = len(self.move_history) + 1

        # Validate it's the current player's token
        if (from_x, from_y) not in current_player.positions:
            return False, None

        # Try capture first (only for North player)
        is_capture = False
        captured_pos = None

        if current_player.side == PlayerSide.NORTH:
            if self.board.is_valid_capture(from_x, from_y, to_x, to_y, current_player):
                success, captured_player = self.board.capture_move(
                    current_player, from_x, from_y, to_x, to_y
                )
                if success:
                    is_capture = True
                    # Calculate captured position
                    dx = to_x - from_x
                    dy = to_y - from_y
                    cap_x = from_x + dx // 2
                    cap_y = from_y + dy // 2
                    captured_pos = TokenPosition(x=cap_x, y=cap_y)

                    # Update positions
                    current_player.positions.remove((from_x, from_y))
                    current_player.positions.append((to_x, to_y))
                    captured_player.positions.remove((cap_x, cap_y))
                else:
                    return False, None
            else:
                # Try regular move
                success = self.board.move_player(
                    current_player, from_x, from_y, to_x, to_y
                )
                if success:
                    current_player.positions.remove((from_x, from_y))
                    current_player.positions.append((to_x, to_y))
                else:
                    return False, None
        else:
            # South player can only make regular moves
            success = self.board.move_player(current_player, from_x, from_y, to_x, to_y)
            if success:
                current_player.positions.remove((from_x, from_y))
                current_player.positions.append((to_x, to_y))
            else:
                return False, None

        # Create move record
        end_time = datetime.now()
        duration_ms = (end_time - start_time).total_seconds() * 1000

        move_record = MoveRecord(
            move_number=move_number,
            player=self.get_current_player_side(),
            from_position=TokenPosition(x=from_x, y=from_y),
            to_position=TokenPosition(x=to_x, y=to_y),
            timestamp=end_time,
            success=True,
            is_capture=is_capture,
            captured_position=captured_pos,
            duration_ms=duration_ms,
        )

        self.move_history.append(move_record)
        self.last_move_at = end_time

        # Switch turn
        self.core_state.switch_turn()

        # Check win condition
        self.status = self._check_win_condition()

        return True, move_record

    def get_valid_moves(
        self, from_x: int, from_y: int
    ) -> Tuple[List[TokenPosition], List[Tuple[TokenPosition, TokenPosition]]]:
        """
        Get all valid moves and captures for a token at the given position.
        Returns (valid_moves, valid_captures).
        """
        # Validate position belongs to current player
        if (from_x, from_y) not in self.core_state.current_player.positions:
            return [], []

        valid_moves = []
        valid_captures = []

        # Check regular moves
        adjacent = self.board.get_adjacent_positions(from_x, from_y)
        for to_x, to_y in adjacent:
            if self.board.is_valid_move(from_x, from_y, to_x, to_y):
                valid_moves.append(TokenPosition(x=to_x, y=to_y))

        # Check captures (only for North player)
        if self.core_state.current_player.side == PlayerSide.NORTH:
            for dx in [-2, 0, 2]:
                for dy in [-2, 0, 2]:
                    if dx == 0 and dy == 0:
                        continue
                    to_x, to_y = from_x + dx, from_y + dy
                    if self.board.is_valid_capture(
                        from_x, from_y, to_x, to_y, self.core_state.current_player
                    ):
                        # Calculate captured position
                        cap_x = from_x + dx // 2
                        cap_y = from_y + dy // 2
                        valid_captures.append(
                            (
                                TokenPosition(x=to_x, y=to_y),
                                TokenPosition(x=cap_x, y=cap_y),
                            )
                        )

        return valid_moves, valid_captures

    def get_all_valid_moves(self) -> dict:
        """
        Get all valid moves for every token of the current player.
        Returns a dict with current_player and tokens list.
        """
        current_side = self.core_state.current_player
        tokens = []

        for pos in current_side.positions:
            from_x, from_y = pos
            valid_moves, valid_captures = self.get_valid_moves(from_x, from_y)

            moves = []
            for move in valid_moves:
                moves.append(
                    {
                        "type": "advance",
                        "to": [move.x, move.y],
                        "description": f"Move from ({from_x},{from_y}) to ({move.x},{move.y})",
                    }
                )
            for to_pos, cap_pos in valid_captures:
                moves.append(
                    {
                        "type": "capture",
                        "to": [to_pos.x, to_pos.y],
                        "description": f"Capture from ({from_x},{from_y}) over ({cap_pos.x},{cap_pos.y}) to ({to_pos.x},{to_pos.y})",
                        "captures_from": [[cap_pos.x, cap_pos.y]],
                    }
                )

            tokens.append({"position": [from_x, from_y], "moves": moves})

        return {
            "current_player": self.get_current_player_side().value,
            "tokens": tokens,
        }

    def to_api_model(self) -> GameStateModel:
        """Convert game instance to API model."""
        return GameStateModel(
            game_id=self.game_id,
            status=self.status,
            current_player=self.get_current_player_side(),
            north_player=PlayerStateModel(
                side=PlayerSideModel.NORTH,
                positions=self.core_state.player_north.positions,
                token_count=len(self.core_state.player_north.positions),
            ),
            south_player=PlayerStateModel(
                side=PlayerSideModel.SOUTH,
                positions=self.core_state.player_south.positions,
                token_count=len(self.core_state.player_south.positions),
            ),
            move_count=len(self.move_history),
            created_at=self.created_at,
            last_move_at=self.last_move_at,
        )


class GameManager:
    """Manages multiple concurrent games."""

    def __init__(self):
        self.games: Dict[str, GameInstance] = {}

    def create_game(self) -> GameInstance:
        """Create a new game and return its instance."""
        game_id = str(uuid.uuid4())
        game = GameInstance(game_id)
        self.games[game_id] = game
        return game

    def create_custom_game(
        self,
        north_positions: List[Tuple[int, int]],
        south_positions: List[Tuple[int, int]],
        starting_player: str = "pangui",
    ) -> GameInstance:
        """Create a new game with custom starting positions."""
        game_id = str(uuid.uuid4())
        custom_positions = {
            "north": north_positions,
            "south": south_positions,
            "starting_player": PlayerSide.SOUTH
            if starting_player == "pu trewa"
            else PlayerSide.NORTH,
        }
        game = GameInstance(game_id, custom_positions=custom_positions)
        self.games[game_id] = game
        return game

    def get_game(self, game_id: str) -> Optional[GameInstance]:
        """Get a game by ID."""
        return self.games.get(game_id)

    def delete_game(self, game_id: str) -> bool:
        """Delete a game by ID."""
        if game_id in self.games:
            del self.games[game_id]
            return True
        return False

    def list_games(self) -> List[str]:
        """List all active game IDs."""
        return list(self.games.keys())
