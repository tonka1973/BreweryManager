"""
Sales Module for Brewery Management System
Record cask sales with reserved/delivered workflow
"""

import tkinter as tk
from tkinter import messagebox
import ttkbootstrap as ttk
import uuid
from datetime import datetime
from ..utilities.date_utils import format_date_for_display, parse_display_date, get_today_display, get_today_db, get_now_db
from ..utilities.window_manager import get_window_manager, enable_mousewheel_scrolling, enable_treeview_keyboard_navigation
from .components import ScrollableFrame, DateEntry
from .invoicing import PaymentDialog


class SalesModule(ttk.Frame):
    """Sales module for recording sales and deliveries"""

    def __init__(self, parent, cache_manager, current_user, sync_callback=None):
        super().__init__(parent)
        self.cache = cache_manager
        self.current_user = current_user
        self.sync_callback = sync_callback

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

        ttk.Button(toolbar, text="💳 Payment",
                 bootstyle='primary',
                 cursor='hand2',
                 command=self.make_payment).pack(side=tk.LEFT, padx=(0, 10))

        ttk.Button(toolbar, text="🔄 Refresh",
                 bootstyle='secondary',
                 cursor='hand2',
                 command=self.load_sales).pack(side=tk.LEFT)

        # Remove old status filter as we now have specific view logic
        # But we could keep a search box potentially? For now, stick to the request: "Mirror Current Orders"

        # Sales list
        list_frame = ttk.Frame(self)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))

        vsb = ttk.Scrollbar(list_frame, orient="vertical")
        vsb.pack(side=tk.RIGHT, fill=tk.Y)

        # New Columns to match Customer View
        columns = ('Ordered Date', 'Customer', 'Delivery Date', 'Invoice Number', 'Delivered', 'Invoiced', 'Paid')
        self.tree = ttk.Treeview(list_frame, columns=columns, show='headings', yscrollcommand=vsb.set)

        self.tree.heading('Ordered Date', text='Ordered Date', anchor='w')
        self.tree.heading('Customer', text='Customer', anchor='w')
        self.tree.heading('Delivery Date', text='Delivery Date', anchor='w')
        self.tree.heading('Invoice Number', text='Invoice Number', anchor='w')
        self.tree.heading('Delivered', text='Delivered', anchor='w')
        self.tree.heading('Invoiced', text='Invoiced', anchor='w')
        self.tree.heading('Paid', text='Paid', anchor='w')

        self.tree.column('Ordered Date', width=90, anchor='w')
        self.tree.column('Customer', width=150, anchor='w')
        self.tree.column('Delivery Date', width=90, anchor='w')
        self.tree.column('Invoice Number', width=120, anchor='w')
        self.tree.column('Delivered', width=70, anchor='w')
        self.tree.column('Invoiced', width=70, anchor='w')
        self.tree.column('Paid', width=70, anchor='w')

        self.tree.pack(fill=tk.BOTH, expand=True)
        vsb.config(command=self.tree.yview)

        enable_mousewheel_scrolling(self.tree)
        enable_treeview_keyboard_navigation(self.tree)
        
        self.tree.bind("<Double-1>", self.on_sale_double_click)

    def load_sales(self):
        """Load sales from database and group into Orders"""
        for item in self.tree.get_children():
            self.tree.delete(item)

        self.cache.connect()
        
        # 1. Fetch Reference Data
        all_customers = self.cache.get_all_records('customers')
        customer_map = {c['customer_id']: c['customer_name'] for c in all_customers}
        
        all_invoices = self.cache.get_all_records('invoices')
        invoices_map = {inv['invoice_id']: inv for inv in all_invoices}

        # 2. Fetch All Sales
        sales = self.cache.get_all_records('sales', None, 'delivery_date DESC')
        
        self.cache.close()

        # 3. Group Sales into "Orders"
        # Key: (customer_id, sale_date_str, invoice_id_or_none)
        grouped_orders = {}
        
        for sale in sales:
            invoice_id = sale.get('invoice_id')
            cust_id = sale.get('customer_id')
            sale_date = sale.get('sale_date')
            
            # Normalize Invoice ID
            if not invoice_id or invoice_id in ['None', 'NULL', '']:
                invoice_id = None
                
            # Create Group Key
            if invoice_id:
                # If invoiced, group by Invoice ID (regardless of date, though usually same)
                key = (cust_id, 'INVOICED', invoice_id)
            else:
                # If not invoiced, group by Customer + Date
                key = (cust_id, sale_date, None)
                
            if key not in grouped_orders:
                grouped_orders[key] = {
                    'sales': [],
                    'total': 0.0,
                    'items_count': 0,
                    'representative': sale # Keep one sale for dates/status
                }
            
            grouped_orders[key]['sales'].append(sale)
            grouped_orders[key]['total'] += sale.get('line_total', 0)
            grouped_orders[key]['items_count'] += 1
            
            # If any item in the group is 'delivered', we might want to show that? 
            # Or if ALL are delivered?
            # Let's verify status consistency in loop or just take representative
            if sale.get('status') == 'delivered':
                grouped_orders[key]['representative']['status'] = 'delivered' # Promote delivered status

        # 4. Display Groups
        for key, group in grouped_orders.items():
            sale = group['representative']
            
            # Resolve Customer Name
            cust_name = customer_map.get(sale.get('customer_id'), 'Unknown')
            
            # Delivery Status
            del_status = sale.get('status', '').lower()
            
            # Invoice Status
            invoice_id = sale.get('invoice_id')
            inv_status = "Pending"
            
            is_invoiced = False
            is_paid = False
            
            if invoice_id and invoice_id in invoices_map:
                inv = invoices_map[invoice_id]
                inv_status = inv.get('invoice_number', 'Unknown')
                pay_status_raw = inv.get('payment_status', '')
                
                is_invoiced = True
                if pay_status_raw == 'paid':
                    is_paid = True
                    
            elif invoice_id: # Orphan
                 inv_status = "Error"

            # FILTERING LOGIC:
            # Exclude if: Delivered AND Invoiced AND Paid
            is_delivered = del_status == 'delivered'
            
            if is_delivered and is_invoiced and is_paid:
                continue # Skip completed
            
            # Display Values
            txt_inv_num = inv_status if is_invoiced else "Not Invoiced"
            # Optional: Show item count? We don't have a column for it, but could append to customer or invoice?
            # Let's keep columns distinct for now.
            
            values = (
                format_date_for_display(sale.get('sale_date', '')),
                f"{cust_name} ({group['items_count']} items)", # Added item count context
                format_date_for_display(sale.get('delivery_date')) if sale.get('delivery_date') else 'TBD',
                txt_inv_num,
                "Yes" if is_delivered else "No",
                "Yes" if is_invoiced else "No",
                "Yes" if is_paid else "No"
            )

            # Style tags + IDs for interaction
            style_tag = ''
            if del_status == 'reserved': style_tag = 'reserved'
            elif is_paid: style_tag = 'paid'
            elif is_invoiced and not is_paid: style_tag = 'unpaid'
            
            inv_id_tag = f"invoice_id:{invoice_id}" if invoice_id else "invoice_id:None"
            sale_id_tag = f"sale_id:{sale['sale_id']}"
            
            tags = (style_tag, sale_id_tag, inv_id_tag) if style_tag else (sale_id_tag, inv_id_tag)
            
            self.tree.insert('', 'end', values=values, tags=tags)

        # Configure tags for status colors
        self.tree.tag_configure('reserved', foreground='#f39c12') # Orange
        self.tree.tag_configure('paid', foreground='#27ae60')     # Green
        self.tree.tag_configure('unpaid', foreground='#c0392b')   # Red

    def add_sale(self):
        """Add new sale"""
        dialog = SaleDialog(self, self.cache, self.current_user, mode='add')
        self.wait_window(dialog)
        self.load_sales()
        if self.sync_callback: self.sync_callback()

    def edit_sale(self):
        """Edit selected order"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a sale to edit the order.")
            return

        tags = self.tree.item(selection[0], 'tags')
        sale_id = None
        invoice_id = None
        
        for tag in tags:
            if tag.startswith('sale_id:'):
                sale_id = tag.split(':')[1]
            elif tag.startswith('invoice_id:'):
                invoice_id = tag.split(':')[1]

        if not sale_id: return

        self.cache.connect()
        
        # Determine "Order" context
        related_sales = []
        if invoice_id and invoice_id != 'None' and invoice_id != 'NULL':
            # If invoiced, get all sales on this invoice
            related_sales = self.cache.get_all_records('sales', f"invoice_id = '{invoice_id}'")
        else:
            # If not invoiced, get the specific sale first to find context
            target_sale = self.cache.get_all_records('sales', f"sale_id = '{sale_id}'")
            if target_sale:
                s = target_sale[0]
                # Logic: An "Order" is same Customer + Same Date + Uninvoiced
                # This groups them so editing one shows all items for that "delivery/order"
                customer_id = s['customer_id']
                sale_date = s['sale_date']
                
                # Safety: Ensure we only pick up uninvoiced ones here to match logic
                related_sales = self.cache.get_all_records('sales', 
                    f"customer_id = '{customer_id}' AND sale_date = '{sale_date}' AND (invoice_id IS NULL OR invoice_id = '' OR invoice_id = 'None' OR invoice_id = 'NULL')")

        self.cache.close()

        if related_sales:
            # Pass the list of sales to the dialog
            dialog = SaleDialog(self, self.cache, self.current_user, mode='edit', sale=None, sales_list=related_sales)
            self.wait_window(dialog)
            self.load_sales()
            if self.sync_callback: self.sync_callback()
        else:
            messagebox.showerror("Error", "Could not load order details.")

    def mark_delivered(self):
        """Mark sale as delivered"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a sale.")
            return

        tags = self.tree.item(selection[0], 'tags')
        sale_id = None
        
        for tag in tags:
            if tag.startswith('sale_id:'):
                sale_id = tag.split(':')[1]
                break
                
        if not sale_id: return

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
                if self.sync_callback: self.sync_callback()
        else:
            messagebox.showinfo("Info", "Sale already delivered or valid sale not selected.")

    def make_payment(self):
        """Record payment for selected order"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select an order.")
            return

        tags = self.tree.item(selection[0], 'tags')
        invoice_id = None
        
        for tag in tags:
            if tag.startswith('invoice_id:'):
                invoice_id = tag.split(':')[1]
                break
        
        if not invoice_id or invoice_id == 'None' or invoice_id == 'NULL':
             messagebox.showwarning("Not Invoiced", "This order has not been invoiced yet.\nPlease create an invoice first.")
             return

        # Fetch invoice
        self.cache.connect()
        invoices = self.cache.get_all_records('invoices', f"invoice_id = '{invoice_id}'")
        self.cache.close()

        if invoices:
            try:
                # Check if fully paid
                if invoices[0].get('payment_status') == 'paid':
                     messagebox.showinfo("Info", "This invoice is already fully paid.")
                     return
                     
                dialog = PaymentDialog(self, self.cache, self.current_user, invoices[0])
                self.wait_window(dialog)
                self.load_sales()
            except Exception as e:
                messagebox.showerror("Error", f"Could not open payment dialog: {e}")

    def on_sale_double_click(self, event):
        """Handle double click on sale"""
        selection = self.tree.selection()
        if not selection: return

        tags = self.tree.item(selection[0], 'tags')
        sale_id = None
        invoice_id = None

        for tag in tags:
            if tag.startswith('sale_id:'):
                sale_id = tag.split(':')[1]
            elif tag.startswith('invoice_id:'):
                invoice_id = tag.split(':')[1]
        
        if invoice_id and invoice_id != 'None':
             self.open_invoice(invoice_id)
        elif sale_id:
             # Open Order Details (Proforma)
             from .order_view import OrderDetailsDialog
             dialog = OrderDetailsDialog(self, self.cache, self.current_user, sale_id=sale_id)
             self.wait_window(dialog)
             self.load_sales()

    def open_invoice(self, invoice_id):
        from .invoicing import InvoiceViewDialog
        self.cache.connect()
        invoices = self.cache.get_all_records('invoices', f"invoice_id = '{invoice_id}'")
        lines = self.cache.get_all_records('invoice_lines', f"invoice_id = '{invoice_id}'")
        self.cache.close()
        
        if invoices:
            dialog = InvoiceViewDialog(self, invoices[0], lines, self.cache)
            self.wait_window(dialog)
            self.load_sales()


class SaleDialog(tk.Toplevel):
    """Dialog for adding/editing sales (Order)"""

    def __init__(self, parent, cache_manager, current_user, mode='add', sale=None, customer_id=None, sales_list=None):
        super().__init__(parent)
        self.cache = cache_manager
        self.current_user = current_user
        print(f"DEBUG: SaleDialog initialized. Has create_header_section: {hasattr(self, 'create_header_section')}")
        self.mode = mode
        self.sale = sale # Kept for back-compat if needed, but sales_list preferred for edit
        self.sales_list = sales_list if sales_list else ([sale] if sale else [])
        self.initial_customer_id = customer_id
        
        self.added_items = [] # New items to add
        self.existing_items = [] # Items already in DB (for edit mode)
        self.deleted_ids = [] # IDs of existing items to delete
        
        self.added_items_map = {} # iid -> item_data
        self.existing_items_map = {} # iid -> sale_data
        
        self.customer_list = {}
        self.product_list = {}

        title = "New Order" if mode == 'add' else "Edit Order"
        self.title(title)
        self.transient(parent)
        self.grab_set()

        # Use window manager for sizing if available
        wm = get_window_manager()
        if wm:
            wm.setup_dialog(self, 'sale_dialog', width_pct=0.5, height_pct=0.8,
                          add_grip=True, save_on_close=True, resizable=True)
        else:
            # Fallback to hardcoded size
            self.geometry("700x700")
            self.resizable(True, True)

        self.create_widgets()
        if mode == 'edit':
            self.populate_fields()

    def create_header_section(self):
        """Create customer and date inputs"""
        frame = ttk.LabelFrame(self.main_frame, text="Sale Details", padding=15)
        frame.pack(fill=tk.X, pady=(0,10))
        
        frame.columnconfigure(1, weight=1)
        frame.columnconfigure(3, weight=1)

        # Customer
        ttk.Label(frame, text="Customer *", font=('Arial', 10, 'bold')).grid(row=0, column=0, sticky='w', pady=5)
        self.customer_var = tk.StringVar()
        self.cache.connect()
        customers = self.cache.get_all_records('customers', 'is_active = 1', 'customer_name')
        self.cache.close()
        self.customer_list = {c['customer_name']: c['customer_id'] for c in customers}
        self.customer_combo = ttk.Combobox(frame, textvariable=self.customer_var,
                    values=list(self.customer_list.keys()), width=30, state='readonly')
        self.customer_combo.grid(row=0, column=1, sticky='ew', padx=(5, 20), pady=5)
        self.customer_combo.bind('<<ComboboxSelected>>', self.on_customer_selected)

        # Pre-select customer if provided
        if self.mode == 'add' and self.initial_customer_id:
            for name, cid in self.customer_list.items():
                if cid == self.initial_customer_id:
                    self.customer_var.set(name)
                    self.on_customer_selected()
                    break

        # Status
        self.status_var = tk.StringVar(value='reserved')
        if self.mode == 'edit':
            ttk.Label(frame, text="Status", font=('Arial', 10, 'bold')).grid(row=0, column=2, sticky='w', pady=5)
            ttk.Combobox(frame, textvariable=self.status_var,
                        values=['reserved', 'delivered'],
                        width=15, state='readonly').grid(row=0, column=3, sticky='ew', padx=5, pady=5)

        # Sale Date
        ttk.Label(frame, text="Sale Date", font=('Arial', 10, 'bold')).grid(row=1, column=0, sticky='w', pady=5)
        self.sale_date_entry = DateEntry(frame, font=('Arial', 10), width=15)
        self.sale_date_entry.insert(0, get_today_display())
        self.sale_date_entry.grid(row=1, column=1, sticky='w', padx=5, pady=5)

        # Delivery Date
        ttk.Label(frame, text="Delivery Date", font=('Arial', 10, 'bold')).grid(row=1, column=2, sticky='w', pady=5)
        self.delivery_entry = DateEntry(frame, font=('Arial', 10), width=15)
        self.delivery_entry.grid(row=1, column=3, sticky='w', padx=5, pady=5)
        
        # Notes
        ttk.Label(frame, text="Notes", font=('Arial', 10, 'bold')).grid(row=2, column=0, sticky='nw', pady=5)
        self.notes_text = tk.Text(frame, font=('Arial', 10), width=40, height=3)
        self.notes_text.grid(row=2, column=1, columnspan=3, sticky='ew', padx=5, pady=5)

    def create_widgets(self):
        """Create widgets"""
        # Buttons (Top)
        button_frame = ttk.Frame(self, padding=(20, 10))
        button_frame.pack(fill=tk.X, side=tk.TOP)

        ttk.Button(button_frame, text="Cancel", bootstyle='secondary',
                  command=self.destroy).pack(side=tk.RIGHT, padx=(10,0))
        ttk.Button(button_frame, text="Save Order", bootstyle='success',
                  command=self.save).pack(side=tk.RIGHT)

        # Main scrollable container
        scroll_frame = ScrollableFrame(self)
        scroll_frame.pack(fill=tk.BOTH, expand=True)

        self.main_frame = ttk.Frame(scroll_frame.inner_frame, padding=20)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 1. Header Section (Customer, Dates, Status, Notes)
        self.create_header_section()
        
        ttk.Separator(self.main_frame, orient='horizontal').pack(fill=tk.X, pady=15)
        
        # 2. Items Section (Product Selection)
        self.create_items_section()



    def create_items_section(self):
        """Create product selection inputs"""
        frame = ttk.LabelFrame(self.main_frame, text="Order Items", padding=15)
        frame.pack(fill=tk.BOTH, expand=True)

        frame.columnconfigure(1, weight=1)

        # Product selection
        ttk.Label(frame, text="Product *", font=('Arial', 10, 'bold')).grid(row=0, column=0, sticky='w', pady=5)
        self.product_var = tk.StringVar()
        self.cache.connect()
        products = self.cache.get_all_records('products', "quantity_in_stock > 0", 'gyle_number DESC')
        self.cache.close()
        
        self.product_list = {}
        product_displays = []
        for p in products:
            display = f"Gyle {p['gyle_number']} - {p['product_name']} ({p['container_type']}) - {p['quantity_in_stock']} in stock"
            self.product_list[display] = p
            product_displays.append(display)

        self.product_combo = ttk.Combobox(frame, textvariable=self.product_var,
                                     values=product_displays, width=40, state='readonly')
        self.product_combo.grid(row=0, column=1, columnspan=3, sticky='ew', padx=5, pady=5)
        self.product_combo.bind('<<ComboboxSelected>>', self.on_product_selected)

        # Beer Name (Disabled, auto-filled)
        ttk.Label(frame, text="Beer Name", font=('Arial', 10, 'bold')).grid(row=1, column=0, sticky='w', pady=5)
        self.beer_entry = ttk.Entry(frame, font=('Arial', 10), state='readonly')
        self.beer_entry.grid(row=1, column=1, sticky='ew', padx=5, pady=5)
        
        # Container Type
        ttk.Label(frame, text="Container", font=('Arial', 10, 'bold')).grid(row=1, column=2, sticky='w', pady=5)
        self.container_var = tk.StringVar(value='firkin')
        ttk.Combobox(frame, textvariable=self.container_var,
                    values=['pin', 'firkin', 'kilderkin', '30l_keg', '50l_keg', 'bottle_330ml', 'bottle_500ml'],
                    width=15, state='readonly').grid(row=1, column=3, sticky='ew', padx=5, pady=5)

        # Qty and Price row
        ttk.Label(frame, text="Quantity *", font=('Arial', 10, 'bold')).grid(row=2, column=0, sticky='w', pady=5)
        self.qty_entry = ttk.Entry(frame, font=('Arial', 10), width=10)
        self.qty_entry.insert(0, "1")
        self.qty_entry.grid(row=2, column=1, sticky='w', padx=5, pady=5)

        ttk.Label(frame, text="Unit Price", font=('Arial', 10, 'bold')).grid(row=2, column=2, sticky='w', pady=5)
        self.price_entry = ttk.Entry(frame, font=('Arial', 10), width=10)
        self.price_entry.insert(0, "65.00")
        self.price_entry.grid(row=2, column=3, sticky='w', padx=5, pady=5)

        # Add Button - Always visible now
        ttk.Button(frame, text="Add Item", bootstyle='info-outline', command=self.add_item_to_list)\
            .grid(row=3, column=0, columnspan=4, pady=10)
        
        # Treeview for added items
        columns = ('Beer', 'Container', 'Qty', 'Price', 'Total', 'Status')
        self.items_tree = ttk.Treeview(frame, columns=columns, show='headings', height=8)
        for col in columns:
            self.items_tree.heading(col, text=col)
            self.items_tree.column(col, width=70)
        self.items_tree.column('Beer', width=150)
        self.items_tree.column('Status', width=60)
        
        self.items_tree.grid(row=4, column=0, columnspan=4, sticky='nsew', pady=5)
        
        # Delete item button
        ttk.Button(frame, text="Remove Selected", bootstyle='danger-outline',
                  command=self.remove_item_from_list).grid(row=5, column=0, columnspan=4, pady=5)
    
    def on_customer_selected(self, event=None):
        """Handle customer selection"""
        name = self.customer_var.get()
        if name in self.customer_list:
            # We could fetch address here if needed
            pass

    def on_product_selected(self, event=None):
        """Handle product selection"""
        name = self.product_var.get()
        if name in self.product_list:
            p = self.product_list[name]
            
            # Auto-fill Beer Name
            self.beer_entry.config(state='normal')
            self.beer_entry.delete(0, tk.END)
            self.beer_entry.insert(0, p['product_name'])
            self.beer_entry.config(state='readonly')
            
            # Update Price
            retail_price = p.get('retail_price', 0.0)
            self.price_entry.delete(0, tk.END)
            self.price_entry.insert(0, f"{retail_price:.2f}")
            
            # Update Container if possible
            if p['container_type'] in ['pin', 'firkin', 'kilderkin', '30l_keg', '50l_keg', 'bottle_330ml', 'bottle_500ml']:
                self.container_var.set(p['container_type'])

    # ... handlers ...

    def remove_item_from_list(self):
        """Remove selected item"""
        selected = self.items_tree.selection()
        if not selected: return
        
        iid = selected[0]
        
        # Remove from maps
        if iid in self.added_items_map:
             del self.added_items_map[iid]
        elif iid in self.existing_items_map:
             self.deleted_ids.append(self.existing_items_map[iid]['sale_id'])
             del self.existing_items_map[iid]
        
        # Remove from tree
        self.items_tree.delete(iid)

    def populate_fields(self):
        """Populate fields with order data"""
        if not self.sales_list: return
        
        # Use first sale for header info
        first_sale = self.sales_list[0]
        
        # Header
        if first_sale.get('customer_id'):
            self.cache.connect()
            customers = self.cache.get_all_records('customers', f"customer_id = '{first_sale['customer_id']}'")
            self.cache.close()
            if customers:
                self.customer_var.set(customers[0]['customer_name'])
                # Trigger callback safely? No, avoid triggering delivery date reset if we have one
                self.initial_customer_id = first_sale['customer_id']

        self.status_var.set(first_sale.get('status', 'reserved'))
        self.sale_date_entry.delete(0, tk.END)
        self.sale_date_entry.insert(0, format_date_for_display(first_sale.get('sale_date', '')))
        self.delivery_entry.delete(0, tk.END)
        if first_sale.get('delivery_date'):
            self.delivery_entry.insert(0, format_date_for_display(first_sale['delivery_date']))
        if first_sale.get('notes'):
            self.notes_text.insert('1.0', first_sale['notes'])

        # Populate Items Tree
        for sale in self.sales_list:
            values = (
                sale.get('beer_name', ''),
                sale.get('container_type', ''),
                sale.get('quantity', 0),
                f"£{sale.get('unit_price', 0):.2f}",
                f"£{sale.get('line_total', 0):.2f}",
                'Saved'
            )
            iid = self.items_tree.insert('', 'end', values=values, tags=(sale['sale_id'], 'existing'))
            self.existing_items_map[iid] = sale

    def add_item_to_list(self):
        """Add current inputs to items list"""
        # Validate inputs
        product_display = self.product_var.get()
        if not product_display or product_display not in self.product_list:
            messagebox.showerror("Error", "Please select a product.")
            return

        try:
            qty = int(self.qty_entry.get())
            price = float(self.price_entry.get())
        except ValueError:
            messagebox.showerror("Error", "Invalid quantity or price.")
            return
            
        if qty <= 0:
            messagebox.showerror("Error", "Quantity must be greater than 0.")
            return

        product = self.product_list[product_display]
        
        # Check stock (accounting for already added items AND existing items if same product)
        # Note: Existing items already deduct from stock. We only care about NEW additions relative to current stock?
        # Current stock logic in `create_sale` updates stock.
        # But `quantity_in_stock` in DB is AFTER existing sales.
        # So we just check against `quantity_in_stock` for the NEW quantity.
        # However, we must account for `added_items` in this session.
        
        current_session_added = sum(item['qty'] for item in self.added_items_map.values() if item['product']['product_id'] == product['product_id'])
        
        if qty + current_session_added > product.get('quantity_in_stock', 0):
             messagebox.showerror("Error", f"Insufficient stock! Only {product.get('quantity_in_stock', 0)} available.")
             return

        item = {
            'product': product,
            'beer_name': self.beer_entry.get(),
            'container_type': self.container_var.get(),
            'qty': qty,
            'price': price,
            'total': qty * price
        }
        
        # Update treeview
        iid = self.items_tree.insert('', 'end', values=(
            item['beer_name'],
            item['container_type'],
            item['qty'],
            f"£{item['price']:.2f}",
            f"£{item['total']:.2f}",
            'New'
        ), tags=('new',))
        
        self.added_items_map[iid] = item
        
        # Clear inputs for next item
        self.product_var.set('')
        self.beer_entry.config(state='normal')
        self.beer_entry.delete(0, tk.END)
        self.beer_entry.config(state='readonly')
        self.qty_entry.delete(0, tk.END)
        self.qty_entry.insert(0, "1")

    def remove_item_from_list(self):
        """Remove selected item"""
        selected = self.items_tree.selection()
        if not selected: return
        
        iid = selected[0]
        
        if iid in self.added_items_map:
             del self.added_items_map[iid]
        elif iid in self.existing_items_map:
             self.deleted_ids.append(self.existing_items_map[iid]['sale_id'])
             del self.existing_items_map[iid]
        
        self.items_tree.delete(iid)

    def save(self):
        """Save order changes"""
        # Validate Customer and Dates
        customer_name = self.customer_var.get()
        if not customer_name or customer_name not in self.customer_list:
            messagebox.showerror("Error", "Please select a customer.")
            return

        sale_date_db = parse_display_date(self.sale_date_entry.get())
        if not sale_date_db:
             messagebox.showerror("Error", "Invalid sale date format.")
             return

        delivery_date_db = None
        if self.delivery_entry.get().strip():
            delivery_date_db = parse_display_date(self.delivery_entry.get())
            if not delivery_date_db:
                messagebox.showerror("Error", "Invalid delivery date format.")
                return

        # Common Data
        self.cache.connect()
        customers = self.cache.get_all_records('customers', f"customer_id = '{self.customer_list[customer_name]}'")
        customer_address = customers[0].get('address', '') if customers else ''
        customer_id = self.customer_list[customer_name]
        
        container_sizes = {'pin': 20.5, 'firkin': 40.9, 'kilderkin': 81.8,
                          '30l_keg': 30.0, '50l_keg': 50.0,
                          'bottle_330ml': 0.33, 'bottle_500ml': 0.50}

        # 1. PROCESS DELETIONS
        for sale_id in self.deleted_ids:
            # Check if invoiced
            sale = self.cache.get_all_records('sales', f"sale_id = '{sale_id}'")
            if sale:
                invoice_id = sale[0].get('invoice_id')
                if invoice_id:
                     self.cache.delete_record('invoice_lines', f"sale_id = '{sale_id}'")
                
                # Restore stock? (Optional, skipping for safety unless explicitly requested)
                
                self.cache.delete_record('sales', f"sale_id = '{sale_id}'")
                self.cache.delete_record('product_sales', f"sale_id = '{sale_id}'")

        # 1.5 UPDATE EXISTING ITEMS (To keep them grouped with new items)
        # This fixes the bug where adding items (or changing date) splits the order
        if self.existing_items_map:
            # Prepare update data common to all items in this order
            update_data = {
                'customer_id': customer_id,
                'sale_date': sale_date_db, # Make sure they align
                'delivery_date': delivery_date_db,
                'status': self.status_var.get(),
                'notes': self.notes_text.get('1.0', tk.END).strip(),
                'last_modified': get_now_db(), # Assuming this helper exists or we specifically update modification time
                'sync_status': 'pending'
            }
            
            for iid, existing_sale in self.existing_items_map.items():
                sale_id = existing_sale['sale_id']
                # Update main sales record
                self.cache.update_record('sales', sale_id, update_data, 'sale_id')
                
                # Also update product_sales for consistency (dates/customer)
                # We need to find the product_sale_id or just update by sale_id?
                # product_sales table links by sale_id usually.
                ps_update = {
                    'customer_id': customer_id,
                    'date_sold': sale_date_db,
                    'date_delivered': delivery_date_db,
                    'delivery_address': customer_address,
                    'sync_status': 'pending'
                }
                # Update all product_sales linked to this sale_id
                # Note: update_record usually takes a primary key. 
                # We can use execute_query or get the ID first.
                # Let's get the product_sale_id first to be safe/clean.
                ps_records = self.cache.get_all_records('product_sales', f"sale_id = '{sale_id}'")
                for ps in ps_records:
                    self.cache.update_record('product_sales', ps['product_sale_id'], ps_update, 'product_sale_id')


        # 2. PROCESS NEW ITEMS
        for item in self.added_items_map.values():
             product = item['product']
             qty = item['qty']
             price = item['price']
             container_type = item['container_type']
             container_size = container_sizes.get(container_type, 40.9)
             
             sale_id = str(uuid.uuid4())
             
             # Inherit invoice ID from context if possible
             # If we are editing an order that is already invoiced, new items should probably go on same invoice?
             # Let's check if there's a common invoice_id in existing items
             invoice_id = None
             if self.sales_list:
                  invoice_id = self.sales_list[0].get('invoice_id')
             
             sale_data = {
                'sale_id': sale_id,
                'customer_id': customer_id,
                'batch_id': product.get('batch_id'),
                'gyle_number': product.get('gyle_number'),
                'beer_name': item['beer_name'],
                'container_type': container_type,
                'container_size': container_size,
                'quantity': qty,
                'total_litres': qty * container_size,
                'unit_price': price,
                'line_total': qty * price,
                'status': self.status_var.get(),
                'sale_date': sale_date_db,
                'reserved_date': sale_date_db,
                'delivery_date': delivery_date_db,
                'invoice_id': invoice_id, # Link to invoice if exists
                'recorded_by': self.current_user.username,
                'notes': self.notes_text.get('1.0', tk.END).strip(),
                'sync_status': 'pending'
            }
             
             product_sale_data = {
                'product_sale_id': str(uuid.uuid4()),
                'product_id': product['product_id'],
                'gyle_number': product['gyle_number'],
                'sale_id': sale_id,
                'customer_id': customer_id,
                'invoice_id': invoice_id,
                'quantity_sold': qty,
                'date_sold': sale_date_db,
                'date_delivered': delivery_date_db,
                'delivery_address': customer_address,
                'container_type': container_type,
                'created_date': get_today_db(),
                'sync_status': 'pending'
            }
             
             self.cache.insert_record('sales', sale_data)
             
             # Update stock
             new_qty_in_stock = product['quantity_in_stock'] - qty
             new_qty_sold = product.get('quantity_sold', 0) + qty
             new_status = 'Sold Out' if new_qty_in_stock == 0 else ('Partially Sold' if new_qty_sold > 0 else 'In Stock')
             
             self.cache.update_record('products', product['product_id'], {
                    'quantity_in_stock': new_qty_in_stock,
                    'quantity_sold': new_qty_sold,
                    'status': new_status,
                    'last_modified': get_today_db(),
                    'sync_status': 'pending'
                }, 'product_id')

             self.cache.insert_record('product_sales', product_sale_data)
             
             # If invoiced, add invoice line
             if invoice_id:
                  invoice_line_data = {
                        'line_id': str(uuid.uuid4()),
                        'invoice_id': invoice_id,
                        'sale_id': sale_id,
                        'description': f"{item['beer_name']} - {container_type}",
                        'quantity': qty,
                        'unit_price': price,
                        'line_total': qty * price,
                        'gyle_number': product.get('gyle_number'),
                        'sync_status': 'pending'
                  }
                  self.cache.insert_record('invoice_lines', invoice_line_data)

        # 3. UPDATE/VERIFY INVOICE TOTALS
        # If we touched an invocied order (added or removed), we must recalc totals
        affected_invoice_id = None
        if self.sales_list and self.sales_list[0].get('invoice_id'):
             affected_invoice_id = self.sales_list[0].get('invoice_id')
        
        if affected_invoice_id:
             # Recalculate
             all_lines = self.cache.get_all_records('invoice_lines', f"invoice_id = '{affected_invoice_id}'")
             subtotal = sum(l['line_total'] for l in all_lines)
             
             invoices = self.cache.get_all_records('invoices', f"invoice_id = '{affected_invoice_id}'")
             if invoices:
                 inv = invoices[0]
                 vat_rate = inv.get('vat_rate', 0.2)
                 vat_amount = subtotal * vat_rate
                 total = subtotal + vat_amount
                 
                 amount_paid = inv.get('amount_paid', 0)
                 amount_outstanding = total - amount_paid
                 # If negative outstanding (overpaid), we leave it or setting to 0? 
                 # Let's allow negative for credit situation or just plain math.
                 
                 new_payment_status = 'paid' if amount_outstanding <= 0.01 else 'partially_paid'
                 if amount_paid == 0: new_payment_status = 'pending'
                 
                 self.cache.update_record('invoices', affected_invoice_id, {
                      'subtotal': subtotal,
                      'vat_amount': vat_amount,
                      'total': total,
                      'amount_outstanding': amount_outstanding,
                      'payment_status': new_payment_status,
                      'sync_status': 'pending'
                 }, 'invoice_id')

        self.cache.close()
        messagebox.showinfo("Success", "Order updated successfully!")
        self.destroy()                    

