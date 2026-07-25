# AGENTS.md

## What this repo is

Komikan is a traditional Mapuche hunt game. The repo has three layers:

- **Core game logic** — Python package (`src/komikan/`): `board.py` (5×8 grid, movement/capture), `player.py` (state, PlayerSide enum)
- **FastAPI REST backend** — `src/komikan/api/` (in-memory game sessions, Pydantic v2 models)
- **React SPA frontend** — `frontend/` (React 19, TypeScript 5.9, Tailwind v4, Vite 8 beta)

The copilot-instructions file (`.github/copilot-instructions.md`) covers the Python/pygame side well. The sections below focus on gaps and the web stack.

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

uv run pytest tests/ -v                           # all tests (~84 pass, 1 skip, 1 xfail)
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
docker-compose up  # backend :8000, frontend :5173, API docs :8000/docs
```

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
- **No CI pipeline** — pre-commit hooks are the only automated quality gate.

---

## Roadmap / agent tasks

`agent-roadmap/` contains numbered markdown files for incremental MCP server conversion. Use them sequentially via:

```bash
gh agent-task create -F agent-roadmap/<file>.md
```

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

- Game rules: `docs/GAME_RULES.md`
- Architecture Decision Records: `docs/adr/`
- Version bumping: `cz bump` (generates changelog, PEP 440 versioning via Commitizen)
