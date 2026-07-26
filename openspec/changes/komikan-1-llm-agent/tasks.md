# Tasks: Komikan LLM Agent (ALMUD-278)

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | ~850-1000 (additions only; mostly new files) |
| 400-line budget risk | High |
| Chained PRs recommended | Yes |
| Suggested split | PR 1 → PR 2 → PR 3 → PR 4 |
| Delivery strategy | ask-on-risk |
| Chain strategy | pending |

Decision needed before apply: Yes
Chained PRs recommended: Yes
Chain strategy: pending
400-line budget risk: High

### Suggested Work Units

| Unit | Goal | Likely PR | Focused test command | Runtime harness | Rollback boundary |
|------|------|-----------|----------------------|-----------------|-------------------|
| 1 | Bulk valid-moves endpoint | PR 1 | `uv run pytest tests/test_api.py -v` | API tests via AsyncClient | api/models.py, api/game_manager.py, api/main.py + test_api.py additions |
| 2 | LLM provider abstraction + adapters | PR 2 | `uv run pytest tests/test_agent/test_provider.py tests/test_agent/test_openai_provider.py tests/test_agent/test_anthropic_provider.py -v` | Unit tests with mocked SDKs | agent/provider.py, agent/openai_provider.py, agent/anthropic_provider.py, agent/factory.py |
| 3 | Agent game loop, bot, prompts | PR 3 | `uv run pytest tests/test_agent/ -v` | Unit tests with mocked LLM + API | agent/agent.py, agent/bot.py, agent/opponent.py, agent/prompts.py |
| 4 | CLI entry point + pyproject.toml | PR 4 | `uv run komikan-agent --help` + full integration test | CLI subprocess call | cli.py, pyproject.toml |

## Phase 1: Bulk Valid-Moves Endpoint

- [ ] 1.1 Add `TokenMoves` and `AllValidMovesResponse` models to `src/komikan/api/models.py`
- [ ] 1.2 RED: Add test `test_get_all_valid_moves` to `tests/test_api.py` — create game, GET all-valid-moves, assert 200 and token list with moves/captures
- [ ] 1.3 GREEN: Add `get_all_valid_moves()` method to `GameInstance` in `src/komikan/api/game_manager.py` — iterate current player positions, reuse existing `get_valid_moves()` per token
- [ ] 1.4 GREEN: Add `GET /api/games/{game_id}/all-valid-moves` endpoint to `src/komikan/api/main.py` — game-not-found → 404, game-over → 400, valid → 200
- [ ] 1.5 RED: Add tests for 404 and game-over scenarios to `tests/test_api.py`
- [ ] 1.6 RED: Add test for South player with no captures in response
- [ ] 1.7 Run `uv run pytest tests/test_api.py -v` — all pass; run `uv run pytest tests/ -v` — 220+ existing tests still pass

## Phase 2: LLM Provider Abstraction

- [ ] 2.1 Create `src/komikan/agent/__init__.py` with public re-exports
- [ ] 2.2 Create `src/komikan/agent/provider.py` — `ToolCall` dataclass, `ChatResponse` dataclass, `LLMProvider` Protocol with `chat()` method
- [ ] 2.3 RED: Create `tests/test_agent/__init__.py` and `tests/test_agent/test_provider.py` — test protocol conformance via structural typing, test ChatResponse construction
- [ ] 2.4 Create `src/komikan/agent/openai_provider.py` — `OpenAIProvider` wrapping openai SDK; `chat()` translates tool-calling response to `ChatResponse`; rate-limit retry with exponential backoff (3 retries)
- [ ] 2.5 RED: Create `tests/test_agent/test_openai_provider.py` — mock openai client; verify tool_calls round-trip, verify rate-limit retry behavior
- [ ] 2.6 Create `src/komikan/agent/anthropic_provider.py` — `AnthropicProvider` wrapping anthropic SDK; `chat()` translates tool-use response to `ChatResponse`; rate-limit retry (3 retries)
- [ ] 2.7 RED: Create `tests/test_agent/test_anthropic_provider.py` — mock anthropic client; verify tool_use round-trip, verify rate-limit retry
- [ ] 2.8 Create `src/komikan/agent/factory.py` — `create_provider(name, **kwargs)` dispatching to OpenAI/Anthropic; raises ValueError for unknown
- [ ] 2.9 RED: Add factory tests to `tests/test_agent/test_provider.py` — create_provider("openai") returns OpenAIProvider, create_provider("unknown") raises ValueError
- [ ] 2.10 Run `uv run pytest tests/test_agent/test_provider.py tests/test_agent/test_openai_provider.py tests/test_agent/test_anthropic_provider.py -v`

## Phase 3: Agent Game Loop, Bot, and Prompts

- [ ] 3.1 Create `src/komikan/agent/opponent.py` — `Opponent` Protocol with `get_move(game_id: str) -> tuple[int,int,int,int] | None`
- [ ] 3.2 Create `src/komikan/agent/prompts.py` — `format_game_state()` and `format_valid_moves()` producing LLM context; system prompt with Komikan rules; `KOMIKAN_TOOLS` tool definition list
- [ ] 3.3 RED: Create `tests/test_agent/test_bot.py` — test `RandomBot.get_move()` returns a valid move from all-valid-moves; test single HTTP call per turn (mock httpx)
- [ ] 3.4 Create `src/komikan/agent/bot.py` — `RandomBot` implementing Opponent; uses httpx to call all-valid-moves + moves endpoints; uniform random selection
- [ ] 3.5 RED: Create `tests/test_agent/test_agent.py` — test agent retry logic: mock LLM returns invalid moves 3x then valid; assert fallback to random legal move; test agent plays North to terminal state with mocked LLM returning valid moves
- [ ] 3.6 Create `src/komikan/agent/agent.py` — `KomikanAgent` with `play_game()` loop; fetches state → fetches moves → formats context → calls LLM → validates output → retries 3x → fallback; prints LLM text explanations alongside moves
- [ ] 3.7 RED: Add test for agent playing South to completion
- [ ] 3.8 Run `uv run pytest tests/test_agent/ -v`

## Phase 4: CLI Entry Point and Integration

- [ ] 4.1 Create `src/komikan/cli.py` — `main()` with argparse: `--side` (north/south), `--provider` (openai/anthropic), `--model`, `--opponent` (random/human), `--delay` (seconds between moves)
- [ ] 4.2 RED: Create `tests/test_agent/test_cli.py` — test CLI invocation via subprocess with `--help`; test `--side` and `--provider` flag parsing
- [ ] 4.3 Add `openai` and `anthropic` as optional dev dependencies in `pyproject.toml`; add `komikan-agent = "komikan.cli:main"` to `[project.scripts]`
- [ ] 4.4 Run `uv run komikan-agent --help` — verify output
- [ ] 4.5 Run `uv run pytest tests/ -v` — all 220+ existing tests + new tests pass
- [ ] 4.6 Run `uv run ruff check .` and `uv run ruff format --check .` — clean
