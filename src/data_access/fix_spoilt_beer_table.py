"""
Fix spoilt_beer table schema
Drops and recreates the spoilt_beer table with the correct schema
"""

import sqlite3
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.config.constants import CACHE_DB_PATH


def fix_spoilt_beer_table():
    """Drop and recreate spoilt_beer table with correct schema"""

    print("=" * 70)
    print("FIX SPOILT_BEER TABLE SCHEMA")
    print("=" * 70)
    print(f"\nDatabase: {CACHE_DB_PATH}")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    try:
        conn = sqlite3.connect(CACHE_DB_PATH)
        cursor = conn.cursor()

        # Check if table exists
        cursor.execute('''
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='spoilt_beer'
        ''')

        if cursor.fetchone():
            print("1. Dropping old spoilt_beer table...")
            cursor.execute('DROP TABLE IF EXISTS spoilt_beer')
            print("   ✓ Old table dropped")
        else:
            print("1. No existing spoilt_beer table found")

        # Recreate table with correct schema
        print("\n2. Creating spoilt_beer table with correct schema...")
        cursor.execute('''
            CREATE TABLE spoilt_beer (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                -- Batch reference
                batch_id TEXT,
                gyle_number TEXT,

                -- When and which month
                date_discovered TEXT NOT NULL,
                duty_month TEXT NOT NULL,
                status TEXT DEFAULT 'pending',

                -- Container details
                container_type TEXT NOT NULL,
                quantity INTEGER NOT NULL,

                -- Volumes
                total_volume REAL,
                duty_paid_volume REAL,
                pure_alcohol_litres REAL,

                -- Duty calculation (from original packaging)
                spr_category TEXT,
                original_duty_rate REAL,
                duty_to_reclaim REAL,

                -- Reason for spoilage
                reason_category TEXT,
                reason_notes TEXT,

                -- Audit
                recorded_by TEXT,
                recorded_at TEXT DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY (batch_id) REFERENCES batches(batch_id)
            )
        ''')
        print("   ✓ Spoilt beer table created with correct schema")

        # Create indexes
        print("\n3. Creating indexes...")
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_spoilt_beer_month
            ON spoilt_beer(duty_month)
        ''')
        print("   ✓ Created index: idx_spoilt_beer_month")

        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_spoilt_beer_batch
            ON spoilt_beer(batch_id)
        ''')
        print("   ✓ Created index: idx_spoilt_beer_batch")

        # Commit changes
        conn.commit()

        print("\n" + "=" * 70)
        print("✅ SPOILT_BEER TABLE FIXED SUCCESSFULLY!")
        print("=" * 70)
        print("\nYou can now re-run the main migration script.")
        print("=" * 70)

        return True

    except sqlite3.Error as e:
        print(f"\n❌ ERROR: Failed to fix spoilt_beer table!")
        print(f"   {str(e)}")
        return False

    finally:
        if conn:
            conn.close()


if __name__ == "__main__":
    print("\n⚠️  WARNING: This will DROP and recreate the spoilt_beer table.")
    print("   Any existing spoilt beer records will be DELETED.\n")

    response = input("Continue? (yes/no): ")
    if response.lower() == 'yes':
        success = fix_spoilt_beer_table()
        sys.exit(0 if success else 1)
    else:
        print("\nOperation cancelled.")
        sys.exit(0)
