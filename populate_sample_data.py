"""
Populate the database with sample data for testing and demonstration.
Run this script to add realistic brewery data to the system.
"""

import sys
import os
from datetime import datetime, timedelta
import uuid

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.data_access.sqlite_cache import SQLiteCacheManager
from src.utilities.auth import AuthManager

def populate_sample_data():
    """Populate database with realistic sample data."""

    cache = SQLiteCacheManager()
    cache.connect()

    # Initialize database (create all tables)
    print("Initializing database...")
    cache.initialize_database()
    print("✓ Database initialized")

    print("\nPopulating sample data...")

    # Sample Recipes
    print("\n1. Adding recipes...")
    recipes = [
        {
            'recipe_id': str(uuid.uuid4()),
            'recipe_name': 'Golden Ale',
            'style': 'Blonde Ale',
            'target_batch_size_litres': 500,
            'target_abv': 4.2,
            'version': 1,
            'brewing_notes': 'Maris Otter: 80kg, Crystal 60L: 5kg, Wheat Malt: 10kg. Challenger 60min: 200g, Goldings 15min: 150g, Goldings 0min: 100g. Safale S-04 yeast. Classic session ale. Popular with local pubs.',
            'is_active': 1,
            'created_date': (datetime.now() - timedelta(days=60)).strftime('%Y-%m-%d %H:%M:%S'),
            'created_by': 'admin',
            'last_modified': (datetime.now() - timedelta(days=60)).strftime('%Y-%m-%d %H:%M:%S'),
            'sync_status': 'synced'
        },
        {
            'recipe_id': str(uuid.uuid4()),
            'recipe_name': 'Dark Porter',
            'style': 'English Porter',
            'target_batch_size_litres': 500,
            'target_abv': 5.4,
            'version': 1,
            'brewing_notes': 'Maris Otter: 75kg, Brown Malt: 8kg, Chocolate Malt: 6kg, Crystal 150L: 6kg. Fuggles 60min: 250g, East Kent Goldings 30min: 200g. Wyeast 1968 London ESB. Rich, smooth porter with coffee notes.',
            'is_active': 1,
            'created_date': (datetime.now() - timedelta(days=45)).strftime('%Y-%m-%d %H:%M:%S'),
            'created_by': 'admin',
            'last_modified': (datetime.now() - timedelta(days=45)).strftime('%Y-%m-%d %H:%M:%S'),
            'sync_status': 'synced'
        },
        {
            'recipe_id': str(uuid.uuid4()),
            'recipe_name': 'IPA Session',
            'style': 'Session IPA',
            'target_batch_size_litres': 500,
            'target_abv': 3.8,
            'version': 1,
            'brewing_notes': 'Maris Otter: 70kg, Carapils: 8kg, Vienna: 5kg. Cascade 60min: 100g, Citra 15min: 200g, Mosaic 5min: 250g, Amarillo dry hop: 300g. Safale US-05. Hoppy but sessionable. Great for summer.',
            'is_active': 1,
            'created_date': (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d %H:%M:%S'),
            'created_by': 'admin',
            'last_modified': (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d %H:%M:%S'),
            'sync_status': 'synced'
        }
    ]

    for recipe in recipes:
        cache.insert_record('recipes', recipe)
        print(f"  ✓ Added recipe: {recipe['recipe_name']}")

    # Sample Inventory - Grains
    print("\n2. Adding inventory items...")
    inventory_items = [
        {
            'material_id': str(uuid.uuid4()),
            'material_type': 'grain',
            'material_name': 'Maris Otter Malt',
            'current_stock': 2500,
            'unit': 'kg',
            'supplier': 'Crisp Malting Group',
            'cost_per_unit': 1.20,
            'reorder_level': 500,
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'sync_status': 'synced'
        },
        {
            'material_id': str(uuid.uuid4()),
            'material_type': 'grain',
            'material_name': 'Crystal Malt 60L',
            'current_stock': 150,
            'unit': 'kg',
            'supplier': 'Crisp Malting Group',
            'cost_per_unit': 1.35,
            'reorder_level': 50,
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'sync_status': 'synced'
        },
        {
            'material_id': str(uuid.uuid4()),
            'material_type': 'grain',
            'material_name': 'Chocolate Malt',
            'current_stock': 80,
            'unit': 'kg',
            'supplier': 'Crisp Malting Group',
            'cost_per_unit': 1.45,
            'reorder_level': 30,
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'sync_status': 'synced'
        },
        {
            'material_id': str(uuid.uuid4()),
            'material_type': 'hops',
            'material_name': 'Cascade Hops',
            'current_stock': 5.5,
            'unit': 'kg',
            'supplier': 'Charles Faram',
            'cost_per_unit': 18.50,
            'reorder_level': 2,
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'sync_status': 'synced'
        },
        {
            'material_id': str(uuid.uuid4()),
            'material_type': 'hops',
            'material_name': 'East Kent Goldings',
            'current_stock': 4.2,
            'unit': 'kg',
            'supplier': 'Charles Faram',
            'cost_per_unit': 16.00,
            'reorder_level': 2,
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'sync_status': 'synced'
        },
        {
            'material_id': str(uuid.uuid4()),
            'material_type': 'yeast',
            'material_name': 'Safale S-04',
            'current_stock': 25,
            'unit': 'packs',
            'supplier': 'Fermentis',
            'cost_per_unit': 3.50,
            'reorder_level': 10,
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'sync_status': 'synced'
        }
    ]

    for item in inventory_items:
        cache.insert_record('inventory_materials', item)
        print(f"  ✓ Added inventory: {item['material_name']}")

    # Sample Batches
    print("\n3. Adding batches...")
    batches = [
        {
            'batch_id': str(uuid.uuid4()),
            'gyle_number': 'G2025-001',
            'recipe_id': recipes[0]['recipe_id'],
            'brew_date': (datetime.now() - timedelta(days=21)).strftime('%Y-%m-%d'),
            'brewer_name': 'admin',
            'actual_batch_size': 500,
            'measured_abv': 4.3,
            'pure_alcohol_litres': 21.5,
            'status': 'packaged',
            'fermenting_start': (datetime.now() - timedelta(days=21)).strftime('%Y-%m-%d'),
            'conditioning_start': (datetime.now() - timedelta(days=14)).strftime('%Y-%m-%d'),
            'ready_date': (datetime.now() - timedelta(days=10)).strftime('%Y-%m-%d'),
            'packaged_date': (datetime.now() - timedelta(days=10)).strftime('%Y-%m-%d'),
            'spr_rate_applied': 0.0,
            'duty_rate_applied': 21.01,
            'is_draught': 1,
            'brewing_notes': 'Fermentation went smoothly. Good clarity.',
            'created_by': 'admin',
            'last_modified': (datetime.now() - timedelta(days=10)).strftime('%Y-%m-%d %H:%M:%S'),
            'sync_status': 'synced'
        },
        {
            'batch_id': str(uuid.uuid4()),
            'gyle_number': 'G2025-002',
            'recipe_id': recipes[1]['recipe_id'],
            'brew_date': (datetime.now() - timedelta(days=18)).strftime('%Y-%m-%d'),
            'brewer_name': 'admin',
            'actual_batch_size': 500,
            'measured_abv': 5.5,
            'pure_alcohol_litres': 27.5,
            'status': 'conditioning',
            'fermenting_start': (datetime.now() - timedelta(days=18)).strftime('%Y-%m-%d'),
            'conditioning_start': (datetime.now() - timedelta(days=11)).strftime('%Y-%m-%d'),
            'packaged_date': (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d'),
            'spr_rate_applied': 0.0,
            'duty_rate_applied': 21.01,
            'is_draught': 1,
            'brewing_notes': 'Excellent porter. Rich malt character.',
            'created_by': 'admin',
            'last_modified': (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d %H:%M:%S'),
            'sync_status': 'synced'
        },
        {
            'batch_id': str(uuid.uuid4()),
            'gyle_number': 'G2025-003',
            'recipe_id': recipes[2]['recipe_id'],
            'brew_date': (datetime.now() - timedelta(days=10)).strftime('%Y-%m-%d'),
            'brewer_name': 'admin',
            'actual_batch_size': 500,
            'measured_abv': 3.9,
            'pure_alcohol_litres': 19.5,
            'status': 'fermenting',
            'fermenting_start': (datetime.now() - timedelta(days=10)).strftime('%Y-%m-%d'),
            'spr_rate_applied': 0.0,
            'duty_rate_applied': 21.01,
            'is_draught': 1,
            'brewing_notes': 'Dry hopping scheduled for day 7.',
            'created_by': 'admin',
            'last_modified': (datetime.now() - timedelta(days=10)).strftime('%Y-%m-%d %H:%M:%S'),
            'sync_status': 'synced'
        }
    ]

    for batch in batches:
        cache.insert_record('batches', batch)
        print(f"  ✓ Added batch: {batch['gyle_number']}")

    # Sample Customers
    print("\n4. Adding customers...")
    customers = [
        {
            'customer_id': str(uuid.uuid4()),
            'customer_name': 'The Red Lion',
            'contact_person': 'John Smith',
            'email': 'john@redlionpub.co.uk',
            'phone': '01234 567890',
            'delivery_address': '45 High Street, Townsville, AB12 3CD',
            'billing_address': '45 High Street, Townsville, AB12 3CD',
            'customer_type': 'pub',
            'credit_limit': 2000,
            'payment_terms': '30 days',
            'preferred_delivery_day': 'Monday',
            'preferred_delivery_time': '10:00',
            'likes': 'Golden Ale, Session beers',
            'dislikes': '',
            'notes': 'Regular customer. Orders every 2 weeks.',
            'is_active': 1,
            'created_date': (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d %H:%M:%S'),
            'sync_status': 'synced'
        },
        {
            'customer_id': str(uuid.uuid4()),
            'customer_name': 'The Brewers Arms',
            'contact_person': 'Sarah Johnson',
            'email': 'sarah@brewersarms.co.uk',
            'phone': '01234 567891',
            'delivery_address': '23 Market Square, Cityville, CD34 5EF',
            'billing_address': '23 Market Square, Cityville, CD34 5EF',
            'customer_type': 'pub',
            'credit_limit': 3000,
            'payment_terms': '30 days',
            'preferred_delivery_day': 'Wednesday',
            'preferred_delivery_time': '14:00',
            'likes': 'All beers',
            'dislikes': '',
            'notes': 'Premium location. Sells high volumes.',
            'is_active': 1,
            'created_date': (datetime.now() - timedelta(days=75)).strftime('%Y-%m-%d %H:%M:%S'),
            'sync_status': 'synced'
        },
        {
            'customer_id': str(uuid.uuid4()),
            'customer_name': 'Beer & Wine Shop',
            'contact_person': 'Mike Brown',
            'email': 'mike@beerandwine.co.uk',
            'phone': '01234 567892',
            'delivery_address': '12 Station Road, Villageton, EF56 7GH',
            'billing_address': '12 Station Road, Villageton, EF56 7GH',
            'customer_type': 'retail',
            'credit_limit': 1000,
            'payment_terms': '14 days',
            'preferred_delivery_day': 'Friday',
            'preferred_delivery_time': '09:00',
            'likes': 'Bottles',
            'dislikes': 'Casks',
            'notes': 'Bottle sales only. Payment on delivery.',
            'is_active': 1,
            'created_date': (datetime.now() - timedelta(days=45)).strftime('%Y-%m-%d %H:%M:%S'),
            'sync_status': 'synced'
        }
    ]

    for customer in customers:
        cache.insert_record('customers', customer)
        print(f"  ✓ Added customer: {customer['customer_name']}")

    # Sample Sales
    print("\n5. Adding sales...")
    sales = [
        {
            'sale_id': str(uuid.uuid4()),
            'customer_id': customers[0]['customer_id'],
            'batch_id': batches[0]['batch_id'],
            'gyle_number': batches[0]['gyle_number'],
            'beer_name': 'Golden Ale',
            'sale_date': (datetime.now() - timedelta(days=8)).strftime('%Y-%m-%d'),
            'container_type': 'firkin',
            'container_size': 40.9,
            'quantity': 10,
            'total_litres': 409,
            'unit_price': 75.00,
            'line_total': 750.00,
            'status': 'delivered',
            'reserved_date': (datetime.now() - timedelta(days=9)).strftime('%Y-%m-%d'),
            'delivery_date': (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d'),
            'invoice_id': None,
            'recorded_by': 'admin',
            'notes': 'Regular monthly order.',
            'sync_status': 'synced'
        },
        {
            'sale_id': str(uuid.uuid4()),
            'customer_id': customers[1]['customer_id'],
            'batch_id': batches[0]['batch_id'],
            'gyle_number': batches[0]['gyle_number'],
            'beer_name': 'Golden Ale',
            'sale_date': (datetime.now() - timedelta(days=5)).strftime('%Y-%m-%d'),
            'container_type': 'firkin',
            'container_size': 40.9,
            'quantity': 15,
            'total_litres': 613.5,
            'unit_price': 72.00,
            'line_total': 1080.00,
            'status': 'delivered',
            'reserved_date': (datetime.now() - timedelta(days=6)).strftime('%Y-%m-%d'),
            'delivery_date': (datetime.now() - timedelta(days=4)).strftime('%Y-%m-%d'),
            'invoice_id': None,
            'recorded_by': 'admin',
            'notes': 'Bulk order - volume discount applied.',
            'sync_status': 'synced'
        },
        {
            'sale_id': str(uuid.uuid4()),
            'customer_id': customers[0]['customer_id'],
            'batch_id': batches[1]['batch_id'],
            'gyle_number': batches[1]['gyle_number'],
            'beer_name': 'Dark Porter',
            'sale_date': (datetime.now() - timedelta(days=3)).strftime('%Y-%m-%d'),
            'container_type': 'firkin',
            'container_size': 40.9,
            'quantity': 8,
            'total_litres': 327.2,
            'unit_price': 78.00,
            'line_total': 624.00,
            'status': 'delivered',
            'reserved_date': (datetime.now() - timedelta(days=4)).strftime('%Y-%m-%d'),
            'delivery_date': (datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d'),
            'invoice_id': None,
            'recorded_by': 'admin',
            'notes': 'Special order for winter season.',
            'sync_status': 'synced'
        }
    ]

    for sale in sales:
        cache.insert_record('sales', sale)
        print(f"  ✓ Added sale: {sale['beer_name']} ({sale['quantity']} {sale['container_type']}s)")

    # Sample Invoices
    print("\n6. Adding invoices...")
    invoices = [
        {
            'invoice_id': str(uuid.uuid4()),
            'invoice_number': 'INV-2025-001',
            'customer_id': customers[0]['customer_id'],
            'invoice_date': (datetime.now() - timedelta(days=8)).strftime('%Y-%m-%d'),
            'due_date': (datetime.now() + timedelta(days=22)).strftime('%Y-%m-%d'),
            'subtotal': 750.00,
            'vat_rate': 20.0,
            'vat_amount': 150.00,
            'total': 900.00,
            'payment_status': 'unpaid',
            'amount_paid': 0.0,
            'amount_outstanding': 900.00,
            'created_by': 'admin',
            'notes': 'Payment terms: 30 days',
            'created_date': (datetime.now() - timedelta(days=8)).strftime('%Y-%m-%d %H:%M:%S'),
            'sync_status': 'synced'
        },
        {
            'invoice_id': str(uuid.uuid4()),
            'invoice_number': 'INV-2025-002',
            'customer_id': customers[1]['customer_id'],
            'invoice_date': (datetime.now() - timedelta(days=5)).strftime('%Y-%m-%d'),
            'due_date': (datetime.now() + timedelta(days=25)).strftime('%Y-%m-%d'),
            'subtotal': 1080.00,
            'vat_rate': 20.0,
            'vat_amount': 216.00,
            'total': 1296.00,
            'payment_status': 'unpaid',
            'amount_paid': 0.0,
            'amount_outstanding': 1296.00,
            'created_by': 'admin',
            'notes': 'Volume discount applied',
            'created_date': (datetime.now() - timedelta(days=5)).strftime('%Y-%m-%d %H:%M:%S'),
            'sync_status': 'synced'
        },
        {
            'invoice_id': str(uuid.uuid4()),
            'invoice_number': 'INV-2025-003',
            'customer_id': customers[0]['customer_id'],
            'invoice_date': (datetime.now() - timedelta(days=3)).strftime('%Y-%m-%d'),
            'due_date': (datetime.now() + timedelta(days=27)).strftime('%Y-%m-%d'),
            'subtotal': 624.00,
            'vat_rate': 20.0,
            'vat_amount': 124.80,
            'total': 748.80,
            'payment_status': 'unpaid',
            'amount_paid': 0.0,
            'amount_outstanding': 748.80,
            'created_by': 'admin',
            'notes': 'Winter seasonal order',
            'created_date': (datetime.now() - timedelta(days=3)).strftime('%Y-%m-%d %H:%M:%S'),
            'sync_status': 'synced'
        }
    ]

    for invoice in invoices:
        cache.insert_record('invoices', invoice)
        print(f"  ✓ Added invoice: {invoice['invoice_number']} - £{invoice['total']:.2f}")

    cache.close()

    print("\n" + "="*60)
    print("✓ Sample data population complete!")
    print("="*60)
    print("\nSummary:")
    print(f"  • {len(recipes)} Recipes added")
    print(f"  • {len(inventory_items)} Inventory materials added")
    print(f"  • {len(batches)} Batches added")
    print(f"  • {len(customers)} Customers added")
    print(f"  • {len(sales)} Sales transactions added")
    print(f"  • {len(invoices)} Invoices added")
    print("\nYou can now explore the application with realistic data!")
    print("Login with: admin / admin")
    print("\nRestart the application to see the data!")
    print("="*60)

if __name__ == "__main__":
    try:
        populate_sample_data()
    except Exception as e:
        print(f"\n❌ Error populating sample data: {str(e)}")
        import traceback
        traceback.print_exc()
