# Random Bot Specification

## Purpose

Deterministic random legal-move opponent for testing the agent. Picks uniformly from all valid moves for the current player.

## Requirements

### Requirement: Random Move Selection

The bot SHALL pick a random move uniformly from the set of all legal moves (regular moves and captures) for the current player.

#### Scenario: Bot has both moves and captures available

- GIVEN a game where the current player (bot) has 3 regular moves and 1 capture
- WHEN the bot selects a move
- THEN exactly one of the 4 options is chosen (uniformly random)

#### Scenario: Bot has only regular moves (South side)

- GIVEN a game where the bot plays South
- WHEN the bot selects a move
- THEN only regular moves are considered (South cannot capture by rule)

### Requirement: Bot Uses Bulk Endpoint

The bot SHALL fetch all valid moves via the bulk `GET /api/games/{game_id}/all-valid-moves` endpoint rather than per-token queries.

#### Scenario: Bot fetches moves in single call

- GIVEN an active game with the bot as current player
- WHEN the bot needs to select a move
- THEN only one HTTP request to all-valid-moves is made per turn

### Requirement: Bot Plays via REST API

The bot SHALL make moves by calling `POST /api/games/{game_id}/moves` through the API, not by manipulating game state directly.

#### Scenario: Bot move goes through API validation

- GIVEN the bot selects a move
- WHEN the bot submits it via the moves endpoint
- THEN the move is validated by the API and returns success

### Requirement: Bot Implements LLMProvider-compatible Interface

The bot SHALL implement the same interface the agent expects from an opponent, accepting game context and returning a move.

#### Scenario: Bot is interchangeable with human opponent

- GIVEN an agent expecting an opponent that returns moves
- WHEN the bot is used as the opponent
- THEN the agent game loop runs identically to human opponent mode
