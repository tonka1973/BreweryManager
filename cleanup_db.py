
import sqlite3
import os
from pathlib import Path

def clean_database():
    home = Path.home()
    db_path = home / ".brewerymanager" / "cache.db"
    
    if not db_path.exists():
        print(f"DB not found at {db_path}")
        return

    print(f"Cleaning DB: {db_path}")
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Count before
        cursor.execute("SELECT count(*) FROM sales WHERE invoice_id = 'None'")
        before = cursor.fetchone()[0]
        print(f"Found {before} rows with invoice_id = 'None'")
        
        if before > 0:
            cursor.execute("UPDATE sales SET invoice_id = NULL WHERE invoice_id = 'None'")
            conn.commit()
            print(f"Updated {cursor.rowcount} rows to NULL")
        else:
            print("No rows to clean.")

        conn.close()
    except Exception as e:
        print(f"Error cleaning DB: {e}")

if __name__ == "__main__":
    clean_database()
