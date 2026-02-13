import sys
import os
import inspect
sys.path.append(os.getcwd())

try:
    from src.gui.sales import SaleDialog
    print("Successfully imported SaleDialog")
    
    print(f"File location: {inspect.getfile(SaleDialog)}")
    
    if hasattr(SaleDialog, 'create_header_section'):
        print("PASS: SaleDialog has create_header_section")
    else:
        print("FAIL: SaleDialog MISSING create_header_section")
        
    print("\nClass Dictionary keys:")
    for k in SaleDialog.__dict__.keys():
        print(f" - {k}")
        
except ImportError as e:
    print(f"ImportError: {e}")
except Exception as e:
    print(f"Error: {e}")
