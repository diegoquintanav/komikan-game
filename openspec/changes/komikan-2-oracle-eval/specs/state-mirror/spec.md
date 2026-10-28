# State Mirror Specification

## Purpose

Reconstruct a searchable local state from a live REST game so the oracle searches against the same position the server holds.

## Requirements

### Requirement: Replay Parity

The system SHALL rebuild a snapshot by replaying the game move history from `GET /api/games/{id}/moves`.

#### Scenario: Replay matches the server

- GIVEN an active game with at least one recorded move
- WHEN the mirror replays the history
- THEN the resulting positions, side to move, and status match `GET /api/games/{id}`

### Requirement: Fail Loudly on Mismatch

The system SHALL raise a clear error when replay disagrees with the server state instead of returning a wrong snapshot.

#### Scenario: Divergence aborts

- GIVEN a replayed state that disagrees with the server
- WHEN the mirror completes the replay
- THEN it raises an error naming the mismatched fields and returns no snapshot

### Requirement: In-Process Snapshot Path

The system SHALL provide `snapshot_from_instance()` for unit tests that does not require HTTP.

#### Scenario: Snapshot from a known instance

- GIVEN an in-memory `GameInstance`
- WHEN `snapshot_from_instance()` is called
- THEN the snapshot matches the instance positions and side to move
