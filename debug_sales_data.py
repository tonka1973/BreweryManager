
import sqlite3
import os
from pathlib import Path

def inspect_real_db():
    home = Path.home()
    db_path = home / ".brewerymanager" / "cache.db"
    
    if not db_path.exists():
        print(f"DB not found at {db_path}")
        return

    print(f"DB: {db_path}")
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("\n--- DISTINCT STATUSES ---")
        cursor.execute("SELECT DISTINCT status FROM sales")
        for row in cursor.fetchall():
            print(f"Status: '{row[0]}'")

        print("\n--- INVOICE ID COUNTS ---")
        
        cursor.execute("SELECT count(*) FROM sales WHERE invoice_id IS NULL")
        print(f"NULL invoice_id: {cursor.fetchone()[0]}")

        cursor.execute("SELECT count(*) FROM sales WHERE invoice_id = ''")
        print(f"Empty string invoice_id: {cursor.fetchone()[0]}")

        cursor.execute("SELECT count(*) FROM sales WHERE invoice_id = 'None'")
        print(f"'None' string invoice_id: {cursor.fetchone()[0]}")

        print("\n--- SAMPLE SALES with NULL/Empty Invoice ---")
        cursor.execute("SELECT sale_id, status, invoice_id FROM sales WHERE invoice_id IS NULL OR invoice_id = '' OR invoice_id = 'None' LIMIT 5")
        for row in cursor.fetchall():
            print(f"Sale: {row[0]}, Status: {row[1]}, Invoice: '{row[2]}'")

        conn.close()
    except Exception as e:
        print(f"Error inspecting DB: {e}")

if __name__ == "__main__":
    inspect_real_db()
