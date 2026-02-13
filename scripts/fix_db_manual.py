import sqlite3
from pathlib import Path

# Path to the database
HOME_DIR = Path.home()
DB_PATH = HOME_DIR / ".brewerymanager" / "cache.db"

print(f"Repairing database at: {DB_PATH}")

try:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 1. Fix Spoilt Beer
    print("Fixing spoilt_beer table...")
    try:
        cursor.execute("DROP TABLE IF EXISTS spoilt_beer")
        cursor.execute('''
            CREATE TABLE spoilt_beer (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date_discovered TEXT,
                duty_month TEXT,
                batch_id TEXT,
                container_type TEXT,
                quantity INTEGER,
                duty_paid_volume REAL,
                pure_alcohol_litres REAL,
                original_duty_rate REAL,
                duty_to_reclaim REAL,
                reason_category TEXT,
                status TEXT,
                notes TEXT,
                recorded_by TEXT,
                created_at TEXT,
                sync_status TEXT DEFAULT 'synced',
                FOREIGN KEY (batch_id) REFERENCES batches(batch_id)
            )
        ''')
        print("✓ spoilt_beer recreated with 'duty_month'")
    except Exception as e:
        print(f"❌ Failed to fix spoilt_beer: {e}")

    # 2. Fix Batches (Add Columns)
    print("Fixing batches table...")
    columns = ['fermented_volume', 'packaged_volume', 'waste_volume']
    for col in columns:
        try:
            cursor.execute(f"SELECT {col} FROM batches LIMIT 1")
            print(f"✓ Column '{col}' exists")
        except sqlite3.OperationalError:
            try:
                cursor.execute(f"ALTER TABLE batches ADD COLUMN {col} REAL")
                print(f"✓ Added column '{col}'")
            except Exception as e:
                print(f"❌ Failed to add '{col}': {e}")
                
    # 3. Add batch_packaging_lines if missing
    print("Checking batch_packaging_lines...")
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS batch_packaging_lines (
            line_id INTEGER PRIMARY KEY AUTOINCREMENT,
            batch_id TEXT,
            gyle_number TEXT,
            packaging_date TEXT,
            container_type TEXT,
            quantity INTEGER,
            total_duty_volume REAL,
            batch_abv REAL,
            pure_alcohol_litres REAL,
            spr_category TEXT,
            effective_duty_rate REAL,
            duty_payable REAL,
            created_by TEXT,
            created_at TEXT,
            sync_status TEXT DEFAULT 'synced',
            FOREIGN KEY (batch_id) REFERENCES batches(batch_id)
        )
    ''')
    print("✓ batch_packaging_lines ensured")

    # 4. Fix Duty Returns (Add all missing columns)
    print("Fixing duty_returns table...")
    missing_cols = [
        'duty_month', 'net_duty_payable', 'production_duty_total', 'spoilt_duty_reclaim',
        'under_declarations', 'over_declarations',
        'draught_low_litres', 'draught_low_lpa', 'draught_low_duty',
        'draught_std_litres', 'draught_std_lpa', 'draught_std_duty',
        'non_draught_litres', 'non_draught_lpa', 'non_draught_duty',
        'high_abv_litres', 'high_abv_lpa', 'high_abv_duty'
    ]

    for col in missing_cols:
        try:
            cursor.execute(f"SELECT {col} FROM duty_returns LIMIT 1")
            print(f"✓ Column '{col}' exists")
        except sqlite3.OperationalError:
            try:
                cursor.execute(f"ALTER TABLE duty_returns ADD COLUMN {col} REAL")
                print(f"✓ Added column '{col}'")
            except Exception as e:
                print(f"❌ Failed to add '{col}': {e}")

    conn.commit()
    conn.close()
    print("\nSUCCESS: Database repair complete.")
except Exception as e:
    print(f"\nCRITICAL ERROR: {e}")
