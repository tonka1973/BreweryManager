"""
Check the actual schema of duty_returns table
"""
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from src.config.constants import CACHE_DB_PATH

print("=" * 70)
print("DUTY_RETURNS TABLE SCHEMA INSPECTOR")
print("=" * 70)
print(f"\nDatabase: {CACHE_DB_PATH}\n")

conn = sqlite3.connect(CACHE_DB_PATH)
cursor = conn.cursor()

# Get table info
cursor.execute("PRAGMA table_info(duty_returns)")
columns = cursor.fetchall()

print(f"Found {len(columns)} columns:\n")
print(f"{'#':<4} {'Column Name':<30} {'Type':<15} {'Not Null':<10} {'Default':<20} {'PK':<5}")
print("-" * 90)

for col in columns:
    col_id, name, type_, notnull, default, pk = col
    notnull_str = "NOT NULL" if notnull else ""
    default_str = str(default) if default else ""
    pk_str = "PK" if pk else ""
    print(f"{col_id:<4} {name:<30} {type_:<15} {notnull_str:<10} {default_str:<20} {pk_str:<5}")

conn.close()

print("\n" + "=" * 70)
