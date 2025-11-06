"""
Brewery Management System
Main Application Entry Point
"""

from src.gui.main_window import BreweryMainWindow


def main():
    """Main application entry point."""
    # Create and run the application
    app = BreweryMainWindow()
    app.run()


if __name__ == "__main__":
    main()
