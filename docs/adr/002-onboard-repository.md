# ADR-002: Onboard Repository for Coding Agent

## Status

Accepted (completed)

## Context

The repository needed a `.github/copilot-instructions.md` file to onboard coding agents, enabling them to work efficiently by understanding project structure, tech stack, and established practices without extensive exploration.

## Decision

Create agent instructions covering:

- Project summary (Komikan as a traditional Mapuche hunt game)
- Tech stack (Python 3.11, uv, pygame, Ruff, pytest, Commitizen, pre-commit hooks)
- Project structure (src/komikan/, tests/, docs/, agent-roadmap/)
- Coding guidelines (conventional commits, uv for deps, Ruff for linting)
- Essential commands for setup, run, test, lint, and versioning

Instructions were kept to 2 pages maximum and broadly applicable to the entire project.

## Consequences

- Agents can immediately start working without codebase exploration
- Reduced bash command and build failures
- Established practices (conventional commits, Ruff formatting) are consistently followed
