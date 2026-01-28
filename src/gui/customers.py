"""
Customers Module for Brewery Management System
CRM system for managing customer relationships
"""

import tkinter as tk
from tkinter import messagebox
import ttkbootstrap as ttk
import uuid
from datetime import datetime
from ..utilities.date_utils import get_today_db, format_date_for_display
from ..utilities.window_manager import get_window_manager, enable_mousewheel_scrolling, enable_treeview_keyboard_navigation, enable_canvas_scrolling
from .components import ScrollableFrame


class CustomersModule(ttk.Frame):
    """Customers CRM module"""

    def __init__(self, parent, cache_manager, current_user, sync_callback=None):
        super().__init__(parent)
        self.cache = cache_manager
        self.current_user = current_user
        self.sync_callback = sync_callback

        self.create_widgets()
        self.load_customers()

    def create_widgets(self):
        """Create customer widgets"""
        toolbar = ttk.Frame(self)
        toolbar.pack(fill=tk.X, padx=20, pady=(0, 10))

        ttk.Button(toolbar, text="➕ New Customer",
                  bootstyle="success",
                  command=self.add_customer).pack(side=tk.LEFT, padx=(0, 10))

        ttk.Button(toolbar, text="✏️ Edit",
                  bootstyle="primary",
                  command=self.edit_customer).pack(side=tk.LEFT, padx=(0, 10))

        ttk.Button(toolbar, text="👁️ View Details",
                  bootstyle="info",
                  command=self.view_customer).pack(side=tk.LEFT, padx=(0, 10))

        ttk.Button(toolbar, text="🗑️ Deactivate",
                  bootstyle="danger",
                  command=self.deactivate_customer).pack(side=tk.LEFT, padx=(0, 10))

        ttk.Button(toolbar, text="🔄 Refresh",
                  bootstyle="secondary",
                  command=self.load_customers).pack(side=tk.LEFT)

        # Search
        ttk.Label(toolbar, text="Search:").pack(side=tk.RIGHT, padx=(0,5))
        self.search_var = tk.StringVar()
        self.search_var.trace('w', lambda *args: self.load_customers())
        ttk.Entry(toolbar, textvariable=self.search_var, width=20).pack(side=tk.RIGHT)

        # Customer list
        list_frame = ttk.Frame(self)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))

        vsb = ttk.Scrollbar(list_frame, orient="vertical")
        vsb.pack(side=tk.RIGHT, fill=tk.Y)

        columns = ('Name', 'Contact', 'Phone', 'Email', 'Type', 'Terms', 'Status')
        self.tree = ttk.Treeview(list_frame, columns=columns, show='headings', yscrollcommand=vsb.set)

        for col in columns:
            self.tree.heading(col, text=col)

        self.tree.column('Name', width=180)
        self.tree.column('Contact', width=140)
        self.tree.column('Phone', width=120)
        self.tree.column('Email', width=180)
        self.tree.column('Type', width=80)
        self.tree.column('Terms', width=100)
        self.tree.column('Status', width=80)

        self.tree.pack(fill=tk.BOTH, expand=True)
        vsb.config(command=self.tree.yview)

        enable_mousewheel_scrolling(self.tree)
        enable_treeview_keyboard_navigation(self.tree)

        self.tree.bind('<Double-1>', lambda e: self.view_customer())

    def load_customers(self):
        """Load customers from database"""
        for item in self.tree.get_children():
            self.tree.delete(item)

        search = self.search_var.get().lower()

        self.cache.connect()
        customers = self.cache.get_all_records('customers', order_by='customer_name')
        self.cache.close()

        for cust in customers:
            name = cust.get('customer_name', '')
            if search and search not in name.lower():
                continue

            values = (
                name,
                cust.get('contact_person', 'N/A'),
                cust.get('phone', 'N/A'),
                cust.get('email', 'N/A'),
                cust.get('customer_type', 'N/A').capitalize(),
                cust.get('payment_terms', 'N/A'),
                'Active' if cust.get('is_active', 1) else 'Inactive'
            )

            tag = 'active' if cust.get('is_active', 1) else 'inactive'
            self.tree.insert('', 'end', values=values, tags=(tag, cust['customer_id']))

        self.tree.tag_configure('active', background='#e8f5e9')
        self.tree.tag_configure('inactive', background='#ffebee')

    def add_customer(self):
        """Add new customer"""
        dialog = CustomerDialog(self, self.cache, self.current_user, mode='add')
        self.wait_window(dialog)
        self.load_customers()
        if self.sync_callback: self.sync_callback()

    def edit_customer(self):
        """Edit selected customer"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a customer.")
            return

        tags = self.tree.item(selection[0], 'tags')
        customer_id = tags[1] if len(tags) > 1 else None

        self.cache.connect()
        customers = self.cache.get_all_records('customers', f"customer_id = '{customer_id}'")
        self.cache.close()

        if customers:
            dialog = CustomerDialog(self, self.cache, self.current_user, mode='edit', customer=customers[0])
            self.wait_window(dialog)
            self.load_customers()
            if self.sync_callback: self.sync_callback()

    def view_customer(self):
        """View customer details"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a customer.")
            return

        tags = self.tree.item(selection[0], 'tags')
        customer_id = tags[1] if len(tags) > 1 else None

        self.cache.connect()
        customers = self.cache.get_all_records('customers', f"customer_id = '{customer_id}'")
        self.cache.close()

        if customers:
            dialog = CustomerDashboard(self, customers[0], self.cache, self.current_user)
            self.wait_window(dialog)

    def deactivate_customer(self):
        """Deactivate customer"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a customer.")
            return

        result = messagebox.askyesno("Confirm", "Deactivate this customer?")
        if result:
            tags = self.tree.item(selection[0], 'tags')
            customer_id = tags[1] if len(tags) > 1 else None

            self.cache.connect()
            self.cache.update_record('customers', customer_id, {'is_active': 0, 'sync_status': 'pending'}, 'customer_id')
            self.cache.close()

            messagebox.showinfo("Success", "Customer deactivated.")
            messagebox.showinfo("Success", "Customer deactivated.")
            self.load_customers()
            if self.sync_callback: self.sync_callback()


class CustomerDialog(tk.Toplevel):
    """Dialog for adding/editing customers"""

    def __init__(self, parent, cache_manager, current_user, mode='add', customer=None):
        super().__init__(parent)
        self.cache = cache_manager
        self.current_user = current_user
        self.mode = mode
        self.customer = customer

        self.title("New Customer" if mode == 'add' else "Edit Customer")
        self.transient(parent)
        self.grab_set()

        # Use window manager for sizing if available
        wm = get_window_manager()
        if wm:
            wm.setup_dialog(self, 'customer_dialog', width_pct=0.45, height_pct=0.75,
                          add_grip=True, save_on_close=True, resizable=True)
        else:
            # Fallback to hardcoded size
            self.geometry("650x750")
            self.resizable(True, True)

        self.create_widgets()
        if mode == 'edit' and customer:
            self.populate_fields()

    def create_widgets(self):
        """Create widgets"""
        # Buttons (Top)
        button_frame = ttk.Frame(self)
        button_frame.pack(fill=tk.X, padx=20, pady=10, side=tk.TOP)

        ttk.Button(button_frame, text="Cancel", bootstyle="secondary",
                  command=self.destroy).pack(side=tk.RIGHT, padx=(10,0))
        ttk.Button(button_frame, text="Save Customer", bootstyle="success",
                  command=self.save).pack(side=tk.RIGHT)

        scroll_frame = ScrollableFrame(self)
        scroll_frame.pack(fill=tk.BOTH, expand=True)

        frame = ttk.Frame(scroll_frame.inner_frame)

        # Customer Name
        ttk.Label(frame, text="Customer Name *", font=('Arial', 10, 'bold')).grid(row=0, column=0, sticky='w', pady=(0,5), padx=(20,0))
        self.name_entry = ttk.Entry(frame, font=('Arial', 10), width=50)
        self.name_entry.grid(row=1, column=0, columnspan=2, sticky='ew', pady=(0,15), padx=(20,20))

        # Contact Person
        ttk.Label(frame, text="Contact Person *", font=('Arial', 10, 'bold')).grid(row=2, column=0, sticky='w', pady=(0,5), padx=(20,0))
        self.contact_entry = ttk.Entry(frame, font=('Arial', 10), width=24)
        self.contact_entry.grid(row=3, column=0, sticky='ew', pady=(0,15), padx=(20,0))

        # Phone
        ttk.Label(frame, text="Phone *", font=('Arial', 10, 'bold')).grid(row=2, column=1, sticky='w', pady=(0,5), padx=(20,0))
        self.phone_entry = ttk.Entry(frame, font=('Arial', 10), width=20)
        self.phone_entry.grid(row=3, column=1, sticky='ew', pady=(0,15), padx=(20,20))

        # Email
        ttk.Label(frame, text="Email", font=('Arial', 10, 'bold')).grid(row=4, column=0, sticky='w', pady=(0,5), padx=(20,0))
        self.email_entry = ttk.Entry(frame, font=('Arial', 10), width=50)
        self.email_entry.grid(row=5, column=0, columnspan=2, sticky='ew', pady=(0,15), padx=(20,20))

        # Delivery Address
        ttk.Label(frame, text="Delivery Address *", font=('Arial', 10, 'bold')).grid(row=6, column=0, sticky='w', pady=(0,5), padx=(20,0))
        self.delivery_text = tk.Text(frame, font=('Arial', 10), width=50, height=3)
        self.delivery_text.grid(row=7, column=0, columnspan=2, sticky='ew', pady=(0,15), padx=(20,20))

        # Billing Address
        ttk.Label(frame, text="Billing Address", font=('Arial', 10, 'bold')).grid(row=8, column=0, sticky='w', pady=(0,5), padx=(20,0))
        self.billing_text = tk.Text(frame, font=('Arial', 10), width=50, height=3)
        self.billing_text.grid(row=9, column=0, columnspan=2, sticky='ew', pady=(0,15), padx=(20,20))

        # Customer Type
        ttk.Label(frame, text="Type", font=('Arial', 10, 'bold')).grid(row=10, column=0, sticky='w', pady=(0,5), padx=(20,0))
        self.type_var = tk.StringVar(value='pub')
        ttk.Combobox(frame, textvariable=self.type_var,
                    values=['pub', 'restaurant', 'shop', 'event', 'other'],
                    width=21, state='readonly').grid(row=11, column=0, sticky='w', pady=(0,15), padx=(20,0))

        # Payment Terms
        ttk.Label(frame, text="Payment Terms", font=('Arial', 10, 'bold')).grid(row=10, column=1, sticky='w', pady=(0,5), padx=(20,0))
        self.terms_var = tk.StringVar(value='net_30')
        ttk.Combobox(frame, textvariable=self.terms_var,
                    values=['cash', 'net_7', 'net_14', 'net_30'],
                    width=17, state='readonly').grid(row=11, column=1, sticky='w', pady=(0,15), padx=(20,20))

        # Credit Limit
        ttk.Label(frame, text="Credit Limit (£)", font=('Arial', 10, 'bold')).grid(row=12, column=0, sticky='w', pady=(0,5), padx=(20,0))
        self.credit_entry = ttk.Entry(frame, font=('Arial', 10), width=15)
        self.credit_entry.insert(0, "1000.00")
        self.credit_entry.grid(row=13, column=0, sticky='w', pady=(0,15), padx=(20,0))

        # Delivery Area (Smart Scheduling)
        ttk.Label(frame, text="Delivery Area", font=('Arial', 10, 'bold')).grid(row=12, column=1, sticky='w', pady=(0,5), padx=(20,0))
        # We could use a combobox later if we load runs, but for now simple text matching
        self.area_entry = ttk.Entry(frame, font=('Arial', 10), width=20)
        self.area_entry.grid(row=13, column=1, sticky='w', pady=(0,15), padx=(20,20))

        # Delivery Day
        ttk.Label(frame, text="Preferred Delivery Day", font=('Arial', 10, 'bold')).grid(row=14, column=0, sticky='w', pady=(0,5), padx=(20,0))
        self.day_var = tk.StringVar()
        ttk.Combobox(frame, textvariable=self.day_var,
                    values=['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'],
                    width=21, state='readonly').grid(row=15, column=0, sticky='w', pady=(0,15), padx=(20,0))

        # Delivery Time
        ttk.Label(frame, text="Preferred Time", font=('Arial', 10, 'bold')).grid(row=14, column=1, sticky='w', pady=(0,5), padx=(20,0))
        self.time_entry = ttk.Entry(frame, font=('Arial', 10), width=15)
        self.time_entry.insert(0, "10:00")
        self.time_entry.grid(row=15, column=1, sticky='w', pady=(0,15), padx=(20,20))

        # Likes
        ttk.Label(frame, text="Likes (beer preferences)", font=('Arial', 10, 'bold')).grid(row=16, column=0, sticky='w', pady=(0,5), padx=(20,0))
        self.likes_entry = ttk.Entry(frame, font=('Arial', 10), width=50)
        self.likes_entry.grid(row=17, column=0, columnspan=2, sticky='ew', pady=(0,15), padx=(20,20))

        # Dislikes
        ttk.Label(frame, text="Dislikes", font=('Arial', 10, 'bold')).grid(row=18, column=0, sticky='w', pady=(0,5), padx=(20,0))
        self.dislikes_entry = ttk.Entry(frame, font=('Arial', 10), width=50)
        self.dislikes_entry.grid(row=19, column=0, columnspan=2, sticky='ew', pady=(0,15), padx=(20,20))

        # Notes
        ttk.Label(frame, text="Notes", font=('Arial', 10, 'bold')).grid(row=20, column=0, sticky='w', pady=(0,5), padx=(20,0))
        self.notes_text = tk.Text(frame, font=('Arial', 10), width=50, height=4)
        self.notes_text.grid(row=21, column=0, columnspan=2, sticky='ew', pady=(0,15), padx=(20,20))

        frame.grid_columnconfigure(0, weight=1)
        frame.grid_columnconfigure(1, weight=1)



    def populate_fields(self):
        """Populate fields with customer data"""
        self.name_entry.insert(0, self.customer.get('customer_name', ''))
        self.contact_entry.insert(0, self.customer.get('contact_person', ''))
        self.phone_entry.insert(0, self.customer.get('phone', ''))
        self.email_entry.insert(0, self.customer.get('email', ''))
        self.delivery_text.insert('1.0', self.customer.get('delivery_address', ''))
        self.billing_text.insert('1.0', self.customer.get('billing_address', ''))
        self.type_var.set(self.customer.get('customer_type', 'pub'))
        self.terms_var.set(self.customer.get('payment_terms', 'net_30'))
        self.credit_entry.delete(0, tk.END)
        self.credit_entry.insert(0, str(self.customer.get('credit_limit', '')))
        
        self.area_entry.delete(0, tk.END)
        if self.customer.get('delivery_area'):
            self.area_entry.insert(0, self.customer.get('delivery_area', ''))

        self.day_var.set(self.customer.get('preferred_delivery_day', ''))
        self.time_entry.delete(0, tk.END)
        self.time_entry.insert(0, self.customer.get('preferred_delivery_time', ''))
        self.likes_entry.insert(0, self.customer.get('likes', ''))
        self.dislikes_entry.insert(0, self.customer.get('dislikes', ''))
        self.notes_text.insert('1.0', self.customer.get('notes', ''))

    def save(self):
        """Save customer"""
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showerror("Error", "Customer name is required.")
            return

        try:
            credit = float(self.credit_entry.get() or 0)
        except ValueError:
            messagebox.showerror("Error", "Invalid credit limit.")
            return

        data = {
            'customer_name': name,
            'contact_person': self.contact_entry.get().strip(),
            'phone': self.phone_entry.get().strip(),
            'email': self.email_entry.get().strip(),
            'delivery_address': self.delivery_text.get('1.0', tk.END).strip(),
            'billing_address': self.billing_text.get('1.0', tk.END).strip(),
            'customer_type': self.type_var.get(),
            'payment_terms': self.terms_var.get(),
            'credit_limit': credit,
            'delivery_area': self.area_entry.get().strip(),
            'preferred_delivery_day': self.day_var.get(),
            'preferred_delivery_time': self.time_entry.get().strip(),
            'likes': self.likes_entry.get().strip(),
            'dislikes': self.dislikes_entry.get().strip(),
            'notes': self.notes_text.get('1.0', tk.END).strip(),
            'sync_status': 'pending'
        }

        self.cache.connect()
        if self.mode == 'add':
            data['customer_id'] = str(uuid.uuid4())
            data['is_active'] = 1
            data['created_date'] = get_today_db()
            self.cache.insert_record('customers', data)
        else:
            self.cache.update_record('customers', self.customer['customer_id'], data, 'customer_id')
        self.cache.close()

        messagebox.showinfo("Success", "Customer saved!")
        self.destroy()


class CustomerDashboard(tk.Toplevel):
    """Enhanced dashboard for viewing and managing a customer"""

    def __init__(self, parent, customer, cache, current_user):
        super().__init__(parent)
        self.customer = customer
        self.cache = cache
        self.current_user = current_user
        
        self.title(f"Dashboard: {customer.get('customer_name', 'Unknown')}")
        self.state('zoomed')  # Open maximized for dashboard feel
        
        self.create_widgets()
        self.load_dashboard_data()

    def create_widgets(self):
        """Create dashboard layout"""
        # Main container
        main_container = ttk.Frame(self, padding=20)
        main_container.pack(fill=tk.BOTH, expand=True)

        # --- Header Section ---
        header_frame = ttk.Frame(main_container)
        header_frame.pack(fill=tk.X, pady=(0, 20))

        # Title and Status
        title_frame = ttk.Frame(header_frame)
        title_frame.pack(side=tk.LEFT)

        ttk.Label(title_frame, 
                 text=self.customer.get('customer_name', 'Unknown'), 
                 font=('Arial', 24, 'bold')).pack(anchor='w')
        
        status = "Active" if self.customer.get('is_active', 1) else "Inactive"
        status_color = "success" if status == "Active" else "danger"
        ttk.Label(title_frame, text=status, bootstyle=f"{status_color}-inverse").pack(anchor='w', pady=(5,0))

        # Action Bar (Right side)
        action_frame = ttk.Frame(header_frame)
        action_frame.pack(side=tk.RIGHT)

        ttk.Button(action_frame, text="➕ Place New Order", 
                  bootstyle="success", 
                  command=self.place_order).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(action_frame, text="✏️ Edit Details", 
                  bootstyle="primary-outline", 
                  command=self.edit_customer).pack(side=tk.LEFT, padx=5)

        ttk.Button(action_frame, text="Current Statement", 
                  bootstyle="info-outline", 
                  state="disabled").pack(side=tk.LEFT, padx=5) # Placeholder
        
        ttk.Button(action_frame, text="Close", 
                  bootstyle="secondary", 
                  command=self.destroy).pack(side=tk.LEFT, padx=5)

        # --- Tabbed Content ---
        self.notebook = ttk.Notebook(main_container)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Create Tabs
        self.tab_overview = ttk.Frame(self.notebook, padding=15)
        self.tab_deliveries = ttk.Frame(self.notebook, padding=15)
        self.tab_financials = ttk.Frame(self.notebook, padding=15)

        self.notebook.add(self.tab_overview, text="Overview")
        self.notebook.add(self.tab_deliveries, text="Deliveries")
        self.notebook.add(self.tab_financials, text="Financials")

        # Build Overview Tab
        self.build_overview_tab()
        # Build Other tabs (placeholders for now)
        self.build_deliveries_tab()
        self.build_financials_tab()

    def build_overview_tab(self):
        """Build the Overview tab content"""
        # Top Stats Row
        stats_frame = ttk.Frame(self.tab_overview)
        stats_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.create_stat_card(stats_frame, "Total Outstanding", "£0.00", "danger").pack(side=tk.LEFT, padx=(0, 20), fill=tk.X, expand=True)
        self.create_stat_card(stats_frame, "Credit Available", "£0.00", "success").pack(side=tk.LEFT, padx=(0, 20), fill=tk.X, expand=True)
        self.create_stat_card(stats_frame, "Last Order", "Never", "info").pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Content Grid
        content_frame = ttk.Frame(self.tab_overview)
        content_frame.pack(fill=tk.BOTH, expand=True)
        content_frame.columnconfigure(0, weight=1)
        content_frame.columnconfigure(1, weight=1)

        # Left Column: Contact & Details
        details_frame = ttk.LabelFrame(content_frame, text="Contact Details", padding=15)
        details_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        
        # Helper to create label pairs
        def add_detail(parent, label, value):
            f = ttk.Frame(parent)
            f.pack(fill=tk.X, pady=2)
            ttk.Label(f, text=label, font=('Arial', 9, 'bold'), width=15).pack(side=tk.LEFT)
            ttk.Label(f, text=value, font=('Arial', 9)).pack(side=tk.LEFT, fill=tk.X, expand=True)

        add_detail(details_frame, "Contact Person:", self.customer.get('contact_person', 'N/A'))
        add_detail(details_frame, "Phone:", self.customer.get('phone', 'N/A'))
        add_detail(details_frame, "Email:", self.customer.get('email', 'N/A'))
        
        ttk.Separator(details_frame).pack(fill=tk.X, pady=10)
        
        ttk.Label(details_frame, text="Delivery Address:", font=('Arial', 9, 'bold')).pack(anchor='w')
        ttk.Label(details_frame, text=self.customer.get('delivery_address', 'N/A'), wraplength=300).pack(anchor='w', pady=(0, 10))

        ttk.Label(details_frame, text="Billing Address:", font=('Arial', 9, 'bold')).pack(anchor='w')
        ttk.Label(details_frame, text=self.customer.get('billing_address', 'N/A'), wraplength=300).pack(anchor='w')

        # Right Column: Preferences & Notes
        prefs_frame = ttk.Frame(content_frame)
        prefs_frame.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        
        # Payment Info
        payment_frame = ttk.LabelFrame(prefs_frame, text="Trading Terms", padding=15)
        payment_frame.pack(fill=tk.X, pady=(0, 20))
        add_detail(payment_frame, "Payment Terms:", self.customer.get('payment_terms', 'N/A'))
        add_detail(payment_frame, "Credit Limit:", f"£{self.customer.get('credit_limit', 0):.2f}")
        
        # Preferences
        beer_frame = ttk.LabelFrame(prefs_frame, text="Preferences", padding=15)
        beer_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(beer_frame, text="Likes:", font=('Arial', 9, 'bold')).pack(anchor='w')
        ttk.Label(beer_frame, text=self.customer.get('likes', 'None'), wraplength=300).pack(anchor='w', pady=(0, 10))
        
        ttk.Label(beer_frame, text="Dislikes:", font=('Arial', 9, 'bold')).pack(anchor='w')
        ttk.Label(beer_frame, text=self.customer.get('dislikes', 'None'), wraplength=300).pack(anchor='w')

        # Notes
        notes_frame = ttk.LabelFrame(prefs_frame, text="Notes", padding=15)
        notes_frame.pack(fill=tk.BOTH, expand=True)
        ttk.Label(notes_frame, text=self.customer.get('notes', ''), wraplength=300).pack(anchor='w')

    def create_stat_card(self, parent, title, value, color):
        """Create a styled statistic card"""
        card = ttk.Frame(parent, bootstyle=f"{color}-bg", padding=15)
        
        # Inner frame for white text
        ttk.Label(card, text=title, font=('Arial', 10), bootstyle=f"inverse-{color}").pack(anchor='w')
        label = ttk.Label(card, text=value, font=('Arial', 20, 'bold'), bootstyle=f"inverse-{color}")
        label.pack(anchor='w')
        
        # Store reference to update later
        setattr(self, f"stat_{title.lower().replace(' ', '_')}", label)
        
        return card

    def build_deliveries_tab(self):
        """Build Deliveries tab"""
        # Pending Deliveries
        pending_frame = ttk.LabelFrame(self.tab_deliveries, text="Pending / Reserved Orders", padding=10)
        pending_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        columns = ('Date', 'Status', 'Items', 'Total')
        self.tree_pending = ttk.Treeview(pending_frame, columns=columns, show='headings', height=5)
        for col in columns:
            self.tree_pending.heading(col, text=col)
            self.tree_pending.column(col, width=100)
        
        self.tree_pending.pack(fill=tk.BOTH, expand=True)
        enable_mousewheel_scrolling(self.tree_pending)

        # Delivery History
        history_frame = ttk.LabelFrame(self.tab_deliveries, text="Delivery History (Last 10)", padding=10)
        history_frame.pack(fill=tk.BOTH, expand=True)

        self.tree_history = ttk.Treeview(history_frame, columns=columns, show='headings', height=5)
        for col in columns:
            self.tree_history.heading(col, text=col)
            self.tree_history.column(col, width=100)
        
        self.tree_history.pack(fill=tk.BOTH, expand=True)
        enable_mousewheel_scrolling(self.tree_history)

    def build_financials_tab(self):
        """Build Financials tab"""
        # Outstanding Invoices
        inv_frame = ttk.LabelFrame(self.tab_financials, text="Outstanding Invoices", padding=10)
        inv_frame.pack(fill=tk.BOTH, expand=True)

        columns = ('Invoice #', 'Date', 'Due Date', 'Outstanding', 'Total', 'Status')
        self.tree_invoices = ttk.Treeview(inv_frame, columns=columns, show='headings')
        for col in columns:
            self.tree_invoices.heading(col, text=col)
            self.tree_invoices.column(col, width=100)
        
        self.tree_invoices.pack(fill=tk.BOTH, expand=True)
        enable_mousewheel_scrolling(self.tree_invoices)

    def load_dashboard_data(self):
        """Fetch data for all tabs"""
        customer_id = self.customer['customer_id']
        self.cache.connect()
        try:
            # --- Overview & Stats ---
            invoices = self.cache.get_all_records('invoices', f"customer_id = '{customer_id}' AND payment_status != 'paid'")
            total_outstanding = sum(inv.get('amount_outstanding', 0) for inv in invoices)
            
            sales_history = self.cache.get_all_records('sales', f"customer_id = '{customer_id}' AND status = 'delivered'", "delivery_date DESC")
            last_order = "Never"
            if sales_history:
                last_order = format_date_for_display(sales_history[0].get('delivery_date'))
            
            credit_limit = self.customer.get('credit_limit', 0)
            credit_available = credit_limit - total_outstanding
            
            # Update Stats
            if hasattr(self, 'stat_total_outstanding'):
                self.stat_total_outstanding.configure(text=f"£{total_outstanding:.2f}")
            
            if hasattr(self, 'stat_credit_available'):
                self.stat_credit_available.configure(text=f"£{credit_available:.2f}")
                if credit_available < 0:
                    self.stat_credit_available.configure(bootstyle="inverse-danger")
                else:
                    self.stat_credit_available.configure(bootstyle="inverse-success")
                    
            if hasattr(self, 'stat_last_order'):
                self.stat_last_order.configure(text=last_order)

            # --- Deliveries Tab ---
            # Pending
            pending_sales = self.cache.get_all_records('sales', f"customer_id = '{customer_id}' AND status = 'reserved'", "delivery_date ASC")
            
            if hasattr(self, 'tree_pending'):
                self.tree_pending.delete(*self.tree_pending.get_children())
                for sale in pending_sales:
                    values = (
                        format_date_for_display(sale.get('delivery_date')),
                        sale.get('status', '').title(),
                        f"{sale.get('quantity')} x {sale.get('beer_name')}",
                        f"£{sale.get('line_total', 0):.2f}"
                    )
                    self.tree_pending.insert('', 'end', values=values)

            # History
            if hasattr(self, 'tree_history'):
                self.tree_history.delete(*self.tree_history.get_children())
                for sale in sales_history[:10]: # Limit to 10
                    values = (
                        format_date_for_display(sale.get('delivery_date')),
                        sale.get('status', '').title(),
                        f"{sale.get('quantity')} x {sale.get('beer_name')}",
                        f"£{sale.get('line_total', 0):.2f}"
                    )
                    self.tree_history.insert('', 'end', values=values)

            # --- Financials Tab ---
            if hasattr(self, 'tree_invoices'):
                self.tree_invoices.delete(*self.tree_invoices.get_children())
                for inv in invoices:
                    values = (
                        inv.get('invoice_number'),
                        format_date_for_display(inv.get('invoice_date')),
                        format_date_for_display(inv.get('due_date')),
                        f"£{inv.get('amount_outstanding', 0):.2f}",
                        f"£{inv.get('total', 0):.2f}",
                        inv.get('payment_status', '').replace('_', ' ').title()
                    )
                    self.tree_invoices.insert('', 'end', values=values)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load dashboard data: {e}")
        finally:
            self.cache.close()

    def place_order(self):
        """Open Sales Dialog"""
        from .sales import SaleDialog  # Local import to avoid circular dependency
        dialog = SaleDialog(self, self.cache, self.current_user, mode='add')
        # Here we would ideally pre-select the customer, but the SaleDialog logic might need tweaking 
        # to accept a pre-selected customer_id. For now, it opens the dialog.
        self.wait_window(dialog)
        self.load_dashboard_data() # Refresh after sale

    def edit_customer(self):
        """Edit customer details"""
        # Close dashboard temporarily or refresh after
        dialog = CustomerDialog(self, self.cache, self.current_user, mode='edit', customer=self.customer)
        self.wait_window(dialog)
        # In a real app we'd reload the customer data from DB
        # self.customer = self.cache.get_customer(self.customer['customer_id'])
        # self.create_widgets() # Rebuild UI
        pass
