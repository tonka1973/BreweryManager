"""
Reports Module - Comprehensive Business Reports
Includes Sales, Inventory, Production, Financial, and Duty Reports
"""

import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import tkinter as tk
from tkinter import messagebox
from datetime import datetime, timedelta
from decimal import Decimal
import calendar


class ReportsModule(ttk.Frame):
    """Reports module for viewing historical duty returns"""

    def __init__(self, parent, cache_manager, current_user):
        super().__init__(parent)
        self.cache = cache_manager
        self.current_user = current_user

        self.create_widgets()

    def create_widgets(self):
        """Create the module interface"""
        # Title
        title_frame = ttk.Frame(self)
        title_frame.pack(fill=X, padx=20, pady=(20, 10))

        title_label = ttk.Label(
            title_frame,
            text="📊 Business Reports",
            font=("Helvetica", 16, "bold")
        )
        title_label.pack(side=LEFT)

        # Info label
        info_label = ttk.Label(
            title_frame,
            text="Comprehensive analytics and reporting across all brewery operations",
            font=("Helvetica", 10)
        )
        info_label.pack(side=LEFT, padx=(15, 0))

        # Notebook for tabs with better visibility
        self.notebook = ttk.Notebook(self, bootstyle="primary")
        self.notebook.pack(fill=BOTH, expand=True, padx=20, pady=10)

        # Create all report tabs
        self.sales_tab = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.sales_tab, text="  Sales Reports  ")

        self.inventory_tab = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.inventory_tab, text="  Inventory Reports  ")

        self.production_tab = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.production_tab, text="  Production Reports  ")

        self.financial_tab = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.financial_tab, text="  Financial Reports  ")

        self.duty_reports_tab = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.duty_reports_tab, text="  Duty Reports  ")

        # Create tab content
        self.create_sales_tab()
        self.create_inventory_tab()
        self.create_production_tab()
        self.create_financial_tab()
        self.create_duty_reports_tab()

    # ================================================================
    # SALES REPORTS TAB
    # ================================================================
    def create_sales_tab(self):
        """Sales Reports - Revenue, customers, products performance"""

        # Date range selector
        control_frame = ttk.Frame(self.sales_tab)
        control_frame.pack(fill=X, padx=10, pady=10)

        ttk.Label(control_frame, text="Period:").pack(side=LEFT, padx=(0, 5))

        self.sales_period = ttk.Combobox(
            control_frame,
            values=['Last 7 Days', 'Last 30 Days', 'Last 90 Days', 'Year to Date', 'All Time'],
            state='readonly',
            width=15
        )
        self.sales_period.set('Last 30 Days')
        self.sales_period.pack(side=LEFT, padx=(0, 10))
        self.sales_period.bind('<<ComboboxSelected>>', lambda e: self.load_sales_report())

        ttk.Button(
            control_frame,
            text="🔄 Refresh",
            command=self.load_sales_report,
            bootstyle=PRIMARY
        ).pack(side=LEFT)

        # Summary cards
        summary_frame = ttk.Frame(self.sales_tab)
        summary_frame.pack(fill=X, padx=10, pady=10)

        self.sales_summary_cards = {}
        card_data = [
            ('total_revenue', '💰 Total Revenue', '£0.00', SUCCESS),
            ('total_volume', '🍺 Volume Sold', '0 L', INFO),
            ('total_orders', '📦 Total Orders', '0', PRIMARY),
            ('avg_order', '📊 Avg Order Value', '£0.00', WARNING)
        ]

        for i, (key, label, default, style) in enumerate(card_data):
            card = ttk.Frame(summary_frame, bootstyle=style, relief=RAISED)
            card.pack(side=LEFT, fill=BOTH, expand=True, padx=5)

            ttk.Label(card, text=label, font=('Helvetica', 10)).pack(pady=(10, 5))
            value_label = ttk.Label(card, text=default, font=('Helvetica', 16, 'bold'))
            value_label.pack(pady=(0, 10))
            self.sales_summary_cards[key] = value_label

        # Notebook for different sales views
        sales_notebook = ttk.Notebook(self.sales_tab)
        sales_notebook.pack(fill=BOTH, expand=True, padx=10, pady=10)

        # Tab 1: By Product
        product_frame = ttk.Frame(sales_notebook)
        sales_notebook.add(product_frame, text="By Product")

        columns = ('product', 'quantity', 'litres', 'revenue', 'avg_price')
        self.sales_by_product_tree = ttk.Treeview(
            product_frame,
            columns=columns,
            show='tree headings',
            height=15
        )

        self.sales_by_product_tree.heading('#0', text='Beer Name')
        self.sales_by_product_tree.heading('product', text='Container Type')
        self.sales_by_product_tree.heading('quantity', text='Qty Sold')
        self.sales_by_product_tree.heading('litres', text='Litres')
        self.sales_by_product_tree.heading('revenue', text='Revenue')
        self.sales_by_product_tree.heading('avg_price', text='Avg Price/L')

        self.sales_by_product_tree.column('#0', width=200)
        self.sales_by_product_tree.column('product', width=150)
        self.sales_by_product_tree.column('quantity', width=100)
        self.sales_by_product_tree.column('litres', width=100)
        self.sales_by_product_tree.column('revenue', width=120)
        self.sales_by_product_tree.column('avg_price', width=120)

        scrollbar = ttk.Scrollbar(product_frame, orient=VERTICAL, command=self.sales_by_product_tree.yview)
        self.sales_by_product_tree.configure(yscrollcommand=scrollbar.set)

        self.sales_by_product_tree.pack(side=LEFT, fill=BOTH, expand=True)
        scrollbar.pack(side=RIGHT, fill=Y)

        # Tab 2: By Customer
        customer_frame = ttk.Frame(sales_notebook)
        sales_notebook.add(customer_frame, text="By Customer")

        columns = ('orders', 'litres', 'revenue', 'last_order')
        self.sales_by_customer_tree = ttk.Treeview(
            customer_frame,
            columns=columns,
            show='headings',
            height=15
        )

        self.sales_by_customer_tree.heading('orders', text='Customer Name')
        self.sales_by_customer_tree.heading('litres', text='Total Orders')
        self.sales_by_customer_tree.heading('revenue', text='Litres')
        self.sales_by_customer_tree.heading('last_order', text='Revenue')

        self.sales_by_customer_tree.column('orders', width=250)
        self.sales_by_customer_tree.column('litres', width=150)
        self.sales_by_customer_tree.column('revenue', width=150)
        self.sales_by_customer_tree.column('last_order', width=200)

        scrollbar2 = ttk.Scrollbar(customer_frame, orient=VERTICAL, command=self.sales_by_customer_tree.yview)
        self.sales_by_customer_tree.configure(yscrollcommand=scrollbar2.set)

        self.sales_by_customer_tree.pack(side=LEFT, fill=BOTH, expand=True)
        scrollbar2.pack(side=RIGHT, fill=Y)

        # Load initial data
        self.load_sales_report()

    # ================================================================
    # INVENTORY REPORTS TAB
    # ================================================================
    def create_inventory_tab(self):
        """Inventory Reports - Stock levels, aging, value"""

        # Control bar
        control_frame = ttk.Frame(self.inventory_tab)
        control_frame.pack(fill=X, padx=10, pady=10)

        ttk.Label(control_frame, text="Show:").pack(side=LEFT, padx=(0, 5))

        self.inventory_filter = ttk.Combobox(
            control_frame,
            values=['All Stock', 'Finished Goods Only', 'Raw Materials Only', 'Low Stock Alerts'],
            state='readonly',
            width=20
        )
        self.inventory_filter.set('Finished Goods Only')
        self.inventory_filter.pack(side=LEFT, padx=(0, 10))
        self.inventory_filter.bind('<<ComboboxSelected>>', lambda e: self.load_inventory_report())

        ttk.Button(
            control_frame,
            text="🔄 Refresh",
            command=self.load_inventory_report,
            bootstyle=PRIMARY
        ).pack(side=LEFT)

        # Summary cards
        summary_frame = ttk.Frame(self.inventory_tab)
        summary_frame.pack(fill=X, padx=10, pady=10)

        self.inventory_summary_cards = {}
        card_data = [
            ('total_stock', '🍺 Total Stock', '0 L', INFO),
            ('stock_value', '💷 Stock Value', '£0.00', SUCCESS),
            ('products', '📦 Products', '0', PRIMARY),
            ('low_stock', '⚠️ Low Stock Items', '0', DANGER)
        ]

        for i, (key, label, default, style) in enumerate(card_data):
            card = ttk.Frame(summary_frame, bootstyle=style, relief=RAISED)
            card.pack(side=LEFT, fill=BOTH, expand=True, padx=5)

            ttk.Label(card, text=label, font=('Helvetica', 10)).pack(pady=(10, 5))
            value_label = ttk.Label(card, text=default, font=('Helvetica', 16, 'bold'))
            value_label.pack(pady=(0, 10))
            self.inventory_summary_cards[key] = value_label

        # Stock table
        table_frame = ttk.Frame(self.inventory_tab)
        table_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)

        columns = ('product', 'quantity', 'litres', 'age_days', 'value', 'status')
        self.inventory_tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show='headings',
            height=20
        )

        self.inventory_tree.heading('product', text='Product / Material')
        self.inventory_tree.heading('quantity', text='Quantity')
        self.inventory_tree.heading('litres', text='Litres / Unit')
        self.inventory_tree.heading('age_days', text='Age (Days)')
        self.inventory_tree.heading('value', text='Est. Value')
        self.inventory_tree.heading('status', text='Status')

        self.inventory_tree.column('product', width=250)
        self.inventory_tree.column('quantity', width=100)
        self.inventory_tree.column('litres', width=120)
        self.inventory_tree.column('age_days', width=100)
        self.inventory_tree.column('value', width=120)
        self.inventory_tree.column('status', width=150)

        scrollbar = ttk.Scrollbar(table_frame, orient=VERTICAL, command=self.inventory_tree.yview)
        self.inventory_tree.configure(yscrollcommand=scrollbar.set)

        self.inventory_tree.pack(side=LEFT, fill=BOTH, expand=True)
        scrollbar.pack(side=RIGHT, fill=Y)

        # Load initial data
        self.load_inventory_report()

    # ================================================================
    # PRODUCTION REPORTS TAB
    # ================================================================
    def create_production_tab(self):
        """Production Reports - Volumes, efficiency, brewer performance"""

        # Date range selector
        control_frame = ttk.Frame(self.production_tab)
        control_frame.pack(fill=X, padx=10, pady=10)

        ttk.Label(control_frame, text="Period:").pack(side=LEFT, padx=(0, 5))

        self.production_period = ttk.Combobox(
            control_frame,
            values=['Last 30 Days', 'Last 90 Days', 'Year to Date', 'All Time'],
            state='readonly',
            width=15
        )
        self.production_period.set('Last 90 Days')
        self.production_period.pack(side=LEFT, padx=(0, 10))
        self.production_period.bind('<<ComboboxSelected>>', lambda e: self.load_production_report())

        ttk.Button(
            control_frame,
            text="🔄 Refresh",
            command=self.load_production_report,
            bootstyle=PRIMARY
        ).pack(side=LEFT)

        # Summary cards
        summary_frame = ttk.Frame(self.production_tab)
        summary_frame.pack(fill=X, padx=10, pady=10)

        self.production_summary_cards = {}
        card_data = [
            ('total_batches', '🍺 Total Batches', '0', INFO),
            ('total_volume', '📊 Total Volume', '0 L', SUCCESS),
            ('avg_efficiency', '⚙️ Avg Waste %', '0%', WARNING),
            ('packaged_volume', '📦 Packaged Volume', '0 L', PRIMARY)
        ]

        for i, (key, label, default, style) in enumerate(card_data):
            card = ttk.Frame(summary_frame, bootstyle=style, relief=RAISED)
            card.pack(side=LEFT, fill=BOTH, expand=True, padx=5)

            ttk.Label(card, text=label, font=('Helvetica', 10)).pack(pady=(10, 5))
            value_label = ttk.Label(card, text=default, font=('Helvetica', 16, 'bold'))
            value_label.pack(pady=(0, 10))
            self.production_summary_cards[key] = value_label

        # Production notebook
        prod_notebook = ttk.Notebook(self.production_tab)
        prod_notebook.pack(fill=BOTH, expand=True, padx=10, pady=10)

        # Tab 1: By Style
        style_frame = ttk.Frame(prod_notebook)
        prod_notebook.add(style_frame, text="By Style")

        columns = ('batches', 'volume', 'avg_abv', 'packaged')
        self.production_by_style_tree = ttk.Treeview(
            style_frame,
            columns=columns,
            show='headings',
            height=15
        )

        self.production_by_style_tree.heading('batches', text='Beer Style')
        self.production_by_style_tree.heading('volume', text='Batches')
        self.production_by_style_tree.heading('avg_abv', text='Total Volume (L)')
        self.production_by_style_tree.heading('packaged', text='Avg ABV %')

        self.production_by_style_tree.column('batches', width=250)
        self.production_by_style_tree.column('volume', width=150)
        self.production_by_style_tree.column('avg_abv', width=200)
        self.production_by_style_tree.column('packaged', width=150)

        scrollbar = ttk.Scrollbar(style_frame, orient=VERTICAL, command=self.production_by_style_tree.yview)
        self.production_by_style_tree.configure(yscrollcommand=scrollbar.set)

        self.production_by_style_tree.pack(side=LEFT, fill=BOTH, expand=True)
        scrollbar.pack(side=RIGHT, fill=Y)

        # Tab 2: By Brewer
        brewer_frame = ttk.Frame(prod_notebook)
        prod_notebook.add(brewer_frame, text="By Brewer")

        columns = ('batches', 'volume', 'waste_pct')
        self.production_by_brewer_tree = ttk.Treeview(
            brewer_frame,
            columns=columns,
            show='headings',
            height=15
        )

        self.production_by_brewer_tree.heading('batches', text='Brewer')
        self.production_by_brewer_tree.heading('volume', text='Batches Brewed')
        self.production_by_brewer_tree.heading('waste_pct', text='Total Volume (L)')

        self.production_by_brewer_tree.column('batches', width=250)
        self.production_by_brewer_tree.column('volume', width=200)
        self.production_by_brewer_tree.column('waste_pct', width=200)

        scrollbar2 = ttk.Scrollbar(brewer_frame, orient=VERTICAL, command=self.production_by_brewer_tree.yview)
        self.production_by_brewer_tree.configure(yscrollcommand=scrollbar2.set)

        self.production_by_brewer_tree.pack(side=LEFT, fill=BOTH, expand=True)
        scrollbar2.pack(side=RIGHT, fill=Y)

        # Tab 3: Packaging Breakdown
        packaging_frame = ttk.Frame(prod_notebook)
        prod_notebook.add(packaging_frame, text="Packaging Mix")

        columns = ('quantity', 'litres', 'percentage')
        self.production_packaging_tree = ttk.Treeview(
            packaging_frame,
            columns=columns,
            show='headings',
            height=15
        )

        self.production_packaging_tree.heading('quantity', text='Container Type')
        self.production_packaging_tree.heading('litres', text='Units Packaged')
        self.production_packaging_tree.heading('percentage', text='Total Litres')

        self.production_packaging_tree.column('quantity', width=250)
        self.production_packaging_tree.column('litres', width=200)
        self.production_packaging_tree.column('percentage', width=200)

        scrollbar3 = ttk.Scrollbar(packaging_frame, orient=VERTICAL, command=self.production_packaging_tree.yview)
        self.production_packaging_tree.configure(yscrollcommand=scrollbar3.set)

        self.production_packaging_tree.pack(side=LEFT, fill=BOTH, expand=True)
        scrollbar3.pack(side=RIGHT, fill=Y)

        # Load initial data
        self.load_production_report()

    # ================================================================
    # FINANCIAL REPORTS TAB
    # ================================================================
    def create_financial_tab(self):
        """Financial Reports - P&L, duty impact, costs"""

        # Date range selector
        control_frame = ttk.Frame(self.financial_tab)
        control_frame.pack(fill=X, padx=10, pady=10)

        ttk.Label(control_frame, text="Period:").pack(side=LEFT, padx=(0, 5))

        self.financial_period = ttk.Combobox(
            control_frame,
            values=['Last 30 Days', 'Last 90 Days', 'Year to Date', 'Custom Range'],
            state='readonly',
            width=15
        )
        self.financial_period.set('Last 90 Days')
        self.financial_period.pack(side=LEFT, padx=(0, 10))
        self.financial_period.bind('<<ComboboxSelected>>', lambda e: self.load_financial_report())

        ttk.Button(
            control_frame,
            text="🔄 Refresh",
            command=self.load_financial_report,
            bootstyle=PRIMARY
        ).pack(side=LEFT)

        # Summary cards
        summary_frame = ttk.Frame(self.financial_tab)
        summary_frame.pack(fill=X, padx=10, pady=10)

        self.financial_summary_cards = {}
        card_data = [
            ('revenue', '💰 Revenue', '£0.00', SUCCESS),
            ('cogs', '📦 COGS', '£0.00', WARNING),
            ('duty', '🏛️ Duty Paid', '£0.00', DANGER),
            ('profit', '📊 Gross Profit', '£0.00', INFO)
        ]

        for i, (key, label, default, style) in enumerate(card_data):
            card = ttk.Frame(summary_frame, bootstyle=style, relief=RAISED)
            card.pack(side=LEFT, fill=BOTH, expand=True, padx=5)

            ttk.Label(card, text=label, font=('Helvetica', 10)).pack(pady=(10, 5))
            value_label = ttk.Label(card, text=default, font=('Helvetica', 16, 'bold'))
            value_label.pack(pady=(0, 10))
            self.financial_summary_cards[key] = value_label

        # Financial details table
        table_frame = ttk.Frame(self.financial_tab)
        table_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)

        # Create a nice P&L statement view
        ttk.Label(
            table_frame,
            text="Profit & Loss Statement",
            font=('Helvetica', 14, 'bold')
        ).pack(pady=(0, 10))

        columns = ('category', 'amount', 'percentage')
        self.financial_tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show='tree headings',
            height=20
        )

        self.financial_tree.heading('#0', text='Line Item')
        self.financial_tree.heading('category', text='Category')
        self.financial_tree.heading('amount', text='Amount')
        self.financial_tree.heading('percentage', text='% of Revenue')

        self.financial_tree.column('#0', width=250)
        self.financial_tree.column('category', width=200)
        self.financial_tree.column('amount', width=150)
        self.financial_tree.column('percentage', width=150)

        scrollbar = ttk.Scrollbar(table_frame, orient=VERTICAL, command=self.financial_tree.yview)
        self.financial_tree.configure(yscrollcommand=scrollbar.set)

        self.financial_tree.pack(side=LEFT, fill=BOTH, expand=True)
        scrollbar.pack(side=RIGHT, fill=Y)

        # Load initial data
        self.load_financial_report()

    # ================================================================
    # DUTY REPORTS TAB (EXISTING)
    # ================================================================
    def create_duty_reports_tab(self):
        """Create the duty reports tab showing all past returns"""

        # Control frame
        control_frame = ttk.Frame(self.duty_reports_tab)
        control_frame.pack(fill=X, padx=10, pady=10)

        # Filter by year
        ttk.Label(control_frame, text="Filter by Year:").pack(side=LEFT, padx=(0, 5))

        self.year_filter = ttk.Combobox(
            control_frame,
            width=10,
            state='readonly'
        )
        self.year_filter.pack(side=LEFT, padx=(0, 20))
        self.year_filter.bind('<<ComboboxSelected>>', lambda e: self.load_duty_returns())

        # Refresh button
        ttk.Button(
            control_frame,
            text="🔄 Refresh",
            command=self.load_duty_returns,
            bootstyle=INFO
        ).pack(side=LEFT, padx=5)

        # Export button (placeholder)
        ttk.Button(
            control_frame,
            text="📥 Export to Excel",
            command=self.export_to_excel,
            bootstyle=SUCCESS
        ).pack(side=LEFT, padx=5)

        # Annual summary button
        ttk.Button(
            control_frame,
            text="📈 Annual Summary",
            command=self.show_annual_summary,
            bootstyle=PRIMARY
        ).pack(side=LEFT, padx=5)

        # Returns list frame
        list_frame = ttk.Frame(self.duty_reports_tab)
        list_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)

        # Scrollbars
        y_scroll = ttk.Scrollbar(list_frame, orient=VERTICAL)
        y_scroll.pack(side=RIGHT, fill=Y)

        x_scroll = ttk.Scrollbar(list_frame, orient=HORIZONTAL)
        x_scroll.pack(side=BOTTOM, fill=X)

        # Treeview for duty returns
        columns = (
            'month', 'status', 'total_litres', 'total_lpa',
            'production_duty', 'spoilt_reclaim', 'net_payable',
            'submitted_date', 'payment_date'
        )

        self.returns_tree = ttk.Treeview(
            list_frame,
            columns=columns,
            show='headings',
            yscrollcommand=y_scroll.set,
            xscrollcommand=x_scroll.set
        )

        y_scroll.config(command=self.returns_tree.yview)
        x_scroll.config(command=self.returns_tree.xview)

        # Configure columns
        self.returns_tree.heading('month', text='Duty Month')
        self.returns_tree.heading('status', text='Status')
        self.returns_tree.heading('total_litres', text='Total Litres')
        self.returns_tree.heading('total_lpa', text='Total LPA')
        self.returns_tree.heading('production_duty', text='Production Duty')
        self.returns_tree.heading('spoilt_reclaim', text='Spoilt Reclaim')
        self.returns_tree.heading('net_payable', text='Net Payable')
        self.returns_tree.heading('submitted_date', text='Submitted')
        self.returns_tree.heading('payment_date', text='Payment Date')

        self.returns_tree.column('month', width=100, anchor=W)
        self.returns_tree.column('status', width=100, anchor=CENTER)
        self.returns_tree.column('total_litres', width=100, anchor=E)
        self.returns_tree.column('total_lpa', width=100, anchor=E)
        self.returns_tree.column('production_duty', width=120, anchor=E)
        self.returns_tree.column('spoilt_reclaim', width=120, anchor=E)
        self.returns_tree.column('net_payable', width=120, anchor=E)
        self.returns_tree.column('submitted_date', width=100, anchor=CENTER)
        self.returns_tree.column('payment_date', width=100, anchor=CENTER)

        self.returns_tree.pack(fill=BOTH, expand=True)

        # Bind double-click to view details
        self.returns_tree.bind('<Double-Button-1>', self.view_return_details)

        # Context menu
        self.context_menu = tk.Menu(self.returns_tree, tearoff=0)
        self.context_menu.add_command(label="View Details", command=self.view_return_details)
        self.context_menu.add_command(label="View Packaging Lines", command=self.view_packaging_lines)
        self.context_menu.add_command(label="View Spoilt Beer", command=self.view_spoilt_beer)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Export This Return", command=self.export_single_return)

        self.returns_tree.bind('<Button-3>', self.show_context_menu)

        # Summary frame at bottom
        summary_frame = ttk.LabelFrame(
            self.duty_reports_tab,
            text="Summary",
            padding=10
        )
        summary_frame.pack(fill=X, padx=10, pady=(0, 10))

        self.summary_label = ttk.Label(
            summary_frame,
            text="No returns loaded",
            font=("Helvetica", 10)
        )
        self.summary_label.pack()

        # Load initial data
        self.populate_year_filter()
        self.load_duty_returns()

    def populate_year_filter(self):
        """Populate the year filter dropdown"""
        self.cache.connect()

        cursor = self.cache.cursor

        cursor.execute('''
            SELECT DISTINCT substr(duty_month, 1, 4) as year
            FROM duty_returns
            ORDER BY year DESC
        ''')

        years = [row[0] for row in cursor.fetchall()]

        # Add "All Years" option
        years.insert(0, "All Years")

        self.year_filter['values'] = years
        if years:
            self.year_filter.current(0)

    def load_duty_returns(self):
        """Load all duty returns from database"""
        # Clear existing items
        for item in self.returns_tree.get_children():
            self.returns_tree.delete(item)

        self.cache.connect()


        cursor = self.cache.cursor

        # Build query with optional year filter
        year_filter = self.year_filter.get()
        if year_filter and year_filter != "All Years":
            where_clause = f"WHERE duty_month LIKE '{year_filter}-%'"
        else:
            where_clause = ""

        cursor.execute(f'''
            SELECT
                duty_month,
                status,
                draught_low_litres + draught_std_litres + non_draught_litres + high_abv_litres as total_litres,
                draught_low_lpa + draught_std_lpa + non_draught_lpa + high_abv_lpa as total_lpa,
                production_duty_total,
                spoilt_duty_reclaim,
                net_duty_payable,
                submitted_date,
                payment_date
            FROM duty_returns
            {where_clause}
            ORDER BY duty_month DESC
        ''')

        rows = cursor.fetchall()

        total_production = 0.0
        total_reclaim = 0.0
        total_net = 0.0

        for row in rows:
            month, status, litres, lpa, prod_duty, reclaim, net, submitted, payment = row

            # Format values
            litres_str = f"{litres:.2f}L" if litres else "0.00L"
            lpa_str = f"{lpa:.2f}" if lpa else "0.00"
            prod_str = f"£{prod_duty:.2f}" if prod_duty else "£0.00"
            reclaim_str = f"£{reclaim:.2f}" if reclaim else "£0.00"
            net_str = f"£{net:.2f}" if net else "£0.00"

            submitted_str = submitted if submitted else "-"
            payment_str = payment if payment else "-"

            # Status badge
            status_display = status.upper() if status else "IN PROGRESS"

            self.returns_tree.insert('', END, values=(
                month,
                status_display,
                litres_str,
                lpa_str,
                prod_str,
                reclaim_str,
                net_str,
                submitted_str,
                payment_str
            ))

            # Sum totals
            total_production += prod_duty or 0
            total_reclaim += reclaim or 0
            total_net += net or 0

        # Update summary
        count = len(rows)
        summary_text = (
            f"Showing {count} return(s)  |  "
            f"Total Production Duty: £{total_production:.2f}  |  "
            f"Total Spoilt Reclaim: £{total_reclaim:.2f}  |  "
            f"Total Net Payable: £{total_net:.2f}"
        )
        self.summary_label.config(text=summary_text)

    def show_context_menu(self, event):
        """Show context menu on right-click"""
        item = self.returns_tree.identify_row(event.y)
        if item:
            self.returns_tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)

    def view_return_details(self, event=None):
        """View detailed breakdown of a selected return"""
        selection = self.returns_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a duty return to view.")
            return

        item = selection[0]
        values = self.returns_tree.item(item, 'values')
        duty_month = values[0]

        # Fetch full details from database
        self.cache.connect()

        cursor = self.cache.cursor

        cursor.execute('''
            SELECT * FROM duty_returns WHERE duty_month = ?
        ''', (duty_month,))

        row = cursor.fetchone()
        if not row:
            messagebox.showerror("Error", "Could not find duty return details.")
            return

        # Show details dialog
        DutyReturnDetailsDialog(self, duty_month, row)

    def view_packaging_lines(self):
        """View all packaging lines for selected month"""
        selection = self.returns_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a duty return to view packaging lines.")
            return

        item = selection[0]
        values = self.returns_tree.item(item, 'values')
        duty_month = values[0]

        PackagingLinesDialog(self, duty_month)

    def view_spoilt_beer(self):
        """View all spoilt beer for selected month"""
        selection = self.returns_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a duty return to view spoilt beer.")
            return

        item = selection[0]
        values = self.returns_tree.item(item, 'values')
        duty_month = values[0]

        SpoiltBeerDialog(self, duty_month)

    def show_annual_summary(self):
        """Show annual summary of duty returns"""
        AnnualSummaryDialog(self, self.cache)

    def export_to_excel(self):
        """Export all visible returns to Excel (placeholder)"""
        messagebox.showinfo(
            "Export to Excel",
            "Excel export functionality will be implemented in a future update.\n\n"
            "This will export all duty returns to an Excel workbook with separate sheets for:\n"
            "• Monthly returns summary\n"
            "• Packaging lines detail\n"
            "• Spoilt beer records\n"
            "• Annual totals"
        )

    def export_single_return(self):
        """Export selected return to Excel (placeholder)"""
        selection = self.returns_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a duty return to export.")
            return

        item = selection[0]
        values = self.returns_tree.item(item, 'values')
        duty_month = values[0]

        messagebox.showinfo(
            "Export Return",
            f"Excel export for {duty_month} will be implemented in a future update.\n\n"
            "This will create a detailed workbook with all data for this return period."
        )


class DutyReturnDetailsDialog(tk.Toplevel):
    """Dialog to show full breakdown of a duty return"""

    def __init__(self, parent, duty_month, return_data):
        super().__init__(parent)
        self.duty_month = duty_month
        self.return_data = return_data

        self.title(f"Duty Return Details - {duty_month}")
        self.geometry("800x700")

        # Make modal
        self.transient(parent)
        self.grab_set()

        self.create_widgets()

    def create_widgets(self):
        """Create the dialog widgets"""
        # Unpack data (matches duty_returns table structure)
        (id, duty_month,
         dl_litres, dl_lpa, dl_duty,
         ds_litres, ds_lpa, ds_duty,
         nd_litres, nd_lpa, nd_duty,
         ha_litres, ha_lpa, ha_duty,
         production_total,
         spoilt_reclaim, under_decl, over_decl,
         net_payable,
         status, submitted_date, payment_date, payment_ref,
         created_at, updated_at) = self.return_data

        # Scrollable frame
        canvas = tk.Canvas(self)
        scrollbar = ttk.Scrollbar(self, orient=VERTICAL, command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Title
        title_label = ttk.Label(
            scrollable_frame,
            text=f"HMRC Duty Return - {duty_month}",
            font=("Helvetica", 14, "bold")
        )
        title_label.pack(pady=10)

        # Category 1: Draught <3.5% ABV
        cat1_frame = ttk.LabelFrame(
            scrollable_frame,
            text="Category 1: Draught <3.5% ABV (SPR Low)",
            padding=10
        )
        cat1_frame.pack(fill=X, padx=20, pady=5)

        ttk.Label(cat1_frame, text=f"Volume: {dl_litres:.2f} litres").pack(anchor=W)
        ttk.Label(cat1_frame, text=f"Pure Alcohol: {dl_lpa:.2f} LPA").pack(anchor=W)
        ttk.Label(cat1_frame, text=f"Duty: £{dl_duty:.2f}", font=("Helvetica", 10, "bold")).pack(anchor=W)

        # Category 2: Draught 3.5-8.4% ABV
        cat2_frame = ttk.LabelFrame(
            scrollable_frame,
            text="Category 2: Draught 3.5-8.4% ABV (SPR Standard)",
            padding=10
        )
        cat2_frame.pack(fill=X, padx=20, pady=5)

        ttk.Label(cat2_frame, text=f"Volume: {ds_litres:.2f} litres").pack(anchor=W)
        ttk.Label(cat2_frame, text=f"Pure Alcohol: {ds_lpa:.2f} LPA").pack(anchor=W)
        ttk.Label(cat2_frame, text=f"Duty: £{ds_duty:.2f}", font=("Helvetica", 10, "bold")).pack(anchor=W)

        # Category 3: Non-Draught 3.5-8.4% ABV
        cat3_frame = ttk.LabelFrame(
            scrollable_frame,
            text="Category 3: Non-Draught 3.5-8.4% ABV (SPR Standard)",
            padding=10
        )
        cat3_frame.pack(fill=X, padx=20, pady=5)

        ttk.Label(cat3_frame, text=f"Volume: {nd_litres:.2f} litres").pack(anchor=W)
        ttk.Label(cat3_frame, text=f"Pure Alcohol: {nd_lpa:.2f} LPA").pack(anchor=W)
        ttk.Label(cat3_frame, text=f"Duty: £{nd_duty:.2f}", font=("Helvetica", 10, "bold")).pack(anchor=W)

        # Category 4: High ABV 8.5-22% (No SPR)
        cat4_frame = ttk.LabelFrame(
            scrollable_frame,
            text="Category 4: High ABV 8.5-22% (No SPR)",
            padding=10
        )
        cat4_frame.pack(fill=X, padx=20, pady=5)

        ttk.Label(cat4_frame, text=f"Volume: {ha_litres:.2f} litres").pack(anchor=W)
        ttk.Label(cat4_frame, text=f"Pure Alcohol: {ha_lpa:.2f} LPA").pack(anchor=W)
        ttk.Label(cat4_frame, text=f"Duty: £{ha_duty:.2f}", font=("Helvetica", 10, "bold")).pack(anchor=W)

        # Production total
        prod_frame = ttk.LabelFrame(
            scrollable_frame,
            text="Production Duty Total",
            padding=10
        )
        prod_frame.pack(fill=X, padx=20, pady=10)

        ttk.Label(
            prod_frame,
            text=f"£{production_total:.2f}",
            font=("Helvetica", 12, "bold")
        ).pack()

        # Adjustments
        adj_frame = ttk.LabelFrame(
            scrollable_frame,
            text="Adjustments",
            padding=10
        )
        adj_frame.pack(fill=X, padx=20, pady=5)

        ttk.Label(adj_frame, text=f"Spoilt Beer Duty Reclaim: -£{spoilt_reclaim:.2f}").pack(anchor=W)
        ttk.Label(adj_frame, text=f"Under Declarations (previous): +£{under_decl:.2f}").pack(anchor=W)
        ttk.Label(adj_frame, text=f"Over Declarations (previous): -£{over_decl:.2f}").pack(anchor=W)

        # Net payable
        net_frame = ttk.LabelFrame(
            scrollable_frame,
            text="NET DUTY PAYABLE TO HMRC",
            padding=10
        )
        net_frame.pack(fill=X, padx=20, pady=10)

        ttk.Label(
            net_frame,
            text=f"£{net_payable:.2f}",
            font=("Helvetica", 14, "bold"),
            foreground="red" if net_payable > 0 else "green"
        ).pack()

        # Status information
        status_frame = ttk.LabelFrame(
            scrollable_frame,
            text="Return Status",
            padding=10
        )
        status_frame.pack(fill=X, padx=20, pady=5)

        ttk.Label(status_frame, text=f"Status: {status.upper() if status else 'IN PROGRESS'}").pack(anchor=W)
        ttk.Label(status_frame, text=f"Submitted: {submitted_date if submitted_date else 'Not submitted'}").pack(anchor=W)
        ttk.Label(status_frame, text=f"Payment Date: {payment_date if payment_date else 'Not paid'}").pack(anchor=W)
        ttk.Label(status_frame, text=f"Payment Reference: {payment_ref if payment_ref else 'N/A'}").pack(anchor=W)

        # Metadata
        meta_frame = ttk.LabelFrame(
            scrollable_frame,
            text="Metadata",
            padding=10
        )
        meta_frame.pack(fill=X, padx=20, pady=5)

        ttk.Label(meta_frame, text=f"Created: {created_at}").pack(anchor=W)
        ttk.Label(meta_frame, text=f"Last Updated: {updated_at if updated_at else 'Never'}").pack(anchor=W)

        # Close button
        ttk.Button(
            scrollable_frame,
            text="Close",
            command=self.destroy,
            bootstyle=SECONDARY
        ).pack(pady=20)

        # Pack canvas and scrollbar
        canvas.pack(side=LEFT, fill=BOTH, expand=True)
        scrollbar.pack(side=RIGHT, fill=Y)


class PackagingLinesDialog(tk.Toplevel):
    """Dialog to show all packaging lines for a duty month"""

    def __init__(self, parent, duty_month):
        super().__init__(parent)
        self.duty_month = duty_month

        self.title(f"Packaging Lines - {duty_month}")
        self.geometry("1200x600")

        # Make modal
        self.transient(parent)
        self.grab_set()

        self.create_widgets()
        self.load_packaging_lines()

    def create_widgets(self):
        """Create the dialog widgets"""
        # Title
        title_label = ttk.Label(
            self,
            text=f"All Packaging Lines for {self.duty_month}",
            font=("Helvetica", 12, "bold")
        )
        title_label.pack(pady=10)

        # Tree frame
        tree_frame = ttk.Frame(self)
        tree_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)

        # Scrollbars
        y_scroll = ttk.Scrollbar(tree_frame, orient=VERTICAL)
        y_scroll.pack(side=RIGHT, fill=Y)

        x_scroll = ttk.Scrollbar(tree_frame, orient=HORIZONTAL)
        x_scroll.pack(side=BOTTOM, fill=X)

        # Treeview
        columns = (
            'date', 'batch_id', 'container', 'qty', 'duty_vol',
            'abv', 'lpa', 'spr_cat', 'rate', 'duty'
        )

        self.tree = ttk.Treeview(
            tree_frame,
            columns=columns,
            show='headings',
            yscrollcommand=y_scroll.set,
            xscrollcommand=x_scroll.set
        )

        y_scroll.config(command=self.tree.yview)
        x_scroll.config(command=self.tree.xview)

        # Configure columns
        self.tree.heading('date', text='Date')
        self.tree.heading('batch_id', text='Batch ID')
        self.tree.heading('container', text='Container')
        self.tree.heading('qty', text='Qty')
        self.tree.heading('duty_vol', text='Duty Vol')
        self.tree.heading('abv', text='ABV')
        self.tree.heading('lpa', text='LPA')
        self.tree.heading('spr_cat', text='SPR Category')
        self.tree.heading('rate', text='Rate')
        self.tree.heading('duty', text='Duty')

        self.tree.column('date', width=100)
        self.tree.column('batch_id', width=120)
        self.tree.column('container', width=120)
        self.tree.column('qty', width=60)
        self.tree.column('duty_vol', width=100)
        self.tree.column('abv', width=60)
        self.tree.column('lpa', width=80)
        self.tree.column('spr_cat', width=150)
        self.tree.column('rate', width=80)
        self.tree.column('duty', width=100)

        self.tree.pack(fill=BOTH, expand=True)

        # Close button
        ttk.Button(
            self,
            text="Close",
            command=self.destroy,
            bootstyle=SECONDARY
        ).pack(pady=10)

    def load_packaging_lines(self):
        """Load all packaging lines for this duty month"""
        # Parse duty month (YYYY-MM format)
        year, month = self.duty_month.split('-')

        # Get parent's cache manager
        cache = self.master.cache
        cache.connect()
        cursor = cache.cursor

        # Query packaging lines from this month
        cursor.execute('''
            SELECT
                packaging_date,
                batch_id,
                container_type,
                quantity,
                total_duty_volume,
                batch_abv,
                pure_alcohol_litres,
                spr_category,
                effective_duty_rate,
                duty_payable
            FROM batch_packaging_lines
            WHERE strftime('%Y-%m', packaging_date) = ?
            ORDER BY packaging_date DESC, batch_id
        ''', (self.duty_month,))

        rows = cursor.fetchall()

        for row in rows:
            date, batch, container, qty, duty_vol, abv, lpa, spr_cat, rate, duty = row

            self.tree.insert('', END, values=(
                date,
                batch,
                container,
                qty,
                f"{duty_vol:.2f}L",
                f"{abv:.1f}%",
                f"{lpa:.2f}",
                spr_cat or "N/A",
                f"£{rate:.2f}" if rate else "£0.00",
                f"£{duty:.2f}" if duty else "£0.00"
            ))


class SpoiltBeerDialog(tk.Toplevel):
    """Dialog to show all spoilt beer for a duty month"""

    def __init__(self, parent, duty_month):
        super().__init__(parent)
        self.duty_month = duty_month

        self.title(f"Spoilt Beer - {duty_month}")
        self.geometry("1000x500")

        # Make modal
        self.transient(parent)
        self.grab_set()

        self.create_widgets()
        self.load_spoilt_beer()

    def create_widgets(self):
        """Create the dialog widgets"""
        # Title
        title_label = ttk.Label(
            self,
            text=f"Spoilt Beer Records for {self.duty_month}",
            font=("Helvetica", 12, "bold")
        )
        title_label.pack(pady=10)

        # Tree frame
        tree_frame = ttk.Frame(self)
        tree_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)

        # Scrollbars
        y_scroll = ttk.Scrollbar(tree_frame, orient=VERTICAL)
        y_scroll.pack(side=RIGHT, fill=Y)

        x_scroll = ttk.Scrollbar(tree_frame, orient=HORIZONTAL)
        x_scroll.pack(side=BOTTOM, fill=X)

        # Treeview
        columns = (
            'date', 'batch_id', 'container', 'qty', 'volume',
            'lpa', 'rate', 'reclaim', 'reason', 'status'
        )

        self.tree = ttk.Treeview(
            tree_frame,
            columns=columns,
            show='headings',
            yscrollcommand=y_scroll.set,
            xscrollcommand=x_scroll.set
        )

        y_scroll.config(command=self.tree.yview)
        x_scroll.config(command=self.tree.xview)

        # Configure columns
        self.tree.heading('date', text='Date Found')
        self.tree.heading('batch_id', text='Batch ID')
        self.tree.heading('container', text='Container')
        self.tree.heading('qty', text='Qty')
        self.tree.heading('volume', text='Volume')
        self.tree.heading('lpa', text='LPA')
        self.tree.heading('rate', text='Rate')
        self.tree.heading('reclaim', text='Reclaim')
        self.tree.heading('reason', text='Reason')
        self.tree.heading('status', text='Status')

        self.tree.column('date', width=100)
        self.tree.column('batch_id', width=120)
        self.tree.column('container', width=100)
        self.tree.column('qty', width=60)
        self.tree.column('volume', width=80)
        self.tree.column('lpa', width=80)
        self.tree.column('rate', width=80)
        self.tree.column('reclaim', width=100)
        self.tree.column('reason', width=120)
        self.tree.column('status', width=80)

        self.tree.pack(fill=BOTH, expand=True)

        # Close button
        ttk.Button(
            self,
            text="Close",
            command=self.destroy,
            bootstyle=SECONDARY
        ).pack(pady=10)

    def load_spoilt_beer(self):
        """Load all spoilt beer records for this duty month"""
        # Get parent's cache manager
        cache = self.master.cache
        cache.connect()
        cursor = cache.cursor

        cursor.execute('''
            SELECT
                date_discovered,
                batch_id,
                container_type,
                quantity,
                duty_paid_volume,
                pure_alcohol_litres,
                original_duty_rate,
                duty_to_reclaim,
                reason_category,
                status
            FROM spoilt_beer
            WHERE duty_month = ?
            ORDER BY date_discovered DESC
        ''', (self.duty_month,))

        rows = cursor.fetchall()

        for row in rows:
            date, batch, container, qty, vol, lpa, rate, reclaim, reason, status = row

            self.tree.insert('', END, values=(
                date,
                batch or "N/A",
                container,
                qty,
                f"{vol:.2f}L" if vol else "0.00L",
                f"{lpa:.2f}" if lpa else "0.00",
                f"£{rate:.2f}" if rate else "£0.00",
                f"£{reclaim:.2f}" if reclaim else "£0.00",
                reason or "N/A",
                status or "pending"
            ))


class AnnualSummaryDialog(tk.Toplevel):
    """Dialog to show annual summary of all returns"""

    def __init__(self, parent, cache_manager):
        super().__init__(parent)
        self.cache = cache_manager

        self.title("Annual Duty Summary")
        self.geometry("700x600")

        # Make modal
        self.transient(parent)
        self.grab_set()

        self.create_widgets()

    def create_widgets(self):
        """Create the dialog widgets"""
        # Title
        title_label = ttk.Label(
            self,
            text="Annual Duty Summary",
            font=("Helvetica", 14, "bold")
        )
        title_label.pack(pady=10)

        # Year selector
        year_frame = ttk.Frame(self)
        year_frame.pack(fill=X, padx=20, pady=10)

        ttk.Label(year_frame, text="Select Year:").pack(side=LEFT, padx=(0, 10))

        self.year_var = tk.StringVar()
        year_combo = ttk.Combobox(
            year_frame,
            textvariable=self.year_var,
            width=10,
            state='readonly'
        )
        year_combo.pack(side=LEFT)
        year_combo.bind('<<ComboboxSelected>>', lambda e: self.load_summary())

        # Populate years
        self.cache.connect()

        cursor = self.cache.cursor
        cursor.execute('''
            SELECT DISTINCT substr(duty_month, 1, 4) as year
            FROM duty_returns
            ORDER BY year DESC
        ''')
        years = [row[0] for row in cursor.fetchall()]
        year_combo['values'] = years
        if years:
            year_combo.current(0)

        # Summary text
        self.summary_text = tk.Text(
            self,
            wrap=tk.WORD,
            width=70,
            height=30,
            font=("Courier", 10)
        )
        self.summary_text.pack(fill=BOTH, expand=True, padx=20, pady=10)

        # Close button
        ttk.Button(
            self,
            text="Close",
            command=self.destroy,
            bootstyle=SECONDARY
        ).pack(pady=10)

        # Load initial data
        if years:
            self.load_summary()

    def load_summary(self):
        """Load annual summary for selected year"""
        year = self.year_var.get()
        if not year:
            return

        self.summary_text.delete('1.0', END)

        self.cache.connect()


        cursor = self.cache.cursor

        # Get all returns for this year
        cursor.execute('''
            SELECT
                duty_month,
                draught_low_litres, draught_low_lpa, draught_low_duty,
                draught_std_litres, draught_std_lpa, draught_std_duty,
                non_draught_litres, non_draught_lpa, non_draught_duty,
                high_abv_litres, high_abv_lpa, high_abv_duty,
                production_duty_total,
                spoilt_duty_reclaim,
                net_duty_payable
            FROM duty_returns
            WHERE duty_month LIKE ?
            ORDER BY duty_month
        ''', (f"{year}-%",))

        rows = cursor.fetchall()

        if not rows:
            self.summary_text.insert(END, f"No duty returns found for {year}")
            return

        # Build summary report
        report = f"ANNUAL DUTY SUMMARY - {year}\n"
        report += "=" * 70 + "\n\n"

        # Totals
        total_dl_litres = sum(r[1] or 0 for r in rows)
        total_dl_duty = sum(r[3] or 0 for r in rows)
        total_ds_litres = sum(r[4] or 0 for r in rows)
        total_ds_duty = sum(r[6] or 0 for r in rows)
        total_nd_litres = sum(r[7] or 0 for r in rows)
        total_nd_duty = sum(r[9] or 0 for r in rows)
        total_ha_litres = sum(r[10] or 0 for r in rows)
        total_ha_duty = sum(r[12] or 0 for r in rows)
        total_production_duty = sum(r[13] or 0 for r in rows)
        total_spoilt_reclaim = sum(r[14] or 0 for r in rows)
        total_net_payable = sum(r[15] or 0 for r in rows)

        report += "CATEGORY TOTALS:\n"
        report += "-" * 70 + "\n"
        report += f"Draught <3.5% ABV:        {total_dl_litres:>10.2f}L    Duty: £{total_dl_duty:>10.2f}\n"
        report += f"Draught 3.5-8.4% ABV:     {total_ds_litres:>10.2f}L    Duty: £{total_ds_duty:>10.2f}\n"
        report += f"Non-Draught 3.5-8.4% ABV: {total_nd_litres:>10.2f}L    Duty: £{total_nd_duty:>10.2f}\n"
        report += f"High ABV 8.5-22%:         {total_ha_litres:>10.2f}L    Duty: £{total_ha_duty:>10.2f}\n"
        report += "-" * 70 + "\n"
        report += f"TOTAL PRODUCTION:         {total_dl_litres + total_ds_litres + total_nd_litres + total_ha_litres:>10.2f}L    "
        report += f"Duty: £{total_production_duty:>10.2f}\n\n"

        report += f"Spoilt Beer Reclaim:      £{total_spoilt_reclaim:>10.2f}\n"
        report += f"NET DUTY PAYABLE:         £{total_net_payable:>10.2f}\n\n"

        # Monthly breakdown
        report += "\nMONTHLY BREAKDOWN:\n"
        report += "=" * 70 + "\n"

        for row in rows:
            month = row[0]
            prod_duty = row[13] or 0
            reclaim = row[14] or 0
            net = row[15] or 0

            report += f"{month}:  Production £{prod_duty:>8.2f}  |  Reclaim £{reclaim:>8.2f}  |  Net £{net:>8.2f}\n"

        self.summary_text.insert(END, report)

    # ================================================================
    # DATA LOADING METHODS FOR NEW TABS
    # ================================================================

    def load_sales_report(self):
        """Load sales data based on selected period"""
        period = self.sales_period.get()

        # Calculate date range
        today = datetime.now()
        if period == 'Last 7 Days':
            start_date = (today - timedelta(days=7)).strftime('%Y-%m-%d')
        elif period == 'Last 30 Days':
            start_date = (today - timedelta(days=30)).strftime('%Y-%m-%d')
        elif period == 'Last 90 Days':
            start_date = (today - timedelta(days=90)).strftime('%Y-%m-%d')
        elif period == 'Year to Date':
            start_date = f"{today.year}-01-01"
        else:  # All Time
            start_date = '2000-01-01'

        self.cache.connect()
        cursor = self.cache.cursor

        # Summary statistics
        cursor.execute('''
            SELECT
                COUNT(DISTINCT sale_id) as total_orders,
                SUM(quantity) as total_quantity,
                SUM(total_litres) as total_litres,
                SUM(line_total) as total_revenue
            FROM sales
            WHERE sale_date >= ?
                AND status IN ('reserved', 'delivered', 'invoiced')
        ''', (start_date,))

        summary = cursor.fetchone()
        total_orders = summary[0] or 0
        total_litres = summary[1] or 0.0
        total_revenue = summary[2] or 0.0
        avg_order = (total_revenue / total_orders) if total_orders > 0 else 0.0

        # Update summary cards
        self.sales_summary_cards['total_revenue'].config(text=f"£{total_revenue:,.2f}")
        self.sales_summary_cards['total_volume'].config(text=f"{total_litres:,.1f} L")
        self.sales_summary_cards['total_orders'].config(text=f"{total_orders:,}")
        self.sales_summary_cards['avg_order'].config(text=f"£{avg_order:,.2f}")

        # Sales by product
        self.sales_by_product_tree.delete(*self.sales_by_product_tree.get_children())

        cursor.execute('''
            SELECT
                beer_name,
                container_type,
                SUM(quantity) as qty,
                SUM(total_litres) as litres,
                SUM(line_total) as revenue
            FROM sales
            WHERE sale_date >= ?
                AND status IN ('reserved', 'delivered', 'invoiced')
            GROUP BY beer_name, container_type
            ORDER BY revenue DESC
        ''', (start_date,))

        products = {}
        for row in cursor.fetchall():
            beer_name = row[0] or 'Unknown'
            container = row[1] or 'Unknown'
            qty = row[2] or 0
            litres = row[3] or 0.0
            revenue = row[4] or 0.0
            avg_price_per_litre = (revenue / litres) if litres > 0 else 0.0

            if beer_name not in products:
                products[beer_name] = {
                    'total_qty': 0,
                    'total_litres': 0,
                    'total_revenue': 0,
                    'containers': []
                }

            products[beer_name]['total_qty'] += qty
            products[beer_name]['total_litres'] += litres
            products[beer_name]['total_revenue'] += revenue
            products[beer_name]['containers'].append((container, qty, litres, revenue, avg_price_per_litre))

        for beer_name, data in sorted(products.items(), key=lambda x: x[1]['total_revenue'], reverse=True):
            avg_price = (data['total_revenue'] / data['total_litres']) if data['total_litres'] > 0 else 0
            parent = self.sales_by_product_tree.insert('', 'end', text=beer_name, values=(
                'ALL',
                f"{data['total_qty']:,}",
                f"{data['total_litres']:,.1f}",
                f"£{data['total_revenue']:,.2f}",
                f"£{avg_price:.2f}/L"
            ))

            for container, qty, litres, revenue, price_per_l in data['containers']:
                self.sales_by_product_tree.insert(parent, 'end', text='', values=(
                    container,
                    f"{qty:,}",
                    f"{litres:,.1f}",
                    f"£{revenue:,.2f}",
                    f"£{price_per_l:.2f}/L"
                ))

        # Sales by customer
        self.sales_by_customer_tree.delete(*self.sales_by_customer_tree.get_children())

        cursor.execute('''
            SELECT
                c.customer_name,
                COUNT(DISTINCT s.sale_id) as orders,
                SUM(s.total_litres) as litres,
                SUM(s.line_total) as revenue
            FROM sales s
            JOIN customers c ON s.customer_id = c.customer_id
            WHERE s.sale_date >= ?
                AND s.status IN ('reserved', 'delivered', 'invoiced')
            GROUP BY c.customer_name
            ORDER BY revenue DESC
        ''', (start_date,))

        for row in cursor.fetchall():
            self.sales_by_customer_tree.insert('', 'end', values=(
                row[0],
                f"{row[1]:,}",
                f"{row[2]:,.1f} L",
                f"£{row[3]:,.2f}"
            ))

        self.cache.close()

    def load_inventory_report(self):
        """Load inventory data based on selected filter"""
        filter_mode = self.inventory_filter.get()

        self.cache.connect()
        cursor = self.cache.cursor

        # Clear existing data
        self.inventory_tree.delete(*self.inventory_tree.get_children())

        # Finished Goods (Products from sales table)
        if filter_mode in ['All Stock', 'Finished Goods Only']:
            # Get products with stock (from Products module logic)
            # This would join with actual product inventory if you track it
            # For now, show recent batches as available stock

            cursor.execute('''
                SELECT
                    r.recipe_name,
                    b.gyle_number,
                    b.actual_batch_size,
                    JULIANDAY('now') - JULIANDAY(b.packaged_date) as age_days,
                    b.measured_abv
                FROM batches b
                JOIN recipes r ON b.recipe_id = r.recipe_id
                WHERE b.status = 'Packaged'
                    AND b.packaged_date >= date('now', '-90 days')
                ORDER BY b.packaged_date DESC
            ''')

            total_stock_litres = 0
            total_value = 0
            product_count = 0

            for row in cursor.fetchall():
                recipe_name = row[0] or 'Unknown'
                gyle = row[1] or ''
                litres = row[2] or 0
                age_days = int(row[3] or 0)

                # Estimate value (you'd use actual pricing logic)
                est_value_per_litre = 2.50  # Placeholder
                est_value = litres * est_value_per_litre

                # Status based on age
                if age_days < 14:
                    status = '✅ Fresh'
                elif age_days < 30:
                    status = '⚠️ Aging'
                else:
                    status = '🔴 Old Stock'

                self.inventory_tree.insert('', 'end', values=(
                    f"{recipe_name} ({gyle})",
                    '1 batch',
                    f"{litres:.1f} L",
                    f"{age_days} days",
                    f"£{est_value:.2f}",
                    status
                ))

                total_stock_litres += litres
                total_value += est_value
                product_count += 1

        # Raw Materials
        if filter_mode in ['All Stock', 'Raw Materials Only']:
            cursor.execute('''
                SELECT
                    material_name,
                    current_stock,
                    unit,
                    cost_per_unit,
                    reorder_level
                FROM inventory_materials
                WHERE current_stock > 0
                ORDER BY material_type, material_name
            ''')

            for row in cursor.fetchall():
                name = row[0]
                stock = row[1] or 0
                unit = row[2] or 'kg'
                cost = row[3] or 0
                reorder = row[4] or 0

                value = stock * cost

                if reorder > 0 and stock <= reorder:
                    status = '🔴 Low Stock'
                elif reorder > 0 and stock <= reorder * 1.5:
                    status = '⚠️ Getting Low'
                else:
                    status = '✅ In Stock'

                self.inventory_tree.insert('', 'end', values=(
                    name,
                    f"{stock:.1f}",
                    unit,
                    '-',
                    f"£{value:.2f}",
                    status
                ))

        # Update summary cards (using finished goods data)
        self.inventory_summary_cards['total_stock'].config(text=f"{total_stock_litres:,.1f} L")
        self.inventory_summary_cards['stock_value'].config(text=f"£{total_value:,.2f}")
        self.inventory_summary_cards['products'].config(text=f"{product_count}")
        self.inventory_summary_cards['low_stock'].config(text="0")  # Would calculate from inventory

        self.cache.close()

    def load_production_report(self):
        """Load production data based on selected period"""
        period = self.production_period.get()

        # Calculate date range
        today = datetime.now()
        if period == 'Last 30 Days':
            start_date = (today - timedelta(days=30)).strftime('%Y-%m-%d')
        elif period == 'Last 90 Days':
            start_date = (today - timedelta(days=90)).strftime('%Y-%m-%d')
        elif period == 'Year to Date':
            start_date = f"{today.year}-01-01"
        else:  # All Time
            start_date = '2000-01-01'

        self.cache.connect()
        cursor = self.cache.cursor

        # Summary statistics
        cursor.execute('''
            SELECT
                COUNT(*) as total_batches,
                SUM(COALESCE(fermented_volume, actual_batch_size, 0)) as total_volume,
                SUM(packaged_volume) as packaged_volume,
                SUM(waste_volume) as waste_volume
            FROM batches
            WHERE packaged_date >= ?
                AND status = 'Packaged'
        ''', (start_date,))

        summary = cursor.fetchone()
        total_batches = summary[0] or 0
        total_volume = summary[1] or 0.0
        packaged_volume = summary[2] or 0.0
        waste_volume = summary[3] or 0.0

        avg_waste_pct = ((waste_volume / total_volume) * 100) if total_volume > 0 else 0

        # Update summary cards
        self.production_summary_cards['total_batches'].config(text=f"{total_batches:,}")
        self.production_summary_cards['total_volume'].config(text=f"{total_volume:,.1f} L")
        self.production_summary_cards['avg_efficiency'].config(text=f"{avg_waste_pct:.1f}%")
        self.production_summary_cards['packaged_volume'].config(text=f"{packaged_volume:,.1f} L")

        # Production by style
        self.production_by_style_tree.delete(*self.production_by_style_tree.get_children())

        cursor.execute('''
            SELECT
                r.style,
                COUNT(*) as batches,
                SUM(COALESCE(b.fermented_volume, b.actual_batch_size, 0)) as volume,
                AVG(b.measured_abv) as avg_abv
            FROM batches b
            JOIN recipes r ON b.recipe_id = r.recipe_id
            WHERE b.packaged_date >= ?
                AND b.status = 'Packaged'
            GROUP BY r.style
            ORDER BY volume DESC
        ''', (start_date,))

        for row in cursor.fetchall():
            self.production_by_style_tree.insert('', 'end', values=(
                row[0] or 'Unknown',
                f"{row[1]:,}",
                f"{row[2]:,.1f} L",
                f"{row[3]:.1f}%"
            ))

        # Production by brewer
        self.production_by_brewer_tree.delete(*self.production_by_brewer_tree.get_children())

        cursor.execute('''
            SELECT
                brewer_name,
                COUNT(*) as batches,
                SUM(COALESCE(fermented_volume, actual_batch_size, 0)) as volume
            FROM batches
            WHERE packaged_date >= ?
                AND status = 'Packaged'
                AND brewer_name IS NOT NULL
            GROUP BY brewer_name
            ORDER BY volume DESC
        ''', (start_date,))

        for row in cursor.fetchall():
            self.production_by_brewer_tree.insert('', 'end', values=(
                row[0],
                f"{row[1]:,}",
                f"{row[2]:,.1f} L"
            ))

        # Packaging breakdown
        self.production_packaging_tree.delete(*self.production_packaging_tree.get_children())

        cursor.execute('''
            SELECT
                container_type,
                SUM(quantity) as total_quantity,
                SUM(total_duty_volume) as total_litres
            FROM batch_packaging_lines
            WHERE packaging_date >= ?
            GROUP BY container_type
            ORDER BY total_litres DESC
        ''', (start_date,))

        for row in cursor.fetchall():
            self.production_packaging_tree.insert('', 'end', values=(
                row[0],
                f"{row[1]:,}",
                f"{row[2]:,.1f} L"
            ))

        self.cache.close()

    def load_financial_report(self):
        """Load financial data - P&L statement"""
        period = self.financial_period.get()

        # Calculate date range
        today = datetime.now()
        if period == 'Last 30 Days':
            start_date = (today - timedelta(days=30)).strftime('%Y-%m-%d')
        elif period == 'Last 90 Days':
            start_date = (today - timedelta(days=90)).strftime('%Y-%m-%d')
        elif period == 'Year to Date':
            start_date = f"{today.year}-01-01"
        else:  # Custom Range - for now use YTD
            start_date = f"{today.year}-01-01"

        self.cache.connect()
        cursor = self.cache.cursor

        # Revenue from sales
        cursor.execute('''
            SELECT SUM(line_total)
            FROM sales
            WHERE sale_date >= ?
                AND status IN ('delivered', 'invoiced')
        ''', (start_date,))

        revenue = cursor.fetchone()[0] or 0.0

        # Cost of Goods Sold (simplified - based on ingredient costs)
        # This is a placeholder - real COGS would track actual batch costs
        cogs = revenue * 0.25  # Estimate 25% ingredient cost

        # Duty paid (from duty returns)
        cursor.execute('''
            SELECT SUM(net_duty_payable)
            FROM duty_returns
            WHERE duty_month >= ?
        ''', (start_date[:7],))  # YYYY-MM format

        duty_paid = cursor.fetchone()[0] or 0.0

        # Gross profit
        gross_profit = revenue - cogs - duty_paid

        # Update summary cards
        self.financial_summary_cards['revenue'].config(text=f"£{revenue:,.2f}")
        self.financial_summary_cards['cogs'].config(text=f"£{cogs:,.2f}")
        self.financial_summary_cards['duty'].config(text=f"£{duty_paid:,.2f}")
        self.financial_summary_cards['profit'].config(text=f"£{gross_profit:,.2f}")

        # Build P&L tree
        self.financial_tree.delete(*self.financial_tree.get_children())

        # Revenue section
        revenue_node = self.financial_tree.insert('', 'end', text='REVENUE', values=(
            '', f"£{revenue:,.2f}", '100.0%'
        ), tags=('bold',))

        # Cost of Sales
        cogs_pct = (cogs / revenue * 100) if revenue > 0 else 0
        cogs_node = self.financial_tree.insert('', 'end', text='COST OF SALES', values=(
            '', f"£{cogs:,.2f}", f"{cogs_pct:.1f}%"
        ), tags=('bold',))

        self.financial_tree.insert(cogs_node, 'end', text='  Ingredients', values=(
            'Materials', f"£{cogs:,.2f}", f"{cogs_pct:.1f}%"
        ))

        # Gross Profit Before Duty
        gross_before_duty = revenue - cogs
        gross_before_duty_pct = (gross_before_duty / revenue * 100) if revenue > 0 else 0
        self.financial_tree.insert('', 'end', text='GROSS PROFIT (Before Duty)', values=(
            '', f"£{gross_before_duty:,.2f}", f"{gross_before_duty_pct:.1f}%"
        ), tags=('highlight',))

        # Duty
        duty_pct = (duty_paid / revenue * 100) if revenue > 0 else 0
        duty_node = self.financial_tree.insert('', 'end', text='HMRC DUTY', values=(
            '', f"£{duty_paid:,.2f}", f"{duty_pct:.1f}%"
        ), tags=('bold',))

        # Net Gross Profit
        profit_pct = (gross_profit / revenue * 100) if revenue > 0 else 0
        self.financial_tree.insert('', 'end', text='NET GROSS PROFIT', values=(
            '', f"£{gross_profit:,.2f}", f"{profit_pct:.1f}%"
        ), tags=('total',))

        # Configure tags for styling
        self.financial_tree.tag_configure('bold', font=('Helvetica', 10, 'bold'))
        self.financial_tree.tag_configure('highlight', background='#e8f4f8')
        self.financial_tree.tag_configure('total', font=('Helvetica', 11, 'bold'), background='#d4edda')

        self.cache.close()
