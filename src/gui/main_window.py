"""
Brewery Management System - Main Application Window
Provides the GUI interface with login, navigation, and module display.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.utilities.auth import AuthManager
from src.data_access.sync_manager import SyncManager
from src.data_access.sqlite_cache import SQLiteCacheManager
from src.data_access.google_sheets_client import GoogleSheetsClient
from datetime import datetime


class BreweryMainWindow:
    """Main application window with login and navigation."""
    
    def __init__(self):
        """Initialize the main window."""
        self.root = tk.Tk()
        self.root.title("Brewery Management System")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 600)
        
        # Initialize data access layer
        self.cache_manager = SQLiteCacheManager()
        self.sheets_client = GoogleSheetsClient()
        
        # Initialize sync manager
        self.sync_manager = SyncManager(self.sheets_client, self.cache_manager)
        
        # Initialize authentication
        self.auth = AuthManager(self.cache_manager)
        
        # Create default admin user if no users exist
        self.auth.create_default_admin()
        
        self.current_user = None
        self.current_module = None
        
        # Widgets containers
        self.login_frame = None
        self.main_frame = None
        self.sidebar = None
        self.content_area = None
        self.status_bar = None
        
        # Center window on screen
        self.center_window()
        
        # Start with login screen
        self.create_login_screen()
    
    def center_window(self):
        """Center the window on the screen."""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
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
        login_button.pack(pady=(0, 20), padx=20)
        
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
    
    def create_main_interface(self):
        """Create the main application interface after login."""
        # Clear login screen
        if self.login_frame:
            self.login_frame.destroy()
        
        # Create main container
        self.main_frame = tk.Frame(self.root, bg='white')
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create menu bar
        self.create_menu_bar()
        
        # Create sidebar (left navigation)
        self.create_sidebar()
        
        # Create content area (center)
        self.create_content_area()
        
        # Create status bar (bottom)
        self.create_status_bar()
        
        # Load default module (Dashboard)
        self.switch_module('Dashboard')
    
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
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="Documentation", command=self.show_documentation)
        help_menu.add_command(label="About", command=self.show_about)
    
    def create_sidebar(self):
        """Create the left sidebar with navigation buttons."""
        self.sidebar = tk.Frame(self.main_frame, bg='#2c3e50', width=200)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)
        self.sidebar.pack_propagate(False)
        
        # Sidebar title
        title_label = tk.Label(
            self.sidebar,
            text="Navigation",
            font=('Arial', 14, 'bold'),
            bg='#2c3e50',
            fg='white'
        )
        title_label.pack(pady=(20, 10))
        
        # Module buttons
        modules = [
            'Dashboard',
            'Recipes',
            'Inventory',
            'Batches',
            'Customers',
            'Sales',
            'Invoicing',
            'Duty Calculator',
            'Label Printing'
        ]
        
        self.nav_buttons = {}
        for module in modules:
            btn = tk.Button(
                self.sidebar,
                text=module,
                font=('Arial', 11),
                bg='#34495e',
                fg='white',
                activebackground='#4CAF50',
                activeforeground='white',
                cursor='hand2',
                relief=tk.FLAT,
                bd=0,
                command=lambda m=module: self.switch_module(m)
            )
            btn.pack(fill=tk.X, padx=10, pady=5)
            self.nav_buttons[module] = btn
        
        # User info at bottom
        user_frame = tk.Frame(self.sidebar, bg='#2c3e50')
        user_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=20)
        
        user_label = tk.Label(
            user_frame,
            text=f"👤 {self.current_user.username}\n({self.current_user.role})",
            font=('Arial', 9),
            bg='#2c3e50',
            fg='white',
            justify=tk.CENTER
        )
        user_label.pack()
        
        logout_btn = tk.Button(
            user_frame,
            text="Logout",
            font=('Arial', 9),
            bg='#e74c3c',
            fg='white',
            cursor='hand2',
            command=self.logout
        )
        logout_btn.pack(pady=(10, 0))
    
    def create_content_area(self):
        """Create the main content area for displaying modules."""
        self.content_area = tk.Frame(self.main_frame, bg='white')
        self.content_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    
    def create_status_bar(self):
        """Create the bottom status bar."""
        self.status_bar = tk.Frame(self.root, bg='#ecf0f1', relief=tk.SUNKEN, bd=1)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Connection status
        self.status_connection = tk.Label(
            self.status_bar,
            text="🟢 Online",
            font=('Arial', 9),
            bg='#ecf0f1',
            fg='#27ae60'
        )
        self.status_connection.pack(side=tk.LEFT, padx=10, pady=5)
        
        # User info
        self.status_user = tk.Label(
            self.status_bar,
            text=f"User: {self.current_user.username} ({self.current_user.role})",
            font=('Arial', 9),
            bg='#ecf0f1'
        )
        self.status_user.pack(side=tk.LEFT, padx=10, pady=5)
        
        # Last sync time
        self.status_sync = tk.Label(
            self.status_bar,
            text="Last sync: Never",
            font=('Arial', 9),
            bg='#ecf0f1'
        )
        self.status_sync.pack(side=tk.LEFT, padx=10, pady=5)
        
        # Manual sync button
        sync_button = tk.Button(
            self.status_bar,
            text="🔄 Sync Now",
            font=('Arial', 9),
            bg='#3498db',
            fg='white',
            cursor='hand2',
            command=self.manual_sync
        )
        sync_button.pack(side=tk.RIGHT, padx=10, pady=3)
    
    def switch_module(self, module_name):
        """Switch to a different module in the content area."""
        # Update current module
        self.current_module = module_name
        
        # Update button colors (highlight active)
        for name, btn in self.nav_buttons.items():
            if name == module_name:
                btn.config(bg='#4CAF50')
            else:
                btn.config(bg='#34495e')
        
        # Clear content area
        for widget in self.content_area.winfo_children():
            widget.destroy()
        
        # Create module header
        header_frame = tk.Frame(self.content_area, bg='white')
        header_frame.pack(fill=tk.X, padx=20, pady=(20, 10))
        
        module_title = tk.Label(
            header_frame,
            text=module_name,
            font=('Arial', 20, 'bold'),
            bg='white',
            fg='#2c3e50'
        )
        module_title.pack(anchor=tk.W)
        
        # Separator
        separator = ttk.Separator(self.content_area, orient='horizontal')
        separator.pack(fill=tk.X, padx=20, pady=10)
        
        # Module content (placeholder for now - Phase 2 will implement actual modules)
        self.load_module_content(module_name)
    
    def load_module_content(self, module_name):
        """Load the content for a specific module (placeholder for Phase 2)."""
        content_frame = tk.Frame(self.content_area, bg='white')
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        if module_name == 'Dashboard':
            # Dashboard placeholder
            welcome_label = tk.Label(
                content_frame,
                text=f"Welcome, {self.current_user.username}!",
                font=('Arial', 16),
                bg='white',
                fg='#2c3e50'
            )
            welcome_label.pack(pady=20)
            
            info_label = tk.Label(
                content_frame,
                text="Phase 1 Complete! 🎉\n\n"
                     "The core infrastructure is ready:\n"
                     "• User Authentication ✅\n"
                     "• Google Sheets Sync ✅\n"
                     "• Local Database ✅\n"
                     "• GUI Framework ✅\n\n"
                     "Phase 2 will implement all 9 modules.\n"
                     "Select a module from the sidebar to continue.",
                font=('Arial', 12),
                bg='white',
                fg='#34495e',
                justify=tk.LEFT
            )
            info_label.pack(pady=20)
        
        else:
            # Other modules placeholder
            placeholder_label = tk.Label(
                content_frame,
                text=f"{module_name} module coming in Phase 2!",
                font=('Arial', 14),
                bg='white',
                fg='#7f8c8d'
            )
            placeholder_label.pack(pady=50)
    
    def update_status_bar(self):
        """Update the status bar information."""
        # Check connection status
        is_online = self.sync_manager.check_connection()
        
        if is_online:
            self.status_connection.config(text="🟢 Online", fg='#27ae60')
        else:
            self.status_connection.config(text="🔴 Offline", fg='#e74c3c')
        
        # Update last sync time
        last_sync = self.sync_manager.get_last_sync_time()
        if last_sync:
            self.status_sync.config(text=f"Last sync: {last_sync}")
        else:
            self.status_sync.config(text="Last sync: Never")
    
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
            result = self.sync_manager.sync_all()
            
            if result:
                messagebox.showinfo("Sync Complete", "Data synchronized successfully!")
                self.update_status_bar()
            else:
                messagebox.showerror("Sync Failed", "Failed to synchronize data.")
        
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
            "Phase 2: Module Implementation (Coming Soon)\n"
            "Phase 3: Windows Installer (Final)"
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
