"""
Migration Script: Add VAT Rate to Settings Table
This adds a configurable VAT rate field to the settings table.
"""

import sqlite3
from datetime import datetime
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from config.constants import CACHE_DB_PATH


def migrate():
    """Add VAT rate to settings table"""
    print("=" * 60)
    print("Migration: Add VAT Rate to Settings")
    print("=" * 60)

    try:
        conn = sqlite3.connect(CACHE_DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Check if settings table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='settings'")
        if cursor.fetchone() is None:
            print("✗ Settings table does not exist yet.")
            print("  Please run the main duty system migration first:")
            print("  python src/data_access/migrate_duty_system.py")
            conn.close()
            return

        # Check if vat_rate column already exists
        cursor.execute("PRAGMA table_info(settings)")
        columns = [row[1] for row in cursor.fetchall()]

        if 'vat_rate' in columns:
            print("✓ vat_rate column already exists in settings table")
        else:
            print("\nAdding vat_rate column to settings table...")
            cursor.execute('''
                ALTER TABLE settings
                ADD COLUMN vat_rate REAL DEFAULT 0.20
            ''')
            print("✓ vat_rate column added successfully (default: 0.20 = 20%)")

        conn.commit()
        print("\n" + "=" * 60)
        print("Migration completed successfully!")
        print("=" * 60)

        conn.close()

    except Exception as e:
        print(f"\n✗ Migration failed: {str(e)}")
        if conn:
            conn.rollback()
            conn.close()
        raise


if __name__ == "__main__":
    migrate()
