// Game types matching backend API models

export type PlayerSide = 'pangui' | 'pu trewa';

export type GameStatus = 'active' | 'north_won' | 'south_won' | 'stalemate';

export interface TokenPosition {
  x: number;
  y: number;
}

export interface PlayerState {
  side: PlayerSide;
  positions: [number, number][];
  token_count: number;
}

export interface GameState {
  game_id: string;
  status: GameStatus;
  current_player: PlayerSide;
  north_player: PlayerState;
  south_player: PlayerState;
  move_count: number;
  created_at: string;
  last_move_at: string | null;
}

export interface MoveRecord {
  move_number: number;
  player: PlayerSide;
  from_position: TokenPosition;
  to_position: TokenPosition;
  timestamp: string;
  success: boolean;
  is_capture: boolean;
  captured_position: TokenPosition | null;
  duration_ms: number | null;
}

export interface MoveRequest {
  from_x: number;
  from_y: number;
  to_x: number;
  to_y: number;
}

export interface ValidMovesResponse {
  from_position: TokenPosition;
  valid_moves: TokenPosition[];
  valid_captures: [TokenPosition, TokenPosition][];
}
