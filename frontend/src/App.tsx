import { useState, useEffect } from 'react';
import { GameBoard } from './components/GameBoard';
import { GameStatus } from './components/GameStatus';
import { MoveHistory } from './components/MoveHistory';
import { ExampleGames } from './components/ExampleGames';
import { GameAPI } from './api';
import type { GameState, MoveRecord, TokenPosition, ExampleScenario } from './types/game';

const DISABLED_NODES: [number, number][] = [[0, 2], [4, 2]];

function App() {
  const [game, setGame] = useState<GameState | null>(null);
  const [moves, setMoves] = useState<MoveRecord[]>([]);
  const [selectedPosition, setSelectedPosition] = useState<TokenPosition | null>(null);
  const [validMoves, setValidMoves] = useState<TokenPosition[]>([]);
  const [captureDestinations, setCaptureDestinations] = useState<TokenPosition[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const clearSelection = () => {
    setSelectedPosition(null);
    setValidMoves([]);
    setCaptureDestinations([]);
  };

  const createNewGame = async () => {
    try {
      setLoading(true);
      setError(null);
      const newGame = await GameAPI.createGame();
      setGame(newGame);
      setMoves([]);
      clearSelection();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create game');
    } finally {
      setLoading(false);
    }
  };

  const loadExampleGame = async (scenario: ExampleScenario) => {
    try {
      setLoading(true);
      setError(null);
      const newGame = await GameAPI.createCustomGame({
        north_positions: scenario.northPositions.map(([x, y]) => ({ x, y })),
        south_positions: scenario.southPositions.map(([x, y]) => ({ x, y })),
        starting_player: scenario.startingPlayer,
      });
      setGame(newGame);
      setMoves([]);
      clearSelection();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load example game');
    } finally {
      setLoading(false);
    }
  };

  const getInvalidMoveReason = (x: number, y: number): string | null => {
    if (!game || !selectedPosition) return null;

    // Check if it's a disabled node
    if (DISABLED_NODES.some(([dx, dy]) => dx === x && dy === y)) {
      return 'That position is disabled and cannot be moved to.';
    }

    // Check if it's occupied by the opponent
    const opponentPositions =
      game.current_player === 'pangui'
        ? game.south_player.positions
        : game.north_player.positions;
    if (opponentPositions.some(([px, py]) => px === x && py === y)) {
      return "That position is occupied by the opponent's piece.";
    }

    // If it's a known valid move/capture, let the API handle it
    const allDestinations = [...validMoves, ...captureDestinations];
    if (allDestinations.some((m) => m.x === x && m.y === y)) {
      return null;
    }

    // Not in valid moves list - explain why
    const dx = Math.abs(x - selectedPosition.x);
    const dy = Math.abs(y - selectedPosition.y);
    const isAdjacent = dx <= 1 && dy <= 1 && (dx + dy > 0);

    if (!isAdjacent) {
      return `That position is not reachable from (${selectedPosition.x}, ${selectedPosition.y}). You can only move to adjacent nodes or capture by jumping over an opponent.`;
    }

    return `The path from (${selectedPosition.x}, ${selectedPosition.y}) to (${x}, ${y}) is blocked.`;
  };

  const handleNodeClick = async (x: number, y: number) => {
    if (!game || game.status !== 'active') return;

    try {
      setError(null);

      // Check if clicking on current player's token
      const currentPlayerPositions =
        game.current_player === 'pangui'
          ? game.north_player.positions
          : game.south_player.positions;

      const clickedOwnToken = currentPlayerPositions.find(
        ([px, py]) => px === x && py === y
      );

      if (clickedOwnToken) {
        // Select this token and get valid moves
        setSelectedPosition({ x, y });
        const validMovesData = await GameAPI.getValidMoves(game.game_id, x, y);
        setValidMoves(validMovesData.valid_moves);
        setCaptureDestinations(
          validMovesData.valid_captures.map(([dest]) => dest)
        );
      } else if (selectedPosition) {
        // Check client-side first for a better error message
        const reason = getInvalidMoveReason(x, y);
        if (reason) {
          setError(reason);
          return;
        }

        // Try to make the move via API
        try {
          const result = await GameAPI.makeMove(game.game_id, {
            from_x: selectedPosition.x,
            from_y: selectedPosition.y,
            to_x: x,
            to_y: y,
          });

          setGame(result.game);
          setMoves((prev) => [...prev, result.move]);
          clearSelection();
        } catch (err) {
          setError(err instanceof Error ? err.message : 'Invalid move');
        }
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    }
  };

  const importGame = async (data: { game: GameState; moves: MoveRecord[] }) => {
    try {
      setLoading(true);
      setError(null);
      const savedGame = data.game;
      const newGame = await GameAPI.createCustomGame({
        north_positions: savedGame.north_player.positions.map(([x, y]) => ({ x, y })),
        south_positions: savedGame.south_player.positions.map(([x, y]) => ({ x, y })),
        starting_player: savedGame.current_player,
      });
      setGame(newGame);
      setMoves(data.moves);
      clearSelection();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to import game');
    } finally {
      setLoading(false);
    }
  };

  const loadMoveHistory = async () => {
    if (!game) return;

    try {
      const history = await GameAPI.getMoveHistory(game.game_id);
      setMoves(history);
    } catch (err) {
      console.error('Failed to load move history:', err);
    }
  };

  useEffect(() => {
    createNewGame();
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-200 py-8">
      <div className="container mx-auto px-4">
        <header className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-800 mb-2">Komikan Game</h1>
          <p className="text-gray-600">Traditional Mapuche Board Game</p>
        </header>

        <div className="flex justify-center mb-6 gap-4">
          <button
            onClick={createNewGame}
            disabled={loading}
            className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 transition-colors font-semibold shadow-md"
          >
            {loading ? 'Creating...' : 'New Game'}
          </button>

          {game && (
            <button
              onClick={loadMoveHistory}
              className="px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors font-semibold shadow-md"
            >
              Refresh History
            </button>
          )}
        </div>

        {error && (
          <div className="max-w-2xl mx-auto mb-6 p-4 bg-red-100 border border-red-400 text-red-700 rounded-lg">
            <p className="font-semibold">Error:</p>
            <p>{error}</p>
          </div>
        )}

        {game && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2">
              <GameBoard
                northPlayer={game.north_player}
                southPlayer={game.south_player}
                selectedPosition={selectedPosition}
                validMoves={validMoves}
                captureDestinations={captureDestinations}
                onNodeClick={handleNodeClick}
                currentPlayer={game.current_player}
              />
            </div>

            <div className="space-y-6">
              <GameStatus game={game} />
              <ExampleGames onLoadScenario={loadExampleGame} loading={loading} />
              <MoveHistory moves={moves} game={game} onImportGame={importGame} />
            </div>
          </div>
        )}

        {!game && !loading && (
          <div className="text-center text-gray-500 mt-12">
            <p>Click "New Game" to start playing</p>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
