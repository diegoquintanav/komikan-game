# Proposal: Komikan LLM Agent (ALMUD-278)

## Intent

First proof that an LLM can play a full legal game of Komikan using the existing REST API via tool/function calling. This validates the API surface is agent-consumable and establishes the foundation for future AI opponents and eval harnesses.

## Scope

### In Scope

- **Bulk valid-moves endpoint**: `GET /api/games/{game_id}/all-valid-moves` returning all legal moves for the current player in one call (prerequisite for agent efficiency)
- **LLM provider abstraction**: Provider-agnostic interface supporting OpenAI, Anthropic, and local models via a `LLMProvider` protocol with `chat()` method
- **Komikan agent**: Game loop that reads state, queries LLM with tool definitions, executes moves. Configurable to play North (Pangui) or South (Pu Trewa)
- **Random legal-move bot**: Deterministic opponent for testing (picks randomly from valid moves)
- **CLI runner**: Terminal entry point showing game state after each move. Supports `--side`, `--provider`, `--model`, `--opponent` flags
- **Full game completion**: Agent plays until terminal state (north_won, south_won, stalemate)

### Out of Scope

- MCP server wrapping (Project 2)
- RAG rules explainer (Project 2)
- Eval harness / win-rate benchmarks (Project 3)
- Frontend integration
- Persistent game storage
- Multi-turn conversation / memory across games

## Capabilities

### New Capabilities

- `bulk-valid-moves`: All-valid-moves endpoint for the current player without per-token queries
- `llm-provider`: Abstract provider interface with OpenAI and Anthropic implementations
- `komikan-agent`: LLM-powered game agent using tool calling to play Komikan
- `random-bot`: Random legal-move opponent for testing

### Modified Capabilities

None — no existing spec-level behavior changes.

## Approach

1. Add `GET /api/games/{game_id}/all-valid-moves` endpoint returning `[{from, moves[], captures[]}]` for all current-player tokens. Unit + API tests first (TDD).
2. Implement `LLMProvider` protocol in `src/komikan/agent/` with OpenAI and Anthropic adapters. Each wraps the provider's native tool-calling API.
3. Build `KomikanAgent` that: (a) fetches game state, (b) gets all valid moves, (c) formats game state + moves as LLM context, (d) calls LLM with tool definitions, (e) executes the returned move.
4. Build `RandomBot` that picks uniformly from valid moves.
5. Create `komikan-agent` CLI entry point using `click` or `argparse`.

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `src/komikan/api/main.py` | Modified | New `all-valid-moves` endpoint |
| `src/komikan/api/models.py` | Modified | New response model for bulk moves |
| `src/komikan/api/game_manager.py` | Modified | Method to aggregate valid moves across all tokens |
| `src/komikan/agent/` | New | LLM provider, agent, random bot modules |
| `src/komikan/cli.py` or equivalent | New | CLI entry point for agent runner |
| `tests/test_api.py` | Modified | Tests for new endpoint |
| `tests/test_agent/` | New | Agent, provider, and bot tests |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| LLM returns illegal move despite valid-move context | Med | Validate LLM output against valid moves; retry or fall back to random |
| Provider API rate limits during long games | Low | CLI supports `--delay` flag; agent handles 429 with backoff |
| Game state grows too large for LLM context window | Low | 5x8 grid + ~12 tokens is compact; truncate move history if needed |
| Anthropic/OpenAI tool-calling API differences | Med | Abstract behind protocol; test each provider independently |

## Rollback Plan

- Delete `src/komikan/agent/` directory and CLI entry point
- Revert changes to `api/main.py`, `api/models.py`, `api/game_manager.py`
- Remove agent-related test files
- No data migration needed (in-memory only)

## Dependencies

- `httpx` (already present) for API calls from agent to backend
- OpenAI Python SDK (`openai`) — new dev dependency
- Anthropic Python SDK (`anthropic`) — new dev dependency
- Backend server must be running on `localhost:8000`

## Success Criteria

- [ ] `GET /api/games/{game_id}/all-valid-moves` returns correct bulk moves with tests passing
- [ ] Agent can play a full game (North vs random bot) reaching a terminal state
- [ ] Agent can play a full game (South vs random bot) reaching a terminal state
- [ ] All moves executed by agent are legal (validated against valid-moves endpoint)
- [ ] CLI runs with `uv run komikan-agent --side north --provider openai --model gpt-4o`
- [ ] All existing 220+ tests continue passing
- [ ] New tests cover provider abstraction, agent loop, bot, and new endpoint
