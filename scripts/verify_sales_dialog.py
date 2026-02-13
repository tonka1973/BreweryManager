
import sys
import os
import inspect
import py_compile

# Add src to path
sys.path.append(os.path.join(os.getcwd(), 'src'))

print("--- Syntax Check ---")
try:
    py_compile.compile('src/gui/sales.py', doraise=True)
    print("✅ sales.py syntax OK")
    py_compile.compile('src/gui/customers.py', doraise=True)
    print("✅ customers.py syntax OK")
except Exception as e:
    print(f"❌ Syntax ERROR: {e}")
    sys.exit(1)

print("\n--- Signature Check ---")
try:
    from src.gui.sales import SaleDialog
    sig = inspect.signature(SaleDialog.__init__)
    if 'customer_id' in sig.parameters:
        print("✅ SaleDialog.__init__ accepts customer_id")
    else:
        print("❌ SaleDialog.__init__ does NOT accept customer_id")

except ImportError as e:
    print(f"Import Error: {e}")
except Exception as e:
    print(f"Error: {e}")
