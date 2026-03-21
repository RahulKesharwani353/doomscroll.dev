#!/usr/bin/env python
"""
Alembic migration helper script for Doomscroll.

Usage:
    python scripts/migrate.py generate "migration description"
    python scripts/migrate.py upgrade
    python scripts/migrate.py downgrade
    python scripts/migrate.py current
    python scripts/migrate.py history
    python scripts/migrate.py check
"""

import subprocess
import sys
import os

# Change to backend directory
BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(BACKEND_DIR)


def run_command(cmd: list[str]) -> int:
    """Run an alembic command and return exit code."""
    # Use python -m alembic for cross-platform compatibility
    full_cmd = [sys.executable, "-m"] + cmd
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(full_cmd)
    return result.returncode


def generate(message: str) -> int:
    """Generate a new migration using autogenerate."""
    return run_command(["alembic", "revision", "--autogenerate", "-m", message])


def upgrade(revision: str = "head") -> int:
    """Upgrade database to a revision."""
    return run_command(["alembic", "upgrade", revision])


def downgrade(revision: str = "-1") -> int:
    """Downgrade database by revision count or to specific revision."""
    return run_command(["alembic", "downgrade", revision])


def current() -> int:
    """Show current revision."""
    return run_command(["alembic", "current"])


def history() -> int:
    """Show migration history."""
    return run_command(["alembic", "history", "--verbose"])


def check() -> int:
    """Check if migrations are needed (useful for CI)."""
    return run_command(["alembic", "check"])


def print_usage():
    """Print usage information."""
    print(__doc__)


def main():
    if len(sys.argv) < 2:
        print_usage()
        sys.exit(1)

    command = sys.argv[1].lower()

    if command == "generate":
        if len(sys.argv) < 3:
            print("Error: Migration description required")
            print("Usage: python scripts/migrate.py generate \"migration description\"")
            sys.exit(1)
        sys.exit(generate(sys.argv[2]))

    elif command == "upgrade":
        revision = sys.argv[2] if len(sys.argv) > 2 else "head"
        sys.exit(upgrade(revision))

    elif command == "downgrade":
        revision = sys.argv[2] if len(sys.argv) > 2 else "-1"
        sys.exit(downgrade(revision))

    elif command == "current":
        sys.exit(current())

    elif command == "history":
        sys.exit(history())

    elif command == "check":
        sys.exit(check())

    elif command in ["help", "-h", "--help"]:
        print_usage()
        sys.exit(0)

    else:
        print(f"Unknown command: {command}")
        print_usage()
        sys.exit(1)


if __name__ == "__main__":
    main()
