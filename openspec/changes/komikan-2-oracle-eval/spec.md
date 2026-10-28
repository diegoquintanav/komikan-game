# Delta for komikan-2-oracle-eval

## ADDED Requirements

### Requirement: Deterministic Position Evaluation

The system SHALL provide a static evaluation function over an immutable board snapshot that is deterministic and antisymmetric under side-to-move flips.

#### Scenario: Repeated evaluation is identical

- GIVEN a board snapshot with a side to move
- WHEN the evaluation function is called twice on the same snapshot
- THEN both calls return the same numeric score

#### Scenario: Antisymmetry under side-to-move flip

- GIVEN a board snapshot `s` and its side-to-move flip `flipped(s)`
- WHEN both are evaluated
- THEN `evaluate(s)` equals `-evaluate(flipped(s))`

#### Scenario: Material term rewards captured dogs

- GIVEN two otherwise identical snapshots where one has fewer South tokens
- WHEN both are evaluated from North's perspective
- THEN the snapshot with fewer South tokens scores higher for North

### Requirement: Oracle Returns Only Legal Moves

The system SHALL provide a negamax oracle with alpha-beta pruning that returns a move from the current legal move set, or None when no legal move exists.

#### Scenario: Oracle move is legal

- GIVEN a non-terminal snapshot with at least one legal move
- WHEN the oracle searches at depth 3 or 4
- THEN the returned move is present in the legal move set for that snapshot

#### Scenario: Oracle returns None on a terminal position

- GIVEN a snapshot where the side to move has no legal moves
- WHEN the oracle is asked to choose a move
- THEN it returns None

#### Scenario: Forced capture is found

- GIVEN a snapshot where North has an immediate capture and no better alternative at depth 2
- WHEN the oracle searches at depth 2 or greater
- THEN it returns the capture move

### Requirement: Oracle Determinism

The system SHALL produce identical moves for identical inputs, with tie-breaking controlled by an explicit seed.

#### Scenario: Same inputs, same move

- GIVEN a snapshot, a depth, and a seed
- WHEN the oracle chooses a move repeatedly
- THEN every run returns the same move

#### Scenario: Equal-valued moves are stable

- GIVEN a snapshot with two moves of equal search value
- WHEN the oracle chooses a move with the same seed across runs
- THEN the same tied move is selected every time

### Requirement: State Mirror Reproduces Server State

The system SHALL reconstruct a local searchable state by replaying the move history of a live REST game, and SHALL fail loudly when the reconstruction disagrees with the server state.

#### Scenario: Replay matches the server

- GIVEN an active game with a recorded move history
- WHEN the mirror replays the history and compares the result with `GET /api/games/{id}`
- THEN positions, side to move, and status match

#### Scenario: Mismatch aborts the search

- GIVEN a replayed state that disagrees with the server state
- WHEN the mirror completes the replay
- THEN it raises a clear error and does not return a searchable state

#### Scenario: In-process snapshot for tests

- GIVEN an in-memory game instance
- WHEN `snapshot_from_instance()` is called
- THEN the returned snapshot matches the instance positions and side to move

### Requirement: Oracle Opponent Conforms to the Opponent Protocol

The system SHALL adapt the oracle to the existing `Opponent` protocol so it is interchangeable with the random opponent and the LLM agent.

#### Scenario: Protocol conformance

- GIVEN an `OracleOpponent` instance
- WHEN checked against the `Opponent` protocol
- THEN it satisfies `choose_move() -> dict[str, int]`

#### Scenario: Exactly one move is posted

- GIVEN an active game with a legal move for the side to move
- WHEN `choose_move()` is called
- THEN exactly one POST to the moves endpoint occurs with a legal body

### Requirement: Match Runner and Metrics

The system SHALL run configurable head-to-head matches and collect per-game and per-move metrics.

#### Scenario: Supported pairings run to terminal state

- GIVEN a pairing of `llm-vs-oracle`, `oracle-vs-random`, or `random-vs-random`
- WHEN the runner executes a game
- THEN the game reaches a terminal status and a result is recorded

#### Scenario: Sides alternate across games

- GIVEN a configured number of games greater than one
- WHEN the runner schedules them
- THEN each player takes each side roughly equally

#### Scenario: Metrics are collected

- GIVEN a completed game
- WHEN the result is recorded
- THEN it includes result, plies, per-move latency, illegal-move count, fallback count, and usage when the provider exposes it

### Requirement: Report With Honest Statistics

The system SHALL emit JSON and Markdown reports that include raw counts, rates, Wilson score intervals, per-model and per-side breakdowns, blunder metrics, and run metadata.

#### Scenario: Report contains rates and intervals

- GIVEN a set of game results
- WHEN the report is generated
- THEN it contains win, stalemate, and fallback rates with Wilson 95 percent intervals

#### Scenario: Breakdowns by model, config, and side

- GIVEN results from more than one model or prompt strategy
- WHEN the report is generated
- THEN it contains win rates grouped by model, by configuration, and by side

#### Scenario: Blunder metrics are present

- GIVEN structured per-move logs
- WHEN the report is generated
- THEN it contains exact oracle-match rate, top-3 match rate, mean evaluation delta, and a threshold blunder rate

#### Scenario: Run metadata is recorded

- GIVEN a run that used a specific provider, model, temperature, seed, and oracle depth
- WHEN the report is generated
- THEN those values appear in the report header

#### Scenario: Low N is labeled directional

- GIVEN a run with fewer than 20 games
- WHEN the report is generated
- THEN it states that the results are directional and no significance is claimed

### Requirement: CLI Entry Point

The system SHALL expose an eval CLI discoverable as `komikan-eval` and as `python -m komikan.eval`.

#### Scenario: Help output lists flags

- GIVEN the package is installed
- WHEN `uv run komikan-eval --help` runs
- THEN it exits zero and lists pairing, games, depth, provider, model, seed, output, and max-nodes flags

#### Scenario: Runnable smoke pairing

- GIVEN a running backend
- WHEN the CLI runs a small `random-vs-random` pairing
- THEN it writes the report files and exits zero

### Requirement: Structured Match Log

The system SHALL write one append-only JSONL record per move, including legality, the oracle preferred move, and the evaluation delta.

#### Scenario: One record per move

- GIVEN a game in progress
- WHEN a move is completed
- THEN exactly one JSONL record is appended with the agreed schema

#### Scenario: Blunder inputs are logged

- GIVEN a completed move
- WHEN the record is written
- THEN it contains the chosen move, the oracle move, both evaluations, and the evaluation delta

#### Scenario: Fallbacks are visible

- GIVEN a move that fell back to a random legal move
- WHEN the record is written
- THEN the record is flagged as a fallback and still contains the move

### Requirement: Budget Gate

The system SHALL estimate the size and cost of a proposed sweep and SHALL refuse to run a sweep without explicit confirmation.

#### Scenario: Budget estimate is available

- GIVEN a proposed matrix of models, strategies, and games
- WHEN the budget command runs
- THEN it prints the game count, call estimate, and cost estimate

#### Scenario: Unconfirmed sweep is refused

- GIVEN a sweep request without the confirmation flag
- WHEN the sweep command runs
- THEN it exits non-zero without creating games

#### Scenario: Confirmed sizing is recorded

- GIVEN a confirmed sweep
- WHEN the report is generated
- THEN the confirmed sizing appears in the report header

### Requirement: Minimal Dashboard

The system SHALL generate a self-contained static page summarizing the report.

#### Scenario: Static dashboard is generated

- GIVEN a report JSON
- WHEN the dashboard command runs
- THEN it writes one HTML file with inline CSS and no external dependencies

#### Scenario: Dashboard shows headline results

- GIVEN a generated dashboard
- WHEN opened
- THEN it shows headline rates with intervals, per-model and per-side tables, and an evaluation-delta distribution

### Requirement: Comparative Sweep

The system SHALL compare at least two prompting strategies while holding the model and search depth fixed.

#### Scenario: Two strategies are compared

- GIVEN a confirmed sweep budget
- WHEN the sweep runs
- THEN it executes `direct` and `cot` strategies for the configured models

#### Scenario: Strategy is recorded

- GIVEN a sweep result
- WHEN the record is written
- THEN the prompt strategy appears in the per-move log and the report
