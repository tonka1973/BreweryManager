"""
Inventory Module for Brewery Management System
Tracks brewing materials and finished goods inventory
"""

import os
import tkinter as tk
from tkinter import messagebox
import ttkbootstrap as ttk
import uuid
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from ..utilities.date_utils import get_today_db
from ..utilities.window_manager import get_window_manager, enable_mousewheel_scrolling, enable_treeview_keyboard_navigation


class InventoryModule(ttk.Frame):
    """Inventory module for tracking materials and finished goods"""

    def __init__(self, parent, cache_manager, current_user, sync_callback=None):
        super().__init__(parent)
        self.cache = cache_manager
        self.current_user = current_user
        self.sync_callback = sync_callback
        self.current_category = 'all'  # Track selected category

        self.create_widgets()
        self.load_materials()

    def create_widgets(self):
        """Create inventory widgets"""
        # Category tabs/buttons
        category_frame = ttk.Frame(self)
        category_frame.pack(fill=tk.X, padx=20, pady=(0, 10))

        categories = [
            ('All', 'all'),
            ('Grain', 'grain'),
            ('Hops', 'hops'),
            ('Yeast', 'yeast'),
            ('Adjunct', 'adjunct'),
            ('Sundries', 'sundries'),
            ('Containers', 'containers')
        ]

        self.category_buttons = {}
        for label, cat_id in categories:
            btn = ttk.Button(
                category_frame,
                text=label,
                bootstyle="secondary",
                cursor='hand2',
                command=lambda c=cat_id: self.switch_category(c)
            )
            btn.pack(side=tk.LEFT, padx=(0, 5))
            self.category_buttons[cat_id] = btn

        # Highlight "All" button by default
        self.category_buttons['all'].configure(bootstyle="success")

        # Toolbar
        toolbar = ttk.Frame(self)
        toolbar.pack(fill=tk.X, padx=20, pady=(10, 10))

        add_btn = ttk.Button(toolbar, text="➕ Add Material",
                           bootstyle="success",
                           cursor='hand2',
                           command=self.add_material)
        add_btn.pack(side=tk.LEFT, padx=(0, 10))

        edit_btn = ttk.Button(toolbar, text="✏️ Edit",
                            bootstyle="info",
                            cursor='hand2',
                            command=self.edit_material)
        edit_btn.pack(side=tk.LEFT, padx=(0, 10))

        stock_btn = ttk.Button(toolbar, text="📦 Adjust Stock",
                             bootstyle="warning",
                             cursor='hand2',
                             command=self.adjust_stock)
        stock_btn.pack(side=tk.LEFT, padx=(0, 10))

        delete_btn = ttk.Button(toolbar, text="🗑️ Delete",
                              bootstyle="danger",
                              cursor='hand2',
                              command=self.delete_material)
        delete_btn.pack(side=tk.LEFT, padx=(0, 10))

        refresh_btn = ttk.Button(toolbar, text="🔄 Refresh",
                               bootstyle="secondary",
                               cursor='hand2',
                               command=self.load_materials)
        refresh_btn.pack(side=tk.LEFT)

        logbook_btn = ttk.Button(toolbar, text="📖 Logbook",
                                bootstyle="info",
                                cursor='hand2',
                                command=self.open_logbook)
        logbook_btn.pack(side=tk.LEFT, padx=(10, 0))

        save_txt_btn = ttk.Button(toolbar, text="💾 Save TXT",
                                 bootstyle="info",
                                 cursor='hand2',
                                 command=self.save_txt_stock_report)
        save_txt_btn.pack(side=tk.LEFT, padx=(10, 0))

        print_btn = ttk.Button(toolbar, text="🖨️ Print",
                              bootstyle="success",
                              cursor='hand2',
                              command=self.print_stock_report)
        print_btn.pack(side=tk.LEFT, padx=(5, 0))

        # Materials list
        list_frame = ttk.Frame(self, relief=tk.SOLID, borderwidth=1)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))

        vsb = ttk.Scrollbar(list_frame, orient="vertical")
        vsb.pack(side=tk.RIGHT, fill=tk.Y)

        columns = ('Material', 'Type', 'Stock', 'Unit', 'Reorder', 'Supplier', 'Cost/Unit')
        self.tree = ttk.Treeview(list_frame, columns=columns, show='headings',
                                yscrollcommand=vsb.set)

        for col in columns:
            self.tree.heading(col, text=col, anchor='w')

        self.tree.column('Material', width=200)
        self.tree.column('Type', width=100)
        self.tree.column('Stock', width=100)
        self.tree.column('Unit', width=80)
        self.tree.column('Reorder', width=100)
        self.tree.column('Supplier', width=150)
        self.tree.column('Cost/Unit', width=100)

        self.tree.pack(fill=tk.BOTH, expand=True)
        vsb.config(command=self.tree.yview)

        # Double-click to adjust stock
        self.tree.bind('<Double-Button-1>', lambda e: self.adjust_stock())

        enable_mousewheel_scrolling(self.tree)
        enable_treeview_keyboard_navigation(self.tree)

    def switch_category(self, category):
        """Switch to a different category"""
        self.current_category = category

        # Update button colors (highlight active)
        for cat, btn in self.category_buttons.items():
            if cat == category:
                btn.configure(bootstyle="success")
            else:
                btn.configure(bootstyle="secondary")

        # Load appropriate view
        if category == 'containers':
            self.load_containers()
        else:
            self.load_materials()

    def load_materials(self):
        """Load materials from database"""
        for item in self.tree.get_children():
            self.tree.delete(item)

        self.cache.connect()
        materials = self.cache.get_all_records('inventory_materials', order_by='material_name')
        self.cache.close()

        for mat in materials:
            # Filter by category
            mat_type = mat.get('material_type', '')
            if self.current_category != 'all' and mat_type != self.current_category:
                continue

            stock = mat.get('current_stock', 0)
            reorder = mat.get('reorder_level', 0)

            # Display "Sundries" instead of "other" in the type column
            display_type = mat_type.capitalize()
            if mat_type == 'sundries':
                display_type = 'Sundries'

            values = (
                mat.get('material_name', ''),
                display_type,
                f"{stock:.1f}",
                mat.get('unit', ''),
                f"{reorder:.1f}",
                mat.get('supplier', 'N/A'),
                f"£{mat.get('cost_per_unit', 0):.2f}"
            )

            tag = 'low' if stock <= reorder else 'ok'
            self.tree.insert('', 'end', values=values, tags=(tag, mat['material_id']))

        self.tree.tag_configure('low', background='#ffebee')
        self.tree.tag_configure('ok', background='#e8f5e9')

    def load_containers(self):
        """Load containers from container_types table"""
        for item in self.tree.get_children():
            self.tree.delete(item)

        self.cache.connect()

        # Load from unified container_types table
        containers = self.cache.get_all_records('container_types', 'active = 1', order_by='category, name')

        for container in containers:
            values = (
                f"{container.get('name', '')} ({container.get('size_litres', 0):.1f}L)",
                container.get('category', 'Container'),
                str(container.get('quantity_available', 0)),
                'units',
                '',  # No reorder level for containers
                '',  # No supplier
                ''   # No cost
            )
            self.tree.insert('', 'end', values=values, tags=('container', container['container_type_id']))

        self.cache.close()

        # Tag all containers with neutral color
        self.tree.tag_configure('container', background='#e3f2fd')

    def add_material(self):
        """Add new material or container"""
        if self.current_category == 'containers':
            dialog = ContainerTypeDialog(self, self.cache, self.current_user, mode='add')
            self.wait_window(dialog)
            self.load_containers()
            if self.sync_callback: self.sync_callback()
        else:
            dialog = MaterialDialog(self, self.cache, self.current_user, mode='add')
            self.wait_window(dialog)
            self.load_materials()
            if self.sync_callback: self.sync_callback()

    def edit_material(self):
        """Edit selected material"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a material.")
            return

        tags = self.tree.item(selection[0], 'tags')
        material_id = tags[1] if len(tags) > 1 else None

        self.cache.connect()
        materials = self.cache.get_all_records('inventory_materials', f"material_id = '{material_id}'")
        self.cache.close()

        if materials:
            dialog = MaterialDialog(self, self.cache, self.current_user, mode='edit', material=materials[0])
            self.wait_window(dialog)
            self.load_materials()
            if self.sync_callback: self.sync_callback()

    def adjust_stock(self):
        """Adjust stock levels"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select an item.")
            return

        tags = self.tree.item(selection[0], 'tags')

        if self.current_category == 'containers':
            # Handle container adjustment from container_types table
            container_type_id = tags[1] if len(tags) > 1 else None

            self.cache.connect()
            containers = self.cache.get_all_records('container_types',
                f"container_type_id = '{container_type_id}'")
            self.cache.close()

            if containers:
                dialog = ContainerTypeAdjustDialog(self, self.cache, self.current_user, containers[0])
                self.wait_window(dialog)
                self.load_containers()
                if self.sync_callback: self.sync_callback()
        else:
            # Handle material adjustment
            material_id = tags[1] if len(tags) > 1 else None

            self.cache.connect()
            materials = self.cache.get_all_records('inventory_materials', f"material_id = '{material_id}'")
            self.cache.close()

            if materials:
                dialog = StockAdjustDialog(self, self.cache, self.current_user, materials[0])
                self.wait_window(dialog)
                self.load_materials()
                if self.sync_callback: self.sync_callback()

    def delete_material(self):
        """Delete material or container"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select an item.")
            return

        result = messagebox.askyesno("Confirm Delete", "Delete this item?")
        if result:
            tags = self.tree.item(selection[0], 'tags')

            self.cache.connect()
            if self.current_category == 'containers':
                container_type_id = tags[1] if len(tags) > 1 else None

                # Mark as inactive instead of deleting (for data integrity)
                self.cache.update_record('container_types', container_type_id, {
                    'active': 0,
                    'last_modified': datetime.now().isoformat()
                }, 'container_type_id')

                self.cache.close()
                messagebox.showinfo("Success", "Container type deactivated.")
                self.load_containers()
                if self.sync_callback: self.sync_callback()
            else:
                material_id = tags[1] if len(tags) > 1 else None
                self.cache.delete_record('inventory_materials', material_id, 'material_id')
                self.cache.close()
                messagebox.showinfo("Success", "Material deleted.")
                self.load_materials()
                if self.sync_callback: self.sync_callback()

    def open_logbook(self):
        """Open inventory logbook dialog"""
        dialog = InventoryLogbookDialog(self, self.cache, self.current_user)
        self.wait_window(dialog)

    def save_txt_stock_report(self):
        """Save stock report to TXT file"""
        from tkinter import filedialog

        # Build report header
        report_lines = []
        report_lines.append("=" * 100)
        report_lines.append("BREWERY INVENTORY STOCK REPORT")
        report_lines.append("=" * 100)
        report_lines.append(f"Generated: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        report_lines.append("")

        # Show active category
        category_name = self.current_category.capitalize() if self.current_category != 'all' else 'All Categories'
        if self.current_category == 'containers':
            category_name = 'Containers'

        report_lines.append(f"Category: {category_name}")
        report_lines.append("=" * 100)
        report_lines.append("")

        # Get all items from tree
        items = self.tree.get_children()
        if not items:
            messagebox.showinfo("No Data", "No items to print in current category.")
            return

        # Table header
        report_lines.append(f"{'Material':<30} {'Type':<12} {'Stock':<12} {'Unit':<8} {'Reorder':<12} {'Supplier':<25} {'Cost/Unit':<12}")
        report_lines.append("-" * 100)

        # Add each material
        low_stock_items = []
        for item in items:
            values = self.tree.item(item)['values']
            material, mat_type, stock, unit, reorder, supplier, cost = values

            # Truncate long fields
            material = material[:29] if len(material) > 29 else material
            mat_type = mat_type[:11] if len(mat_type) > 11 else mat_type
            supplier = supplier[:24] if len(supplier) > 24 else supplier

            line = f"{material:<30} {mat_type:<12} {stock:<12} {unit:<8} {reorder:<12} {supplier:<25} {cost:<12}"
            report_lines.append(line)

            # Check for low stock
            try:
                stock_val = float(stock)
                reorder_val = float(reorder)
                if stock_val <= reorder_val:
                    low_stock_items.append(material)
            except:
                pass

        report_lines.append("")
        report_lines.append("=" * 100)
        report_lines.append(f"Total Items: {len(items)}")

        if low_stock_items:
            report_lines.append("")
            report_lines.append("*** LOW STOCK ALERT ***")
            report_lines.append(f"Items at or below reorder level: {len(low_stock_items)}")
            for item in low_stock_items:
                report_lines.append(f"  - {item}")

        report_lines.append("=" * 100)

        # Save to file
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            initialfile=f"inventory_stock_{category_name.lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        )

        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(report_lines))
                messagebox.showinfo("Success", f"Report saved to:\n{filename}\n\nYou can now open and print this file.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save report:\n{str(e)}")

    def print_stock_report(self):
        """Generate PDF report and open it for printing"""
        # Get all items from tree
        items = self.tree.get_children()
        if not items:
            messagebox.showinfo("No Data", "No items to print in current category.")
            return

        # Build report data
        report_lines = []
        report_lines.append("BREWERY INVENTORY STOCK REPORT")
        report_lines.append(f"Generated: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        report_lines.append("")

        # Show active category
        category_name = self.current_category.capitalize() if self.current_category != 'all' else 'All Categories'
        if self.current_category == 'containers':
            category_name = 'Containers'

        report_lines.append(f"Category: {category_name}")
        report_lines.append("")
        report_lines.append(f"{'Material':<30} {'Type':<12} {'Stock':<12} {'Unit':<8} {'Reorder':<12} {'Supplier':<25} {'Cost/Unit':<12}")
        report_lines.append("-" * 115)

        # Add each material
        low_stock_items = []
        for item in items:
            values = self.tree.item(item)['values']
            material, mat_type, stock, unit, reorder, supplier, cost = values

            # Truncate long fields
            material = material[:29] if len(material) > 29 else material
            mat_type = mat_type[:11] if len(mat_type) > 11 else mat_type
            supplier = supplier[:24] if len(supplier) > 24 else supplier

            line = f"{material:<30} {mat_type:<12} {stock:<12} {unit:<8} {reorder:<12} {supplier:<25} {cost:<12}"
            report_lines.append(line)

            # Check for low stock
            try:
                stock_val = float(stock)
                reorder_val = float(reorder)
                if stock_val <= reorder_val:
                    low_stock_items.append(material)
            except:
                pass

        report_lines.append("")
        report_lines.append(f"Total Items: {len(items)}")

        if low_stock_items:
            report_lines.append("")
            report_lines.append("*** LOW STOCK ALERT ***")
            report_lines.append(f"Items at or below reorder level: {len(low_stock_items)}")
            for item in low_stock_items:
                report_lines.append(f"  - {item}")

        # Generate PDF
        try:
            # Create reports directory if it doesn't exist
            reports_dir = os.path.expanduser('~/.brewerymanager/reports')
            os.makedirs(reports_dir, exist_ok=True)

            # Generate filename with timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            category_suffix = self.current_category if self.current_category != 'all' else 'all'
            pdf_filename = os.path.join(reports_dir, f"stock_report_{category_suffix}_{timestamp}.pdf")

            # Create PDF
            c = canvas.Canvas(pdf_filename, pagesize=A4)
            width, height = A4

            # Use Courier (monospace) for table alignment
            c.setFont("Courier", 8)

            # Starting position
            y_position = height - 40
            line_height = 12

            # Draw each line
            for line in report_lines:
                if y_position < 40:  # New page if near bottom
                    c.showPage()
                    c.setFont("Courier", 8)
                    y_position = height - 40

                c.drawString(40, y_position, line)
                y_position -= line_height

            # Save PDF
            c.save()

            # Open PDF in default viewer (like label printing)
            os.startfile(pdf_filename)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate PDF:\n{str(e)}")


class MaterialDialog(tk.Toplevel):
    """Dialog for adding/editing materials"""

    def __init__(self, parent, cache_manager, current_user, mode='add', material=None):
        super().__init__(parent)
        self.cache = cache_manager
        self.current_user = current_user
        self.mode = mode
        self.material = material

        self.title("Add Material" if mode == 'add' else "Edit Material")
        self.transient(parent)
        self.grab_set()

        # Use window manager for sizing if available
        wm = get_window_manager()
        if wm:
            wm.setup_dialog(self, 'material_dialog', width_pct=0.35, height_pct=0.6,
                          add_grip=True, save_on_close=True, resizable=True)
        else:
            # Fallback to hardcoded size
            self.geometry("500x550")
            self.resizable(True, True)

        self.create_widgets()
        if mode == 'edit' and material:
            self.populate_fields()

    def create_widgets(self):
        """Create dialog widgets"""
        # Buttons (Bottom) - PACK FIRST
        button_frame = ttk.Frame(self, padding=(20, 10))
        button_frame.pack(fill=tk.X, side=tk.BOTTOM)

        ttk.Button(button_frame, text="Cancel", bootstyle="secondary",
                  command=self.destroy).pack(side=tk.RIGHT, padx=(10,0))
        ttk.Button(button_frame, text="Save", bootstyle="success",
                  command=self.save).pack(side=tk.RIGHT)

        frame = ttk.Frame(self, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text="Material Name *", font=('Arial', 10, 'bold')).grid(row=0, column=0, sticky='w', pady=(0,5))
        self.name_entry = ttk.Entry(frame, font=('Arial', 10), width=40)
        self.name_entry.grid(row=1, column=0, columnspan=2, sticky='ew', pady=(0,15))

        ttk.Label(frame, text="Type *", font=('Arial', 10, 'bold')).grid(row=2, column=0, sticky='w', pady=(0,5))
        self.type_var = tk.StringVar(value='grain')
        types = ['grain', 'hops', 'yeast', 'adjunct', 'sundries']
        type_menu = ttk.Combobox(frame, textvariable=self.type_var, values=types, font=('Arial', 10), width=37, state='readonly')
        type_menu.grid(row=3, column=0, columnspan=2, sticky='ew', pady=(0,15))

        ttk.Label(frame, text="Current Stock *", font=('Arial', 10, 'bold')).grid(row=4, column=0, sticky='w', pady=(0,5))
        self.stock_entry = ttk.Entry(frame, font=('Arial', 10), width=15)
        self.stock_entry.grid(row=5, column=0, sticky='w', pady=(0,15))

        ttk.Label(frame, text="Unit *", font=('Arial', 10, 'bold')).grid(row=4, column=1, sticky='w', pady=(0,5), padx=(20,0))
        self.unit_var = tk.StringVar()
        self.unit_entry = ttk.Combobox(frame, textvariable=self.unit_var, 
                                      values=['kg', 'g', 'L', 'ml', 'oz', 'lb', 'units'],
                                      font=('Arial', 10), width=13)
        self.unit_entry.grid(row=5, column=1, sticky='w', pady=(0,15), padx=(20,0))

        ttk.Label(frame, text="Reorder Level", font=('Arial', 10, 'bold')).grid(row=6, column=0, sticky='w', pady=(0,5))
        self.reorder_entry = ttk.Entry(frame, font=('Arial', 10), width=15)
        self.reorder_entry.grid(row=7, column=0, sticky='w', pady=(0,15))

        ttk.Label(frame, text="Cost per Unit (£)", font=('Arial', 10, 'bold')).grid(row=6, column=1, sticky='w', pady=(0,5), padx=(20,0))
        self.cost_entry = ttk.Entry(frame, font=('Arial', 10), width=15)
        self.cost_entry.grid(row=7, column=1, sticky='w', pady=(0,15), padx=(20,0))

        ttk.Label(frame, text="Supplier", font=('Arial', 10, 'bold')).grid(row=8, column=0, sticky='w', pady=(0,5))
        self.supplier_entry = ttk.Entry(frame, font=('Arial', 10), width=40)
        self.supplier_entry.grid(row=9, column=0, columnspan=2, sticky='ew', pady=(0,15))

        frame.grid_columnconfigure(0, weight=1)
        frame.grid_columnconfigure(1, weight=1)

        

    def populate_fields(self):
        """Populate fields with material data"""
        self.name_entry.insert(0, self.material.get('material_name', ''))
        self.type_var.set(self.material.get('material_type', 'grain'))
        self.stock_entry.insert(0, str(self.material.get('current_stock', '')))
        self.unit_entry.set(self.material.get('unit', ''))
        self.reorder_entry.insert(0, str(self.material.get('reorder_level', '')))
        self.cost_entry.insert(0, str(self.material.get('cost_per_unit', '')))
        self.supplier_entry.insert(0, self.material.get('supplier', ''))

    def save(self):
        """Save material"""
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showerror("Error", "Material name is required.")
            return

        try:
            stock = float(self.stock_entry.get() or 0)
            reorder = float(self.reorder_entry.get() or 0)
            cost = float(self.cost_entry.get() or 0)
        except ValueError:
            messagebox.showerror("Error", "Invalid number format.")
            return

        data = {
            'material_name': name,
            'material_type': self.type_var.get(),
            'current_stock': stock,
            'unit': self.unit_entry.get().strip(),
            'reorder_level': reorder,
            'cost_per_unit': cost,
            'supplier': self.supplier_entry.get().strip(),
            'last_updated': get_today_db(),
            'sync_status': 'pending'
        }

        self.cache.connect()
        if self.mode == 'add':
            data['material_id'] = str(uuid.uuid4())
            self.cache.insert_record('inventory_materials', data)
        else:
            self.cache.update_record('inventory_materials', self.material['material_id'], data, 'material_id')
        self.cache.close()

        messagebox.showinfo("Success", "Material saved!")
        self.destroy()


class StockAdjustDialog(tk.Toplevel):
    """Dialog for adjusting stock levels"""

    def __init__(self, parent, cache_manager, current_user, material):
        super().__init__(parent)
        self.cache = cache_manager
        self.current_user = current_user
        self.material = material

        self.title(f"Adjust Stock: {material['material_name']}")
        self.transient(parent)
        self.grab_set()

        # Use window manager for sizing if available
        wm = get_window_manager()
        if wm:
            wm.setup_dialog(self, 'stock_adjust_dialog', width_pct=0.3, height_pct=0.4,
                          add_grip=True, save_on_close=True, resizable=True)
        else:
            # Fallback to hardcoded size
            self.geometry("400x350")
            self.resizable(True, True)

        self.create_widgets()

    def create_widgets(self):
        """Create widgets"""
        # Buttons (Bottom) - PACK FIRST
        button_frame = ttk.Frame(self, padding=(20, 10))
        button_frame.pack(fill=tk.X, side=tk.BOTTOM)

        ttk.Button(button_frame, text="Cancel", bootstyle="secondary",
                  command=self.destroy).pack(side=tk.RIGHT, padx=(10,0))
        ttk.Button(button_frame, text="Apply", bootstyle="warning",
                  command=self.apply_adjustment).pack(side=tk.RIGHT)

        frame = ttk.Frame(self, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)

        current = self.material.get('current_stock', 0)
        ttk.Label(frame, text=f"Current Stock: {current:.1f} {self.material.get('unit', '')}",
                font=('Arial', 12, 'bold')).pack(pady=(0,20))

        ttk.Label(frame, text="Adjustment Type", font=('Arial', 10, 'bold')).pack(anchor='w', pady=(0,5))
        self.adj_type = tk.StringVar(value='add')
        ttk.Radiobutton(frame, text="Add Stock", variable=self.adj_type, value='add').pack(anchor='w')
        ttk.Radiobutton(frame, text="Remove Stock", variable=self.adj_type, value='remove').pack(anchor='w', pady=(0,15))

        ttk.Label(frame, text="Quantity", font=('Arial', 10, 'bold')).pack(anchor='w', pady=(0,5))
        self.qty_entry = ttk.Entry(frame, font=('Arial', 11), width=15)
        self.qty_entry.pack(anchor='w', pady=(0,15))

        ttk.Label(frame, text="Reason/Notes", font=('Arial', 10, 'bold')).pack(anchor='w', pady=(0,5))
        self.notes_text = tk.Text(frame, font=('Arial', 10), width=40, height=4)
        self.notes_text.pack(pady=(0,15))

    def apply_adjustment(self):
        """Apply stock adjustment"""
        try:
            qty = float(self.qty_entry.get())
        except ValueError:
            messagebox.showerror("Error", "Invalid quantity.")
            return

        current = self.material.get('current_stock', 0)
        if self.adj_type.get() == 'add':
            new_stock = current + qty
        else:
            new_stock = current - qty

        if new_stock < 0:
            messagebox.showerror("Error", "Stock cannot be negative.")
            return

        # Update material stock
        self.cache.connect()
        self.cache.update_record('inventory_materials', self.material['material_id'],
                                {'current_stock': new_stock, 'last_updated': get_today_db(),
                                 'sync_status': 'pending'}, 'material_id')

        # Log transaction
        trans_data = {
            'transaction_id': str(uuid.uuid4()),
            'transaction_date': get_today_db(),
            'transaction_type': self.adj_type.get(),
            'material_id': self.material['material_id'],
            'quantity_change': qty if self.adj_type.get() == 'add' else -qty,
            'new_balance': new_stock,
            'reference': 'Manual adjustment',
            'username': self.current_user.username,
            'notes': self.notes_text.get('1.0', tk.END).strip(),
            'sync_status': 'pending'
        }
        self.cache.insert_record('inventory_transactions', trans_data)
        self.cache.close()

        messagebox.showinfo("Success", f"Stock updated to {new_stock:.1f}")
        self.destroy()


class ContainerDialog(tk.Toplevel):
    """Dialog for adding new containers"""

    def __init__(self, parent, cache_manager, current_user, mode='add'):
        super().__init__(parent)
        self.cache = cache_manager
        self.current_user = current_user
        self.mode = mode

        self.title("Add Container")
        self.transient(parent)
        self.grab_set()

        # Use window manager for sizing if available
        wm = get_window_manager()
        if wm:
            wm.setup_dialog(self, 'container_dialog', width_pct=0.32, height_pct=0.45,
                          add_grip=True, save_on_close=True, resizable=True)
        else:
            # Fallback to hardcoded size
            self.geometry("450x400")
            self.resizable(True, True)

        self.create_widgets()

    def create_widgets(self):
        """Create dialog widgets"""
        # Buttons (Bottom) - PACK FIRST
        button_frame = ttk.Frame(self, padding=(20, 10))
        button_frame.pack(fill=tk.X, side=tk.BOTTOM)

        ttk.Button(button_frame, text="Cancel", bootstyle="secondary",
                  command=self.destroy).pack(side=tk.RIGHT, padx=(10,0))
        ttk.Button(button_frame, text="Save", bootstyle="success",
                  command=self.save).pack(side=tk.RIGHT)

        frame = ttk.Frame(self, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text="Container Type *", font=('Arial', 10, 'bold')).grid(row=0, column=0, sticky='w', pady=(0,5))
        self.type_var = tk.StringVar(value='cask')
        type_menu = ttk.Combobox(frame, textvariable=self.type_var, values=['cask', 'bottle', 'can'],
                                font=('Arial', 10), width=37, state='readonly')
        type_menu.grid(row=1, column=0, columnspan=2, sticky='ew', pady=(0,15))
        type_menu.bind('<<ComboboxSelected>>', self.on_type_change)

        ttk.Label(frame, text="Container Size *", font=('Arial', 10, 'bold')).grid(row=2, column=0, sticky='w', pady=(0,5))
        self.size_var = tk.StringVar()
        self.size_menu = ttk.Combobox(frame, textvariable=self.size_var, font=('Arial', 10), width=37, state='readonly')
        self.size_menu.grid(row=3, column=0, columnspan=2, sticky='ew', pady=(0,15))

        ttk.Label(frame, text="Initial Quantity *", font=('Arial', 10, 'bold')).grid(row=4, column=0, sticky='w', pady=(0,5))
        self.qty_entry = ttk.Entry(frame, font=('Arial', 10), width=15)
        self.qty_entry.grid(row=5, column=0, sticky='w', pady=(0,15))
        self.qty_entry.insert(0, "0")

        ttk.Label(frame, text="Condition", font=('Arial', 10, 'bold')).grid(row=6, column=0, sticky='w', pady=(0,5))
        self.condition_var = tk.StringVar(value='Good')
        condition_menu = ttk.Combobox(frame, textvariable=self.condition_var,
                                     values=['Good', 'Fair', 'Poor', 'Needs Repair'],
                                     font=('Arial', 10), width=37, state='readonly')
        condition_menu.grid(row=7, column=0, columnspan=2, sticky='ew', pady=(0,15))

        ttk.Label(frame, text="Notes", font=('Arial', 10, 'bold')).grid(row=8, column=0, sticky='w', pady=(0,5))
        self.notes_text = tk.Text(frame, font=('Arial', 10), width=40, height=3)
        self.notes_text.grid(row=9, column=0, columnspan=2, sticky='ew', pady=(0,15))

        frame.grid_columnconfigure(0, weight=1)

        # Initialize size options
        self.on_type_change()

    def on_type_change(self, event=None):
        """Update size options based on container type"""
        container_type = self.type_var.get()

        if container_type == 'cask':
            sizes = ['Pin (4.5 gallons / 20.5L)', 'Firkin (9 gallons / 40.9L)', 'Kilderkin (18 gallons / 81.8L)']
        elif container_type == 'bottle':
            sizes = ['330ml', '500ml', '568ml']
        elif container_type == 'can':
            sizes = ['330ml', '500ml', '568ml', '5L']
        else:
            sizes = []

        self.size_menu['values'] = sizes
        if sizes:
            self.size_var.set(sizes[0])

    def save(self):
        """Save container"""
        container_type = self.type_var.get()
        size_str = self.size_var.get()

        if not size_str:
            messagebox.showerror("Error", "Please select a container size.")
            return

        try:
            qty = int(self.qty_entry.get())
        except ValueError:
            messagebox.showerror("Error", "Quantity must be a whole number.")
            return

        if qty < 0:
            messagebox.showerror("Error", "Quantity cannot be negative.")
            return

        self.cache.connect()

        # Prepare data based on container type
        if container_type == 'cask':
            # Extract cask size and litres from selection
            if 'Pin' in size_str:
                cask_size = 'Pin'
                cask_size_litres = 20.5
            elif 'Firkin' in size_str:
                cask_size = 'Firkin'
                cask_size_litres = 40.9
            elif 'Kilderkin' in size_str:
                cask_size = 'Kilderkin'
                cask_size_litres = 81.8
            else:
                messagebox.showerror("Error", "Invalid cask size.")
                self.cache.close()
                return

            # Check if this cask size already exists
            existing = self.cache.get_all_records('casks_empty', f"cask_size = '{cask_size}'")
            if existing:
                messagebox.showwarning("Already Exists", f"{cask_size} casks already exist. Use 'Adjust Stock' to change quantity.")
                self.cache.close()
                return

            data = {
                'cask_id': str(uuid.uuid4()),
                'cask_size': cask_size,
                'cask_size_litres': cask_size_litres,
                'quantity_in_stock': qty,
                'condition': self.condition_var.get(),
                'last_updated': get_today_db(),
                'notes': self.notes_text.get('1.0', tk.END).strip(),
                'sync_status': 'pending'
            }
            self.cache.insert_record('casks_empty', data)

        elif container_type == 'bottle':
            bottle_size_ml = int(size_str.replace('ml', ''))

            # Check if this bottle size already exists
            existing = self.cache.get_all_records('bottles_empty', f"bottle_size_ml = {bottle_size_ml}")
            if existing:
                messagebox.showwarning("Already Exists", f"{bottle_size_ml}ml bottles already exist. Use 'Adjust Stock' to change quantity.")
                self.cache.close()
                return

            data = {
                'bottle_id': str(uuid.uuid4()),
                'bottle_size_ml': bottle_size_ml,
                'quantity_in_stock': qty,
                'condition': self.condition_var.get(),
                'last_updated': get_today_db(),
                'notes': self.notes_text.get('1.0', tk.END).strip(),
                'sync_status': 'pending'
            }
            self.cache.insert_record('bottles_empty', data)

        elif container_type == 'can':
            # Parse can size (handle both ml and L)
            if 'L' in size_str and 'ml' not in size_str:
                can_size_ml = int(float(size_str.replace('L', '')) * 1000)
            else:
                can_size_ml = int(size_str.replace('ml', ''))

            # Check if this can size already exists
            existing = self.cache.get_all_records('cans_empty', f"can_size_ml = {can_size_ml}")
            if existing:
                size_display = f"{can_size_ml/1000:.1f}L" if can_size_ml >= 1000 else f"{can_size_ml}ml"
                messagebox.showwarning("Already Exists", f"{size_display} cans already exist. Use 'Adjust Stock' to change quantity.")
                self.cache.close()
                return

            data = {
                'can_id': str(uuid.uuid4()),
                'can_size_ml': can_size_ml,
                'quantity_in_stock': qty,
                'condition': self.condition_var.get(),
                'last_updated': get_today_db(),
                'notes': self.notes_text.get('1.0', tk.END).strip(),
                'sync_status': 'pending'
            }
            self.cache.insert_record('cans_empty', data)

        self.cache.close()

        messagebox.showinfo("Success", "Container added!")
        self.destroy()


class ContainerAdjustDialog(tk.Toplevel):
    """Dialog for adjusting container quantities"""

    def __init__(self, parent, cache_manager, current_user, container, container_type, table, id_field):
        super().__init__(parent)
        self.cache = cache_manager
        self.current_user = current_user
        self.container = container
        self.container_type = container_type
        self.table = table
        self.id_field = id_field

        # Get container name for title
        if container_type == 'cask':
            name = f"{container.get('cask_size', '')} ({container.get('cask_size_litres', 0):.1f}L)"
        elif container_type == 'bottle':
            name = f"Bottle {container.get('bottle_size_ml', 0)}ml"
        elif container_type == 'can':
            size_ml = container.get('can_size_ml', 0)
            name = f"Can {size_ml/1000:.1f}L" if size_ml >= 1000 else f"Can {size_ml}ml"
        else:
            name = "Container"

        self.title(f"Adjust Stock: {name}")
        self.transient(parent)
        self.grab_set()

        # Use window manager for sizing if available
        wm = get_window_manager()
        if wm:
            wm.setup_dialog(self, 'container_adjust_dialog', width_pct=0.3, height_pct=0.35,
                          add_grip=True, save_on_close=True, resizable=True)
        else:
            # Fallback to hardcoded size
            self.geometry("400x300")
            self.resizable(True, True)

        self.create_widgets()

    def create_widgets(self):
        """Create widgets"""
        # Buttons (Top)
        button_frame = ttk.Frame(self, padding=(20, 10))
        button_frame.pack(fill=tk.X, side=tk.TOP)

        ttk.Button(button_frame, text="Cancel", bootstyle="secondary",
                  command=self.destroy).pack(side=tk.RIGHT, padx=(10,0))
        ttk.Button(button_frame, text="Apply", bootstyle="warning",
                  command=self.apply_adjustment).pack(side=tk.RIGHT)

        frame = ttk.Frame(self, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)

        current = self.container.get('quantity_in_stock', 0)
        ttk.Label(frame, text=f"Current Stock: {current} units",
                font=('Arial', 12, 'bold')).pack(pady=(0,20))

        ttk.Label(frame, text="Adjustment Type", font=('Arial', 10, 'bold')).pack(anchor='w', pady=(0,5))
        self.adj_type = tk.StringVar(value='add')
        ttk.Radiobutton(frame, text="Add Stock", variable=self.adj_type, value='add').pack(anchor='w')
        ttk.Radiobutton(frame, text="Remove Stock", variable=self.adj_type, value='remove').pack(anchor='w', pady=(0,15))

        ttk.Label(frame, text="Quantity", font=('Arial', 10, 'bold')).pack(anchor='w', pady=(0,5))
        self.qty_entry = ttk.Entry(frame, font=('Arial', 11), width=15)
        self.qty_entry.pack(anchor='w', pady=(0,15))

        ttk.Label(frame, text="Reason/Notes", font=('Arial', 10, 'bold')).pack(anchor='w', pady=(0,5))
        self.notes_text = tk.Text(frame, font=('Arial', 10), width=40, height=3)
        self.notes_text.pack(pady=(0,15))


    def apply_adjustment(self):
        """Apply stock adjustment"""
        try:
            qty = int(self.qty_entry.get())
        except ValueError:
            messagebox.showerror("Error", "Quantity must be a whole number.")
            return

        current = self.container.get('quantity_in_stock', 0)
        if self.adj_type.get() == 'add':
            new_stock = current + qty
        else:
            new_stock = current - qty

        if new_stock < 0:
            messagebox.showerror("Error", "Stock cannot be negative.")
            return

        # Update container stock
        self.cache.connect()
        container_id = self.container[self.id_field]
        self.cache.update_record(self.table, container_id,
                                {'quantity_in_stock': new_stock, 'last_updated': get_today_db(),
                                 'sync_status': 'pending'}, self.id_field)
        self.cache.close()

        messagebox.showinfo("Success", f"Stock updated to {new_stock} units")
        self.destroy()

# NEW: Container Type Management Dialogs for unified container_types table

class ContainerTypeDialog(tk.Toplevel):
    """Dialog for adding new container types to container_types table"""

    def __init__(self, parent, cache_manager, current_user, mode='add'):
        super().__init__(parent)
        self.cache = cache_manager
        self.current_user = current_user
        self.mode = mode

        self.title("Add Container Type")
        self.transient(parent)
        self.grab_set()

        # Use window manager for sizing if available
        wm = get_window_manager()
        if wm:
            wm.setup_dialog(self, 'container_type_dialog', width_pct=0.35, height_pct=0.45,
                          add_grip=True, save_on_close=True, resizable=True)
        else:
            self.geometry("500x400")
            self.resizable(True, True)

        self.create_widgets()

    def create_widgets(self):
        """Create dialog widgets"""
        # Buttons (Top)
        button_frame = ttk.Frame(self, padding=(20, 10))
        button_frame.pack(fill=tk.X, side=tk.TOP)

        ttk.Button(button_frame, text="Cancel", bootstyle="secondary",
                  command=self.destroy).pack(side=tk.RIGHT, padx=(10,0))
        ttk.Button(button_frame, text="Save", bootstyle="success",
                  command=self.save).pack(side=tk.RIGHT)

        frame = ttk.Frame(self, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text="Container Name *", font=('Arial', 10, 'bold')).grid(row=0, column=0, sticky='w', pady=(0,5))
        ttk.Label(frame, text="e.g., 'Firkin', '500ml Bottle', '30L Keg'", font=('Arial', 8, 'italic'),
                 foreground='#666').grid(row=1, column=0, sticky='w', pady=(0,5))
        self.name_entry = ttk.Entry(frame, font=('Arial', 10), width=40)
        self.name_entry.grid(row=2, column=0, columnspan=2, sticky='ew', pady=(0,15))

        ttk.Label(frame, text="Size (Litres) *", font=('Arial', 10, 'bold')).grid(row=3, column=0, sticky='w', pady=(0,5))
        ttk.Label(frame, text="e.g., '40.9' for Firkin, '0.5' for 500ml", font=('Arial', 8, 'italic'),
                 foreground='#666').grid(row=4, column=0, sticky='w', pady=(0,5))
        self.size_entry = ttk.Entry(frame, font=('Arial', 10), width=15)
        self.size_entry.grid(row=5, column=0, sticky='w', pady=(0,15))

        ttk.Label(frame, text="Category", font=('Arial', 10, 'bold')).grid(row=3, column=1, sticky='w', pady=(0,5), padx=(20,0))
        self.category_var = tk.StringVar(value='Cask')
        category_menu = ttk.Combobox(frame, textvariable=self.category_var,
                                     values=['Cask', 'Keg', 'Bottle', 'Can', 'Other'],
                                     font=('Arial', 10), width=15, state='readonly')
        category_menu.grid(row=5, column=1, sticky='w', pady=(0,15), padx=(20,0))

        ttk.Label(frame, text="Initial Quantity *", font=('Arial', 10, 'bold')).grid(row=6, column=0, sticky='w', pady=(0,5))
        self.qty_entry = ttk.Entry(frame, font=('Arial', 10), width=15)
        self.qty_entry.grid(row=7, column=0, sticky='w', pady=(0,15))
        self.qty_entry.insert(0, "0")

        frame.grid_columnconfigure(0, weight=1)


    def save(self):
        """Save container type"""
        name = self.name_entry.get().strip()
        size_str = self.size_entry.get().strip()
        category = self.category_var.get()

        if not name or not size_str:
            messagebox.showerror("Error", "Please fill in all required fields.")
            return

        try:
            size_litres = float(size_str)
            if size_litres <= 0:
                raise ValueError()
        except ValueError:
            messagebox.showerror("Error", "Size must be a positive number.")
            return

        try:
            qty = int(self.qty_entry.get())
            if qty < 0:
                raise ValueError()
        except ValueError:
            messagebox.showerror("Error", "Quantity must be a non-negative number.")
            return

        self.cache.connect()

        # Check if this container type already exists
        existing = self.cache.get_all_records('container_types',
            f"name = '{name}' AND active = 1")
        if existing:
            messagebox.showwarning("Already Exists",
                f"Container type '{name}' already exists. Use 'Adjust Stock' to change quantity.")
            self.cache.close()
            return

        data = {
            'container_type_id': str(uuid.uuid4()),
            'name': name,
            'size_litres': size_litres,
            'category': category,
            'quantity_available': qty,
            'active': 1,
            'created_date': datetime.now().isoformat(),
            'last_modified': datetime.now().isoformat(),
            'sync_status': 'pending'
        }
        self.cache.insert_record('container_types', data)
        self.cache.close()

        messagebox.showinfo("Success", f"Container type '{name}' added!")
        self.destroy()


class ContainerTypeAdjustDialog(tk.Toplevel):
    """Dialog for adjusting container type quantities"""

    def __init__(self, parent, cache_manager, current_user, container_type):
        super().__init__(parent)
        self.cache = cache_manager
        self.current_user = current_user
        self.container_type = container_type

        self.title(f"Adjust Stock: {container_type.get('name', 'Unknown')}")
        self.transient(parent)
        self.grab_set()

        # Use window manager for sizing if available
        wm = get_window_manager()
        if wm:
            wm.setup_dialog(self, 'container_type_adjust_dialog', width_pct=0.3, height_pct=0.35,
                          add_grip=True, save_on_close=True, resizable=True)
        else:
            self.geometry("400x300")
            self.resizable(True, True)

        self.create_widgets()

    def create_widgets(self):
        """Create widgets"""
        button_frame = ttk.Frame(self, padding=(20, 10, 20, 10))
        button_frame.pack(fill=tk.X, side=tk.TOP)

        ttk.Button(button_frame, text="Cancel", bootstyle="secondary",
                 command=self.destroy).pack(side=tk.RIGHT, padx=(10,0))
        ttk.Button(button_frame, text="Update Stock", bootstyle="success",
                 command=self.update_stock).pack(side=tk.RIGHT)

        frame = ttk.Frame(self, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)

        # Display current info
        ttk.Label(frame, text=f"Container: {self.container_type.get('name', '')}",
                 font=('Arial', 12, 'bold')).pack(anchor='w', pady=(0,5))
        ttk.Label(frame, text=f"Size: {self.container_type.get('size_litres', 0):.1f}L",
                 font=('Arial', 10)).pack(anchor='w', pady=(0,5))
        ttk.Label(frame, text=f"Current Stock: {self.container_type.get('quantity_available', 0)} units",
                 font=('Arial', 10)).pack(anchor='w', pady=(0,20))

        ttk.Label(frame, text="Adjustment Type:", font=('Arial', 10, 'bold')).pack(anchor='w', pady=(0,5))
        self.adjustment_var = tk.StringVar(value='set')
        ttk.Radiobutton(frame, text="Set to exact amount", variable=self.adjustment_var,
                       value='set').pack(anchor='w')
        ttk.Radiobutton(frame, text="Add to current stock", variable=self.adjustment_var,
                       value='add').pack(anchor='w')
        ttk.Radiobutton(frame, text="Subtract from current stock", variable=self.adjustment_var,
                       value='subtract').pack(anchor='w', pady=(0,15))

        ttk.Label(frame, text="Quantity:", font=('Arial', 10, 'bold')).pack(anchor='w', pady=(0,5))
        self.qty_entry = ttk.Entry(frame, font=('Arial', 11), width=15)
        self.qty_entry.pack(anchor='w', pady=(0,20))
        self.qty_entry.insert(0, str(self.container_type.get('quantity_available', 0)))
        self.qty_entry.focus()


    def update_stock(self):
        """Update stock level"""
        try:
            qty = int(self.qty_entry.get())
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number.")
            return

        current_stock = self.container_type.get('quantity_available', 0)
        adjustment_type = self.adjustment_var.get()

        if adjustment_type == 'set':
            new_stock = qty
        elif adjustment_type == 'add':
            new_stock = current_stock + qty
        else:  # subtract
            new_stock = current_stock - qty

        if new_stock < 0:
            messagebox.showerror("Error", "Stock cannot be negative.")
            return

        self.cache.connect()
        self.cache.update_record('container_types', self.container_type['container_type_id'], {
            'quantity_available': new_stock,
            'last_modified': datetime.now().isoformat(),
            'sync_status': 'pending'
        }, 'container_type_id')
        self.cache.close()

        messagebox.showinfo("Success", f"Stock updated to {new_stock} units")
        self.destroy()


class InventoryLogbookDialog(tk.Toplevel):
    """Dialog for viewing inventory transaction history"""

    def __init__(self, parent, cache_manager, current_user):
        super().__init__(parent)
        self.cache = cache_manager
        self.current_user = current_user
        self.current_category = 'all'  # Track selected category

        self.title("Inventory Logbook - Transaction History")
        self.transient(parent)
        self.grab_set()

        # Use window manager for sizing if available
        wm = get_window_manager()
        if wm:
            wm.setup_dialog(self, 'logbook_dialog', width_pct=0.7, height_pct=0.75,
                          add_grip=True, save_on_close=True, resizable=True)
        else:
            self.geometry("1000x700")
            self.resizable(True, True)

        self.create_widgets()
        self.load_transactions()

    def create_widgets(self):
        """Create dialog widgets"""
        # Buttons (Top)
        button_frame = ttk.Frame(self, padding=(20, 10))
        button_frame.pack(fill=tk.X, side=tk.TOP)

        ttk.Button(button_frame, text="Close", bootstyle="secondary",
                  command=self.destroy).pack(side=tk.RIGHT)

        frame = ttk.Frame(self, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)

        # Header
        ttk.Label(frame, text="Inventory Transaction History",
                 font=('Arial', 14, 'bold')).pack(pady=(0, 10))

        # Category tabs/buttons
        category_frame = ttk.Frame(frame)
        category_frame.pack(fill=tk.X, pady=(0, 10))

        categories = [
            ('All', 'all'),
            ('Grain', 'grain'),
            ('Hops', 'hops'),
            ('Yeast', 'yeast'),
            ('Adjunct', 'adjunct'),
            ('Sundries', 'sundries'),
            ('Containers', 'containers')
        ]

        self.category_buttons = {}
        for label, cat_id in categories:
            btn = ttk.Button(
                category_frame,
                text=label,
                bootstyle="secondary",
                cursor='hand2',
                command=lambda c=cat_id: self.switch_category(c)
            )
            btn.pack(side=tk.LEFT, padx=(0, 5))
            self.category_buttons[cat_id] = btn

        # Highlight "All" button by default
        self.category_buttons['all'].configure(bootstyle="success")

        # Filter frame (two filters side by side)
        filter_frame = ttk.Frame(frame)
        filter_frame.pack(fill=tk.X, pady=(0, 10))

        # Transaction type filter
        ttk.Label(filter_frame, text="Transaction Type:", font=('Arial', 10)).pack(side=tk.LEFT, padx=(0, 5))
        self.trans_type_var = tk.StringVar(value='all')
        trans_type_combo = ttk.Combobox(filter_frame, textvariable=self.trans_type_var,
                                    values=['all', 'added', 'removed'],
                                    width=12, state='readonly')
        trans_type_combo.pack(side=tk.LEFT, padx=(0, 20))
        trans_type_combo.bind('<<ComboboxSelected>>', lambda e: self.load_transactions())

        # Material filter
        ttk.Label(filter_frame, text="Material:", font=('Arial', 10)).pack(side=tk.LEFT, padx=(0, 5))
        self.material_var = tk.StringVar(value='all')
        self.material_combo = ttk.Combobox(filter_frame, textvariable=self.material_var,
                                          width=25, state='readonly')
        self.material_combo.pack(side=tk.LEFT, padx=(0, 20))
        self.material_combo.bind('<<ComboboxSelected>>', lambda e: self.load_transactions())

        refresh_btn = ttk.Button(filter_frame, text="🔄 Refresh",
                                bootstyle="secondary",
                                command=self.load_transactions)
        refresh_btn.pack(side=tk.LEFT)

        print_txt_btn = ttk.Button(filter_frame, text="💾 Save TXT",
                                   bootstyle="info",
                                   cursor='hand2',
                                   command=self.save_txt_report)
        print_txt_btn.pack(side=tk.LEFT, padx=(10, 0))

        print_btn = ttk.Button(filter_frame, text="🖨️ Print",
                              bootstyle="success",
                              cursor='hand2',
                              command=self.print_report)
        print_btn.pack(side=tk.LEFT, padx=(5, 0))

        # Transactions list
        list_frame = ttk.Frame(frame, relief=tk.SOLID, borderwidth=1)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        vsb = ttk.Scrollbar(list_frame, orient="vertical")
        vsb.pack(side=tk.RIGHT, fill=tk.Y)

        columns = ('Date', 'Type', 'Material', 'Quantity Change', 'New Balance', 'Reference', 'User', 'Notes')
        self.tree = ttk.Treeview(list_frame, columns=columns, show='headings',
                                yscrollcommand=vsb.set)

        for col in columns:
            self.tree.heading(col, text=col, anchor='w')

        self.tree.column('Date', width=100)
        self.tree.column('Type', width=70)
        self.tree.column('Material', width=180)
        self.tree.column('Quantity Change', width=120)
        self.tree.column('New Balance', width=100)
        self.tree.column('Reference', width=150)
        self.tree.column('User', width=100)
        self.tree.column('Notes', width=200)

        self.tree.pack(fill=tk.BOTH, expand=True)
        vsb.config(command=self.tree.yview)

        enable_mousewheel_scrolling(self.tree)
        enable_treeview_keyboard_navigation(self.tree)

        # Tag configurations
        self.tree.tag_configure('add', background='#e8f5e9')  # Green for additions
        self.tree.tag_configure('remove', background='#ffebee')  # Red for removals

        # Close button

    def switch_category(self, category):
        """Switch to a different category"""
        self.current_category = category

        # Update button colors (highlight active)
        for cat, btn in self.category_buttons.items():
            if cat == category:
                btn.configure(bootstyle="success")
            else:
                btn.configure(bootstyle="secondary")

        # Update material filter options
        self.update_material_filter()

        # Reload transactions
        self.load_transactions()

    def update_material_filter(self):
        """Update the material filter dropdown based on current category"""
        self.cache.connect()

        if self.current_category == 'all':
            # Get all materials
            materials = self.cache.get_all_records('inventory_materials', order_by='material_name')
        else:
            # Get materials for this category
            materials = self.cache.get_all_records('inventory_materials',
                                                   f"material_type = '{self.current_category}'",
                                                   order_by='material_name')

        self.cache.close()

        # Build material list
        material_names = ['all'] + [m.get('material_name', '') for m in materials]

        # Update combobox
        self.material_combo['values'] = material_names
        self.material_var.set('all')  # Reset to 'all' when category changes

    def load_transactions(self):
        """Load transactions from database"""
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Build where clauses
        where_clauses = []

        # Filter by transaction type (added/removed)
        trans_type = self.trans_type_var.get()
        if trans_type != 'all':
            # Map 'added' to 'add' and 'removed' to 'remove' for database
            db_type = 'add' if trans_type == 'added' else 'remove'
            where_clauses.append(f"transaction_type = '{db_type}'")

        self.cache.connect()

        # Get all transactions
        where = ' AND '.join(where_clauses) if where_clauses else None
        transactions = self.cache.get_all_records('inventory_transactions', where,
                                                  order_by='transaction_date DESC, transaction_id DESC')

        # Now filter by category and material
        for trans in transactions:
            # Get material info
            material_name = 'Unknown'
            material_type = None
            material_id = trans.get('material_id')
            if material_id:
                materials = self.cache.get_all_records('inventory_materials',
                    f"material_id = '{material_id}'")
                if materials:
                    material_name = materials[0].get('material_name', 'Unknown')
                    material_type = materials[0].get('material_type', '')

            # Filter by category
            if self.current_category != 'all':
                if material_type != self.current_category:
                    continue

            # Filter by specific material
            if self.material_var.get() != 'all':
                if material_name != self.material_var.get():
                    continue

            # Format date
            date_str = trans.get('transaction_date', '')
            if date_str:
                try:
                    # Handle both date formats (YYYY-MM-DD and DD/MM/YYYY)
                    if '-' in date_str and len(date_str.split('-')[0]) == 4:
                        # Format is YYYY-MM-DD, convert to DD/MM/YYYY
                        parts = date_str.split('-')
                        date_str = f"{parts[2]}/{parts[1]}/{parts[0]}"
                except:
                    pass  # Keep original if conversion fails

            trans_type_display = trans.get('transaction_type', '').capitalize()
            # Change 'Add' to 'Added' and 'Remove' to 'Removed'
            if trans_type_display == 'Add':
                trans_type_display = 'Added'
            elif trans_type_display == 'Remove':
                trans_type_display = 'Removed'

            quantity_change = trans.get('quantity_change', 0)
            new_balance = trans.get('new_balance', 0)
            reference = trans.get('reference', '')
            username = trans.get('username', '')
            notes = trans.get('notes', '')

            values = (
                date_str,
                trans_type_display,
                material_name,
                f"{quantity_change:+.1f}",  # Show + or - sign
                f"{new_balance:.1f}",
                reference,
                username,
                notes
            )

            tag = trans.get('transaction_type', 'add')
            self.tree.insert('', 'end', values=values, tags=(tag,))

        self.cache.close()

    def save_txt_report(self):
        """Save report to TXT file"""
        from tkinter import filedialog

        # Build report header
        report_lines = []
        report_lines.append("=" * 100)
        report_lines.append("INVENTORY TRANSACTION HISTORY REPORT")
        report_lines.append("=" * 100)
        report_lines.append(f"Generated: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        report_lines.append("")

        # Show active filters
        category_name = self.current_category.capitalize() if self.current_category != 'all' else 'All Categories'
        trans_type = self.trans_type_var.get().capitalize() if self.trans_type_var.get() != 'all' else 'All Types'
        material = self.material_var.get() if self.material_var.get() != 'all' else 'All Materials'

        report_lines.append(f"Category: {category_name}")
        report_lines.append(f"Transaction Type: {trans_type}")
        report_lines.append(f"Material: {material}")
        report_lines.append("=" * 100)
        report_lines.append("")

        # Get all items from tree
        items = self.tree.get_children()
        if not items:
            messagebox.showinfo("No Data", "No transactions to print with current filters.")
            return

        # Table header
        report_lines.append(f"{'Date':<12} {'Type':<8} {'Material':<25} {'Qty Change':<12} {'New Balance':<12} {'Reference':<20} {'User':<15}")
        report_lines.append("-" * 100)

        # Add each transaction
        for item in items:
            values = self.tree.item(item)['values']
            date, trans_type, material, qty_change, new_balance, reference, username, notes = values

            # Truncate long fields
            material = material[:24] if len(material) > 24 else material
            reference = reference[:19] if len(reference) > 19 else reference
            username = username[:14] if len(username) > 14 else username

            line = f"{date:<12} {trans_type:<8} {material:<25} {qty_change:<12} {new_balance:<12} {reference:<20} {username:<15}"
            report_lines.append(line)

            # Add notes if present
            if notes and notes.strip():
                report_lines.append(f"    Notes: {notes}")

        report_lines.append("")
        report_lines.append("=" * 100)
        report_lines.append(f"Total Transactions: {len(items)}")
        report_lines.append("=" * 100)

        # Save to file
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            initialfile=f"inventory_transactions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        )

        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(report_lines))
                messagebox.showinfo("Success", f"Report saved to:\n{filename}\n\nYou can now open and print this file.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save report:\n{str(e)}")

    def print_report(self):
        """Generate PDF report and open it for printing"""
        # Get all items from tree
        items = self.tree.get_children()
        if not items:
            messagebox.showinfo("No Data", "No transactions to print with current filters.")
            return

        # Build report data
        report_lines = []
        report_lines.append("INVENTORY TRANSACTION HISTORY REPORT")
        report_lines.append(f"Generated: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        report_lines.append("")

        # Show active filters
        category_name = self.current_category.capitalize() if self.current_category != 'all' else 'All Categories'
        trans_type = self.trans_type_var.get().capitalize() if self.trans_type_var.get() != 'all' else 'All Types'
        material = self.material_var.get() if self.material_var.get() != 'all' else 'All Materials'

        report_lines.append(f"Category: {category_name}")
        report_lines.append(f"Transaction Type: {trans_type}")
        report_lines.append(f"Material: {material}")
        report_lines.append("")
        report_lines.append(f"{'Date':<12} {'Type':<8} {'Material':<25} {'Qty Change':<12} {'New Balance':<12} {'Reference':<20} {'User':<15}")
        report_lines.append("-" * 115)

        # Add each transaction
        for item in items:
            values = self.tree.item(item)['values']
            date, trans_type, material, qty_change, new_balance, reference, username, notes = values

            # Truncate long fields
            material = material[:24] if len(material) > 24 else material
            reference = reference[:19] if len(reference) > 19 else reference
            username = username[:14] if len(username) > 14 else username

            line = f"{date:<12} {trans_type:<8} {material:<25} {qty_change:<12} {new_balance:<12} {reference:<20} {username:<15}"
            report_lines.append(line)

            # Add notes if present
            if notes and notes.strip():
                report_lines.append(f"    Notes: {notes}")

        report_lines.append("")
        report_lines.append(f"Total Transactions: {len(items)}")

        # Generate PDF
        try:
            # Create reports directory if it doesn't exist
            reports_dir = os.path.expanduser('~/.brewerymanager/reports')
            os.makedirs(reports_dir, exist_ok=True)

            # Generate filename with timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            category_suffix = self.current_category if self.current_category != 'all' else 'all'
            pdf_filename = os.path.join(reports_dir, f"logbook_report_{category_suffix}_{timestamp}.pdf")

            # Create PDF
            c = canvas.Canvas(pdf_filename, pagesize=A4)
            width, height = A4

            # Use Courier (monospace) for table alignment
            c.setFont("Courier", 8)

            # Starting position
            y_position = height - 40
            line_height = 12

            # Draw each line
            for line in report_lines:
                if y_position < 40:  # New page if near bottom
                    c.showPage()
                    c.setFont("Courier", 8)
                    y_position = height - 40

                c.drawString(40, y_position, line)
                y_position -= line_height

            # Save PDF
            c.save()

            # Open PDF in default viewer (like label printing)
            os.startfile(pdf_filename)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate PDF:\n{str(e)}")
