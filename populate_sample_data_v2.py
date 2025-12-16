"""
Populate Sample Data for Testing (v2 - Correct Schema)
Creates realistic brewery data matching actual database structure
"""
import sqlite3
import sys
from pathlib import Path
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).parent))
from src.config.constants import CACHE_DB_PATH

print("=" * 70)
print("BREWERY MANAGER - SAMPLE DATA GENERATOR (v2)")
print("=" * 70)
print(f"\nDatabase: {CACHE_DB_PATH}")
print("\nThis will create sample data for testing:")
print("  • 3 Beer Recipes (IPA, Stout, Pale Ale)")
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
            'recipe_name': 'Hoppy IPA',
            'style': 'India Pale Ale',
            'version': 1,
            'target_abv': 5.6,
            'target_batch_size_litres': 200.0,
            'brewing_notes': 'Classic West Coast IPA with citrus and pine notes. Malt: 35kg Pale, 3kg Crystal, 2kg Wheat. Hops: 200g Cascade @60min, 150g Citra @15min, 100g Mosaic dry hop. Yeast: US-05 x2 packets.',
            'created_by': 'admin',
            'created_date': datetime.now().isoformat(),
            'is_active': 1
        },
        {
            'recipe_id': 'RECIPE-STOUT-001',
            'recipe_name': 'Classic Stout',
            'style': 'Dry Stout',
            'version': 1,
            'target_abv': 4.7,
            'target_batch_size_litres': 200.0,
            'brewing_notes': 'Smooth, roasty stout with coffee notes. Malt: 30kg Pale, 4kg Roasted Barley, 2kg Flaked Barley. Hops: 150g Fuggles @60min. Yeast: Irish Ale x2 packets.',
            'created_by': 'admin',
            'created_date': datetime.now().isoformat(),
            'is_active': 1
        },
        {
            'recipe_id': 'RECIPE-PALE-001',
            'recipe_name': 'Golden Pale Ale',
            'style': 'Golden Ale',
            'version': 1,
            'target_abv': 4.2,
            'target_batch_size_litres': 200.0,
            'brewing_notes': 'Easy-drinking session ale. Malt: 32kg Pale, 3kg Wheat. Hops: 100g EKG @60min, 80g Styrian Goldings @15min. Yeast: WLP002 x2 packets.',
            'created_by': 'admin',
            'created_date': datetime.now().isoformat(),
            'is_active': 1
        }
    ]

    for recipe in recipes:
        cursor.execute('''
            INSERT INTO recipes (recipe_id, recipe_name, style, version, target_abv,
                               target_batch_size_litres, brewing_notes, created_by,
                               created_date, is_active, sync_status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'synced')
        ''', (recipe['recipe_id'], recipe['recipe_name'], recipe['style'], recipe['version'],
              recipe['target_abv'], recipe['target_batch_size_litres'], recipe['brewing_notes'],
              recipe['created_by'], recipe['created_date'], recipe['is_active']))
        print(f"   ✓ {recipe['recipe_name']} - {recipe['style']} ({recipe['target_abv']}% ABV)")

    # ================================================================
    # 2. CUSTOMERS
    # ================================================================
    print("\n2. Creating Sample Customers...")

    customers = [
        {
            'customer_id': 'CUST-001',
            'customer_name': 'The Red Lion Pub',
            'contact_person': 'John Smith',
            'email': 'john@redlionpub.co.uk',
            'phone': '01234 567890',
            'delivery_address': '123 High Street, Townville, TV1 2AB',
            'billing_address': '123 High Street, Townville, TV1 2AB',
            'customer_type': 'Pub',
            'payment_terms': 'Net 30',
            'credit_limit': 5000.0,
            'preferred_delivery_day': 'Monday',
            'likes': 'Hoppy beers, IPAs',
            'notes': 'Regular weekly orders',
        },
        {
            'customer_id': 'CUST-002',
            'customer_name': 'The Crown & Anchor',
            'contact_person': 'Sarah Jones',
            'email': 'sarah@crownandanchor.co.uk',
            'phone': '01234 567891',
            'delivery_address': '45 Market Square, Townville, TV2 3CD',
            'billing_address': '45 Market Square, Townville, TV2 3CD',
            'customer_type': 'Pub',
            'payment_terms': 'Net 30',
            'credit_limit': 3000.0,
            'preferred_delivery_day': 'Tuesday',
            'likes': 'Cask ales, traditional styles',
            'notes': 'Prefers cask ales',
        },
        {
            'customer_id': 'CUST-003',
            'customer_name': 'Craft Beer Shop',
            'contact_person': 'Mike Brown',
            'email': 'mike@craftbeershop.co.uk',
            'phone': '01234 567892',
            'delivery_address': '78 Station Road, Townville, TV3 4EF',
            'billing_address': '78 Station Road, Townville, TV3 4EF',
            'customer_type': 'Retail',
            'payment_terms': 'Net 14',
            'credit_limit': 2000.0,
            'preferred_delivery_day': 'Wednesday',
            'likes': 'Bottled products, variety',
            'notes': 'Bottled products only',
        },
        {
            'customer_id': 'CUST-004',
            'customer_name': 'The Brewery Tap',
            'contact_person': 'Emma Wilson',
            'email': 'emma@brewerytap.co.uk',
            'phone': '01234 567893',
            'delivery_address': '12 Brewery Lane, Townville, TV4 5GH',
            'billing_address': '12 Brewery Lane, Townville, TV4 5GH',
            'customer_type': 'Taproom',
            'payment_terms': 'Cash',
            'credit_limit': 0.0,
            'preferred_delivery_day': 'Friday',
            'likes': 'All styles',
            'notes': 'On-site taproom - immediate payment',
        },
        {
            'customer_id': 'CUST-005',
            'customer_name': 'Festival Organizers Ltd',
            'contact_person': 'David Taylor',
            'email': 'david@festivals.co.uk',
            'phone': '01234 567894',
            'delivery_address': '99 Event Plaza, Cityville, CV1 6IJ',
            'billing_address': '99 Event Plaza, Cityville, CV1 6IJ',
            'customer_type': 'Events',
            'payment_terms': 'Advance Payment',
            'credit_limit': 10000.0,
            'preferred_delivery_day': 'Thursday',
            'likes': 'Variety for festivals',
            'notes': 'Bulk orders for festivals',
        }
    ]

    for cust in customers:
        cursor.execute('''
            INSERT INTO customers (customer_id, customer_name, contact_person, email, phone,
                                 delivery_address, billing_address, customer_type, payment_terms,
                                 credit_limit, preferred_delivery_day, likes, notes,
                                 is_active, created_date, sync_status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, ?, 'synced')
        ''', (cust['customer_id'], cust['customer_name'], cust['contact_person'], cust['email'],
              cust['phone'], cust['delivery_address'], cust['billing_address'], cust['customer_type'],
              cust['payment_terms'], cust['credit_limit'], cust['preferred_delivery_day'],
              cust['likes'], cust['notes'], datetime.now().isoformat()))
        print(f"   ✓ {cust['customer_name']} ({cust['customer_type']})")

    # ================================================================
    # 3. BATCHES
    # ================================================================
    print("\n3. Creating Sample Batches...")

    base_date = datetime.now() - timedelta(days=30)

    batches = [
        {
            'batch_id': 'BATCH-2025-001',
            'gyle_number': 'G001',
            'recipe_id': 'RECIPE-IPA-001',
            'brew_date': (base_date - timedelta(days=20)).strftime('%Y-%m-%d'),
            'brewer_name': 'admin',
            'actual_batch_size': 200.0,
            'measured_abv': 5.8,
            'pure_alcohol_litres': 11.6,  # 200L * 5.8%
            'status': 'Packaged',
            'fermenting_start': (base_date - timedelta(days=20)).strftime('%Y-%m-%d'),
            'conditioning_start': (base_date - timedelta(days=13)).strftime('%Y-%m-%d'),
            'ready_date': (base_date - timedelta(days=6)).strftime('%Y-%m-%d'),
            'packaged_date': (base_date - timedelta(days=5)).strftime('%Y-%m-%d'),
            'is_draught': 1,
            'fermented_volume': 200.0,
            'packaged_volume': 190.0,
            'waste_volume': 10.0,
            'waste_percentage': 5.0,
            'brewing_notes': 'First IPA batch - excellent fermentation'
        },
        {
            'batch_id': 'BATCH-2025-002',
            'gyle_number': 'G002',
            'recipe_id': 'RECIPE-STOUT-001',
            'brew_date': (base_date - timedelta(days=15)).strftime('%Y-%m-%d'),
            'brewer_name': 'admin',
            'actual_batch_size': 200.0,
            'measured_abv': 4.7,
            'pure_alcohol_litres': 9.4,  # 200L * 4.7%
            'status': 'Conditioning',
            'fermenting_start': (base_date - timedelta(days=15)).strftime('%Y-%m-%d'),
            'conditioning_start': (base_date - timedelta(days=8)).strftime('%Y-%m-%d'),
            'is_draught': 1,
            'fermented_volume': 200.0,
            'brewing_notes': 'Beautiful roasty character'
        },
        {
            'batch_id': 'BATCH-2025-003',
            'gyle_number': 'G003',
            'recipe_id': 'RECIPE-PALE-001',
            'brew_date': (base_date - timedelta(days=10)).strftime('%Y-%m-%d'),
            'brewer_name': 'admin',
            'actual_batch_size': 200.0,
            'measured_abv': 4.3,
            'pure_alcohol_litres': 8.6,  # 200L * 4.3%
            'status': 'Fermenting',
            'fermenting_start': (base_date - timedelta(days=10)).strftime('%Y-%m-%d'),
            'is_draught': 1,
            'fermented_volume': 200.0,
            'brewing_notes': 'Clean fermentation, nice hop character'
        }
    ]

    for batch in batches:
        cursor.execute('''
            INSERT INTO batches (batch_id, gyle_number, recipe_id, brew_date, brewer_name,
                               actual_batch_size, measured_abv, pure_alcohol_litres, status,
                               fermenting_start, conditioning_start, ready_date, packaged_date,
                               is_draught, fermented_volume, packaged_volume, waste_volume,
                               waste_percentage, brewing_notes, created_by, sync_status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'synced')
        ''', (batch['batch_id'], batch['gyle_number'], batch['recipe_id'], batch['brew_date'],
              batch['brewer_name'], batch['actual_batch_size'], batch['measured_abv'],
              batch['pure_alcohol_litres'], batch['status'], batch['fermenting_start'],
              batch.get('conditioning_start'), batch.get('ready_date'), batch.get('packaged_date'),
              batch['is_draught'], batch['fermented_volume'], batch.get('packaged_volume'),
              batch.get('waste_volume'), batch.get('waste_percentage'), batch['brewing_notes'],
              'admin'))
        print(f"   ✓ Gyle {batch['gyle_number']} - {batch['status']} ({batch['measured_abv']}% ABV)")

    # ================================================================
    # 4. SALES
    # ================================================================
    print("\n4. Creating Sample Sales...")

    sales = [
        {
            'sale_id': 'SALE-001',
            'sale_date': (datetime.now() - timedelta(days=5)).strftime('%Y-%m-%d'),
            'customer_id': 'CUST-001',
            'batch_id': 'BATCH-2025-001',
            'gyle_number': 'G001',
            'beer_name': 'Hoppy IPA',
            'container_type': 'Firkin',
            'container_size': 40.9,
            'quantity': 5,
            'total_litres': 204.5,
            'unit_price': 65.00,
            'line_total': 325.00,
            'status': 'Delivered',
            'delivery_date': (datetime.now() - timedelta(days=4)).strftime('%Y-%m-%d'),
            'notes': '5 firkins of IPA'
        },
        {
            'sale_id': 'SALE-002',
            'sale_date': (datetime.now() - timedelta(days=4)).strftime('%Y-%m-%d'),
            'customer_id': 'CUST-002',
            'batch_id': 'BATCH-2025-001',
            'gyle_number': 'G001',
            'beer_name': 'Hoppy IPA',
            'container_type': 'Firkin',
            'container_size': 40.9,
            'quantity': 3,
            'total_litres': 122.7,
            'unit_price': 65.00,
            'line_total': 195.00,
            'status': 'Delivered',
            'delivery_date': (datetime.now() - timedelta(days=3)).strftime('%Y-%m-%d'),
            'notes': '3 firkins of IPA'
        },
        {
            'sale_id': 'SALE-003',
            'sale_date': (datetime.now() - timedelta(days=3)).strftime('%Y-%m-%d'),
            'customer_id': 'CUST-003',
            'batch_id': 'BATCH-2025-002',
            'gyle_number': 'G002',
            'beer_name': 'Classic Stout',
            'container_type': 'Bottle 500ml',
            'container_size': 0.5,
            'quantity': 96,
            'total_litres': 48.0,
            'unit_price': 2.50,
            'line_total': 240.00,
            'status': 'Reserved',
            'reserved_date': (datetime.now() - timedelta(days=3)).strftime('%Y-%m-%d'),
            'notes': '96 x 500ml bottles of Stout'
        },
        {
            'sale_id': 'SALE-004',
            'sale_date': (datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d'),
            'customer_id': 'CUST-004',
            'batch_id': 'BATCH-2025-001',
            'gyle_number': 'G001',
            'beer_name': 'Hoppy IPA',
            'container_type': 'Kilderkin',
            'container_size': 81.8,
            'quantity': 2,
            'total_litres': 163.6,
            'unit_price': 120.00,
            'line_total': 240.00,
            'status': 'Delivered',
            'delivery_date': (datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d'),
            'notes': '2 kilderkins for taproom'
        },
        {
            'sale_id': 'SALE-005',
            'sale_date': (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d'),
            'customer_id': 'CUST-005',
            'batch_id': 'BATCH-2025-003',
            'gyle_number': 'G003',
            'beer_name': 'Golden Pale Ale',
            'container_type': 'Firkin',
            'container_size': 40.9,
            'quantity': 10,
            'total_litres': 409.0,
            'unit_price': 65.00,
            'line_total': 650.00,
            'status': 'Reserved',
            'reserved_date': (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d'),
            'notes': 'Festival order - 10 firkins (awaiting batch completion)'
        }
    ]

    for sale in sales:
        cursor.execute('''
            INSERT INTO sales (sale_id, sale_date, customer_id, batch_id, gyle_number,
                             beer_name, container_type, container_size, quantity, total_litres,
                             unit_price, line_total, status, reserved_date, delivery_date,
                             recorded_by, notes, sync_status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'synced')
        ''', (sale['sale_id'], sale['sale_date'], sale['customer_id'], sale['batch_id'],
              sale['gyle_number'], sale['beer_name'], sale['container_type'], sale['container_size'],
              sale['quantity'], sale['total_litres'], sale['unit_price'], sale['line_total'],
              sale['status'], sale.get('reserved_date'), sale.get('delivery_date'),
              'admin', sale['notes']))
        print(f"   ✓ {sale['sale_id']}: {sale['quantity']}x {sale['container_type']} - £{sale['line_total']:.2f}")

    # Commit all changes
    conn.commit()

    print("\n" + "=" * 70)
    print("✅ SAMPLE DATA CREATED SUCCESSFULLY!")
    print("=" * 70)
    print("\nData Summary:")
    print(f"  • 3 Recipes (IPA, Stout, Pale Ale)")
    print(f"  • 5 Customers (Pubs, Retail, Taproom, Events)")
    print(f"  • 3 Batches (at different stages)")
    print(f"  • 5 Sales Transactions (£1,650 total)")
    print("\nYou can now:")
    print("  • Browse recipes and create new batches")
    print("  • View customer details and sales history")
    print("  • Track batch progress through fermentation")
    print("  • Generate invoices from sales")
    print("  • Calculate duty on packaged batches")
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
