import React, { useRef, useEffect } from 'react';
import type { GameState, MoveRecord } from '../types/game';

interface MoveHistoryProps {
  moves: MoveRecord[];
  game: GameState | null;
  onImportGame: (data: { game: GameState; moves: MoveRecord[] }) => void;
}

const PLAYER_COLORS = {
  pangui: { bg: '#fee2e2', text: '#b91c1c', border: '#fecaca' },
  'pu trewa': { bg: '#dbeafe', text: '#1d4ed8', border: '#bfdbfe' },
  capture: { border: '#fdba74' },
} as const;

const getDirection = (
  fromX: number,
  fromY: number,
  toX: number,
  toY: number,
): string => {
  const dx = Math.sign(toX - fromX);
  const dy = Math.sign(toY - fromY);
  const map: Record<string, string> = {
    '0,-1': 'north',
    '1,-1': 'north-east',
    '1,0': 'east',
    '1,1': 'south-east',
    '0,1': 'south',
    '-1,1': 'south-west',
    '-1,0': 'west',
    '-1,-1': 'north-west',
  };
  return map[`${dx},${dy}`] ?? '';
};

const getMoveEmoji = (move: MoveRecord): string => {
  if (move.is_capture) return '\u2694\uFE0F';

  const dx = Math.sign(move.to_position.x - move.from_position.x);
  const dy = Math.sign(move.to_position.y - move.from_position.y);
  const arrows: Record<string, string> = {
    '0,-1': '\u2B06\uFE0F',
    '1,-1': '\u2197\uFE0F',
    '1,0': '\u27A1\uFE0F',
    '1,1': '\u2198\uFE0F',
    '0,1': '\u2B07\uFE0F',
    '-1,1': '\u2199\uFE0F',
    '-1,0': '\u2B05\uFE0F',
    '-1,-1': '\u2196\uFE0F',
  };
  return arrows[`${dx},${dy}`] ?? '\u25CF';
};

const getMoveCommentary = (move: MoveRecord): string => {
  const dir = getDirection(
    move.from_position.x,
    move.from_position.y,
    move.to_position.x,
    move.to_position.y,
  );
  if (move.is_capture) {
    return `Captured ${dir}`;
  }
  return `Moved ${dir}`;
};

export const MoveHistory: React.FC<MoveHistoryProps> = ({ moves, game, onImportGame }) => {
  const scrollRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [moves.length]);

  const handleExport = () => {
    if (!game) return;
    const data = { game, moves };
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `komikan-${game.game_id.slice(0, 8)}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const handleImport = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (event) => {
      try {
        const data = JSON.parse(event.target?.result as string);
        if (!data.game || !data.moves) {
          alert('Invalid file format. Expected { game, moves }.');
          return;
        }
        onImportGame(data);
      } catch {
        alert('Failed to parse JSON file.');
      }
    };
    reader.readAsText(file);

    // Reset input so the same file can be re-imported
    e.target.value = '';
  };

  return (
    <div className="bg-white rounded-xl shadow-md p-4">
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-lg font-bold text-gray-800">Move Log</h3>
        <div className="flex gap-1">
          <button
            onClick={handleExport}
            disabled={!game || moves.length === 0}
            className="px-2 py-1 text-xs rounded border border-gray-200 text-gray-600 hover:bg-gray-50 disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
            title="Export game as JSON"
          >
            Export
          </button>
          <button
            onClick={() => fileInputRef.current?.click()}
            className="px-2 py-1 text-xs rounded border border-gray-200 text-gray-600 hover:bg-gray-50 transition-colors"
            title="Import game from JSON"
          >
            Import
          </button>
          <input
            ref={fileInputRef}
            type="file"
            accept=".json"
            onChange={handleImport}
            className="hidden"
          />
        </div>
      </div>

      {moves.length === 0 ? (
        <p className="text-sm text-gray-400 italic py-4 text-center">No moves yet</p>
      ) : (
        <div ref={scrollRef} className="max-h-72 overflow-y-auto space-y-2">
          {moves.map((move) => {
            const isNorth = move.player === 'pangui';
            const playerName = isNorth ? 'Pangui' : 'Pu Trewa';
            const colors = PLAYER_COLORS[move.player];
            const borderColor = move.is_capture
              ? PLAYER_COLORS.capture.border
              : colors.border;
            const commentary = getMoveCommentary(move);
            const emoji = getMoveEmoji(move);

            return (
              <div
                key={move.move_number}
                className="p-3 rounded-lg"
                style={{ border: `1px solid ${borderColor}` }}
              >
                <div className="flex items-center gap-2">
                  <span
                    className="px-2 py-0.5 rounded-full text-xs font-bold"
                    style={{ backgroundColor: colors.bg, color: colors.text }}
                  >
                    {playerName}
                  </span>
                  <span className="text-xs text-gray-400">#{move.move_number}</span>
                  {move.is_capture && (
                    <span
                      className="px-1.5 py-0.5 rounded text-xs font-bold"
                      style={{ backgroundColor: '#ffedd5', color: '#c2410c' }}
                    >
                      capture
                    </span>
                  )}
                </div>
                <div className="text-gray-600 text-xs mt-1">
                  {emoji} {commentary}
                </div>
                <div className="flex gap-3 mt-2 text-xs text-gray-400">
                  <span>
                    From: {move.from_position.x},{move.from_position.y}
                  </span>
                  <span>
                    To: {move.to_position.x},{move.to_position.y}
                  </span>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};
