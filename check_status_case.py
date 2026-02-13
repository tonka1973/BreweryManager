
import sqlite3
import os
from pathlib import Path

def check_status_casing():
    home = Path.home()
    db_path = home / ".brewerymanager" / "cache.db"
    
    if not db_path.exists():
        print(f"DB not found at {db_path}")
        return

    print(f"DB: {db_path}")
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("\n--- DISTINCT STATUSES (Raw) ---")
        cursor.execute("SELECT DISTINCT status FROM sales")
        for row in cursor.fetchall():
            print(f"'{row[0]}'")

        print("\n--- Testing LOWER(status) Query ---")
        cursor.execute("SELECT count(*) FROM sales WHERE LOWER(status) = 'delivered'")
        delivered_count = cursor.fetchone()[0]
        print(f"LOWER(status)='delivered' count: {delivered_count}")

        cursor.execute("SELECT count(*) FROM sales WHERE status = 'delivered'")
        exact_lower_count = cursor.fetchone()[0]
        print(f"status='delivered' count: {exact_lower_count}")
        
        cursor.execute("SELECT count(*) FROM sales WHERE status = 'Delivered'")
        exact_upper_count = cursor.fetchone()[0]
        print(f"status='Delivered' count: {exact_upper_count}")

        conn.close()
    except Exception as e:
        print(f"Error inspecting DB: {e}")

if __name__ == "__main__":
    check_status_casing()
