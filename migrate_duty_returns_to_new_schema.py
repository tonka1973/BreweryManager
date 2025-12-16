"""
Migrate duty_returns table from old schema to new schema
Safely preserves existing data by renaming old table
"""
import sqlite3
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))
from src.config.constants import CACHE_DB_PATH

print("=" * 70)
print("DUTY_RETURNS TABLE SCHEMA MIGRATION")
print("=" * 70)
print(f"\nDatabase: {CACHE_DB_PATH}")
print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

print("This will:")
print("  1. Rename the old duty_returns table to duty_returns_old")
print("  2. Create the new duty_returns table with updated schema")
print("  3. Create the missing index")
print("\nYour old data will be preserved in duty_returns_old")
print("=" * 70)

response = input("\nContinue? (yes/no): ")
if response.lower() != 'yes':
    print("\nMigration cancelled.")
    sys.exit(0)

try:
    conn = sqlite3.connect(CACHE_DB_PATH)
    cursor = conn.cursor()

    # Step 1: Rename old table
    print("\n1. Renaming old duty_returns table...")
    cursor.execute("ALTER TABLE duty_returns RENAME TO duty_returns_old")
    print("   ✓ Old table renamed to duty_returns_old")

    # Step 2: Create new table with correct schema
    print("\n2. Creating new duty_returns table with updated schema...")
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
    print("   ✓ New duty_returns table created")
    print("   ✓ Supports 4 SPR categories")
    print("   ✓ Tracks production, spoilage, and adjustments")

    # Step 3: Create the index
    print("\n3. Creating index on duty_month...")
    cursor.execute('''
        CREATE INDEX idx_duty_returns_month ON duty_returns(duty_month)
    ''')
    print("   ✓ Index created successfully")

    # Step 4: Verify
    print("\n4. Verifying new schema...")
    cursor.execute("PRAGMA table_info(duty_returns)")
    columns = cursor.fetchall()
    print(f"   ✓ New table has {len(columns)} columns")

    cursor.execute("""
        SELECT name FROM sqlite_master
        WHERE type='index' AND name='idx_duty_returns_month'
    """)
    if cursor.fetchone():
        print("   ✓ Index verified")

    # Commit all changes
    conn.commit()

    print("\n" + "=" * 70)
    print("✅ MIGRATION COMPLETED SUCCESSFULLY!")
    print("=" * 70)
    print("\nChanges made:")
    print("  • Old table preserved as: duty_returns_old")
    print("  • New table created: duty_returns")
    print("  • Index created: idx_duty_returns_month")
    print("\nThe duty system is now ready with the full HMRC-compliant schema!")
    print("=" * 70)

except sqlite3.Error as e:
    print(f"\n❌ ERROR: {str(e)}")
    conn.rollback()
    sys.exit(1)

finally:
    if conn:
        conn.close()
