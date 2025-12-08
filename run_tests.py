#!/usr/bin/env python3
"""
Test runner script for the Komikan game.
Provides convenient ways to run different test suites.
"""

import sys
import subprocess


def run_command(cmd):
    """Run a command and return the result."""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)


def main():
    """Main test runner function."""
    print("Komikan Game Test Runner")
    print("=" * 50)

    if len(sys.argv) > 1:
        test_type = sys.argv[1].lower()
    else:
        test_type = "all"

    # Test commands
    commands = {
        "all": "uv run pytest tests/ -v",
        "board": "uv run pytest tests/test_board.py -v",
        "player": "uv run pytest tests/test_player.py -v",
        "integration": "uv run pytest tests/test_integration.py -v",
        "performance": "uv run pytest tests/test_performance.py -v",
        "coverage": "uv run pytest tests/ --cov=. --cov-report=html --cov-report=term",
        "fast": "uv run pytest tests/ -x -q",  # Stop on first failure, quiet
        "slow": "uv run pytest tests/ -v -m 'not slow'",  # Skip slow tests
    }

    if test_type not in commands:
        print(f"Unknown test type: {test_type}")
        print("Available options:")
        for cmd_name, cmd in commands.items():
            print(f"  {cmd_name}: {cmd}")
        sys.exit(1)

    print(f"Running {test_type} tests...")
    print(f"Command: {commands[test_type]}")
    print()

    # Run the command
    success, stdout, stderr = run_command(commands[test_type])

    print(stdout)
    if stderr:
        print("STDERR:")
        print(stderr)

    if success:
        print("✅ Tests completed successfully!")
        sys.exit(0)
    else:
        print("❌ Tests failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
