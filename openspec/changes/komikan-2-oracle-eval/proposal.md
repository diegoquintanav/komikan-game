# Proposal: Komikan Oracle and Eval Harness (ALMUD-280)

## Intent

Add a deterministic oracle player, structured match logging, and an eval harness that runs head-to-head matches, so the existing LLM agent can be measured against a stable, reproducible baseline. This covers the eight implementation tickets in the project backlog (ALMUD-281 to ALMUD-288) in dependency order and establishes the measurement layer that the LLM agent change (komikan-1) deferred.

Related ADRs: ADR-004 (REST API), ADR-005 (MCP server, still Proposed), ADR-006 (LLM agent integration). This change records the sequencing decision in ADR-007 and builds on the REST contract from ADR-004 and the `Opponent` seam from ADR-006.

## Ticket Map

| Ticket | Backlog item | Covered by |
|--------|--------------|------------|
| ALMUD-280 | Define specs using SDD | This change |
| ALMUD-281 | Minimax oracle with alpha-beta | `oracle-player` |
| ALMUD-282 | Position evaluation heuristic | `position-evaluation` |
| ALMUD-283 | Match runner with configurable pairings | `eval-harness` (runner) |
| ALMUD-284 | Structured per-move match logging | `match-logging` |
| ALMUD-285 | Decide sweep scope against budget | `comparative-sweep` (budget gate) |
| ALMUD-286 | Aggregation and reporting layer | `eval-harness` (report) |
| ALMUD-287 | Minimal results dashboard | `eval-harness` (dashboard) |
| ALMUD-288 | Comparative sweep across models and prompts | `comparative-sweep` |

## Scope

### In Scope

- Deterministic position evaluation heuristic over the core engine: South tokens remaining (material), mobility, capture availability, Pangui distance to nearest dog, escape-square count.
- Oracle player: negamax with alpha-beta pruning over the core engine, configurable depth (default 3), deterministic tie-breaking, returns only legal moves.
- State mirror: reconstruct a local searchable state by replaying `GET /api/games/{id}/moves`, plus an in-process snapshot path for unit tests.
- `OracleOpponent`: implements the existing `Opponent` protocol and posts the chosen move.
- Match runner: LLM vs oracle, LLM vs LLM, oracle vs oracle (sanity), and oracle vs random pairings; configurable games, seeds, and max plies; alternating sides.
- Structured per-move logging: legality, the oracle's preferred move, the chosen move, and the evaluation delta that feeds the blunder rate.
- Budget gate: an explicit decision on model count, games per pairing, and prompt variants before any sweep runs.
- Aggregation and reporting: win rate by model and config, win rate by side, blunder rate, average evaluation delta, latency, illegal moves, fallbacks, and usage.
- Minimal dashboard: a generated static page or notebook that presents the report legibly. No frontend framework.
- Comparative sweep: at least two prompting strategies (direct-move vs chain-of-thought) and as many model families and sizes as the budget allows.
- CLI entry point `komikan-eval` (also `python -m komikan.eval`).
- Tests and gates: `uv run pytest`, `uv run ruff check .`, `uv run ruff format --check .`.
- ADR-007 documenting the oracle-plus-eval-first sequencing decision.

### Out of Scope

- MCP server wrapping and RAG (now Project 3).
- The React frontend.
- Research benchmark publication or leaderboard.
- Persistent database storage (results are local files).

## Capabilities

### New Capabilities

- `position-evaluation`: Static, deterministic evaluation of a board position.
- `oracle-player`: Negamax search with alpha-beta pruning over the core engine.
- `state-mirror`: Reconstruct a searchable local state from a live REST game.
- `oracle-opponent`: Oracle adapter implementing the existing `Opponent` protocol.
- `match-logging`: Structured per-move records with oracle agreement and evaluation delta.
- `eval-harness`: Match runner, aggregation, report, dashboard, and CLI.
- `comparative-sweep`: Budget gate plus the model and prompting-strategy sweep.

### Modified Capabilities

None - no existing spec-level behavior changes.

## Approach

1. Write ADR-007 and the static evaluation over an immutable `SearchState` (ALMUD-282). Unit tests first.
2. Build the negamax plus alpha-beta oracle with capture-first ordering and seeded tie-breaking (ALMUD-281).
3. Build the state mirror and `OracleOpponent`, then the match runner with configurable pairings (ALMUD-283).
4. Add structured per-move JSONL logging with legality, oracle move, and evaluation delta (ALMUD-284).
5. Add the budget gate: a sizing decision recorded before any sweep (ALMUD-285).
6. Build aggregation and reporting (ALMUD-286) and the minimal dashboard (ALMUD-287).
7. Run the comparative sweep across prompting strategies and models sized to budget (ALMUD-288).
8. Add the CLI entry point and run the full test, lint, and format gates.

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `src/komikan/eval/` | New | Evaluation, oracle, mirror, opponent, runner, logging, report, dashboard, sweep, CLI |
| `pyproject.toml` | Modified | Add `komikan-eval` console script |
| `tests/test_eval/` | New | Unit and integration tests for each module |
| `reports/` | New (generated) | JSONL match logs, JSON and Markdown reports, dashboard output |
| `docs/adr/007-oracle-and-eval-harness.md` | New | Sequencing decision record |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Search too slow at depth 4+ | Med | Alpha-beta plus capture-first ordering; default depth 3; node cap via CLI |
| Mirror drifts from live REST state | Med | Replay is authoritative; parity assertion against `GET /api/games/{id}`; raise on mismatch |
| Evaluation sign bug under negamax | Med | Antisymmetry tests; terminal-handling tests |
| LLM nondeterminism skews results | High | Record model, temperature, provider, and prompt strategy; Wilson intervals; no significance claims at low N |
| Sweep cost overrun | High | Budget gate before any sweep; small N default; per-game cost reported; sweeps opt-in |
| Dashboard scope creep | Med | Static HTML or notebook only; no framework, no server |
| Prompt-strategy comparison confounded | Med | Hold model and depth fixed while varying strategy; log both in every record |

## Rollback Plan

- Delete `src/komikan/eval/` and `tests/test_eval/`.
- Revert the `komikan-eval` script line in `pyproject.toml`.
- Delete `docs/adr/007-oracle-and-eval-harness.md`.
- No data migration (local files only).

## Dependencies

- Project 1 (LLM agent) is complete and merged.
- `httpx` (already present) for mirror and runner REST calls.
- `random` (stdlib) for seeded tie-breaking and pairing.
- Optional `llm` extra (`openai`, `anthropic`) already present for LLM pairings.
- A running backend on `localhost:8000` for the replay-mirror and LLM pairings.

## Success Criteria

- [ ] ALMUD-282: evaluation is deterministic and antisymmetric under side flips
- [ ] ALMUD-281: oracle returns only legal moves and is deterministic given (state, depth, seed)
- [ ] ALMUD-283: the match runner executes all configured pairings to a terminal state with alternating sides
- [ ] ALMUD-284: every move is logged with legality, oracle preferred move, and evaluation delta
- [ ] ALMUD-285: the sweep sizing decision is recorded before any sweep runs
- [ ] ALMUD-286: the report includes win rate by model/config and by side, blunder rate, average evaluation delta, latency, fallbacks, and Wilson intervals
- [ ] ALMUD-287: a static dashboard renders the report without a frontend framework
- [ ] ALMUD-288: the comparative sweep runs at least two prompting strategies across the models the budget allows
- [ ] `uv run komikan-eval --help` runs and lists all flags
- [ ] `uv run pytest`, `uv run ruff check .`, `uv run ruff format --check .` all pass
- [ ] ADR-007 committed under `docs/adr/`
