# ADR-006: LLM Agent Integration

## Status

Accepted (completed)

## Context

With the REST API in place (ADR-004), the game can be played programmatically. The next step is enabling LLM-powered agents to play Komikan autonomously — either as opponents for human players, or headless for strategy evaluation.

## Decision

### Agent Architecture

- Create `src/komikan/agent/` package with a provider-agnostic LLM agent
- Agent communicates with the game exclusively via the REST API (no direct access to in-memory game state)
- This keeps the agent decoupled from the game engine and testable against any API server

### Provider Abstraction

- Define `LLMProvider` protocol in `provider.py` — any adapter must implement `chat(system_prompt, user_prompt, tools) -> LLMResponse`
- Ship two adapters:
  - `openai_provider.py` — OpenAI tool-calling API
  - `anthropic_provider.py` — Anthropic tool-use API
- Factory function in `factory.py` creates providers by name (`"openai"` or `"anthropic"`)
- Provider SDKs are optional dependencies (`pip install komikan-game[llm]`)

### Tool-Calling Strategy

- Agent sends game state + valid moves as a structured prompt
- LLM responds by calling a single `make_move(from_x, from_y, to_x, to_y)` tool
- Agent validates the returned move against the list of legal moves before executing
- On invalid moves, the agent retries with corrected prompt (up to 3 attempts)
- After exhausting retries, falls back to a random legal move

### Game Loop

- `KomikanAgent.play_turn()` — executes one turn (fetch state, query LLM, validate, execute)
- `KomikanAgent.play_until_done(max_turns)` — runs a full game loop, skipping opponent turns
- `agent_game_loop(agent, opponent, max_turns)` — orchestrates agent vs opponent via `Opponent` protocol
- `RandomOpponent` — picks a uniformly random legal move via the REST API

### Side Normalization

- User-facing CLI accepts `--side north` / `--side south` (human-friendly)
- API enum values are `"pangui"` / `"pu trewa"`
- `KomikanAgent.__init__` normalizes via `_SIDE_MAP = {"north": "pangui", "south": "pu trewa"}`
- Accepts both forms idempotently (passing `"pangui"` directly also works)

### CLI Entry Point

- `komikan-agent` script registered in `pyproject.toml`
- Flags: `--provider`, `--model`, `--side`, `--opponent`, `--delay`, `--base-url`
- Creates game, runs agent vs opponent, prints board state each turn
- Supports human opponent (`--opponent human`) for interactive play

## Consequences

- LLM choice is decoupled from game logic — adding a new provider only requires implementing `LLMProvider`
- Agent works against any running API server (local or remote)
- Random fallback ensures the game never stalls due to LLM errors
- Optional `[llm]` extra keeps core dependencies light
- Headless game loop enables automated strategy evaluation and benchmarking
