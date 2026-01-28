
import sys
import os
import sqlite3
import uuid
from datetime import datetime

# Relative imports should work if run as module
from ..data_access.sqlite_cache import SQLiteCacheManager
from ..utilities.date_utils import get_today_db

def verify():
    print("--- Verifying Production Enhancements ---")
    cache = SQLiteCacheManager()
    
    # 1. Connect & Initialize (triggers migrations)
    print("1. Initializing Database...")
    if not cache.connect():
        print("FAILED to connect.")
        return
        
    cache.initialize_database()
    
    # 2. Check Schema
    print("2. Checking Schema...")
    try:
        cache.cursor.execute("SELECT * FROM inventory_batches LIMIT 1")
        print("   [PASS] inventory_batches table exists.")
    except Exception as e:
        print(f"   [FAIL] inventory_batches table missing: {e}")
        return

    try:
        cache.cursor.execute("SELECT ingredient_source_batches FROM batches LIMIT 1")
        print("   [PASS] batches.ingredient_source_batches column exists.")
    except Exception as e:
        print(f"   [FAIL] batches.ingredient_source_batches column missing: {e}")
        return

    # 3. Setup Test Data (Material + Batches)
    print("3. Setting up Test Data...")
    mat_id = str(uuid.uuid4())
    try:
        # Create Material
        cache.cursor.execute(f"DELETE FROM inventory_materials WHERE material_name = 'TEST_MALT_{mat_id}'")
        cache.insert_record('inventory_materials', {
            'material_id': mat_id,
            'material_name': f'TEST_MALT_{mat_id}',
            'current_stock': 100,
            'unit': 'kg',
            'sync_status': 'pending'
        })
        
        # Create Batches (FIFO Setup: B1(Old) = 20kg, B2(New) = 100kg)
        
        cache.insert_record('inventory_batches', {
            'batch_id': str(uuid.uuid4()),
            'material_id': mat_id,
            'batch_number': 'B001_OLD',
            'quantity_initial': 20,
            'quantity_remaining': 20,
            'received_date': '2025-01-01',
            'sync_status': 'pending'
        })
        
        cache.insert_record('inventory_batches', {
            'batch_id': str(uuid.uuid4()),
            'material_id': mat_id,
            'batch_number': 'B002_NEW',
            'quantity_initial': 80,
            'quantity_remaining': 80,
            'received_date': '2026-01-01',
            'sync_status': 'pending'
        })
        print("   [PASS] Test data created.")
        
    except Exception as e:
        print(f"   [FAIL] creating test data: {e}")

    # 4. Simulate FIFO Logic (Use 30kg)
    print("4. Simulating FIFO Usage (Need 30kg)...")
    # Expected: 20kg from B001, 10kg from B002
    
    qty_needed = 30
    allocations = []
    remaining = qty_needed
    
    batches = cache.get_all_records(
        'inventory_batches', 
        f"material_id = '{mat_id}' AND quantity_remaining > 0",
        order_by='received_date ASC'
    )
    
    for b in batches:
        if remaining <= 0: break
        take = min(b['quantity_remaining'], remaining)
        allocations.append({'batch_num': b.get('batch_number'), 'qty': take})
        remaining -= take
        
    print(f"   Allocations: {allocations}")
    
    if len(allocations) == 2 and allocations[0]['batch_num'] == 'B001_OLD' and allocations[0]['qty'] == 20:
        print("   [PASS] FIFO Logic Correct (Took 20 from Old, 10 from New)")
    else:
        print("   [FAIL] FIFO Logic Incorrect")
        
    # 5. Check Warning Logic
    print("5. Checking Warning Logic...")
    if len(allocations) > 1:
        batches_str = " & ".join([f"{b['batch_num']} ({b['qty']:.1f})" for b in allocations])
        print(f"   [PASS] Detected Mixed Batch: {batches_str}")
    else:
        print("   [FAIL] Did not detect mixed batch")

    # Clean up
    cache.cursor.execute(f"DELETE FROM inventory_batches WHERE material_id = '{mat_id}'")
    cache.cursor.execute(f"DELETE FROM inventory_materials WHERE material_id = '{mat_id}'")
    cache.connection.commit()
    cache.close()
    print("--- Verification Complete ---")

if __name__ == "__main__":
    verify()
