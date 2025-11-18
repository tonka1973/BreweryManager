"""
Dashboard Module for Brewery Management System
Provides overview of key metrics, alerts, and recent activity
"""

import tkinter as tk
import ttkbootstrap as ttk
from datetime import datetime, timedelta
from typing import Optional
from ..utilities.window_manager import enable_mousewheel_scrolling, enable_treeview_keyboard_navigation


class DashboardModule(ttk.Frame):
    """Dashboard module showing overview and quick stats"""

    def __init__(self, parent, cache_manager, current_user, navigate_callback=None):
        """
        Initialize the Dashboard module.

        Args:
            parent: Parent widget
            cache_manager: SQLiteCacheManager instance
            current_user: Current logged-in user
            navigate_callback: Function to call for navigation to other modules
        """
        super().__init__(parent)
        self.cache = cache_manager
        self.current_user = current_user
        self.navigate = navigate_callback

        # Create dashboard layout
        self.create_widgets()

        # Load data
        self.refresh_data()

    def create_widgets(self):
        """Create all dashboard widgets"""
        # Welcome section
        welcome_frame = ttk.Frame(self)
        welcome_frame.pack(fill=tk.X, padx=20, pady=(0, 20))

        welcome_label = ttk.Label(
            welcome_frame,
            text=f"Welcome back, {self.current_user.full_name}!",
            font=('Arial', 16, 'bold')
        )
        welcome_label.pack(side=tk.LEFT)

        date_label = ttk.Label(
            welcome_frame,
            text=datetime.now().strftime("%A, %d/%m/%Y"),
            font=('Arial', 11)
        )
        date_label.pack(side=tk.RIGHT)

        # Quick stats cards
        self.create_stats_cards()

        # Two column layout for content
        content_frame = ttk.Frame(self)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # Left column
        left_column = ttk.Frame(content_frame)
        left_column.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        # Right column
        right_column = ttk.Frame(content_frame)
        right_column.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0))

        # Recent batches (left)
        self.create_recent_batches(left_column)

        # Alerts section (right top)
        self.create_alerts_section(right_column)

        # Upcoming deliveries (right bottom)
        self.create_upcoming_deliveries(right_column)

    def create_stats_cards(self):
        """Create quick stats cards at the top"""
        stats_frame = ttk.Frame(self)
        stats_frame.pack(fill=tk.X, padx=20, pady=(0, 20))

        # Get stats data
        self.cache.connect()

        # Total batches
        all_batches = self.cache.get_all_records('batches')
        total_batches = len(all_batches)

        # Active batches (brewing/fermenting/conditioning)
        active_batches = [b for b in all_batches if b.get('status') in ['brewing', 'fermenting', 'conditioning']]
        active_count = len(active_batches)

        # Total customers
        customers = self.cache.get_all_records('customers', 'is_active = 1')
        total_customers = len(customers)

        # Sales this month
        current_month = datetime.now().strftime('%Y-%m')
        sales = self.cache.get_all_records('sales', f"sale_date LIKE '{current_month}%'")
        monthly_sales = len(sales)

        self.cache.close()

        # Create cards (now clickable) with bright, readable colors
        self.create_stat_card(stats_frame, "Total Batches", str(total_batches), "#2196F3", 0, "Production")  # Bright Blue
        self.create_stat_card(stats_frame, "In Production", str(active_count), "#FF9800", 1, "Production")  # Bright Orange
        self.create_stat_card(stats_frame, "Customers", str(total_customers), "#4CAF50", 2, "Customers")  # Bright Green
        self.create_stat_card(stats_frame, "Sales (Month)", str(monthly_sales), "#9C27B0", 3, "Sales")  # Bright Purple

    def create_stat_card(self, parent, title, value, color, column, destination=None):
        """Create a single stat card as a clickable frame"""
        # Frame wrapper (keep tk.Frame for specific color requirements)
        card = tk.Frame(
            parent,
            relief=tk.RAISED,
            borderwidth=2,
            cursor='hand2' if destination and self.navigate else 'arrow',
            highlightbackground=color,
            highlightthickness=3
        )
        # Explicitly configure background color
        card.configure(bg=color)
        card.grid(row=0, column=column, padx=8, pady=5, sticky='ew')
        parent.grid_columnconfigure(column, weight=1)

        # Make clickable if navigate callback exists
        if destination and self.navigate:
            card.bind('<Button-1>', lambda e: self.navigate(destination))

        # Value (larger font, more padding) - keep tk.Label for colored background
        value_label = tk.Label(
            card,
            text=value,
            font=('Arial', 20, 'bold'),
            fg='white'
        )
        # Explicitly configure background color
        value_label.configure(bg=color)
        value_label.pack(pady=(15, 5), fill=tk.BOTH, expand=True)

        # Make label clickable too
        if destination and self.navigate:
            value_label.bind('<Button-1>', lambda e: self.navigate(destination))
            value_label.config(cursor='hand2')

        # Title (larger font) - keep tk.Label for colored background
        title_label = tk.Label(
            card,
            text=title,
            font=('Arial', 10),
            fg='white'
        )
        # Explicitly configure background color
        title_label.configure(bg=color)
        title_label.pack(pady=(0, 15), fill=tk.BOTH, expand=True)

        # Make label clickable too
        if destination and self.navigate:
            title_label.bind('<Button-1>', lambda e: self.navigate(destination))
            title_label.config(cursor='hand2')

    def create_recent_batches(self, parent):
        """Create recent batches section"""
        # Section header
        header_frame = ttk.Frame(parent)
        header_frame.pack(fill=tk.X, pady=(0, 10))

        header_label = ttk.Label(
            header_frame,
            text="Production Flow",
            font=('Arial', 13, 'bold')
        )
        header_label.pack(side=tk.LEFT)

        # Batches list
        list_frame = ttk.Frame(parent, relief=tk.SOLID, borderwidth=1)
        list_frame.pack(fill=tk.BOTH, expand=True)

        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Treeview
        columns = ('Gyle', 'Recipe', 'Date', 'Status')
        self.batches_tree = ttk.Treeview(
            list_frame,
            columns=columns,
            show='headings',
            height=8,
            yscrollcommand=scrollbar.set
        )

        # Column headings
        self.batches_tree.heading('Gyle', text='Gyle Number')
        self.batches_tree.heading('Recipe', text='Beer Name')
        self.batches_tree.heading('Date', text='Brew Date')
        self.batches_tree.heading('Status', text='Status')

        # Column widths
        self.batches_tree.column('Gyle', width=120)
        self.batches_tree.column('Recipe', width=150)
        self.batches_tree.column('Date', width=100)
        self.batches_tree.column('Status', width=100)

        self.batches_tree.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.batches_tree.yview)

        enable_mousewheel_scrolling(self.batches_tree)
        enable_treeview_keyboard_navigation(self.batches_tree)

        # Load recent batches
        self.load_recent_batches()

    def load_recent_batches(self):
        """Load recent batches into treeview"""
        # Clear existing
        for item in self.batches_tree.get_children():
            self.batches_tree.delete(item)

        # Get recent batches
        self.cache.connect()
        batches = self.cache.get_all_records('batches', order_by='brew_date DESC')
        self.cache.close()

        # Show last 10
        for batch in batches[:10]:
            gyle = batch.get('gyle_number', 'N/A')
            recipe_id = batch.get('recipe_id', '')

            # Get recipe name
            beer_name = 'Unknown'
            if recipe_id:
                self.cache.connect()
                recipes = self.cache.get_all_records('recipes', f"recipe_id = '{recipe_id}'")
                self.cache.close()
                if recipes:
                    beer_name = recipes[0].get('recipe_name', 'Unknown')

            brew_date_raw = batch.get('brew_date', 'N/A')
            # Convert date format from YYYY-MM-DD to DD/MM/YYYY
            if brew_date_raw != 'N/A':
                try:
                    date_obj = datetime.strptime(brew_date_raw, '%Y-%m-%d')
                    brew_date = date_obj.strftime('%d/%m/%Y')
                except:
                    brew_date = brew_date_raw
            else:
                brew_date = 'N/A'

            status = batch.get('status', 'N/A').capitalize()

            # Color code by status
            tag = 'status_' + batch.get('status', 'unknown')
            self.batches_tree.insert('', 'end', values=(gyle, beer_name, brew_date, status), tags=(tag,))

        # Tag colors
        self.batches_tree.tag_configure('status_brewing', background='#e3f2fd')
        self.batches_tree.tag_configure('status_fermenting', background='#fff3e0')
        self.batches_tree.tag_configure('status_conditioning', background='#f3e5f5')
        self.batches_tree.tag_configure('status_ready', background='#e8f5e9')
        self.batches_tree.tag_configure('status_packaged', background='#f5f5f5')

    def create_alerts_section(self, parent):
        """Create alerts section for low stock, etc."""
        # Section header
        header_frame = ttk.Frame(parent)
        header_frame.pack(fill=tk.X, pady=(0, 10))

        header_label = ttk.Label(
            header_frame,
            text="⚠️ Alerts",
            font=('Arial', 13, 'bold')
        )
        header_label.pack(side=tk.LEFT)

        # Alerts container
        alerts_frame = ttk.Frame(parent, relief=tk.SOLID, borderwidth=1)
        alerts_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # Check for alerts
        self.cache.connect()

        alerts = []

        # Low stock materials
        materials = self.cache.get_all_records('inventory_materials')
        for material in materials:
            current = material.get('current_stock', 0)
            reorder = material.get('reorder_level', 0)
            if reorder and current <= reorder:
                alerts.append({
                    'type': 'Low Stock',
                    'message': f"{material.get('material_name')} is low ({current} {material.get('unit')})",
                    'color': '#ff9800'
                })

        # Batches ready for packaging
        ready_batches = self.cache.get_all_records('batches', "status = 'ready'")
        if ready_batches:
            count = len(ready_batches)
            alerts.append({
                'type': 'Ready',
                'message': f"{count} batch{'es' if count > 1 else ''} ready for packaging",
                'color': '#4caf50'
            })

        # Overdue invoices
        invoices = self.cache.get_all_records('invoices', "payment_status != 'paid'")
        overdue = []
        for inv in invoices:
            due_date = inv.get('due_date')
            if due_date and due_date < datetime.now().strftime('%Y-%m-%d'):
                overdue.append(inv)

        if overdue:
            count = len(overdue)
            alerts.append({
                'type': 'Overdue',
                'message': f"{count} overdue invoice{'s' if count > 1 else ''}",
                'color': '#f44336'
            })

        self.cache.close()

        # Display alerts
        if alerts:
            for alert in alerts[:5]:  # Show max 5 alerts
                self.create_alert_item(alerts_frame, alert)
        else:
            no_alerts = ttk.Label(
                alerts_frame,
                text="✓ No alerts - everything looks good!",
                font=('Arial', 11),
                padding=(0, 20)
            )
            no_alerts.pack()

    def create_alert_item(self, parent, alert):
        """Create a single alert item"""
        # Keep tk.Frame for specific color requirements
        alert_frame = tk.Frame(parent, bg=alert['color'], relief=tk.FLAT)
        alert_frame.pack(fill=tk.X, padx=5, pady=5)

        # Keep tk.Label for colored background
        type_label = tk.Label(
            alert_frame,
            text=f"[{alert['type']}]",
            font=('Arial', 9, 'bold'),
            bg=alert['color'],
            fg='white',
            padx=10,
            pady=5
        )
        type_label.pack(side=tk.LEFT)

        # Keep tk.Label for colored background
        msg_label = tk.Label(
            alert_frame,
            text=alert['message'],
            font=('Arial', 10),
            bg=alert['color'],
            fg='white',
            padx=10,
            pady=5
        )
        msg_label.pack(side=tk.LEFT)

    def create_upcoming_deliveries(self, parent):
        """Create upcoming deliveries section"""
        # Section header
        header_frame = ttk.Frame(parent)
        header_frame.pack(fill=tk.X, pady=(10, 10))

        header_label = ttk.Label(
            header_frame,
            text="📦 Upcoming Deliveries",
            font=('Arial', 13, 'bold')
        )
        header_label.pack(side=tk.LEFT)

        # Deliveries container
        deliveries_frame = ttk.Frame(parent, relief=tk.SOLID, borderwidth=1)
        deliveries_frame.pack(fill=tk.BOTH, expand=True)

        # Get upcoming deliveries
        self.cache.connect()
        today = datetime.now().strftime('%Y-%m-%d')
        next_week = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')

        deliveries = self.cache.get_all_records(
            'sales',
            f"status = 'reserved' AND delivery_date >= '{today}' AND delivery_date <= '{next_week}'",
            order_by='delivery_date'
        )

        self.cache.close()

        # Display deliveries
        if deliveries:
            for delivery in deliveries[:5]:  # Show max 5
                self.create_delivery_item(deliveries_frame, delivery)
        else:
            no_deliveries = ttk.Label(
                deliveries_frame,
                text="No deliveries scheduled this week",
                font=('Arial', 10),
                padding=(0, 20)
            )
            no_deliveries.pack()

    def create_delivery_item(self, parent, delivery):
        """Create a single delivery item"""
        # Keep tk.Frame for specific color requirements
        item_frame = tk.Frame(parent, bg='#ecf0f1', relief=tk.FLAT)
        item_frame.pack(fill=tk.X, padx=5, pady=3)

        # Date (convert to DD/MM/YYYY)
        delivery_date_raw = delivery.get('delivery_date', 'N/A')
        if delivery_date_raw != 'N/A':
            try:
                date_obj = datetime.strptime(delivery_date_raw, '%Y-%m-%d')
                delivery_date_formatted = date_obj.strftime('%d/%m/%Y')
            except:
                delivery_date_formatted = delivery_date_raw
        else:
            delivery_date_formatted = 'N/A'

        # Keep tk.Label for colored background
        date_label = tk.Label(
            item_frame,
            text=delivery_date_formatted,
            font=('Arial', 9, 'bold'),
            bg='#ecf0f1',
            fg='#2c3e50',
            width=12
        )
        date_label.pack(side=tk.LEFT, padx=5, pady=5)

        # Customer and details
        self.cache.connect()
        customers = self.cache.get_all_records('customers', f"customer_id = '{delivery.get('customer_id')}'")
        self.cache.close()

        customer_name = customers[0].get('customer_name', 'Unknown') if customers else 'Unknown'

        details = f"{customer_name} - {delivery.get('beer_name', 'N/A')} ({delivery.get('quantity', 0)} x {delivery.get('container_type', 'N/A')})"

        # Keep tk.Label for colored background
        details_label = tk.Label(
            item_frame,
            text=details,
            font=('Arial', 9),
            bg='#ecf0f1',
            fg='#34495e',
            anchor='w'
        )
        details_label.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5, pady=5)

    def refresh_data(self):
        """Refresh all dashboard data"""
        # This method can be called to reload all data
        # For now, data is loaded in create methods
        pass
