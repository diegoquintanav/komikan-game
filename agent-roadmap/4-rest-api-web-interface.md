# Feature 4: REST API with FastAPI and React Web Interface

Modify the project so that the Komikan game can be interacted with through a REST API using FastAPI and a web interface that reflects the board state and tracks every movement.

## Requirements

### Backend (FastAPI)

1. Create a FastAPI application in `src/komikan/api/` that exposes the game logic via REST endpoints:
   - `POST /api/games` — Create a new game, returns game ID and initial state.
   - `GET /api/games/{game_id}` — Get current game state (board, positions, current player, move history).
   - `POST /api/games/{game_id}/moves` — Submit a move (from_x, from_y, to_x, to_y), returns updated state.
   - `GET /api/games/{game_id}/moves` — Get full move history for auditing/replay.
   - `GET /api/games/{game_id}/valid-moves` — Get valid moves for the current player's selected token.
   - `DELETE /api/games/{game_id}` — Delete/forfeit a game.

2. Game state management:
   - Support multiple concurrent games (in-memory store keyed by game ID).
   - Track every move with timestamps, player, from/to positions, success/failure, and capture details.
   - Detect and report win conditions (North captures enough tokens, South blocks North).
   - Handle edge cases: invalid moves, game-over state, out-of-turn moves.

3. Use Pydantic models for request/response schemas.

4. Add CORS middleware for local development.

### Frontend (React + Tailwind)

1. Create a React application in `frontend/` using Vite:
   - Board visualization showing the 5×8 grid with nodes, paths, and tokens.
   - Click-to-select and click-to-move interaction.
   - Visual indicators for: current player, selected token, valid moves, disabled nodes.
   - Move history panel showing all moves in chronological order.
   - Game status display (current player turn, win condition, token counts).

2. Follow React best practices from https://github.com/vercel-labs/agent-skills/tree/main/skills/react-best-practices:
   - Use functional components with hooks.
   - Proper state management.
   - Component composition and separation of concerns.
   - TypeScript for type safety.

3. Style with Tailwind CSS.

### Integration

- FastAPI serves the React build as static files in production.
- Development mode supports separate frontend/backend servers with proxy.
- Add scripts to `pyproject.toml` or a `Makefile` for running dev/prod modes.

## Border Cases and Endgame

- Validate all moves server-side; never trust the client.
- Handle game replay from move history (auditing).
- Detect stalemate (South player has no valid moves).
- Detect North player trapped (no valid moves or captures available).
- Prevent moves after game is over.
- Track game duration and per-move timing.

## Validation

- All existing tests must continue to pass.
- Add API tests using `pytest` with `httpx` for the FastAPI endpoints.
- Verify the web interface correctly reflects board state after each move.
- Test concurrent game sessions.
- Test full game replay from move history.
