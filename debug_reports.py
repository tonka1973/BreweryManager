import tkinter as tk
import ttkbootstrap as ttk
import sys
import os
import logging
from unittest.mock import MagicMock

# Setup logging
logging.basicConfig(level=logging.DEBUG)

# Add project root to path
sys.path.insert(0, os.getcwd())

from src.gui.reports import ReportsModule
from src.data_access.sqlite_cache import SQLiteCacheManager

def test_reports_module():
    print("Initializing Root Window...")
    root = ttk.Window(themename="litera")
    
    print("Connecting to DB...")
    cache = SQLiteCacheManager()
    cache.connect()
    
    # Mock user
    user = MagicMock()
    user.username = "debug_user"
    user.role = "admin"
    
    print("Instantiating ReportsModule...")
    try:
        reports = ReportsModule(root, cache, user)
        reports.pack(fill='both', expand=True)
        print("ReportsModule instantiated and packed.")
    except Exception as e:
        print(f"CRITICAL ERROR in ReportsModule: {e}")
        import traceback
        traceback.print_exc()
        
    root.mainloop()

if __name__ == "__main__":
    test_reports_module()
