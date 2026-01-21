"""
Brewery Management System
Main Application Entry Point
"""

import sys
import traceback
import logging
import os
import shutil
import tkinter as tk
from tkinter import messagebox, filedialog
from src.gui.main_window import BreweryMainWindow
from src.config.constants import CREDENTIALS_PATH, APP_DATA_DIR


def check_credentials_setup():
    """
    Check if Google credentials exist.
    If not, confirm with user and import them via file dialog.
    """
    if os.path.exists(CREDENTIALS_PATH):
        return

    # Create a temporary root for dialogs
    root = tk.Tk()
    root.withdraw()

    # Explain the situation
    messagebox.showinfo(
        "First Run Setup",
        "Welcome to Brewery Manager!\n\n"
        "To enable Google Sheets integration, we need your 'credentials.json' file.\n"
        "Please locate the file you were provided."
    )

    # Ask for file
    file_path = filedialog.askopenfilename(
        title="Select credentials.json",
        filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")]
    )

    if file_path:
        try:
            # Ensure directory exists
            os.makedirs(APP_DATA_DIR, exist_ok=True)
            
            # Copy file
            shutil.copy(file_path, CREDENTIALS_PATH)
            
            messagebox.showinfo(
                "Setup Complete",
                "Credentials imported successfully!\n"
                "The application will now start."
            )
        except Exception as e:
            messagebox.showerror(
                "Import Error",
                f"Failed to copy credentials file:\n{str(e)}"
            )
    else:
        # User cancelled
        if messagebox.askyesno("Setup Incomplete", 
                             "You cancelled the credentials setup.\n"
                             "Google features will not work.\n\n"
                             "Do you want to continue anyway?"):
            pass
        else:
            sys.exit(0)
            
    root.destroy()


def main():
    """Main application entry point."""
    try:
        # Configure logging
        from src.config.constants import LOG_FILE_PATH
        
        # Create handlers
        file_handler = logging.FileHandler(LOG_FILE_PATH)
        console_handler = logging.StreamHandler()
        
        # Set format
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # Configure root logger
        logging.basicConfig(
            level=logging.INFO,
            handlers=[file_handler, console_handler]
        )
        
        # Check for credentials on First Run
        check_credentials_setup()
        
        # Create and run the application
        app = BreweryMainWindow()
        app.run()
    except Exception as e:
        print("CRITICAL ERROR: Application failed to start", file=sys.stderr)
        traceback.print_exc()
        # Ensure we exit with error code
        sys.exit(1)


if __name__ == "__main__":
    main()
