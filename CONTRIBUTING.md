# Contributing to Komikan

Thanks for your interest in contributing to Komikan!

## Prerequisites

- Python 3.11+
- Node.js 22+
- [uv](https://docs.astral.sh/uv/) (Python package manager)
- npm (ships with Node)

## Setup

```bash
git clone https://github.com/diegoquintanav/komikan-game.git
cd komikan-game
uv sync
cd frontend && npm install && cd ..
```

## Running the app

| Layer | Command |
|---|---|
| Pygame desktop | `uv run python -m komikan` |
| REST API | `uv run komikan-api` |
| React frontend | `cd frontend && npm run dev` |
| Docker (all) | `docker-compose up` |

## Running tests

```bash
uv run pytest tests/ -v            # Python tests
cd frontend && npm run build       # TypeScript type-check
cd frontend && npm run lint        # ESLint
```

## PR expectations

- **Commits**: [Conventional Commits](https://www.conventionalcommits.org/) (`feat:`, `fix:`, `docs:`, etc.)
- **Branch naming**: `diegoquintanav/almud-XXX-short-description`
- Keep PRs focused — one issue per PR when possible.

## Code style

- **Python**: [Ruff](https://docs.astral.sh/ruff/) for linting and formatting (`ruff check .`, `ruff format .`)
- **TypeScript**: ESLint via `npm run lint` in `frontend/`

## Architecture

- Game logic lives in `src/komikan/` (board, player, API)
- Frontend lives in `frontend/` (React + TypeScript + Tailwind + Vite)
- No database — game state is in-memory only
- See [README.md](README.md) for full project structure
