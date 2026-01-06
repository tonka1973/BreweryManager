"""
Brewery Management System
Main Application Entry Point
"""

import sys
import traceback
import logging
from src.gui.main_window import BreweryMainWindow


def main():
    """Main application entry point."""
    try:
        # Configure logging to print to console if file logging fails
        logging.basicConfig(level=logging.INFO)
        
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
