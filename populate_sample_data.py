"""
Populate Sample Data for Testing
Creates realistic brewery data across all modules
"""
import sqlite3
import sys
from pathlib import Path
from datetime import datetime, timedelta
import random

sys.path.insert(0, str(Path(__file__).parent))
from src.config.constants import CACHE_DB_PATH

print("=" * 70)
print("BREWERY MANAGER - SAMPLE DATA GENERATOR")
print("=" * 70)
print(f"\nDatabase: {CACHE_DB_PATH}")
print("\nThis will create sample data for testing:")
print("  • 3 Beer Recipes (IPA, Stout, Pale Ale)")
print("  • 15 Inventory Items (Malts, Hops, Yeast)")
print("  • 5 Customers")
print("  • 3 Brewing Batches")
print("  • 5 Sales Transactions")
print("=" * 70)

response = input("\nContinue? (yes/no): ")
if response.lower() != 'yes':
    print("\nCancelled.")
    sys.exit(0)

try:
    conn = sqlite3.connect(CACHE_DB_PATH)
    cursor = conn.cursor()

    print("\n" + "=" * 70)
    print("CREATING SAMPLE DATA")
    print("=" * 70)

    # ================================================================
    # 1. RECIPES
    # ================================================================
    print("\n1. Creating Sample Recipes...")

    recipes = [
        {
            'recipe_id': 'RECIPE-IPA-001',
            'name': 'Hoppy IPA',
            'style': 'India Pale Ale',
            'batch_size': 200.0,
            'target_og': 1.055,
            'target_fg': 1.012,
            'target_abv': 5.6,
            'malt_bill': 'Pale Malt: 35kg, Crystal Malt: 3kg, Wheat Malt: 2kg',
            'hop_schedule': 'Cascade: 200g @ 60min, Citra: 150g @ 15min, Mosaic: 100g Dry Hop',
            'yeast': 'US-05 - 2 packets',
            'notes': 'Classic West Coast IPA with citrus and pine notes',
            'created_by': 'admin',
            'created_at': datetime.now().isoformat()
        },
        {
            'recipe_id': 'RECIPE-STOUT-001',
            'name': 'Classic Stout',
            'style': 'Dry Stout',
            'batch_size': 200.0,
            'target_og': 1.048,
            'target_fg': 1.012,
            'target_abv': 4.7,
            'malt_bill': 'Pale Malt: 30kg, Roasted Barley: 4kg, Flaked Barley: 2kg',
            'hop_schedule': 'Fuggles: 150g @ 60min',
            'yeast': 'Irish Ale Yeast - 2 packets',
            'notes': 'Smooth, roasty stout with coffee notes',
            'created_by': 'admin',
            'created_at': datetime.now().isoformat()
        },
        {
            'recipe_id': 'RECIPE-PALE-001',
            'name': 'Golden Pale Ale',
            'style': 'Golden Ale',
            'batch_size': 200.0,
            'target_og': 1.042,
            'target_fg': 1.010,
            'target_abv': 4.2,
            'malt_bill': 'Pale Malt: 32kg, Wheat Malt: 3kg',
            'hop_schedule': 'East Kent Goldings: 100g @ 60min, Styrian Goldings: 80g @ 15min',
            'yeast': 'WLP002 English Ale - 2 packets',
            'notes': 'Easy-drinking session ale',
            'created_by': 'admin',
            'created_at': datetime.now().isoformat()
        }
    ]

    for recipe in recipes:
        cursor.execute('''
            INSERT INTO recipes (recipe_id, name, style, batch_size, target_og, target_fg,
                               target_abv, malt_bill, hop_schedule, yeast, notes,
                               created_by, created_at, active)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
        ''', (recipe['recipe_id'], recipe['name'], recipe['style'], recipe['batch_size'],
              recipe['target_og'], recipe['target_fg'], recipe['target_abv'],
              recipe['malt_bill'], recipe['hop_schedule'], recipe['yeast'],
              recipe['notes'], recipe['created_by'], recipe['created_at']))
        print(f"   ✓ {recipe['name']} - {recipe['style']} ({recipe['target_abv']}% ABV)")

    # ================================================================
    # 2. INVENTORY - MALTS
    # ================================================================
    print("\n2. Creating Inventory Items...")
    print("   Malts:")

    malts = [
        ('INV-MALT-001', 'Pale Malt', 'Malt', 500.0, 'kg', 1.20, 'Crisp Pale Malt'),
        ('INV-MALT-002', 'Crystal Malt', 'Malt', 100.0, 'kg', 1.45, 'Medium Crystal 60L'),
        ('INV-MALT-003', 'Roasted Barley', 'Malt', 50.0, 'kg', 1.35, 'Crisp Roasted Barley'),
        ('INV-MALT-004', 'Wheat Malt', 'Malt', 80.0, 'kg', 1.25, 'German Wheat Malt'),
        ('INV-MALT-005', 'Flaked Barley', 'Malt', 40.0, 'kg', 1.30, 'Flaked Barley'),
    ]

    for item_id, name, category, qty, unit, price, notes in malts:
        cursor.execute('''
            INSERT INTO inventory (item_id, name, category, quantity, unit,
                                 cost_per_unit, notes, last_updated, updated_by)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (item_id, name, category, qty, unit, price, notes,
              datetime.now().isoformat(), 'admin'))
        print(f"     • {name}: {qty}{unit}")

    # ================================================================
    # 3. INVENTORY - HOPS
    # ================================================================
    print("   Hops:")

    hops = [
        ('INV-HOP-001', 'Cascade Hops', 'Hops', 5.0, 'kg', 18.50, 'US Cascade - Citrus/Grapefruit'),
        ('INV-HOP-002', 'Citra Hops', 'Hops', 3.0, 'kg', 22.00, 'US Citra - Tropical fruit'),
        ('INV-HOP-003', 'Mosaic Hops', 'Hops', 2.5, 'kg', 24.00, 'US Mosaic - Complex fruit'),
        ('INV-HOP-004', 'Fuggles Hops', 'Hops', 4.0, 'kg', 16.00, 'UK Fuggles - Earthy'),
        ('INV-HOP-005', 'East Kent Goldings', 'Hops', 3.5, 'kg', 17.50, 'UK EKG - Spicy/Floral'),
    ]

    for item_id, name, category, qty, unit, price, notes in hops:
        cursor.execute('''
            INSERT INTO inventory (item_id, name, category, quantity, unit,
                                 cost_per_unit, notes, last_updated, updated_by)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (item_id, name, category, qty, unit, price, notes,
              datetime.now().isoformat(), 'admin'))
        print(f"     • {name}: {qty}{unit}")

    # ================================================================
    # 4. INVENTORY - YEAST
    # ================================================================
    print("   Yeast:")

    yeasts = [
        ('INV-YEAST-001', 'US-05 Yeast', 'Yeast', 20, 'packets', 4.50, 'Safale US-05 Dry Yeast'),
        ('INV-YEAST-002', 'Irish Ale Yeast', 'Yeast', 15, 'packets', 4.80, 'Safale S-04'),
        ('INV-YEAST-003', 'English Ale Yeast', 'Yeast', 12, 'packets', 5.20, 'WLP002 Liquid'),
    ]

    for item_id, name, category, qty, unit, price, notes in yeasts:
        cursor.execute('''
            INSERT INTO inventory (item_id, name, category, quantity, unit,
                                 cost_per_unit, notes, last_updated, updated_by)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (item_id, name, category, qty, unit, price, notes,
              datetime.now().isoformat(), 'admin'))
        print(f"     • {name}: {qty} {unit}")

    # ================================================================
    # 5. CUSTOMERS
    # ================================================================
    print("\n3. Creating Sample Customers...")

    customers = [
        {
            'customer_id': 'CUST-001',
            'name': 'The Red Lion Pub',
            'contact_name': 'John Smith',
            'email': 'john@redlionpub.co.uk',
            'phone': '01234 567890',
            'address': '123 High Street, Townville, TV1 2AB',
            'customer_type': 'Pub',
            'notes': 'Regular weekly orders',
        },
        {
            'customer_id': 'CUST-002',
            'name': 'The Crown & Anchor',
            'contact_name': 'Sarah Jones',
            'email': 'sarah@crownandanchor.co.uk',
            'phone': '01234 567891',
            'address': '45 Market Square, Townville, TV2 3CD',
            'customer_type': 'Pub',
            'notes': 'Prefers cask ales',
        },
        {
            'customer_id': 'CUST-003',
            'name': 'Craft Beer Shop',
            'contact_name': 'Mike Brown',
            'email': 'mike@craftbeershop.co.uk',
            'phone': '01234 567892',
            'address': '78 Station Road, Townville, TV3 4EF',
            'customer_type': 'Retail',
            'notes': 'Bottled products only',
        },
        {
            'customer_id': 'CUST-004',
            'name': 'The Brewery Tap',
            'contact_name': 'Emma Wilson',
            'email': 'emma@brewerytap.co.uk',
            'phone': '01234 567893',
            'address': '12 Brewery Lane, Townville, TV4 5GH',
            'customer_type': 'Taproom',
            'notes': 'On-site taproom',
        },
        {
            'customer_id': 'CUST-005',
            'name': 'Festival Organizers Ltd',
            'contact_name': 'David Taylor',
            'email': 'david@festivals.co.uk',
            'phone': '01234 567894',
            'address': '99 Event Plaza, Cityville, CV1 6IJ',
            'customer_type': 'Events',
            'notes': 'Bulk orders for festivals',
        }
    ]

    for cust in customers:
        cursor.execute('''
            INSERT INTO customers (customer_id, name, contact_name, email, phone,
                                 address, customer_type, notes, created_at, created_by, active)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
        ''', (cust['customer_id'], cust['name'], cust['contact_name'], cust['email'],
              cust['phone'], cust['address'], cust['customer_type'], cust['notes'],
              datetime.now().isoformat(), 'admin'))
        print(f"   ✓ {cust['name']} ({cust['customer_type']})")

    # ================================================================
    # 6. BATCHES
    # ================================================================
    print("\n4. Creating Sample Batches...")

    # Create batches with dates in the past
    base_date = datetime.now() - timedelta(days=30)

    batches = [
        {
            'batch_id': 'BATCH-2025-001',
            'gyle_number': 'G001',
            'recipe_id': 'RECIPE-IPA-001',
            'brew_date': (base_date - timedelta(days=20)).strftime('%Y-%m-%d'),
            'batch_size': 200.0,
            'original_gravity': 1.056,
            'final_gravity': 1.012,
            'abv': 5.8,
            'status': 'Packaged',
            'notes': 'First IPA batch - excellent fermentation',
            'brewed_by': 'admin'
        },
        {
            'batch_id': 'BATCH-2025-002',
            'gyle_number': 'G002',
            'recipe_id': 'RECIPE-STOUT-001',
            'brew_date': (base_date - timedelta(days=15)).strftime('%Y-%m-%d'),
            'batch_size': 200.0,
            'original_gravity': 1.049,
            'final_gravity': 1.013,
            'abv': 4.7,
            'status': 'Conditioning',
            'notes': 'Beautiful roasty character',
            'brewed_by': 'admin'
        },
        {
            'batch_id': 'BATCH-2025-003',
            'gyle_number': 'G003',
            'recipe_id': 'RECIPE-PALE-001',
            'brew_date': (base_date - timedelta(days=10)).strftime('%Y-%m-%d'),
            'batch_size': 200.0,
            'original_gravity': 1.043,
            'final_gravity': 1.010,
            'abv': 4.3,
            'status': 'Fermenting',
            'notes': 'Clean fermentation, nice hop character',
            'brewed_by': 'admin'
        }
    ]

    for batch in batches:
        cursor.execute('''
            INSERT INTO batches (batch_id, gyle_number, recipe_id, brew_date, batch_size,
                               original_gravity, final_gravity, abv, status, notes,
                               brewed_by, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (batch['batch_id'], batch['gyle_number'], batch['recipe_id'], batch['brew_date'],
              batch['batch_size'], batch['original_gravity'], batch['final_gravity'],
              batch['abv'], batch['status'], batch['notes'], batch['brewed_by'],
              datetime.now().isoformat()))
        print(f"   ✓ Gyle {batch['gyle_number']} - {batch['status']} ({batch['abv']}% ABV)")

    # ================================================================
    # 7. SALES
    # ================================================================
    print("\n5. Creating Sample Sales...")

    sales = [
        {
            'sale_id': 'SALE-001',
            'customer_id': 'CUST-001',
            'batch_id': 'BATCH-2025-001',
            'sale_date': (datetime.now() - timedelta(days=5)).strftime('%Y-%m-%d'),
            'quantity': 5.0,
            'unit': 'Firkins',
            'unit_price': 65.00,
            'total_amount': 325.00,
            'payment_status': 'Paid',
            'notes': '5 firkins of IPA'
        },
        {
            'sale_id': 'SALE-002',
            'customer_id': 'CUST-002',
            'batch_id': 'BATCH-2025-001',
            'sale_date': (datetime.now() - timedelta(days=4)).strftime('%Y-%m-%d'),
            'quantity': 3.0,
            'unit': 'Firkins',
            'unit_price': 65.00,
            'total_amount': 195.00,
            'payment_status': 'Paid',
            'notes': '3 firkins of IPA'
        },
        {
            'sale_id': 'SALE-003',
            'customer_id': 'CUST-003',
            'batch_id': 'BATCH-2025-002',
            'sale_date': (datetime.now() - timedelta(days=3)).strftime('%Y-%m-%d'),
            'quantity': 48.0,
            'unit': 'Bottles',
            'unit_price': 2.50,
            'total_amount': 120.00,
            'payment_status': 'Pending',
            'notes': '48 x 500ml bottles of Stout'
        },
        {
            'sale_id': 'SALE-004',
            'customer_id': 'CUST-004',
            'batch_id': 'BATCH-2025-001',
            'sale_date': (datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d'),
            'quantity': 2.0,
            'unit': 'Kilderkins',
            'unit_price': 120.00,
            'total_amount': 240.00,
            'payment_status': 'Paid',
            'notes': '2 kilderkins for taproom'
        },
        {
            'sale_id': 'SALE-005',
            'customer_id': 'CUST-005',
            'batch_id': 'BATCH-2025-003',
            'sale_date': (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d'),
            'quantity': 10.0,
            'unit': 'Firkins',
            'unit_price': 65.00,
            'total_amount': 650.00,
            'payment_status': 'Pending',
            'notes': 'Festival order - 10 firkins'
        }
    ]

    for sale in sales:
        cursor.execute('''
            INSERT INTO sales (sale_id, customer_id, batch_id, sale_date, quantity, unit,
                             unit_price, total_amount, payment_status, notes, created_at, created_by)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (sale['sale_id'], sale['customer_id'], sale['batch_id'], sale['sale_date'],
              sale['quantity'], sale['unit'], sale['unit_price'], sale['total_amount'],
              sale['payment_status'], sale['notes'], datetime.now().isoformat(), 'admin'))
        print(f"   ✓ {sale['sale_id']}: {sale['quantity']} {sale['unit']} - £{sale['total_amount']:.2f}")

    # Commit all changes
    conn.commit()

    print("\n" + "=" * 70)
    print("✅ SAMPLE DATA CREATED SUCCESSFULLY!")
    print("=" * 70)
    print("\nData Summary:")
    print(f"  • 3 Recipes (IPA, Stout, Pale Ale)")
    print(f"  • 13 Inventory Items (5 Malts, 5 Hops, 3 Yeasts)")
    print(f"  • 5 Customers")
    print(f"  • 3 Batches (at different stages)")
    print(f"  • 5 Sales Transactions (£1,530 total)")
    print("\nYou can now:")
    print("  • Browse recipes and create new batches")
    print("  • Check inventory levels")
    print("  • View customer details and sales history")
    print("  • Generate invoices")
    print("  • Calculate duty on batches")
    print("  • Print labels")
    print("\nRestart the application to see the sample data!")
    print("=" * 70)

except sqlite3.Error as e:
    print(f"\n❌ ERROR: {str(e)}")
    conn.rollback()
    sys.exit(1)

finally:
    if conn:
        conn.close()
