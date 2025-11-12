"""
Database Migration: Add Empty Bottles and Cans Tables
This script adds the bottles_empty and cans_empty tables to existing databases.
Run this once to upgrade the database schema.
"""

import sqlite3
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.config.constants import CACHE_DB_PATH


def migrate_database():
    """Add bottles_empty and cans_empty tables to the database"""

    print(f"Connecting to database at: {CACHE_DB_PATH}")

    if not CACHE_DB_PATH.exists():
        print("Error: Database does not exist. Please initialize the database first.")
        return False

    try:
        conn = sqlite3.connect(CACHE_DB_PATH)
        cursor = conn.cursor()

        # Check if tables already exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='bottles_empty'")
        bottles_exists = cursor.fetchone() is not None

        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='cans_empty'")
        cans_exists = cursor.fetchone() is not None

        if bottles_exists and cans_exists:
            print("✓ Migration not needed - tables already exist!")
            conn.close()
            return True

        # Create bottles_empty table
        if not bottles_exists:
            print("Creating bottles_empty table...")
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS bottles_empty (
                    bottle_id TEXT PRIMARY KEY,
                    bottle_size_ml INTEGER,
                    quantity_in_stock INTEGER DEFAULT 0,
                    condition TEXT,
                    last_updated TEXT,
                    notes TEXT,
                    sync_status TEXT DEFAULT 'synced'
                )
            ''')
            print("✓ bottles_empty table created")

        # Create cans_empty table
        if not cans_exists:
            print("Creating cans_empty table...")
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS cans_empty (
                    can_id TEXT PRIMARY KEY,
                    can_size_ml INTEGER,
                    quantity_in_stock INTEGER DEFAULT 0,
                    condition TEXT,
                    last_updated TEXT,
                    notes TEXT,
                    sync_status TEXT DEFAULT 'synced'
                )
            ''')
            print("✓ cans_empty table created")

        # Commit changes
        conn.commit()
        conn.close()

        print("\n✅ Database migration completed successfully!")
        return True

    except Exception as e:
        print(f"\n❌ Migration failed: {str(e)}")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("Database Migration: Add Container Tables")
    print("=" * 60)
    print()

    success = migrate_database()

    if success:
        print("\nYou can now use the container tracking feature in the Inventory module.")
    else:
        print("\nPlease check the error and try again.")

    print()
    input("Press Enter to exit...")
