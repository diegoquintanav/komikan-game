# Oracle Opponent Specification

## Purpose

Adapter that lets the oracle play in the existing game loop through the `Opponent` protocol.

## Requirements

### Requirement: Protocol Conformance

The system SHALL implement the existing `Opponent` protocol.

#### Scenario: Structural conformance

- GIVEN an `OracleOpponent` instance
- WHEN checked against `Opponent`
- THEN it satisfies `choose_move() -> dict[str, int]`

### Requirement: Single Move Post

The system SHALL post exactly one move per `choose_move()` call and return that move.

#### Scenario: One POST per move

- GIVEN an active game with a legal move
- WHEN `choose_move()` is called
- THEN exactly one POST to the moves endpoint occurs with a legal body

#### Scenario: No legal move

- GIVEN a game where the side to move has no legal move
- WHEN `choose_move()` is called
- THEN it raises a clear error and performs no POST
