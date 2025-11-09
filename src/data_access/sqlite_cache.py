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
                    spr_rate_applied REAL,
                    duty_rate_applied REAL,
                    is_draught INTEGER,
                    brewing_notes TEXT,
                    created_by TEXT,
                    last_modified TEXT,
                    sync_status TEXT DEFAULT 'synced'
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
                    sync_status TEXT DEFAULT 'synced'
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
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS duty_returns (
                    return_id TEXT PRIMARY KEY,
                    return_period_start TEXT,
                    return_period_end TEXT,
                    total_duty_payable REAL,
                    submitted_date TEXT,
                    submitted_by TEXT,
                    payment_date TEXT,
                    payment_reference TEXT,
                    status TEXT DEFAULT 'draft',
                    notes TEXT,
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
            
            self.connection.commit()
            logger.info("Database tables initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize database: {str(e)}")
            return False
    
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
