"""
Check if duty settings were loaded correctly
"""
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from src.config.constants import CACHE_DB_PATH

print("=" * 70)
print("DUTY SETTINGS VERIFICATION")
print("=" * 70)
print(f"\nDatabase: {CACHE_DB_PATH}\n")

conn = sqlite3.connect(CACHE_DB_PATH)
cursor = conn.cursor()

# Check settings table
print("1. CHECKING SETTINGS TABLE:")
print("-" * 70)
cursor.execute("SELECT * FROM settings")
settings = cursor.fetchone()

if settings:
    print("✓ Settings record found\n")
    cursor.execute("PRAGMA table_info(settings)")
    columns = [col[1] for col in cursor.fetchall()]

    cursor.execute("SELECT * FROM settings")
    row = cursor.fetchone()

    important_fields = [
        'spr_draught_low',
        'spr_draught_standard',
        'spr_non_draught_standard',
        'rate_full_8_5_to_22',
        'vat_rate'
    ]

    for field in important_fields:
        if field in columns:
            idx = columns.index(field)
            value = row[idx] if row else None
            print(f"  {field}: £{value}/lpa" if 'rate' in field and 'vat' not in field else f"  {field}: {value}")
else:
    print("✗ No settings record found!")

# Check containers
print("\n2. CHECKING CONTAINER CONFIGURATIONS:")
print("-" * 70)
cursor.execute("SELECT name, actual_capacity, duty_paid_volume, is_draught_eligible FROM settings_containers")
containers = cursor.fetchall()

if containers:
    print(f"✓ Found {len(containers)} container types:\n")
    for name, actual, duty_paid, draught in containers:
        draught_text = " (Draught)" if draught else ""
        print(f"  • {name}: {actual}L → {duty_paid}L duty paid{draught_text}")
else:
    print("✗ No containers found!")

# Check batch packaging lines table
print("\n3. CHECKING BATCH PACKAGING LINES TABLE:")
print("-" * 70)
cursor.execute("SELECT COUNT(*) FROM batch_packaging_lines")
count = cursor.fetchone()[0]
print(f"  Records: {count} (expected 0 for new install)")

# Check duty returns table
print("\n4. CHECKING DUTY RETURNS TABLE:")
print("-" * 70)
cursor.execute("PRAGMA table_info(duty_returns)")
columns = cursor.fetchall()
print(f"  ✓ Table has {len(columns)} columns (expected 25)")

cursor.execute("SELECT COUNT(*) FROM duty_returns")
count = cursor.fetchone()[0]
print(f"  Records: {count} (expected 0 for new install)")

conn.close()

print("\n" + "=" * 70)
print("VERIFICATION COMPLETE")
print("=" * 70)
