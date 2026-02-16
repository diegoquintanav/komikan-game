import React, { useMemo } from 'react';
import type { PlayerState, TokenPosition } from '../types/game';

interface GameBoardProps {
  northPlayer: PlayerState;
  southPlayer: PlayerState;
  selectedPosition: TokenPosition | null;
  validMoves: TokenPosition[];
  captureDestinations: TokenPosition[];
  onNodeClick: (x: number, y: number) => void;
  currentPlayer: 'pangui' | 'pu trewa';
}

const BOARD_WIDTH = 5;
const BOARD_HEIGHT = 8;
const DISABLED_NODES: [number, number][] = [[0, 2], [4, 2]];

// Layout constants for SVG coordinate system
const NODE_SPACING = 90;
const MARGIN = 50;
const SVG_WIDTH = MARGIN + (BOARD_WIDTH - 1) * NODE_SPACING + MARGIN;
const SVG_HEIGHT = MARGIN + (BOARD_HEIGHT - 1) * NODE_SPACING + MARGIN;
const NODE_RADIUS = 8;
const TOKEN_RADIUS = 20;
const HIT_RADIUS = 28; // invisible click target

// Disabled paths from backend board.py
const DISABLED_PATHS = new Set<string>([
  // Triangle paths
  '1,2-1,3', '2,2-1,3', '1,2-0,3', '3,2-3,3', '2,2-3,3', '3,2-4,3',
  '0,2-0,1', '0,2-1,1', '0,2-1,2', '0,2-1,3', '0,2-0,3',
  '4,2-4,1', '4,2-3,1', '4,2-3,2', '4,2-3,3', '4,2-4,3',
  '0,0-1,1', '1,1-2,2', '1,0-0,1', '1,0-2,1', '2,0-1,1', '2,0-3,1', '3,0-2,1', '3,0-4,1', '4,0-3,1',
  '1,2-2,1', '2,2-1,1', '2,2-3,1', '3,2-2,1',
  // Positive diagonals
  '1,3-2,4', '2,4-3,5', '3,5-4,6', '3,3-4,4', '0,4-1,5', '1,5-2,6', '2,6-3,7', '0,6-1,7',
  // Negative diagonals
  '1,3-0,4', '3,3-2,4', '2,4-1,5', '1,5-0,6', '4,4-3,5', '3,5-2,6', '2,6-1,7', '4,6-3,7',
]);

const isPathDisabled = (x1: number, y1: number, x2: number, y2: number): boolean => {
  return DISABLED_PATHS.has(`${x1},${y1}-${x2},${y2}`) || DISABLED_PATHS.has(`${x2},${y2}-${x1},${y1}`);
};

const isDisabledNode = (x: number, y: number): boolean => {
  return DISABLED_NODES.some(([dx, dy]) => dx === x && dy === y);
};

const nodeX = (x: number) => MARGIN + x * NODE_SPACING;
const nodeY = (y: number) => MARGIN + y * NODE_SPACING;

const DIRECTIONS = [
  [0, -1], [1, -1], [1, 0], [1, 1], [0, 1], [-1, 1], [-1, 0], [-1, -1],
] as const;

// Pre-compute all valid edges once
const computeEdges = (): Array<{ x1: number; y1: number; x2: number; y2: number; key: string }> => {
  const edges: Array<{ x1: number; y1: number; x2: number; y2: number; key: string }> = [];
  for (let y = 0; y < BOARD_HEIGHT; y++) {
    for (let x = 0; x < BOARD_WIDTH; x++) {
      for (const [dx, dy] of DIRECTIONS) {
        const nx = x + dx;
        const ny = y + dy;
        if (nx >= 0 && nx < BOARD_WIDTH && ny >= 0 && ny < BOARD_HEIGHT) {
          // Only emit each edge once (avoid duplicates)
          if (nx > x || (nx === x && ny > y)) {
            if (!isPathDisabled(x, y, nx, ny)) {
              edges.push({
                x1: nodeX(x), y1: nodeY(y),
                x2: nodeX(nx), y2: nodeY(ny),
                key: `${x},${y}-${nx},${ny}`,
              });
            }
          }
        }
      }
    }
  }
  return edges;
};

const EDGES = computeEdges();

export const GameBoard: React.FC<GameBoardProps> = ({
  northPlayer,
  southPlayer,
  selectedPosition,
  validMoves,
  captureDestinations,
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

  const isSelected = (x: number, y: number): boolean => {
    return selectedPosition !== null && selectedPosition.x === x && selectedPosition.y === y;
  };

  const isValidMoveAt = (x: number, y: number): boolean => {
    return validMoves.some((m) => m.x === x && m.y === y);
  };

  const isCaptureAt = (x: number, y: number): boolean => {
    return captureDestinations.some((m) => m.x === x && m.y === y);
  };

  const nodes = useMemo(() => {
    const result: Array<{ x: number; y: number; cx: number; cy: number; disabled: boolean }> = [];
    for (let y = 0; y < BOARD_HEIGHT; y++) {
      for (let x = 0; x < BOARD_WIDTH; x++) {
        result.push({ x, y, cx: nodeX(x), cy: nodeY(y), disabled: isDisabledNode(x, y) });
      }
    }
    return result;
  }, []);

  return (
    <div className="flex justify-center">
      <svg
        viewBox={`0 0 ${SVG_WIDTH} ${SVG_HEIGHT}`}
        width={SVG_WIDTH}
        height={SVG_HEIGHT}
        className="select-none"
        style={{ maxWidth: '100%', height: 'auto' }}
      >
        {/* Background */}
        <rect x="0" y="0" width={SVG_WIDTH} height={SVG_HEIGHT} rx="16" fill="#f1f5f9" stroke="#cbd5e1" strokeWidth="2" />

        {/* Column labels */}
        {Array.from({ length: BOARD_WIDTH }, (_, x) => (
          <text
            key={`col-${x}`}
            x={nodeX(x)}
            y={20}
            textAnchor="middle"
            fill="#475569"
            fontSize="16"
            fontWeight="600"
            fontFamily="monospace"
          >
            {x}
          </text>
        ))}

        {/* Row labels */}
        {Array.from({ length: BOARD_HEIGHT }, (_, y) => (
          <text
            key={`row-${y}`}
            x={16}
            y={nodeY(y) + 5}
            textAnchor="middle"
            fill="#475569"
            fontSize="16"
            fontWeight="600"
            fontFamily="monospace"
          >
            {y}
          </text>
        ))}

        {/* Edges */}
        {EDGES.map((e) => (
          <line
            key={e.key}
            x1={e.x1} y1={e.y1}
            x2={e.x2} y2={e.y2}
            stroke="#94a3b8"
            strokeWidth="1.5"
          />
        ))}

        {/* Nodes and tokens */}
        {nodes.map(({ x, y, cx, cy, disabled }) => {
          const token = getTokenAtPosition(x, y);
          const selected = isSelected(x, y);
          const validMove = isValidMoveAt(x, y);
          const capture = isCaptureAt(x, y);

          // Determine node fill/stroke based on state
          let nodeFill = '#fff';
          let nodeStroke = '#64748b';
          if (capture) {
            nodeFill = '#fed7aa'; // orange-200
            nodeStroke = '#ea580c'; // orange-600
          } else if (validMove) {
            nodeFill = '#d1fae5'; // emerald-100
            nodeStroke = '#059669'; // emerald-600
          }

          return (
            <g key={`node-${x}-${y}`}>
              {/* Base node dot */}
              {!disabled && (
                <circle
                  cx={cx} cy={cy} r={NODE_RADIUS}
                  fill={nodeFill}
                  stroke={nodeStroke}
                  strokeWidth="2"
                />
              )}

              {/* Disabled node X marker */}
              {disabled && (
                <>
                  <line x1={cx - 6} y1={cy - 6} x2={cx + 6} y2={cy + 6} stroke="#94a3b8" strokeWidth="2" />
                  <line x1={cx + 6} y1={cy - 6} x2={cx - 6} y2={cy + 6} stroke="#94a3b8" strokeWidth="2" />
                </>
              )}

              {/* Selected highlight ring */}
              {selected && (
                <circle
                  cx={cx} cy={cy} r={TOKEN_RADIUS + 6}
                  fill="none"
                  stroke="#3b82f6"
                  strokeWidth="3"
                  strokeDasharray="6 3"
                >
                  <animateTransform
                    attributeName="transform"
                    type="rotate"
                    from={`0 ${cx} ${cy}`}
                    to={`360 ${cx} ${cy}`}
                    dur="3s"
                    repeatCount="indefinite"
                  />
                </circle>
              )}

              {/* Valid move indicator (pulsing ring for empty targets) */}
              {validMove && !token && (
                <circle cx={cx} cy={cy} r={NODE_RADIUS + 4} fill="none" stroke="#10b981" strokeWidth="2">
                  <animate attributeName="opacity" values="1;0.3;1" dur="1.5s" repeatCount="indefinite" />
                </circle>
              )}

              {/* Capture destination indicator (pulsing orange ring) */}
              {capture && !token && (
                <circle cx={cx} cy={cy} r={NODE_RADIUS + 4} fill="none" stroke="#ea580c" strokeWidth="2">
                  <animate attributeName="opacity" values="1;0.3;1" dur="1.5s" repeatCount="indefinite" />
                </circle>
              )}

              {/* Token (player piece) */}
              {token && (() => {
                const isActive = currentPlayer === token.side;
                const fill = token.side === 'pangui'
                  ? (isActive ? '#dc2626' : '#fca5a5') // red-600 / red-300
                  : (isActive ? '#2563eb' : '#93c5fd'); // blue-600 / blue-300
                const stroke = token.side === 'pangui'
                  ? (isActive ? '#991b1b' : '#fca5a5') // red-900 / red-300
                  : (isActive ? '#1e3a8a' : '#93c5fd'); // blue-900 / blue-300
                const textFill = isActive ? '#fff' : '#f8fafc'; // white / slate-50

                return (
                  <>
                    <circle
                      cx={cx} cy={cy} r={TOKEN_RADIUS}
                      fill={fill}
                      stroke={stroke}
                      strokeWidth="3"
                      opacity={isActive ? 1 : 0.5}
                    />
                    {/* Current player glow */}
                    {isActive && (
                      <circle cx={cx} cy={cy} r={TOKEN_RADIUS + 3} fill="none" stroke="#facc15" strokeWidth="2">
                        <animate attributeName="opacity" values="1;0.4;1" dur="1s" repeatCount="indefinite" />
                      </circle>
                    )}
                    {/* Token label */}
                    <text
                      x={cx} y={cy + 6}
                      textAnchor="middle"
                      fill={textFill}
                      fontSize="18"
                      fontWeight="bold"
                      fontFamily="sans-serif"
                      opacity={isActive ? 1 : 0.5}
                      style={{ pointerEvents: 'none' }}
                    >
                      {token.side === 'pangui' ? 'P' : 'D'}
                    </text>
                  </>
                );
              })()}

              {/* Invisible click target (larger than visible node) */}
              {!disabled && (
                <circle
                  cx={cx} cy={cy} r={HIT_RADIUS}
                  fill="transparent"
                  cursor="pointer"
                  onClick={() => onNodeClick(x, y)}
                />
              )}
            </g>
          );
        })}
      </svg>
    </div>
  );
};
