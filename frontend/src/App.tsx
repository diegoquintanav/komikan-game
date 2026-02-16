import { useState, useEffect } from 'react';
import { GameBoard } from './components/GameBoard';
import { GameStatus } from './components/GameStatus';
import { MoveHistory } from './components/MoveHistory';
import { GameAPI } from './api';
import type { GameState, MoveRecord, TokenPosition } from './types/game';

function App() {
  const [game, setGame] = useState<GameState | null>(null);
  const [moves, setMoves] = useState<MoveRecord[]>([]);
  const [selectedPosition, setSelectedPosition] = useState<TokenPosition | null>(null);
  const [validMoves, setValidMoves] = useState<TokenPosition[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const createNewGame = async () => {
    try {
      setLoading(true);
      setError(null);
      const newGame = await GameAPI.createGame();
      setGame(newGame);
      setMoves([]);
      setSelectedPosition(null);
      setValidMoves([]);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create game');
    } finally {
      setLoading(false);
    }
  };

  const handleNodeClick = async (x: number, y: number) => {
    if (!game || game.status !== 'active') return;

    try {
      setError(null);

      // Check if clicking on a token
      const currentPlayerPositions =
        game.current_player === 'pangui'
          ? game.north_player.positions
          : game.south_player.positions;

      const clickedToken = currentPlayerPositions.find(
        ([px, py]) => px === x && py === y
      );

      if (clickedToken) {
        // Select this token and get valid moves
        setSelectedPosition({ x, y });
        const validMovesData = await GameAPI.getValidMoves(game.game_id, x, y);
        setValidMoves(validMovesData.valid_moves);
      } else if (selectedPosition) {
        // Try to make a move
        try {
          const result = await GameAPI.makeMove(game.game_id, {
            from_x: selectedPosition.x,
            from_y: selectedPosition.y,
            to_x: x,
            to_y: y,
          });

          setGame(result.game);
          setMoves((prev) => [...prev, result.move]);
          setSelectedPosition(null);
          setValidMoves([]);
        } catch (err) {
          setError(err instanceof Error ? err.message : 'Invalid move');
          // Don't clear selection on invalid move
        }
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
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
                onNodeClick={handleNodeClick}
                currentPlayer={game.current_player}
              />
            </div>

            <div className="space-y-6">
              <GameStatus game={game} />
              <MoveHistory moves={moves} />
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
