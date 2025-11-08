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

    print("Populating sample data...")

    # Sample Recipes
    print("\n1. Adding recipes...")
    recipes = [
        {
            'recipe_id': str(uuid.uuid4()),
            'recipe_name': 'Golden Ale',
            'style': 'Blonde Ale',
            'batch_size_litres': 500,
            'abv': 4.2,
            'og': 1.042,
            'fg': 1.010,
            'ibu': 25,
            'grain_bill': 'Maris Otter: 80kg, Crystal 60L: 5kg, Wheat Malt: 10kg',
            'hops_schedule': 'Challenger 60min: 200g, Goldings 15min: 150g, Goldings 0min: 100g',
            'yeast': 'Safale S-04',
            'mash_temp': 66,
            'mash_time': 60,
            'boil_time': 60,
            'notes': 'Classic session ale. Popular with local pubs.',
            'created_date': (datetime.now() - timedelta(days=60)).strftime('%Y-%m-%d %H:%M:%S'),
            'sync_status': 'synced'
        },
        {
            'recipe_id': str(uuid.uuid4()),
            'recipe_name': 'Dark Porter',
            'style': 'English Porter',
            'batch_size_litres': 500,
            'abv': 5.4,
            'og': 1.054,
            'fg': 1.014,
            'ibu': 35,
            'grain_bill': 'Maris Otter: 75kg, Brown Malt: 8kg, Chocolate Malt: 6kg, Crystal 150L: 6kg',
            'hops_schedule': 'Fuggles 60min: 250g, East Kent Goldings 30min: 200g',
            'yeast': 'Wyeast 1968 London ESB',
            'mash_temp': 67,
            'mash_time': 75,
            'boil_time': 60,
            'notes': 'Rich, smooth porter with coffee notes.',
            'created_date': (datetime.now() - timedelta(days=45)).strftime('%Y-%m-%d %H:%M:%S'),
            'sync_status': 'synced'
        },
        {
            'recipe_id': str(uuid.uuid4()),
            'recipe_name': 'IPA Session',
            'style': 'Session IPA',
            'batch_size_litres': 500,
            'abv': 3.8,
            'og': 1.038,
            'fg': 1.008,
            'ibu': 40,
            'grain_bill': 'Maris Otter: 70kg, Carapils: 8kg, Vienna: 5kg',
            'hops_schedule': 'Cascade 60min: 100g, Citra 15min: 200g, Mosaic 5min: 250g, Amarillo dry hop: 300g',
            'yeast': 'Safale US-05',
            'mash_temp': 65,
            'mash_time': 60,
            'boil_time': 60,
            'notes': 'Hoppy but sessionable. Great for summer.',
            'created_date': (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d %H:%M:%S'),
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
            'inventory_id': str(uuid.uuid4()),
            'item_type': 'grain',
            'item_name': 'Maris Otter Malt',
            'quantity': 2500,
            'unit': 'kg',
            'supplier': 'Crisp Malting Group',
            'cost_per_unit': 1.20,
            'reorder_level': 500,
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'sync_status': 'synced'
        },
        {
            'inventory_id': str(uuid.uuid4()),
            'item_type': 'grain',
            'item_name': 'Crystal Malt 60L',
            'quantity': 150,
            'unit': 'kg',
            'supplier': 'Crisp Malting Group',
            'cost_per_unit': 1.35,
            'reorder_level': 50,
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'sync_status': 'synced'
        },
        {
            'inventory_id': str(uuid.uuid4()),
            'item_type': 'grain',
            'item_name': 'Chocolate Malt',
            'quantity': 80,
            'unit': 'kg',
            'supplier': 'Crisp Malting Group',
            'cost_per_unit': 1.45,
            'reorder_level': 30,
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'sync_status': 'synced'
        },
        {
            'inventory_id': str(uuid.uuid4()),
            'item_type': 'hops',
            'item_name': 'Cascade Hops',
            'quantity': 5.5,
            'unit': 'kg',
            'supplier': 'Charles Faram',
            'cost_per_unit': 18.50,
            'reorder_level': 2,
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'sync_status': 'synced'
        },
        {
            'inventory_id': str(uuid.uuid4()),
            'item_type': 'hops',
            'item_name': 'East Kent Goldings',
            'quantity': 4.2,
            'unit': 'kg',
            'supplier': 'Charles Faram',
            'cost_per_unit': 16.00,
            'reorder_level': 2,
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'sync_status': 'synced'
        },
        {
            'inventory_id': str(uuid.uuid4()),
            'item_type': 'yeast',
            'item_name': 'Safale S-04',
            'quantity': 25,
            'unit': 'packs',
            'supplier': 'Fermentis',
            'cost_per_unit': 3.50,
            'reorder_level': 10,
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'sync_status': 'synced'
        },
        {
            'inventory_id': str(uuid.uuid4()),
            'item_type': 'finished_goods',
            'item_name': 'Golden Ale (Firkins)',
            'quantity': 12,
            'unit': 'firkins',
            'supplier': 'Internal',
            'cost_per_unit': 0,
            'reorder_level': 5,
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'sync_status': 'synced'
        },
        {
            'inventory_id': str(uuid.uuid4()),
            'item_type': 'finished_goods',
            'item_name': 'Dark Porter (Firkins)',
            'quantity': 8,
            'unit': 'firkins',
            'supplier': 'Internal',
            'cost_per_unit': 0,
            'reorder_level': 5,
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'sync_status': 'synced'
        }
    ]

    for item in inventory_items:
        cache.insert_record('inventory', item)
        print(f"  ✓ Added inventory: {item['item_name']}")

    # Sample Batches
    print("\n3. Adding batches...")
    batches = [
        {
            'batch_id': str(uuid.uuid4()),
            'gyle_number': 'G2025-001',
            'recipe_id': recipes[0]['recipe_id'],
            'recipe_name': recipes[0]['recipe_name'],
            'brew_date': (datetime.now() - timedelta(days=21)).strftime('%Y-%m-%d'),
            'batch_size_litres': 500,
            'target_abv': 4.2,
            'actual_abv': 4.3,
            'og': 1.042,
            'fg': 1.010,
            'status': 'Packaged',
            'fermentation_start': (datetime.now() - timedelta(days=21)).strftime('%Y-%m-%d'),
            'fermentation_end': (datetime.now() - timedelta(days=14)).strftime('%Y-%m-%d'),
            'packaging_date': (datetime.now() - timedelta(days=10)).strftime('%Y-%m-%d'),
            'notes': 'Fermentation went smoothly. Good clarity.',
            'created_date': (datetime.now() - timedelta(days=21)).strftime('%Y-%m-%d %H:%M:%S'),
            'sync_status': 'synced'
        },
        {
            'batch_id': str(uuid.uuid4()),
            'gyle_number': 'G2025-002',
            'recipe_id': recipes[1]['recipe_id'],
            'recipe_name': recipes[1]['recipe_name'],
            'brew_date': (datetime.now() - timedelta(days=18)).strftime('%Y-%m-%d'),
            'batch_size_litres': 500,
            'target_abv': 5.4,
            'actual_abv': 5.5,
            'og': 1.054,
            'fg': 1.013,
            'status': 'Conditioning',
            'fermentation_start': (datetime.now() - timedelta(days=18)).strftime('%Y-%m-%d'),
            'fermentation_end': (datetime.now() - timedelta(days=11)).strftime('%Y-%m-%d'),
            'packaging_date': (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d'),
            'notes': 'Excellent porter. Rich malt character.',
            'created_date': (datetime.now() - timedelta(days=18)).strftime('%Y-%m-%d %H:%M:%S'),
            'sync_status': 'synced'
        },
        {
            'batch_id': str(uuid.uuid4()),
            'gyle_number': 'G2025-003',
            'recipe_id': recipes[2]['recipe_id'],
            'recipe_name': recipes[2]['recipe_name'],
            'brew_date': (datetime.now() - timedelta(days=10)).strftime('%Y-%m-%d'),
            'batch_size_litres': 500,
            'target_abv': 3.8,
            'actual_abv': 3.9,
            'og': 1.038,
            'fg': 1.008,
            'status': 'Fermenting',
            'fermentation_start': (datetime.now() - timedelta(days=10)).strftime('%Y-%m-%d'),
            'notes': 'Dry hopping scheduled for day 7.',
            'created_date': (datetime.now() - timedelta(days=10)).strftime('%Y-%m-%d %H:%M:%S'),
            'sync_status': 'synced'
        }
    ]

    for batch in batches:
        cache.insert_record('batches', batch)
        print(f"  ✓ Added batch: {batch['gyle_number']} - {batch['recipe_name']}")

    # Sample Customers
    print("\n4. Adding customers...")
    customers = [
        {
            'customer_id': str(uuid.uuid4()),
            'customer_name': 'The Red Lion',
            'contact_person': 'John Smith',
            'email': 'john@redlionpub.co.uk',
            'phone': '01234 567890',
            'address': '45 High Street, Townsville',
            'postcode': 'AB12 3CD',
            'customer_type': 'pub',
            'credit_limit': 2000,
            'payment_terms': '30 days',
            'notes': 'Regular customer. Orders every 2 weeks.',
            'created_date': (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d %H:%M:%S'),
            'sync_status': 'synced'
        },
        {
            'customer_id': str(uuid.uuid4()),
            'customer_name': 'The Brewers Arms',
            'contact_person': 'Sarah Johnson',
            'email': 'sarah@brewersarms.co.uk',
            'phone': '01234 567891',
            'address': '23 Market Square, Cityville',
            'postcode': 'CD34 5EF',
            'customer_type': 'pub',
            'credit_limit': 3000,
            'payment_terms': '30 days',
            'notes': 'Premium location. Sells high volumes.',
            'created_date': (datetime.now() - timedelta(days=75)).strftime('%Y-%m-%d %H:%M:%S'),
            'sync_status': 'synced'
        },
        {
            'customer_id': str(uuid.uuid4()),
            'customer_name': 'Beer & Wine Shop',
            'contact_person': 'Mike Brown',
            'email': 'mike@beerandwine.co.uk',
            'phone': '01234 567892',
            'address': '12 Station Road, Villageton',
            'postcode': 'EF56 7GH',
            'customer_type': 'retail',
            'credit_limit': 1000,
            'payment_terms': '14 days',
            'notes': 'Bottle sales only. Payment on delivery.',
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
            'customer_name': customers[0]['customer_name'],
            'batch_id': batches[0]['batch_id'],
            'gyle_number': batches[0]['gyle_number'],
            'product_name': 'Golden Ale',
            'sale_date': (datetime.now() - timedelta(days=8)).strftime('%Y-%m-%d'),
            'quantity': 10,
            'unit': 'firkins',
            'unit_price': 75.00,
            'total_amount': 750.00,
            'vat_amount': 150.00,
            'dispatch_date': (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d'),
            'dispatch_status': 'Delivered',
            'notes': 'Regular monthly order.',
            'created_date': (datetime.now() - timedelta(days=8)).strftime('%Y-%m-%d %H:%M:%S'),
            'sync_status': 'synced'
        },
        {
            'sale_id': str(uuid.uuid4()),
            'customer_id': customers[1]['customer_id'],
            'customer_name': customers[1]['customer_name'],
            'batch_id': batches[0]['batch_id'],
            'gyle_number': batches[0]['gyle_number'],
            'product_name': 'Golden Ale',
            'sale_date': (datetime.now() - timedelta(days=5)).strftime('%Y-%m-%d'),
            'quantity': 15,
            'unit': 'firkins',
            'unit_price': 72.00,
            'total_amount': 1080.00,
            'vat_amount': 216.00,
            'dispatch_date': (datetime.now() - timedelta(days=4)).strftime('%Y-%m-%d'),
            'dispatch_status': 'Delivered',
            'notes': 'Bulk order - volume discount applied.',
            'created_date': (datetime.now() - timedelta(days=5)).strftime('%Y-%m-%d %H:%M:%S'),
            'sync_status': 'synced'
        },
        {
            'sale_id': str(uuid.uuid4()),
            'customer_id': customers[0]['customer_id'],
            'customer_name': customers[0]['customer_name'],
            'batch_id': batches[1]['batch_id'],
            'gyle_number': batches[1]['gyle_number'],
            'product_name': 'Dark Porter',
            'sale_date': (datetime.now() - timedelta(days=3)).strftime('%Y-%m-%d'),
            'quantity': 8,
            'unit': 'firkins',
            'unit_price': 78.00,
            'total_amount': 624.00,
            'vat_amount': 124.80,
            'dispatch_date': (datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d'),
            'dispatch_status': 'Delivered',
            'notes': 'Special order for winter season.',
            'created_date': (datetime.now() - timedelta(days=3)).strftime('%Y-%m-%d %H:%M:%S'),
            'sync_status': 'synced'
        }
    ]

    for sale in sales:
        cache.insert_record('sales', sale)
        print(f"  ✓ Added sale: {sale['customer_name']} - {sale['product_name']} ({sale['quantity']} {sale['unit']})")

    # Sample Invoices
    print("\n6. Adding invoices...")
    invoices = [
        {
            'invoice_id': str(uuid.uuid4()),
            'invoice_number': 'INV-2025-001',
            'customer_id': customers[0]['customer_id'],
            'customer_name': customers[0]['customer_name'],
            'invoice_date': (datetime.now() - timedelta(days=8)).strftime('%Y-%m-%d'),
            'due_date': (datetime.now() + timedelta(days=22)).strftime('%Y-%m-%d'),
            'subtotal': 750.00,
            'vat_amount': 150.00,
            'total_amount': 900.00,
            'payment_status': 'Unpaid',
            'payment_date': None,
            'notes': 'Payment terms: 30 days',
            'created_date': (datetime.now() - timedelta(days=8)).strftime('%Y-%m-%d %H:%M:%S'),
            'sync_status': 'synced'
        },
        {
            'invoice_id': str(uuid.uuid4()),
            'invoice_number': 'INV-2025-002',
            'customer_id': customers[1]['customer_id'],
            'customer_name': customers[1]['customer_name'],
            'invoice_date': (datetime.now() - timedelta(days=5)).strftime('%Y-%m-%d'),
            'due_date': (datetime.now() + timedelta(days=25)).strftime('%Y-%m-%d'),
            'subtotal': 1080.00,
            'vat_amount': 216.00,
            'total_amount': 1296.00,
            'payment_status': 'Unpaid',
            'payment_date': None,
            'notes': 'Volume discount applied',
            'created_date': (datetime.now() - timedelta(days=5)).strftime('%Y-%m-%d %H:%M:%S'),
            'sync_status': 'synced'
        },
        {
            'invoice_id': str(uuid.uuid4()),
            'invoice_number': 'INV-2025-003',
            'customer_id': customers[0]['customer_id'],
            'customer_name': customers[0]['customer_name'],
            'invoice_date': (datetime.now() - timedelta(days=3)).strftime('%Y-%m-%d'),
            'due_date': (datetime.now() + timedelta(days=27)).strftime('%Y-%m-%d'),
            'subtotal': 624.00,
            'vat_amount': 124.80,
            'total_amount': 748.80,
            'payment_status': 'Unpaid',
            'payment_date': None,
            'notes': 'Winter seasonal order',
            'created_date': (datetime.now() - timedelta(days=3)).strftime('%Y-%m-%d %H:%M:%S'),
            'sync_status': 'synced'
        }
    ]

    for invoice in invoices:
        cache.insert_record('invoices', invoice)
        print(f"  ✓ Added invoice: {invoice['invoice_number']} - {invoice['customer_name']} - £{invoice['total_amount']:.2f}")

    cache.close()

    print("\n" + "="*60)
    print("✓ Sample data population complete!")
    print("="*60)
    print("\nSummary:")
    print(f"  • {len(recipes)} Recipes added")
    print(f"  • {len(inventory_items)} Inventory items added")
    print(f"  • {len(batches)} Batches added")
    print(f"  • {len(customers)} Customers added")
    print(f"  • {len(sales)} Sales transactions added")
    print(f"  • {len(invoices)} Invoices added")
    print("\nYou can now explore the application with realistic data!")
    print("Login with: admin / admin")
    print("="*60)

if __name__ == "__main__":
    try:
        populate_sample_data()
    except Exception as e:
        print(f"\n❌ Error populating sample data: {str(e)}")
        import traceback
        traceback.print_exc()
