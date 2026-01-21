
import sqlite3
import os
import sys

# Define path to the database
DB_PATH = r"C:\Users\darre\.brewerymanager\cache.db"

def verify_schema():
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("Verifying 'batches' table schema...")
    cursor.execute("PRAGMA table_info(batches)")
    columns = [info[1] for info in cursor.fetchall()]
    
    required_batches_cols = ['final_gravity', 'actual_abv', 'measured_abv', 'waste_percentage']
    missing_batches = [col for col in required_batches_cols if col not in columns]
    
    if missing_batches:
        print(f"❌ Missing columns in 'batches': {missing_batches}")
    else:
        print("✅ All required columns present in 'batches'")

    print("\nVerifying 'batch_packaging_lines' table schema...")
    cursor.execute("PRAGMA table_info(batch_packaging_lines)")
    columns = [info[1] for info in cursor.fetchall()]
    
    required_packaging_cols = [
        'container_actual_size', 
        'container_duty_volume', 
        'spr_rate_applied', 
        'full_duty_rate', 
        'is_draught_eligible'
    ]
    missing_packaging = [col for col in required_packaging_cols if col not in columns]
    
    if missing_packaging:
        print(f"❌ Missing columns in 'batch_packaging_lines': {missing_packaging}")
    else:
        print("✅ All required columns present in 'batch_packaging_lines'")

    conn.close()

    # Note: The database schema won't actually update until the app is run and initialize_database() is called.
    # This script is to be run AFTER the app has started or if we manually trigger the initialization code.
    
if __name__ == "__main__":
    verify_schema()
