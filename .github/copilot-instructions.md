# Copilot Instructions for Komikan Game

## Project Overview

Komikan is a traditional Mapuche board game (hunt game) where one player controls a **Pangui** (Puma, 1 token) and the other controls **Pu Trewa** (Dogs, 12 tokens) on a 5×8 node grid. North (Pangui) captures by jumping; South (Pu Trewa) wins by surrounding and trapping. See `docs/GAME_RULES.md` for full rules.

## Roadmap

This project is being incrementally converted into an MCP server. The roadmap is in `agent-roadmap/` with numbered prompt files. Each file contains instructions for a feature and can be used with `gh agent-task create -F agent-roadmap/<file>.md`. Follow features sequentially.

## Tech Stack

- **Python 3.11** (`.python-version`) — core runtime
- **UV** — package manager (use `uv sync`, `uv add`, `uv run`)
- **pygame 2.6.1** — game rendering (original interface)
- **Ruff** — linter and formatter
- **pytest** — test framework (71 tests)
- **Commitizen** — conventional commits and versioning
- **Pre-commit hooks** — commit message standards and code quality

## Project Structure

```
src/komikan/
├── __init__.py
├── run.py           # Pygame entry point and Game class
├── board.py         # GameBoard (5×8 grid), Node, movement/capture validation
└── player.py        # Player, PlayerSide enum, GameState
tests/
├── conftest.py      # Shared fixtures (empty_board, board_with_players, etc.)
├── test_board.py    # Node and board mechanics
├── test_player.py   # Player and game state
├── test_integration.py  # Full gameplay scenarios
├── test_performance.py  # Performance and memory tests
└── test_example.py  # Testing patterns template
docs/
└── GAME_RULES.md    # Full game rules documentation
agent-roadmap/       # Incremental feature prompts for MCP conversion
pyproject.toml       # Project config, dependencies, scripts
pytest.ini           # Test configuration and custom markers
.cz.toml             # Commitizen config (PEP 440 versioning)
.pre-commit-config.yaml  # Ruff + commitizen hooks
```

## Essential Commands

```bash
# Setup
uv sync                          # Install all dependencies

# Run
uv run python -m komikan     # Run the pygame game
KOMIKAN_DEBUG=1 uv run python -m komikan  # Run with debug logging

# Test
uv run pytest tests/ -v          # Run all tests
uv run pytest tests/test_board.py -v  # Run specific test file
uv run pytest -m "not performance"    # Skip performance tests

# Lint & Format
uv run ruff check .              # Lint
uv run ruff format .             # Format

# Dependencies
uv add <package>                 # Add runtime dependency
uv add --group dev <package>     # Add dev dependency

# Version
cz bump                          # Bump version with changelog
```

## Coding Guidelines

1. **Commits**: Use conventional commit format (`feat:`, `fix:`, `docs:`, `refactor:`, `test:`).
2. **Dependencies**: Always use `uv add`, never `pip install`.
3. **Code style**: Ruff enforces formatting and linting. Run `uv run ruff check .` and `uv run ruff format .` before committing.
4. **Tests**: Add tests in `tests/` using fixtures from `conftest.py`. Follow existing patterns in `test_example.py`.
5. **Game logic**: Core logic lives in `board.py` (movement, capture, validation) and `player.py` (state). Keep rendering separate from logic.
6. **Type hints**: Use Python type hints consistently (see existing code for patterns).
7. **Logging**: Use `KOMIKAN_DEBUG=1` env var; never add print statements to production code.

## Agent Update Reflection

- **Purpose:** When this file is edited, the Copilot agent MUST evaluate whether the change requires code modifications or other repository edits.
- **If code changes are required:** the agent should make the edits (using the workspace), run or suggest running tests when feasible, and include an explicit report in its final message: `Applies to code: Yes` followed by a short list of modified files (workspace-relative links).
- **If no code changes are required:** the agent should state `Applies to code: No` in its final message.
- **Tracking:** For multi-step tasks invoked because of these instructions, the agent MUST start with the todo list tool and keep it updated until completion.

## Key Game Constants (in `board.py`)

- Board: 5 wide × 8 tall
- Disabled nodes: `{(0, 2), (4, 2)}`
- Disabled paths: Multiple diagonal restrictions (see `GameBoard.DISABLED_PATHS`)
- North starts at `(2, 0)`, South has 12 tokens at rows 5–7

## Test Markers

- `@pytest.mark.slow` — long-running tests
- `@pytest.mark.integration` — integration tests
- `@pytest.mark.performance` — performance benchmarks