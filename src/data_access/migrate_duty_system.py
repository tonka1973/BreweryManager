"""
Database Migration: Duty System Implementation
Adds all tables and fields for HMRC-compliant duty tracking system

Run this once to add:
- settings table (duty rates and SPR rates)
- settings_containers table (container configurations with sediment allowances)
- batch_packaging_lines table (multiple containers per batch with duty calculations)
- spoilt_beer table (post-packaging spoilage tracking for duty refunds)
- duty_returns table (monthly HMRC returns)
- batches table updates (waste tracking fields)
"""

import sqlite3
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.config.constants import CACHE_DB_PATH


def migrate():
    """Add all duty system tables and fields"""

    print("=" * 70)
    print("DUTY SYSTEM DATABASE MIGRATION")
    print("=" * 70)
    print(f"\nDatabase: {CACHE_DB_PATH}")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    try:
        conn = sqlite3.connect(CACHE_DB_PATH)
        cursor = conn.cursor()

        # ================================================================
        # TABLE 1: Settings (Duty Rates and SPR Rates)
        # ================================================================
        print("1. Creating settings table...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                id INTEGER PRIMARY KEY,

                -- Annual production tracking (auto-calculated)
                annual_production_hl_pa REAL DEFAULT 0.0,
                production_year_start TEXT DEFAULT '2025-02-01',
                production_year_end TEXT DEFAULT '2026-01-31',

                -- SPR RATES (£/lpa) - Manually entered effective rates for <8.5% ABV
                spr_draught_low REAL DEFAULT 2.46,
                spr_draught_standard REAL DEFAULT 4.89,
                spr_non_draught_standard REAL DEFAULT 5.38,

                -- FULL DUTY RATE (£/lpa) - Only for 8.5-22% ABV (no SPR applies)
                rate_full_8_5_to_22 REAL DEFAULT 29.54,

                -- VAT RATE (decimal, e.g., 0.20 = 20%)
                vat_rate REAL DEFAULT 0.20,

                -- Metadata
                rates_effective_from TEXT DEFAULT '2025-02-01',
                updated_at TEXT,
                updated_by TEXT
            )
        ''')

        # Insert default settings record
        cursor.execute('SELECT COUNT(*) FROM settings')
        if cursor.fetchone()[0] == 0:
            cursor.execute('''
                INSERT INTO settings (id, updated_at)
                VALUES (1, ?)
            ''', (datetime.now().isoformat(),))
            print("   ✓ Settings table created with default February 2025 rates")
        else:
            print("   ✓ Settings table already exists")

        # ================================================================
        # TABLE 2: Container Configuration (with sediment allowances)
        # ================================================================
        print("\n2. Creating settings_containers table...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS settings_containers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                actual_capacity REAL NOT NULL,
                duty_paid_volume REAL NOT NULL,
                is_draught_eligible INTEGER DEFAULT 0,
                default_price REAL DEFAULT 0.0,
                active INTEGER DEFAULT 1,
                updated_at TEXT,
                updated_by TEXT
            )
        ''')
        print("   ✓ Container configuration table created")

        # Insert default containers
        print("\n3. Inserting default container configurations...")
        default_containers = [
            ('Firkin', 40.9, 38.5, 1, 65.00),
            ('Pin', 20.5, 19.0, 1, 35.00),
            ('Kilderkin', 81.8, 77.0, 1, 120.00),
            ('Barrel', 163.6, 155.0, 1, 250.00),
            ('30L Keg', 30.0, 28.5, 1, 50.00),
            ('50L Keg', 50.0, 48.0, 1, 80.00),
            ('Bottle 330ml', 0.33, 0.33, 0, 2.50),
            ('Bottle 500ml', 0.50, 0.50, 0, 3.00),
            ('Bottle 750ml', 0.75, 0.75, 0, 4.00),
        ]

        for name, actual, duty_paid, draught, price in default_containers:
            try:
                sediment = actual - duty_paid
                cursor.execute('''
                    INSERT INTO settings_containers
                    (name, actual_capacity, duty_paid_volume, is_draught_eligible,
                     default_price, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (name, actual, duty_paid, draught, price, datetime.now().isoformat()))
                sediment_text = f" (sediment: {sediment:.1f}L)" if draught else ""
                print(f"   ✓ {name}: {actual:.2f}L → {duty_paid:.2f}L duty paid{sediment_text}")
            except sqlite3.IntegrityError:
                print(f"   - {name} already exists")

        # ================================================================
        # TABLE 3: Batch Packaging Lines (multiple containers per batch)
        # ================================================================
        print("\n4. Creating batch_packaging_lines table...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS batch_packaging_lines (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                batch_id TEXT NOT NULL,
                packaging_date TEXT NOT NULL,

                -- Container details
                container_type TEXT NOT NULL,
                quantity INTEGER NOT NULL,

                -- Volumes (snapshot from settings at packaging time)
                container_actual_size REAL,
                container_duty_volume REAL,
                total_duty_volume REAL,

                -- Batch details at packaging time
                batch_abv REAL,
                pure_alcohol_litres REAL,

                -- Duty calculation (snapshot at packaging time)
                spr_category TEXT,
                spr_rate_applied REAL,
                full_duty_rate REAL,
                effective_duty_rate REAL,
                duty_payable REAL,

                is_draught_eligible INTEGER,

                created_at TEXT DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY (batch_id) REFERENCES batches(batch_id)
            )
        ''')
        print("   ✓ Batch packaging lines table created")
        print("   ✓ Supports multiple container types per batch")
        print("   ✓ Snapshots rates at packaging time (immutable audit trail)")

        # ================================================================
        # TABLE 4: Update Batches Table (waste tracking)
        # ================================================================
        print("\n5. Updating batches table with waste tracking fields...")

        # Check existing columns
        cursor.execute("PRAGMA table_info(batches)")
        existing_columns = [col[1] for col in cursor.fetchall()]

        columns_to_add = [
            ('fermented_volume', 'REAL DEFAULT 0.0'),
            ('packaged_volume', 'REAL DEFAULT 0.0'),
            ('waste_volume', 'REAL DEFAULT 0.0'),
            ('waste_percentage', 'REAL DEFAULT 0.0'),
        ]

        for col_name, col_type in columns_to_add:
            if col_name not in existing_columns:
                cursor.execute(f"ALTER TABLE batches ADD COLUMN {col_name} {col_type}")
                print(f"   ✓ Added column: {col_name}")
            else:
                print(f"   - Column {col_name} already exists")

        # ================================================================
        # TABLE 5: Spoilt Beer (post-packaging spoilage tracking)
        # ================================================================
        print("\n6. Creating spoilt_beer table...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS spoilt_beer (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                -- Batch reference
                batch_id TEXT,
                gyle_number TEXT,

                -- When and which month
                date_discovered TEXT NOT NULL,
                duty_month TEXT NOT NULL,
                status TEXT DEFAULT 'pending',

                -- Container details
                container_type TEXT NOT NULL,
                quantity INTEGER NOT NULL,

                -- Volumes
                total_volume REAL,
                duty_paid_volume REAL,
                pure_alcohol_litres REAL,

                -- Duty calculation (from original packaging)
                spr_category TEXT,
                original_duty_rate REAL,
                duty_to_reclaim REAL,

                -- Reason for spoilage
                reason_category TEXT,
                reason_notes TEXT,

                -- Audit
                recorded_by TEXT,
                recorded_at TEXT DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY (batch_id) REFERENCES batches(batch_id)
            )
        ''')
        print("   ✓ Spoilt beer tracking table created")
        print("   ✓ Tracks post-packaging spoilage for duty refunds")

        # ================================================================
        # TABLE 6: Monthly Duty Returns
        # ================================================================
        print("\n7. Creating duty_returns table...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS duty_returns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                duty_month TEXT UNIQUE NOT NULL,

                -- Category 1: Draught <3.5% ABV
                draught_low_litres REAL DEFAULT 0.0,
                draught_low_lpa REAL DEFAULT 0.0,
                draught_low_duty REAL DEFAULT 0.0,

                -- Category 2: Draught 3.5-8.4% ABV
                draught_std_litres REAL DEFAULT 0.0,
                draught_std_lpa REAL DEFAULT 0.0,
                draught_std_duty REAL DEFAULT 0.0,

                -- Category 3: Non-Draught 3.5-8.4% ABV
                non_draught_litres REAL DEFAULT 0.0,
                non_draught_lpa REAL DEFAULT 0.0,
                non_draught_duty REAL DEFAULT 0.0,

                -- Category 4: Products ≥8.5% ABV (no SPR)
                high_abv_litres REAL DEFAULT 0.0,
                high_abv_lpa REAL DEFAULT 0.0,
                high_abv_duty REAL DEFAULT 0.0,

                -- Production total
                production_duty_total REAL DEFAULT 0.0,

                -- Adjustments
                spoilt_duty_reclaim REAL DEFAULT 0.0,
                under_declarations REAL DEFAULT 0.0,
                over_declarations REAL DEFAULT 0.0,

                -- Net duty payable
                net_duty_payable REAL DEFAULT 0.0,

                -- Status tracking
                status TEXT DEFAULT 'in_progress',
                submitted_date TEXT,
                payment_date TEXT,
                payment_reference TEXT,

                -- Audit
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT
            )
        ''')
        print("   ✓ Monthly duty returns table created")
        print("   ✓ Tracks 4 SPR categories + adjustments")

        # ================================================================
        # CREATE INDEXES
        # ================================================================
        print("\n8. Creating indexes for performance...")

        indexes = [
            ('idx_packaging_lines_batch', 'batch_packaging_lines', 'batch_id'),
            ('idx_packaging_lines_date', 'batch_packaging_lines', 'packaging_date'),
            ('idx_spoilt_beer_month', 'spoilt_beer', 'duty_month'),
            ('idx_spoilt_beer_batch', 'spoilt_beer', 'batch_id'),
            ('idx_duty_returns_month', 'duty_returns', 'duty_month'),
        ]

        for idx_name, table, column in indexes:
            cursor.execute(f'''
                CREATE INDEX IF NOT EXISTS {idx_name} ON {table}({column})
            ''')
            print(f"   ✓ Created index: {idx_name}")

        # ================================================================
        # COMMIT ALL CHANGES
        # ================================================================
        conn.commit()

        print("\n" + "=" * 70)
        print("✅ MIGRATION COMPLETED SUCCESSFULLY!")
        print("=" * 70)
        print("\nNew tables added:")
        print("  • settings                 - SPR rates (3) + Full rate (1) configuration")
        print("  • settings_containers      - Container specifications with sediment allowances")
        print("  • batch_packaging_lines    - Multiple containers per batch with duty calculations")
        print("  • spoilt_beer             - Post-packaging spoilage tracking for refunds")
        print("  • duty_returns            - Monthly HMRC duty returns")
        print("\nRate structure:")
        print("  • 3 SPR rates              - For beers <8.5% ABV (draught low, draught std, non-draught)")
        print("  • 1 Full rate              - For beers 8.5-22% ABV (no SPR discount)")
        print("\nBatches table updated:")
        print("  • fermented_volume        - Total volume after fermentation")
        print("  • packaged_volume         - Total volume packaged into containers")
        print("  • waste_volume            - Brewery losses (no duty paid)")
        print("  • waste_percentage        - Waste as percentage of fermented")
        print("\nThe duty system is now ready to use!")
        print("=" * 70)

        return True

    except sqlite3.Error as e:
        print(f"\n❌ ERROR: Database migration failed!")
        print(f"   {str(e)}")
        return False

    finally:
        if conn:
            conn.close()


if __name__ == "__main__":
    print("\n⚠️  WARNING: This migration will add new tables to your database.")
    print("   It is safe to run multiple times (will skip existing tables).\n")

    response = input("Continue with migration? (yes/no): ")
    if response.lower() == 'yes':
        success = migrate()
        sys.exit(0 if success else 1)
    else:
        print("\nMigration cancelled.")
        sys.exit(0)
