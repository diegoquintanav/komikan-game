# Design: Komikan LLM Agent (ALMUD-278)

## Technical Approach

Extend the existing FastAPI REST API with one new bulk endpoint, then build a new `src/komikan/agent/` package containing a provider-agnostic LLM protocol, two provider adapters (OpenAI, Anthropic), a game agent that plays via tool-calling, and a random-move bot for testing. A CLI entry point orchestrates full games. All new code follows existing TDD patterns: httpx AsyncClient for API tests, pytest fixtures from `conftest.py`, Pydantic v2 models.

## Architecture Decisions

### Decision: Bulk Valid-Moves Endpoint

| Option | Tradeoff | Decision |
|--------|----------|----------|
| New `GET /all-valid-moves` endpoint | One extra route; server iterates tokens | **Chosen** — clean, O(1) calls for agent |
| Reuse existing per-token endpoint in a loop | No API change; N HTTP calls per turn | Rejected — latency and token waste |
| Add batch parameter to existing endpoint | Smaller diff; backward-compatible | Rejected — muddies single-token semantics |

### Decision: LLMProvider Protocol

| Option | Tradeoff | Decision |
|--------|----------|----------|
| Python `Protocol` with `chat()` method | Structural typing, no ABC inheritance | **Chosen** — idiomatic, duck-typing friendly |
| Abstract base class | Enforces implementation; more boilerplate | Rejected — protocols are sufficient for 2 adapters |
| Direct SDK calls in agent | No abstraction; tight coupling | Rejected — blocks future providers |

### Decision: Retry + Fallback Strategy

| Option | Tradeoff | Decision |
|--------|----------|----------|
| 3 retries then random legal move | Guarantees progress; loses LLM strategy | **Chosen** — per spec |
| Unlimited retries | Never degrades; may hang | Rejected — no termination guarantee |
| Reject game on bad output | Strict; loses games | Rejected — agent must complete |

### Decision: Agent Game Loop Architecture

| Option | Tradeoff | Decision |
|--------|----------|----------|
| Poll-based loop: fetch state → fetch moves → call LLM → execute | Simple; clear state machine | **Chosen** — minimal, debuggable |
| WebSocket streaming | Real-time; complex | Rejected — overkill for CLI |
| Direct board manipulation | Fastest; bypasses API validation | Rejected — must validate via REST |

### Decision: CLI Framework

| Option | Tradeoff | Decision |
|--------|----------|----------|
| `argparse` (stdlib) | No extra dep; verbose | **Chosen** — lightweight, already have it |
| `click` | Rich features; new dependency | Rejected — adds dep for minimal benefit |

### Decision: Opponent Abstraction

| Option | Tradeoff | Decision |
|--------|----------|----------|
| Common `Opponent` protocol with `get_move(game_id)` | Clean swap; one interface | **Chosen** — RandomBot and human both fit |
| Separate code paths per opponent type | Simpler per path; duplicated logic | Rejected — violates DRY |

## Data Flow

```
CLI (komikan-agent)
  │
  ├─→ POST /api/games              (create game)
  │
  ├─→ Game Loop ──────────────────────────────────────┐
  │     │                                              │
  │     ├─→ GET /api/games/{id}               (state)  │
  │     ├─→ GET /api/games/{id}/all-valid-moves (moves)│
  │     ├─→ LLMProvider.chat(state, moves, tools)      │
  │     │     │                                        │
  │     │     ├─→ OpenAI API (tool calling)            │
  │     │     └─→ Anthropic API (tool use)             │
  │     │                                              │
  │     ├─→ Validate LLM output against valid moves    │
  │     │     ├─→ Valid: POST /api/games/{id}/moves     │
  │     │     └─→ Invalid: retry (×3) then random      │
  │     │                                              │
  │     ├─→ If opponent=human: wait for API poll        │
  │     ├─→ If opponent=random: RandomBot.get_move()   │
  │     │     └─→ GET /all-valid-moves → random pick   │
  │     │         └─→ POST /moves                      │
  │     │                                              │
  │     └─→ Check terminal state → loop or exit        │
  └────────────────────────────────────────────────────┘
```

## File Changes

| File | Action | Description |
|------|--------|-------------|
| `src/komikan/agent/__init__.py` | Create | Package init, re-exports public API |
| `src/komikan/agent/provider.py` | Create | `LLMProvider` protocol, `ChatResponse`, `ToolCall` dataclasses |
| `src/komikan/agent/openai_provider.py` | Create | `OpenAIProvider` adapter wrapping openai SDK |
| `src/komikan/agent/anthropic_provider.py` | Create | `AnthropicProvider` adapter wrapping anthropic SDK |
| `src/komikan/agent/factory.py` | Create | `create_provider(name, **kwargs)` factory function |
| `src/komikan/agent/agent.py` | Create | `KomikanAgent` — game loop, tool defs, retry logic |
| `src/komikan/agent/bot.py` | Create | `RandomBot` — random legal-move opponent |
| `src/komikan/agent/opponent.py` | Create | `Opponent` protocol for agent opponent abstraction |
| `src/komikan/agent/prompts.py` | Create | System prompt and state formatting for LLM context |
| `src/komikan/cli.py` | Create | CLI entry point with argparse flags |
| `src/komikan/api/main.py` | Modify | Add `GET /api/games/{game_id}/all-valid-moves` endpoint |
| `src/komikan/api/models.py` | Modify | Add `AllValidMovesResponse`, `TokenMoves` models |
| `src/komikan/api/game_manager.py` | Modify | Add `get_all_valid_moves()` method on `GameInstance` |
| `pyproject.toml` | Modify | Add `openai`, `anthropic` dev deps; add `komikan-agent` script |
| `tests/test_api.py` | Modify | Tests for all-valid-moves endpoint |
| `tests/test_agent/__init__.py` | Create | Test package |
| `tests/test_agent/test_provider.py` | Create | Unit tests for provider protocol and factory |
| `tests/test_agent/test_openai_provider.py` | Create | OpenAI adapter tests with mocked SDK |
| `tests/test_agent/test_anthropic_provider.py` | Create | Anthropic adapter tests with mocked SDK |
| `tests/test_agent/test_agent.py` | Create | Agent game loop tests with mocked LLM and API |
| `tests/test_agent/test_bot.py` | Create | RandomBot tests |
| `tests/test_agent/test_cli.py` | Create | CLI integration tests |

## Interfaces / Contracts

### LLMProvider Protocol

```python
from typing import Protocol, List
from dataclasses import dataclass

@dataclass
class ToolCall:
    name: str
    arguments: dict

@dataclass
class ChatResponse:
    tool_calls: List[ToolCall] | None
    text: str | None

class LLMProvider(Protocol):
    def chat(
        self,
        messages: list[dict],
        tools: list[dict],
        model: str,
    ) -> ChatResponse: ...
```

### AllValidMovesResponse (API model)

```python
class CapturePair(BaseModel):
    to: TokenPosition
    captured: TokenPosition

class TokenMoves(BaseModel):
    from_position: TokenPosition
    moves: List[TokenPosition]
    captures: List[CapturePair]

class AllValidMovesResponse(BaseModel):
    tokens: List[TokenMoves]
```

### Opponent Protocol

```python
class Opponent(Protocol):
    def get_move(self, game_id: str) -> tuple[int, int, int, int] | None: ...
```

### Tool Definitions (sent to LLM)

```python
KOMIKAN_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "make_move",
            "description": "Move a token from one position to another",
            "parameters": {
                "type": "object",
                "properties": {
                    "from_x": {"type": "integer", "enum": [0,1,2,3,4]},
                    "from_y": {"type": "integer", "enum": [0,1,2,3,4,5,6,7]},
                    "to_x": {"type": "integer", "enum": [0,1,2,3,4]},
                    "to_y": {"type": "integer", "enum": [0,1,2,3,4,5,6,7]},
                },
                "required": ["from_x", "from_y", "to_x", "to_y"],
            },
        },
    }
]
```

## Testing Strategy

| Layer | What to Test | Approach |
|-------|-------------|----------|
| Unit | `get_all_valid_moves()` on GameInstance | Direct method call, assert token list and captures |
| Unit | Provider factory | `create_provider("openai")` returns correct type; unknown raises ValueError |
| Unit | Provider adapters | Mock SDK client; verify chat() translates response to ChatResponse |
| Unit | RandomBot | Mock API calls; verify move is in valid set |
| Unit | Agent retry logic | Mock LLM to return invalid moves 3× then valid; assert fallback |
| Unit | Agent prompt formatting | Assert system prompt includes board state and legal moves |
| Integration | all-valid-moves endpoint | AsyncClient GET; verify 200/400/404 per spec scenarios |
| Integration | Agent full game loop | Mock LLM returns valid moves; assert game reaches terminal state |
| Integration | CLI invocation | Subprocess call with flags; verify stdout output |

## Threat Matrix

N/A — no routing, shell, subprocess, VCS/PR automation, executable-file classification, or process-integration boundary.

## Migration / Rollout

No data migration required. The backend is in-memory only. New endpoint is additive — no existing endpoints change. Agent package is new code under `src/komikan/agent/`. CLI entry point is new. Dev dependencies (`openai`, `anthropic`) are optional — agent fails gracefully if SDK not installed.

## Open Questions

- [ ] Should the agent print move explanations from LLM text output alongside move execution? (Enhancement, not blocking)
- [ ] Should `--delay` flag be included in MVP or deferred? (Spec mentions it; low priority)
- [ ] Local model support (ollama, etc.) — is a third adapter needed for MVP or deferred to follow-up?
