# Bulk Valid Moves Specification

## Purpose

Single-call endpoint returning all legal moves for the current player, eliminating the need for per-token queries when an agent needs the full move space.

## Requirements

### Requirement: Bulk Valid Moves Endpoint

The system SHALL expose `GET /api/games/{game_id}/all-valid-moves` returning every legal move and capture for the current player in one response.

#### Scenario: Happy path — active game with multiple tokens

- GIVEN an active game with game_id
- WHEN GET /api/games/{game_id}/all-valid-moves is called
- THEN the response contains a list of token entries, each with `from` position, `moves` (list of destination positions), and `captures` (list of [to, captured] pairs)
- AND the response status is 200

#### Scenario: Game not found

- GIVEN no game exists with game_id "nonexistent"
- WHEN GET /api/games/nonexistent/all-valid-moves is called
- THEN the response status is 404 with error detail "Game nonexistent not found"

#### Scenario: Game already over

- GIVEN a game with status "north_won" or "south_won" or "stalemate"
- WHEN GET /api/games/{game_id}/all-valid-moves is called
- THEN the response status is 400 with error detail containing "Game is already over"

#### Scenario: Current player has no valid moves

- GIVEN an active game where the current player has zero legal moves (stalemate condition)
- WHEN GET /api/games/{game_id}/all-valid-moves is called
- THEN the response contains an empty list of tokens

#### Scenario: North player with capture options

- GIVEN an active game where North has a token adjacent to a South token with an empty landing behind it
- WHEN GET /api/games/{game_id}/all-valid-moves is called
- THEN North's token entry includes both regular moves and captures in its response

#### Scenario: South player never has captures

- GIVEN an active game where it is South's turn
- WHEN GET /api/games/{game_id}/all-valid-moves is called
- THEN no token entry contains captures (South cannot capture by rule)
