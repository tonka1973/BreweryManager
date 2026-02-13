"""
Database Migration Script
Adds inventory_item_id column to recipe_ingredients table
"""

import sqlite3
from pathlib import Path

# Database path (same as in constants.py)
DB_PATH = Path.home() / ".brewerymanager" / "cache.db"

def migrate():
    """Add inventory_item_id column to recipe_ingredients table"""
    try:
        # Connect to database
        connection = sqlite3.connect(DB_PATH)
        cursor = connection.cursor()

        # Check if column already exists
        cursor.execute("PRAGMA table_info(recipe_ingredients)")
        columns = [row[1] for row in cursor.fetchall()]

        if 'inventory_item_id' in columns:
            print("✓ Column 'inventory_item_id' already exists in recipe_ingredients table")
        else:
            print("Adding 'inventory_item_id' column to recipe_ingredients table...")
            cursor.execute('''
                ALTER TABLE recipe_ingredients
                ADD COLUMN inventory_item_id TEXT
            ''')
            connection.commit()
            print("✓ Migration completed successfully!")

        connection.close()

    except Exception as e:
        print(f"✗ Migration failed: {str(e)}")
        return False

    return True

if __name__ == "__main__":
    print("=" * 50)
    print("Database Migration: Add inventory_item_id column")
    print("=" * 50)

    if not DB_PATH.exists():
        print(f"✗ Database not found at: {DB_PATH}")
        print("Please make sure the database exists before running this migration.")
    else:
        migrate()

    print("=" * 50)
