# Komikan Board Game

A Python-based board game built with pygame featuring a 5x8 node grid where two players compete in asymmetric gameplay.

## Game Features

- **5x8 Grid Network**: Game board with 40 nodes connected orthogonally and diagonally
- **Asymmetric Gameplay**: North player (1 token) vs South player (12 tokens)
- **Multiple Movement Types**: Regular moves and capture attacks
- **Visual Feedback**: Player highlighting, coordinate labels, and move validation
- **Dual Input Support**: Both mouse and keyboard controls
- **Debug Logging**: Comprehensive move tracking for replay and analysis

## Quick Start

```bash
# Install dependencies
uv sync

# Run the game
uv run python main.py

# Run with debug logging
KOMIKAN_DEBUG=1 uv run python main.py
```

## Game Rules

### Setup
- **North Player**: 1 token starts at center-top position (2, 0)
- **South Player**: 12 tokens start across bottom two rows (y=6,7)
- **Disabled Nodes**: Positions (0,2) and (4,2) are blocked

### Movement
- **Valid Directions**: Orthogonal (up/down/left/right) and diagonal
- **Path Restrictions**: Some diagonal paths are disabled for strategic balance
- **Turn-based**: Players alternate turns

### Capture Mechanics
- **North Player Only**: Can capture by jumping over south tokens
- **Jump Pattern**: Must land on empty node directly beyond captured token
- **Capture Range**: One token per jump in any valid direction

## Controls

### Mouse Controls
- **Left Click**: Select token or move to highlighted position
- **Right Click**: Deselect current token

### Keyboard Controls
- **WASD/Arrow Keys**: Move selected token orthogonally
- **Q/E or Z/C**: Move selected token diagonally (up-left/up-right or down-left/down-right)
- **ESC**: Deselect token (double ESC within 2 seconds to exit)
- **Auto-selection**: Pressing movement keys automatically selects your active token

## Debug Logging

Enable comprehensive move logging for replay and analysis:

```bash
KOMIKAN_DEBUG=1 uv run python main.py
```

Analyze logs with the included tool:
```bash
python test_logging.py
```

See [DEBUG_LOGGING.md](DEBUG_LOGGING.md) for detailed logging documentation.

## Development

Built with modern Python tooling:
- **Python 3.11**: Core runtime
- **pygame 2.6.1**: Game engine and rendering
- **UV**: Package management and virtual environment
- **Commitizen**: Conventional commits and versioning

### Project Structure
```
main.py              # Game loop and rendering
board.py             # Game board logic and validation
player.py            # Player state and game management
test_logging.py      # Log analysis tool
DEBUG_LOGGING.md     # Logging system documentation
```

### Adding Features
```bash
# Install new dependencies
uv add <package-name>

# Development dependencies
uv add --group dev <package-name>

# Version bump with changelog
cz bump
```

## License

Open source - see project files for details.