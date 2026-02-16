import React from 'react';
import type { GameState } from '../types/game';

interface GameStatusProps {
  game: GameState | null;
}

export const GameStatus: React.FC<GameStatusProps> = ({ game }) => {
  if (!game) {
    return (
      <div className="bg-gray-100 p-4 rounded-lg">
        <p className="text-gray-500">No game loaded</p>
      </div>
    );
  }

  const getStatusMessage = () => {
    switch (game.status) {
      case 'north_won':
        return '🏆 Pangui (North) wins!';
      case 'south_won':
        return '🏆 Pu Trewa (South) wins!';
      case 'stalemate':
        return '🤝 Stalemate!';
      default:
        return `Current turn: ${game.current_player === 'pangui' ? 'Pangui (North)' : 'Pu Trewa (South)'}`;
    }
  };

  const getStatusColor = () => {
    switch (game.status) {
      case 'north_won':
        return 'bg-red-100 text-red-800';
      case 'south_won':
        return 'bg-blue-100 text-blue-800';
      case 'stalemate':
        return 'bg-gray-100 text-gray-800';
      default:
        return game.current_player === 'pangui' ? 'bg-red-50 text-red-700' : 'bg-blue-50 text-blue-700';
    }
  };

  return (
    <div className="bg-white p-6 rounded-lg shadow-md space-y-4">
      <h2 className="text-2xl font-bold text-gray-800">Game Status</h2>

      <div className={`p-4 rounded-lg ${getStatusColor()}`}>
        <p className="text-lg font-semibold">{getStatusMessage()}</p>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div className="bg-red-50 p-3 rounded">
          <p className="text-sm text-gray-600">Pangui (North)</p>
          <p className="text-2xl font-bold text-red-600">{game.north_player.token_count}</p>
          <p className="text-xs text-gray-500">tokens</p>
        </div>

        <div className="bg-blue-50 p-3 rounded">
          <p className="text-sm text-gray-600">Pu Trewa (South)</p>
          <p className="text-2xl font-bold text-blue-600">{game.south_player.token_count}</p>
          <p className="text-xs text-gray-500">tokens</p>
        </div>
      </div>

      <div className="pt-2 border-t">
        <p className="text-sm text-gray-600">
          <span className="font-semibold">Moves:</span> {game.move_count}
        </p>
        <p className="text-sm text-gray-600">
          <span className="font-semibold">Game ID:</span>{' '}
          <span className="font-mono text-xs">{game.game_id.slice(0, 8)}...</span>
        </p>
      </div>
    </div>
  );
};
