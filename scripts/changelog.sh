#!/bin/bash
# Changelog management script for Komikan Game

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

show_help() {
    cat << EOF
Komikan Game Changelog Management

USAGE:
    ./scripts/changelog.sh [COMMAND]

COMMANDS:
    preview     Generate a preview of changelog changes (dry run)
    update      Update the changelog file
    bump        Bump version and update changelog
    help        Show this help message

EXAMPLES:
    ./scripts/changelog.sh preview
    ./scripts/changelog.sh update
    ./scripts/changelog.sh bump

REQUIREMENTS:
    - UV package manager installed
    - Commitizen configured in project
    - Git repository with conventional commits

EOF
}

preview_changelog() {
    echo "🔍 Previewing changelog changes..."
    echo "================================="

    if [ -f "CHANGELOG.md" ]; then
        echo "📋 Current changelog exists. Showing what would be added:"
        echo ""
        uv run cz changelog --dry-run --incremental
    else
        echo "📋 No changelog exists yet. Showing what would be created:"
        echo ""
        uv run cz changelog --dry-run
    fi
}

update_changelog() {
    echo "📝 Updating changelog..."
    echo "======================="

    if [ -f "CHANGELOG.md" ]; then
        echo "📋 Updating existing changelog..."
        uv run cz changelog --incremental
    else
        echo "📋 Creating new changelog..."
        uv run cz changelog
    fi

    if git diff --quiet CHANGELOG.md 2>/dev/null; then
        echo "ℹ️ No changes to commit - changelog is up to date"
    else
        echo "✅ Changelog updated successfully!"
        echo ""
        echo "📋 Changes made:"
        git diff CHANGELOG.md
        echo ""
        echo "💡 To commit these changes, run:"
        echo "   git add CHANGELOG.md"
        echo "   git commit -m \"docs: update CHANGELOG.md\""
    fi
}

bump_version() {
    echo "🚀 Bumping version and updating changelog..."
    echo "=========================================="

    # Show what would happen first
    echo "🔍 Checking what version bump would occur..."
    PREVIEW=$(uv run cz bump --dry-run 2>&1 || true)
    echo "$PREVIEW"

    if echo "$PREVIEW" | grep -q "No commits to bump"; then
        echo "ℹ️ No version bump needed - no significant changes found"
        exit 0
    fi

    # Ask for confirmation
    echo ""
    read -p "❓ Do you want to proceed with this version bump? (y/N): " -n 1 -r
    echo

    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "✅ Proceeding with version bump..."
        uv run cz bump --yes

        echo "🎉 Version bumped successfully!"
        echo ""
        echo "💡 Don't forget to push your changes:"
        echo "   git push origin main"
        echo "   git push origin --tags"
    else
        echo "❌ Version bump cancelled"
    fi
}

check_requirements() {
    # Check if UV is installed
    if ! command -v uv &> /dev/null; then
        echo "❌ UV package manager not found. Please install UV first:"
        echo "   curl -LsSf https://astral.sh/uv/install.sh | sh"
        exit 1
    fi

    # Check if we're in a git repository
    if ! git rev-parse --git-dir > /dev/null 2>&1; then
        echo "❌ This script must be run from within a git repository"
        exit 1
    fi

    # Check if commitizen is available
    if ! uv run cz --help &> /dev/null; then
        echo "❌ Commitizen not available. Installing dependencies..."
        uv sync
    fi
}

main() {
    check_requirements

    case "${1:-help}" in
        preview)
            preview_changelog
            ;;
        update)
            update_changelog
            ;;
        bump)
            bump_version
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            echo "❌ Unknown command: $1"
            echo ""
            show_help
            exit 1
            ;;
    esac
}

main "$@"