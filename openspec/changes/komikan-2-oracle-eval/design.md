# Design: Komikan Oracle and Eval Harness (ALMUD-280)

Related ADRs: ADR-004 (REST API), ADR-005 (MCP server, Proposed), ADR-006 (LLM agent integration). This change records the sequencing decision in ADR-007 and builds on the REST contract from ADR-004 and the `Opponent` seam from ADR-006.

## Technical Approach

Add a new `src/komikan/eval/` package that is purely additive to the existing engine and API layers. The oracle searches over an immutable `SearchState` snapshot built from the core `GameBoard`/`Player` model, so move legality comes from `board.py` while the tree search stays side-effect-free. A state mirror reconstructs that snapshot from a live REST game by replaying the move history, with an in-process snapshot path reserved for unit tests. `OracleOpponent` adapts the oracle to the existing `Opponent` protocol so it is drop-in interchangeable with `RandomOpponent` and the LLM agent. A match runner pairs LLM/oracle/random players and collects per-move metrics, and a report module emits JSON and Markdown with a Wilson interval for small sample sizes. All new code follows the repo's TDD pattern (RED then GREEN), uses `uv` for everything, and keeps dependencies to stdlib plus the already-present `httpx`.

## Ticket Alignment

| Ticket | Backlog item | Design coverage |
|--------|--------------|-----------------|
| ALMUD-280 | Define specs using SDD | This document and the change package |
| ALMUD-281 | Minimax oracle with alpha-beta | Oracle search, determinism, move ordering |
| ALMUD-282 | Position evaluation heuristic | Evaluation terms and antisymmetry |
| ALMUD-283 | Match runner with configurable pairings | Runner pairings, side alternation, metrics |
| ALMUD-284 | Structured per-move match logging | Match log schema and blunder inputs |
| ALMUD-285 | Decide sweep scope against budget | Budget gate decision and sizing record |
| ALMUD-286 | Aggregation and reporting layer | Report metrics and Wilson intervals |
| ALMUD-287 | Minimal results dashboard | Static dashboard decision |
| ALMUD-288 | Comparative sweep across models and prompts | Prompting strategies and sweep matrix |

## Architecture Decisions

### Decision: State Mirror Path

| Option | Tradeoff | Decision |
|--------|----------|----------|
| Replay mirror against live REST (replay `GET /api/games/{id}/moves`) | Extra HTTP calls; exercises the real API path under test | **Chosen** - REST path stays under test |
| In-process engine only (build `GameInstance` directly) | Fast; no server; but never tests the live contract | Reserved for unit tests, not the primary path |
| Snapshot directly from `GET /api/games/{id}` | One call; simplest | Rejected - skips the move-history replay the scope requires |

Recommendation: the mirror's primary mode replays the move history (proving the mirror reproduces the server state), then cross-checks against `GET /api/games/{id}` for parity. The in-process path is a thin `snapshot_from_instance()` used only by unit tests.

### Decision: Search State Representation

| Option | Tradeoff | Decision |
|--------|----------|----------|
| Immutable `SearchState` snapshot (frozensets of positions + side to move) | Copy-on-write; no mutation; alpha-beta stays pure | **Chosen** - safe and fast in Python |
| Mutate `GameInstance` with apply/undo | Reuses engine verbatim; fragile undo and history side effects | Rejected - `make_move` appends history and has no undo |
| Deep-copy `GameInstance` per node | Simple; very expensive for depth 4 | Rejected - allocation-bound |

Recommendation: move generation reconstructs a lightweight `GameBoard` from the snapshot and reuses `GameBoard.is_valid_move` / `is_valid_capture` (single source of truth for legality). Applying a move returns a new immutable `SearchState`.

### Decision: Negamax Sign Convention

| Option | Tradeoff | Decision |
|--------|----------|----------|
| Single North-reference score, negated on South's turn | One reference frame; sign flips cleanly | **Chosen** |
| Separate eval per side | No negation; duplicated logic and higher bug risk | Rejected |
| Maximin with explicit min/max branches | Clear; more code than negamax | Rejected - negamax is equivalent and shorter |

Recommendation: compute `raw(state)` = North-perspective utility (positive = good for North), then `evaluate(state) = raw(state)` when North is to move else `-raw(state)`. Terminal scores use the same rule: north_won -> +MATE for North to move, -MATE for South to move; south_won and stalemate mirrored. The terms combine as:

- `south_tokens_remaining`: `-W_MATERIAL * south_count` (fewer dogs is good for North).
- `mobility`: `+W_MOB_N * north_legal_moves - W_MOB_S * south_legal_moves`.
- `capture_availability`: `+W_CAP * north_capture_count`.
- `distance_to_nearest_dog`: `+W_DIST * manhattan_distance(pangui, nearest dog)` (farther is safer for North).
- `escape_square_count`: `+W_ESC * empty_adjacent_squares_around_pangui`.

This yields a single score correct under negamax because it is a fixed North-reference utility negated when South is to move, so `evaluate(state) == -evaluate(flipped(state))` and negamax's `-negamax(child)` stays consistent.

### Decision: Search Depth and Branching Budget

| Option | Tradeoff | Decision |
|--------|----------|----------|
| Default depth 3, opt-in 4 | Cheap per move; weaker | **Chosen** - safe default |
| Default depth 4 | Stronger; roughly 4x more nodes | Opt-in via `--depth` |
| Depth >= 5 | Strong; likely over 1s/move in Python | Rejected for default |

Recommendation: branching factor is about 8 for North (single Pangui, advances + captures) and about 24 for South (12 dogs x ~2-3 moves), average roughly 15. Worst-case nodes are roughly b^depth: depth 3 -> ~3,375 leaves, depth 4 -> ~50,625. Alpha-beta with capture-first ordering reduces the typical node count to about 2*sqrt(b^depth) (~116 at depth 3, ~450 at depth 4), keeping depth 3 and 4 comfortably under a second per move in CPython. Add a `--max-nodes` cap as a hard stop.

### Decision: Move Ordering for Alpha-Beta

| Option | Tradeoff | Decision |
|--------|----------|----------|
| Captures first, then by heuristic score, seeded tie-break | Best cutoffs; small sort cost | **Chosen** |
| No ordering (generation order) | Zero cost; weak pruning | Rejected |
| Full static eval per child as key | Stronger ordering; doubles eval cost | Rejected - not needed at depth 3-4 |

Recommendation: order children captures first (largest immediate swing), then advances keyed by a cheap heuristic (material delta, then mobility delta), with a seeded tie-break so equal moves are stable and deterministic.

### Decision: Determinism and Seeding

| Option | Tradeoff | Decision |
|--------|----------|----------|
| `random.Random(seed)` for tie-break and pairing only | Oracle fully deterministic given (state, depth, seed) | **Chosen** |
| Global RNG | Reproducible only if nobody else consumes it | Rejected - non-local state |
| LLM side also seeded | Impossible; LLM is stochastic | Rejected - record model/temperature/provider instead |

Recommendation: the oracle and random opponent are fully deterministic given (state, depth, seed). The LLM side cannot be seeded, so each run records model, temperature, provider, and seed into the report for reproducibility of the non-LLM side.

### Decision: Cost Control

| Option | Tradeoff | Decision |
|--------|----------|----------|
| Small fixed N default, per-game cost, opt-in sweeps | Cheap, predictable | **Chosen** |
| Large N by default | More signal; can be expensive | Rejected |
| No cost accounting | Simplest; hides spend | Rejected |

Recommendation: default N is small (5 games per pairing). Report cost per game using provider usage when the provider exposes token counts; larger sweeps are opt-in via `--games` and `--depth`.

### Decision: Statistics and Significance

| Option | Tradeoff | Decision |
|--------|----------|----------|
| Raw counts + Wilson 95% interval for rates | Honest at small N; no fake significance | **Chosen** |
| Point estimate + naive confidence interval | Misleading at small N | Rejected |
| Significance tests (t-test etc.) | Needs assumptions and power not met at low N | Rejected |

Recommendation: for each rate (win, stalemate, fallback) report raw counts and a Wilson score interval. Explicitly state in the report that low N is directional only and no significance is claimed.

### Decision: Structured Match Log

| Option | Tradeoff | Decision |
|--------|----------|----------|
| Append-only JSONL, one record per move | Streamable, cheap, survives crashes | **Chosen** |
| In-memory results only | Simplest; loses detail and cannot audit blunders | Rejected |
| One large JSON per game | Easy to read; rewrite cost grows with game length | Rejected - JSONL is simpler to append |

Recommendation: write one JSONL record per move with at least: `game_id`, `pairing`, `game_index`, `ply`, `side`, `provider`, `model`, `temperature`, `prompt_strategy`, `chosen_move`, `legal_move_count`, `is_legal`, `oracle_move`, `oracle_eval`, `chosen_eval`, `eval_delta`, `is_fallback`, `latency_ms`, and `usage` when exposed. The log is the source of truth for the report, so the report can be regenerated without rerunning games.

### Decision: Blunder Definition

| Option | Tradeoff | Decision |
|--------|----------|----------|
| Exact oracle-match rate plus mean eval delta plus threshold blunder rate | Honest, several views of the same data | **Chosen** |
| Exact match only | Too harsh; many near-optimal moves count as failures | Rejected |
| Threshold only | Hides the distribution and depends on arbitrary units | Rejected |

Recommendation: report four numbers: exact-match rate against the oracle move, top-3 match rate, mean evaluation delta, and a blunder rate at a configurable threshold. Define `eval_delta = oracle_eval - chosen_eval` from the side-to-move perspective, so 0 means optimal and positive means worse. Because evaluation units are heuristic, the threshold is configurable and the report always shows the distribution alongside the rate.

### Decision: Budget Gate

| Option | Tradeoff | Decision |
|--------|----------|----------|
| Explicit sizing record plus a required confirmation flag before a sweep | Prevents accidental spend; auditable | **Chosen** |
| Run whatever the flags say | Simple; easy to overspend | Rejected |
| Hard-coded caps only | Safe; inflexible and invisible | Rejected |

Recommendation: `komikan-eval budget` prints the estimated games, calls, and cost for a proposed sweep. The sweep subcommand refuses to run unless `--confirm-budget` is passed with the same sizing. The chosen sizing is written into the report header.

### Decision: Dashboard Format

| Option | Tradeoff | Decision |
|--------|----------|----------|
| Single static HTML file generated from the report JSON, inline CSS | Legible, portable, no dependencies | **Chosen** |
| Notebook | Good for exploration; heavier to reproduce | Optional companion, not the deliverable |
| React frontend page | Polished; violates the "minimal" constraint and couples to the SPA | Rejected |

Recommendation: `komikan-eval dashboard` renders one self-contained HTML file: headline rates with intervals, per-model and per-side tables, and an eval-delta histogram. No server, no JavaScript framework.

### Decision: Prompting Strategies

| Option | Tradeoff | Decision |
|--------|----------|----------|
| `direct` (current tool-call prompt) vs `cot` (ask for a short plan before the tool call) | Clean comparison of one variable | **Chosen** |
| Vary prompt and model together | More coverage per game; confounded results | Rejected |
| Many prompt variants | Rich; exceeds the budget and the project scope | Rejected for the first sweep |

Recommendation: implement the strategy as a prompt-variant field in the eval layer, leaving the agent's default prompt unchanged. When comparing strategies, hold model, temperature, and oracle depth fixed and log the strategy in every record.

## Data Flow

```
komikan-eval CLI
  |
  +-> budget (ALMUD-285)
  |     +-> prints games, calls, and estimated cost for a proposed sweep
  |     +-> sweep refuses to run without --confirm-budget
  |
  +-> MatchRunner (ALMUD-283)
        |
        +-> POST /api/games                 (create game, get game_id)
        |
        +-> loop until terminal:
        |     +-> GET /api/games/{id}                     (state)
        |     +-> current side -> player:
        |     |     LLM:    KomikanAgent.play_turn()      (records usage/latency/fallback)
        |     |     Oracle: StateMirror.replay(game_id)    (replay moves -> SearchState)
        |     |             -> Oracle.choose_move(state)   (negamax, legal only)
        |     |             -> POST /api/games/{id}/moves  (posts chosen move)
        |     |     Random: RandomOpponent.choose_move()   (posts random legal move)
        |     +-> MatchLogger.write(record)                (JSONL, ALMUD-284)
        |
        +-> Aggregator (ALMUD-286)
        |     +-> report.json     (machine-readable)
        |     +-> report.md       (Markdown summary + Wilson intervals)
        |
        +-> Dashboard (ALMUD-287)
              +-> dashboard.html  (single static file, inline CSS)
```

## File Changes

| File | Action | Description |
|------|--------|-------------|
| `src/komikan/eval/__init__.py` | Create | Package init, re-exports public API |
| `src/komikan/eval/evaluation.py` | Create | `SearchState` dataclass, `evaluate(state)` static heuristic |
| `src/komikan/eval/oracle.py` | Create | `Move` dataclass, `Oracle` negamax + alpha-beta, move ordering |
| `src/komikan/eval/mirror.py` | Create | `replay()` REST mirror + `snapshot_from_instance()` in-process path |
| `src/komikan/eval/oracle_opponent.py` | Create | `OracleOpponent` implementing the `Opponent` protocol, posts moves |
| `src/komikan/eval/runner.py` | Create | `MatchRunner`, player adapters, metric collection |
| `src/komikan/eval/report.py` | Create | JSON + Markdown report, Wilson interval |
| `src/komikan/eval/logging.py` | Create | MatchLogger writing append-only JSONL per-move records |
| `src/komikan/eval/sweep.py` | Create | Budget sizing, sweep matrix, and the confirmation gate |
| `src/komikan/eval/dashboard.py` | Create | Static HTML dashboard renderer |
| `src/komikan/eval/cli.py` | Create | argparse CLI, `komikan-eval` entry point |
| `pyproject.toml` | Modify | Add `komikan-eval = "komikan.eval.cli:main"` script |
| `tests/test_eval/test_evaluation.py` | Create | Evaluation and antisymmetry tests |
| `tests/test_eval/test_oracle.py` | Create | Search, legality, determinism, tie-break tests |
| `tests/test_eval/test_mirror.py` | Create | Replay and snapshot parity tests |
| `tests/test_eval/test_oracle_opponent.py` | Create | Protocol conformance and POST behavior tests |
| `tests/test_eval/test_runner.py` | Create | Pairing and metric tests with mocked players |
| `tests/test_eval/test_report.py` | Create | Report shape and Wilson interval tests |
| `tests/test_eval/test_logging.py` | Create | JSONL schema, append behavior, evaluation delta, blunder inputs |
| `tests/test_eval/test_sweep.py` | Create | Budget sizing math and the confirmation gate |
| `tests/test_eval/test_dashboard.py` | Create | Static HTML rendering from a report |
| `tests/test_eval/test_cli.py` | Create | CLI flag parsing and end-to-end tests |
| `docs/adr/007-oracle-and-eval-harness.md` | Create | Sequencing decision record |

## Interfaces / Contracts

### SearchState and Move

```python
from dataclasses import dataclass
from enum import Enum

class Side(str, Enum):
    NORTH = "north"
    SOUTH = "south"

@dataclass(frozen=True)
class SearchState:
    north: frozenset[tuple[int, int]]
    south: frozenset[tuple[int, int]]
    side_to_move: Side

@dataclass(frozen=True)
class Move:
    from_pos: tuple[int, int]
    to_pos: tuple[int, int]
    is_capture: bool = False
    captured_pos: tuple[int, int] | None = None
```

### Evaluation

```python
def evaluate(state: SearchState) -> float:
    """Return a score from the side-to-move's perspective (positive = good)."""
    ...
```

### Oracle

```python
class Oracle:
    def __init__(self, depth: int = 3, seed: int | None = None) -> None: ...

    def choose_move(self, state: SearchState) -> Move | None:
        """Return the best legal move, or None if no legal move exists."""
        ...
```

### Opponent protocol (existing source signature)

```python
class Opponent(Protocol):
    def choose_move(self) -> dict[str, int]: ...   # {"from_x","from_y","to_x","to_y"}
```

### OracleOpponent

```python
class OracleOpponent:
    def __init__(
        self, base_url: str, game_id: str, depth: int = 3, seed: int | None = None
    ) -> None: ...
    def choose_move(self) -> dict[str, int]: ...
```

### Report result shape

```python
@dataclass
class GameResult:
    pairing: str
    result: str                 # north_won | south_won | stalemate
    plies: int
    latencies_ms: list[float]
    illegal_moves: int
    fallbacks: int
    usage: dict[str, int]       # tokens/cost when exposed
```

## Testing Strategy

| Layer | What to Test | Approach |
|-------|-------------|----------|
| Unit | `evaluate()` terms and antisymmetry | Assert `evaluate(s) == -evaluate(flipped(s))` for sampled positions |
| Unit | Oracle returns only legal moves | Enumerate legal moves; assert chosen move is in the set at depth 3 and 4 |
| Unit | Oracle determinism | Same (state, depth, seed) -> identical move across runs |
| Unit | Tie-breaking | Equal-valued moves resolved by seeded order, stable across runs |
| Unit | Mirror replay parity | Replay a game's move history; assert snapshot matches final server state |
| Unit | Mirror in-process path | `snapshot_from_instance()` matches a known GameInstance |
| Unit | OracleOpponent protocol + POST | Assert `choose_move()` returns a legal dict and posts once |
| Unit | Runner pairings and metrics | Mock players; assert result, plies, latency, fallback collected |
| Unit | Report + Wilson interval | Synthetic results; assert rates, counts, and interval bounds |
| Unit | Match log | Assert JSONL schema, one record per move, and correct evaluation delta |
| Unit | Budget gate | Assert sizing math and that a sweep without confirmation is refused |
| Unit | Dashboard | Assert the HTML contains headline rates and per-model sections |
| Integration | CLI end-to-end | `komikan-eval --help`; small random-vs-random run to terminal state |

## Threat Matrix

N/A - the eval harness performs no routing, shell, subprocess, VCS/PR automation, executable-file classification, or process-integration boundary. It reads provider keys from the environment exactly as the existing agent does and makes only the same localhost REST calls.

## Migration / Rollout

Additive only. No existing endpoints or modules change. The new `src/komikan/eval/` package and `tests/test_eval/` are net-new; the only touched existing file is `pyproject.toml` (one console-script line). No data migration. Results are written to local files by the CLI.

## Open Questions

- [x] Linear tickets: ALMUD-280 (this SDD) with ALMUD-281 to ALMUD-288 for the eight implementation items; the mapping is in the Ticket Alignment table.
- [ ] The komikan-1 design documents `get_move(game_id)`, but the source `Opponent` protocol is `choose_move() -> dict[str, int]`. This plan targets the source; confirm a docs-only correction to komikan-1.
- [ ] Default depth 3 (recommended) or 4 (available via `--depth`)?
- [ ] Wilson interval hand-rolled (recommended, no new dependency) or add `scipy`?
- [ ] Runner output: silent by default with an opt-in `--verbose` flag (recommended)?
- [ ] Dashboard: single static HTML file (recommended) or also generate a notebook companion?
- [ ] Chain-of-thought strategy: confirm a prompt variant in the eval layer is acceptable without changing the agent's default system prompt.
