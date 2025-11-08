#!/usr/bin/env python3
"""
Simple Validation Test
Quick checks that everything is ready for Windows deployment
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.data_access.sqlite_cache import SQLiteCacheManager
from src.utilities.auth import AuthManager

def main():
    print("=" * 70)
    print("PHASE 2 DEPLOYMENT VALIDATION")
    print("=" * 70)
    print()

    all_passed = True

    # Test 1: Database exists and has data
    print("TEST 1: Database & Sample Data")
    print("-" * 70)
    try:
        cache = SQLiteCacheManager()
        cache.connect()

        cursor = cache.connection.cursor()

        # Check key tables have data
        cursor.execute("SELECT COUNT(*) FROM recipes")
        recipe_count = cursor.fetchone()[0]
        print(f"✓ Recipes: {recipe_count} records")

        cursor.execute("SELECT COUNT(*) FROM batches")
        batch_count = cursor.fetchone()[0]
        print(f"✓ Batches: {batch_count} records")

        cursor.execute("SELECT COUNT(*) FROM customers")
        customer_count = cursor.fetchone()[0]
        print(f"✓ Customers: {customer_count} records")

        cursor.execute("SELECT COUNT(*) FROM sales")
        sales_count = cursor.fetchone()[0]
        print(f"✓ Sales: {sales_count} records")

        cursor.execute("SELECT COUNT(*) FROM inventory_materials")
        material_count = cursor.fetchone()[0]
        print(f"✓ Inventory materials: {material_count} records")

        if recipe_count == 0:
            print("\n⚠ WARNING: No sample data found. Run: python add_sample_data.py\n")

        cache.close()

    except Exception as e:
        print(f"✗ Database test failed: {e}")
        all_passed = False

    print()

    # Test 2: Authentication works
    print("TEST 2: User Authentication")
    print("-" * 70)
    try:
        cache = SQLiteCacheManager()
        auth = AuthManager(cache)

        user = auth.login("admin", "admin")
        if user:
            print(f"✓ Admin login successful (role: {user.role})")
        else:
            print("✗ Admin login failed")
            all_passed = False

    except Exception as e:
        print(f"✗ Authentication test failed: {e}")
        all_passed = False

    print()

    # Test 3: All Phase 2 modules exist
    print("TEST 3: Phase 2 Modules")
    print("-" * 70)

    modules = [
        ("src/gui/main_window.py", "Main Window"),
        ("src/gui/dashboard.py", "Module 1: Dashboard"),
        ("src/gui/recipes.py", "Module 2: Recipes"),
        ("src/gui/inventory.py", "Module 3: Inventory"),
        ("src/gui/batches.py", "Module 4: Batches"),
        ("src/gui/duty.py", "Module 5: Duty Calculator"),
        ("src/gui/customers.py", "Module 6: Customers"),
        ("src/gui/sales.py", "Module 7: Sales"),
        ("src/gui/invoicing.py", "Module 8: Invoicing"),
        ("src/gui/labels.py", "Module 9: Labels"),
    ]

    for filepath, name in modules:
        if os.path.exists(filepath):
            print(f"✓ {name}")
        else:
            print(f"✗ {name} - FILE MISSING")
            all_passed = False

    print()

    # Test 4: Helper files exist
    print("TEST 4: Helper Files")
    print("-" * 70)

    helpers = [
        ("add_sample_data.py", "Sample data script"),
        ("TESTING_CHECKLIST.md", "Testing checklist"),
    ]

    for filepath, name in helpers:
        if os.path.exists(filepath):
            print(f"✓ {name}")
        else:
            print(f"✗ {name} - FILE MISSING")
            all_passed = False

    print()

    # Summary
    print("=" * 70)
    if all_passed:
        print("✅ ALL VALIDATION CHECKS PASSED")
        print("=" * 70)
        print()
        print("Phase 2 is complete and ready for Windows deployment testing.")
        print()
        print("To test on Windows:")
        print("  1. Run: python main.py")
        print("  2. Login with: admin / admin")
        print("  3. Follow TESTING_CHECKLIST.md for complete validation")
        print()
        return 0
    else:
        print("❌ SOME VALIDATION CHECKS FAILED")
        print("=" * 70)
        print("\nPlease fix the issues above before deploying.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
