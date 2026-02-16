# Feature 2: Document Komikan Game Rules

Create a markdown document at `docs/GAME_RULES.md` that describes the rules of the Komikan board game.

## Sources

- Spanish rulebook: https://www.chileparaninos.gob.cl/639/articles-639005_archivo_01.pdf
- English reference: https://en.wikipedia.org/wiki/Komikan

## Requirements

1. Write the rules in English with clear sections covering:
   - **Overview and Origin**: Brief history of Komikan as a traditional Mapuche board game from southern Chile.
   - **Board Setup**: Description of the 5×8 node grid, disabled nodes at (0,2) and (4,2), and path restrictions.
   - **Players and Pieces**: North player (Pangui/Puma) with 1 token vs South player (Pu Trewa/Dogs) with 12 tokens.
   - **Starting Positions**: North at (2,0); South tokens across bottom rows and flanking columns.
   - **Movement Rules**: Orthogonal and diagonal movement along valid paths.
   - **Capture Mechanics**: North player captures by jumping over adjacent South tokens landing on empty nodes.
   - **Win Conditions**: North wins by capturing enough South tokens; South wins by surrounding/blocking North.
   - **Special Rules**: Disabled paths, disabled nodes, turn order.

2. Include a simple ASCII diagram of the initial board layout.

3. Match the implementation in `src/komikan/board.py` and `src/komikan/player.py`.

## Validation

- Verify the documented rules are consistent with the game logic in the codebase.
- Ensure disabled nodes, disabled paths, and capture mechanics match `GameBoard` class constants.
