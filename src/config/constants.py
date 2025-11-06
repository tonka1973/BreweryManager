# Configuration Constants for Brewery Management System

import os
from pathlib import Path

# Application Info
APP_NAME = "Brewery Manager"
APP_VERSION = "1.0.0"
DEVELOPER = "Custom Brewery Solutions"

# File Paths
HOME_DIR = Path.home()
APP_DATA_DIR = HOME_DIR / ".brewerymanager"
CACHE_DB_PATH = APP_DATA_DIR / "cache.db"
LOG_FILE_PATH = APP_DATA_DIR / "app.log"
CONFIG_FILE_PATH = APP_DATA_DIR / "config.json"
CREDENTIALS_PATH = APP_DATA_DIR / "credentials.json"
TOKEN_PATH = APP_DATA_DIR / "token.json"

# Create app data directory if it doesn't exist
os.makedirs(APP_DATA_DIR, exist_ok=True)

# Google Sheets Configuration
GOOGLE_SHEETS_SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SPREADSHEET_NAME = "BreweryManager_Data"

# Sync Configuration
SYNC_INTERVAL_SECONDS = 300  # 5 minutes
CONNECTION_TIMEOUT_SECONDS = 10

# UI Configuration
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800
MIN_WINDOW_WIDTH = 1024
MIN_WINDOW_HEIGHT = 768

# Colors
COLOR_PRIMARY = "#2E7D32"  # Green for brewery
COLOR_SECONDARY = "#FFA000"  # Amber/gold
COLOR_SUCCESS = "#4CAF50"
COLOR_WARNING = "#FF9800"
COLOR_ERROR = "#F44336"
COLOR_INFO = "#2196F3"
COLOR_BG = "#FFFFFF"
COLOR_BG_ALT = "#F5F5F5"
COLOR_TEXT = "#212121"
COLOR_TEXT_SECONDARY = "#757575"

# Fonts
FONT_FAMILY = "Segoe UI"  # Windows default
FONT_SIZE_SMALL = 9
FONT_SIZE_NORMAL = 10
FONT_SIZE_MEDIUM = 11
FONT_SIZE_LARGE = 12
FONT_SIZE_HEADING = 14
FONT_SIZE_TITLE = 16

# UK Duty Rates (February 2025)
# These are the base rates - SPR discounts are applied per brewery
DUTY_RATES = {
    "beer_non_draught": {
        (0, 1.2): 0.00,
        (1.3, 3.4): 9.61,
        (3.5, 8.4): 21.78,  # Most craft beer
        (8.5, 22): 29.54,
        (22, 100): 32.79,
    },
    "beer_draught": {
        (0, 1.2): 0.00,
        (1.3, 3.4): 8.28,  # 13.9% discount applied
        (3.5, 8.4): 18.76,  # 13.9% discount applied
        (8.5, 22): 29.54,  # No draught relief
        (22, 100): 32.79,  # No draught relief
    },
    "cider_still_non_draught": {
        (0, 1.2): 0.00,
        (1.3, 3.4): 9.61,
        (3.5, 8.4): 10.02,
        (8.5, 22): 29.54,
        (22, 100): 32.79,
    },
    "cider_still_draught": {
        (0, 1.2): 0.00,
        (1.3, 3.4): 8.28,
        (3.5, 8.4): 8.63,  # 13.9% discount applied
        (8.5, 22): 29.54,
        (22, 100): 32.79,
    },
}

# Draught Relief Percentages (for reference)
DRAUGHT_RELIEF_BEER_CIDER = 0.139  # 13.9%
DRAUGHT_RELIEF_WINE_SPIRITS = 0.269  # 26.9%

# VAT Rate
VAT_RATE = 0.20  # 20% UK standard rate

# Container Sizes (litres)
CONTAINER_SIZES = {
    "pin": 20.5,
    "firkin": 40.9,
    "kilderkin": 81.8,
    "30l_keg": 30.0,
    "50l_keg": 50.0,
    "bottle_330ml": 0.33,
    "bottle_500ml": 0.50,
    "bottle_750ml": 0.75,
}

# Minimum container size for draught relief
MIN_DRAUGHT_CONTAINER_SIZE = 20.0  # litres

# Database Table Names (matching Google Sheets)
TABLES = {
    "recipes": "Recipes",
    "recipe_ingredients": "Recipe_Ingredients",
    "inventory_materials": "Inventory_Materials",
    "inventory_transactions": "Inventory_Transactions",
    "casks_empty": "Casks_Empty",
    "batches": "Batches",
    "fermentation_logs": "Fermentation_Logs",
    "casks_full": "Casks_Full",
    "bottles_stock": "Bottles_Stock",
    "customers": "Customers",
    "sales_calendar": "Sales_Calendar",
    "call_log": "Call_Log",
    "tasks": "Tasks",
    "sales_pipeline": "Sales_Pipeline",
    "sales": "Sales",
    "invoices": "Invoices",
    "invoice_lines": "Invoice_Lines",
    "payments": "Payments",
    "duty_returns": "Duty_Returns",
    "duty_return_lines": "Duty_Return_Lines",
    "pricing": "Pricing",
    "customer_pricing_overrides": "Customer_Pricing_Overrides",
    "users": "Users",
    "system_settings": "System_Settings",
    "audit_log": "Audit_Log",
}

# User Roles
USER_ROLES = {
    "admin": "Administrator",
    "brewer": "Brewer",
    "office": "Office Staff",
    "sales": "Sales Representative",
}

# Permissions by Role
PERMISSIONS = {
    "admin": [
        "all",  # Admins have access to everything
    ],
    "brewer": [
        "view_recipes",
        "view_inventory",
        "manage_inventory",
        "create_batches",
        "manage_batches",
        "package_batches",
        "print_labels",
        "view_sales_readonly",
    ],
    "office": [
        "view_recipes_readonly",
        "view_inventory_readonly",
        "view_batches_readonly",
        "manage_customers",
        "manage_sales",
        "manage_invoices",
        "manage_payments",
        "view_duty",
        "generate_reports",
        "use_sales_tools",
    ],
    "sales": [
        "view_customers_readonly",
        "view_stock_readonly",
        "record_sales",
        "use_sales_tools",
        "view_pricing",
    ],
}

# Validation Ranges
VALIDATION = {
    "abv_min": 0.5,
    "abv_max": 15.0,
    "abv_warning_min": 2.0,
    "abv_warning_max": 12.0,
    "batch_size_min": 50,  # litres
    "batch_size_max": 2000,  # litres
    "spr_production_max": 4500,  # hectolitres
}

# Date Formats
DATE_FORMAT = "%Y-%m-%d"
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
DISPLAY_DATE_FORMAT = "%d/%m/%Y"
DISPLAY_DATETIME_FORMAT = "%d/%m/%Y %H:%M"

# Gyle Number Format
GYLE_NUMBER_FORMAT = "GYLE-{year}-{number:03d}"

# Invoice Number Format
INVOICE_NUMBER_FORMAT = "INV-{year}-{number:04d}"

# Production Year (Feb 1 - Jan 31)
PRODUCTION_YEAR_START_MONTH = 2
PRODUCTION_YEAR_START_DAY = 1
PRODUCTION_YEAR_END_MONTH = 1
PRODUCTION_YEAR_END_DAY = 31

# Default Payment Terms
PAYMENT_TERMS = {
    "cash": "Cash on Delivery",
    "net_7": "Net 7 Days",
    "net_14": "Net 14 Days",
    "net_30": "Net 30 Days",
}

# Status Values
BATCH_STATUSES = ["brewing", "fermenting", "conditioning", "ready", "packaged"]
SALE_STATUSES = ["reserved", "delivered"]
INVOICE_STATUSES = ["unpaid", "partially_paid", "paid"]
STOCK_STATUSES = ["in_stock", "reserved", "sold"]

# Default Prices (can be overridden in system)
DEFAULT_PRICES = {
    "firkin": 65.00,
    "pin": 35.00,
    "kilderkin": 120.00,
    "30l_keg": 50.00,
    "50l_keg": 80.00,
    "bottle_500ml": 3.00,
    "bottle_330ml": 2.50,
}
