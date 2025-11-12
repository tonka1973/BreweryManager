#!/usr/bin/env python3
"""
Code Formatter Script

Runs black code formatter on all Python files in the project.
"""

import subprocess
import sys
from pathlib import Path


def main():
    """Run black formatter on project files."""
    project_root = Path(__file__).parent.parent

    print("=" * 70)
    print("Running Black Code Formatter")
    print("=" * 70)
    print()

    # Directories to format
    targets = [
        "src",
        "tests",
        "scripts",
        "main.py"
    ]

    # Check if black is installed
    try:
        subprocess.run(
            ["black", "--version"],
            check=True,
            capture_output=True
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("ERROR: black is not installed!")
        print("Install it with: pip install black")
        return 1

    # Run black
    cmd = ["black"] + targets
    print(f"Command: {' '.join(cmd)}")
    print()

    try:
        result = subprocess.run(
            cmd,
            cwd=project_root,
            check=False
        )

        if result.returncode == 0:
            print()
            print("✅ Code formatting complete!")
            return 0
        else:
            print()
            print("❌ Code formatting failed!")
            return result.returncode

    except Exception as e:
        print(f"❌ Error running black: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
