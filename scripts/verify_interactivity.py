
import sys
import os
import py_compile

# Add src to path
sys.path.append(os.path.join(os.getcwd(), 'src'))

print("--- Syntax Check ---")
try:
    py_compile.compile('src/gui/customers.py', doraise=True)
    print("✅ customers.py syntax OK")
except Exception as e:
    print(f"❌ customers.py syntax ERROR: {e}")
    sys.exit(1)

print("\n--- Method Check ---")
try:
    from src.gui.customers import CustomerDashboard
    if hasattr(CustomerDashboard, 'on_status_double_click'):
        print("✅ on_status_double_click exists")
    else:
        print("❌ on_status_double_click MISSING")
        
    import inspect
    method = CustomerDashboard.on_status_double_click
    sig = inspect.signature(method)
    if 'event' in sig.parameters:
        print("✅ on_status_double_click accepts event")
    else:
        print("❌ on_status_double_click bad signature")

except ImportError as e:
    print(f"Import Error: {e}")
except Exception as e:
    print(f"Error: {e}")
