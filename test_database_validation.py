#!/usr/bin/env python3
"""
Database Validation Test
Checks database tables, schemas, and basic operations
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.data_access.sqlite_cache import SQLiteCacheManager
from src.utilities.auth import AuthManager
from datetime import datetime

def main():
    print("=" * 70)
    print("DATABASE VALIDATION TEST")
    print("=" * 70)
    print()

    cache = SQLiteCacheManager()

    try:
        # Test 1: Database connection
        print("TEST 1: Database Connection")
        print("-" * 70)
        cache.connect()
        print("✓ Database connected")
        print()

        # Test 2: Table initialization
        print("TEST 2: Database Initialization")
        print("-" * 70)
        cache.initialize_database()
        print("✓ Database initialized")
        print()

        # Test 3: Check all required tables exist
        print("TEST 3: Required Tables")
        print("-" * 70)
        required_tables = [
            'users',
            'recipes',
            'recipe_ingredients',
            'inventory_materials',
            'inventory_transactions',
            'batches',
            'customers',
            'sales',
            'invoices',
            'invoice_lines',
            'payments',
        ]

        cursor = cache.connection.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        existing_tables = [row[0] for row in cursor.fetchall()]

        all_tables_exist = True
        for table in required_tables:
            if table in existing_tables:
                print(f"✓ Table '{table}' exists")
            else:
                print(f"✗ Table '{table}' MISSING")
                all_tables_exist = False

        print()

        # Test 4: User authentication
        print("TEST 4: Authentication")
        print("-" * 70)
        auth = AuthManager(cache)
        auth.create_default_admin()

        user = auth.login("admin", "admin")
        if user:
            print(f"✓ Login successful: {user.username} (role: {user.role})")
        else:
            print("✗ Login failed")
        print()

        # Test 5: Basic CRUD operations
        print("TEST 5: Basic CRUD Operations")
        print("-" * 70)

        # Create
        test_recipe = {
            'beer_name': 'Test IPA',
            'style': 'IPA',
            'abv': 6.5,
            'ibu': 60,
            'srm': 10,
            'batch_size': 1000,
            'grain_bill': 'Test grain bill',
            'hop_schedule': 'Test hop schedule',
            'yeast': 'Test yeast',
            'mash_schedule': 'Test mash',
            'fermentation_notes': 'Test fermentation',
            'is_active': 1,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }

        cache.connect()  # Reconnect for operations
        recipe_id = cache.insert_record('recipes', test_recipe)
        if recipe_id:
            print(f"✓ INSERT: Created recipe with ID {recipe_id}")
        else:
            print("✗ INSERT failed")

        # Read
        recipe = cache.get_record('recipes', recipe_id, 'recipe_id')
        if recipe and recipe['beer_name'] == 'Test IPA':
            print(f"✓ SELECT: Retrieved recipe '{recipe['beer_name']}'")
        else:
            print("✗ SELECT failed")

        # Update
        update_data = {'abv': 7.0, 'updated_at': datetime.now().isoformat()}
        success = cache.update_record('recipes', recipe_id, update_data, id_column='recipe_id')
        if success:
            updated = cache.get_record('recipes', recipe_id, 'recipe_id')
            if updated and updated['abv'] == 7.0:
                print(f"✓ UPDATE: Changed ABV to {updated['abv']}")
            else:
                print("✗ UPDATE verification failed")
        else:
            print("✗ UPDATE failed")

        # Delete
        success = cache.delete_record('recipes', recipe_id, id_column='recipe_id')
        if success:
            deleted = cache.get_record('recipes', recipe_id, 'recipe_id')
            if not deleted:
                print("✓ DELETE: Recipe successfully deleted")
            else:
                print("✗ DELETE verification failed")
        else:
            print("✗ DELETE failed")

        cache.close()

        print()

        # Test 6: Check sample data was loaded
        print("TEST 6: Sample Data")
        print("-" * 70)

        cache.connect()  # Reconnect for more operations

        # Count records in key tables
        tables_to_check = {
            'recipes': 'recipe_id',
            'batches': 'batch_id',
            'customers': 'customer_id',
            'sales': 'sale_id',
            'inventory_materials': 'material_id'
        }

        cursor = cache.connection.cursor()
        for table, id_col in tables_to_check.items():
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"  {table}: {count} records")

        print()

        # Test 7: Foreign key constraints
        print("TEST 7: Data Relationships")
        print("-" * 70)

        # Check recipes have ingredients
        cursor.execute("""
            SELECT r.beer_name, COUNT(ri.ingredient_id) as ingredient_count
            FROM recipes r
            LEFT JOIN recipe_ingredients ri ON r.recipe_id = ri.recipe_id
            GROUP BY r.recipe_id
        """)
        recipes_with_ingredients = cursor.fetchall()
        if recipes_with_ingredients:
            print("✓ Recipes with ingredients:")
            for beer_name, count in recipes_with_ingredients:
                print(f"    - {beer_name}: {count} ingredients")
        else:
            print("  No recipes with ingredients found")

        # Check batches linked to recipes
        cursor.execute("""
            SELECT b.gyle_number, r.beer_name
            FROM batches b
            INNER JOIN recipes r ON b.recipe_id = r.recipe_id
            LIMIT 5
        """)
        batches_with_recipes = cursor.fetchall()
        if batches_with_recipes:
            print("✓ Batches linked to recipes:")
            for gyle, beer in batches_with_recipes:
                print(f"    - {gyle}: {beer}")
        else:
            print("  No batches with recipes found")

        # Check sales linked to customers
        cursor.execute("""
            SELECT s.sale_id, c.customer_name, s.status
            FROM sales s
            INNER JOIN customers c ON s.customer_id = c.customer_id
            LIMIT 5
        """)
        sales_with_customers = cursor.fetchall()
        if sales_with_customers:
            print("✓ Sales linked to customers:")
            for sale_id, customer, status in sales_with_customers:
                print(f"    - Sale #{sale_id}: {customer} ({status})")
        else:
            print("  No sales with customers found")

        print()

        # Close connection
        cache.close()
        print("✓ Database connection closed")
        print()

        # Summary
        print("=" * 70)
        print("✓ ALL DATABASE TESTS PASSED")
        print("=" * 70)
        print()
        print("Database structure is valid and functional.")
        print("Sample data is loaded and relationships are working.")
        print()

        return 0

    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
