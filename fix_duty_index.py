"""
Fix the missing idx_duty_returns_month index
"""
import sqlite3
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))
from src.config.constants import CACHE_DB_PATH

print("=" * 70)
print("FIX MISSING INDEX: idx_duty_returns_month")
print("=" * 70)
print(f"\nDatabase: {CACHE_DB_PATH}")
print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

try:
    conn = sqlite3.connect(CACHE_DB_PATH)
    cursor = conn.cursor()

    # Step 1: Check if duty_returns table exists
    print("1. Checking if duty_returns table exists...")
    cursor.execute("""
        SELECT name FROM sqlite_master
        WHERE type='table' AND name='duty_returns'
    """)
    table_exists = cursor.fetchone()

    if not table_exists:
        print("   ❌ duty_returns table does not exist!")
        print("   Please run migrate_duty_system.py first.")
        sys.exit(1)
    else:
        print("   ✓ duty_returns table found")

    # Step 2: Check what columns exist
    print("\n2. Checking table schema...")
    cursor.execute("PRAGMA table_info(duty_returns)")
    columns = cursor.fetchall()
    column_names = [col[1] for col in columns]

    print(f"   Found {len(columns)} columns")

    if 'duty_month' not in column_names:
        print("   ❌ duty_month column is missing!")
        print("   Table needs to be recreated with migrate_duty_system.py")
        sys.exit(1)
    else:
        print("   ✓ duty_month column exists")

    # Step 3: Check if index already exists
    print("\n3. Checking if index already exists...")
    cursor.execute("""
        SELECT name FROM sqlite_master
        WHERE type='index' AND name='idx_duty_returns_month'
    """)
    index_exists = cursor.fetchone()

    if index_exists:
        print("   ✓ Index already exists - nothing to do!")
        conn.close()
        sys.exit(0)
    else:
        print("   - Index does not exist")

    # Step 4: Create the index
    print("\n4. Creating index idx_duty_returns_month...")
    cursor.execute("""
        CREATE INDEX idx_duty_returns_month ON duty_returns(duty_month)
    """)
    conn.commit()
    print("   ✓ Index created successfully!")

    # Step 5: Verify it was created
    print("\n5. Verifying index creation...")
    cursor.execute("""
        SELECT name FROM sqlite_master
        WHERE type='index' AND name='idx_duty_returns_month'
    """)
    if cursor.fetchone():
        print("   ✓ Index verified!")
    else:
        print("   ❌ Index verification failed!")
        sys.exit(1)

    print("\n" + "=" * 70)
    print("✅ INDEX FIX COMPLETED SUCCESSFULLY!")
    print("=" * 70)
    print("\nThe idx_duty_returns_month index has been created.")
    print("This will improve performance when searching duty returns by month.")
    print("=" * 70)

except sqlite3.Error as e:
    print(f"\n❌ ERROR: {str(e)}")
    sys.exit(1)

finally:
    if conn:
        conn.close()
