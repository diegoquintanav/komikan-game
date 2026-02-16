// API client for Komikan game backend

import type { GameState, MoveRequest, MoveRecord, ValidMovesResponse } from './types/game';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export class GameAPI {
  static async createGame(): Promise<GameState> {
    const response = await fetch(`${API_BASE_URL}/api/games`, {
      method: 'POST',
    });
    if (!response.ok) {
      throw new Error('Failed to create game');
    }
    const data = await response.json();
    return data.game;
  }

  static async getGame(gameId: string): Promise<GameState> {
    const response = await fetch(`${API_BASE_URL}/api/games/${gameId}`);
    if (!response.ok) {
      throw new Error('Failed to get game');
    }
    const data = await response.json();
    return data.game;
  }

  static async makeMove(gameId: string, move: MoveRequest): Promise<{ game: GameState; move: MoveRecord }> {
    const response = await fetch(`${API_BASE_URL}/api/games/${gameId}/moves`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(move),
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to make move');
    }
    return await response.json();
  }

  static async getMoveHistory(gameId: string): Promise<MoveRecord[]> {
    const response = await fetch(`${API_BASE_URL}/api/games/${gameId}/moves`);
    if (!response.ok) {
      throw new Error('Failed to get move history');
    }
    return await response.json();
  }

  static async getValidMoves(gameId: string, fromX: number, fromY: number): Promise<ValidMovesResponse> {
    const response = await fetch(
      `${API_BASE_URL}/api/games/${gameId}/valid-moves?from_x=${fromX}&from_y=${fromY}`
    );
    if (!response.ok) {
      throw new Error('Failed to get valid moves');
    }
    return await response.json();
  }

  static async deleteGame(gameId: string): Promise<void> {
    const response = await fetch(`${API_BASE_URL}/api/games/${gameId}`, {
      method: 'DELETE',
    });
    if (!response.ok) {
      throw new Error('Failed to delete game');
    }
  }
}
