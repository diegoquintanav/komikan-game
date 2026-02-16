# Feature 5: MCP Server with FastMCP and AI Agents

Implement a layer with FastMCP so that the Komikan game can be played as an MCP (Model Context Protocol) server. Create two agents that play a game against each other.

## Requirements

### MCP Server (FastMCP)

1. Create an MCP server in `src/komikan/mcp/` using the FastMCP library:
   - Expose the game as MCP tools that AI agents can invoke.
   - Tools should include:
     - `create_game` — Start a new game session.
     - `get_game_state` — Retrieve current board state, positions, and whose turn it is.
     - `get_valid_moves` — Get all valid moves for the current player.
     - `make_move` — Execute a move (from_x, from_y, to_x, to_y).
     - `get_move_history` — Retrieve the full move log.
     - `get_game_rules` — Return the game rules summary.
   - Include MCP resources for game state observation.
   - Include MCP prompts for guiding agents on how to play.

2. Reuse the game engine from `src/komikan/board.py` and `src/komikan/player.py`.
3. Reuse the REST API game management logic from Feature 4 if available.

### AI Agents

1. Create two agents in `src/komikan/agents/` that play Komikan against each other:
   - **Agent North (Pangui)**: Plays as the North player (1 token, can capture).
   - **Agent South (Pu Trewa)**: Plays as the South player (12 tokens, tries to surround).

2. Each agent should:
   - Connect to the MCP server as a client.
   - Query the game state and valid moves.
   - Choose a move based on a strategy (can be simple heuristic or random for MVP).
   - Execute moves through MCP tool calls.
   - Handle game-over conditions gracefully.

3. Create a runner script that:
   - Starts the MCP server.
   - Initializes both agents.
   - Plays a complete game with both agents taking turns.
   - Logs the full game for replay and analysis.

### Integration

- The MCP server should work with `fastmcp` library.
- Agents should use an MCP client to interact with the server.
- The game should be fully playable without human intervention.
- All moves should be logged and auditable.

## Validation

- Run a complete automated game between the two agents.
- Verify all moves are valid and the game reaches a conclusion.
- Verify the move history can reproduce the game.
- All existing tests must continue to pass.
- Add tests for MCP tool invocations.
