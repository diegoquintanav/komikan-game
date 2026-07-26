## Unreleased

### Feat

- add Pygame target to Makefile for running the desktop version

### Test

- remove dead skip/xfail example markers (ALMUD-265)
- add game isolation and idempotency edge case tests (ALMUD-261, ALMUD-262)
- add comprehensive bug audit edge case tests (ALMUD-256 through ALMUD-263)

### CI

- add release workflow with changelog and GitHub Release automation

### Chore

- switch cz config to cz_customize for full commit type support
- polish README.md
- add Makefile and version bump script

## v0.1.0 (2026-07-26)

### Feat

- add openspec boilerplate
- **docs**: update copilot instructions and game rules for clarity and consistency
- **docs**: add CHANGELOG using commitizen
- first commit with uv and commitizen boilerplate

### Docs

- add web gameplay screenshot
- public release docs batch (ALMUD-251, 252, 266, 255) (#9)
- link LICENSE in README

### CI

- add release workflow with changelog and GitHub Release automation
- add GitHub Actions workflow (ALMUD-254) (#8)

### Chore

- add LICENSE, fix .gitignore and Dockerfile for public release
- housekeeping and add AGENTS.md
