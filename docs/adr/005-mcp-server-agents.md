# ADR-005: MCP Server with FastMCP and AI Agents

## Status

Proposed

## Context

To enable AI agents to play Komikan, the game needs to be exposed via the Model Context Protocol (MCP), allowing autonomous agents to interact with the game engine through standard tool calls.

## Decision

### MCP Server (FastMCP)

- Create MCP server in `src/komikan/mcp/` using the FastMCP library
- Expose game as MCP tools:
  - `create_game` — Start a new game session
  - `get_game_state` — Retrieve current board state, positions, and turn
  - `get_valid_moves` — Get all valid moves for the current player
  - `make_move` — Execute a move (from_x, from_y, to_x, to_y)
  - `get_move_history` — Retrieve the full move log
  - `get_game_rules` — Return the game rules summary
- Include MCP resources for game state observation
- Include MCP prompts for guiding agents on how to play
- Reuse game engine from `board.py` and `player.py`
- Reuse REST API game management logic from ADR-004

### AI Agents

- Create two agents in `src/komikan/agents/`:
  - **Agent North (Pangui)**: Plays as the North player (1 token, can capture)
  - **Agent South (Pu Trewa)**: Plays as the South player (12 tokens, tries to surround)
- Each agent connects to MCP server as a client
- Agents query game state, evaluate valid moves, choose moves (heuristic or random for MVP)
- Runner script starts MCP server, initializes both agents, plays a complete game

## Consequences

- Game becomes playable without human intervention
- AI agents can develop and test strategies automatically
- MCP integration enables composition with other MCP-compatible tools
- All moves are logged and auditable through existing logging system
- Foundation for tournament play and AI training data generation
