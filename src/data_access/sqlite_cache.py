# SQLite Cache Manager
# Manages local SQLite database that mirrors Google Sheets for offline access

import sqlite3
import logging
import json
from datetime import datetime
from pathlib import Path

from ..config.constants import CACHE_DB_PATH, TABLES, DATE_FORMAT, DATETIME_FORMAT

logger = logging.getLogger(__name__)


class SQLiteCacheManager:
    """
    Manages local SQLite database that serves as a cache for Google Sheets.
    Enables offline functionality by storing all data locally.
    """
    
    def __init__(self):
        self.db_path = CACHE_DB_PATH
        self.connection = None
        self.cursor = None
        
    def connect(self):
        """
        Connect to the SQLite database.
        Creates the database file if it doesn't exist.
        """
        try:
            # Ensure directory exists
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Connect to database
            self.connection = sqlite3.connect(self.db_path)
            self.connection.row_factory = sqlite3.Row  # Access columns by name
            self.cursor = self.connection.cursor()
            
            logger.info(f"Connected to SQLite database at {self.db_path}")
            
            # Enable WAL mode for better concurrency (UI reads + Background writes)
            self.connection.execute("PRAGMA journal_mode=WAL;")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to SQLite database: {str(e)}")
            return False
    
    def close(self):
        """Close the database connection."""
        if self.connection:
            self.connection.close()
            logger.info("Closed SQLite database connection")
    
    def initialize_database(self):
        """
        Create all required tables in the database.
        This is called once during initial setup.
        """
        try:
            # Batches table
            # Check for missing columns (Schema Migration - Batches)
            try:
                self.cursor.execute("SELECT fermented_volume FROM batches LIMIT 1")
            except sqlite3.OperationalError:
                try:
                    logger.info("Migrating batches table...")
                    self.cursor.execute("ALTER TABLE batches ADD COLUMN fermented_volume REAL")
                    self.cursor.execute("ALTER TABLE batches ADD COLUMN packaged_volume REAL")
                    self.cursor.execute("ALTER TABLE batches ADD COLUMN waste_volume REAL")
                except Exception as e:
                    logger.error(f"Migration error (batches): {e}")

            # Check for original_gravity (Schema Migration - Batches Update)
            try:
                self.cursor.execute("SELECT original_gravity FROM batches LIMIT 1")
            except sqlite3.OperationalError:
                try:
                    logger.info("Migrating batches table (adding original_gravity)...")
                    self.cursor.execute("ALTER TABLE batches ADD COLUMN original_gravity REAL")
                except Exception as e:
                    logger.error(f"Migration error (batches OG): {e}")

            # Check for final_gravity and ABVs (Schema Migration - Batches Packaging)
            try:
                self.cursor.execute("SELECT final_gravity FROM batches LIMIT 1")
            except sqlite3.OperationalError:
                try:
                    logger.info("Migrating batches table (adding packaging columns)...")
                    self.cursor.execute("ALTER TABLE batches ADD COLUMN final_gravity REAL")
                    self.cursor.execute("ALTER TABLE batches ADD COLUMN actual_abv REAL")
                    self.cursor.execute("ALTER TABLE batches ADD COLUMN measured_abv REAL")
                    self.cursor.execute("ALTER TABLE batches ADD COLUMN waste_percentage REAL")
                except Exception as e:
                    logger.error(f"Migration error (batches packaging): {e}")

            # Check for waste_percentage (Schema Migration - Batches Waste)
            try:
                self.cursor.execute("SELECT waste_percentage FROM batches LIMIT 1")
            except sqlite3.OperationalError:
                try:
                    logger.info("Migrating batches table (adding waste_percentage)...")
                    self.cursor.execute("ALTER TABLE batches ADD COLUMN waste_percentage REAL")
                except Exception as e:
                    logger.error(f"Migration error (batches waste_percentage): {e}")

            # Check for missing columns (Schema Migration - Recipes)
            try:
                self.cursor.execute("SELECT allergens FROM recipes LIMIT 1")
            except sqlite3.OperationalError:
                try:
                    logger.info("Migrating recipes table...")
                    self.cursor.execute("ALTER TABLE recipes ADD COLUMN allergens TEXT")
                except Exception as e:
                    logger.error(f"Migration error (recipes): {e}")

            # Check for ingredient_source_batches (Schema Migration - Batches Warning System)
            try:
                self.cursor.execute("SELECT ingredient_source_batches FROM batches LIMIT 1")
            except sqlite3.OperationalError:
                try:
                    logger.info("Migrating batches table (adding ingredient_source_batches)...")
                    self.cursor.execute("ALTER TABLE batches ADD COLUMN ingredient_source_batches TEXT")
                except Exception as e:
                    logger.error(f"Migration error (batches ingredient_source_batches): {e}")

            # Check for delivery_area (Schema Migration - Customers)
            try:
                self.cursor.execute("SELECT delivery_area FROM customers LIMIT 1")
            except sqlite3.OperationalError:
                try:
                    logger.info("Migrating customers table (adding delivery_area)...")
                    self.cursor.execute("ALTER TABLE customers ADD COLUMN delivery_area TEXT")
                except Exception as e:
                    logger.error(f"Migration error (customers delivery_area): {e}")

            # Delivery Runs table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS delivery_runs (
                    run_id TEXT PRIMARY KEY,
                    run_name TEXT NOT NULL,
                    day_of_week TEXT,
                    area_id TEXT,
                    description TEXT,
                    driver_name TEXT,
                    sync_status TEXT DEFAULT 'synced'
                )
            ''')

            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS batches (
                    batch_id TEXT PRIMARY KEY,
                    gyle_number TEXT UNIQUE NOT NULL,
                    recipe_id TEXT,
                    brew_date TEXT,
                    brewer_name TEXT,
                    actual_batch_size REAL,
                    measured_abv REAL,
                    pure_alcohol_litres REAL,
                    status TEXT,
                    fermenting_start TEXT,
                    conditioning_start TEXT,
                    ready_date TEXT,
                    packaged_date TEXT,
                    fermented_volume REAL,
                    packaged_volume REAL,
                    waste_volume REAL,
                    original_gravity REAL,
                    final_gravity REAL,
                    actual_abv REAL,
                    measured_abv REAL,
                    waste_percentage REAL,
                    spr_rate_applied REAL,
                    duty_rate_applied REAL,
                    is_draught INTEGER,
                    brewing_notes TEXT,
                    created_by TEXT,
                    last_modified TEXT,
                    sync_status TEXT DEFAULT 'synced',
                    ingredient_source_batches TEXT
                )
            ''')
            
            # Recipes table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS recipes (
                    recipe_id TEXT PRIMARY KEY,
                    recipe_name TEXT NOT NULL,
                    style TEXT,
                    version INTEGER,
                    target_abv REAL,
                    target_batch_size_litres REAL,
                    created_date TEXT,
                    created_by TEXT,
                    last_modified TEXT,
                    is_active INTEGER DEFAULT 1,
                    brewing_notes TEXT,
                    allergens TEXT,
                    sync_status TEXT DEFAULT 'synced'
                )
            ''')
            
            # Recipe Ingredients table (Legacy/Unified for GUI)
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS recipe_ingredients (
                    ingredient_id TEXT PRIMARY KEY,
                    recipe_id TEXT,
                    ingredient_name TEXT,
                    ingredient_type TEXT,
                    quantity REAL,
                    unit TEXT,
                    timing TEXT,
                    notes TEXT,
                    inventory_item_id TEXT,
                    sync_status TEXT DEFAULT 'synced',
                    FOREIGN KEY (recipe_id) REFERENCES recipes(recipe_id)
                )
            ''')
            
            # Recipe Grains table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS recipe_grains (
                    grain_id TEXT PRIMARY KEY,
                    recipe_id TEXT,
                    material_id TEXT,
                    quantity REAL,
                    unit TEXT,
                    mash_notes TEXT,
                    sync_status TEXT DEFAULT 'synced',
                    FOREIGN KEY (recipe_id) REFERENCES recipes(recipe_id),
                    FOREIGN KEY (material_id) REFERENCES inventory_materials(material_id)
                )
            ''')

            # Recipe Hops table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS recipe_hops (
                    hop_id TEXT PRIMARY KEY,
                    recipe_id TEXT,
                    material_id TEXT,
                    quantity REAL,
                    unit TEXT,
                    boil_time_minutes REAL,
                    alpha_acid_percent REAL,
                    addition_type TEXT,
                    sync_status TEXT DEFAULT 'synced',
                    FOREIGN KEY (recipe_id) REFERENCES recipes(recipe_id),
                    FOREIGN KEY (material_id) REFERENCES inventory_materials(material_id)
                )
            ''')

            # Recipe Yeast table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS recipe_yeast (
                    yeast_id TEXT PRIMARY KEY,
                    recipe_id TEXT,
                    material_id TEXT,
                    quantity REAL,
                    unit TEXT,
                    notes TEXT,
                    sync_status TEXT DEFAULT 'synced',
                    FOREIGN KEY (recipe_id) REFERENCES recipes(recipe_id),
                    FOREIGN KEY (material_id) REFERENCES inventory_materials(material_id)
                )
            ''')

            # Recipe Adjuncts table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS recipe_adjuncts (
                    adjunct_id TEXT PRIMARY KEY,
                    recipe_id TEXT,
                    material_id TEXT,
                    quantity REAL,
                    unit TEXT,
                    timing TEXT,
                    sync_status TEXT DEFAULT 'synced',
                    FOREIGN KEY (recipe_id) REFERENCES recipes(recipe_id),
                    FOREIGN KEY (material_id) REFERENCES inventory_materials(material_id)
                )
            ''')
            
            # Inventory Materials table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS inventory_materials (
                    material_id TEXT PRIMARY KEY,
                    material_type TEXT,
                    material_name TEXT UNIQUE NOT NULL,
                    current_stock REAL DEFAULT 0,
                    unit TEXT,
                    reorder_level REAL,
                    last_updated TEXT,
                    supplier TEXT,
                    cost_per_unit REAL,
                    sync_status TEXT DEFAULT 'synced'
                )
            ''')
            
            # Inventory Batches table (New - FIFO Tracking)
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS inventory_batches (
                    batch_id TEXT PRIMARY KEY,
                    material_id TEXT,
                    batch_number TEXT,
                    expiry_date TEXT,
                    quantity_initial REAL,
                    quantity_remaining REAL,
                    received_date TEXT,
                    sync_status TEXT DEFAULT 'synced',
                    FOREIGN KEY (material_id) REFERENCES inventory_materials(material_id)
                )
            ''')

            # Migration: Create Legacy Batches for existing stock
            try:
                # Check if inventory_batches is empty
                self.cursor.execute("SELECT COUNT(*) FROM inventory_batches")
                count = self.cursor.fetchone()[0]
                if count == 0:
                    logger.info("Migrating existing inventory to legacy batches...")
                    # Get all materials with stock > 0
                    self.cursor.execute("SELECT material_id, current_stock, last_updated FROM inventory_materials WHERE current_stock > 0")
                    items = self.cursor.fetchall()
                    
                    for item in items:
                        import uuid
                        batch_id = str(uuid.uuid4())
                        # Create a "Legacy" batch for the current stock
                        self.cursor.execute('''
                            INSERT INTO inventory_batches (batch_id, material_id, batch_number, quantity_initial, quantity_remaining, received_date, sync_status)
                            VALUES (?, ?, ?, ?, ?, ?, ?)
                        ''', (batch_id, item['material_id'], 'LEGACY-STOCK', item['current_stock'], item['current_stock'], item['last_updated'] or get_today_db(), 'pending'))
                    
                    self.cursor.connection.commit()
            except Exception as e:
                logger.error(f"Migration error (legacy inventory batches): {e}")
            
            # Inventory Transactions table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS inventory_transactions (
                    transaction_id TEXT PRIMARY KEY,
                    transaction_date TEXT,
                    transaction_type TEXT,
                    material_id TEXT,
                    quantity_change REAL,
                    new_balance REAL,
                    reference TEXT,
                    username TEXT,
                    notes TEXT,
                    sync_status TEXT DEFAULT 'synced',
                    FOREIGN KEY (material_id) REFERENCES inventory_materials(material_id)
                )
            ''')
            
            # Customers table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS customers (
                    customer_id TEXT PRIMARY KEY,
                    customer_name TEXT NOT NULL,
                    contact_person TEXT,
                    phone TEXT,
                    email TEXT,
                    delivery_address TEXT,
                    billing_address TEXT,
                    customer_type TEXT,
                    payment_terms TEXT,
                    credit_limit REAL,
                    preferred_delivery_day TEXT,
                    preferred_delivery_time TEXT,
                    likes TEXT,
                    dislikes TEXT,
                    notes TEXT,
                    is_active INTEGER DEFAULT 1,
                    created_date TEXT,
                    sync_status TEXT DEFAULT 'synced'
                )
            ''')
            
            # Sales table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS sales (
                    sale_id TEXT PRIMARY KEY,
                    sale_date TEXT,
                    customer_id TEXT,
                    batch_id TEXT,
                    gyle_number TEXT,
                    beer_name TEXT,
                    container_type TEXT,
                    container_size REAL,
                    quantity INTEGER,
                    total_litres REAL,
                    unit_price REAL,
                    line_total REAL,
                    status TEXT DEFAULT 'reserved',
                    reserved_date TEXT,
                    delivery_date TEXT,
                    invoice_id TEXT,
                    recorded_by TEXT,
                    notes TEXT,
                    sync_status TEXT DEFAULT 'synced',
                    FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
                    FOREIGN KEY (batch_id) REFERENCES batches(batch_id)
                )
            ''')
            
            # Invoices table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS invoices (
                    invoice_id TEXT PRIMARY KEY,
                    invoice_number TEXT UNIQUE NOT NULL,
                    invoice_date TEXT,
                    customer_id TEXT,
                    subtotal REAL,
                    vat_rate REAL,
                    vat_amount REAL,
                    total REAL,
                    payment_status TEXT DEFAULT 'unpaid',
                    amount_paid REAL DEFAULT 0,
                    amount_outstanding REAL,
                    due_date TEXT,
                    created_by TEXT,
                    created_date TEXT,
                    notes TEXT,
                    sync_status TEXT DEFAULT 'synced',
                    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
                )
            ''')
            
            # Invoice Lines table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS invoice_lines (
                    line_id TEXT PRIMARY KEY,
                    invoice_id TEXT,
                    sale_id TEXT,
                    description TEXT,
                    quantity REAL,
                    unit_price REAL,
                    line_total REAL,
                    gyle_number TEXT,
                    sync_status TEXT DEFAULT 'synced',
                    FOREIGN KEY (invoice_id) REFERENCES invoices(invoice_id)
                )
            ''')
            
            # Payments table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS payments (
                    payment_id TEXT PRIMARY KEY,
                    invoice_id TEXT,
                    payment_date TEXT,
                    payment_amount REAL,
                    payment_method TEXT,
                    payment_reference TEXT,
                    recorded_by TEXT,
                    recorded_date TEXT,
                    notes TEXT,
                    sync_status TEXT DEFAULT 'synced',
                    FOREIGN KEY (invoice_id) REFERENCES invoices(invoice_id)
                )
            ''')
            
            # Users table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id TEXT PRIMARY KEY,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    full_name TEXT,
                    role TEXT,
                    is_active INTEGER DEFAULT 1,
                    created_date TEXT,
                    last_login TEXT,
                    sync_status TEXT DEFAULT 'synced'
                )
            ''')
            
            # Settings table (for duty rates and configuration)
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS settings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    annual_production_hl_pa REAL DEFAULT 0,
                    production_year_start TEXT,
                    production_year_end TEXT,
                    spr_draught_low REAL DEFAULT 0,
                    spr_draught_standard REAL DEFAULT 0,
                    spr_non_draught_standard REAL DEFAULT 0,
                    rate_full_8_5_to_22 REAL DEFAULT 0,
                    rates_effective_from TEXT,
                    vat_rate REAL DEFAULT 0.20,
                    updated_at TEXT,
                    updated_by TEXT,
                    sync_status TEXT DEFAULT 'synced'
                )
            ''')

            # System Settings table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS system_settings (
                    setting_key TEXT PRIMARY KEY,
                    setting_value TEXT,
                    setting_type TEXT,
                    description TEXT,
                    last_updated TEXT,
                    sync_status TEXT DEFAULT 'synced'
                )
            ''')
            
            # Casks Empty table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS casks_empty (
                    cask_id TEXT PRIMARY KEY,
                    cask_size TEXT,
                    cask_size_litres REAL,
                    quantity_in_stock INTEGER DEFAULT 0,
                    condition TEXT,
                    last_updated TEXT,
                    notes TEXT,
                    sync_status TEXT DEFAULT 'synced'
                )
            ''')

            # Bottles Empty table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS bottles_empty (
                    bottle_id TEXT PRIMARY KEY,
                    bottle_size_ml INTEGER,
                    quantity_in_stock INTEGER DEFAULT 0,
                    condition TEXT,
                    last_updated TEXT,
                    notes TEXT,
                    sync_status TEXT DEFAULT 'synced'
                )
            ''')

            # Cans Empty table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS cans_empty (
                    can_id TEXT PRIMARY KEY,
                    can_size_ml INTEGER,
                    quantity_in_stock INTEGER DEFAULT 0,
                    condition TEXT,
                    last_updated TEXT,
                    notes TEXT,
                    sync_status TEXT DEFAULT 'synced'
                )
            ''')

            # Settings Containers table (for duty calculations)
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS settings_containers (
                    container_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    actual_capacity REAL NOT NULL,
                    duty_paid_volume REAL NOT NULL,
                    is_draught_eligible INTEGER DEFAULT 0,
                    default_price REAL DEFAULT 0,
                    active INTEGER DEFAULT 1,
                    sync_status TEXT DEFAULT 'synced'
                )
            ''')

            # Container Types table (unified container management)
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS container_types (
                    container_type_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    size_litres REAL NOT NULL,
                    category TEXT,
                    quantity_available INTEGER DEFAULT 0,
                    active INTEGER DEFAULT 1,
                    created_date TEXT,
                    last_modified TEXT,
                    sync_status TEXT DEFAULT 'synced'
                )
            ''')

            # Products table (finished goods tracking)
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS products (
                    product_id TEXT PRIMARY KEY,
                    gyle_number TEXT NOT NULL,
                    batch_id TEXT,
                    recipe_id TEXT,
                    product_name TEXT,
                    style TEXT,
                    container_type TEXT,
                    container_size_l REAL,
                    quantity_total INTEGER,
                    quantity_in_stock INTEGER,
                    quantity_sold INTEGER DEFAULT 0,
                    abv REAL,
                    date_packaged TEXT,
                    date_in_stock TEXT,
                    status TEXT,
                    is_name_locked INTEGER DEFAULT 0,
                    created_date TEXT,
                    created_by TEXT,
                    last_modified TEXT,
                    sync_status TEXT DEFAULT 'synced',
                    FOREIGN KEY (batch_id) REFERENCES batches(batch_id),
                    FOREIGN KEY (recipe_id) REFERENCES recipes(recipe_id)
                )
            ''')

            # Product Sales table (for recall tracking)
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS product_sales (
                    product_sale_id TEXT PRIMARY KEY,
                    product_id TEXT NOT NULL,
                    gyle_number TEXT NOT NULL,
                    sale_id TEXT,
                    customer_id TEXT,
                    invoice_id TEXT,
                    quantity_sold INTEGER,
                    date_sold TEXT,
                    date_delivered TEXT,
                    delivery_address TEXT,
                    container_type TEXT,
                    created_date TEXT,
                    sync_status TEXT DEFAULT 'synced',
                    FOREIGN KEY (product_id) REFERENCES products(product_id),
                    FOREIGN KEY (sale_id) REFERENCES sales(sale_id),
                    FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
                    FOREIGN KEY (invoice_id) REFERENCES invoices(invoice_id)
                )
            ''')

            # Batch Packaging Lines (for duty calculations)
            # Check for missing columns (Schema Migration - Packaging Lines)
            try:
                self.cursor.execute("SELECT container_actual_size FROM batch_packaging_lines LIMIT 1")
            except sqlite3.OperationalError:
                try:
                    # Check if table exists first before trying to alter
                    self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='batch_packaging_lines'")
                    if self.cursor.fetchone():
                        logger.info("Migrating batch_packaging_lines table...")
                        try:
                            self.cursor.execute("ALTER TABLE batch_packaging_lines ADD COLUMN container_actual_size REAL")
                        except: pass
                        try:
                            self.cursor.execute("ALTER TABLE batch_packaging_lines ADD COLUMN container_duty_volume REAL")
                        except: pass
                        try:
                            self.cursor.execute("ALTER TABLE batch_packaging_lines ADD COLUMN spr_rate_applied REAL")
                        except: pass
                        try:
                            self.cursor.execute("ALTER TABLE batch_packaging_lines ADD COLUMN full_duty_rate REAL")
                        except: pass
                        try:
                            self.cursor.execute("ALTER TABLE batch_packaging_lines ADD COLUMN is_draught_eligible INTEGER")
                        except: pass
                except Exception as e:
                    logger.error(f"Migration error (batch_packaging_lines): {e}")

            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS batch_packaging_lines (
                    line_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    batch_id TEXT,
                    gyle_number TEXT,
                    packaging_date TEXT,
                    container_type TEXT,
                    quantity INTEGER,
                    container_actual_size REAL,
                    container_duty_volume REAL,
                    total_duty_volume REAL,
                    batch_abv REAL,
                    pure_alcohol_litres REAL,
                    spr_category TEXT,
                    spr_rate_applied REAL,
                    full_duty_rate REAL,
                    effective_duty_rate REAL,
                    duty_payable REAL,
                    is_draught_eligible INTEGER,
                    created_by TEXT,
                    created_at TEXT,
                    sync_status TEXT DEFAULT 'synced',
                    FOREIGN KEY (batch_id) REFERENCES batches(batch_id)
                )
            ''')

            # Spoilt Beer (for duty reclaim)
            # Check if table exists but might be missing columns (migration fix)
            try:
                self.cursor.execute("SELECT duty_month FROM spoilt_beer LIMIT 1")
            except sqlite3.OperationalError:
                # Column missing or table doesn't exist. safe to drop and recreate for this fix as table is likely empty/broken
                self.cursor.execute("DROP TABLE IF EXISTS spoilt_beer")
            
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS spoilt_beer (
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

            # Fermentation Logs table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS fermentation_logs (
                    log_id TEXT PRIMARY KEY,
                    batch_id TEXT,
                    gyle_number TEXT,
                    log_date TEXT,
                    temperature REAL,
                    gravity REAL,
                    ph REAL,
                    notes TEXT,
                    recorded_by TEXT,
                    sync_status TEXT DEFAULT 'synced',
                    FOREIGN KEY (batch_id) REFERENCES batches(batch_id)
                )
            ''')
            
            # Casks Full table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS casks_full (
                    cask_record_id TEXT PRIMARY KEY,
                    batch_id TEXT,
                    gyle_number TEXT,
                    beer_name TEXT,
                    abv REAL,
                    packaged_date TEXT,
                    cask_type TEXT,
                    cask_size_litres REAL,
                    quantity INTEGER DEFAULT 0,
                    status TEXT DEFAULT 'in_stock',
                    reserved_for_customer TEXT,
                    location TEXT,
                    notes TEXT,
                    sync_status TEXT DEFAULT 'synced',
                    FOREIGN KEY (batch_id) REFERENCES batches(batch_id)
                )
            ''')
            
            # Bottles Stock table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS bottles_stock (
                    bottle_record_id TEXT PRIMARY KEY,
                    batch_id TEXT,
                    gyle_number TEXT,
                    beer_name TEXT,
                    abv REAL,
                    packaged_date TEXT,
                    bottle_size_ml INTEGER,
                    quantity INTEGER DEFAULT 0,
                    status TEXT DEFAULT 'in_stock',
                    reserved_for_customer TEXT,
                    location TEXT,
                    notes TEXT,
                    sync_status TEXT DEFAULT 'synced',
                    FOREIGN KEY (batch_id) REFERENCES batches(batch_id)
                )
            ''')
            
            # Sales Calendar table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS sales_calendar (
                    event_id TEXT PRIMARY KEY,
                    event_date TEXT,
                    event_time TEXT,
                    event_type TEXT,
                    customer_id TEXT,
                    customer_name TEXT,
                    subject TEXT,
                    description TEXT,
                    location TEXT,
                    reminder_time TEXT,
                    completed INTEGER DEFAULT 0,
                    created_by TEXT,
                    created_date TEXT,
                    sync_status TEXT DEFAULT 'synced',
                    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
                )
            ''')
            
            # Call Log table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS call_log (
                    call_id TEXT PRIMARY KEY,
                    call_date TEXT,
                    call_time TEXT,
                    customer_id TEXT,
                    customer_name TEXT,
                    call_type TEXT,
                    duration_minutes INTEGER,
                    outcome TEXT,
                    notes TEXT,
                    follow_up_required INTEGER DEFAULT 0,
                    follow_up_date TEXT,
                    recorded_by TEXT,
                    sync_status TEXT DEFAULT 'synced',
                    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
                )
            ''')
            
            # Tasks table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS tasks (
                    task_id TEXT PRIMARY KEY,
                    task_title TEXT NOT NULL,
                    task_description TEXT,
                    customer_id TEXT,
                    customer_name TEXT,
                    priority TEXT,
                    due_date TEXT,
                    assigned_to TEXT,
                    status TEXT DEFAULT 'pending',
                    completed_date TEXT,
                    created_by TEXT,
                    created_date TEXT,
                    notes TEXT,
                    sync_status TEXT DEFAULT 'synced',
                    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
                )
            ''')
            
            # Sales Pipeline table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS sales_pipeline (
                    opportunity_id TEXT PRIMARY KEY,
                    customer_id TEXT,
                    customer_name TEXT,
                    opportunity_name TEXT,
                    stage TEXT,
                    estimated_value REAL,
                    probability INTEGER,
                    expected_close_date TEXT,
                    notes TEXT,
                    created_by TEXT,
                    created_date TEXT,
                    last_updated TEXT,
                    status TEXT DEFAULT 'active',
                    sync_status TEXT DEFAULT 'synced',
                    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
                )
            ''')
            
            # Duty Returns table
            # Duty Returns table
            # Check for missing columns (Schema Migration)
            missing_cols = [
                'duty_month', 'net_duty_payable', 'production_duty_total', 'spoilt_duty_reclaim',
                'under_declarations', 'over_declarations',
                'draught_low_litres', 'draught_low_lpa', 'draught_low_duty',
                'draught_std_litres', 'draught_std_lpa', 'draught_std_duty',
                'non_draught_litres', 'non_draught_lpa', 'non_draught_duty',
                'high_abv_litres', 'high_abv_lpa', 'high_abv_duty'
            ]
            
            try:
                # Check what we have
                self.cursor.execute("SELECT * FROM duty_returns LIMIT 1")
                existing_cols = [description[0] for description in self.cursor.description]
                
                for col in missing_cols:
                    if col not in existing_cols:
                        try:
                            logger.info(f"Adding missing column to duty_returns: {col}")
                            self.cursor.execute(f"ALTER TABLE duty_returns ADD COLUMN {col} REAL")
                        except Exception as e:
                            logger.error(f"Migration error (duty_returns {col}): {e}")
            except sqlite3.OperationalError:
                # Table might not exist yet, CREATE will handle it
                pass

            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS duty_returns (
                    return_id TEXT PRIMARY KEY,
                    duty_month TEXT,
                    return_period_start TEXT,
                    return_period_end TEXT,
                    total_duty_payable REAL,
                    submitted_date TEXT,
                    submitted_by TEXT,
                    payment_date TEXT,
                    payment_reference TEXT,
                    status TEXT DEFAULT 'draft',
                    notes TEXT,
                    
                    draught_low_litres REAL DEFAULT 0,
                    draught_low_lpa REAL DEFAULT 0,
                    draught_low_duty REAL DEFAULT 0,
                    
                    draught_std_litres REAL DEFAULT 0,
                    draught_std_lpa REAL DEFAULT 0,
                    draught_std_duty REAL DEFAULT 0,
                    
                    non_draught_litres REAL DEFAULT 0,
                    non_draught_lpa REAL DEFAULT 0,
                    non_draught_duty REAL DEFAULT 0,
                    
                    high_abv_litres REAL DEFAULT 0,
                    high_abv_lpa REAL DEFAULT 0,
                    high_abv_duty REAL DEFAULT 0,
                    
                    production_duty_total REAL DEFAULT 0,
                    spoilt_duty_reclaim REAL DEFAULT 0,
                    under_declarations REAL DEFAULT 0,
                    over_declarations REAL DEFAULT 0,
                    net_duty_payable REAL DEFAULT 0,
                    
                    sync_status TEXT DEFAULT 'synced'
                )
            ''')
            
            # Duty Return Lines table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS duty_return_lines (
                    line_id TEXT PRIMARY KEY,
                    return_id TEXT,
                    batch_id TEXT,
                    gyle_number TEXT,
                    beer_name TEXT,
                    abv REAL,
                    volume_litres REAL,
                    pure_alcohol_litres REAL,
                    is_draught INTEGER,
                    duty_rate_applied REAL,
                    spr_rate_applied REAL,
                    duty_amount REAL,
                    packaged_date TEXT,
                    sync_status TEXT DEFAULT 'synced',
                    FOREIGN KEY (return_id) REFERENCES duty_returns(return_id),
                    FOREIGN KEY (batch_id) REFERENCES batches(batch_id)
                )
            ''')
            
            # Pricing table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS pricing (
                    price_id TEXT PRIMARY KEY,
                    container_type TEXT UNIQUE NOT NULL,
                    container_size_litres REAL,
                    base_price REAL,
                    effective_date TEXT,
                    last_updated TEXT,
                    sync_status TEXT DEFAULT 'synced'
                )
            ''')
            
            # Customer Pricing Overrides table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS customer_pricing_overrides (
                    override_id TEXT PRIMARY KEY,
                    customer_id TEXT,
                    container_type TEXT,
                    custom_price REAL,
                    effective_date TEXT,
                    expiry_date TEXT,
                    notes TEXT,
                    last_updated TEXT,
                    sync_status TEXT DEFAULT 'synced',
                    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
                )
            ''')
            
            # Audit Log table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS audit_log (
                    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT,
                    username TEXT,
                    action TEXT,
                    table_name TEXT,
                    record_id TEXT,
                    old_value TEXT,
                    new_value TEXT,
                    ip_address TEXT
                )
            ''')
            
            # Sync Queue table (for tracking pending syncs)
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS sync_queue (
                    queue_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    table_name TEXT,
                    record_id TEXT,
                    operation TEXT,
                    data TEXT,
                    timestamp TEXT,
                    attempts INTEGER DEFAULT 0,
                    last_attempt TEXT
                )
            ''')

            # Seed default data
            self._seed_defaults()
            
            self.connection.commit()
            logger.info("Database tables initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize database: {str(e)}")
            return False

    def _seed_defaults(self):
        """Insert default data if tables are empty"""
        try:
            # Seed Settings
            count = self.cursor.execute("SELECT COUNT(*) FROM settings").fetchone()[0]
            if count == 0:
                self.cursor.execute("""
                    INSERT INTO settings (
                        annual_production_hl_pa, production_year_start, production_year_end,
                        spr_draught_low, spr_draught_standard, spr_non_draught_standard,
                        rate_full_8_5_to_22, rates_effective_from, vat_rate, updated_at, updated_by
                    ) VALUES (
                        0, '2025-02-01', '2026-01-31',
                        10.01, 19.08, 21.01, 25.80, '2025-02-01', 0.20, ?, 'System'
                    )
                """, (datetime.now().isoformat(),))
                logger.info("Seeded default settings")

            # Seed Settings Containers
            count = self.cursor.execute("SELECT COUNT(*) FROM settings_containers").fetchone()[0]
            if count == 0:
                containers = [
                    ('Cask 9G (Firkin)', 40.91, 39.50, 1, 120.00),
                    ('Cask 18G (Kilderkin)', 81.82, 79.00, 1, 230.00),
                    ('Keg 30L', 30.00, 30.00, 1, 110.00),
                    ('Keg 50L', 50.00, 50.00, 1, 175.00),
                    ('Can 440ml', 0.44, 0.44, 0, 3.50),
                    ('Bottle 500ml', 0.50, 0.50, 0, 3.80)
                ]
                self.cursor.executemany("""
                    INSERT INTO settings_containers (name, actual_capacity, duty_paid_volume, is_draught_eligible, default_price)
                    VALUES (?, ?, ?, ?, ?)
                """, containers)
                logger.info("Seeded default containers")
                
        except Exception as e:
            logger.error(f"Failed to seed defaults: {e}")
    
    def insert_record(self, table_name, data):
        """
        Insert a new record into a table.
        
        Args:
            table_name: Name of the table
            data: Dictionary of column:value pairs
        
        Returns:
            True if successful, False otherwise
        """
        try:
            columns = ', '.join(data.keys())
            placeholders = ', '.join(['?' for _ in data])
            query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
            
            self.cursor.execute(query, list(data.values()))
            self.connection.commit()
            return True
            
        except Exception as e:
            logger.error(f"Failed to insert record into {table_name}: {str(e)}")
            return False
    
    def update_record(self, table_name, record_id, data, id_column='id'):
        """
        Update an existing record.
        
        Args:
            table_name: Name of the table
            record_id: ID of the record to update
            data: Dictionary of column:value pairs to update
            id_column: Name of the ID column (default: 'id')
        
        Returns:
            True if successful, False otherwise
        """
        try:
            set_clause = ', '.join([f"{k} = ?" for k in data.keys()])
            query = f"UPDATE {table_name} SET {set_clause} WHERE {id_column} = ?"
            
            values = list(data.values()) + [record_id]
            self.cursor.execute(query, values)
            self.connection.commit()
            return True
            
        except Exception as e:
            logger.error(f"Failed to update record in {table_name}: {str(e)}")
            return False

    def update_record_by_id_column(self, table_name, record_id, data):
        """
        Update a record by automatically determining the primary key column.
        Useful for generic sync updating.
        """
        try:
            # 1. Try common pattern: table_name (singular) + "_id"
            # simple singular conversion
            singular = table_name[:-1] if table_name.endswith('s') else table_name
            candidate_id = f"{singular}_id"
            
            # Verify if this column exists
            self.cursor.execute(f"PRAGMA table_info({table_name})")
            columns = [info[1] for info in self.cursor.fetchall()]
            
            id_col = 'id' # Default
            if candidate_id in columns:
                id_col = candidate_id
            elif columns:
                # Fallback: assume first column is PK
                id_col = columns[0]
                
            return self.update_record(table_name, record_id, data, id_column=id_col)
            
        except Exception as e:
            logger.error(f"Failed to auto-update record in {table_name}: {e}")
            return False
    
    def get_record(self, table_name, record_id, id_column='id'):
        """
        Get a single record by ID.
        
        Args:
            table_name: Name of the table
            record_id: ID of the record
            id_column: Name of the ID column
        
        Returns:
            Dictionary of the record, or None if not found
        """
        try:
            query = f"SELECT * FROM {table_name} WHERE {id_column} = ?"
            self.cursor.execute(query, (record_id,))
            row = self.cursor.fetchone()
            
            if row:
                return dict(row)
            return None
            
        except Exception as e:
            logger.error(f"Failed to get record from {table_name}: {str(e)}")
            return None
    
    def get_all_records(self, table_name, where_clause=None, order_by=None):
        """
        Get all records from a table.
        
        Args:
            table_name: Name of the table
            where_clause: Optional WHERE clause (without "WHERE")
            order_by: Optional ORDER BY clause (without "ORDER BY")
        
        Returns:
            List of dictionaries, one per record
        """
        try:
            query = f"SELECT * FROM {table_name}"
            
            if where_clause:
                query += f" WHERE {where_clause}"
            
            if order_by:
                query += f" ORDER BY {order_by}"
            
            self.cursor.execute(query)
            rows = self.cursor.fetchall()
            
            return [dict(row) for row in rows]
            
        except Exception as e:
            logger.error(f"Failed to get records from {table_name}: {str(e)}")
            return []
    
    def delete_record(self, table_name, record_id, id_column='id'):
        """
        Delete a record by ID.
        
        Args:
            table_name: Name of the table
            record_id: ID of the record to delete
            id_column: Name of the ID column
        
        Returns:
            True if successful, False otherwise
        """
        try:
            query = f"DELETE FROM {table_name} WHERE {id_column} = ?"
            self.cursor.execute(query, (record_id,))
            self.connection.commit()
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete record from {table_name}: {str(e)}")
            return False
    
    def mark_for_sync(self, table_name, record_id):
        """
        Mark a record as needing to be synced to Google Sheets.
        
        Args:
            table_name: Name of the table
            record_id: ID of the record
        
        Returns:
            True if successful, False otherwise
        """
        try:
            id_column = f"{table_name[:-1]}_id" if table_name.endswith('s') else f"{table_name}_id"
            self.update_record(table_name, record_id, {'sync_status': 'pending'}, id_column)
            return True
        except Exception as e:
            logger.error(f"Failed to mark record for sync: {str(e)}")
            return False
    
    def get_pending_syncs(self, table_name=None):
        """
        Get all records that need to be synced.
        
        Args:
            table_name: Optional - filter by specific table
        
        Returns:
            List of (table_name, record) tuples
        """
        try:
            if table_name:
                records = self.get_all_records(table_name, "sync_status = 'pending'")
                return [(table_name, record) for record in records]
            else:
                # Get pending syncs from all tables
                all_pending = []
                for table in TABLES.keys():
                    records = self.get_all_records(table, "sync_status = 'pending'")
                    all_pending.extend([(table, record) for record in records])
                return all_pending
        except Exception as e:
            logger.error(f"Failed to get pending syncs: {str(e)}")
            return []
