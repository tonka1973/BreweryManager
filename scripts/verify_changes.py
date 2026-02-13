
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.getcwd(), 'src'))

try:
    from src.gui.invoicing import InvoiceViewDialog, InvoiceCreateDialog
    from src.gui.customers import CustomerDashboard
    
    print("Imports successful.")
    
    if hasattr(InvoiceViewDialog, 'generate_pdf'):
        print("✅ InvoiceViewDialog.generate_pdf exists")
    else:
        print("❌ InvoiceViewDialog.generate_pdf MISSING")

    if hasattr(CustomerDashboard, 'create_invoice'):
        print("✅ CustomerDashboard.create_invoice exists")
    else:
        print("❌ CustomerDashboard.create_invoice MISSING")

    # Check init signature of InvoiceCreateDialog
    import inspect
    sig = inspect.signature(InvoiceCreateDialog.__init__)
    if 'customer_id' in sig.parameters:
        print("✅ InvoiceCreateDialog accepts customer_id")
    else:
        print("❌ InvoiceCreateDialog DOES NOT accept customer_id")

except ImportError as e:
    print(f"Import Error: {e}")
except Exception as e:
    print(f"Error: {e}")
