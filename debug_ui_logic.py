
import sqlite3
import tkinter as tk
from tkinter import ttk
import os
from pathlib import Path

# Mock classes to simulate the environment
class MockCache:
    def __init__(self, db_path):
        self.db_path = db_path
        self.connection = None
        self.cursor = None

    def connect(self):
        self.connection = sqlite3.connect(self.db_path)
        self.connection.row_factory = sqlite3.Row
        self.cursor = self.connection.cursor()

    def close(self):
        if self.connection: self.connection.close()

    def get_all_records(self, table, where=None, order=None):
        query = f"SELECT * FROM {table}"
        if where: query += f" WHERE {where}"
        if order: query += f" ORDER BY {order}"
        
        self.connect()
        print(f"Executing: {query}")
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        self.close()
        return rows

def format_date_for_display(date_str):
    return date_str  # Simplified

def debug_ui_logic():
    home = Path.home()
    db_path = home / ".brewerymanager" / "cache.db"
    
    if not db_path.exists():
        print(f"DB not found.")
        return

    print("--- SIMULATING UI LOGIC ---")
    cache = MockCache(db_path)
    
    # Simulate: The Crossways
    customer_name = "The Crossways"
    customer_id = "95925643-2949-4bd4-bbd3-0ab4fd69d979"
    selected_sale_ids = []

    print(f"Loading sales for: {customer_name} ({customer_id})")

    try:
        # EXACT Logic from Invoicing.py
        sales = cache.get_all_records('sales',
                                      f"customer_id = '{customer_id}' AND (invoice_id IS NULL OR invoice_id = '' OR invoice_id = 'None' OR invoice_id = 'NULL')",
                                      'delivery_date DESC')
        
        print(f"Found {len(sales)} sales.")
        
        for sale in sales:
            is_selected = '☑' if sale['sale_id'] in selected_sale_ids else '☐'
            
            # Simulate value creation
            values = (is_selected, format_date_for_display(sale.get('delivery_date', '')), sale.get('beer_name', ''),
                     sale.get('quantity', 0), f"£{sale.get('unit_price', 0):.2f}",
                     f"£{sale.get('line_total', 0):.2f}")
            
            print(f" -> Inserting: {values}")

    except Exception as e:
        print(f"ERROR in logic: {e}")

if __name__ == "__main__":
    debug_ui_logic()
