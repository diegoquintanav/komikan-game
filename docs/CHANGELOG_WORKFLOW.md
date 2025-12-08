# Changelog and Release Workflow

This document explains how the automated changelog and release workflow works for the Komikan Game project.

## Overview

The project uses [Commitizen](https://commitizen-tools.github.io/commitizen/) to automatically generate changelogs and manage semantic versioning based on [Conventional Commits](https://www.conventionalcommits.org/).

## Workflow Components

### 1. Commit Message Validation (`pr-validation.yml`)

**Triggers:** On pull request events (opened, synchronize, reopened)

**What it does:**
- Validates that all commit messages follow conventional commit format
- Runs tests to ensure code quality
- Checks if changelog needs updating for significant changes (feat/fix commits)

**Required commit format:**
```
type(scope): description

feat: add new game feature
fix: resolve capture bug
docs: update README
chore: update dependencies
```

### 2. Changelog Update (`changelog.yml`)

**Triggers:** On pull request events and manual dispatch

**What it does:**
- Detects if PR contains conventional commits that need changelog entries
- Automatically generates and updates `CHANGELOG.md`
- Commits changelog updates back to the PR branch
- Posts changelog preview as PR comment

**Automatic behavior:**
- Only runs if conventional commits are detected
- Updates existing changelog incrementally
- Creates initial changelog if none exists

### 3. Release Creation (`release.yml`)

**Triggers:** On push to main branch and manual dispatch

**What it does:**
- Analyzes commits since last release
- Automatically bumps version based on conventional commits:
  - `feat:` → minor version bump
  - `fix:` → patch version bump
  - `feat!:` or `fix!:` → major version bump
- Updates changelog with new version
- Creates GitHub release with release notes
- Pushes version tag

## Usage Guide

### For Developers

#### 1. Making Changes
Always use conventional commit messages:
```bash
git commit -m "feat: add diagonal movement validation"
git commit -m "fix: resolve capture move execution bug"
git commit -m "docs: update game rules documentation"
```

#### 2. Before Creating PR
Check your changelog locally:
```bash
# Preview what would be added to changelog
./scripts/changelog.sh preview

# Update changelog locally (optional)
./scripts/changelog.sh update
```

#### 3. Pull Request Process
1. Create PR with conventional commits
2. Automated validation will run
3. If significant changes detected, changelog workflow will:
   - Update `CHANGELOG.md` automatically
   - Commit changes to your PR branch
   - Post changelog preview as comment

#### 4. Manual Changelog Management
```bash
# Preview changelog changes
./scripts/changelog.sh preview

# Update changelog file
./scripts/changelog.sh update

# Bump version and update changelog
./scripts/changelog.sh bump
```

### For Maintainers

#### 1. Merge Process
- Ensure PR validation passes
- Review changelog updates
- Merge PR to main branch

#### 2. Release Process
After merge to main:
1. Release workflow automatically triggers
2. Analyzes new commits
3. Bumps version appropriately
4. Updates changelog
5. Creates GitHub release

#### 3. Manual Release
For manual version bumps:
1. Go to Actions → "Release and Version Bump"
2. Click "Run workflow"
3. Select bump type (auto/patch/minor/major)

## Configuration Files

### `.cz.toml`
Commitizen configuration:
- Conventional commits format
- Version scheme (PEP 440)
- Changelog generation settings
- UV integration

### GitHub Workflows
- `.github/workflows/pr-validation.yml` - PR validation and testing
- `.github/workflows/changelog.yml` - Automatic changelog updates
- `.github/workflows/release.yml` - Version bumping and releases

## Commit Types

| Type       | Description             | Version Impact |
| ---------- | ----------------------- | -------------- |
| `feat`     | New feature             | Minor bump     |
| `fix`      | Bug fix                 | Patch bump     |
| `docs`     | Documentation           | No bump        |
| `style`    | Code style changes      | No bump        |
| `refactor` | Code refactoring        | No bump        |
| `perf`     | Performance improvement | Patch bump     |
| `test`     | Test changes            | No bump        |
| `chore`    | Maintenance tasks       | No bump        |
| `build`    | Build system changes    | No bump        |
| `ci`       | CI/CD changes           | No bump        |

### Breaking Changes
Add `!` for breaking changes:
```bash
feat!: redesign board layout (breaking change)
fix!: change capture move API (breaking change)
```

## Branch Protection

The workflow enforces:
- ✅ All commits must follow conventional commit format
- ✅ Tests must pass
- ✅ Significant changes must have changelog updates
- ✅ No direct pushes to main branch

## Troubleshooting

### Common Issues

1. **"Conventional commits validation failed"**
   - Check commit message format
   - Ensure type prefix is correct
   - Use scope if applicable: `feat(board): add feature`

2. **"Changelog not updated for significant changes"**
   - Re-run changelog workflow
   - Manually update using `./scripts/changelog.sh update`

3. **"No version bump needed"**
   - Only `feat`/`fix` commits trigger releases
   - Use `docs`/`chore` for non-release changes

### Manual Override

To bypass validation (use sparingly):
```bash
git commit --no-verify -m "emergency fix"
git push --no-verify
```

## Benefits

- 📝 **Automatic Documentation** - Changelog always up-to-date
- 🏷️ **Semantic Versioning** - Predictable version numbers
- 🚀 **Automated Releases** - No manual release process
- ✅ **Quality Gates** - Enforced commit standards
- 🔄 **Consistent Process** - Same workflow for all contributors