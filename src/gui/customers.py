"""
Customers Module for Brewery Management System
CRM system for managing customer relationships
"""

import tkinter as tk
from tkinter import messagebox
import ttkbootstrap as ttk
import uuid
from datetime import datetime
from ..utilities.date_utils import get_today_db
from ..utilities.window_manager import get_window_manager, enable_mousewheel_scrolling, enable_treeview_keyboard_navigation, enable_canvas_scrolling


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
            dialog = CustomerDetailsDialog(self, customers[0], self.cache)
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

        canvas = tk.Canvas(self)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        frame = ttk.Frame(canvas)

        frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

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

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        enable_canvas_scrolling(canvas)

        # Buttons
        button_frame = ttk.Frame(self)
        button_frame.pack(fill=tk.X, padx=20, pady=10)

        ttk.Button(button_frame, text="Cancel", bootstyle="secondary",
                  command=self.destroy).pack(side=tk.RIGHT, padx=(10,0))
        ttk.Button(button_frame, text="Save Customer", bootstyle="success",
                  command=self.save).pack(side=tk.RIGHT)

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


class CustomerDetailsDialog(tk.Toplevel):
    """Dialog for viewing customer details"""

    def __init__(self, parent, customer, cache):
        super().__init__(parent)
        self.customer = customer
        self.cache = cache

        self.title(f"Customer: {customer.get('customer_name', 'Unknown')}")
        self.transient(parent)
        self.grab_set()

        # Use window manager for sizing if available
        wm = get_window_manager()
        if wm:
            wm.setup_dialog(self, 'customer_details_dialog', width_pct=0.4, height_pct=0.65,
                          add_grip=True, save_on_close=True, resizable=True)
        else:
            # Fallback to hardcoded size
            self.geometry("600x600")
            self.resizable(True, True)

        self.create_widgets()

    def create_widgets(self):
        """Create widgets"""
        frame = ttk.Frame(self, padding=(30, 20))
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text=self.customer.get('customer_name', 'Unknown'),
                 font=('Arial', 18, 'bold')).pack(anchor='w', pady=(0,20))

        info = f"""
Contact: {self.customer.get('contact_person', 'N/A')}
Phone: {self.customer.get('phone', 'N/A')}
Email: {self.customer.get('email', 'N/A')}

Delivery Address:
{self.customer.get('delivery_address', 'N/A')}

Type: {self.customer.get('customer_type', 'N/A').capitalize()}
Payment Terms: {self.customer.get('payment_terms', 'N/A')}
Credit Limit: £{self.customer.get('credit_limit', 0):.2f}

Preferred Delivery: {self.customer.get('preferred_delivery_day', 'N/A')} at {self.customer.get('preferred_delivery_time', 'N/A')}

Likes: {self.customer.get('likes', 'None specified')}
Dislikes: {self.customer.get('dislikes', 'None specified')}

Status: {'Active' if self.customer.get('is_active') else 'Inactive'}
        """

        ttk.Label(frame, text=info.strip(), font=('Arial', 10),
                 justify=tk.LEFT).pack(anchor='w', pady=(0,20))

        if self.customer.get('notes'):
            ttk.Label(frame, text="Notes:", font=('Arial', 11, 'bold')).pack(anchor='w', pady=(0,5))
            # Keep tk.Frame with specific background color for notes section
            notes_frame = tk.Frame(frame, bg='#f5f5f5', relief=tk.SOLID, borderwidth=1)
            notes_frame.pack(fill=tk.X)
            tk.Label(notes_frame, text=self.customer['notes'], font=('Arial', 10),
                    bg='#f5f5f5', justify=tk.LEFT, wraplength=500).pack(padx=10, pady=10, anchor='w')

        ttk.Button(self, text="Close", bootstyle="secondary",
                  command=self.destroy).pack(pady=(0,20))
