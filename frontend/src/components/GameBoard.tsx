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
    <div className="flex flex-col items-center gap-2 p-4 bg-gray-100 rounded-lg">
      {Array.from({ length: BOARD_HEIGHT }, (_, y) => (
        <div key={y} className="flex gap-2">
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
                  w-16 h-16 rounded-lg border-2 transition-all
                  ${disabled ? 'bg-gray-400 cursor-not-allowed opacity-50' : 'bg-white hover:bg-gray-50'}
                  ${selected ? 'ring-4 ring-blue-500 border-blue-600' : 'border-gray-300'}
                  ${validMove ? 'bg-green-100 border-green-500' : ''}
                  relative
                `}
              >
                {token && (
                  <div
                    className={`
                      w-12 h-12 rounded-full absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2
                      ${token.side === 'pangui' ? 'bg-red-500' : 'bg-blue-500'}
                      ${currentPlayer === token.side ? 'ring-2 ring-yellow-400' : ''}
                      flex items-center justify-center text-white font-bold
                    `}
                  >
                    {token.side === 'pangui' ? 'P' : 'D'}
                  </div>
                )}
                {validMove && !token && (
                  <div className="w-4 h-4 rounded-full bg-green-500 absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2" />
                )}
                <span className="absolute bottom-0 right-1 text-xs text-gray-500">
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
