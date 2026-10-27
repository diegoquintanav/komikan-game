# Delta for komikan-1-llm-agent

## ADDED Requirements

### Requirement: Bulk Valid Moves Endpoint

The system SHALL expose `GET /api/games/{game_id}/all-valid-moves` returning every legal move and capture for the current player in one response.

#### Scenario: Happy path — active game with multiple tokens

- GIVEN an active game with game_id
- WHEN GET /api/games/{game_id}/all-valid-moves is called
- THEN the response contains a list of token entries, each with `from` position, `moves` (list of destination positions), and `captures` (list of [to, captured] pairs)
- AND the response status is 200

#### Scenario: Game not found

- GIVEN no game exists with game_id "nonexistent"
- WHEN GET /api/games/nonexistent/all-valid-moves is called
- THEN the response status is 404 with error detail "Game nonexistent not found"

#### Scenario: Game already over

- GIVEN a game with status "north_won" or "south_won" or "stalemate"
- WHEN GET /api/games/{game_id}/all-valid-moves is called
- THEN the response status is 400 with error detail containing "Game is already over"

#### Scenario: Current player has no valid moves

- GIVEN an active game where the current player has zero legal moves (stalemate condition)
- WHEN GET /api/games/{game_id}/all-valid-moves is called
- THEN the response contains an empty list of tokens

#### Scenario: North player with capture options

- GIVEN an active game where North has a token adjacent to a South token with an empty landing behind it
- WHEN GET /api/games/{game_id}/all-valid-moves is called
- THEN North's token entry includes both regular moves and captures in its response

#### Scenario: South player never has captures

- GIVEN an active game where it is South's turn
- WHEN GET /api/games/{game_id}/all-valid-moves is called
- THEN no token entry contains captures (South cannot capture by rule)

### Requirement: LLMProvider Protocol

The system SHALL define a `LLMProvider` protocol with a `chat()` method accepting messages and tool definitions, returning a response with tool calls or text.

#### Scenario: Successful tool call response

- GIVEN an LLMProvider instance configured with valid credentials
- WHEN chat() is called with messages and tool definitions
- THEN the response contains either tool_calls (list of {name, arguments}) or text content

#### Scenario: Provider rejects invalid credentials

- GIVEN an LLMProvider with malformed API key
- WHEN chat() is called
- THEN the provider raises an appropriate error (not an unhandled exception)

### Requirement: OpenAI Provider Implementation

The system SHALL provide an OpenAI adapter implementing LLMProvider, wrapping the OpenAI Python SDK's tool-calling API.

#### Scenario: OpenAI tool call round-trip

- GIVEN an OpenAIProvider with valid API key and model (e.g., gpt-4o)
- WHEN chat() is called with Komikan move tool definitions
- THEN the response tool_calls match the OpenAI function-calling response format

#### Scenario: OpenAI provider handles rate limits

- GIVEN an OpenAIProvider receiving a 429 rate-limit response
- WHEN chat() is called
- THEN the provider retries with exponential backoff (up to 3 retries)

### Requirement: Anthropic Provider Implementation

The system SHALL provide an Anthropic adapter implementing LLMProvider, wrapping the Anthropic Python SDK's tool-use API.

#### Scenario: Anthropic tool use round-trip

- GIVEN an AnthropicProvider with valid API key and model (e.g., claude-sonnet-4-20250514)
- WHEN chat() is called with Komikan move tool definitions
- THEN the response tool_calls match the Anthropic tool_use response format

#### Scenario: Anthropic provider handles rate limits

- GIVEN an AnthropicProvider receiving a 429 rate-limit response
- WHEN chat() is called
- THEN the provider retries with exponential backoff (up to 3 retries)

### Requirement: Provider Factory

The system SHALL provide a factory function `create_provider(name, **kwargs)` returning an LLMProvider instance by name ("openai" or "anthropic").

#### Scenario: Factory creates OpenAI provider

- GIVEN the string "openai" and api_key kwarg
- WHEN create_provider("openai", api_key="sk-...") is called
- THEN the returned instance implements LLMProvider and delegates to OpenAI

#### Scenario: Factory rejects unknown provider

- GIVEN the string "ollama"
- WHEN create_provider("ollama") is called
- THEN a ValueError is raised with message listing supported providers

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

### Requirement: Random Move Selection

The bot SHALL pick a random move uniformly from the set of all legal moves (regular moves and captures) for the current player.

#### Scenario: Bot has both moves and captures available

- GIVEN a game where the current player (bot) has 3 regular moves and 1 capture
- WHEN the bot selects a move
- THEN exactly one of the 4 options is chosen (uniformly random)

#### Scenario: Bot has only regular moves (South side)

- GIVEN a game where the bot plays South
- WHEN the bot selects a move
- THEN only regular moves are considered (South cannot capture by rule)

### Requirement: Bot Uses Bulk Endpoint

The bot SHALL fetch all valid moves via the bulk `GET /api/games/{game_id}/all-valid-moves` endpoint rather than per-token queries.

#### Scenario: Bot fetches moves in single call

- GIVEN an active game with the bot as current player
- WHEN the bot needs to select a move
- THEN only one HTTP request to all-valid-moves is made per turn

### Requirement: Bot Plays via REST API

The bot SHALL make moves by calling `POST /api/games/{game_id}/moves` through the API, not by manipulating game state directly.

#### Scenario: Bot move goes through API validation

- GIVEN the bot selects a move
- WHEN the bot submits it via the moves endpoint
- THEN the move is validated by the API and returns success

### Requirement: Bot Implements Opponent Interface

The bot SHALL implement the same interface the agent expects from an opponent, accepting game context and returning a move.

#### Scenario: Bot is interchangeable with human opponent

- GIVEN an agent expecting an opponent that returns moves
- WHEN the bot is used as the opponent
- THEN the agent game loop runs identically to human opponent mode
