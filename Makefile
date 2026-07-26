.PHONY: help install test test-slow lint format check dev-backend dev-frontend dev build clean bump-patch bump-minor bump-major changelog release

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-18s\033[0m %s\n", $$1, $$2}'

# ── Setup ──────────────────────────────────────────────

install: ## Install all dependencies (Python + frontend)
	uv sync
	cd frontend && npm install

# ── Testing ────────────────────────────────────────────

test: ## Run tests (fast, skip slow)
	uv run pytest tests/ -v -m "not slow"

test-all: ## Run all tests including slow/performance
	uv run pytest tests/ -v

test-cov: ## Run tests with coverage report
	uv run pytest tests/ -v --cov=komikan --cov-report=html

# ── Linting & Formatting ───────────────────────────────

lint: ## Run ruff linter
	uv run ruff check .

format: ## Auto-format with ruff
	uv run ruff format .
	uv run ruff check --fix .

check: ## Run all checks (lint + format check + frontend lint)
	uv run ruff check .
	uv run ruff format --check .
	cd frontend && npm run lint

# ── Pygame ─────────────────────────────────────────────

pygame: ## Run the Pygame desktop version of the game
	uv run komikan

# ── Development Servers ────────────────────────────────

dev-backend: ## Start FastAPI dev server (port 8000)
	uv run komikan-api

dev-frontend: ## Start Vite dev server (port 5173)
	cd frontend && npm run dev

dev: ## Start both backend + frontend (background)
	@echo "Starting backend on :8000..."
	@uv run komikan-api &
	@echo "Starting frontend on :5173..."
	@cd frontend && npm run dev &
	@echo "Both servers starting. Backend: http://localhost:8000  Frontend: http://localhost:5173"

# ── Build ──────────────────────────────────────────────

build: ## Build frontend for production
	cd frontend && npm run build

# ── Version Management ─────────────────────────────────

bump-patch: ## Bump patch version (0.1.0 → 0.1.1)
	./scripts/bump-version.sh patch

bump-minor: ## Bump minor version (0.1.0 → 0.2.0)
	./scripts/bump-version.sh minor

bump-major: ## Bump major version (0.1.0 → 1.0.0)
	./scripts/bump-version.sh major

changelog: ## Regenerate CHANGELOG.md from conventional commits
	uv run cz changelog --unreleased-version $(shell cat VERSION | sed 's/^v//')
	uv run python scripts/link-changelog.py CHANGELOG.md

# ── Release ────────────────────────────────────────────

release: ## Full release flow: push commit with existing VERSION
	./scripts/bump-version.sh release

# ── Cleanup ────────────────────────────────────────────

clean: ## Remove build artifacts and caches
	rm -rf build/ dist/ *.egg-info .pytest_cache .mypy_cache .ruff_cache htmlcov .coverage
	rm -rf frontend/dist frontend/node_modules/.vite
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
