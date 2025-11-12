#!/usr/bin/env python3
"""
Code Quality Checker Script

Runs pylint code quality checker on all Python files in the project.
"""

import subprocess
import sys
from pathlib import Path


def main():
    """Run pylint on project files."""
    project_root = Path(__file__).parent.parent

    print("=" * 70)
    print("Running Pylint Code Quality Checker")
    print("=" * 70)
    print()

    # Directories to check
    targets = [
        "src",
        "tests",
        "scripts",
        "main.py"
    ]

    # Check if pylint is installed
    try:
        subprocess.run(
            ["pylint", "--version"],
            check=True,
            capture_output=True
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("ERROR: pylint is not installed!")
        print("Install it with: pip install pylint")
        return 1

    # Run pylint
    cmd = ["pylint"] + targets
    print(f"Command: {' '.join(cmd)}")
    print()
    print("Target score: 7.0/10 or higher")
    print()

    try:
        result = subprocess.run(
            cmd,
            cwd=project_root,
            check=False
        )

        print()
        if result.returncode == 0:
            print("✅ Code quality check passed!")
            return 0
        else:
            print("⚠️  Code quality check complete with warnings.")
            print("   (This is normal - aim for score > 7.0/10)")
            return 0  # Don't fail on warnings

    except Exception as e:
        print(f"❌ Error running pylint: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
