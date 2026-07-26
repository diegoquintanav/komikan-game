#!/usr/bin/env python3
"""Post-process CHANGELOG.md to add PR number links.

Called as a pre_bump_hook by commitizen. Converts bare (#N) or #N references
in changelog entries to clickable GitHub PR links.

Usage:
    scripts/link-changelog.py [changelog_path]

When called by commitizen hooks, receives $CZ_PRE_CHANGELOG_FILE_NAME as env var.
"""

import os
import re
import sys

GITHUB_REPO = "https://github.com/diegoquintanav/komikan-game"


def link_prs(content: str) -> str:
    """Convert PR references to GitHub PR links."""
    # Match (#N) at end of a line (before newline) — e.g. "message (#9)"
    content = re.sub(
        r"(?<=\s)\(#(\d+)\)(?=\s*$)",
        r"([#\1](" + GITHUB_REPO + r"/pull/\1))",
        content,
        flags=re.MULTILINE,
    )
    # Match standalone #N that is NOT already inside a markdown link or commit hash
    # Only match #N preceded by space/comma/opening paren and followed by space/comma/period/paren/newline
    content = re.sub(
        r"(?<![/`\[])(?<!\d)#(\d+)(?![\d/`\]])",
        r"[#\1](" + GITHUB_REPO + r"/pull/\1)",
        content,
    )
    return content


def main() -> None:
    changelog_path = sys.argv[1] if len(sys.argv) > 1 else None
    if not changelog_path:
        changelog_path = os.environ.get("CZ_PRE_CHANGELOG_FILE_NAME", "CHANGELOG.md")

    if not os.path.exists(changelog_path):
        print(f"link-changelog: {changelog_path} not found, skipping")
        return

    with open(changelog_path, "r") as f:
        content = f.read()

    linked = link_prs(content)

    if linked != content:
        with open(changelog_path, "w") as f:
            f.write(linked)
        print(f"link-changelog: added PR links to {changelog_path}")
    else:
        print(f"link-changelog: no PR references found in {changelog_path}")


if __name__ == "__main__":
    main()
