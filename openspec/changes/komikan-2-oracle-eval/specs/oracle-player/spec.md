# Oracle Player Specification

## Purpose

Legal, deterministic move selection for the eval harness using negamax search with alpha-beta pruning.

## Requirements

### Requirement: Legal Move Selection

The system SHALL return a move from the legal move set for the current snapshot, or None when no legal move exists.

#### Scenario: Legal move returned

- GIVEN a non-terminal snapshot with at least one legal move
- WHEN the oracle searches at the configured depth
- THEN the returned move belongs to the legal move set

#### Scenario: Terminal snapshot

- GIVEN a snapshot with no legal move for the side to move
- WHEN the oracle chooses a move
- THEN it returns None

### Requirement: Negamax With Alpha-Beta

The system SHALL search with negamax and alpha-beta pruning, capture-first move ordering, and a configurable depth.

#### Scenario: Forced capture is found

- GIVEN a snapshot where North has an immediate capture and no better alternative at depth 2
- WHEN the oracle searches at depth 2 or greater
- THEN it returns the capture move

#### Scenario: Node cap stops the search

- GIVEN a `max_nodes` limit lower than the full tree size
- WHEN the oracle searches
- THEN it stops at the cap and returns the best move found so far

### Requirement: Determinism

The system SHALL return identical moves for identical `(state, depth, seed)` inputs.

#### Scenario: Repeated runs agree

- GIVEN the same snapshot, depth, and seed
- WHEN the oracle runs multiple times in one process or across processes
- THEN the chosen move is identical

#### Scenario: Ties are stable

- GIVEN two moves of equal search value
- WHEN the same seed is used across runs
- THEN the same tied move is selected
