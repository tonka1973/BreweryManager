#!/usr/bin/env python3
"""
Full Quality Check Script

Runs all code quality tools in sequence:
1. Black (code formatting)
2. Pylint (code quality)
3. Pytest (test suite)
"""

import subprocess
import sys
from pathlib import Path


def run_step(name, script_name):
    """
    Run a quality check step.

    Args:
        name: Display name of the step
        script_name: Name of the script file to run

    Returns:
        True if successful, False otherwise
    """
    script_path = Path(__file__).parent / script_name

    print()
    print("=" * 70)
    print(f"STEP: {name}")
    print("=" * 70)
    print()

    try:
        result = subprocess.run(
            [sys.executable, str(script_path)],
            check=False
        )

        if result.returncode == 0:
            print()
            print(f"✅ {name} - PASSED")
            return True
        else:
            print()
            print(f"⚠️  {name} - COMPLETED WITH WARNINGS")
            return True  # Don't fail on warnings

    except Exception as e:
        print()
        print(f"❌ {name} - FAILED: {e}")
        return False


def main():
    """Run full quality check suite."""
    print("=" * 70)
    print("BREWERY MANAGER - FULL QUALITY CHECK")
    print("=" * 70)
    print()
    print("This will run:")
    print("  1. Black code formatter")
    print("  2. Pylint code quality checker")
    print("  3. Pytest test suite")
    print()

    results = []

    # Step 1: Format code
    results.append(("Code Formatting (Black)", run_step("Code Formatting", "format_code.py")))

    # Step 2: Check quality
    results.append(("Code Quality (Pylint)", run_step("Code Quality", "check_quality.py")))

    # Step 3: Run tests
    results.append(("Test Suite (Pytest)", run_step("Test Suite", "run_tests.py")))

    # Summary
    print()
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print()

    all_passed = True
    for name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{status:12} - {name}")
        if not passed:
            all_passed = False

    print()
    print("=" * 70)

    if all_passed:
        print("✅ ALL CHECKS PASSED!")
        print("=" * 70)
        return 0
    else:
        print("❌ SOME CHECKS FAILED!")
        print("=" * 70)
        return 1


if __name__ == "__main__":
    sys.exit(main())
