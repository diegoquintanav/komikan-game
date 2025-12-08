# Copilot Instructions for Komikan Game

## Project Overview
This is a Python-based board game project called "komikan-game" built with pygame and modern Python tooling. The game features a 5x8 node grid where two players start on opposite sides (north/south) and can move orthogonally and diagonally. The project focuses on clean development practices and modular game architecture.

## Development Environment Setup

### Python Environment
- **Python Version**: 3.11 (specified in `.python-version`)
- **Package Manager**: UV (modern Python package manager)
- **Virtual Environment**: `.venv/` (managed by UV)

### Key Commands
```bash
# Install dependencies
uv sync

# Run the game
python main.py
# or
uv run python main.py

# Install new packages
uv add <package-name>

# Dev dependencies
uv add --group dev <package-name>
```

## Project Structure & Conventions

### Architecture
- **Entry Point**: `main.py` - Pygame game loop and initialization
- **Game Logic**: Modular classes for board, players, and game state
- **Board System**: 5x8 node grid with orthogonal and diagonal movement
- **Player System**: Two-player turn-based mechanics
- **Configuration**: `pyproject.toml` - Modern Python project configuration using UV
- **Dependencies**: Managed through `uv.lock` for reproducible builds

### Development Workflow
- **Git Hooks**: Pre-commit hooks configured via `.pre-commit-config.yaml`
- **Commit Standards**: Uses Commitizen for conventional commits
  - Configuration in `.cz.toml`
  - Enforces conventional commit format
  - Automatic changelog generation on version bumps
- **Version Management**: Uses semantic versioning with PEP 440 scheme

### Code Quality Setup
- Pre-commit hooks enforce commit message standards
- Commitizen integration for automated versioning
- VS Code workspace has custom color theme (purple/pink themed)

## Development Patterns

### Adding New Features
1. Use conventional commit messages (feat:, fix:, etc.)
2. Install dependencies via `uv add` rather than pip
3. Follow the existing simple module structure in `main.py`

### Version Management
- Use `cz bump` for version updates
- Changelog automatically updated on version bumps
- Tags follow `$version` format

### Dependencies
- Runtime dependencies go in main `dependencies` array (pygame for game engine)
- Development tools go in `[dependency-groups.dev]`
- Currently includes commitizen for development workflow

### Game Architecture
- **Board**: 5x8 grid of nodes (40 total positions)
- **Players**: Start on north/south edges, move orthogonally and diagonally
- **Movement**: Valid moves to adjacent nodes in all 8 directions
- **Turn System**: Alternating player turns with move validation

## Important Files
- `main.py`: Application entry point
- `pyproject.toml`: Project configuration and dependencies
- `uv.lock`: Lock file for reproducible dependency installation
- `.cz.toml`: Commitizen configuration for conventional commits
- `.pre-commit-config.yaml`: Git hooks configuration

## VS Code Configuration
- Custom workspace colors (purple theme) in `.vscode/settings.json`
- Whitespace visualization configured for better code readability