import React from 'react';
import type { PlayerState, TokenPosition } from '../types/game';

interface GameBoardProps {
  northPlayer: PlayerState;
  southPlayer: PlayerState;
  selectedPosition: TokenPosition | null;
  validMoves: TokenPosition[];
  onNodeClick: (x: number, y: number) => void;
  currentPlayer: 'pangui' | 'pu trewa';
}

const BOARD_WIDTH = 5;
const BOARD_HEIGHT = 8;
const DISABLED_NODES = [[0, 2], [4, 2]];

export const GameBoard: React.FC<GameBoardProps> = ({
  northPlayer,
  southPlayer,
  selectedPosition,
  validMoves,
  onNodeClick,
  currentPlayer,
}) => {
  const getTokenAtPosition = (x: number, y: number): PlayerState | null => {
    if (northPlayer.positions.some(([px, py]) => px === x && py === y)) {
      return northPlayer;
    }
    if (southPlayer.positions.some(([px, py]) => px === x && py === y)) {
      return southPlayer;
    }
    return null;
  };

  const isDisabledNode = (x: number, y: number): boolean => {
    return DISABLED_NODES.some(([dx, dy]) => dx === x && dy === y);
  };

  const isSelected = (x: number, y: number): boolean => {
    return selectedPosition !== null && selectedPosition.x === x && selectedPosition.y === y;
  };

  const isValidMove = (x: number, y: number): boolean => {
    return validMoves.some((move) => move.x === x && move.y === y);
  };

  return (
    <div className="flex flex-col items-center gap-3 p-8 bg-gradient-to-br from-gray-100 to-gray-200 rounded-xl shadow-lg">
      {Array.from({ length: BOARD_HEIGHT }, (_, y) => (
        <div key={y} className="flex gap-3">
          {Array.from({ length: BOARD_WIDTH }, (_, x) => {
            const token = getTokenAtPosition(x, y);
            const disabled = isDisabledNode(x, y);
            const selected = isSelected(x, y);
            const validMove = isValidMove(x, y);

            return (
              <button
                key={`${x}-${y}`}
                onClick={() => !disabled && onNodeClick(x, y)}
                disabled={disabled}
                className={`
                  w-24 h-24 rounded-xl border-3 transition-all shadow-md
                  ${disabled ? 'bg-gray-300 cursor-not-allowed opacity-40 border-gray-400' : 'bg-white hover:bg-gray-50 hover:shadow-lg border-gray-400'}
                  ${selected ? 'ring-4 ring-blue-500 border-blue-700 shadow-xl scale-105' : ''}
                  ${validMove ? 'bg-green-50 border-green-600 ring-2 ring-green-400' : ''}
                  relative
                `}
              >
                {token && (
                  <div
                    className={`
                      w-18 h-18 rounded-full absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2
                      ${token.side === 'pangui' ? 'bg-red-600 border-4 border-red-800' : 'bg-blue-600 border-4 border-blue-800'}
                      ${currentPlayer === token.side ? 'ring-4 ring-yellow-400 animate-pulse' : ''}
                      flex items-center justify-center text-white font-bold text-2xl shadow-lg
                    `}
                  >
                    {token.side === 'pangui' ? 'P' : 'D'}
                  </div>
                )}
                {validMove && !token && (
                  <div className="w-6 h-6 rounded-full bg-green-500 absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 animate-pulse shadow-md" />
                )}
                <span className="absolute bottom-1 right-2 text-xs text-gray-600 font-mono">
                  {x},{y}
                </span>
              </button>
            );
          })}
        </div>
      ))}
    </div>
  );
};
