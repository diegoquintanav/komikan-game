# AGENTS.md

## What this repo is

Komikan is a traditional Mapuche hunt game. The repo has three layers:

- **Core game logic** — Python package (`src/komikan/`): `board.py` (5×8 grid, movement/capture), `player.py` (state, PlayerSide enum)
- **FastAPI REST backend** — `src/komikan/api/` (in-memory game sessions, Pydantic v2 models)
- **React SPA frontend** — `frontend/` (React 19, TypeScript 5.9, Tailwind v4, Vite 8 beta)

The copilot-instructions file (`.github/copilot-instructions.md`) covers the Python/pygame side well. The sections below focus on gaps and the web stack.

---

## Language conventions

* Use english for all code, comments, and documentation, unless told otherwise
* Don't use non-ASCII characters in code, comments, or documentation unless told otherwise
* Use skills for testing your writing style against common AI style patterns (e.g., "avoid AI style" skill) to ensure your writing is human-like and not AI-generated

---

## Project management and specification conventions

* This project uses [Linear](https://linear.app/) for issue tracking. All issues must be linked to a Linear ticket (e.g., ALMUD-123) in the commit message. 
* The linear initiative for this project is <https://linear.app/almudata/initiative/komikan-game-66e620fd3b3e/overview>
* This project uses [OpenSpec](https://openspec.org) as its default Specification framework

--- 

## Pull requests workflow

- A merge request must be linked to a Linear ticket and must reference the ticket in the PR description.
- All PRs must pass CI checks (backend + frontend) before merging.
- All PRs must be reviewed and approved by at least one other developer before merging.

---

## Commit conventions

* This project uses [commitizen](https://commitizen-tools.github.io/commitizen/) for changelog generation and versioning. All commits must follow Conventional Commits format as configured in `.cz.toml`.
* **Accepted types**: `feat`, `fix`, `docs`, `test`, `ci`, `refactor`, `perf`, `chore`, `style`, `build`
* **Scope** is optional. Example: `feat(api): add game session timeout`
* **Semver mapping**: `feat` → MINOR, `fix`/`refactor`/`perf` → PATCH (major version is locked at 0.x)
* **Bump auto-detection**: `cz bump` infers the increment from commit types since the last tag. No manual increment argument is required (but `--increment` can override).
* All branches must follow the naming convention: `<github-username>/<ticket-number>-<short-description>` (e.g., `diegoquintanav/ALMUD-123-add-new-feature`).
* All pull requests must be linked to a Linear ticket and must reference the ticket in the PR description.

---

## Releases conventions

* This project uses [commitizen](https://commitizen-tools.github.io/commitizen/) for changelog generation and versioning. All releases must follow the conventions in the `.cz.toml` file.
* All releases must be tagged with a version number in the format `vX.Y.Z` (e.g., `v0.1.0`).

### Version file and sync locations

`VERSION` is the source of truth. `cz bump` syncs it to three places:
- `VERSION` — plain text file
- `frontend/package.json` — `"version"` field
- `src/komikan/__init__.py` — `__version__` string

Always edit `VERSION` directly or use `cz bump`. Never edit the other two files manually.

### Release workflow

1. Ensure all changes are committed and pushed to `main`
2. Bump version: `./scripts/bump-version.sh patch` (or `minor`, `major`, `release`)
   - This runs `cz bump --changelog` which:
     - Auto-detects increment from commit types since last tag
     - Regenerates `CHANGELOG.md` using the custom Jinja2 template
     - Runs `pre_bump_hooks` (converts `#N` references to PR links)
     - Updates `VERSION`, `package.json`, and `__init__.py`
     - Creates a git commit with message `bump: version X.Y.Z → A.B.C`
     - Creates a `vX.Y.Z` tag
   - The `release` argument also pushes the commit and tag
3. CI (`.github/workflows/release.yml`) creates a GitHub Release from the tag

### Changelog customization

- **Template**: `CHANGELOG.md.jinja2` renders every entry with a clickable GitHub commit hash link
- **PR linking**: `scripts/link-changelog.py` is a pre-bump hook that converts bare `#N` references in commit messages to GitHub pull request links
- **Makefile**: `make changelog` regenerates the changelog and runs the linking script
- CZ pre_bump_hooks run **only** during `cz bump --changelog`, not during standalone `cz changelog`

---

## Package manager: always `uv`, never `pip`

```bash
uv sync                        # install all deps (respects .python-version → 3.11)
uv add <pkg>                   # add runtime dep
uv add --group dev <pkg>       # add dev dep
uv run <cmd>                   # run any command in the venv
```

Build backend is `uv_build`; do not change it to setuptools/hatchling.

---

## Commands

### Python / backend

```bash
uv run python -m komikan                          # pygame desktop app
KOMIKAN_DEBUG=1 uv run python -m komikan          # with debug logging
uv run komikan-api                                # FastAPI dev server (port 8000)
# or explicitly:
uv run python -m uvicorn komikan.api.main:app --reload --host 0.0.0.0 --port 8000

uv run pytest tests/ -v                           # all tests (220 pass)
uv run pytest tests/test_board.py::TestBoardCapture -v   # single class
uv run pytest tests/test_api.py::test_create_game -v     # single function
uv run pytest -m "not performance"                # skip slow benchmarks
uv run pytest tests/ --cov=komikan --cov-report=html

uv run ruff check .                               # lint
uv run ruff check --fix .                         # lint + auto-fix
uv run ruff format .                              # format
```

### Frontend

```bash
cd frontend
npm install
npm run dev        # Vite dev server → http://localhost:5173
npm run build      # tsc type-check + production build
npm run lint       # ESLint
npm run preview    # preview production build
```

### Full stack

```bash
docker compose up  # backend :8000, frontend :5173, API docs :8000/docs
```

### Version management and releases

```bash
make changelog                          # regenerate CHANGELOG.md + add PR links
make bump-patch                         # 0.1.0 → 0.1.1 (interactive, no push)
make bump-minor                         # 0.1.0 → 0.2.0
make bump-major                         # 0.1.0 → 1.0.0
make release                            # bump + push commit + tag → CI creates GitHub Release

# Or directly:
./scripts/bump-version.sh patch         # same as make bump-patch
./scripts/bump-version.sh release       # same as make release (bump + push + tag)
uv run cz bump --increment patch --changelog  # raw cz (non-interactive)
uv run cz changelog --unreleased-version 0.1.2  # regenerate without bumping

---

## Environment variables

| Variable | Location | Purpose |
|---|---|---|
| `KOMIKAN_DEBUG=1` | shell | enables debug logging; never use `print()` in production |
| `VITE_API_URL` | `frontend/.env` (checked in) | backend URL for the React app (default: `http://localhost:8000`) |

---

## Architecture notes

- Game state is **in-memory only** — no database, no migrations.
- `src/komikan/api/game_manager.py` manages sessions; `src/komikan/api/models.py` defines Pydantic request/response shapes.
- `frontend/src/api.ts` is the API client; it reads `VITE_API_URL` at build time.
- Board constants: 5×8 grid, disabled nodes `{(0,2),(4,2)}`, Pangui starts at `(2,0)`, 12 Pu Trewa tokens fill rows 5–7.

---

## Toolchain quirks

- **Vite 8 is beta** (`^8.0.0-beta.13`) and React 19 — pre-release packages; treat build warnings with caution.
- **Pre-commit hooks**: Ruff (check + format) runs on commit; Commitizen validates message format on commit and branch name on push. Install once: `pre-commit install`.
- **Commit messages must follow Conventional Commits** (`feat:`, `fix:`, `docs:`, `refactor:`, `test:`, etc.) — enforced by Commitizen at commit time.
- **`pytest.ini` uses `--strict-markers`** — any undeclared marker causes a hard error. Declared markers: `slow`, `integration`, `performance`.
- **API tests** (`test_api.py`) use `httpx` + FastAPI `TestClient` — no live server needed.
- **Pygame tests** require a display; on headless environments, skip or mock `run.py`-dependent tests.
- **CI pipeline** (`.github/workflows/ci.yml`): runs on push/PR to `main` — backend (uv sync, pytest, ruff check, ruff format --check) and frontend (npm ci, npm run build, npm run lint).

---

## Roadmap / agent tasks

`openspec/` contains change artifacts (specs, proposals, tasks) for feature development. Use the OpenSpec skills to work through changes.

---

## Agent Update Reflection

- **Purpose:** When agent instructions are edited, the agent MUST evaluate whether the change requires code modifications or other repository edits.
- **If code changes are required:** the agent should make the edits (using the workspace), run or suggest running tests when feasible, and include an explicit report in its final message: `Applies to code: Yes` followed by a short list of modified files (workspace-relative links).
- **If no code changes are required:** the agent should state `Applies to code: No` in its final message.
- **Tracking:** For multi-step tasks invoked because of these instructions, the agent MUST start with the todo list tool and keep it updated until completion.

---

## Key Game Constants (in `board.py`)

- Board: 5 wide × 8 tall
- Disabled nodes: `{(0, 2), (4, 2)}`
- Disabled paths: Multiple diagonal restrictions (see `GameBoard.DISABLED_PATHS`)
- North starts at `(2, 0)`, South has 12 tokens at rows 5–7

---

## Test Markers

- `@pytest.mark.slow` — long-running tests
- `@pytest.mark.integration` — integration tests
- `@pytest.mark.performance` — performance benchmarks

---

## Key references

- Game rules: `docs/01-game-rules.md`
- Architecture Decision Records: `docs/adr/`
- Version bumping: `cz bump` (generates changelog, PEP 440 versioning via Commitizen)
