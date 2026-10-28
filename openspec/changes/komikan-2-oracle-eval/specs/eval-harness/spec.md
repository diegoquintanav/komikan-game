# Eval Harness Specification

## Purpose

Run head-to-head matches, collect metrics, and report results honestly at small sample sizes.

## Requirements

### Requirement: Supported Pairings

The system SHALL run `llm-vs-oracle`, `llm-vs-llm`, `oracle-vs-oracle`, `oracle-vs-random`, and `random-vs-random` pairings for a configurable number of games.

#### Scenario: Pairing reaches terminal state

- GIVEN a configured pairing and a running backend
- WHEN the runner executes a game
- THEN the game reaches a terminal status and a result is recorded

#### Scenario: Sides alternate

- GIVEN more than one game in a pairing
- WHEN games are scheduled
- THEN each player takes each side roughly equally

### Requirement: Metric Collection

The system SHALL record per-game and per-move metrics.

#### Scenario: Metrics recorded per game

- GIVEN a completed game
- WHEN the result is stored
- THEN it contains result, plies, per-move latency, illegal-move count, fallback count, oracle agreement, mean evaluation delta, and usage when available

#### Scenario: Metrics grouped for reporting

- GIVEN results across models, prompt strategies, and sides
- WHEN the results are aggregated
- THEN win rate can be grouped by model, by configuration, and by side

### Requirement: Honest Report

The system SHALL emit JSON and Markdown reports with raw counts, rates, Wilson intervals, and run metadata.

#### Scenario: Report includes intervals

- GIVEN a set of game results
- WHEN the report is generated
- THEN win, stalemate, and fallback rates include Wilson 95 percent intervals

#### Scenario: Low N is labeled directional

- GIVEN fewer than 20 games
- WHEN the report is generated
- THEN it states that results are directional and no significance is claimed

### Requirement: CLI Entry Point

The system SHALL expose `komikan-eval` and `python -m komikan.eval`.

#### Scenario: Help output

- GIVEN the package is installed
- WHEN `uv run komikan-eval --help` runs
- THEN it exits zero and lists the pairing, games, depth, provider, model, prompt strategy, seed, output, max-nodes, and budget flags

### Requirement: Minimal Dashboard

The system SHALL render a self-contained static dashboard from the report.

#### Scenario: Dashboard is generated

- GIVEN a report JSON
- WHEN the dashboard command runs
- THEN it writes one HTML file with inline CSS and no external dependencies

#### Scenario: Dashboard summarizes results

- GIVEN a generated dashboard
- WHEN opened
- THEN it shows headline rates with intervals, per-model and per-side tables, and an evaluation-delta distribution
