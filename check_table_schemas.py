"""
Check the actual schemas of all main tables
"""
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from src.config.constants import CACHE_DB_PATH

conn = sqlite3.connect(CACHE_DB_PATH)
cursor = conn.cursor()

tables = ['recipes', 'inventory', 'customers', 'batches', 'sales', 'invoices']

print("=" * 70)
print("DATABASE TABLE SCHEMAS")
print("=" * 70)

for table in tables:
    print(f"\n{table.upper()} TABLE:")
    print("-" * 70)

    try:
        cursor.execute(f"PRAGMA table_info({table})")
        columns = cursor.fetchall()

        if columns:
            for col in columns:
                col_id, name, type_, notnull, default, pk = col
                pk_str = " (PK)" if pk else ""
                print(f"  {name:<30} {type_:<15}{pk_str}")
        else:
            print("  Table doesn't exist or has no columns")
    except sqlite3.Error as e:
        print(f"  Error: {e}")

conn.close()

print("\n" + "=" * 70)
