
import sqlite3
from pathlib import Path

# Path from constants.py
HOME_DIR = Path.home()
APP_DATA_DIR = HOME_DIR / ".brewerymanager"
DB_PATH = APP_DATA_DIR / "cache.db"

def verify_query():
    if not DB_PATH.exists():
        print(f"Database not found at {DB_PATH}")
        return

    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()

        # We know from debug_output.txt that we have sales with status 'reserved'
        # Let's try to fetch them using a query similar to the one we put in the code
        
        # First get a customer ID that has reserved sales
        cur.execute("SELECT customer_id FROM sales WHERE status = 'reserved' LIMIT 1")
        row = cur.fetchone()
        if not row:
            print("No reserved sales found to test with.")
            return

        customer_id = row['customer_id']
        print(f"Testing with Customer ID: {customer_id}")

        # The Query from the code:
        # f"customer_id = '{customer_id}' AND (status = 'delivered' OR status = 'reserved') AND (invoice_id IS NULL OR invoice_id = '')"
        
        sql = f"SELECT sale_id, status, delivery_date FROM sales WHERE customer_id = '{customer_id}' AND (status = 'delivered' OR status = 'reserved') AND (invoice_id IS NULL OR invoice_id = '') ORDER BY delivery_date DESC"
        
        print(f"Executing SQL: {sql}")
        cur.execute(sql)
        results = cur.fetchall()
        
        print(f"\nFound {len(results)} invoiceable sales:")
        for res in results:
            print(f"- Sale: {res['sale_id']}, Status: {res['status']}, Date: {res['delivery_date']}")

        conn.close()

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    verify_query()
