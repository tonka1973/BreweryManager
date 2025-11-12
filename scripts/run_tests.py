#!/usr/bin/env python3
"""
Test Runner Script

Runs pytest test suite with various options.
"""

import argparse
import subprocess
import sys
from pathlib import Path


def main():
    """Run pytest on test suite."""
    project_root = Path(__file__).parent.parent

    parser = argparse.ArgumentParser(description="Run test suite")
    parser.add_argument(
        "--unit",
        action="store_true",
        help="Run only unit tests"
    )
    parser.add_argument(
        "--integration",
        action="store_true",
        help="Run only integration tests"
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Verbose output"
    )
    parser.add_argument(
        "--coverage",
        action="store_true",
        help="Run with coverage report (requires pytest-cov)"
    )

    args = parser.parse_args()

    print("=" * 70)
    print("Running Pytest Test Suite")
    print("=" * 70)
    print()

    # Check if pytest is installed
    try:
        subprocess.run(
            ["pytest", "--version"],
            check=True,
            capture_output=True
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("ERROR: pytest is not installed!")
        print("Install it with: pip install pytest")
        return 1

    # Build pytest command
    cmd = ["pytest"]

    if args.unit:
        cmd.extend(["-m", "unit"])
        print("Running: Unit tests only")
    elif args.integration:
        cmd.extend(["-m", "integration"])
        print("Running: Integration tests only")
    else:
        print("Running: All tests")

    if args.verbose:
        cmd.append("-vv")

    if args.coverage:
        cmd.extend(["--cov=src", "--cov-report=html", "--cov-report=term"])
        print("Coverage: Enabled")

    print(f"Command: {' '.join(cmd)}")
    print()

    try:
        result = subprocess.run(
            cmd,
            cwd=project_root,
            check=False
        )

        print()
        if result.returncode == 0:
            print("✅ All tests passed!")
            if args.coverage:
                print("📊 Coverage report: htmlcov/index.html")
            return 0
        else:
            print("❌ Some tests failed!")
            return result.returncode

    except Exception as e:
        print(f"❌ Error running pytest: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
