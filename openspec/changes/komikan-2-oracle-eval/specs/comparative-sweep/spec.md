# Comparative Sweep Specification

## Purpose

Compare prompting strategies and models within an explicit API and compute budget, without over-promising statistical rigor.

## Requirements

### Requirement: Budget Estimate

The system SHALL estimate the number of games, provider calls, and cost of a proposed sweep before it runs.

#### Scenario: Estimate is printed

- GIVEN a matrix of models, prompt strategies, games, and oracle depth
- WHEN the budget command runs
- THEN it prints the game count, call estimate, and cost estimate

### Requirement: Confirmation Gate

The system SHALL refuse to run a sweep without explicit confirmation of the sizing.

#### Scenario: Missing confirmation

- GIVEN a sweep request without the confirmation flag
- WHEN the sweep command runs
- THEN it exits non-zero and creates no games

#### Scenario: Confirmed sizing matches the estimate

- GIVEN a confirmed sweep
- WHEN it starts
- THEN the executed matrix matches the confirmed sizing

### Requirement: Controlled Comparison

The system SHALL compare at least two prompt strategies while holding model, temperature, and oracle depth fixed.

#### Scenario: Direct versus chain-of-thought

- GIVEN a confirmed sweep with two strategies
- WHEN the sweep runs
- THEN each strategy runs against the same models and depth

#### Scenario: Strategy is attributable

- GIVEN a sweep result
- WHEN the log and report are inspected
- THEN the prompt strategy is recorded on every move and in every aggregate

### Requirement: Sizing Recorded

The system SHALL record the confirmed budget sizing in the report.

#### Scenario: Sizing in the report header

- GIVEN a completed sweep
- WHEN the report is generated
- THEN the models, strategies, games per pairing, and estimated cost appear in the header
