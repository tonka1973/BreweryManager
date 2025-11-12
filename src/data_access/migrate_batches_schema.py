"""
Database Migration Script for Batches Table

Adds new fields for the refactored batch workflow:
- original_gravity: O.G. measurement
- final_gravity: F.G. measurement
- actual_abv: Calculated from O.G. and F.G.
- duty_abv: Higher of expected or actual ABV

Run this once to update existing databases.
"""

import sqlite3
from pathlib import Path


def migrate_batches_table(db_path):
    """
    Migrate batches table to add new fields

    Args:
        db_path: Path to SQLite database file
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Check if columns exist
    cursor.execute("PRAGMA table_info(batches)")
    columns = [col[1] for col in cursor.fetchall()]

    try:
        # Add new columns if they don't exist
        if 'original_gravity' not in columns:
            cursor.execute("ALTER TABLE batches ADD COLUMN original_gravity REAL")
            print("✓ Added original_gravity column")

        if 'final_gravity' not in columns:
            cursor.execute("ALTER TABLE batches ADD COLUMN final_gravity REAL")
            print("✓ Added final_gravity column")

        if 'actual_abv' not in columns:
            cursor.execute("ALTER TABLE batches ADD COLUMN actual_abv REAL")
            print("✓ Added actual_abv column")

        if 'duty_abv' not in columns:
            cursor.execute("ALTER TABLE batches ADD COLUMN duty_abv REAL")
            print("✓ Added duty_abv column")

        # Update existing batches to use only 'fermenting' or 'packaged' status
        cursor.execute("""
            UPDATE batches
            SET status = 'fermenting'
            WHERE status IN ('brewing', 'conditioning', 'ready')
        """)
        print("✓ Updated old status values to 'fermenting'")

        conn.commit()
        print("\n✅ Migration completed successfully!")

    except Exception as e:
        conn.rollback()
        print(f"\n❌ Migration failed: {e}")
        raise

    finally:
        conn.close()


if __name__ == '__main__':
    # Default database path
    db_path = Path(__file__).parent.parent.parent / 'data' / 'brewery_cache.db'

    if not db_path.exists():
        print(f"❌ Database not found at: {db_path}")
        print("   Create the database first by running the application.")
    else:
        print(f"Migrating database at: {db_path}\n")
        migrate_batches_table(db_path)
