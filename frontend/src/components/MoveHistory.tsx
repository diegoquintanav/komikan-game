import React from 'react';
import type { MoveRecord } from '../types/game';

interface MoveHistoryProps {
  moves: MoveRecord[];
}

export const MoveHistory: React.FC<MoveHistoryProps> = ({ moves }) => {
  return (
    <div className="bg-white p-6 rounded-lg shadow-md">
      <h2 className="text-2xl font-bold text-gray-800 mb-4">Move History</h2>

      {moves.length === 0 ? (
        <p className="text-gray-500 italic">No moves yet</p>
      ) : (
        <div className="max-h-96 overflow-y-auto space-y-2">
          {moves.map((move) => (
            <div
              key={move.move_number}
              className={`p-3 rounded-lg ${
                move.player === 'pangui' ? 'bg-red-50' : 'bg-blue-50'
              }`}
            >
              <div className="flex justify-between items-start">
                <div>
                  <span className="font-bold text-gray-700">
                    #{move.move_number}
                  </span>
                  <span className="ml-2 text-sm text-gray-600">
                    {move.player === 'pangui' ? 'Pangui' : 'Pu Trewa'}
                  </span>
                </div>
                <span className="text-xs text-gray-500">
                  {new Date(move.timestamp).toLocaleTimeString()}
                </span>
              </div>

              <div className="mt-1 text-sm">
                <span className="font-mono text-gray-700">
                  ({move.from_position.x}, {move.from_position.y})
                </span>
                <span className="mx-2">→</span>
                <span className="font-mono text-gray-700">
                  ({move.to_position.x}, {move.to_position.y})
                </span>

                {move.is_capture && (
                  <span className="ml-2 px-2 py-0.5 bg-orange-200 text-orange-800 rounded text-xs font-semibold">
                    CAPTURE
                  </span>
                )}
              </div>

              {move.duration_ms && (
                <div className="mt-1 text-xs text-gray-500">
                  {move.duration_ms.toFixed(2)}ms
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
