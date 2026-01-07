import sqlite3
from pathlib import Path

# Path to the database
HOME_DIR = Path.home()
DB_PATH = HOME_DIR / ".brewerymanager" / "cache.db"

print(f"Checking database at: {DB_PATH}")

if not DB_PATH.exists():
    print("Database file NOT found!")
else:
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        print(f"Found {len(tables)} tables:")
        for table in sorted(tables):
            print(f"- {table}")
            
        # Specific checks
        required = ['settings_containers', 'batch_packaging_lines', 'spoilt_beer', 'products']
        print("\nMissing required tables:")
        for req in required:
            if req not in tables:
                print(f"MISSING: {req}")
            else:
                print(f"OK: {req}")
                
        conn.close()
    except Exception as e:
        print(f"Error reading database: {e}")
