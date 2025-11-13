"""
Database Migration: Add Products Module Tables
Creates container_types, products, and product_sales tables
"""

import sqlite3
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.config.constants import CACHE_DB_PATH


def migrate():
    """Add new tables for Products module"""

    print("=" * 60)
    print("PRODUCTS MODULE DATABASE MIGRATION")
    print("=" * 60)
    print(f"\nDatabase: {CACHE_DB_PATH}")

    try:
        # Connect to database
        conn = sqlite3.connect(CACHE_DB_PATH)
        cursor = conn.cursor()

        print("\n1. Creating container_types table...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS container_types (
                container_type_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                size_litres REAL NOT NULL,
                category TEXT,
                quantity_available INTEGER DEFAULT 0,
                active INTEGER DEFAULT 1,
                created_date TEXT,
                last_modified TEXT,
                sync_status TEXT DEFAULT 'synced'
            )
        ''')
        print("   ✓ container_types table created")

        print("\n2. Creating products table...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                product_id TEXT PRIMARY KEY,
                gyle_number TEXT NOT NULL,
                batch_id TEXT,
                recipe_id TEXT,
                product_name TEXT,
                style TEXT,
                container_type TEXT,
                container_size_l REAL,
                quantity_total INTEGER,
                quantity_in_stock INTEGER,
                quantity_sold INTEGER DEFAULT 0,
                abv REAL,
                date_packaged TEXT,
                date_in_stock TEXT,
                status TEXT,
                is_name_locked INTEGER DEFAULT 0,
                created_date TEXT,
                created_by TEXT,
                last_modified TEXT,
                sync_status TEXT DEFAULT 'synced',
                FOREIGN KEY (batch_id) REFERENCES batches(batch_id),
                FOREIGN KEY (recipe_id) REFERENCES recipes(recipe_id)
            )
        ''')
        print("   ✓ products table created")

        print("\n3. Creating product_sales table...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS product_sales (
                product_sale_id TEXT PRIMARY KEY,
                product_id TEXT NOT NULL,
                gyle_number TEXT NOT NULL,
                sale_id TEXT,
                customer_id TEXT,
                invoice_id TEXT,
                quantity_sold INTEGER,
                date_sold TEXT,
                date_delivered TEXT,
                delivery_address TEXT,
                container_type TEXT,
                created_date TEXT,
                sync_status TEXT DEFAULT 'synced',
                FOREIGN KEY (product_id) REFERENCES products(product_id),
                FOREIGN KEY (sale_id) REFERENCES sales(sale_id),
                FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
                FOREIGN KEY (invoice_id) REFERENCES invoices(invoice_id)
            )
        ''')
        print("   ✓ product_sales table created")

        print("\n4. Creating indexes for better performance...")
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_products_gyle ON products(gyle_number)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_products_batch ON products(batch_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_products_status ON products(status)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_product_sales_gyle ON product_sales(gyle_number)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_product_sales_customer ON product_sales(customer_id)')
        print("   ✓ Indexes created")

        print("\n5. Migrating existing container data to container_types...")

        # Check if casks_empty has data
        cursor.execute('SELECT COUNT(*) FROM casks_empty')
        cask_count = cursor.fetchone()[0]

        if cask_count > 0:
            print(f"   Found {cask_count} cask types in casks_empty")
            cursor.execute('''
                INSERT OR IGNORE INTO container_types
                (container_type_id, name, size_litres, category, quantity_available, created_date, last_modified)
                SELECT
                    cask_id,
                    cask_size,
                    cask_size_litres,
                    'Cask',
                    quantity_in_stock,
                    last_updated,
                    last_updated
                FROM casks_empty
            ''')
            migrated = cursor.rowcount
            print(f"   ✓ Migrated {migrated} cask types to container_types")

        # Check if bottles_empty has data
        cursor.execute('SELECT COUNT(*) FROM bottles_empty')
        bottle_count = cursor.fetchone()[0]

        if bottle_count > 0:
            print(f"   Found {bottle_count} bottle types in bottles_empty")
            cursor.execute('''
                INSERT OR IGNORE INTO container_types
                (container_type_id, name, size_litres, category, quantity_available, created_date, last_modified)
                SELECT
                    bottle_id,
                    bottle_size_ml || 'ml Bottle',
                    CAST(bottle_size_ml AS REAL) / 1000.0,
                    'Bottle',
                    quantity_in_stock,
                    last_updated,
                    last_updated
                FROM bottles_empty
            ''')
            migrated = cursor.rowcount
            print(f"   ✓ Migrated {migrated} bottle types to container_types")

        # Check if cans_empty has data
        cursor.execute('SELECT COUNT(*) FROM cans_empty')
        can_count = cursor.fetchone()[0]

        if can_count > 0:
            print(f"   Found {can_count} can types in cans_empty")
            cursor.execute('''
                INSERT OR IGNORE INTO container_types
                (container_type_id, name, size_litres, category, quantity_available, created_date, last_modified)
                SELECT
                    can_id,
                    can_size_ml || 'ml Can',
                    CAST(can_size_ml AS REAL) / 1000.0,
                    'Can',
                    quantity_in_stock,
                    last_updated,
                    last_updated
                FROM cans_empty
            ''')
            migrated = cursor.rowcount
            print(f"   ✓ Migrated {migrated} can types to container_types")

        if cask_count == 0 and bottle_count == 0 and can_count == 0:
            print("   No existing container data to migrate")
            print("\n6. Creating default container types...")

            # Add common container types for new installations
            import uuid
            from datetime import datetime
            now = datetime.now().isoformat()

            default_containers = [
                {'name': 'Pin', 'size_litres': 20.5, 'category': 'Cask', 'qty': 0},
                {'name': 'Firkin', 'size_litres': 40.9, 'category': 'Cask', 'qty': 0},
                {'name': 'Kilderkin', 'size_litres': 81.8, 'category': 'Cask', 'qty': 0},
                {'name': 'Barrel', 'size_litres': 163.6, 'category': 'Cask', 'qty': 0},
                {'name': '30L Keg', 'size_litres': 30.0, 'category': 'Keg', 'qty': 0},
                {'name': '50L Keg', 'size_litres': 50.0, 'category': 'Keg', 'qty': 0},
                {'name': '330ml Bottle', 'size_litres': 0.33, 'category': 'Bottle', 'qty': 0},
                {'name': '500ml Bottle', 'size_litres': 0.5, 'category': 'Bottle', 'qty': 0},
                {'name': '330ml Can', 'size_litres': 0.33, 'category': 'Can', 'qty': 0},
                {'name': '500ml Can', 'size_litres': 0.5, 'category': 'Can', 'qty': 0},
            ]

            for container in default_containers:
                cursor.execute('''
                    INSERT INTO container_types
                    (container_type_id, name, size_litres, category, quantity_available, active, created_date, last_modified, sync_status)
                    VALUES (?, ?, ?, ?, ?, 1, ?, ?, 'pending')
                ''', (
                    str(uuid.uuid4()),
                    container['name'],
                    container['size_litres'],
                    container['category'],
                    container['qty'],
                    now,
                    now
                ))

            print(f"   ✓ Created {len(default_containers)} default container types")

        # Commit all changes
        conn.commit()

        print("\n" + "=" * 60)
        print("MIGRATION COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print("\nNew tables added:")
        print("  • container_types (unified container management)")
        print("  • products (finished goods tracking)")
        print("  • product_sales (recall tracking)")
        print("\nThe Products module is now ready to use.")
        print("=" * 60)

    except sqlite3.Error as e:
        print(f"\n❌ ERROR: Database migration failed!")
        print(f"   {str(e)}")
        return False

    finally:
        if conn:
            conn.close()

    return True


if __name__ == "__main__":
    success = migrate()
    sys.exit(0 if success else 1)
