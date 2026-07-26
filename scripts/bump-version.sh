#!/usr/bin/env bash
set -euo pipefail

# ── Bump version script ────────────────────────────────
# Usage:
#   ./scripts/bump-version.sh patch   # 0.1.0 → 0.1.1
#   ./scripts/bump-version.sh minor   # 0.1.0 → 0.2.0
#   ./scripts/bump-version.sh major   # 0.1.0 → 1.0.0
#   ./scripts/bump-version.sh release # bump + push commit + tag

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

CURRENT_VERSION=$(cat VERSION | sed 's/^v//')
BUMP_INPUT="${1:-patch}"
RELEASE_MODE=false
INCREMENT=""

if [ "$BUMP_INPUT" = "release" ]; then
  RELEASE_MODE=true
  INCREMENT="PATCH"  # cz bump auto-detects from commits; explicit as fallback
elif [ "$BUMP_INPUT" = "patch" ]; then
  INCREMENT="PATCH"
elif [ "$BUMP_INPUT" = "minor" ]; then
  INCREMENT="MINOR"
elif [ "$BUMP_INPUT" = "major" ]; then
  INCREMENT="MAJOR"
else
  fail "Unknown bump type: $BUMP_INPUT (use: patch, minor, major, release)"
fi

info()  { echo -e "${GREEN}✓${NC} $1"; }
warn()  { echo -e "${YELLOW}⚠${NC} $1"; }
fail()  { echo -e "${RED}✗${NC} $1"; exit 1; }

# ── Pre-flight checks ──────────────────────────────────

echo -e "\n${GREEN}── Komikan version bump ──${NC}"
echo -e "   Current version: ${YELLOW}v${CURRENT_VERSION}${NC}"
echo ""

# Check commitizen is installed
command -v uv >/dev/null 2>&1 || fail "uv not found. Install from https://docs.astral.sh/uv/getting-started/installation/"
uv run cz version >/dev/null 2>&1 || fail "commitizen not found. Install with: uv add --group dev commitizen"

# Check clean working tree
if ! git diff --quiet || ! git diff --cached --quiet; then
  warn "Working tree has uncommitted changes."
  read -p "   Continue anyway? [y/N] " -n 1 -r
  echo
  [[ $REPLY =~ ^[Yy]$ ]] || exit 1
fi

# Check we're on main
BRANCH=$(git branch --show-current)
if [ "$BRANCH" != "main" ]; then
  warn "Not on main branch (currently on: ${BRANCH})"
  read -p "   Continue anyway? [y/N] " -n 1 -r
  echo
  [[ $REPLY =~ ^[Yy]$ ]] || exit 1
fi

# ── Dry run preview ─────────────────────────────────────

echo -e "\n${GREEN}── Dry run (what will change) ──${NC}"
uv run cz bump --increment "$INCREMENT" --dry-run 2>&1 || true
echo ""

# ── Confirm ─────────────────────────────────────────────

read -p "   Proceed with bump? [y/N] " -n 1 -r
echo
[[ $REPLY =~ ^[Yy]$ ]] || exit 0

# ── Bump ────────────────────────────────────────────────

echo -e "\n${GREEN}── Bumping version ──${NC}"
uv run cz bump --increment "$INCREMENT" --changelog
NEW_VERSION=$(cat VERSION | sed 's/^v//')
info "v${CURRENT_VERSION} → v${NEW_VERSION}"

# Show what changed
echo -e "\n${GREEN}── Files updated ──${NC}"
git diff --stat HEAD~1

echo -e "\n${GREEN}── Changelog entry ──${NC}"
git diff HEAD~1 -- CHANGELOG.md | head -60

# ── Push (if release mode) ──────────────────────────────

if [ "$RELEASE_MODE" = true ]; then
  echo -e "\n${GREEN}── Pushing commit + tag ──${NC}"
  git push origin main
  git push origin "v${NEW_VERSION}"
  info "Pushed commit and tag v${NEW_VERSION}"
  info "CI will create GitHub Release after checks pass"
  echo -e "\n   Track it at: https://github.com/diegoquintanav/komikan-game/releases"
else
  echo -e "\n${YELLOW}── Not pushing (run 'make release' or 'git push --tags' when ready) ──${NC}"
fi

echo -e "\n${GREEN}Done.${NC}\n"
