"""
Brewery Management System - Main Application Window
Provides the GUI interface with login, navigation, and module display.
"""

import tkinter as tk
from tkinter import messagebox
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import sys
import os
import logging
import threading

logger = logging.getLogger(__name__)

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.utilities.auth import AuthManager
from src.utilities.theme_manager import get_theme_manager
from src.utilities.window_manager import WindowManager, set_window_manager
from src.data_access.sync_manager import SyncManager
from src.data_access.sqlite_cache import SQLiteCacheManager
from src.data_access.google_sheets_client import GoogleSheetsClient
from src.utilities.ai_client import AIClient
from src.gui.assistant import AIAssistantWidget
from datetime import datetime
from src.utilities.date_utils import format_datetime_for_display

# Import all Phase 2 modules
from src.gui.dashboard import DashboardModule
from src.gui.recipes import RecipesModule
from src.gui.inventory import InventoryModule
from src.gui.batches import BatchesModule
from src.gui.customers import CustomersModule
from src.gui.sales import SalesModule
from src.gui.invoicing import InvoicingModule
from src.gui.duty import DutyModule
from src.gui.products import ProductsModule
from src.gui.reports import ReportsModule
from src.gui.settings import SettingsModule


class BreweryMainWindow:
    """Main application window with login and navigation."""

    def __init__(self):
        """Initialize the main window."""
        # Initialize theme manager
        self.theme_manager = get_theme_manager()

        # Create root window with ttkbootstrap theme (temporary size)
        self.root = ttk.Window(
            title="Brewery Management System",
            themename=self.theme_manager.current_theme,
            size=(1200, 800),
            minsize=(1000, 600)
        )

        # Initialize window manager for screen-aware sizing
        self.window_manager = WindowManager(self.root)
        set_window_manager(self.window_manager)  # Make it globally accessible

        # Initialize data access layer
        self.cache_manager = SQLiteCacheManager()
        self.cache_manager.connect()
        self.cache_manager.initialize_database()
        self.cache_manager.close()

        self.sheets_client = GoogleSheetsClient()
        
        # Trigger interactive auth if silent auth failed (e.g. missing scopes)
        if not self.sheets_client.is_authenticated:
            # This opens the browser for OAuth
            self.sheets_client.authenticate()

        # Initialize sync manager
        self.sync_manager = SyncManager(self.sheets_client, self.cache_manager)
        
        # Initialize sync state (load settings, etc)
        self.sync_manager.initialize()

        # Initialize authentication
        self.auth = AuthManager(self.cache_manager)
        
        # Initialize AI Client
        self.ai_client = AIClient(self.cache_manager)

        # Create default admin user if no users exist
        self.auth.create_default_admin()
        
        self.current_user = None
        self.current_module = None
        self.current_module_name = "Dashboard" # Track current module name for context
        
        # Widgets containers
        self.login_frame = None
        self.main_frame = None
        self.sidebar = None
        self.top_bar = None
        self.page_title_label = None # Label in top bar
        self.content_area = None
        self.status_bar = None
        
        # Setup window with screen-aware sizing and position
        self.window_manager.setup_main_window(self.root, save_on_close=True)

        # Start with login screen
        self.create_login_screen()
    
    def create_login_screen(self):
        """Create the login screen interface."""
        # Clear any existing widgets
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Create login frame
        self.login_frame = tk.Frame(self.root, bg='#f0f0f0')
        self.login_frame.pack(fill=tk.BOTH, expand=True)
        
        # Center container
        center_frame = tk.Frame(self.login_frame, bg='#f0f0f0')
        center_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        # Title
        title_label = tk.Label(
            center_frame,
            text="Brewery Management System",
            font=('Arial', 24, 'bold'),
            bg='#f0f0f0',
            fg='#333333'
        )
        title_label.pack(pady=(0, 30))
        
        # Login card
        card_frame = tk.Frame(center_frame, bg='white', relief=tk.RAISED, borderwidth=2)
        card_frame.pack(padx=40, pady=20)
        
        # Card title
        card_title = tk.Label(
            card_frame,
            text="Login",
            font=('Arial', 18, 'bold'),
            bg='white',
            fg='#333333'
        )
        card_title.pack(pady=(20, 10))
        
        # Username field
        username_label = tk.Label(
            card_frame,
            text="Username:",
            font=('Arial', 11),
            bg='white'
        )
        username_label.pack(pady=(10, 5), padx=20, anchor=tk.W)
        
        self.username_entry = tk.Entry(
            card_frame,
            font=('Arial', 11),
            width=30
        )
        self.username_entry.pack(pady=(0, 15), padx=20)
        
        # Password field
        password_label = tk.Label(
            card_frame,
            text="Password:",
            font=('Arial', 11),
            bg='white'
        )
        password_label.pack(pady=(0, 5), padx=20, anchor=tk.W)
        
        self.password_entry = tk.Entry(
            card_frame,
            font=('Arial', 11),
            width=30,
            show='*'
        )
        self.password_entry.pack(pady=(0, 20), padx=20)
        
        # Bind Enter key to login
        self.password_entry.bind('<Return>', lambda e: self.authenticate_user())
        
        # Login button
        login_button = tk.Button(
            card_frame,
            text="Login",
            font=('Arial', 12, 'bold'),
            bg='#4CAF50',
            fg='white',
            cursor='hand2',
            command=self.authenticate_user,
            width=20
        )
        login_button.pack(pady=(0, 10), padx=20)

        # Quick login button for testing
        quick_login_button = tk.Button(
            card_frame,
            text="Quick Login (Admin)",
            font=('Arial', 10),
            bg='#3498db',
            fg='white',
            cursor='hand2',
            command=self.quick_login_admin,
            width=20
        )
        quick_login_button.pack(pady=(0, 20), padx=20)

        # Error message label
        self.error_label = tk.Label(
            card_frame,
            text="",
            font=('Arial', 10),
            bg='white',
            fg='red'
        )
        self.error_label.pack(pady=(0, 10), padx=20)
        
        # Info text
        info_label = tk.Label(
            center_frame,
            text="Default credentials: admin / admin",
            font=('Arial', 9, 'italic'),
            bg='#f0f0f0',
            fg='#666666'
        )
        info_label.pack(pady=(10, 0))
        
        # Focus on username entry
        self.username_entry.focus()
    
    def authenticate_user(self):
        """Handle user login authentication."""
        username = self.username_entry.get().strip()
        password = self.password_entry.get()

        # Clear previous error
        self.error_label.config(text="")

        # Validate input
        if not username or not password:
            self.error_label.config(text="Please enter both username and password")
            return

        # Attempt login
        user = self.auth.login(username, password)

        if user:
            self.current_user = user
            self.create_main_interface()
        else:
            self.error_label.config(text="Invalid username or password")
            self.password_entry.delete(0, tk.END)

    def quick_login_admin(self):
        """Quick login with admin credentials for testing/debugging."""
        self.username_entry.delete(0, tk.END)
        self.password_entry.delete(0, tk.END)
        self.username_entry.insert(0, "admin")
        self.password_entry.insert(0, "admin")
        self.authenticate_user()

    def create_main_interface(self):
        """Create the main application interface after login."""
        # Clear login screen
        if self.login_frame:
            self.login_frame.destroy()

        # Create status bar (bottom) - Pack FIRST to reserve space
        self.create_status_bar()

        # Create main container
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create menu bar
        self.create_menu_bar()
        
        # Create Top Bar (Header with AI)
        self.create_top_bar()
        
        # Create body container (Sidebar + Content)
        body_frame = ttk.Frame(self.main_frame)
        body_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create sidebar (left navigation) - Pass body_frame instead of main_frame
        self.create_sidebar(body_frame)
        
        # Create content area (center) - Pass body_frame
        self.create_content_area(body_frame)
        
        # Load default module (Dashboard)
        self.switch_module('Dashboard')
        
        # Start connection monitoring
        self.monitor_connection()
        
        # Trigger startup sync
        self.perform_startup_sync()
        
        # Start background polling (every 5 mins)
        self.monitor_background_sync()
        
    def create_top_bar(self):
        """Create the top header bar with Page Title and AI Assistant."""
        self.top_bar = ttk.Frame(self.main_frame, bootstyle="primary")
        self.top_bar.pack(side=tk.TOP, fill=tk.X)
        
        # Inner padding container
        inner = ttk.Frame(self.top_bar, bootstyle="primary", padding=10)
        inner.pack(fill=tk.X)
        
        # LEFT: Page Title
        self.page_title_label = ttk.Label(
            inner,
            text="Dashboard",
            font=('Segoe UI', 18, 'bold'),
            bootstyle="inverse-primary"
        )
        self.page_title_label.pack(side=tk.LEFT, padx=10)
        
        # RIGHT: AI Assistant
        # Pass a callback to get current context
        ai_widget = AIAssistantWidget(inner, self.ai_client, self.get_ai_context)
        ai_widget.pack(side=tk.RIGHT, padx=10)
        
    def get_ai_context(self):
        """Return a string describing the current application state for the AI."""
        context = f"User: {self.current_user.username} ({self.current_user.role})\n"
        context += f"Current Module: {self.current_module_name}\n"
        context += f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
        return context

    def create_menu_bar(self):
        """Create the top menu bar."""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Switch User", command=self.logout)
        file_menu.add_separator()
        file_menu.add_command(label="Settings", command=self.show_settings)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.exit_application)

        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Toggle Dark Mode", command=self.toggle_theme)

        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="Documentation", command=self.show_documentation)
        help_menu.add_command(label="About", command=self.show_about)
    
    def create_sidebar(self, parent):
        """Create the left sidebar with navigation buttons."""
        self.sidebar = ttk.Frame(parent, style='dark.TFrame')
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y, ipadx=10)

        # Sidebar title
        title_label = ttk.Label(
            self.sidebar,
            text="Navigation",
            font=('Arial', 14, 'bold'),
            style='inverse.TLabel'
        )
        title_label.pack(pady=(20, 10))

        # Module buttons with modern styling
        modules = [
            'Dashboard',
            'Brewery Inventory',
            'Recipes',
            'Production',
            'Duty',
            'Products',
            'Customers',
            'Sales',
            'Invoicing',
            'Reports',
            'Settings'
        ]

        self.nav_buttons = {}
        for module in modules:
            btn = ttk.Button(
                self.sidebar,
                text=module,
                style='secondary.TButton',
                command=lambda m=module: self.switch_module(m)
            )
            btn.pack(fill=tk.X, padx=10, pady=5)
            self.nav_buttons[module] = btn

        # User info at bottom
        user_frame = ttk.Frame(self.sidebar, style='dark.TFrame')
        user_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=20)

        user_label = ttk.Label(
            user_frame,
            text=f"👤 {self.current_user.username}\n({self.current_user.role})",
            font=('Arial', 9),
            style='inverse.TLabel',
            justify=tk.CENTER
        )
        user_label.pack()

        logout_btn = ttk.Button(
            user_frame,
            text="Logout",
            bootstyle="danger",
            command=self.logout
        )
        logout_btn.pack(pady=(10, 0))
    
    def create_content_area(self, parent):
        """Create the main content area for displaying modules."""
        self.content_area = ttk.Frame(parent)
        self.content_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    def create_status_bar(self):
        """Create the bottom status bar."""
        self.status_bar = ttk.Frame(self.root)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X, pady=2)

        # Connection status
        self.status_connection = ttk.Label(
            self.status_bar,
            text="⚪ Checking...",
            font=('Arial', 9),
            bootstyle="secondary"
        )
        self.status_connection.pack(side=tk.LEFT, padx=10, pady=5)

        # User info
        self.status_user = ttk.Label(
            self.status_bar,
            text=f"User: {self.current_user.username} ({self.current_user.role})",
            font=('Arial', 9)
        )
        self.status_user.pack(side=tk.LEFT, padx=10, pady=5)

        # Last sync time
        self.status_sync = ttk.Label(
            self.status_bar,
            text="Last sync: Never",
            font=('Arial', 9)
        )
        self.status_sync.pack(side=tk.LEFT, padx=10, pady=5)

        # Resize grip (right side, before sync button)
        resize_grip = ttk.Sizegrip(self.status_bar)
        resize_grip.pack(side=tk.RIGHT, anchor='se')

        # Manual sync button
        sync_button = ttk.Button(
            self.status_bar,
            text="🔄 Sync Now",
            bootstyle="info",
            command=self.manual_sync
        )
        sync_button.pack(side=tk.RIGHT, padx=10, pady=3)
    
    def switch_module(self, module_name):
        """Switch to a different module in the content area."""
        # Update current module tracker
        self.current_module = module_name
        self.current_module_name = module_name
        
        # Update Top Bar Title
        if self.page_title_label:
            self.page_title_label.config(text=module_name)

        # Update button styles (highlight active)
        for name, btn in self.nav_buttons.items():
            if name == module_name:
                btn.config(bootstyle="success")
            else:
                btn.config(bootstyle="secondary")
        
        # Clear content area
        for widget in self.content_area.winfo_children():
            widget.destroy()

        # Load the actual module content
        self.load_module_content(module_name)
    
    def load_module_content(self, module_name):
        """Load the content for a specific module."""
        # Map module names to their classes
        module_map = {
            'Dashboard': DashboardModule,
            'Brewery Inventory': InventoryModule,
            'Recipes': RecipesModule,
            'Production': BatchesModule,
            'Duty': DutyModule,
            'Products': ProductsModule,
            'Customers': CustomersModule,
            'Sales': SalesModule,
            'Invoicing': InvoicingModule,
            'Reports': ReportsModule,
            'Settings': SettingsModule
        }

        # Get the module class
        module_class = module_map.get(module_name)

        if module_class:
            # Create module instance with required parameters
            # Dashboard module accepts navigate_callback, others don't
            # Create module instance with required parameters
            if module_name == 'Dashboard':
                module = module_class(
                    parent=self.content_area,
                    cache_manager=self.cache_manager,
                    current_user=self.current_user,
                    navigate_callback=self.switch_module
                )
            elif module_name == 'Settings':
                module = module_class(
                    parent=self.content_area,
                    cache_manager=self.cache_manager,
                    current_user=self.current_user,
                    sheets_client=self.sheets_client,
                    sync_callback=self.trigger_auto_save_sync
                )
            elif module_name == 'Brewery Inventory':
                module = module_class(
                    parent=self.content_area,
                    cache_manager=self.cache_manager,
                    current_user=self.current_user,
                    sync_callback=self.trigger_auto_save_sync
                )
            elif module_name == 'Production':
                module = module_class(
                    parent=self.content_area,
                    cache_manager=self.cache_manager,
                    current_user=self.current_user,
                    sync_callback=self.trigger_auto_save_sync
                )
            elif module_name in ['Recipes', 'Duty', 'Products', 'Customers', 'Sales', 'Invoicing']:
                module = module_class(
                    parent=self.content_area,
                    cache_manager=self.cache_manager,
                    current_user=self.current_user,
                    sync_callback=self.trigger_auto_save_sync
                )
            else:
                module = module_class(
                    parent=self.content_area,
                    cache_manager=self.cache_manager,
                    current_user=self.current_user
                )
            module.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        else:
            # Fallback for unknown modules
            content_frame = ttk.Frame(self.content_area)
            content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

            error_label = ttk.Label(
                content_frame,
                text=f"Module '{module_name}' not found.",
                font=('Arial', 14),
                bootstyle="danger"
            )
            error_label.pack(pady=50)
    
    def update_status_bar(self):
        """Update the status bar information."""
        # Use cached status from SyncManager instead of blocking check
        is_online = self.sync_manager.is_online

        if is_online:
            self.status_connection.config(text="🟢 Online", bootstyle="success")
        else:
            self.status_connection.config(text="🔴 Offline", bootstyle="danger")
        
        if self.sync_manager.sync_in_progress:
            self.status_sync.config(text="🔄 Syncing...", bootstyle="info")
        else:
            # Update last sync time
            last_sync = self.sync_manager.get_last_sync_time()
            if last_sync:
                # Format from DB format (YYYY-MM-DD HH:MM:SS) to Display (DD/MM/YYYY HH:MM)
                display_sync = format_datetime_for_display(last_sync)
                self.status_sync.config(text=f"Last sync: {display_sync}", bootstyle="default")
            else:
                self.status_sync.config(text="Last sync: Never", bootstyle="default")
    
    def manual_sync(self):
        """Manually trigger a sync operation."""
        try:
            # Check if online
            if not self.sync_manager.check_connection():
                messagebox.showwarning(
                    "Offline",
                    "Cannot sync while offline. Please check your internet connection."
                )
                return
            
            # Perform sync
            logger.info("Starting manual sync...")
            result = self.sync_manager.incremental_sync()
            
            if result and "error" not in result:
                messagebox.showinfo("Sync Complete", "Data synchronized successfully!")
                self.update_status_bar()
            else:
                error_msg = result.get("error", "Unknown error") if result else "Unknown error"
                messagebox.showerror("Sync Failed", f"Failed to synchronize data.\nError: {error_msg}")
        
        except Exception as e:
            messagebox.showerror("Sync Error", f"An error occurred during sync:\n{str(e)}")
    
    def logout(self):
        """Log out current user and return to login screen."""
        if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            self.auth.logout()
            self.current_user = None
            self.current_module = None
            
            # Destroy main interface
            if self.main_frame:
                self.main_frame.destroy()
            
            # Show login screen
            self.create_login_screen()

    def perform_startup_sync(self):
        """Perform an automatic sync on startup."""
        def sync_task():
            # Wait a few seconds for connection check to settle
            import time
            time.sleep(2) 
            
            if self.sync_manager.check_connection():
                logger.info("Performing startup sync...")
                # UI update handled by monitor_connection -> update_status_bar
                
                result = self.sync_manager.incremental_sync()
                
                # Final UI update handled by monitor_connection
            else:
                logger.info("Skipping startup sync (offline)")

        threading.Thread(target=sync_task, daemon=True).start()

    def trigger_auto_save_sync(self):
        """Trigger a background sync after a save operation."""
        def sync_task():
            if self.sync_manager.is_online: # Use cached status for speed check
                logger.info("Auto-syncing after save...")
                 # UI update handled by monitor_connection -> update_status_bar
                
                self.sync_manager.incremental_sync()
                
                # Final UI update handled by monitor_connection

        threading.Thread(target=sync_task, daemon=True).start()

    def monitor_connection(self):
        """Periodically check connection status in background."""
        if self.main_frame and self.main_frame.winfo_exists():
            # Run blocking check in a thread
            thread = threading.Thread(target=self._check_connection_thread, daemon=True)
            thread.start()
            
            # Schedule next check in 3 seconds
            self.root.after(3000, self.monitor_connection)

    def monitor_background_sync(self):
        """Periodically run background sync (every 5 minutes)."""
        if self.main_frame and self.main_frame.winfo_exists():
            # Run blocking check in a thread
            def bg_sync_task():
                if self.sync_manager.is_online and not self.sync_manager.sync_in_progress:
                   # UI update handled by monitor_connection -> update_status_bar 
                   logger.info("Starting background auto-sync...")
                   self.sync_manager.incremental_sync()
                   
            threading.Thread(target=bg_sync_task, daemon=True).start()
            
            # Schedule next check in 5 minutes (300,000 ms)
            self.root.after(300000, self.monitor_background_sync)

    def _check_connection_thread(self):
        """Worker thread checking connection."""
        try:
            self.sync_manager.check_connection()
            # Update UI on main thread
            self.root.after(0, self.update_status_bar)
        except Exception as e:
            logger.error(f"Error in connection thread: {e}")
    
    def show_settings(self):
        """Show settings dialog (placeholder)."""
        messagebox.showinfo(
            "Settings",
            "Settings dialog coming in Phase 2!\n\n"
            "Will include:\n"
            "• Sync interval configuration\n"
            "• Offline mode preferences\n"
            "• Display settings\n"
            "• User management"
        )
    
    def show_documentation(self):
        """Show documentation dialog (placeholder)."""
        messagebox.showinfo(
            "Documentation",
            "User documentation coming soon!\n\n"
            "For now, see:\n"
            "• TECHNICAL_SPECIFICATION.md\n"
            "• UK_ALCOHOL_DUTY_REFERENCE.md"
        )
    
    def show_about(self):
        """Show about dialog."""
        messagebox.showinfo(
            "About",
            "Brewery Management System\n"
            "Version 1.0\n\n"
            "A comprehensive brewery management solution\n"
            "with offline capability and cloud sync.\n\n"
            "Phase 1: Core Infrastructure ✅\n"
            "Phase 2: Module Implementation ✅\n"
            "Phase 3: Integration & Testing (In Progress)\n"
            "Phase 4: Windows Installer (Final)"
        )
    
    def toggle_theme(self):
        """Toggle between light and dark theme."""
        # Toggle theme mode
        new_theme = self.theme_manager.toggle_mode()

        # Apply new theme to window
        self.root.style.theme_use(new_theme)

        # Show confirmation message
        mode = "Dark" if self.theme_manager.is_dark_mode() else "Light"
        messagebox.showinfo(
            "Theme Changed",
            f"Theme switched to {mode} mode!\n\n"
            f"Using theme: {new_theme}\n\n"
            "Some components may require restart for full effect."
        )

    def exit_application(self):
        """Exit the application."""
        if messagebox.askyesno("Exit", "Are you sure you want to exit?"):
            self.root.quit()
            self.root.destroy()
    
    def run(self):
        """Start the application main loop."""
        self.root.mainloop()


# Entry point for testing
if __name__ == "__main__":
    app = BreweryMainWindow()
    app.run()
