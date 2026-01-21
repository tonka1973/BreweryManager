import sqlite3
import random
import uuid
import logging
from datetime import datetime, timedelta
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Constants
DB_PATH = Path.home() / ".brewerymanager" / "cache.db"
SYNC_STATUS_PENDING = 'pending'
SYNC_STATUS_SYNCED = 'synced'

def get_db_connection():
    """Connect to the SQLite database."""
    if not DB_PATH.exists():
        logger.error(f"Database not found at {DB_PATH.resolve()}")
        raise FileNotFoundError(f"Database not found at {DB_PATH}")
    return sqlite3.connect(DB_PATH)

def generate_id(prefix):
    """Generate a unique ID with a prefix."""
    return f"{prefix}_{str(uuid.uuid4())[:8]}"

def generate_date(days_ago=0):
    """Generate a date string for N days ago."""
    date = datetime.now() - timedelta(days=days_ago)
    return date.strftime("%Y-%m-%d")

def generate_datetime(days_ago=0):
    """Generate a datetime string for N days ago."""
    date = datetime.now() - timedelta(days=days_ago)
    return date.strftime("%Y-%m-%d %H:%M:%S")

def populate_inventory_materials(cursor):
    """Populate inventory materials."""
    materials = [
        # Grains
        ("MAT_PALE", "grain", "Pale Ale Malt", 500, "kg", 1.20, "Crisp Malting"),
        ("MAT_WHEAT", "grain", "Wheat Malt", 200, "kg", 1.30, "Crisp Malting"),
        ("MAT_CRYSTAL", "grain", "Crystal Malt", 100, "kg", 1.50, "Crisp Malting"),
        ("MAT_CHOCO", "grain", "Chocolate Malt", 50, "kg", 1.60, "Crisp Malting"),
        # Hops
        ("MAT_CITRA", "hops", "Citra", 20, "kg", 25.00, "Charles Faram"),
        ("MAT_MOSAIC", "hops", "Mosaic", 15, "kg", 28.00, "Charles Faram"),
        ("MAT_EKG", "hops", "East Kent Goldings", 30, "kg", 18.00, "Charles Faram"),
        ("MAT_FUGGLE", "hops", "Fuggles", 25, "kg", 17.00, "Charles Faram"),
        # Yeast
        ("MAT_US05", "yeast", "US-05 SafAle", 50, "pack", 120.00, "Fermentis"),
        ("MAT_S04", "yeast", "S-04 SafAle", 40, "pack", 115.00, "Fermentis"),
        # Adjuncts
        ("MAT_PROTAFLOC", "adjunct", "Protafloc", 5, "kg", 45.00, "Murphy & Son"),
    ]

    for mat_id, mat_type, name, stock, unit, cost, supplier in materials:
        # Check by ID or Name to avoid duplicates
        cursor.execute("SELECT 1 FROM inventory_materials WHERE material_id = ? OR material_name = ?", (mat_id, name))
        if not cursor.fetchone():
            try:
                cursor.execute("""
                    INSERT INTO inventory_materials (
                        material_id, material_type, material_name, current_stock, unit, 
                        reorder_level, last_updated, supplier, cost_per_unit, sync_status
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (mat_id, mat_type, name, stock, unit, 50, generate_datetime(), supplier, cost, SYNC_STATUS_PENDING))
                print(f"Inserted material: {name}")
            except sqlite3.IntegrityError as e:
                print(f"Skipping material {name}: {e}")

def populate_recipes(cursor):
    """Populate recipes."""
    recipes = [
        ("REC_GOLDEN", "Golden Ale", "Pale Ale", 1, 4.2, 800),
        ("REC_IPA", "Hoppy IPA", "IPA", 1, 5.5, 800),
        ("REC_STOUT", "Midnight Stout", "Stout", 1, 4.5, 800),
    ]

    for rec_id, name, style, ver, abv, size in recipes:
        # Check by ID or Name
        cursor.execute("SELECT 1 FROM recipes WHERE recipe_id = ? OR recipe_name = ?", (rec_id, name))
        if not cursor.fetchone():
            try:
                cursor.execute("""
                    INSERT INTO recipes (
                        recipe_id, recipe_name, style, version, target_abv, 
                        target_batch_size_litres, created_date, created_by, last_modified, sync_status
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (rec_id, name, style, ver, abv, size, generate_datetime(30), "Admin", generate_datetime(), SYNC_STATUS_PENDING))
                print(f"Inserted recipe: {name}")
                
                # Link generic ingredients (simplified)
                try:
                    if name == "Golden Ale":
                        cursor.execute("INSERT INTO recipe_grains (grain_id, recipe_id, material_id, quantity, unit, sync_status) VALUES (?, ?, ?, ?, ?, ?)", 
                                    (generate_id("RG"), rec_id, "MAT_PALE", 150, "kg", SYNC_STATUS_PENDING))
                        cursor.execute("INSERT INTO recipe_hops (hop_id, recipe_id, material_id, quantity, unit, sync_status) VALUES (?, ?, ?, ?, ?, ?)", 
                                    (generate_id("RH"), rec_id, "MAT_EKG", 1.5, "kg", SYNC_STATUS_PENDING))
                    elif name == "Hoppy IPA":
                        cursor.execute("INSERT INTO recipe_grains (grain_id, recipe_id, material_id, quantity, unit, sync_status) VALUES (?, ?, ?, ?, ?, ?)", 
                                    (generate_id("RG"), rec_id, "MAT_PALE", 160, "kg", SYNC_STATUS_PENDING))
                        cursor.execute("INSERT INTO recipe_hops (hop_id, recipe_id, material_id, quantity, unit, sync_status) VALUES (?, ?, ?, ?, ?, ?)", 
                                    (generate_id("RH"), rec_id, "MAT_CITRA", 3.0, "kg", SYNC_STATUS_PENDING))
                    elif name == "Midnight Stout":
                        cursor.execute("INSERT INTO recipe_grains (grain_id, recipe_id, material_id, quantity, unit, sync_status) VALUES (?, ?, ?, ?, ?, ?)", 
                                    (generate_id("RG"), rec_id, "MAT_CHOCO", 200, "kg", SYNC_STATUS_PENDING))
                        cursor.execute("INSERT INTO recipe_hops (hop_id, recipe_id, material_id, quantity, unit, sync_status) VALUES (?, ?, ?, ?, ?, ?)", 
                                    (generate_id("RH"), rec_id, "MAT_FUGGLE", 1.8, "kg", SYNC_STATUS_PENDING))
                except sqlite3.IntegrityError as e:
                    print(f"Skipping ingredients for {name}: {e}")

            except sqlite3.IntegrityError as e:
                print(f"Skipping recipe {name}: {e}")

def populate_customers(cursor):
    """Populate customers."""
    customers = [
        ("CUST_RED_LION", "The Red Lion", "John Smith", "01234 567890", "john@redlionpub.com", "1 High St, Townville", "Same", "Pub", "net_30"),
        ("CUST_KINGS_HEAD", "The Kings Head", "Sarah Jones", "01234 567891", "sarah@kingshead.com", "5 Main Rd, Villageton", "Same", "Pub/Hotel", "net_14"),
        ("CUST_CRAFT_CO", "Craft Beer Co", "Mike Brown", "07700 900123", "mike@craftbeer.co", "Unit 4, Ind Est", "Unit 4, Ind Est", "Distributor", "net_30"),
        ("CUST_PRIVATE_1", "Dave Wilson", "Dave", "07700 123456", "dave@email.com", "12 House St", "12 House St", "Private", "cash"),
    ]

    for cust_id, name, contact, phone, email, address, bill_addr, ctype, terms in customers:
        cursor.execute("SELECT 1 FROM customers WHERE customer_id = ?", (cust_id,))
        if not cursor.fetchone():
            try:
                cursor.execute("""
                    INSERT INTO customers (
                        customer_id, customer_name, contact_person, phone, email, 
                        delivery_address, billing_address, customer_type, payment_terms, 
                        created_date, sync_status
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (cust_id, name, contact, phone, email, address, bill_addr, ctype, terms, generate_datetime(60), SYNC_STATUS_PENDING))
                print(f"Inserted customer: {name}")
            except sqlite3.IntegrityError as e:
                print(f"Skipping customer {name}: {e}")

def populate_batches_and_products(cursor):
    """Populate batches and associated products."""
    
    # Check if used recipes exist first!
    
    # 1. A brewing batch (active)
    batch_active = {
        "batch_id": "BATCH_001",
        "gyle_number": "GYLE-2025-001",
        "recipe_id": "REC_GOLDEN",
        "brew_date": generate_date(2),
        "status": "fermenting",
        "actual_batch_size": 820,
        "measured_abv": 4.1,
        "notes": "Fermenting nicely",
        "created_by": "Brewer Bob"
    }
    
    # 2. A packaged batch (completed) - Golden Ale
    batch_packaged_1 = {
        "batch_id": "BATCH_002",
        "gyle_number": "GYLE-2024-050",
        "recipe_id": "REC_GOLDEN",
        "brew_date": generate_date(30),
        "status": "packaged",
        "packaged_date": generate_date(10),
        "actual_batch_size": 810,
        "measured_abv": 4.2,
        "notes": "Good yield",
        "created_by": "Brewer Bob"
    }
    
    # 3. A packaged batch (completed) - IPA
    batch_packaged_2 = {
        "batch_id": "BATCH_003",
        "gyle_number": "GYLE-2024-051",
        "recipe_id": "REC_IPA",
        "brew_date": generate_date(25),
        "status": "packaged",
        "packaged_date": generate_date(5),
        "actual_batch_size": 790,
        "measured_abv": 5.6,
        "notes": "Slightly strong",
        "created_by": "Brewer Bob"
    }

    batches = [batch_active, batch_packaged_1, batch_packaged_2]
    
    for b in batches:
        cursor.execute("SELECT 1 FROM batches WHERE batch_id = ? OR gyle_number = ?", (b['batch_id'], b['gyle_number']))
        if not cursor.fetchone():
            try:
                cursor.execute("""
                    INSERT INTO batches (
                        batch_id, gyle_number, recipe_id, brew_date, status, 
                        packaged_date, actual_batch_size, measured_abv, brewing_notes, 
                        created_by, last_modified, sync_status
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    b['batch_id'], b['gyle_number'], b['recipe_id'], b['brew_date'], b['status'],
                    b.get('packaged_date'), b['actual_batch_size'], b['measured_abv'], b.get('notes'),
                    b['created_by'], generate_datetime(), SYNC_STATUS_PENDING
                ))
                print(f"Inserted batch: {b['gyle_number']}")
                
                # If packaged, create products (Casks/Kegs)
                if b['status'] == 'packaged':
                    # Create Casks (Firkins)
                    try:
                        for i in range(10): # 10 Firkins
                            prod_id = generate_id("PROD_CASK")
                            cursor.execute("""
                                INSERT INTO products (
                                    product_id, gyle_number, batch_id, recipe_id, product_name,
                                    container_type, container_size_l, quantity_total, quantity_in_stock,
                                    display_name, abv, date_packaged, status, sync_status
                                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                            """, (
                                prod_id, b['gyle_number'], b['batch_id'], b['recipe_id'], "Golden Ale Firkin" if "REC_GOLDEN" in b['recipe_id'] else "IPA Firkin",
                                "Firkin", 40.9, 1, 1, None, b['measured_abv'], b['packaged_date'], "in_stock", SYNC_STATUS_PENDING
                            ))
                    except Exception as e:
                        print(f"Error creating products: {e}")
                    
                    # Create Casks (Full)
                    try:
                        cursor.execute("""
                            INSERT INTO casks_full (
                                cask_record_id, batch_id, gyle_number, beer_name, abv, 
                                packaged_date, cask_type, cask_size_litres, quantity, 
                                status, sync_status
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            generate_id("CF"), b['batch_id'], b['gyle_number'], 
                            "Golden Ale" if "REC_GOLDEN" in b['recipe_id'] else "IPA", 
                            b['measured_abv'], b['packaged_date'], "Firkin", 40.9, 10, 
                            "in_stock", SYNC_STATUS_PENDING
                        ))
                        print(f"  -> Created stock for {b['gyle_number']}")
                    except Exception as e:
                         print(f"Error creating cask stock: {e}")
            
            except sqlite3.IntegrityError as e:
                print(f"Skipping batch {b['gyle_number']}: {e}")

def populate_sales_and_invoices(cursor):
    """Populate sales and invoices."""
    
    # 1. Sale to Red Lion (Golden Ale)
    # Check if sale exists? ID is random so checking is hard without known ID.
    # But since I'm using generated IDs, duplicate collision is low, but running script multiple times adds duplicate sales.
    # I'll skip this if "BATCH_002" already has sales? No, that's valid.
    # I will limit sales creation to only if "BATCH_002" exists and we haven't created this specific demo sale?
    # I'll just rely on the fact that I'm inserting a specific sale for testing, maybe I should use a fixed ID for the test sale too.
    
    sale_id = "SALE_TEST_001"
    
    cursor.execute("SELECT 1 FROM sales WHERE sale_id = ?", (sale_id,))
    if not cursor.fetchone():
        try:
            cursor.execute("""
                INSERT INTO sales (
                    sale_id, sale_date, customer_id, batch_id, gyle_number, 
                    beer_name, container_type, container_size, quantity, 
                    total_litres, unit_price, line_total, status, 
                    delivery_date, sync_status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                sale_id, generate_date(5), "CUST_RED_LION", "BATCH_002", "GYLE-2024-050",
                "Golden Ale", "Firkin", 40.9, 2, 81.8, 75.00, 150.00, "delivered",
                generate_date(4), SYNC_STATUS_PENDING
            ))
            print("Inserted Sale to Red Lion")

            # Invoice for Red Lion
            inv_id = "INV_TEST_001"
            inv_num = "INV-2025-0001"
            cursor.execute("""
                INSERT INTO invoices (
                    invoice_id, invoice_number, invoice_date, customer_id, 
                    subtotal, vat_rate, vat_amount, total, 
                    payment_status, due_date, created_date, sync_status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                inv_id, inv_num, generate_date(5), "CUST_RED_LION",
                150.00, 0.20, 30.00, 180.00,
                "unpaid", generate_date(-25), generate_date(5), SYNC_STATUS_PENDING
            ))
            
            # Invoice Line
            cursor.execute("""
                INSERT INTO invoice_lines (
                    line_id, invoice_id, sale_id, description, 
                    quantity, unit_price, line_total, gyle_number, sync_status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                generate_id("LINE"), inv_id, sale_id, "Golden Ale - Firkin",
                2, 75.00, 150.00, "GYLE-2024-050", SYNC_STATUS_PENDING
            ))
            print(f"Inserted Invoice {inv_num}")
        except sqlite3.IntegrityError as e:
            print(f"Skipping sale/invoice: {e}")

def main():
    print("Starting Test Data Population...")
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Populate in dependency order
        populate_inventory_materials(cursor)
        populate_customers(cursor)
        populate_recipes(cursor)
        populate_batches_and_products(cursor)
        populate_sales_and_invoices(cursor)
        
        conn.commit()
        conn.close()
        print("\nSuccess! Test data populated with sync_status='pending'.")
        print("Run the application to trigger sync to Google Sheets.")
        
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
