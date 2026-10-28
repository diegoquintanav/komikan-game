# Match Logging Specification

## Purpose

Append-only structured records of every move so results can be audited, blunders can be measured, and reports can be regenerated without rerunning games.

## Requirements

### Requirement: One JSONL Record Per Move

The system SHALL append exactly one JSON object per completed move to a JSONL file.

#### Scenario: Record appended per move

- GIVEN a game in progress with logging enabled
- WHEN a move completes
- THEN exactly one line is appended and the file remains valid JSONL

#### Scenario: Required fields are present

- GIVEN a completed move
- WHEN the record is written
- THEN it contains game id, pairing, game index, ply, side, provider, model, temperature, prompt strategy, chosen move, legal move count, legality, oracle move, oracle evaluation, chosen evaluation, evaluation delta, fallback flag, and latency

### Requirement: Blunder Inputs

The system SHALL record the oracle preferred move and both evaluations so the report can compute agreement and evaluation delta.

#### Scenario: Evaluation delta is recorded

- GIVEN a move where the oracle prefers a different move
- WHEN the record is written
- THEN `eval_delta` equals the oracle evaluation minus the chosen evaluation from the side-to-move perspective

### Requirement: Fallback Visibility

The system SHALL flag moves that fell back to a random legal move.

#### Scenario: Fallback is flagged

- GIVEN a move produced by the random fallback path
- WHEN the record is written
- THEN the record is marked as a fallback and retains the chosen move

### Requirement: Append-Only Durability

The system SHALL never rewrite earlier records for a run.

#### Scenario: Partial trailing line

- GIVEN a log with a truncated final line from a crash
- WHEN the report is generated
- THEN the truncated line is skipped and earlier records remain valid
