# Tasks: Komikan Oracle and Eval Harness (ALMUD-280)

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | ~1200-1500 (mostly new files) |
| 400-line budget risk | High |
| Chained PRs recommended | Yes |
| Suggested split | PR 1 -> PR 2 -> PR 3 -> PR 4 -> PR 5 -> PR 6 |
| Delivery strategy | ask-on-risk |
| Chain strategy | pending |

Decision needed before apply: Yes
Chained PRs recommended: Yes
Chain strategy: pending
400-line budget risk: High

### Suggested Work Units

| Unit | Goal | Tickets | Likely PR | Focused test command | Rollback boundary |
|------|------|---------|-----------|----------------------|-------------------|
| 1 | SearchState and static evaluation | ALMUD-282 | PR 1 | `uv run pytest tests/test_eval/test_evaluation.py -v` | `src/komikan/eval/evaluation.py`, `__init__.py`, related tests |
| 2 | Negamax oracle with alpha-beta | ALMUD-281 | PR 2 | `uv run pytest tests/test_eval/test_oracle.py -v` | `src/komikan/eval/oracle.py`, related tests |
| 3 | Mirror, OracleOpponent, match runner | ALMUD-283 | PR 3 | `uv run pytest tests/test_eval/test_mirror.py tests/test_eval/test_oracle_opponent.py tests/test_eval/test_runner.py -v` | `src/komikan/eval/mirror.py`, `oracle_opponent.py`, `runner.py`, related tests |
| 4 | Structured per-move logging | ALMUD-284 | PR 4 | `uv run pytest tests/test_eval/test_logging.py -v` | `src/komikan/eval/logging.py`, related tests |
| 5 | Aggregation, report, dashboard | ALMUD-286, ALMUD-287 | PR 5 | `uv run pytest tests/test_eval/test_report.py tests/test_eval/test_dashboard.py -v` | `src/komikan/eval/report.py`, `dashboard.py`, related tests |
| 6 | Budget gate, sweep, CLI | ALMUD-285, ALMUD-288 | PR 6 | `uv run pytest tests/test_eval/test_sweep.py tests/test_eval/test_cli.py -v` | `src/komikan/eval/sweep.py`, `cli.py`, `pyproject.toml`, related tests |

## Phase 0: Decision Record and Scaffolding (ALMUD-280)

- [ ] 0.1 Write `docs/adr/007-oracle-and-eval-harness.md` recording the sequencing decision and the metric definitions.
- [ ] 0.2 Create `src/komikan/eval/__init__.py` with public re-exports.
- [ ] 0.3 Create `tests/test_eval/__init__.py`.
- [ ] 0.4 Confirm the Linear project order (Oracle is Project 2, MCP is Project 3) and link this change to ALMUD-280.

## Phase 1: SearchState and Static Evaluation (ALMUD-282)

- [ ] 1.1 RED: Create `tests/test_eval/test_evaluation.py` asserting `evaluate(state) == -evaluate(flipped(state))` for at least five hand-built positions.
- [ ] 1.2 RED: Add tests for each term in isolation: material, mobility, capture availability, distance to nearest dog, escape squares.
- [ ] 1.3 RED: Add a test that the same state always yields the same score.
- [ ] 1.4 GREEN: Create `src/komikan/eval/evaluation.py` with the immutable `SearchState` dataclass (`north`, `south`, `side_to_move`) and the `evaluate(state)` function.
- [ ] 1.5 GREEN: Implement move generation by rebuilding a lightweight `GameBoard` from the snapshot and reusing `is_valid_move` / `is_valid_capture` for legality.
- [ ] 1.6 Run `uv run pytest tests/test_eval/test_evaluation.py -v` and `uv run ruff check src/komikan/eval`.

## Phase 2: Oracle Search (ALMUD-281)

- [ ] 2.1 RED: Create `tests/test_eval/test_oracle.py` asserting the oracle only returns moves present in the legal move set, at depth 3 and depth 4.
- [ ] 2.2 RED: Add determinism tests: identical `(state, depth, seed)` returns the identical move across repeated runs.
- [ ] 2.3 RED: Add tie-break stability tests for equal-valued moves.
- [ ] 2.4 RED: Add tactical fixtures: a forced North capture and a forced South trapping move are found at depth 2 or 3.
- [ ] 2.5 GREEN: Create `src/komikan/eval/oracle.py` with `Move`, `Oracle.choose_move(state)`, negamax, alpha-beta pruning, capture-first ordering, and seeded tie-breaking.
- [ ] 2.6 GREEN: Add a `max_nodes` guard that aborts the search and returns the best move found so far.
- [ ] 2.7 Run `uv run pytest tests/test_eval/test_oracle.py -v`.

## Phase 3: Mirror, OracleOpponent, and Match Runner (ALMUD-283)

- [ ] 3.1 RED: Create `tests/test_eval/test_mirror.py` for `snapshot_from_instance()` against a known `GameInstance`, and for replay parity on a recorded move history.
- [ ] 3.2 RED: Add a mismatch test: when replayed state disagrees with `GET /api/games/{id}`, the mirror raises a clear error instead of returning a wrong state.
- [ ] 3.3 GREEN: Create `src/komikan/eval/mirror.py` with REST replay (uses `GET /api/games/{id}/moves`) and `snapshot_from_instance()` for unit tests.
- [ ] 3.4 RED: Create `tests/test_eval/test_oracle_opponent.py` asserting protocol conformance, exactly one POST per move, and a legal move body.
- [ ] 3.5 GREEN: Create `src/komikan/eval/oracle_opponent.py` implementing the existing `Opponent` protocol (`choose_move() -> dict[str, int]`).
- [ ] 3.6 RED: Create `tests/test_eval/test_runner.py` with fake players asserting pairings (`llm-vs-oracle`, `llm-vs-llm`, `oracle-vs-oracle`, `oracle-vs-random`), side alternation, ply counts, and metric collection.
- [ ] 3.7 GREEN: Create `src/komikan/eval/runner.py` with `MatchRunner`, player adapters, and a per-game `GameResult`.
- [ ] 3.8 Run `uv run pytest tests/test_eval/test_mirror.py tests/test_eval/test_oracle_opponent.py tests/test_eval/test_runner.py -v`.

## Phase 4: Structured Per-Move Logging (ALMUD-284)

- [ ] 4.1 RED: Create `tests/test_eval/test_logging.py` asserting one JSONL record per move with the agreed schema.
- [ ] 4.2 RED: Add tests for legality, oracle preferred move, chosen move, and evaluation delta.
- [ ] 4.3 RED: Add a test that a fallback move is flagged and still logged.
- [ ] 4.4 GREEN: Create `src/komikan/eval/logging.py` with `MatchLogger` appending JSONL records to a configured path.
- [ ] 4.5 GREEN: Wire the logger into the match runner so every move is written before the next one is requested.
- [ ] 4.6 Run `uv run pytest tests/test_eval/test_logging.py -v`.

## Phase 5: Budget Gate (ALMUD-285)

- [ ] 5.1 RED: Create `tests/test_eval/test_sweep.py` asserting the estimated game and call counts for a proposed matrix.
- [ ] 5.2 RED: Add a test that a sweep without `--confirm-budget` is refused.
- [ ] 5.3 GREEN: Create `src/komikan/eval/sweep.py` with sizing math and a confirmation gate.
- [ ] 5.4 GREEN: Record the confirmed sizing in the report header.
- [ ] 5.5 Run `uv run pytest tests/test_eval/test_sweep.py -v`.

## Phase 6: Aggregation, Reporting, and Dashboard (ALMUD-286, ALMUD-287)

- [ ] 6.1 RED: Create `tests/test_eval/test_report.py` asserting the JSON shape, Markdown sections, and Wilson interval bounds for known counts.
- [ ] 6.2 RED: Add tests for win rate by model and config, win rate by side, blunder rate, mean evaluation delta, latency, and fallback rate.
- [ ] 6.3 GREEN: Create `src/komikan/eval/report.py` aggregating the JSONL log and emitting `report.json` and `report.md`.
- [ ] 6.4 RED: Create `tests/test_eval/test_dashboard.py` asserting the HTML contains headline rates, per-model sections, and an eval-delta histogram placeholder.
- [ ] 6.5 GREEN: Create `src/komikan/eval/dashboard.py` emitting one self-contained `dashboard.html` with inline CSS.
- [ ] 6.6 GREEN: Record provider, model, temperature, prompt strategy, seed, and budget sizing in every report header. State that low N is directional only.
- [ ] 6.7 Run `uv run pytest tests/test_eval/test_report.py tests/test_eval/test_dashboard.py -v`.

## Phase 7: Comparative Sweep and CLI (ALMUD-288)

- [ ] 7.1 RED: Create `tests/test_eval/test_cli.py` asserting flag parsing for `--pairing`, `--games`, `--oracle-depth`, `--provider`, `--model`, `--prompt-strategy`, `--seed`, `--out`, `--max-nodes`, and `--confirm-budget`.
- [ ] 7.2 GREEN: Create `src/komikan/eval/cli.py` with `main()` and argparse subcommands for `run`, `report`, `dashboard`, and `budget`.
- [ ] 7.3 Add `komikan-eval = "komikan.eval.cli:main"` to `[project.scripts]` in `pyproject.toml`.
- [ ] 7.4 Implement the `direct` and `cot` prompt strategies in the eval layer without changing the agent's default system prompt.
- [ ] 7.5 Run `uv run komikan-eval --help` and `uv run komikan-eval budget --help`.
- [ ] 7.6 Run a small `random-vs-random` smoke game, then generate the report and dashboard from its log.
- [ ] 7.7 Run the budget-sized comparative sweep across at least two prompting strategies and the models the budget allows. Record the sizing in the report.

## Phase 8: Final Gates

- [ ] 8.1 Run `uv run pytest tests/ -q`.
- [ ] 8.2 Run `uv run ruff check .`.
- [ ] 8.3 Run `uv run ruff format --check .`.
- [ ] 8.4 Confirm every ticket ALMUD-281 to ALMUD-288 has a corresponding acceptance criterion met or explicitly deferred with a note.
