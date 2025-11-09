"""
Inventory Module for Brewery Management System
Tracks brewing materials and finished goods inventory
"""

import tkinter as tk
from tkinter import ttk, messagebox
import uuid
from datetime import datetime
from ..utilities.date_utils import get_today_db


class InventoryModule(tk.Frame):
    """Inventory module for tracking materials and finished goods"""

    def __init__(self, parent, cache_manager, current_user):
        super().__init__(parent, bg='white')
        self.cache = cache_manager
        self.current_user = current_user
        self.current_category = 'all'  # Track selected category

        self.create_widgets()
        self.load_materials()

    def create_widgets(self):
        """Create inventory widgets"""
        # Category tabs/buttons
        category_frame = tk.Frame(self, bg='white')
        category_frame.pack(fill=tk.X, padx=20, pady=(0, 10))

        categories = [
            ('All', 'all'),
            ('Grain', 'grain'),
            ('Hops', 'hops'),
            ('Yeast', 'yeast'),
            ('Adjunct', 'adjunct'),
            ('Sundries', 'sundries')
        ]

        self.category_buttons = {}
        for label, cat_id in categories:
            btn = tk.Button(
                category_frame,
                text=label,
                font=('Arial', 10, 'bold'),
                bg='#34495e',
                fg='white',
                activebackground='#4CAF50',
                activeforeground='white',
                cursor='hand2',
                relief=tk.FLAT,
                bd=0,
                padx=15,
                pady=8,
                command=lambda c=cat_id: self.switch_category(c)
            )
            btn.pack(side=tk.LEFT, padx=(0, 5))
            self.category_buttons[cat_id] = btn

        # Highlight "All" button by default
        self.category_buttons['all'].config(bg='#4CAF50')

        # Toolbar
        toolbar = tk.Frame(self, bg='white')
        toolbar.pack(fill=tk.X, padx=20, pady=(10, 10))

        add_btn = tk.Button(toolbar, text="➕ Add Material", font=('Arial', 10, 'bold'),
                           bg='#4CAF50', fg='white', cursor='hand2',
                           command=self.add_material, padx=15, pady=8)
        add_btn.pack(side=tk.LEFT, padx=(0, 10))

        edit_btn = tk.Button(toolbar, text="✏️ Edit", font=('Arial', 10),
                            bg='#2196F3', fg='white', cursor='hand2',
                            command=self.edit_material, padx=15, pady=8)
        edit_btn.pack(side=tk.LEFT, padx=(0, 10))

        stock_btn = tk.Button(toolbar, text="📦 Adjust Stock", font=('Arial', 10),
                             bg='#FF9800', fg='white', cursor='hand2',
                             command=self.adjust_stock, padx=15, pady=8)
        stock_btn.pack(side=tk.LEFT, padx=(0, 10))

        delete_btn = tk.Button(toolbar, text="🗑️ Delete", font=('Arial', 10),
                              bg='#f44336', fg='white', cursor='hand2',
                              command=self.delete_material, padx=15, pady=8)
        delete_btn.pack(side=tk.LEFT, padx=(0, 10))

        refresh_btn = tk.Button(toolbar, text="🔄 Refresh", font=('Arial', 10),
                               bg='#607D8B', fg='white', cursor='hand2',
                               command=self.load_materials, padx=15, pady=8)
        refresh_btn.pack(side=tk.LEFT)

        # Materials list
        list_frame = tk.Frame(self, bg='white', relief=tk.SOLID, borderwidth=1)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))

        vsb = tk.Scrollbar(list_frame, orient="vertical")
        vsb.pack(side=tk.RIGHT, fill=tk.Y)

        columns = ('Material', 'Type', 'Stock', 'Unit', 'Reorder', 'Supplier', 'Cost/Unit')
        self.tree = ttk.Treeview(list_frame, columns=columns, show='headings',
                                yscrollcommand=vsb.set)

        for col in columns:
            self.tree.heading(col, text=col)

        self.tree.column('Material', width=200)
        self.tree.column('Type', width=100)
        self.tree.column('Stock', width=100)
        self.tree.column('Unit', width=80)
        self.tree.column('Reorder', width=100)
        self.tree.column('Supplier', width=150)
        self.tree.column('Cost/Unit', width=100)

        self.tree.pack(fill=tk.BOTH, expand=True)
        vsb.config(command=self.tree.yview)

    def switch_category(self, category):
        """Switch to a different category"""
        self.current_category = category

        # Update button colors (highlight active)
        for cat, btn in self.category_buttons.items():
            if cat == category:
                btn.config(bg='#4CAF50')
            else:
                btn.config(bg='#34495e')

        # Reload materials with filter
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

    def add_material(self):
        """Add new material"""
        dialog = MaterialDialog(self, self.cache, self.current_user, mode='add')
        self.wait_window(dialog)
        self.load_materials()

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

    def adjust_stock(self):
        """Adjust stock levels"""
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
            dialog = StockAdjustDialog(self, self.cache, self.current_user, materials[0])
            self.wait_window(dialog)
            self.load_materials()

    def delete_material(self):
        """Delete material"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a material.")
            return

        result = messagebox.askyesno("Confirm Delete", "Delete this material?")
        if result:
            tags = self.tree.item(selection[0], 'tags')
            material_id = tags[1] if len(tags) > 1 else None

            self.cache.connect()
            self.cache.delete_record('inventory_materials', material_id, 'material_id')
            self.cache.close()

            messagebox.showinfo("Success", "Material deleted.")
            self.load_materials()


class MaterialDialog(tk.Toplevel):
    """Dialog for adding/editing materials"""

    def __init__(self, parent, cache_manager, current_user, mode='add', material=None):
        super().__init__(parent)
        self.cache = cache_manager
        self.current_user = current_user
        self.mode = mode
        self.material = material

        self.title("Add Material" if mode == 'add' else "Edit Material")
        self.geometry("500x550")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        self.create_widgets()
        if mode == 'edit' and material:
            self.populate_fields()

    def create_widgets(self):
        """Create dialog widgets"""
        frame = tk.Frame(self, bg='white', padx=20, pady=20)
        frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(frame, text="Material Name *", font=('Arial', 10, 'bold'), bg='white').grid(row=0, column=0, sticky='w', pady=(0,5))
        self.name_entry = tk.Entry(frame, font=('Arial', 10), width=40)
        self.name_entry.grid(row=1, column=0, columnspan=2, sticky='ew', pady=(0,15))

        tk.Label(frame, text="Type *", font=('Arial', 10, 'bold'), bg='white').grid(row=2, column=0, sticky='w', pady=(0,5))
        self.type_var = tk.StringVar(value='grain')
        types = ['grain', 'hops', 'yeast', 'adjunct', 'sundries']
        type_menu = ttk.Combobox(frame, textvariable=self.type_var, values=types, font=('Arial', 10), width=37, state='readonly')
        type_menu.grid(row=3, column=0, columnspan=2, sticky='ew', pady=(0,15))

        tk.Label(frame, text="Current Stock *", font=('Arial', 10, 'bold'), bg='white').grid(row=4, column=0, sticky='w', pady=(0,5))
        self.stock_entry = tk.Entry(frame, font=('Arial', 10), width=15)
        self.stock_entry.grid(row=5, column=0, sticky='w', pady=(0,15))

        tk.Label(frame, text="Unit *", font=('Arial', 10, 'bold'), bg='white').grid(row=4, column=1, sticky='w', pady=(0,5), padx=(20,0))
        self.unit_entry = tk.Entry(frame, font=('Arial', 10), width=15)
        self.unit_entry.grid(row=5, column=1, sticky='w', pady=(0,15), padx=(20,0))

        tk.Label(frame, text="Reorder Level", font=('Arial', 10, 'bold'), bg='white').grid(row=6, column=0, sticky='w', pady=(0,5))
        self.reorder_entry = tk.Entry(frame, font=('Arial', 10), width=15)
        self.reorder_entry.grid(row=7, column=0, sticky='w', pady=(0,15))

        tk.Label(frame, text="Cost per Unit (£)", font=('Arial', 10, 'bold'), bg='white').grid(row=6, column=1, sticky='w', pady=(0,5), padx=(20,0))
        self.cost_entry = tk.Entry(frame, font=('Arial', 10), width=15)
        self.cost_entry.grid(row=7, column=1, sticky='w', pady=(0,15), padx=(20,0))

        tk.Label(frame, text="Supplier", font=('Arial', 10, 'bold'), bg='white').grid(row=8, column=0, sticky='w', pady=(0,5))
        self.supplier_entry = tk.Entry(frame, font=('Arial', 10), width=40)
        self.supplier_entry.grid(row=9, column=0, columnspan=2, sticky='ew', pady=(0,15))

        frame.grid_columnconfigure(0, weight=1)
        frame.grid_columnconfigure(1, weight=1)

        button_frame = tk.Frame(self, bg='white', pady=10)
        button_frame.pack(fill=tk.X, padx=20, pady=(0,20))

        tk.Button(button_frame, text="Cancel", font=('Arial', 10), bg='#757575', fg='white',
                 command=self.destroy, padx=20, pady=8).pack(side=tk.RIGHT, padx=(10,0))
        tk.Button(button_frame, text="Save", font=('Arial', 10, 'bold'), bg='#4CAF50', fg='white',
                 command=self.save, padx=20, pady=8).pack(side=tk.RIGHT)

    def populate_fields(self):
        """Populate fields with material data"""
        self.name_entry.insert(0, self.material.get('material_name', ''))
        self.type_var.set(self.material.get('material_type', 'grain'))
        self.stock_entry.insert(0, str(self.material.get('current_stock', '')))
        self.unit_entry.insert(0, self.material.get('unit', ''))
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
        self.geometry("400x350")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        self.create_widgets()

    def create_widgets(self):
        """Create widgets"""
        frame = tk.Frame(self, bg='white', padx=20, pady=20)
        frame.pack(fill=tk.BOTH, expand=True)

        current = self.material.get('current_stock', 0)
        tk.Label(frame, text=f"Current Stock: {current:.1f} {self.material.get('unit', '')}",
                font=('Arial', 12, 'bold'), bg='white').pack(pady=(0,20))

        tk.Label(frame, text="Adjustment Type", font=('Arial', 10, 'bold'), bg='white').pack(anchor='w', pady=(0,5))
        self.adj_type = tk.StringVar(value='add')
        tk.Radiobutton(frame, text="Add Stock", variable=self.adj_type, value='add', bg='white', font=('Arial', 10)).pack(anchor='w')
        tk.Radiobutton(frame, text="Remove Stock", variable=self.adj_type, value='remove', bg='white', font=('Arial', 10)).pack(anchor='w', pady=(0,15))

        tk.Label(frame, text="Quantity", font=('Arial', 10, 'bold'), bg='white').pack(anchor='w', pady=(0,5))
        self.qty_entry = tk.Entry(frame, font=('Arial', 11), width=15)
        self.qty_entry.pack(anchor='w', pady=(0,15))

        tk.Label(frame, text="Reason/Notes", font=('Arial', 10, 'bold'), bg='white').pack(anchor='w', pady=(0,5))
        self.notes_text = tk.Text(frame, font=('Arial', 10), width=40, height=4)
        self.notes_text.pack(pady=(0,15))

        button_frame = tk.Frame(self, bg='white', pady=10)
        button_frame.pack(fill=tk.X, padx=20)

        tk.Button(button_frame, text="Cancel", font=('Arial', 10), bg='#757575', fg='white',
                 command=self.destroy, padx=20, pady=8).pack(side=tk.RIGHT, padx=(10,0))
        tk.Button(button_frame, text="Apply", font=('Arial', 10, 'bold'), bg='#FF9800', fg='white',
                 command=self.apply_adjustment, padx=20, pady=8).pack(side=tk.RIGHT)

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
