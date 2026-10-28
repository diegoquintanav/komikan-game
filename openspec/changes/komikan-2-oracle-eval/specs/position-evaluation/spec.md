# Position Evaluation Specification

## Purpose

Deterministic static scoring of a Komikan position so the oracle can compare leaves without mutating engine state.

## Requirements

### Requirement: Deterministic Evaluation

The system SHALL compute a numeric score for an immutable `SearchState` that depends only on the snapshot.

#### Scenario: Same snapshot, same score

- GIVEN one immutable snapshot
- WHEN `evaluate(state)` is called repeatedly
- THEN every call returns the same score

### Requirement: Antisymmetry Under Side Flip

The system SHALL express the score from the side-to-move perspective so negamax can negate it.

#### Scenario: Flipping the side negates the score

- GIVEN a snapshot `s` and its side-to-move flip `flipped(s)`
- WHEN both are evaluated
- THEN `evaluate(s) == -evaluate(flipped(s))`

### Requirement: Evaluation Terms

The system SHALL combine material, mobility, capture availability, distance to the nearest dog, and escape-square count with fixed weights.

#### Scenario: Material dominates equal mobility

- GIVEN two snapshots with equal mobility but different South token counts
- WHEN evaluated from North's perspective
- THEN fewer South tokens scores higher for North

#### Scenario: Mobility contributes

- GIVEN two otherwise identical snapshots where North has more legal moves in one
- WHEN both are evaluated
- THEN the higher-mobility snapshot scores higher for North
