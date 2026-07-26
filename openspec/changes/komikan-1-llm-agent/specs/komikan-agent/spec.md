# Komikan Agent Specification

## Purpose

LLM-powered game agent that plays Komikan by reading state, querying the LLM with tool definitions, and executing moves via the REST API. Includes CLI entry point.

## Requirements

### Requirement: Agent Game Loop

The agent SHALL play a complete game by repeating: fetch game state, fetch valid moves, call LLM with tool definitions, execute the returned move, until a terminal state.

#### Scenario: Agent plays North to completion

- GIVEN an active game with agent playing North (Pangui) vs a random bot
- WHEN the agent runs its game loop
- THEN every move executed is valid per the all-valid-moves endpoint
- AND the game reaches a terminal state (north_won, south_won, or stalemate)

#### Scenario: Agent plays South to completion

- GIVEN an active game with agent playing South (Pu Trewa) vs a random bot
- WHEN the agent runs its game loop
- THEN every move executed is valid per the all-valid-moves endpoint
- AND the game reaches a terminal state

#### Scenario: Agent validates LLM output against legal moves

- GIVEN the LLM returns a move not in the valid moves list
- WHEN the agent attempts to execute the move
- THEN the agent retries the LLM call up to 3 times with the invalid move noted in context
- AND after 3 failures, the agent falls back to a random legal move

### Requirement: Agent Side Configuration

The agent SHALL accept a `side` parameter ("north" or "south") determining which player it controls.

#### Scenario: Default side is north

- GIVEN an agent instantiated without explicit side
- WHEN the agent starts
- THEN it plays as North (Pangui)

### Requirement: Agent Tool Definitions

The agent SHALL define tool schemas for `get_game_state`, `get_all_valid_moves`, and `make_move` that the LLM can invoke.

#### Scenario: Tool schemas are valid for OpenAI format

- GIVEN the agent's tool definitions
- WHEN passed to OpenAI's chat API
- THEN the schemas are accepted without validation errors

#### Scenario: Tool schemas are valid for Anthropic format

- GIVEN the agent's tool definitions
- WHEN passed to Anthropic's messages API
- THEN the schemas are accepted without validation errors

### Requirement: Agent Opponent Modes

The agent SHALL support playing against either a human (via existing REST API) or a random bot.

#### Scenario: Agent vs random bot

- GIVEN agent configured with --opponent random
- WHEN the game loop runs
- THEN the agent plays its moves and the bot plays the opponent's moves automatically

#### Scenario: Agent vs human (API passthrough)

- GIVEN agent configured with --opponent human
- WHEN the agent completes its turn
- THEN the agent waits for the human to submit their move via the API before continuing

### Requirement: Agent Provider Configuration

The agent SHALL accept `--provider` and `--model` flags to select which LLM backend to use.

#### Scenario: CLI with provider and model

- GIVEN the command `komikan-agent --provider openai --model gpt-4o`
- WHEN the CLI starts
- THEN the agent uses an OpenAIProvider with model "gpt-4o"

### Requirement: Game State Formatting

The agent SHALL format the game state and valid moves as structured context for the LLM prompt.

#### Scenario: LLM receives actionable context

- GIVEN the agent has fetched game state and valid moves
- WHEN the agent calls the LLM
- THEN the prompt includes: current board positions, current player, move count, and the full list of legal moves with their from/to coordinates

### Requirement: CLI Entry Point

The system SHALL provide a `komikan-agent` CLI command via the `komikan-agent` console_scripts entry point.

#### Scenario: CLI invocation with flags

- GIVEN the command `uv run komikan-agent --side north --provider openai --model gpt-4o --opponent random`
- WHEN executed
- THEN a game is created and played to completion, printing each move to stdout

#### Scenario: CLI shows game result

- GIVEN a game that has reached a terminal state
- WHEN the CLI finishes
- THEN the final game status (north_won/south_won/stalemate) is printed
