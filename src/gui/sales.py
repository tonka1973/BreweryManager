"""
Sales Module for Brewery Management System
Record cask sales with reserved/delivered workflow
"""

import tkinter as tk
from tkinter import messagebox
import ttkbootstrap as ttk
import uuid
from datetime import datetime
from ..utilities.date_utils import format_date_for_display, parse_display_date, get_today_display, get_today_db


class SalesModule(ttk.Frame):
    """Sales module for recording sales and deliveries"""

    def __init__(self, parent, cache_manager, current_user):
        super().__init__(parent)
        self.cache = cache_manager
        self.current_user = current_user

        self.create_widgets()
        self.load_sales()

    def create_widgets(self):
        """Create sales widgets"""
        toolbar = ttk.Frame(self)
        toolbar.pack(fill=tk.X, padx=20, pady=(0, 10))

        ttk.Button(toolbar, text="➕ New Sale",
                 bootstyle='success',
                 cursor='hand2',
                 command=self.add_sale).pack(side=tk.LEFT, padx=(0, 10))

        ttk.Button(toolbar, text="✏️ Edit",
                 bootstyle='info',
                 cursor='hand2',
                 command=self.edit_sale).pack(side=tk.LEFT, padx=(0, 10))

        ttk.Button(toolbar, text="✅ Mark Delivered",
                 bootstyle='warning',
                 cursor='hand2',
                 command=self.mark_delivered).pack(side=tk.LEFT, padx=(0, 10))

        ttk.Button(toolbar, text="🔄 Refresh",
                 bootstyle='secondary',
                 cursor='hand2',
                 command=self.load_sales).pack(side=tk.LEFT)

        # Filter
        ttk.Label(toolbar, text="Status:").pack(side=tk.RIGHT, padx=(0,5))
        self.filter_var = tk.StringVar(value='all')
        self.filter_var.trace('w', lambda *args: self.load_sales())
        ttk.Combobox(toolbar, textvariable=self.filter_var,
                    values=['all', 'reserved', 'delivered'],
                    width=12, state='readonly').pack(side=tk.RIGHT, padx=(10,0))

        # Sales list
        list_frame = ttk.Frame(self)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))

        vsb = ttk.Scrollbar(list_frame, orient="vertical")
        vsb.pack(side=tk.RIGHT, fill=tk.Y)

        columns = ('Date', 'Customer', 'Beer', 'Container', 'Qty', 'Total', 'Delivery', 'Status')
        self.tree = ttk.Treeview(list_frame, columns=columns, show='headings', yscrollcommand=vsb.set)

        for col in columns:
            self.tree.heading(col, text=col)

        self.tree.column('Date', width=100)
        self.tree.column('Customer', width=160)
        self.tree.column('Beer', width=140)
        self.tree.column('Container', width=100)
        self.tree.column('Qty', width=60)
        self.tree.column('Total', width=80)
        self.tree.column('Delivery', width=100)
        self.tree.column('Status', width=100)

        self.tree.pack(fill=tk.BOTH, expand=True)
        vsb.config(command=self.tree.yview)

    def load_sales(self):
        """Load sales from database"""
        for item in self.tree.get_children():
            self.tree.delete(item)

        status_filter = self.filter_var.get()
        where = None if status_filter == 'all' else f"status = '{status_filter}'"

        self.cache.connect()
        sales = self.cache.get_all_records('sales', where, 'sale_date DESC')
        self.cache.close()

        for sale in sales:
            # Get customer name
            customer_name = 'Unknown'
            if sale.get('customer_id'):
                self.cache.connect()
                customers = self.cache.get_all_records('customers', f"customer_id = '{sale['customer_id']}'")
                self.cache.close()
                if customers:
                    customer_name = customers[0]['customer_name']

            values = (
                format_date_for_display(sale.get('sale_date', '')),
                customer_name,
                sale.get('beer_name', 'N/A'),
                sale.get('container_type', 'N/A'),
                sale.get('quantity', 0),
                f"£{sale.get('line_total', 0):.2f}",
                format_date_for_display(sale.get('delivery_date')) if sale.get('delivery_date') else 'TBD',
                sale.get('status', '').capitalize()
            )

            status = sale.get('status', 'reserved')
            self.tree.insert('', 'end', values=values, tags=(f'status_{status}', sale['sale_id']))

        self.tree.tag_configure('status_reserved', background='#fff3e0')
        self.tree.tag_configure('status_delivered', background='#e8f5e9')

    def add_sale(self):
        """Add new sale"""
        dialog = SaleDialog(self, self.cache, self.current_user, mode='add')
        self.wait_window(dialog)
        self.load_sales()

    def edit_sale(self):
        """Edit selected sale"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a sale.")
            return

        tags = self.tree.item(selection[0], 'tags')
        sale_id = tags[1] if len(tags) > 1 else None

        self.cache.connect()
        sales = self.cache.get_all_records('sales', f"sale_id = '{sale_id}'")
        self.cache.close()

        if sales:
            dialog = SaleDialog(self, self.cache, self.current_user, mode='edit', sale=sales[0])
            self.wait_window(dialog)
            self.load_sales()

    def mark_delivered(self):
        """Mark sale as delivered"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a sale.")
            return

        tags = self.tree.item(selection[0], 'tags')
        sale_id = tags[1] if len(tags) > 1 else None

        self.cache.connect()
        sales = self.cache.get_all_records('sales', f"sale_id = '{sale_id}'")
        self.cache.close()

        if sales and sales[0]['status'] == 'reserved':
            result = messagebox.askyesno("Confirm", "Mark this sale as delivered?")
            if result:
                self.cache.connect()
                self.cache.update_record('sales', sale_id, {
                    'status': 'delivered',
                    'delivery_date': get_today_db(),
                    'sync_status': 'pending'
                }, 'sale_id')
                self.cache.close()

                messagebox.showinfo("Success", "Sale marked as delivered!")
                self.load_sales()
        else:
            messagebox.showinfo("Info", "Sale already delivered.")


class SaleDialog(tk.Toplevel):
    """Dialog for adding/editing sales"""

    def __init__(self, parent, cache_manager, current_user, mode='add', sale=None):
        super().__init__(parent)
        self.cache = cache_manager
        self.current_user = current_user
        self.mode = mode
        self.sale = sale

        self.title("New Sale" if mode == 'add' else "Edit Sale")
        self.geometry("600x650")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        self.create_widgets()
        if mode == 'edit' and sale:
            self.populate_fields()

    def create_widgets(self):
        """Create widgets"""
        frame = ttk.Frame(self, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)

        # Customer
        ttk.Label(frame, text="Customer *", font=('Arial', 10, 'bold')).grid(row=0, column=0, sticky='w', pady=(0,5))
        self.customer_var = tk.StringVar()
        self.cache.connect()
        customers = self.cache.get_all_records('customers', 'is_active = 1', 'customer_name')
        self.cache.close()
        self.customer_list = {c['customer_name']: c['customer_id'] for c in customers}
        ttk.Combobox(frame, textvariable=self.customer_var,
                    values=list(self.customer_list.keys()), width=37, state='readonly').grid(row=1, column=0, columnspan=2, sticky='ew', pady=(0,15))

        # Batch
        ttk.Label(frame, text="Batch (Gyle) *", font=('Arial', 10, 'bold')).grid(row=2, column=0, sticky='w', pady=(0,5))
        self.batch_var = tk.StringVar()
        self.cache.connect()
        batches = self.cache.get_all_records('batches', "status IN ('ready', 'packaged')", 'gyle_number DESC')
        self.cache.close()
        self.batch_list = {b['gyle_number']: b for b in batches}
        batch_combo = ttk.Combobox(frame, textvariable=self.batch_var,
                                   values=list(self.batch_list.keys()), width=37, state='readonly')
        batch_combo.grid(row=3, column=0, columnspan=2, sticky='ew', pady=(0,15))
        batch_combo.bind('<<ComboboxSelected>>', self.on_batch_selected)

        # Beer Name (auto-filled)
        ttk.Label(frame, text="Beer Name", font=('Arial', 10, 'bold')).grid(row=4, column=0, sticky='w', pady=(0,5))
        self.beer_entry = ttk.Entry(frame, font=('Arial', 10), width=40, state='readonly')
        self.beer_entry.grid(row=5, column=0, columnspan=2, sticky='ew', pady=(0,15))

        # Container Type
        ttk.Label(frame, text="Container Type *", font=('Arial', 10, 'bold')).grid(row=6, column=0, sticky='w', pady=(0,5))
        self.container_var = tk.StringVar(value='firkin')
        ttk.Combobox(frame, textvariable=self.container_var,
                    values=['pin', 'firkin', 'kilderkin', '30l_keg', '50l_keg', 'bottle_330ml', 'bottle_500ml'],
                    width=17, state='readonly').grid(row=7, column=0, sticky='w', pady=(0,15))

        # Quantity
        ttk.Label(frame, text="Quantity *", font=('Arial', 10, 'bold')).grid(row=6, column=1, sticky='w', pady=(0,5), padx=(20,0))
        self.qty_entry = ttk.Entry(frame, font=('Arial', 10), width=15)
        self.qty_entry.insert(0, "1")
        self.qty_entry.grid(row=7, column=1, sticky='w', pady=(0,15), padx=(20,0))

        # Unit Price
        ttk.Label(frame, text="Unit Price (£) *", font=('Arial', 10, 'bold')).grid(row=8, column=0, sticky='w', pady=(0,5))
        self.price_entry = ttk.Entry(frame, font=('Arial', 10), width=15)
        self.price_entry.insert(0, "65.00")
        self.price_entry.grid(row=9, column=0, sticky='w', pady=(0,15))

        # Sale Date
        ttk.Label(frame, text="Sale Date (DD/MM/YYYY)", font=('Arial', 10, 'bold')).grid(row=8, column=1, sticky='w', pady=(0,5), padx=(20,0))
        self.sale_date_entry = ttk.Entry(frame, font=('Arial', 10), width=15)
        self.sale_date_entry.insert(0, get_today_display())
        self.sale_date_entry.grid(row=9, column=1, sticky='w', pady=(0,15), padx=(20,0))

        # Delivery Date
        ttk.Label(frame, text="Delivery Date (DD/MM/YYYY)", font=('Arial', 10, 'bold')).grid(row=10, column=0, sticky='w', pady=(0,5))
        self.delivery_entry = ttk.Entry(frame, font=('Arial', 10), width=15)
        self.delivery_entry.grid(row=11, column=0, sticky='w', pady=(0,15))

        # Status
        ttk.Label(frame, text="Status", font=('Arial', 10, 'bold')).grid(row=10, column=1, sticky='w', pady=(0,5), padx=(20,0))
        self.status_var = tk.StringVar(value='reserved')
        ttk.Combobox(frame, textvariable=self.status_var,
                    values=['reserved', 'delivered'],
                    width=12, state='readonly').grid(row=11, column=1, sticky='w', pady=(0,15), padx=(20,0))

        # Notes
        ttk.Label(frame, text="Notes", font=('Arial', 10, 'bold')).grid(row=12, column=0, sticky='w', pady=(0,5))
        self.notes_text = tk.Text(frame, font=('Arial', 10), width=40, height=4)
        self.notes_text.grid(row=13, column=0, columnspan=2, sticky='ew', pady=(0,15))

        frame.grid_columnconfigure(0, weight=1)
        frame.grid_columnconfigure(1, weight=1)

        # Buttons
        button_frame = ttk.Frame(self, padding=(20, 0, 20, 20))
        button_frame.pack(fill=tk.X)

        ttk.Button(button_frame, text="Cancel", bootstyle='secondary',
                 command=self.destroy).pack(side=tk.RIGHT, padx=(10,0))
        ttk.Button(button_frame, text="Save Sale", bootstyle='success',
                 command=self.save).pack(side=tk.RIGHT)

    def on_batch_selected(self, event=None):
        """Auto-fill beer name when batch selected"""
        gyle = self.batch_var.get()
        if gyle in self.batch_list:
            batch = self.batch_list[gyle]
            recipe_id = batch.get('recipe_id')
            if recipe_id:
                self.cache.connect()
                recipes = self.cache.get_all_records('recipes', f"recipe_id = '{recipe_id}'")
                self.cache.close()
                if recipes:
                    self.beer_entry.config(state='normal')
                    self.beer_entry.delete(0, tk.END)
                    self.beer_entry.insert(0, recipes[0]['recipe_name'])
                    self.beer_entry.config(state='readonly')

    def populate_fields(self):
        """Populate fields with sale data"""
        # Find customer name
        if self.sale.get('customer_id'):
            self.cache.connect()
            customers = self.cache.get_all_records('customers', f"customer_id = '{self.sale['customer_id']}'")
            self.cache.close()
            if customers:
                self.customer_var.set(customers[0]['customer_name'])

        self.batch_var.set(self.sale.get('gyle_number', ''))
        self.beer_entry.config(state='normal')
        self.beer_entry.delete(0, tk.END)
        self.beer_entry.insert(0, self.sale.get('beer_name', ''))
        self.beer_entry.config(state='readonly')
        self.container_var.set(self.sale.get('container_type', 'firkin'))
        self.qty_entry.delete(0, tk.END)
        self.qty_entry.insert(0, str(self.sale.get('quantity', 1)))
        self.price_entry.delete(0, tk.END)
        self.price_entry.insert(0, str(self.sale.get('unit_price', 65)))
        self.sale_date_entry.delete(0, tk.END)
        self.sale_date_entry.insert(0, format_date_for_display(self.sale.get('sale_date', '')))
        self.delivery_entry.delete(0, tk.END)
        if self.sale.get('delivery_date'):
            self.delivery_entry.insert(0, format_date_for_display(self.sale['delivery_date']))
        self.status_var.set(self.sale.get('status', 'reserved'))
        if self.sale.get('notes'):
            self.notes_text.insert('1.0', self.sale['notes'])

    def save(self):
        """Save sale"""
        customer_name = self.customer_var.get()
        if not customer_name or customer_name not in self.customer_list:
            messagebox.showerror("Error", "Please select a customer.")
            return

        gyle = self.batch_var.get()
        if not gyle or gyle not in self.batch_list:
            messagebox.showerror("Error", "Please select a batch.")
            return

        try:
            qty = int(self.qty_entry.get())
            price = float(self.price_entry.get())
        except ValueError:
            messagebox.showerror("Error", "Invalid quantity or price.")
            return

        # Convert dates from display format to database format
        sale_date_db = parse_display_date(self.sale_date_entry.get())
        if not sale_date_db:
            messagebox.showerror("Error", "Invalid sale date format. Please use DD/MM/YYYY.")
            return

        delivery_date_db = None
        if self.delivery_entry.get().strip():
            delivery_date_db = parse_display_date(self.delivery_entry.get())
            if not delivery_date_db:
                messagebox.showerror("Error", "Invalid delivery date format. Please use DD/MM/YYYY.")
                return

        batch = self.batch_list[gyle]
        container_sizes = {'pin': 20.5, 'firkin': 40.9, 'kilderkin': 81.8,
                          '30l_keg': 30.0, '50l_keg': 50.0,
                          'bottle_330ml': 0.33, 'bottle_500ml': 0.50}
        container_size = container_sizes.get(self.container_var.get(), 40.9)

        data = {
            'customer_id': self.customer_list[customer_name],
            'batch_id': batch['batch_id'],
            'gyle_number': gyle,
            'beer_name': self.beer_entry.get(),
            'container_type': self.container_var.get(),
            'container_size': container_size,
            'quantity': qty,
            'total_litres': qty * container_size,
            'unit_price': price,
            'line_total': qty * price,
            'status': self.status_var.get(),
            'sale_date': sale_date_db,
            'reserved_date': sale_date_db,
            'delivery_date': delivery_date_db,
            'recorded_by': self.current_user.username,
            'notes': self.notes_text.get('1.0', tk.END).strip(),
            'sync_status': 'pending'
        }

        self.cache.connect()
        if self.mode == 'add':
            data['sale_id'] = str(uuid.uuid4())
            self.cache.insert_record('sales', data)
        else:
            self.cache.update_record('sales', self.sale['sale_id'], data, 'sale_id')
        self.cache.close()

        messagebox.showinfo("Success", "Sale saved!")
        self.destroy()
