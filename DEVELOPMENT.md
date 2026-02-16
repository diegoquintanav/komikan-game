# Komikan Game Development Guide

## Running the Application

### Development Mode (Separate Frontend/Backend)

1. **Start the Backend API:**
   ```bash
   python -m uvicorn komikan.api.main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Start the Frontend Dev Server:**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

3. **Access the Application:**
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

### Production Mode (Integrated)

1. **Build the Frontend:**
   ```bash
   cd frontend
   npm run build
   ```

2. **Start the API (serves frontend as static files):**
   ```bash
   python -m uvicorn komikan.api.main:app --host 0.0.0.0 --port 8000
   ```

3. **Access at:** http://localhost:8000

### Using Docker Compose

```bash
docker-compose up
```

This starts both frontend (port 5173) and backend (port 8000) services.

## API Endpoints

- `POST /api/games` - Create a new game
- `GET /api/games/{game_id}` - Get game state
- `POST /api/games/{game_id}/moves` - Make a move
- `GET /api/games/{game_id}/moves` - Get move history
- `GET /api/games/{game_id}/valid-moves?from_x={x}&from_y={y}` - Get valid moves
- `DELETE /api/games/{game_id}` - Delete game

## Testing

### Backend Tests
```bash
pytest tests/ -v
```

### API Tests
```bash
pytest tests/test_api.py -v
```

## Game Rules

See `docs/GAME_RULES.md` for complete game rules.

### Quick Reference

- **Board:** 5×8 grid
- **Players:**
  - North (Pangui): 1 red token, starts at (2, 0)
  - South (Pu Trewa): 12 blue tokens
- **Turns:** North moves first, players alternate
- **Movement:** One token per turn, adjacent node (orthogonal or diagonal)
- **Capture:** Only North can capture by jumping over South tokens
- **Win Conditions:**
  - North wins: Captures enough South tokens (≤4 remaining)
  - South wins: Traps North (no valid moves)
  - Stalemate: South has no valid moves on their turn
