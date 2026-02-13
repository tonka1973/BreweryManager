
import sqlite3
import os
from pathlib import Path

def debug_invoice_creation():
    home = Path.home()
    db_path = home / ".brewerymanager" / "cache.db"
    
    output_file = Path("debug_sales_dump.txt")
    
    if not db_path.exists():
        with open(output_file, 'w') as f:
            f.write(f"DB not found at {db_path}")
        return

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"DEBUGGING DB: {db_path}\n")
        
        try:
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # 1. Inspect Customers
            f.write("\n--- CUSTOMERS ---\n")
            cursor.execute("SELECT customer_id, customer_name, is_active FROM customers")
            customers = cursor.fetchall()
            customer_map = {}
            for c in customers:
                f.write(f"Customer: {c['customer_name']} (Active: {c['is_active']}) ID: {c['customer_id']}\n")
                customer_map[c['customer_id']] = c['customer_name']

            # 2. Inspect Sales for all customers
            f.write("\n--- ALL SALES (Raw Inspect) ---\n")
            cursor.execute("SELECT sale_id, customer_id, sale_date, invoice_id, status FROM sales")
            sales = cursor.fetchall()
            
            customer_sales = {}
            
            for s in sales:
                cid = s['customer_id']
                if cid not in customer_sales: customer_sales[cid] = []
                
                inv_val = s['invoice_id']
                inv_repr = repr(inv_val)
                
                # Logic check
                is_null = (inv_val is None)
                is_empty = (inv_val == '')
                is_none_str = (inv_val == 'None')
                is_null_str = (inv_val == 'NULL')
                
                should_show = (is_null or is_empty or is_none_str or is_null_str)
                
                f.write(f"Sale {s['sale_id']} | Cust: {customer_map.get(cid, 'Unknown')} | Status: {s['status']} | Inv: {inv_repr} | Show? {should_show}\n")
                
                if should_show:
                    customer_sales[cid] = True

            # 3. Simulate Query
            f.write("\n--- SIMULATED QUERIES ---\n")
            for cid in customer_sales:
                cname = customer_map.get(cid, "Unknown")
                f.write(f"\nChecking Customer: {cname} ({cid})\n")
                
                query = f"SELECT * FROM sales WHERE customer_id = '{cid}' AND (invoice_id IS NULL OR invoice_id = '' OR invoice_id = 'None' OR invoice_id = 'NULL')"
                cursor.execute(query)
                results = cursor.fetchall()
                f.write(f"Query found {len(results)} sales.\n")
                for r in results:
                    f.write(f" -> Found: {r['sale_id']} (Inv: {repr(r['invoice_id'])})\n")

            conn.close()
                
        except Exception as e:
            f.write(f"Error: {e}\n")

if __name__ == "__main__":
    debug_invoice_creation()
