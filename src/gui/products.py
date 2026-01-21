"""
Products Module for Brewery Management System
Tracks finished goods ready for sale with gyle-based traceability
"""

import tkinter as tk
from tkinter import messagebox
import ttkbootstrap as ttk
import uuid
from datetime import datetime
from ..utilities.window_manager import get_window_manager, enable_mousewheel_scrolling, enable_treeview_keyboard_navigation, enable_canvas_scrolling


class ProductsModule(ttk.Frame):
    """Products module for tracking finished goods and sales"""

    def __init__(self, parent, cache_manager, current_user, sync_callback=None):
        super().__init__(parent)
        self.cache = cache_manager
        self.current_user = current_user
        self.sync_callback = sync_callback

        self.create_widgets()
        self.load_products()

    def create_widgets(self):
        """Create products widgets with tabbed interface"""
        # Create notebook for tabs with better visibility
        self.notebook = ttk.Notebook(self, bootstyle="primary")
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Tab 1: Products
        self.products_tab = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.products_tab, text="  Products  ")

        # Tab 2: Spoilt Beer
        self.spoilt_tab = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.spoilt_tab, text="  Spoilt Beer  ")

        # Create products tab
        self.create_products_tab()

        # Create spoilt beer tab
        self.create_spoilt_beer_tab()

    def create_products_tab(self):
        """Create the products tab"""
        # Toolbar
        toolbar = ttk.Frame(self.products_tab)
        toolbar.pack(fill=tk.X, padx=20, pady=(20, 10))

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
        list_frame = ttk.Frame(self.products_tab, relief=tk.SOLID, borderwidth=1)
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

        enable_mousewheel_scrolling(self.tree)
        enable_treeview_keyboard_navigation(self.tree)

        # Bind double-click to view sales history
        self.tree.bind('<Double-Button-1>', lambda e: self.view_sales_history())

        # Status bar info
        info_frame = ttk.Frame(self.products_tab)
        info_frame.pack(fill=tk.X, padx=20, pady=(0, 10))

        ttk.Label(info_frame,
                 text="💡 Tip: Double-click a product to view its sales history for recall purposes",
                 font=('Arial', 9, 'italic'),
                 foreground='#666').pack(anchor='w')

    def create_spoilt_beer_tab(self):
        """Create the spoilt beer tracking tab"""
        # Control frame
        control_frame = ttk.Frame(self.spoilt_tab)
        control_frame.pack(fill=tk.X, padx=20, pady=(20, 10))

        # Filter by duty month
        ttk.Label(control_frame, text="Filter by Duty Month:").pack(side=tk.LEFT, padx=(0, 5))

        self.spoilt_month_filter = ttk.Combobox(
            control_frame,
            width=15,
            state='readonly'
        )
        self.spoilt_month_filter.pack(side=tk.LEFT, padx=(0, 20))
        self.spoilt_month_filter.bind('<<ComboboxSelected>>', lambda e: self.load_spoilt_beer())

        # Toolbar buttons
        ttk.Button(control_frame, text="➕ Record Spoilt Beer",
                  bootstyle="danger",
                  cursor='hand2',
                  command=self.add_spoilt_beer).pack(side=tk.LEFT, padx=(0, 10))

        ttk.Button(control_frame, text="✏️ Edit Record",
                  bootstyle="info",
                  cursor='hand2',
                  command=self.edit_spoilt_beer).pack(side=tk.LEFT, padx=(0, 10))

        ttk.Button(control_frame, text="🗑️ Delete Record",
                  bootstyle="danger",
                  cursor='hand2',
                  command=self.delete_spoilt_beer).pack(side=tk.LEFT, padx=(0, 10))

        ttk.Button(control_frame, text="🔄 Refresh",
                  bootstyle="secondary",
                  cursor='hand2',
                  command=self.load_spoilt_beer).pack(side=tk.LEFT)

        # Spoilt beer list
        list_frame = ttk.Frame(self.spoilt_tab, relief=tk.SOLID, borderwidth=1)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))

        vsb = ttk.Scrollbar(list_frame, orient="vertical")
        vsb.pack(side=tk.RIGHT, fill=tk.Y)

        hsb = ttk.Scrollbar(list_frame, orient="horizontal")
        hsb.pack(side=tk.BOTTOM, fill=tk.X)

        columns = ('Date', 'Duty Month', 'Batch ID', 'Container', 'Qty',
                   'Volume', 'ABV', 'LPA', 'Duty Rate', 'Reclaim', 'Reason', 'Status')
        self.spoilt_tree = ttk.Treeview(list_frame, columns=columns, show='headings',
                                yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.spoilt_tree.heading('Date', text='Date Found')
        self.spoilt_tree.heading('Duty Month', text='Duty Month')
        self.spoilt_tree.heading('Batch ID', text='Batch ID')
        self.spoilt_tree.heading('Container', text='Container')
        self.spoilt_tree.heading('Qty', text='Qty')
        self.spoilt_tree.heading('Volume', text='Volume')
        self.spoilt_tree.heading('ABV', text='ABV %')
        self.spoilt_tree.heading('LPA', text='LPA')
        self.spoilt_tree.heading('Duty Rate', text='Rate')
        self.spoilt_tree.heading('Reclaim', text='Duty Reclaim')
        self.spoilt_tree.heading('Reason', text='Reason')
        self.spoilt_tree.heading('Status', text='Status')

        self.spoilt_tree.column('Date', width=100)
        self.spoilt_tree.column('Duty Month', width=100)
        self.spoilt_tree.column('Batch ID', width=120)
        self.spoilt_tree.column('Container', width=120)
        self.spoilt_tree.column('Qty', width=60)
        self.spoilt_tree.column('Volume', width=80)
        self.spoilt_tree.column('ABV', width=70)
        self.spoilt_tree.column('LPA', width=80)
        self.spoilt_tree.column('Duty Rate', width=80)
        self.spoilt_tree.column('Reclaim', width=100)
        self.spoilt_tree.column('Reason', width=120)
        self.spoilt_tree.column('Status', width=100)

        self.spoilt_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb.config(command=self.spoilt_tree.yview)
        hsb.config(command=self.spoilt_tree.xview)

        enable_mousewheel_scrolling(self.spoilt_tree)
        enable_treeview_keyboard_navigation(self.spoilt_tree)

        # Bind double-click to edit
        self.spoilt_tree.bind('<Double-Button-1>', lambda e: self.edit_spoilt_beer())

        # Summary frame at bottom
        summary_frame = ttk.LabelFrame(self.spoilt_tab, text="Summary", padding=10)
        summary_frame.pack(fill=tk.X, padx=20, pady=(0, 10))

        self.spoilt_summary_label = ttk.Label(
            summary_frame,
            text="No spoilt beer records",
            font=("Helvetica", 10)
        )
        self.spoilt_summary_label.pack()

        # Populate month filter
        self.populate_spoilt_month_filter()
        self.load_spoilt_beer()

    def populate_spoilt_month_filter(self):
        """Populate the duty month filter for spoilt beer"""
        self.cache.connect()

        cursor = self.cache.cursor

        cursor.execute('''
            SELECT DISTINCT duty_month
            FROM spoilt_beer
            ORDER BY duty_month DESC
        ''')

        months = [row[0] for row in cursor.fetchall()]

        # Add "All Months" option
        months.insert(0, "All Months")

        self.spoilt_month_filter['values'] = months
        if months:
            self.spoilt_month_filter.current(0)

    def load_spoilt_beer(self):
        """Load spoilt beer records"""
        # Clear existing items
        for item in self.spoilt_tree.get_children():
            self.spoilt_tree.delete(item)

        self.cache.connect()


        cursor = self.cache.cursor

        # Build query with optional month filter
        month_filter = self.spoilt_month_filter.get()
        if month_filter and month_filter != "All Months":
            where_clause = f"WHERE duty_month = '{month_filter}'"
        else:
            where_clause = ""

        cursor.execute(f'''
            SELECT
                id,
                date_discovered,
                duty_month,
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
            {where_clause}
            ORDER BY date_discovered DESC
        ''')

        rows = cursor.fetchall()

        total_reclaim = 0.0
        total_volume = 0.0

        for row in rows:
            (id, date, month, batch, container, qty, vol, lpa,
             rate, reclaim, reason, status) = row

            # Calculate ABV from LPA and volume
            abv = (lpa / vol * 100) if vol and vol > 0 else 0

            # Format values
            vol_str = f"{vol:.2f}L" if vol else "0.00L"
            abv_str = f"{abv:.1f}%" if abv else "N/A"
            lpa_str = f"{lpa:.2f}" if lpa else "0.00"
            rate_str = f"£{rate:.2f}" if rate else "£0.00"
            reclaim_str = f"£{reclaim:.2f}" if reclaim else "£0.00"

            self.spoilt_tree.insert('', tk.END, values=(
                date,
                month,
                batch or "N/A",
                container,
                qty,
                vol_str,
                abv_str,
                lpa_str,
                rate_str,
                reclaim_str,
                reason or "Not specified",
                status or "pending"
            ), tags=(str(id),))

            # Sum totals
            total_reclaim += reclaim or 0
            total_volume += vol or 0

        # Update summary
        count = len(rows)
        summary_text = (
            f"Showing {count} record(s)  |  "
            f"Total Volume Spoilt: {total_volume:.2f}L  |  "
            f"Total Duty Reclaim: £{total_reclaim:.2f}"
        )
        self.spoilt_summary_label.config(text=summary_text)

    def add_spoilt_beer(self):
        """Add new spoilt beer record"""
        dialog = AddSpoiltBeerDialog(self, self.cache, self.current_user)
        self.wait_window(dialog)
        self.populate_spoilt_month_filter()
        self.load_spoilt_beer()
        if self.sync_callback: self.sync_callback()

    def edit_spoilt_beer(self):
        """Edit selected spoilt beer record"""
        selection = self.spoilt_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a spoilt beer record to edit.")
            return

        tags = self.spoilt_tree.item(selection[0], 'tags')
        record_id = int(tags[0]) if tags else None

        if not record_id:
            messagebox.showerror("Error", "Could not identify record.")
            return

        self.cache.connect()


        cursor = self.cache.cursor

        cursor.execute('SELECT * FROM spoilt_beer WHERE id = ?', (record_id,))
        row = cursor.fetchone()

        if not row:
            messagebox.showerror("Error", "Record not found.")
            return

        # Convert row to dict
        columns = [desc[0] for desc in cursor.description]
        record = dict(zip(columns, row))

        dialog = EditSpoiltBeerDialog(self, self.cache, record)
        self.wait_window(dialog)
        self.load_spoilt_beer()
        if self.sync_callback: self.sync_callback()

    def delete_spoilt_beer(self):
        """Delete selected spoilt beer record"""
        selection = self.spoilt_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a spoilt beer record to delete.")
            return

        tags = self.spoilt_tree.item(selection[0], 'tags')
        record_id = int(tags[0]) if tags else None

        if not record_id:
            messagebox.showerror("Error", "Could not identify record.")
            return

        # Confirm deletion
        if not messagebox.askyesno("Confirm Delete",
                                   "Are you sure you want to delete this spoilt beer record?\n\n"
                                   "This will affect duty calculations for the associated month."):
            return

        self.cache.connect()


        cursor = self.cache.cursor

        cursor.execute('DELETE FROM spoilt_beer WHERE id = ?', (record_id,))
        self.cache.connection.commit()

        messagebox.showinfo("Success", "Spoilt beer record deleted.")
        self.populate_spoilt_month_filter()
        self.load_spoilt_beer()
        if self.sync_callback: self.sync_callback()

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
        if self.sync_callback: self.sync_callback()

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
        if self.sync_callback: self.sync_callback()

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
        if self.sync_callback: self.sync_callback()

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
        self.transient(parent)
        self.grab_set()

        # Use window manager for sizing if available
        wm = get_window_manager()
        if wm:
            wm.setup_dialog(self, 'add_product_dialog', width_pct=0.35, height_pct=0.65,
                          add_grip=True, save_on_close=True, resizable=True)
        else:
            self.geometry("500x600")
            self.resizable(True, True)

        self.create_widgets()

    def create_widgets(self):
        """Create dialog widgets"""
        # Buttons (Top)
        button_frame = ttk.Frame(self, padding=10)
        button_frame.pack(fill=tk.X, side=tk.TOP)

        ttk.Button(button_frame, text="Cancel", bootstyle="secondary",
                  command=self.destroy).pack(side=tk.RIGHT, padx=(10, 0))
        ttk.Button(button_frame, text="Add Product", bootstyle="success",
                  command=self.save).pack(side=tk.RIGHT)

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
        self.transient(parent)
        self.grab_set()

        # Use window manager for sizing if available
        wm = get_window_manager()
        if wm:
            wm.setup_dialog(self, 'edit_product_name_dialog', width_pct=0.3, height_pct=0.3,
                          add_grip=True, save_on_close=True, resizable=True)
        else:
            self.geometry("400x250")
            self.resizable(True, True)

        self.create_widgets()

    def create_widgets(self):
        """Create dialog widgets"""
        # Buttons (Top)
        button_frame = ttk.Frame(self)
        button_frame.pack(fill=tk.X, side=tk.TOP, pady=(0, 10))

        ttk.Button(button_frame, text="Cancel", bootstyle="secondary",
                  command=self.destroy).pack(side=tk.RIGHT, padx=(10, 0))
        ttk.Button(button_frame, text="Save", bootstyle="success",
                  command=self.save).pack(side=tk.RIGHT)

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
        self.transient(parent)
        self.grab_set()

        # Use window manager for sizing if available
        wm = get_window_manager()
        if wm:
            wm.setup_dialog(self, 'process_return_dialog', width_pct=0.32, height_pct=0.4,
                          add_grip=True, save_on_close=True, resizable=True)
        else:
            self.geometry("450x350")
            self.resizable(True, True)

        self.create_widgets()

    def create_widgets(self):
        """Create dialog widgets"""
        # Buttons (Top)
        button_frame = ttk.Frame(self, padding=20)
        button_frame.pack(fill=tk.X, side=tk.TOP) # Using self instead of frame, and packing side=TOP

        ttk.Button(button_frame, text="Cancel", bootstyle="secondary",
                  command=self.destroy).pack(side=tk.RIGHT, padx=(10, 0))
        ttk.Button(button_frame, text="Process Return", bootstyle="success",
                  command=self.process).pack(side=tk.RIGHT)

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

        enable_mousewheel_scrolling(self.tree)
        enable_treeview_keyboard_navigation(self.tree)

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


class AddSpoiltBeerDialog(tk.Toplevel):
    """Dialog for recording spoilt beer"""

    def __init__(self, parent, cache, current_user):
        super().__init__(parent)
        self.cache = cache
        self.current_user = current_user

        self.title("Record Spoilt Beer")
        self.geometry("600x750")
        self.transient(parent)
        self.grab_set()

        self.create_widgets()

    def create_widgets(self):
        """Create dialog widgets"""
        from ttkbootstrap.constants import VERTICAL, Y
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

        frame = ttk.Frame(scrollable_frame, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text="Record Spoilt Beer",
                 font=('Arial', 14, 'bold')).pack(pady=(0, 20))

        # Date Discovered
        ttk.Label(frame, text="Date Discovered *", font=('Arial', 10, 'bold')).pack(anchor='w', pady=(0, 5))
        self.date_entry = ttk.Entry(frame, font=('Arial', 10), width=40)
        self.date_entry.insert(0, datetime.now().strftime('%Y-%m-%d'))
        self.date_entry.pack(fill=tk.X, pady=(0, 15))

        # Duty Month
        ttk.Label(frame, text="Duty Month (YYYY-MM) *", font=('Arial', 10, 'bold')).pack(anchor='w', pady=(0, 5))
        self.duty_month_entry = ttk.Entry(frame, font=('Arial', 10), width=40)
        # Default to current month
        self.duty_month_entry.insert(0, datetime.now().strftime('%Y-%m'))
        self.duty_month_entry.pack(fill=tk.X, pady=(0, 15))

        # Batch ID (optional)
        ttk.Label(frame, text="Batch ID (optional)", font=('Arial', 10, 'bold')).pack(anchor='w', pady=(0, 5))
        self.batch_entry = ttk.Entry(frame, font=('Arial', 10), width=40)
        self.batch_entry.pack(fill=tk.X, pady=(0, 15))

        # Gyle Number (optional)
        ttk.Label(frame, text="Gyle Number (optional)", font=('Arial', 10, 'bold')).pack(anchor='w', pady=(0, 5))
        self.gyle_entry = ttk.Entry(frame, font=('Arial', 10), width=40)
        self.gyle_entry.pack(fill=tk.X, pady=(0, 15))

        # Container Type
        ttk.Label(frame, text="Container Type *", font=('Arial', 10, 'bold')).pack(anchor='w', pady=(0, 5))
        self.container_combo = ttk.Combobox(frame, font=('Arial', 10), width=38, state='readonly')
        self.load_container_types()
        self.container_combo.pack(fill=tk.X, pady=(0, 15))

        # Quantity
        ttk.Label(frame, text="Quantity Spoilt *", font=('Arial', 10, 'bold')).pack(anchor='w', pady=(0, 5))
        self.qty_entry = ttk.Entry(frame, font=('Arial', 10), width=40)
        self.qty_entry.pack(fill=tk.X, pady=(0, 15))

        # ABV
        ttk.Label(frame, text="ABV % *", font=('Arial', 10, 'bold')).pack(anchor='w', pady=(0, 5))
        self.abv_entry = ttk.Entry(frame, font=('Arial', 10), width=40)
        self.abv_entry.pack(fill=tk.X, pady=(0, 15))

        # Reason Category
        ttk.Label(frame, text="Reason Category *", font=('Arial', 10, 'bold')).pack(anchor='w', pady=(0, 5))
        self.reason_combo = ttk.Combobox(frame, font=('Arial', 10), width=38, state='readonly')
        self.reason_combo['values'] = [
            'Infection/Contamination',
            'Off-Flavors/Quality Issues',
            'Package Defect/Leakage',
            'Condition Issues (Over/Under carbonated)',
            'Temperature Abuse',
            'Expired/Out of Date',
            'Other'
        ]
        self.reason_combo.pack(fill=tk.X, pady=(0, 15))

        # Reason Notes
        ttk.Label(frame, text="Additional Notes", font=('Arial', 10, 'bold')).pack(anchor='w', pady=(0, 5))
        self.notes_text = tk.Text(frame, font=('Arial', 10), width=40, height=4)
        self.notes_text.pack(fill=tk.X, pady=(0, 15))

        # Status
        ttk.Label(frame, text="Status", font=('Arial', 10, 'bold')).pack(anchor='w', pady=(0, 5))
        self.status_combo = ttk.Combobox(frame, font=('Arial', 10), width=38, state='readonly')
        self.status_combo['values'] = ['pending', 'approved', 'claimed']
        self.status_combo.current(0)
        self.status_combo.pack(fill=tk.X, pady=(0, 15))

        # Info label
        info_label = ttk.Label(frame,
            text="Duty will be automatically calculated based on ABV, container volume, and current rates.",
            font=('Arial', 9, 'italic'),
            foreground='#666',
            wraplength=500)
        info_label.pack(pady=(0, 20))

        # Buttons
        button_frame = ttk.Frame(frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))

        ttk.Button(button_frame, text="Cancel", bootstyle="secondary",
                  command=self.destroy).pack(side=tk.RIGHT, padx=(10, 0))
        ttk.Button(button_frame, text="Save Record", bootstyle="danger",
                  command=self.save).pack(side=tk.RIGHT)

        # Pack canvas and scrollbar
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=Y)

        enable_canvas_scrolling(canvas)

    def load_container_types(self):
        """Load container types from settings_containers"""
        self.cache.connect()

        cursor = self.cache.cursor

        cursor.execute('''
            SELECT name, duty_paid_volume, is_draught_eligible
            FROM settings_containers
            WHERE active = 1
            ORDER BY name
        ''')

        containers = cursor.fetchall()
        if containers:
            self.container_combo['values'] = [c[0] for c in containers]
            # Store full container data for later
            self.container_data = {c[0]: {'duty_volume': c[1], 'is_draught': c[2]} for c in containers}
        else:
            self.container_data = {}

    def save(self):
        """Save spoilt beer record"""
        # Validate inputs
        date_discovered = self.date_entry.get().strip()
        duty_month = self.duty_month_entry.get().strip()
        batch_id = self.batch_entry.get().strip() or None
        gyle_number = self.gyle_entry.get().strip() or None
        container_type = self.container_combo.get().strip()
        qty_str = self.qty_entry.get().strip()
        abv_str = self.abv_entry.get().strip()
        reason_category = self.reason_combo.get().strip() or None
        reason_notes = self.notes_text.get('1.0', tk.END).strip() or None
        status = self.status_combo.get().strip()

        if not all([date_discovered, duty_month, container_type, qty_str, abv_str]):
            messagebox.showerror("Error", "Please fill in all required fields.")
            return

        try:
            quantity = int(qty_str)
            abv = float(abv_str)
            if quantity <= 0 or abv <= 0:
                raise ValueError()
        except ValueError:
            messagebox.showerror("Error", "Invalid quantity or ABV value.")
            return

        # Validate duty month format
        try:
            datetime.strptime(duty_month, '%Y-%m')
        except ValueError:
            messagebox.showerror("Error", "Duty month must be in YYYY-MM format.")
            return

        # Get container details
        if container_type not in self.container_data:
            messagebox.showerror("Error", "Invalid container type.")
            return

        container_info = self.container_data[container_type]
        duty_volume_per_unit = container_info['duty_volume']
        is_draught = container_info['is_draught']

        # Calculate totals
        total_volume = duty_volume_per_unit * quantity
        pure_alcohol_litres = total_volume * (abv / 100)

        # Get current duty rates from settings
        self.cache.connect()

        cursor = self.cache.cursor

        cursor.execute('''
            SELECT
                spr_draught_low,
                spr_draught_standard,
                spr_non_draught_standard,
                rate_full_8_5_to_22
            FROM settings
            WHERE id = 1
        ''')

        settings_row = cursor.fetchone()
        if not settings_row:
            messagebox.showerror("Error", "Duty rates not configured. Please configure rates in Settings module.")
            return

        spr_draught_low, spr_draught_std, spr_non_draught, rate_full = settings_row

        # Determine SPR category and rate
        if abv >= 8.5:
            spr_category = "no_spr"
            duty_rate = rate_full
        elif abv < 3.5 and is_draught:
            spr_category = "draught_low"
            duty_rate = spr_draught_low
        elif 3.5 <= abv < 8.5 and is_draught:
            spr_category = "draught_standard"
            duty_rate = spr_draught_std
        elif 3.5 <= abv < 8.5 and not is_draught:
            spr_category = "non_draught_standard"
            duty_rate = spr_non_draught
        else:
            messagebox.showerror("Error", "Cannot determine duty category for this beer.")
            return

        # Calculate duty to reclaim
        duty_to_reclaim = pure_alcohol_litres * duty_rate

        # Create spoilt beer record
        now = datetime.now().isoformat()

        spoilt_data = {
            'batch_id': batch_id,
            'gyle_number': gyle_number,
            'date_discovered': date_discovered,
            'duty_month': duty_month,
            'status': status,
            'container_type': container_type,
            'quantity': quantity,
            'total_volume': total_volume,
            'duty_paid_volume': total_volume,
            'pure_alcohol_litres': pure_alcohol_litres,
            'spr_category': spr_category,
            'original_duty_rate': duty_rate,
            'duty_to_reclaim': duty_to_reclaim,
            'reason_category': reason_category,
            'reason_notes': reason_notes,
            'recorded_by': self.current_user.username,
            'recorded_at': now
        }

        # Insert into database
        columns = ', '.join(spoilt_data.keys())
        placeholders = ', '.join(['?' for _ in spoilt_data])
        values = tuple(spoilt_data.values())

        cursor.execute(f'''
            INSERT INTO spoilt_beer ({columns})
            VALUES ({placeholders})
        ''', values)

        self.cache.connection.commit()

        messagebox.showinfo("Success",
            f"Spoilt beer recorded successfully!\n\n"
            f"Volume: {total_volume:.2f}L\n"
            f"Pure Alcohol: {pure_alcohol_litres:.2f} LPA\n"
            f"Duty to Reclaim: £{duty_to_reclaim:.2f}")

        self.destroy()


class EditSpoiltBeerDialog(tk.Toplevel):
    """Dialog for editing spoilt beer record"""

    def __init__(self, parent, cache, record):
        super().__init__(parent)
        self.cache = cache
        self.record = record

        self.title("Edit Spoilt Beer Record")
        self.geometry("600x750")
        self.transient(parent)
        self.grab_set()

        self.create_widgets()

    def create_widgets(self):
        """Create dialog widgets"""
        from ttkbootstrap.constants import VERTICAL, Y
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

        frame = ttk.Frame(scrollable_frame, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text="Edit Spoilt Beer Record",
                 font=('Arial', 14, 'bold')).pack(pady=(0, 20))

        # Date Discovered
        ttk.Label(frame, text="Date Discovered *", font=('Arial', 10, 'bold')).pack(anchor='w', pady=(0, 5))
        self.date_entry = ttk.Entry(frame, font=('Arial', 10), width=40)
        self.date_entry.insert(0, self.record.get('date_discovered', ''))
        self.date_entry.pack(fill=tk.X, pady=(0, 15))

        # Duty Month (read-only)
        ttk.Label(frame, text="Duty Month (cannot be changed)", font=('Arial', 10, 'bold')).pack(anchor='w', pady=(0, 5))
        duty_month_label = ttk.Label(frame, text=self.record.get('duty_month', ''), font=('Arial', 10),
                                     foreground='#666')
        duty_month_label.pack(anchor='w', pady=(0, 15))

        # Batch ID
        ttk.Label(frame, text="Batch ID (optional)", font=('Arial', 10, 'bold')).pack(anchor='w', pady=(0, 5))
        self.batch_entry = ttk.Entry(frame, font=('Arial', 10), width=40)
        self.batch_entry.insert(0, self.record.get('batch_id', '') or '')
        self.batch_entry.pack(fill=tk.X, pady=(0, 15))

        # Gyle Number
        ttk.Label(frame, text="Gyle Number (optional)", font=('Arial', 10, 'bold')).pack(anchor='w', pady=(0, 5))
        self.gyle_entry = ttk.Entry(frame, font=('Arial', 10), width=40)
        self.gyle_entry.insert(0, self.record.get('gyle_number', '') or '')
        self.gyle_entry.pack(fill=tk.X, pady=(0, 15))

        # Container Type (read-only)
        ttk.Label(frame, text="Container Type (cannot be changed)", font=('Arial', 10, 'bold')).pack(anchor='w', pady=(0, 5))
        container_label = ttk.Label(frame, text=self.record.get('container_type', ''), font=('Arial', 10),
                                    foreground='#666')
        container_label.pack(anchor='w', pady=(0, 15))

        # Quantity (read-only)
        ttk.Label(frame, text="Quantity (cannot be changed)", font=('Arial', 10, 'bold')).pack(anchor='w', pady=(0, 5))
        qty_label = ttk.Label(frame, text=str(self.record.get('quantity', 0)), font=('Arial', 10),
                             foreground='#666')
        qty_label.pack(anchor='w', pady=(0, 15))

        # Calculated values (read-only)
        ttk.Label(frame, text="Calculated Values (read-only)", font=('Arial', 11, 'bold')).pack(anchor='w', pady=(10, 5))

        calc_frame = ttk.Frame(frame)
        calc_frame.pack(fill=tk.X, pady=(0, 15))

        volume = self.record.get('duty_paid_volume', 0)
        lpa = self.record.get('pure_alcohol_litres', 0)
        rate = self.record.get('original_duty_rate', 0)
        reclaim = self.record.get('duty_to_reclaim', 0)
        spr_cat = self.record.get('spr_category', 'N/A')

        ttk.Label(calc_frame, text=f"Volume: {volume:.2f}L").pack(anchor='w')
        ttk.Label(calc_frame, text=f"Pure Alcohol: {lpa:.2f} LPA").pack(anchor='w')
        ttk.Label(calc_frame, text=f"SPR Category: {spr_cat}").pack(anchor='w')
        ttk.Label(calc_frame, text=f"Duty Rate: £{rate:.2f}/LPA").pack(anchor='w')
        ttk.Label(calc_frame, text=f"Duty to Reclaim: £{reclaim:.2f}", font=('Arial', 10, 'bold')).pack(anchor='w')

        # Reason Category
        ttk.Label(frame, text="Reason Category", font=('Arial', 10, 'bold')).pack(anchor='w', pady=(10, 5))
        self.reason_combo = ttk.Combobox(frame, font=('Arial', 10), width=38, state='readonly')
        self.reason_combo['values'] = [
            'Infection/Contamination',
            'Off-Flavors/Quality Issues',
            'Package Defect/Leakage',
            'Condition Issues (Over/Under carbonated)',
            'Temperature Abuse',
            'Expired/Out of Date',
            'Other'
        ]
        current_reason = self.record.get('reason_category', '')
        if current_reason in self.reason_combo['values']:
            self.reason_combo.set(current_reason)
        self.reason_combo.pack(fill=tk.X, pady=(0, 15))

        # Reason Notes
        ttk.Label(frame, text="Additional Notes", font=('Arial', 10, 'bold')).pack(anchor='w', pady=(0, 5))
        self.notes_text = tk.Text(frame, font=('Arial', 10), width=40, height=4)
        self.notes_text.insert('1.0', self.record.get('reason_notes', '') or '')
        self.notes_text.pack(fill=tk.X, pady=(0, 15))

        # Status
        ttk.Label(frame, text="Status", font=('Arial', 10, 'bold')).pack(anchor='w', pady=(0, 5))
        self.status_combo = ttk.Combobox(frame, font=('Arial', 10), width=38, state='readonly')
        self.status_combo['values'] = ['pending', 'approved', 'claimed']
        current_status = self.record.get('status', 'pending')
        if current_status in self.status_combo['values']:
            self.status_combo.set(current_status)
        else:
            self.status_combo.current(0)
        self.status_combo.pack(fill=tk.X, pady=(0, 15))

        # Buttons
        button_frame = ttk.Frame(frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))

        ttk.Button(button_frame, text="Cancel", bootstyle="secondary",
                  command=self.destroy).pack(side=tk.RIGHT, padx=(10, 0))
        ttk.Button(button_frame, text="Save Changes", bootstyle="success",
                  command=self.save).pack(side=tk.RIGHT)

        # Pack canvas and scrollbar
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=Y)

        enable_canvas_scrolling(canvas)

    def save(self):
        """Save updated record"""
        # Get updated values
        date_discovered = self.date_entry.get().strip()
        batch_id = self.batch_entry.get().strip() or None
        gyle_number = self.gyle_entry.get().strip() or None
        reason_category = self.reason_combo.get().strip() or None
        reason_notes = self.notes_text.get('1.0', tk.END).strip() or None
        status = self.status_combo.get().strip()

        if not date_discovered:
            messagebox.showerror("Error", "Date discovered is required.")
            return

        # Update database
        self.cache.connect()

        cursor = self.cache.cursor

        cursor.execute('''
            UPDATE spoilt_beer
            SET date_discovered = ?,
                batch_id = ?,
                gyle_number = ?,
                reason_category = ?,
                reason_notes = ?,
                status = ?
            WHERE id = ?
        ''', (date_discovered, batch_id, gyle_number, reason_category,
              reason_notes, status, self.record['id']))

        self.cache.connection.commit()

        messagebox.showinfo("Success", "Spoilt beer record updated successfully!")
        self.destroy()
