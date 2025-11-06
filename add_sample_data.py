"""
Add sample data to the database for testing the Dashboard module
Run this script once to populate the database with test data
"""

import sys
import uuid
from datetime import datetime, timedelta
sys.path.insert(0, '/home/user/BreweryManager')

from src.data_access.sqlite_cache import SQLiteCacheManager

print("=" * 60)
print("ADDING SAMPLE DATA TO DATABASE")
print("=" * 60)

cache = SQLiteCacheManager()
cache.connect()

# Clear existing sample data (except users)
print("\n[1/6] Clearing existing data...")
tables_to_clear = ['recipes', 'batches', 'customers', 'sales', 'inventory_materials', 'invoices']
for table in tables_to_clear:
    cache.cursor.execute(f"DELETE FROM {table}")
cache.connection.commit()
print("✅ Existing data cleared")

# Add recipes
print("\n[2/6] Adding sample recipes...")
recipes = [
    {
        'recipe_id': str(uuid.uuid4()),
        'recipe_name': 'Pale Ale',
        'style': 'Pale Ale',
        'version': 1,
        'target_abv': 4.2,
        'target_batch_size_litres': 800.0,
        'created_date': '2024-01-15',
        'created_by': 'admin',
        'last_modified': '2024-01-15',
        'is_active': 1,
        'brewing_notes': 'Classic English pale ale',
        'sync_status': 'synced'
    },
    {
        'recipe_id': str(uuid.uuid4()),
        'recipe_name': 'IPA',
        'style': 'IPA',
        'version': 2,
        'target_abv': 5.8,
        'target_batch_size_litres': 800.0,
        'created_date': '2024-02-10',
        'created_by': 'admin',
        'last_modified': '2024-02-10',
        'is_active': 1,
        'brewing_notes': 'Hoppy IPA with citrus notes',
        'sync_status': 'synced'
    },
    {
        'recipe_id': str(uuid.uuid4()),
        'recipe_name': 'Porter',
        'style': 'Porter',
        'version': 1,
        'target_abv': 4.8,
        'target_batch_size_litres': 400.0,
        'created_date': '2024-03-05',
        'created_by': 'admin',
        'last_modified': '2024-03-05',
        'is_active': 1,
        'brewing_notes': 'Rich dark porter',
        'sync_status': 'synced'
    }
]

for recipe in recipes:
    cache.insert_record('recipes', recipe)
print(f"✅ Added {len(recipes)} recipes")

# Add batches
print("\n[3/6] Adding sample batches...")
batches = [
    {
        'batch_id': str(uuid.uuid4()),
        'gyle_number': 'GYLE-2025-001',
        'recipe_id': recipes[0]['recipe_id'],
        'brew_date': (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'),
        'brewer_name': 'John Brewer',
        'actual_batch_size': 800.0,
        'measured_abv': 4.3,
        'pure_alcohol_litres': 34.4,
        'status': 'packaged',
        'fermenting_start': (datetime.now() - timedelta(days=28)).strftime('%Y-%m-%d'),
        'conditioning_start': (datetime.now() - timedelta(days=14)).strftime('%Y-%m-%d'),
        'ready_date': (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d'),
        'packaged_date': (datetime.now() - timedelta(days=5)).strftime('%Y-%m-%d'),
        'spr_rate_applied': 4.87,
        'duty_rate_applied': 21.78,
        'is_draught': 1,
        'brewing_notes': 'Good fermentation',
        'created_by': 'admin',
        'last_modified': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'sync_status': 'synced'
    },
    {
        'batch_id': str(uuid.uuid4()),
        'gyle_number': 'GYLE-2025-002',
        'recipe_id': recipes[1]['recipe_id'],
        'brew_date': (datetime.now() - timedelta(days=20)).strftime('%Y-%m-%d'),
        'brewer_name': 'John Brewer',
        'actual_batch_size': 800.0,
        'measured_abv': 5.9,
        'pure_alcohol_litres': 47.2,
        'status': 'conditioning',
        'fermenting_start': (datetime.now() - timedelta(days=18)).strftime('%Y-%m-%d'),
        'conditioning_start': (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d'),
        'ready_date': None,
        'packaged_date': None,
        'spr_rate_applied': None,
        'duty_rate_applied': None,
        'is_draught': 1,
        'brewing_notes': 'Vigorous fermentation',
        'created_by': 'admin',
        'last_modified': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'sync_status': 'synced'
    },
    {
        'batch_id': str(uuid.uuid4()),
        'gyle_number': 'GYLE-2025-003',
        'recipe_id': recipes[2]['recipe_id'],
        'brew_date': (datetime.now() - timedelta(days=10)).strftime('%Y-%m-%d'),
        'brewer_name': 'Jane Brewer',
        'actual_batch_size': 400.0,
        'measured_abv': 4.9,
        'pure_alcohol_litres': 19.6,
        'status': 'fermenting',
        'fermenting_start': (datetime.now() - timedelta(days=8)).strftime('%Y-%m-%d'),
        'conditioning_start': None,
        'ready_date': None,
        'packaged_date': None,
        'spr_rate_applied': None,
        'duty_rate_applied': None,
        'is_draught': 1,
        'brewing_notes': 'Looking good',
        'created_by': 'admin',
        'last_modified': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'sync_status': 'synced'
    },
    {
        'batch_id': str(uuid.uuid4()),
        'gyle_number': 'GYLE-2025-004',
        'recipe_id': recipes[0]['recipe_id'],
        'brew_date': (datetime.now() - timedelta(days=3)).strftime('%Y-%m-%d'),
        'brewer_name': 'John Brewer',
        'actual_batch_size': 800.0,
        'measured_abv': None,
        'pure_alcohol_litres': None,
        'status': 'brewing',
        'fermenting_start': None,
        'conditioning_start': None,
        'ready_date': None,
        'packaged_date': None,
        'spr_rate_applied': None,
        'duty_rate_applied': None,
        'is_draught': 1,
        'brewing_notes': 'Just pitched yeast',
        'created_by': 'admin',
        'last_modified': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'sync_status': 'synced'
    }
]

for batch in batches:
    cache.insert_record('batches', batch)
print(f"✅ Added {len(batches)} batches")

# Add customers
print("\n[4/6] Adding sample customers...")
customers = [
    {
        'customer_id': str(uuid.uuid4()),
        'customer_name': 'The Red Lion',
        'contact_person': 'Sarah Johnson',
        'phone': '01234 567890',
        'email': 'sarah@redlion.co.uk',
        'delivery_address': '123 High Street, Anytown, AB1 2CD',
        'billing_address': '123 High Street, Anytown, AB1 2CD',
        'customer_type': 'pub',
        'payment_terms': 'net_30',
        'credit_limit': 1000.0,
        'preferred_delivery_day': 'Tuesday',
        'preferred_delivery_time': '10:00',
        'likes': 'Pale ales, IPAs',
        'dislikes': 'Very dark beers',
        'notes': 'Great customer, always pays on time',
        'is_active': 1,
        'created_date': '2024-01-10',
        'sync_status': 'synced'
    },
    {
        'customer_id': str(uuid.uuid4()),
        'customer_name': 'The Swan',
        'contact_person': 'Mike Smith',
        'phone': '01234 987654',
        'email': 'mike@swan.co.uk',
        'delivery_address': '45 Market Square, Oldtown, CD3 4EF',
        'billing_address': '45 Market Square, Oldtown, CD3 4EF',
        'customer_type': 'pub',
        'payment_terms': 'net_14',
        'credit_limit': 800.0,
        'preferred_delivery_day': 'Friday',
        'preferred_delivery_time': '14:00',
        'likes': 'Traditional ales',
        'dislikes': 'Nothing specific',
        'notes': 'Good volume customer',
        'is_active': 1,
        'created_date': '2024-01-15',
        'sync_status': 'synced'
    },
    {
        'customer_id': str(uuid.uuid4()),
        'customer_name': 'The Bell Inn',
        'contact_person': 'Emma Brown',
        'phone': '01234 555777',
        'email': 'emma@bellinn.co.uk',
        'delivery_address': '78 Church Lane, Newtown, EF5 6GH',
        'billing_address': '78 Church Lane, Newtown, EF5 6GH',
        'customer_type': 'pub',
        'payment_terms': 'net_30',
        'credit_limit': 1500.0,
        'preferred_delivery_day': 'Wednesday',
        'preferred_delivery_time': '11:00',
        'likes': 'All styles',
        'dislikes': 'None',
        'notes': 'Large venue, regular orders',
        'is_active': 1,
        'created_date': '2024-02-01',
        'sync_status': 'synced'
    }
]

for customer in customers:
    cache.insert_record('customers', customer)
print(f"✅ Added {len(customers)} customers")

# Add sales (including upcoming deliveries)
print("\n[5/6] Adding sample sales...")
sales = [
    {
        'sale_id': str(uuid.uuid4()),
        'sale_date': datetime.now().strftime('%Y-%m-%d'),
        'customer_id': customers[0]['customer_id'],
        'batch_id': batches[1]['batch_id'],
        'gyle_number': batches[1]['gyle_number'],
        'beer_name': 'IPA',
        'container_type': 'firkin',
        'container_size': 40.9,
        'quantity': 2,
        'total_litres': 81.8,
        'unit_price': 65.0,
        'line_total': 130.0,
        'status': 'reserved',
        'reserved_date': datetime.now().strftime('%Y-%m-%d'),
        'delivery_date': (datetime.now() + timedelta(days=2)).strftime('%Y-%m-%d'),
        'invoice_id': None,
        'recorded_by': 'admin',
        'notes': 'Delivery Tuesday morning',
        'sync_status': 'synced'
    },
    {
        'sale_id': str(uuid.uuid4()),
        'sale_date': (datetime.now() - timedelta(days=5)).strftime('%Y-%m-%d'),
        'customer_id': customers[1]['customer_id'],
        'batch_id': batches[0]['batch_id'],
        'gyle_number': batches[0]['gyle_number'],
        'beer_name': 'Pale Ale',
        'container_type': 'firkin',
        'container_size': 40.9,
        'quantity': 3,
        'total_litres': 122.7,
        'unit_price': 65.0,
        'line_total': 195.0,
        'status': 'delivered',
        'reserved_date': (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d'),
        'delivery_date': (datetime.now() - timedelta(days=5)).strftime('%Y-%m-%d'),
        'invoice_id': None,
        'recorded_by': 'admin',
        'notes': 'Delivered successfully',
        'sync_status': 'synced'
    },
    {
        'sale_id': str(uuid.uuid4()),
        'sale_date': datetime.now().strftime('%Y-%m-%d'),
        'customer_id': customers[2]['customer_id'],
        'batch_id': batches[1]['batch_id'],
        'gyle_number': batches[1]['gyle_number'],
        'beer_name': 'IPA',
        'container_type': 'kilderkin',
        'container_size': 81.8,
        'quantity': 1,
        'total_litres': 81.8,
        'unit_price': 120.0,
        'line_total': 120.0,
        'status': 'reserved',
        'reserved_date': datetime.now().strftime('%Y-%m-%d'),
        'delivery_date': (datetime.now() + timedelta(days=5)).strftime('%Y-%m-%d'),
        'invoice_id': None,
        'recorded_by': 'admin',
        'notes': 'For weekend event',
        'sync_status': 'synced'
    }
]

for sale in sales:
    cache.insert_record('sales', sale)
print(f"✅ Added {len(sales)} sales")

# Add inventory materials (with some low stock items)
print("\n[6/6] Adding sample inventory...")
materials = [
    {
        'material_id': str(uuid.uuid4()),
        'material_type': 'grain',
        'material_name': 'Pale Malt',
        'current_stock': 150.0,
        'unit': 'kg',
        'reorder_level': 100.0,
        'last_updated': datetime.now().strftime('%Y-%m-%d'),
        'supplier': 'Malt Suppliers Ltd',
        'cost_per_unit': 1.20,
        'sync_status': 'synced'
    },
    {
        'material_id': str(uuid.uuid4()),
        'material_type': 'grain',
        'material_name': 'Crystal Malt',
        'current_stock': 25.0,
        'unit': 'kg',
        'reorder_level': 30.0,
        'last_updated': datetime.now().strftime('%Y-%m-%d'),
        'supplier': 'Malt Suppliers Ltd',
        'cost_per_unit': 1.50,
        'sync_status': 'synced'
    },
    {
        'material_id': str(uuid.uuid4()),
        'material_type': 'hops',
        'material_name': 'Cascade Hops',
        'current_stock': 5.0,
        'unit': 'kg',
        'reorder_level': 10.0,
        'last_updated': datetime.now().strftime('%Y-%m-%d'),
        'supplier': 'Hop Merchants',
        'cost_per_unit': 15.00,
        'sync_status': 'synced'
    },
    {
        'material_id': str(uuid.uuid4()),
        'material_type': 'yeast',
        'material_name': 'Ale Yeast',
        'current_stock': 15.0,
        'unit': 'packets',
        'reorder_level': 20.0,
        'last_updated': datetime.now().strftime('%Y-%m-%d'),
        'supplier': 'Yeast Lab',
        'cost_per_unit': 8.50,
        'sync_status': 'synced'
    }
]

for material in materials:
    cache.insert_record('inventory_materials', material)
print(f"✅ Added {len(materials)} inventory items")

cache.connection.commit()
cache.close()

print("\n" + "=" * 60)
print("✅ SAMPLE DATA ADDED SUCCESSFULLY")
print("=" * 60)
print("\nSummary:")
print(f"  - {len(recipes)} recipes")
print(f"  - {len(batches)} batches (various statuses)")
print(f"  - {len(customers)} customers")
print(f"  - {len(sales)} sales (including upcoming deliveries)")
print(f"  - {len(materials)} inventory items (some low stock)")
print("\nThe Dashboard should now display:")
print("  ✓ Stats cards with real numbers")
print("  ✓ Recent batches list")
print("  ✓ Low stock alerts")
print("  ✓ Upcoming deliveries")
print("\nReady to test!")
