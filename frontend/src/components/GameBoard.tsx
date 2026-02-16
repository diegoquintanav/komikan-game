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
    <div className="flex flex-col items-center gap-4 p-10 bg-gradient-to-br from-slate-100 to-slate-200 rounded-2xl shadow-2xl border-2 border-slate-300">
      {Array.from({ length: BOARD_HEIGHT }, (_, y) => (
        <div key={y} className="flex gap-4">
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
                  w-28 h-28 rounded-2xl border-4 transition-all duration-200 shadow-lg
                  ${disabled ? 'bg-slate-300 cursor-not-allowed opacity-40 border-slate-500' : 'bg-white hover:bg-slate-50 hover:shadow-xl hover:scale-105 border-slate-500'}
                  ${selected ? 'ring-6 ring-blue-500 border-blue-700 shadow-2xl scale-110' : ''}
                  ${validMove ? 'bg-emerald-50 border-emerald-600 ring-4 ring-emerald-400' : ''}
                  relative
                `}
              >
                {token && (
                  <div
                    className={`
                      w-20 h-20 rounded-full absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2
                      ${token.side === 'pangui' ? 'bg-red-600 border-4 border-red-900' : 'bg-blue-600 border-4 border-blue-900'}
                      ${currentPlayer === token.side ? 'ring-4 ring-yellow-400 animate-pulse' : ''}
                      flex items-center justify-center text-white font-bold text-3xl shadow-xl
                    `}
                  >
                    {token.side === 'pangui' ? 'P' : 'D'}
                  </div>
                )}
                {validMove && !token && (
                  <div className="w-8 h-8 rounded-full bg-emerald-500 absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 animate-pulse shadow-lg border-2 border-emerald-700" />
                )}
                <span className="absolute bottom-2 right-3 text-sm text-slate-600 font-mono font-semibold">
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
