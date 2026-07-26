# ADR-004: REST API with FastAPI and React Web Interface

## Status

Accepted (completed)

## Context

The game needed to be accessible beyond the Pygame desktop interface, requiring a web-based approach with a REST API backend and modern frontend for broader accessibility.

## Decision

### Backend (FastAPI)

- Create FastAPI application in `src/komikan/api/` exposing game logic via REST endpoints
- Endpoints: `POST /api/games`, `GET /api/games/{game_id}`, `POST /api/games/{game_id}/moves`, `GET /api/games/{game_id}/moves`, `GET /api/games/{game_id}/valid-moves`, `DELETE /api/games/{game_id}`
- In-memory game state management supporting multiple concurrent games
- Move tracking with timestamps, player info, positions, success/failure, and capture details
- Win condition detection and edge case handling
- Pydantic models for request/response schemas
- CORS middleware for local development

### Frontend (React + Tailwind)

- React application in `frontend/` using Vite
- Board visualization with 5×8 grid, nodes, paths, and tokens
- Click-to-select and click-to-move interaction
- Visual indicators for current player, selected token, valid moves, disabled nodes
- Move history panel with chronological display
- Game status display (turn, win condition, token counts)
- TypeScript for type safety, Tailwind CSS for styling

### Integration

- FastAPI serves React build as static files in production
- Development mode supports separate frontend/backend servers

## Consequences

- Game is accessible via any modern web browser
- Multiple concurrent game sessions supported
- Full move history enables replay and auditing
- Server-side validation prevents client-side manipulation
- API-first design enables future integrations (MCP, AI agents)
