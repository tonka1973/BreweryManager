"""
Fix duty_returns table schema
Drops and recreates the duty_returns table with the correct schema
"""

import sqlite3
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.config.constants import CACHE_DB_PATH


def fix_duty_returns_table():
    """Drop and recreate duty_returns table with correct schema"""

    print("=" * 70)
    print("FIX DUTY_RETURNS TABLE SCHEMA")
    print("=" * 70)
    print(f"\nDatabase: {CACHE_DB_PATH}")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    try:
        conn = sqlite3.connect(CACHE_DB_PATH)
        cursor = conn.cursor()

        # Check if table exists
        cursor.execute('''
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='duty_returns'
        ''')

        if cursor.fetchone():
            print("1. Dropping old duty_returns table...")
            cursor.execute('DROP TABLE IF EXISTS duty_returns')
            print("   ✓ Old table dropped")
        else:
            print("1. No existing duty_returns table found")

        # Recreate table with correct schema
        print("\n2. Creating duty_returns table with correct schema...")
        cursor.execute('''
            CREATE TABLE duty_returns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                duty_month TEXT UNIQUE NOT NULL,

                -- Category 1: Draught <3.5% ABV
                draught_low_litres REAL DEFAULT 0.0,
                draught_low_lpa REAL DEFAULT 0.0,
                draught_low_duty REAL DEFAULT 0.0,

                -- Category 2: Draught 3.5-8.4% ABV
                draught_std_litres REAL DEFAULT 0.0,
                draught_std_lpa REAL DEFAULT 0.0,
                draught_std_duty REAL DEFAULT 0.0,

                -- Category 3: Non-Draught 3.5-8.4% ABV
                non_draught_litres REAL DEFAULT 0.0,
                non_draught_lpa REAL DEFAULT 0.0,
                non_draught_duty REAL DEFAULT 0.0,

                -- Category 4: Products ≥8.5% ABV (no SPR)
                high_abv_litres REAL DEFAULT 0.0,
                high_abv_lpa REAL DEFAULT 0.0,
                high_abv_duty REAL DEFAULT 0.0,

                -- Production total
                production_duty_total REAL DEFAULT 0.0,

                -- Adjustments
                spoilt_duty_reclaim REAL DEFAULT 0.0,
                under_declarations REAL DEFAULT 0.0,
                over_declarations REAL DEFAULT 0.0,

                -- Net duty payable
                net_duty_payable REAL DEFAULT 0.0,

                -- Status tracking
                status TEXT DEFAULT 'in_progress',
                submitted_date TEXT,
                payment_date TEXT,
                payment_reference TEXT,

                -- Audit
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT
            )
        ''')
        print("   ✓ Duty returns table created with correct schema")

        # Create index
        print("\n3. Creating index...")
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_duty_returns_month
            ON duty_returns(duty_month)
        ''')
        print("   ✓ Created index: idx_duty_returns_month")

        # Commit changes
        conn.commit()

        print("\n" + "=" * 70)
        print("✅ DUTY_RETURNS TABLE FIXED SUCCESSFULLY!")
        print("=" * 70)
        print("\nYou can now re-run the main migration script.")
        print("=" * 70)

        return True

    except sqlite3.Error as e:
        print(f"\n❌ ERROR: Failed to fix duty_returns table!")
        print(f"   {str(e)}")
        return False

    finally:
        if conn:
            conn.close()


if __name__ == "__main__":
    print("\n⚠️  WARNING: This will DROP and recreate the duty_returns table.")
    print("   Any existing duty return records will be DELETED.\n")

    response = input("Continue? (yes/no): ")
    if response.lower() == 'yes':
        success = fix_duty_returns_table()
        sys.exit(0 if success else 1)
    else:
        print("\nOperation cancelled.")
        sys.exit(0)
