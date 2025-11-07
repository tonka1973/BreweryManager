#!/usr/bin/env python3
"""
Brewery Management System - Installation Test Script
Verifies that all components are properly installed and configured.
"""

import sys
import os

def print_header(text):
    """Print a formatted header."""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)

def print_test(name, passed, details=""):
    """Print test result."""
    status = "✓ PASS" if passed else "✗ FAIL"
    print(f"{status} - {name}")
    if details:
        print(f"        {details}")

def test_python_version():
    """Test Python version."""
    version = sys.version_info
    passed = version >= (3, 11)
    details = f"Python {version.major}.{version.minor}.{version.micro}"
    if not passed:
        details += " (Upgrade to 3.11+ recommended)"
    return passed, details

def test_module_import(module_name, package=None):
    """Test if a module can be imported."""
    try:
        if package:
            __import__(package, fromlist=[module_name])
        else:
            __import__(module_name)
        return True, "Installed"
    except ImportError as e:
        return False, f"Not found: {str(e)}"

def test_project_structure():
    """Test if project structure exists."""
    required_dirs = [
        "src",
        "src/config",
        "src/data_access",
        "src/utilities",
        "src/gui",
    ]
    required_files = [
        "main.py",
        "requirements.txt",
        "src/config/constants.py",
        "src/utilities/auth.py",
        "src/data_access/sqlite_cache.py",
        "src/data_access/sync_manager.py",
        "src/gui/main_window.py",
    ]

    all_passed = True
    missing = []

    for dir_path in required_dirs:
        if not os.path.isdir(dir_path):
            all_passed = False
            missing.append(f"Directory: {dir_path}")

    for file_path in required_files:
        if not os.path.isfile(file_path):
            all_passed = False
            missing.append(f"File: {file_path}")

    if missing:
        details = "Missing: " + ", ".join(missing[:3])
        if len(missing) > 3:
            details += f" (+{len(missing) - 3} more)"
    else:
        details = "All required files present"

    return all_passed, details

def test_app_data_dir():
    """Test if app data directory can be created."""
    from pathlib import Path
    app_data_dir = Path.home() / ".brewerymanager"
    try:
        os.makedirs(app_data_dir, exist_ok=True)
        return True, f"Location: {app_data_dir}"
    except Exception as e:
        return False, f"Cannot create: {str(e)}"

def test_database_init():
    """Test if database can be initialized."""
    try:
        from src.data_access.sqlite_cache import SQLiteCacheManager
        db = SQLiteCacheManager()
        return True, "Database initialized successfully"
    except Exception as e:
        return False, f"Error: {str(e)}"

def test_gui_import():
    """Test if GUI can be imported."""
    try:
        from src.gui.main_window import BreweryMainWindow
        return True, "GUI module ready"
    except Exception as e:
        return False, f"Error: {str(e)}"

def main():
    """Run all installation tests."""
    print_header("Brewery Management System - Installation Test")
    print("\nTesting installation integrity...\n")

    # Track overall results
    all_tests_passed = True

    # Test Python version
    passed, details = test_python_version()
    print_test("Python Version", passed, details)
    if not passed:
        all_tests_passed = False

    # Test standard library modules
    print("\nStandard Library:")
    for module in ["tkinter", "sqlite3", "json", "pathlib"]:
        passed, details = test_module_import(module)
        print_test(f"  {module}", passed, details)
        if not passed:
            all_tests_passed = False

    # Test required packages
    print("\nRequired Packages:")
    packages = [
        ("google-api-python-client", "googleapiclient"),
        ("google-auth", "google.auth"),
        ("Pillow", "PIL"),
        ("reportlab", "reportlab"),
        ("pandas", "pandas"),
        ("openpyxl", "openpyxl"),
        ("requests", "requests"),
    ]
    for package_name, import_name in packages:
        passed, details = test_module_import(import_name)
        print_test(f"  {package_name}", passed, details)
        if not passed:
            all_tests_passed = False

    # Test project structure
    print("\nProject Structure:")
    passed, details = test_project_structure()
    print_test("  Required files", passed, details)
    if not passed:
        all_tests_passed = False

    # Test application data directory
    print("\nApplication Setup:")
    passed, details = test_app_data_dir()
    print_test("  App data directory", passed, details)
    if not passed:
        all_tests_passed = False

    # Test database initialization
    passed, details = test_database_init()
    print_test("  Database initialization", passed, details)
    if not passed:
        all_tests_passed = False

    # Test GUI import
    passed, details = test_gui_import()
    print_test("  GUI module", passed, details)
    if not passed:
        all_tests_passed = False

    # Print summary
    print_header("Test Summary")
    if all_tests_passed:
        print("\n✓ All tests passed!")
        print("\nThe application is ready to run:")
        print("    python main.py")
        print("\nDefault login:")
        print("    Username: admin")
        print("    Password: admin123")
    else:
        print("\n✗ Some tests failed!")
        print("\nPlease fix the issues above before running the application.")
        print("See LOCAL_SETUP_GUIDE.md for troubleshooting help.")

    print("\n" + "=" * 60 + "\n")

    return 0 if all_tests_passed else 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\nTest cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
