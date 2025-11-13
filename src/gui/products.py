"""
Products Module for Brewery Management System
Tracks finished goods ready for sale with gyle-based traceability
"""

import tkinter as tk
from tkinter import messagebox
import ttkbootstrap as ttk
import uuid
from datetime import datetime


class ProductsModule(ttk.Frame):
    """Products module for tracking finished goods and sales"""

    def __init__(self, parent, cache_manager, current_user):
        super().__init__(parent)
        self.cache = cache_manager
        self.current_user = current_user

        self.create_widgets()
        self.load_products()

    def create_widgets(self):
        """Create products widgets"""
        # Toolbar
        toolbar = ttk.Frame(self)
        toolbar.pack(fill=tk.X, padx=20, pady=(0, 10))

        ttk.Button(toolbar, text="➕ Add Product",
                  bootstyle="success",
                  cursor='hand2',
                  command=self.add_product).pack(side=tk.LEFT, padx=(0, 10))

        ttk.Button(toolbar, text="✏️ Edit Name",
                  bootstyle="info",
                  cursor='hand2',
                  command=self.edit_product_name).pack(side=tk.LEFT, padx=(0, 10))

        ttk.Button(toolbar, text="↩️  Process Return",
                  bootstyle="warning",
                  cursor='hand2',
                  command=self.process_return).pack(side=tk.LEFT, padx=(0, 10))

        ttk.Button(toolbar, text="📊 View Sales History",
                  bootstyle="secondary",
                  cursor='hand2',
                  command=self.view_sales_history).pack(side=tk.LEFT, padx=(0, 10))

        ttk.Button(toolbar, text="🔄 Refresh",
                  bootstyle="secondary",
                  cursor='hand2',
                  command=self.load_products).pack(side=tk.LEFT)

        # Products list
        list_frame = ttk.Frame(self, relief=tk.SOLID, borderwidth=1)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))

        vsb = ttk.Scrollbar(list_frame, orient="vertical")
        vsb.pack(side=tk.RIGHT, fill=tk.Y)

        columns = ('Gyle', 'Product Name', 'Style', 'ABV', 'Container',
                   'Qty Total', 'In Stock', 'Sold', 'Status', 'Date Packaged')
        self.tree = ttk.Treeview(list_frame, columns=columns, show='headings',
                                yscrollcommand=vsb.set)

        self.tree.heading('Gyle', text='Gyle')
        self.tree.heading('Product Name', text='Product Name')
        self.tree.heading('Style', text='Style')
        self.tree.heading('ABV', text='ABV %')
        self.tree.heading('Container', text='Container Type')
        self.tree.heading('Qty Total', text='Qty Total')
        self.tree.heading('In Stock', text='In Stock')
        self.tree.heading('Sold', text='Sold')
        self.tree.heading('Status', text='Status')
        self.tree.heading('Date Packaged', text='Date Packaged')

        self.tree.column('Gyle', width=80)
        self.tree.column('Product Name', width=150)
        self.tree.column('Style', width=120)
        self.tree.column('ABV', width=70)
        self.tree.column('Container', width=120)
        self.tree.column('Qty Total', width=80)
        self.tree.column('In Stock', width=80)
        self.tree.column('Sold', width=80)
        self.tree.column('Status', width=100)
        self.tree.column('Date Packaged', width=110)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb.config(command=self.tree.yview)

        # Bind double-click to view sales history
        self.tree.bind('<Double-Button-1>', lambda e: self.view_sales_history())

        # Status bar info
        info_frame = ttk.Frame(self)
        info_frame.pack(fill=tk.X, padx=20, pady=(0, 10))

        ttk.Label(info_frame,
                 text="💡 Tip: Double-click a product to view its sales history for recall purposes",
                 font=('Arial', 9, 'italic'),
                 foreground='#666').pack(anchor='w')

    def load_products(self):
        """Load all products from database"""
        for item in self.tree.get_children():
            self.tree.delete(item)

        self.cache.connect()
        products = self.cache.get_all_records('products', order_by='date_packaged DESC')
        self.cache.close()

        for product in products:
            values = (
                product.get('gyle_number', ''),
                product.get('product_name', ''),
                product.get('style', ''),
                f"{product.get('abv', 0):.1f}",
                product.get('container_type', ''),
                str(product.get('quantity_total', 0)),
                str(product.get('quantity_in_stock', 0)),
                str(product.get('quantity_sold', 0)),
                product.get('status', ''),
                self.format_date(product.get('date_packaged', ''))
            )

            # Tag based on status
            status = product.get('status', '')
            if status == 'Sold Out':
                tag = 'sold_out'
            elif status == 'Partially Sold':
                tag = 'partial'
            else:
                tag = 'in_stock'

            self.tree.insert('', 'end', values=values,
                           tags=(tag, product['product_id']))

        # Configure tags
        self.tree.tag_configure('sold_out', background='#ffebee')
        self.tree.tag_configure('partial', background='#fff3e0')
        self.tree.tag_configure('in_stock', background='#e8f5e9')

    def format_date(self, date_str):
        """Format date for display"""
        if not date_str:
            return ''
        try:
            dt = datetime.fromisoformat(date_str)
            return dt.strftime('%d/%m/%Y')
        except:
            return date_str

    def add_product(self):
        """Add new product manually (for special cases)"""
        dialog = AddProductDialog(self, self.cache, self.current_user)
        self.wait_window(dialog)
        self.load_products()

    def edit_product_name(self):
        """Edit product name (only if not locked)"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a product.")
            return

        tags = self.tree.item(selection[0], 'tags')
        product_id = tags[1] if len(tags) > 1 else None

        self.cache.connect()
        products = self.cache.get_all_records('products', f"product_id = '{product_id}'")
        self.cache.close()

        if not products:
            messagebox.showerror("Error", "Product not found.")
            return

        product = products[0]

        # Check if name is locked
        if product.get('is_name_locked', 0) == 1:
            messagebox.showwarning("Name Locked",
                "This product name cannot be edited because it has been sold.\n\n"
                "Product names are locked after the first sale for traceability.")
            return

        dialog = EditProductNameDialog(self, self.cache, product)
        self.wait_window(dialog)
        self.load_products()

    def process_return(self):
        """Process returned containers"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a product.")
            return

        tags = self.tree.item(selection[0], 'tags')
        product_id = tags[1] if len(tags) > 1 else None

        self.cache.connect()
        products = self.cache.get_all_records('products', f"product_id = '{product_id}'")
        self.cache.close()

        if not products:
            messagebox.showerror("Error", "Product not found.")
            return

        dialog = ProcessReturnDialog(self, self.cache, products[0])
        self.wait_window(dialog)
        self.load_products()

    def view_sales_history(self):
        """View sales history for selected product's gyle"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a product.")
            return

        tags = self.tree.item(selection[0], 'tags')
        product_id = tags[1] if len(tags) > 1 else None

        self.cache.connect()
        products = self.cache.get_all_records('products', f"product_id = '{product_id}'")
        self.cache.close()

        if not products:
            messagebox.showerror("Error", "Product not found.")
            return

        gyle_number = products[0].get('gyle_number')
        dialog = SalesHistoryDialog(self, self.cache, gyle_number, products[0])
        self.wait_window(dialog)


class AddProductDialog(tk.Toplevel):
    """Dialog for manually adding a product"""

    def __init__(self, parent, cache, current_user):
        super().__init__(parent)
        self.cache = cache
        self.current_user = current_user

        self.title("Add Product")
        self.geometry("500x600")
        self.transient(parent)
        self.grab_set()

        self.create_widgets()

    def create_widgets(self):
        """Create dialog widgets"""
        frame = ttk.Frame(self, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text="Add Product Manually",
                 font=('Arial', 14, 'bold')).pack(pady=(0, 20))

        # Form fields
        fields_frame = ttk.Frame(frame)
        fields_frame.pack(fill=tk.BOTH, expand=True)

        # Gyle Number
        ttk.Label(fields_frame, text="Gyle Number *", font=('Arial', 10, 'bold')).grid(
            row=0, column=0, sticky='w', pady=(0, 5))
        self.gyle_entry = ttk.Entry(fields_frame, font=('Arial', 10), width=30)
        self.gyle_entry.grid(row=1, column=0, sticky='ew', pady=(0, 15))

        # Product Name
        ttk.Label(fields_frame, text="Product Name *", font=('Arial', 10, 'bold')).grid(
            row=2, column=0, sticky='w', pady=(0, 5))
        self.name_entry = ttk.Entry(fields_frame, font=('Arial', 10), width=30)
        self.name_entry.grid(row=3, column=0, sticky='ew', pady=(0, 15))

        # Style
        ttk.Label(fields_frame, text="Style", font=('Arial', 10, 'bold')).grid(
            row=4, column=0, sticky='w', pady=(0, 5))
        self.style_entry = ttk.Entry(fields_frame, font=('Arial', 10), width=30)
        self.style_entry.grid(row=5, column=0, sticky='ew', pady=(0, 15))

        # Container Type
        ttk.Label(fields_frame, text="Container Type *", font=('Arial', 10, 'bold')).grid(
            row=6, column=0, sticky='w', pady=(0, 5))
        self.container_entry = ttk.Entry(fields_frame, font=('Arial', 10), width=30)
        self.container_entry.grid(row=7, column=0, sticky='ew', pady=(0, 15))

        # Quantity
        ttk.Label(fields_frame, text="Quantity *", font=('Arial', 10, 'bold')).grid(
            row=8, column=0, sticky='w', pady=(0, 5))
        self.qty_entry = ttk.Entry(fields_frame, font=('Arial', 10), width=30)
        self.qty_entry.grid(row=9, column=0, sticky='ew', pady=(0, 15))

        # ABV
        ttk.Label(fields_frame, text="ABV % *", font=('Arial', 10, 'bold')).grid(
            row=10, column=0, sticky='w', pady=(0, 5))
        self.abv_entry = ttk.Entry(fields_frame, font=('Arial', 10), width=30)
        self.abv_entry.grid(row=11, column=0, sticky='ew', pady=(0, 15))

        fields_frame.grid_columnconfigure(0, weight=1)

        # Buttons
        button_frame = ttk.Frame(self, padding=10)
        button_frame.pack(fill=tk.X, padx=20, pady=(0, 20))

        ttk.Button(button_frame, text="Cancel", bootstyle="secondary",
                  command=self.destroy).pack(side=tk.RIGHT, padx=(10, 0))
        ttk.Button(button_frame, text="Add Product", bootstyle="success",
                  command=self.save).pack(side=tk.RIGHT)

    def save(self):
        """Save new product"""
        gyle = self.gyle_entry.get().strip()
        name = self.name_entry.get().strip()
        style = self.style_entry.get().strip()
        container = self.container_entry.get().strip()
        qty_str = self.qty_entry.get().strip()
        abv_str = self.abv_entry.get().strip()

        if not all([gyle, name, container, qty_str, abv_str]):
            messagebox.showerror("Error", "Please fill in all required fields.")
            return

        try:
            qty = int(qty_str)
            abv = float(abv_str)
        except ValueError:
            messagebox.showerror("Error", "Invalid quantity or ABV value.")
            return

        # Create product record
        product_id = str(uuid.uuid4())
        now = datetime.now().isoformat()

        product_data = {
            'product_id': product_id,
            'gyle_number': gyle,
            'product_name': name,
            'style': style,
            'container_type': container,
            'quantity_total': qty,
            'quantity_in_stock': qty,
            'quantity_sold': 0,
            'abv': abv,
            'date_packaged': now,
            'date_in_stock': now,
            'status': 'In Stock',
            'is_name_locked': 0,
            'created_date': now,
            'created_by': self.current_user.username,
            'last_modified': now,
            'sync_status': 'pending'
        }

        self.cache.connect()
        self.cache.insert_record('products', product_data)
        self.cache.close()

        messagebox.showinfo("Success", "Product added successfully!")
        self.destroy()


class EditProductNameDialog(tk.Toplevel):
    """Dialog for editing product name"""

    def __init__(self, parent, cache, product):
        super().__init__(parent)
        self.cache = cache
        self.product = product

        self.title("Edit Product Name")
        self.geometry("400x250")
        self.transient(parent)
        self.grab_set()

        self.create_widgets()

    def create_widgets(self):
        """Create dialog widgets"""
        frame = ttk.Frame(self, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text=f"Edit Product Name",
                 font=('Arial', 14, 'bold')).pack(pady=(0, 10))

        ttk.Label(frame, text=f"Gyle: {self.product.get('gyle_number', '')}",
                 font=('Arial', 10)).pack(pady=(0, 20))

        ttk.Label(frame, text="Product Name *", font=('Arial', 10, 'bold')).pack(anchor='w', pady=(0, 5))
        self.name_entry = ttk.Entry(frame, font=('Arial', 11), width=40)
        self.name_entry.insert(0, self.product.get('product_name', ''))
        self.name_entry.pack(fill=tk.X, pady=(0, 20))

        # Buttons
        button_frame = ttk.Frame(frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))

        ttk.Button(button_frame, text="Cancel", bootstyle="secondary",
                  command=self.destroy).pack(side=tk.RIGHT, padx=(10, 0))
        ttk.Button(button_frame, text="Save", bootstyle="success",
                  command=self.save).pack(side=tk.RIGHT)

    def save(self):
        """Save updated name"""
        new_name = self.name_entry.get().strip()

        if not new_name:
            messagebox.showerror("Error", "Product name cannot be empty.")
            return

        self.cache.connect()
        self.cache.update_record('products', self.product['product_id'], {
            'product_name': new_name,
            'last_modified': datetime.now().isoformat(),
            'sync_status': 'pending'
        }, 'product_id')
        self.cache.close()

        messagebox.showinfo("Success", "Product name updated!")
        self.destroy()


class ProcessReturnDialog(tk.Toplevel):
    """Dialog for processing returned containers"""

    def __init__(self, parent, cache, product):
        super().__init__(parent)
        self.cache = cache
        self.product = product

        self.title("Process Return")
        self.geometry("450x350")
        self.transient(parent)
        self.grab_set()

        self.create_widgets()

    def create_widgets(self):
        """Create dialog widgets"""
        frame = ttk.Frame(self, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text="Process Container Return",
                 font=('Arial', 14, 'bold')).pack(pady=(0, 20))

        # Product info
        info_text = f"""Gyle: {self.product.get('gyle_number', '')}
Product: {self.product.get('product_name', '')}
Container: {self.product.get('container_type', '')}
Total Sold: {self.product.get('quantity_sold', 0)} units"""

        ttk.Label(frame, text=info_text, font=('Arial', 10),
                 justify=tk.LEFT).pack(anchor='w', pady=(0, 20))

        # Quantity to return
        ttk.Label(frame, text="Quantity Returned *", font=('Arial', 10, 'bold')).pack(anchor='w', pady=(0, 5))
        self.qty_entry = ttk.Entry(frame, font=('Arial', 11), width=20)
        self.qty_entry.pack(anchor='w', pady=(0, 20))

        ttk.Label(frame, text="This will add containers back to inventory.",
                 font=('Arial', 9, 'italic'),
                 foreground='#666').pack(anchor='w')

        # Buttons
        button_frame = ttk.Frame(frame)
        button_frame.pack(fill=tk.X, pady=(20, 0))

        ttk.Button(button_frame, text="Cancel", bootstyle="secondary",
                  command=self.destroy).pack(side=tk.RIGHT, padx=(10, 0))
        ttk.Button(button_frame, text="Process Return", bootstyle="success",
                  command=self.process).pack(side=tk.RIGHT)

    def process(self):
        """Process the return"""
        qty_str = self.qty_entry.get().strip()

        if not qty_str:
            messagebox.showerror("Error", "Please enter quantity returned.")
            return

        try:
            qty_returned = int(qty_str)
            if qty_returned <= 0:
                raise ValueError()
        except ValueError:
            messagebox.showerror("Error", "Invalid quantity.")
            return

        qty_sold = self.product.get('quantity_sold', 0)
        if qty_returned > qty_sold:
            messagebox.showerror("Error",
                f"Cannot return more than sold quantity ({qty_sold}).")
            return

        # Add back to container inventory
        container_type = self.product.get('container_type', '')

        self.cache.connect()

        # Find matching container type
        containers = self.cache.get_all_records('container_types',
            f"name = '{container_type}'")

        if containers:
            container = containers[0]
            new_qty = container.get('quantity_available', 0) + qty_returned
            self.cache.update_record('container_types', container['container_type_id'], {
                'quantity_available': new_qty,
                'last_modified': datetime.now().isoformat()
            }, 'container_type_id')

        self.cache.close()

        messagebox.showinfo("Success",
            f"{qty_returned} {container_type}(s) returned to inventory!")
        self.destroy()


class SalesHistoryDialog(tk.Toplevel):
    """Dialog showing sales history for a gyle (for recall purposes)"""

    def __init__(self, parent, cache, gyle_number, product):
        super().__init__(parent)
        self.cache = cache
        self.gyle_number = gyle_number
        self.product = product

        self.title(f"Sales History: Gyle {gyle_number}")
        self.geometry("900x600")
        self.transient(parent)
        self.grab_set()

        self.create_widgets()
        self.load_sales_history()

    def create_widgets(self):
        """Create dialog widgets"""
        frame = ttk.Frame(self, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)

        # Header
        header = ttk.Frame(frame)
        header.pack(fill=tk.X, pady=(0, 20))

        ttk.Label(header, text=f"Sales History: Gyle {self.gyle_number}",
                 font=('Arial', 14, 'bold')).pack(side=tk.LEFT)

        ttk.Button(header, text="📄 Export Recall List", bootstyle="warning",
                  command=self.export_recall).pack(side=tk.RIGHT)

        # Product info
        info_text = f"""{self.product.get('product_name', '')} - {self.product.get('style', '')} ({self.product.get('abv', 0):.1f}% ABV)
Packaged: {self.format_date(self.product.get('date_packaged', ''))}"""

        ttk.Label(frame, text=info_text, font=('Arial', 10),
                 justify=tk.LEFT).pack(anchor='w', pady=(0, 20))

        # Sales list
        list_frame = ttk.Frame(frame, relief=tk.SOLID, borderwidth=1)
        list_frame.pack(fill=tk.BOTH, expand=True)

        vsb = ttk.Scrollbar(list_frame, orient="vertical")
        vsb.pack(side=tk.RIGHT, fill=tk.Y)

        columns = ('Container', 'Qty', 'Customer', 'Date Sold', 'Invoice', 'Address')
        self.tree = ttk.Treeview(list_frame, columns=columns, show='headings',
                                yscrollcommand=vsb.set)

        self.tree.heading('Container', text='Container Type')
        self.tree.heading('Qty', text='Qty')
        self.tree.heading('Customer', text='Customer')
        self.tree.heading('Date Sold', text='Date Sold')
        self.tree.heading('Invoice', text='Invoice #')
        self.tree.heading('Address', text='Delivery Address')

        self.tree.column('Container', width=120)
        self.tree.column('Qty', width=60)
        self.tree.column('Customer', width=150)
        self.tree.column('Date Sold', width=100)
        self.tree.column('Invoice', width=100)
        self.tree.column('Address', width=250)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb.config(command=self.tree.yview)

        # Close button
        ttk.Button(self, text="Close", bootstyle="secondary",
                  command=self.destroy).pack(pady=20)

    def load_sales_history(self):
        """Load sales history for this gyle"""
        for item in self.tree.get_children():
            self.tree.delete(item)

        self.cache.connect()
        sales = self.cache.get_all_records('product_sales',
            f"gyle_number = '{self.gyle_number}'",
            order_by='date_sold DESC')

        if not sales:
            # Show message in tree
            self.tree.insert('', 'end', values=('No sales recorded yet', '', '', '', '', ''))
            self.cache.close()
            return

        for sale in sales:
            # Get customer name
            customer_name = 'Unknown'
            if sale.get('customer_id'):
                customers = self.cache.get_all_records('customers',
                    f"customer_id = '{sale['customer_id']}'")
                if customers:
                    customer_name = customers[0].get('customer_name', 'Unknown')

            values = (
                sale.get('container_type', ''),
                str(sale.get('quantity_sold', 0)),
                customer_name,
                self.format_date(sale.get('date_sold', '')),
                sale.get('invoice_id', 'N/A'),
                sale.get('delivery_address', 'N/A')
            )

            self.tree.insert('', 'end', values=values)

        self.cache.close()

    def format_date(self, date_str):
        """Format date for display"""
        if not date_str:
            return ''
        try:
            dt = datetime.fromisoformat(date_str)
            return dt.strftime('%d/%m/%Y')
        except:
            return date_str

    def export_recall(self):
        """Export recall list (placeholder - will implement CSV export later)"""
        messagebox.showinfo("Export Recall List",
            "Export functionality will be implemented in a future update.\n\n"
            "For now, you can manually record the information shown in this window.")
