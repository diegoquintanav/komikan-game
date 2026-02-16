# Komikan Game

A digital implementation of Komikan, a traditional Mapuche board game from southern Chile and Argentina. This project includes both a Pygame desktop version and a modern web interface with REST API.

## Features

- **Pygame Desktop Version**: Traditional desktop game with visual interface
- **REST API**: FastAPI-based backend for game management
- **Web Interface**: React + TypeScript frontend with real-time game state
- **Multiple Concurrent Games**: Support for multiple simultaneous game sessions
- **Move History**: Complete audit trail of all moves with timestamps
- **Win Condition Detection**: Automatic detection of game-ending states

## Game Overview

Komikan is an asymmetric hunt game where:
- **North (Pangui/Puma)**: 1 red token, can capture by jumping
- **South (Pu Trewa/Dogs)**: 12 blue tokens, win by surrounding
- **Board**: 5×8 grid with special disabled nodes and paths
- **Objective**: North captures tokens, South traps the Puma

See [docs/GAME_RULES.md](docs/GAME_RULES.md) for complete rules.

## Quick Start

### Web Application

1. **Install backend dependencies:**
   ```bash
   pip install -e .
   ```

2. **Install frontend dependencies:**
   ```bash
   cd frontend
   npm install
   ```

3. **Development mode** (separate servers):
   ```bash
   # Terminal 1: Start API
   python -m uvicorn komikan.api.main:app --reload

   # Terminal 2: Start frontend
   cd frontend
   npm run dev
   ```

4. **Access the application:**
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

### Using Docker

```bash
docker-compose up
```

### Desktop Game

```bash
python -m komikan
```

## API Endpoints

- `POST /api/games` - Create a new game
- `GET /api/games/{game_id}` - Get current game state
- `POST /api/games/{game_id}/moves` - Submit a move
- `GET /api/games/{game_id}/moves` - Get move history
- `GET /api/games/{game_id}/valid-moves` - Get valid moves for a token
- `DELETE /api/games/{game_id}` - Delete/forfeit a game

## Development

See [DEVELOPMENT.md](DEVELOPMENT.md) for detailed development instructions.

### Project Structure

```
komikan-game/
├── src/komikan/          # Python source code
│   ├── board.py          # Game board logic
│   ├── player.py         # Player management
│   ├── run.py            # Pygame interface
│   └── api/              # FastAPI REST API
│       ├── main.py       # API endpoints
│       ├── models.py     # Pydantic models
│       └── game_manager.py  # Game state management
├── frontend/             # React + TypeScript frontend
│   ├── src/
│   │   ├── components/   # React components
│   │   ├── types/        # TypeScript types
│   │   └── api.ts        # API client
│   └── dist/             # Production build
├── tests/                # Test suite (82 tests)
│   ├── test_board.py     # Board logic tests
│   ├── test_player.py    # Player tests
│   ├── test_integration.py  # Integration tests
│   └── test_api.py       # API tests
└── docs/                 # Documentation
    └── GAME_RULES.md     # Complete game rules
```

## Testing

```bash
# All tests (82 tests)
pytest tests/ -v

# Backend tests only
pytest tests/test_board.py tests/test_player.py tests/test_integration.py -v

# API tests only
pytest tests/test_api.py -v
```

## Technology Stack

- **Backend**: Python 3.11+, FastAPI, Pydantic, Pygame
- **Frontend**: React 18, TypeScript, Tailwind CSS, Vite
- **Testing**: pytest, httpx, pytest-asyncio
- **Deployment**: Docker, docker-compose

## Win Conditions

- **North (Pangui) wins**: Captures enough South tokens (≤4 remaining)
- **South (Pu Trewa) wins**: Traps North with no valid moves
- **Stalemate**: South has no valid moves on their turn

## License

This project is an educational implementation of a traditional Mapuche game.

## Credits

Based on the traditional Mapuche board game Komikan. Learn more at [Komikan on Adrián Cheuque Pan's website](https://adriancheuquepan.cl/komikan/).
