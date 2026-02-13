
import tkinter as tk
import ttkbootstrap as ttk
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.getcwd(), 'src'))

from src.gui.customers import CustomerDialog

# Mock objects
class MockCache:
    def connect(self): pass
    def close(self): pass
    def get_all_records(self, table, where, order=None):
        if table == 'delivery_runs':
            return [{'run_id': '1', 'run_name': 'London', 'day_of_week': 'Monday'}]
        return []

class MockUser:
    username = "test_user"

def test_dialog():
    root = tk.Tk()
    cache = MockCache()
    user = MockUser()
    
    customer_data = {
        'customer_id': '123',
        'customer_name': 'Test Bar',
        'contact_person': 'John Doe',
        'email': 'john@example.com',
        'phone': '0123456789',
        'billing_address': '123 Main St',
        'delivery_address': '123 Main St',
        'delivery_area': '1',
        'payment_terms': '30_days',
        'notes': 'Some notes'
    }
    
    print("Attempting to create dialog...")
    try:
        dialog = CustomerDialog(root, cache, user, mode='edit', customer=customer_data)
        print("Dialog created successfully (in memory).")
        # Don't actually show it to avoid blocking, just tests init
        dialog.destroy()
        print("✅ Success")
    except Exception as e:
        print(f"❌ Failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_dialog()
