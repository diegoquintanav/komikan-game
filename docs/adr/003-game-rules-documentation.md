# ADR-003: Document Komikan Game Rules

## Status

Accepted (completed)

## Context

The Komikan game rules needed to be formally documented in English, sourced from the Spanish rulebook (Chile para Niños) and English Wikipedia reference, to ensure consistent understanding and implementation.

## Decision

Create `docs/GAME_RULES.md` covering:

- **Overview and Origin**: Traditional Mapuche board game from southern Chile
- **Board Setup**: 5×8 node grid, disabled nodes at (0,2) and (4,2), path restrictions
- **Players and Pieces**: North (Pangui/Puma, 1 token) vs South (Pu Trewa/Dogs, 12 tokens)
- **Starting Positions**: North at (2,0); South across bottom rows and flanking columns
- **Movement Rules**: Orthogonal and diagonal movement along valid paths
- **Capture Mechanics**: North captures by jumping over adjacent South tokens
- **Win Conditions**: North captures enough tokens; South surrounds/blocks North
- **Special Rules**: Disabled paths, disabled nodes, turn order

Includes ASCII diagram of initial board layout. Implementation matches `src/komikan/board.py` and `src/komikan/player.py`.

## Consequences

- Single source of truth for game rules
- Consistent implementation across desktop, web, and API interfaces
- New contributors can understand game mechanics from documentation alone
