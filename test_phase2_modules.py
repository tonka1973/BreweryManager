#!/usr/bin/env python3
"""
Phase 2 Module Testing Script
Tests all modules can be imported and basic functionality works
"""

import sys
import os
from datetime import datetime

# Test results tracker
test_results = []
errors_found = []

def test_result(test_name, passed, error=None):
    """Record test result"""
    test_results.append((test_name, passed))
    if not passed:
        errors_found.append(f"{test_name}: {error}")
    status = "✓ PASS" if passed else "✗ FAIL"
    print(f"{status}: {test_name}")
    if error and not passed:
        print(f"  Error: {error}")

print("=" * 60)
print("PHASE 2 MODULE TESTING")
print("=" * 60)
print()

# Test 1: Core imports
print("TEST 1: Core Module Imports")
print("-" * 60)
try:
    from src.utilities.config import Config
    test_result("Import Config", True)
except Exception as e:
    test_result("Import Config", False, str(e))

try:
    from src.utilities.cache_manager import CacheManager
    test_result("Import CacheManager", True)
except Exception as e:
    test_result("Import CacheManager", False, str(e))

try:
    from src.utilities.auth import Authentication
    test_result("Import Authentication", True)
except Exception as e:
    test_result("Import Authentication", False, str(e))

print()

# Test 2: GUI Module Imports
print("TEST 2: GUI Module Imports")
print("-" * 60)

gui_modules = [
    "dashboard",
    "recipes",
    "inventory",
    "batches",
    "duty",
    "customers",
    "sales",
    "invoicing",
    "labels"
]

for module_name in gui_modules:
    try:
        module = __import__(f"src.gui.{module_name}", fromlist=[module_name.capitalize() + "Module"])
        test_result(f"Import {module_name}.py", True)
    except Exception as e:
        test_result(f"Import {module_name}.py", False, str(e))

print()

# Test 3: Main Window Import
print("TEST 3: Main Window Import")
print("-" * 60)
try:
    from src.gui.main_window import MainWindow
    test_result("Import MainWindow", True)
except Exception as e:
    test_result("Import MainWindow", False, str(e))

print()

# Test 4: Database Operations
print("TEST 4: Database Operations")
print("-" * 60)
try:
    config = Config()
    cache = CacheManager(config)
    cache.connect()
    test_result("Database connection", True)

    # Initialize database
    cache.initialize_database()
    test_result("Database initialization", True)

    # Check that tables exist
    tables = [
        'users', 'recipes', 'recipe_ingredients', 'inventory_materials',
        'inventory_transactions', 'batches', 'customers', 'sales',
        'invoices', 'invoice_lines', 'payments'
    ]

    cursor = cache.conn.cursor()
    for table in tables:
        cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
        exists = cursor.fetchone() is not None
        test_result(f"Table '{table}' exists", exists, "Table not found" if not exists else None)

    cache.close()
    test_result("Database close", True)

except Exception as e:
    test_result("Database operations", False, str(e))

print()

# Test 5: Authentication
print("TEST 5: Authentication")
print("-" * 60)
try:
    config = Config()
    cache = CacheManager(config)
    auth = Authentication(cache)

    # Try login with default credentials
    user = auth.login("admin", "admin")
    if user:
        test_result("Admin login", True)
        test_result(f"User data complete (username={user.username}, role={user.role})", True)
    else:
        test_result("Admin login", False, "Login returned None")

except Exception as e:
    test_result("Authentication", False, str(e))

print()

# Test 6: Sample Data Script
print("TEST 6: Sample Data Script")
print("-" * 60)
try:
    # Check if add_sample_data.py exists
    if os.path.exists("add_sample_data.py"):
        test_result("add_sample_data.py exists", True)

        # Import and check it doesn't have syntax errors
        import add_sample_data
        test_result("add_sample_data.py imports successfully", True)
    else:
        test_result("add_sample_data.py exists", False, "File not found")

except Exception as e:
    test_result("Sample data script", False, str(e))

print()

# Test 7: Module Class Checks
print("TEST 7: Module Class Definitions")
print("-" * 60)
try:
    from src.gui.dashboard import DashboardModule
    test_result("DashboardModule class exists", True)

    from src.gui.recipes import RecipesModule
    test_result("RecipesModule class exists", True)

    from src.gui.inventory import InventoryModule
    test_result("InventoryModule class exists", True)

    from src.gui.batches import BatchesModule
    test_result("BatchesModule class exists", True)

    from src.gui.duty import DutyModule
    test_result("DutyModule class exists", True)

    from src.gui.customers import CustomersModule
    test_result("CustomersModule class exists", True)

    from src.gui.sales import SalesModule
    test_result("SalesModule class exists", True)

    from src.gui.invoicing import InvoicingModule
    test_result("InvoicingModule class exists", True)

    from src.gui.labels import LabelsModule
    test_result("LabelsModule class exists", True)

except Exception as e:
    test_result("Module class definitions", False, str(e))

print()

# Test 8: Constants Check
print("TEST 8: Constants and Configuration")
print("-" * 60)
try:
    from src.utilities.constants import DUTY_RATES, DRAUGHT_RELIEF_RATE, VAT_RATE
    test_result("Import DUTY_RATES", True)
    test_result(f"DRAUGHT_RELIEF_RATE = {DRAUGHT_RELIEF_RATE}", True)
    test_result(f"VAT_RATE = {VAT_RATE}", True)

    # Check duty rates structure
    if 'beer_draught' in DUTY_RATES and 'beer_non_draught' in DUTY_RATES:
        test_result("Duty rates properly defined", True)
    else:
        test_result("Duty rates properly defined", False, "Missing beer rates")

except Exception as e:
    test_result("Constants", False, str(e))

print()

# Summary
print("=" * 60)
print("TEST SUMMARY")
print("=" * 60)
passed = sum(1 for _, p in test_results if p)
failed = sum(1 for _, p in test_results if not p)
total = len(test_results)

print(f"Total Tests: {total}")
print(f"Passed: {passed} ({100*passed//total}%)")
print(f"Failed: {failed}")
print()

if errors_found:
    print("ERRORS FOUND:")
    print("-" * 60)
    for error in errors_found:
        print(f"  • {error}")
    print()
    sys.exit(1)
else:
    print("✓ ALL TESTS PASSED!")
    print()
    print("Note: This is a headless environment, so GUI display testing")
    print("cannot be performed. Please test the full GUI on Windows.")
    sys.exit(0)
