#!/usr/bin/env python3
"""
Syntax Validation Test for Phase 2 Modules
Checks all Python files for syntax errors without importing tkinter
"""

import ast
import os
import sys

def check_syntax(filepath):
    """Check Python file for syntax errors"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            source = f.read()
        ast.parse(source, filename=filepath)
        return True, None
    except SyntaxError as e:
        return False, f"Line {e.lineno}: {e.msg}"
    except Exception as e:
        return False, str(e)

def main():
    print("=" * 70)
    print("PHASE 2 SYNTAX VALIDATION")
    print("=" * 70)
    print()

    files_to_check = [
        # Core files
        ("main.py", "Main application entry point"),
        ("add_sample_data.py", "Sample data script"),

        # Infrastructure
        ("src/utilities/auth.py", "Authentication module"),
        ("src/data_access/sqlite_cache.py", "SQLite cache manager"),
        ("src/data_access/sync_manager.py", "Sync manager"),
        ("src/data_access/google_sheets_client.py", "Google Sheets client"),
        ("src/config/constants.py", "Constants and configuration"),

        # GUI modules
        ("src/gui/main_window.py", "Main window"),
        ("src/gui/dashboard.py", "Dashboard module"),
        ("src/gui/recipes.py", "Recipes module"),
        ("src/gui/inventory.py", "Inventory module"),
        ("src/gui/batches.py", "Batches module"),
        ("src/gui/duty.py", "Duty calculator module"),
        ("src/gui/customers.py", "Customers module"),
        ("src/gui/sales.py", "Sales module"),
        ("src/gui/invoicing.py", "Invoicing module"),
        ("src/gui/labels.py", "Label printing module"),
    ]

    passed = 0
    failed = 0
    errors = []

    for filepath, description in files_to_check:
        if os.path.exists(filepath):
            success, error = check_syntax(filepath)
            if success:
                print(f"✓ PASS: {filepath}")
                print(f"         {description}")
                passed += 1
            else:
                print(f"✗ FAIL: {filepath}")
                print(f"         {description}")
                print(f"         Error: {error}")
                failed += 1
                errors.append((filepath, error))
        else:
            print(f"⚠ SKIP: {filepath} (not found)")
            print(f"         {description}")
        print()

    # Check for common patterns
    print("=" * 70)
    print("CHECKING CODE PATTERNS")
    print("=" * 70)
    print()

    # Check that all GUI modules have Module classes
    gui_modules = [
        "dashboard", "recipes", "inventory", "batches",
        "duty", "customers", "sales", "invoicing", "labels"
    ]

    pattern_errors = []

    for module in gui_modules:
        filepath = f"src/gui/{module}.py"
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                content = f.read()
                module_name = module.capitalize()
                expected_class = f"class {module_name}Module(tk.Frame):"

                if expected_class in content or f"class {module_name}Module(" in content:
                    print(f"✓ {filepath}: Has {module_name}Module class")
                else:
                    print(f"✗ {filepath}: Missing {module_name}Module class")
                    pattern_errors.append(f"{filepath}: Missing {module_name}Module class")

    print()

    # Summary
    print("=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    total = passed + failed
    print(f"Files checked: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Pattern issues: {len(pattern_errors)}")
    print()

    if errors:
        print("SYNTAX ERRORS:")
        print("-" * 70)
        for filepath, error in errors:
            print(f"  • {filepath}")
            print(f"    {error}")
        print()

    if pattern_errors:
        print("PATTERN ISSUES:")
        print("-" * 70)
        for error in pattern_errors:
            print(f"  • {error}")
        print()

    if not errors and not pattern_errors:
        print("✓ ALL SYNTAX CHECKS PASSED!")
        print()
        print("Note: Full GUI testing requires Windows with tkinter.")
        print("      The code structure and syntax are valid.")
        return 0
    else:
        print("✗ ISSUES FOUND - See details above")
        return 1

if __name__ == "__main__":
    sys.exit(main())
