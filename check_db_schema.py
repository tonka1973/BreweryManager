"""
Quick script to check database schema after migration
"""
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from src.config.constants import CACHE_DB_PATH

conn = sqlite3.connect(CACHE_DB_PATH)
cursor = conn.cursor()

print("=" * 70)
print("DATABASE SCHEMA CHECK")
print("=" * 70)

# Check which tables exist
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
tables = cursor.fetchall()

print(f"\nDatabase: {CACHE_DB_PATH}")
print(f"\nTables found: {len(tables)}")
for table in tables:
    print(f"  • {table[0]}")

# Check duty_returns table specifically
print("\n" + "-" * 70)
print("DUTY_RETURNS TABLE SCHEMA:")
print("-" * 70)
cursor.execute("PRAGMA table_info(duty_returns)")
columns = cursor.fetchall()

if columns:
    print(f"\nColumns ({len(columns)}):")
    for col in columns:
        col_id, name, type_, notnull, default, pk = col
        print(f"  {col_id}: {name:30s} {type_:15s} {'NOT NULL' if notnull else ''}")
else:
    print("\n❌ Table does not exist or has no columns!")

# Check indexes
print("\n" + "-" * 70)
print("INDEXES:")
print("-" * 70)
cursor.execute("SELECT name FROM sqlite_master WHERE type='index' ORDER BY name")
indexes = cursor.fetchall()
print(f"\nIndexes found: {len(indexes)}")
for idx in indexes:
    print(f"  • {idx[0]}")

conn.close()

print("\n" + "=" * 70)
print("SCHEMA CHECK COMPLETE")
print("=" * 70)
