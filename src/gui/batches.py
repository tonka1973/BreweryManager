"""
Batches Module for Brewery Management System
Tracks batch production with gyle numbers and full traceability

REFACTORED WORKFLOW:
- New batches start as 'fermenting' with O.G. recorded
- Package button moves to 'packaged' status, records F.G., calculates ABV
- Only two statuses: fermenting | packaged
"""

import tkinter as tk
from tkinter import messagebox
import ttkbootstrap as ttk
import uuid
from datetime import datetime
from ..utilities.date_utils import format_date_for_display, parse_display_date, get_today_display, get_today_db, get_now_db
from ..utilities.window_manager import get_window_manager
from ..utilities.calculations import calculate_abv_from_gravity


class BatchesModule(ttk.Frame):
    """Batches module for production tracking"""

    def __init__(self, parent, cache_manager, current_user):
        super().__init__(parent)
        self.cache = cache_manager
        self.current_user = current_user

        self.create_widgets()
        self.load_batches()

    def create_widgets(self):
        """Create batch widgets"""
        # Toolbar
        toolbar = ttk.Frame(self)
        toolbar.pack(fill=tk.X, padx=20, pady=(0, 10))

        add_btn = ttk.Button(toolbar, text="➕ New Batch",
                            bootstyle="success",
                            command=self.add_batch)
        add_btn.pack(side=tk.LEFT, padx=(0, 10))

        edit_btn = ttk.Button(toolbar, text="✏️ Edit",
                             bootstyle="info",
                             command=self.edit_batch)
        edit_btn.pack(side=tk.LEFT, padx=(0, 10))

        package_btn = ttk.Button(toolbar, text="📦 Package",
                                bootstyle="warning",
                                command=self.package_batch)
        package_btn.pack(side=tk.LEFT, padx=(0, 10))

        # Filter by status
        ttk.Label(toolbar, text="Status:").pack(side=tk.RIGHT, padx=(0,5))
        self.filter_var = tk.StringVar(value='all')
        self.filter_var.trace('w', lambda *args: self.load_batches())
        filter_menu = ttk.Combobox(toolbar, textvariable=self.filter_var,
                                   values=['all', 'fermenting', 'packaged'],
                                   width=12, state='readonly')
        filter_menu.pack(side=tk.RIGHT, padx=(10,0))

        # Batches list with 11 columns
        list_frame = ttk.Frame(self, relief=tk.SOLID, borderwidth=1)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))

        vsb = ttk.Scrollbar(list_frame, orient="vertical")
        vsb.pack(side=tk.RIGHT, fill=tk.Y)

        columns = ('Date Brewed', 'Recipe Name', 'Gyle', 'Batch Size', 'Exp. ABV',
                   'O.G.', 'F.G.', 'Actual ABV', 'Duty ABV', 'Status', 'Date Packaged')
        self.tree = ttk.Treeview(list_frame, columns=columns, show='headings', yscrollcommand=vsb.set)

        # Set column headings and widths
        self.tree.heading('Date Brewed', text='Date Brewed')
        self.tree.heading('Recipe Name', text='Recipe Name')
        self.tree.heading('Gyle', text='Gyle')
        self.tree.heading('Batch Size', text='Batch Size')
        self.tree.heading('Exp. ABV', text='Exp. A.B.V.')
        self.tree.heading('O.G.', text='O.G.')
        self.tree.heading('F.G.', text='F.G.')
        self.tree.heading('Actual ABV', text='Actual ABV')
        self.tree.heading('Duty ABV', text='Duty ABV')
        self.tree.heading('Status', text='Status')
        self.tree.heading('Date Packaged', text='Date Packaged')

        self.tree.column('Date Brewed', width=100)
        self.tree.column('Recipe Name', width=180)
        self.tree.column('Gyle', width=140)
        self.tree.column('Batch Size', width=100)
        self.tree.column('Exp. ABV', width=90)
        self.tree.column('O.G.', width=80)
        self.tree.column('F.G.', width=80)
        self.tree.column('Actual ABV', width=90)
        self.tree.column('Duty ABV', width=90)
        self.tree.column('Status', width=100)
        self.tree.column('Date Packaged', width=110)

        self.tree.pack(fill=tk.BOTH, expand=True)
        vsb.config(command=self.tree.yview)

        # Smart double-click: fermenting → edit, packaged → edit packaged
        self.tree.bind('<Double-1>', lambda e: self.on_double_click())

        # Tag configurations for status colors
        self.tree.tag_configure('status_fermenting', background='#fff3e0')
        self.tree.tag_configure('status_packaged', background='#e8f5e9')

    def on_double_click(self):
        """Handle double-click based on batch status"""
        selection = self.tree.selection()
        if not selection:
            return

        tags = self.tree.item(selection[0], 'tags')
        if 'status_fermenting' in tags:
            self.edit_batch()
        elif 'status_packaged' in tags:
            self.edit_packaged_batch()

    def load_batches(self):
        """Load batches from database"""
        for item in self.tree.get_children():
            self.tree.delete(item)

        status_filter = self.filter_var.get()
        where = None if status_filter == 'all' else f"status = '{status_filter}'"

        self.cache.connect()
        batches = self.cache.get_all_records('batches', where, 'brew_date DESC')

        for batch in batches:
            recipe_name = 'Unknown'
            expected_abv = None
            batch_size = batch.get('actual_batch_size', 0)

            if batch.get('recipe_id'):
                recipes = self.cache.get_all_records('recipes', f"recipe_id = '{batch['recipe_id']}'")
                if recipes:
                    recipe = recipes[0]
                    recipe_name = recipe.get('recipe_name', 'Unknown')
                    expected_abv = recipe.get('target_abv')
                    # Use recipe batch size if not overridden
                    if not batch_size:
                        batch_size = recipe.get('target_batch_size_litres', 0)

            # Format values
            og = batch.get('original_gravity')
            fg = batch.get('final_gravity')
            actual_abv = batch.get('actual_abv')
            duty_abv = batch.get('duty_abv')

            values = (
                format_date_for_display(batch.get('brew_date', '')) or 'N/A',
                recipe_name,
                batch.get('gyle_number', ''),
                f"{batch_size:.0f}L" if batch_size else 'N/A',
                f"{expected_abv:.1f}%" if expected_abv else 'N/A',
                f"{og:.3f}" if og else 'N/A',
                f"{fg:.3f}" if fg else 'N/A',
                f"{actual_abv:.1f}%" if actual_abv else 'N/A',
                f"{duty_abv:.1f}%" if duty_abv else 'N/A',
                batch.get('status', '').capitalize(),
                format_date_for_display(batch.get('packaged_date', '')) or 'N/A'
            )

            status = batch.get('status', 'unknown')
            self.tree.insert('', 'end', values=values, tags=(f'status_{status}', batch['batch_id']))

        self.cache.close()

    def add_batch(self):
        """Add new batch"""
        dialog = BatchDialog(self, self.cache, self.current_user, mode='add')
        self.wait_window(dialog)
        self.load_batches()

    def edit_batch(self):
        """Edit selected batch (fermenting only)"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a batch to edit.")
            return

        tags = self.tree.item(selection[0], 'tags')
        batch_id = tags[1] if len(tags) > 1 else None

        self.cache.connect()
        batches = self.cache.get_all_records('batches', f"batch_id = '{batch_id}'")
        self.cache.close()

        if batches:
            batch = batches[0]
            if batch['status'] == 'packaged':
                # Use specialized packaged edit dialog
                self.edit_packaged_batch()
            else:
                dialog = BatchDialog(self, self.cache, self.current_user, mode='edit', batch=batch)
                self.wait_window(dialog)
                self.load_batches()

    def package_batch(self):
        """Open package dialog for selected batch"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a batch to package.")
            return

        tags = self.tree.item(selection[0], 'tags')
        batch_id = tags[1] if len(tags) > 1 else None

        self.cache.connect()
        batches = self.cache.get_all_records('batches', f"batch_id = '{batch_id}'")
        self.cache.close()

        if batches:
            batch = batches[0]
            if batch['status'] != 'fermenting':
                messagebox.showwarning("Invalid Status",
                    "Only batches with status 'fermenting' can be packaged.")
                return

            dialog = PackageDialog(self, self.cache, self.current_user, batch)
            self.wait_window(dialog)
            self.load_batches()

    def edit_packaged_batch(self):
        """Open edit dialog for packaged batch"""
        selection = self.tree.selection()
        if not selection:
            return

        tags = self.tree.item(selection[0], 'tags')
        batch_id = tags[1] if len(tags) > 1 else None

        self.cache.connect()
        batches = self.cache.get_all_records('batches', f"batch_id = '{batch_id}'")
        self.cache.close()

        if batches:
            dialog = EditPackagedBatchDialog(self, self.cache, self.current_user, batches[0])
            self.wait_window(dialog)
            self.load_batches()


class BatchDialog(tk.Toplevel):
    """Dialog for adding/editing fermenting batches"""

    def __init__(self, parent, cache_manager, current_user, mode='add', batch=None):
        super().__init__(parent)
        self.cache = cache_manager
        self.current_user = current_user
        self.mode = mode
        self.batch = batch

        self.title("New Batch" if mode == 'add' else "Edit Batch")
        self.transient(parent)
        self.grab_set()

        # Use window manager for sizing if available
        wm = get_window_manager()
        if wm:
            wm.setup_dialog(self, 'batch_dialog', width_pct=0.4, height_pct=0.55,
                          add_grip=True, save_on_close=True, resizable=True)
        else:
            self.geometry("600x500")
            self.resizable(True, True)

        self.create_widgets()
        if mode == 'edit' and batch:
            self.populate_fields()

    def create_widgets(self):
        """Create widgets"""
        frame = ttk.Frame(self, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)

        # Recipe selection with enhanced format
        ttk.Label(frame, text="Recipe *", font=('Arial', 10, 'bold')).grid(row=0, column=0, sticky='w', pady=(0,5))
        self.recipe_var = tk.StringVar()
        self.cache.connect()
        recipes = self.cache.get_all_records('recipes', 'is_active = 1', 'recipe_name')
        self.cache.close()

        # Format: "Recipe Name - ABV% - vX.X - Volume L"
        self.recipe_dict = {}
        recipe_display_list = []
        for r in recipes:
            abv = r.get('target_abv', 0)
            version = r.get('version', 1)
            volume = r.get('target_batch_size_litres', 0)
            display = f"{r['recipe_name']} - {abv:.1f}% - v{version} - {volume:.0f}L"
            recipe_display_list.append(display)
            self.recipe_dict[display] = r

        recipe_menu = ttk.Combobox(frame, textvariable=self.recipe_var,
                                   values=recipe_display_list, width=50, state='readonly')
        recipe_menu.grid(row=1, column=0, columnspan=2, sticky='ew', pady=(0,15))
        recipe_menu.bind('<<ComboboxSelected>>', self.on_recipe_selected)

        # Gyle Number
        ttk.Label(frame, text="Gyle Number *", font=('Arial', 10, 'bold')).grid(row=2, column=0, sticky='w', pady=(0,5))
        self.gyle_entry = ttk.Entry(frame, font=('Arial', 10), width=20)
        if self.mode == 'add':
            self.gyle_entry.insert(0, self.generate_gyle_number())
        self.gyle_entry.grid(row=3, column=0, sticky='w', pady=(0,15))

        # Brew Date
        ttk.Label(frame, text="Brew Date (DD/MM/YYYY) *", font=('Arial', 10, 'bold')).grid(row=2, column=1, sticky='w', pady=(0,5), padx=(20,0))
        self.brew_date_entry = ttk.Entry(frame, font=('Arial', 10), width=15)
        self.brew_date_entry.insert(0, get_today_display())
        self.brew_date_entry.grid(row=3, column=1, sticky='w', pady=(0,15), padx=(20,0))

        # Brewer Name
        ttk.Label(frame, text="Brewer Name *", font=('Arial', 10, 'bold')).grid(row=4, column=0, sticky='w', pady=(0,5))
        self.brewer_entry = ttk.Entry(frame, font=('Arial', 10), width=20)
        self.brewer_entry.insert(0, self.current_user.full_name)
        self.brewer_entry.grid(row=5, column=0, sticky='w', pady=(0,15))

        # Original Gravity (O.G.) - REQUIRED
        ttk.Label(frame, text="Original Gravity (O.G.) *", font=('Arial', 10, 'bold')).grid(row=4, column=1, sticky='w', pady=(0,5), padx=(20,0))
        self.og_entry = ttk.Entry(frame, font=('Arial', 10), width=15)
        self.og_entry.grid(row=5, column=1, sticky='w', pady=(0,15), padx=(20,0))

        # Brewing Notes
        ttk.Label(frame, text="Brewing Notes", font=('Arial', 10, 'bold')).grid(row=6, column=0, sticky='w', pady=(0,5))
        self.notes_text = tk.Text(frame, font=('Arial', 10), width=50, height=6)
        self.notes_text.grid(row=7, column=0, columnspan=2, sticky='ew', pady=(0,15))

        frame.grid_columnconfigure(0, weight=1)
        frame.grid_columnconfigure(1, weight=1)

        # Buttons
        button_frame = ttk.Frame(self, padding=10)
        button_frame.pack(fill=tk.X, padx=20, pady=(0,20))

        ttk.Button(button_frame, text="Cancel", bootstyle="secondary",
                  command=self.destroy).pack(side=tk.RIGHT, padx=(10,0))
        ttk.Button(button_frame, text="Save Batch", bootstyle="success",
                  command=self.save).pack(side=tk.RIGHT)

    def on_recipe_selected(self, event=None):
        """Handle recipe selection - no batch size needed anymore"""
        pass

    def generate_gyle_number(self):
        """Generate next gyle number"""
        year = datetime.now().year
        self.cache.connect()
        batches = self.cache.get_all_records('batches', f"gyle_number LIKE 'GYLE-{year}-%'")
        self.cache.close()
        next_num = len(batches) + 1
        return f"GYLE-{year}-{next_num:03d}"

    def populate_fields(self):
        """Populate fields with batch data"""
        if self.batch.get('recipe_id'):
            self.cache.connect()
            recipes = self.cache.get_all_records('recipes', f"recipe_id = '{self.batch['recipe_id']}'")
            self.cache.close()
            if recipes:
                r = recipes[0]
                abv = r.get('target_abv', 0)
                version = r.get('version', 1)
                volume = r.get('target_batch_size_litres', 0)
                display = f"{r['recipe_name']} - {abv:.1f}% - v{version} - {volume:.0f}L"
                self.recipe_var.set(display)

        self.gyle_entry.delete(0, tk.END)
        self.gyle_entry.insert(0, self.batch.get('gyle_number', ''))
        self.brew_date_entry.delete(0, tk.END)
        self.brew_date_entry.insert(0, format_date_for_display(self.batch.get('brew_date', '')))
        self.brewer_entry.delete(0, tk.END)
        self.brewer_entry.insert(0, self.batch.get('brewer_name', ''))

        if self.batch.get('original_gravity'):
            self.og_entry.insert(0, str(self.batch['original_gravity']))

        if self.batch.get('brewing_notes'):
            self.notes_text.insert('1.0', self.batch['brewing_notes'])

    def save(self):
        """Save batch"""
        recipe_display = self.recipe_var.get()
        if not recipe_display or recipe_display not in self.recipe_dict:
            messagebox.showerror("Error", "Please select a recipe.")
            return

        recipe = self.recipe_dict[recipe_display]

        gyle = self.gyle_entry.get().strip()
        if not gyle:
            messagebox.showerror("Error", "Gyle number is required.")
            return

        # O.G. is REQUIRED
        og_str = self.og_entry.get().strip()
        if not og_str:
            messagebox.showerror("Error", "Original Gravity (O.G.) is required.")
            return

        try:
            og = float(og_str)
            if og < 1.0 or og > 1.200:
                messagebox.showerror("Error", "O.G. should be between 1.000 and 1.200")
                return
        except ValueError:
            messagebox.showerror("Error", "Invalid O.G. format. Example: 1.045")
            return

        # Convert date
        brew_date_db = parse_display_date(self.brew_date_entry.get())
        if not brew_date_db:
            messagebox.showerror("Error", "Invalid date format. Please use DD/MM/YYYY.")
            return

        # Pull batch size and expected ABV from recipe
        batch_size = recipe.get('target_batch_size_litres', 0)
        expected_abv = recipe.get('target_abv', 0)

        data = {
            'recipe_id': recipe['recipe_id'],
            'gyle_number': gyle,
            'brew_date': brew_date_db,
            'brewer_name': self.brewer_entry.get().strip(),
            'actual_batch_size': batch_size,
            'original_gravity': og,
            'status': 'fermenting',  # Always fermenting for new/edited batches
            'brewing_notes': self.notes_text.get('1.0', tk.END).strip(),
            'last_modified': get_now_db(),
            'created_by': self.current_user.username,
            'sync_status': 'pending'
        }

        self.cache.connect()
        if self.mode == 'add':
            data['batch_id'] = str(uuid.uuid4())
            self.cache.insert_record('batches', data)
        else:
            self.cache.update_record('batches', self.batch['batch_id'], data, 'batch_id')
        self.cache.close()

        messagebox.showinfo("Success", "Batch saved!")
        self.destroy()


class PackageDialog(tk.Toplevel):
    """Dialog for packaging a fermented batch"""

    def __init__(self, parent, cache_manager, current_user, batch):
        super().__init__(parent)
        self.cache = cache_manager
        self.current_user = current_user
        self.batch = batch
        self.selected_containers = []  # List of {type, name, qty, volume, id}

        self.title(f"Package Batch: {batch.get('gyle_number', 'Unknown')}")
        self.transient(parent)
        self.grab_set()

        wm = get_window_manager()
        if wm:
            wm.setup_dialog(self, 'package_dialog', width_pct=0.5, height_pct=0.7,
                          add_grip=True, save_on_close=True, resizable=True)
        else:
            self.geometry("700x700")
            self.resizable(True, True)

        self.create_widgets()

    def create_widgets(self):
        """Create widgets"""
        frame = ttk.Frame(self, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)

        # Header - Read-only batch info
        header_frame = ttk.LabelFrame(frame, text="Batch Information", padding=15)
        header_frame.pack(fill=tk.X, pady=(0,20))

        # Get recipe info
        recipe_name = "Unknown"
        if self.batch.get('recipe_id'):
            self.cache.connect()
            recipes = self.cache.get_all_records('recipes', f"recipe_id = '{self.batch['recipe_id']}'")
            self.cache.close()
            if recipes:
                recipe_name = recipes[0]['recipe_name']

        info_text = f"""Gyle: {self.batch.get('gyle_number', 'N/A')}
Recipe: {recipe_name}
Brew Date: {format_date_for_display(self.batch.get('brew_date', ''))}
Batch Size: {self.batch.get('actual_batch_size', 0):.0f}L
O.G.: {self.batch.get('original_gravity', 0):.3f}"""

        ttk.Label(header_frame, text=info_text, font=('Arial', 10), justify=tk.LEFT).pack(anchor='w')

        # Date Packaged
        date_frame = ttk.Frame(frame)
        date_frame.pack(fill=tk.X, pady=(0,15))
        ttk.Label(date_frame, text="Date Packaged (DD/MM/YYYY) *", font=('Arial', 10, 'bold')).pack(anchor='w', pady=(0,5))
        self.package_date_entry = ttk.Entry(date_frame, font=('Arial', 10), width=15)
        self.package_date_entry.insert(0, get_today_display())
        self.package_date_entry.pack(anchor='w')

        # Final Gravity
        fg_frame = ttk.Frame(frame)
        fg_frame.pack(fill=tk.X, pady=(0,20))
        ttk.Label(fg_frame, text="Final Gravity (F.G.) *", font=('Arial', 10, 'bold')).pack(anchor='w', pady=(0,5))
        self.fg_entry = ttk.Entry(fg_frame, font=('Arial', 10), width=15)
        self.fg_entry.pack(anchor='w')

        # Containers Section
        container_frame = ttk.LabelFrame(frame, text="Containers", padding=15)
        container_frame.pack(fill=tk.BOTH, expand=True, pady=(0,10))

        # Container selection
        select_frame = ttk.Frame(container_frame)
        select_frame.pack(fill=tk.X, pady=(0,10))

        ttk.Label(select_frame, text="Container Type:", font=('Arial', 10, 'bold')).grid(row=0, column=0, sticky='w', pady=(0,5))

        # TODO: Load from brewery_inventory table when containers module is implemented
        # For now, placeholder with common container types
        self.container_var = tk.StringVar()
        self.container_options = {
            "Firkin (40.9L)": {"name": "Firkin", "volume": 40.9, "stock": 999},
            "Kilderkin (82L)": {"name": "Kilderkin", "volume": 82, "stock": 999},
            "Pin (20.5L)": {"name": "Pin", "volume": 20.5, "stock": 999},
            "Barrel (164L)": {"name": "Barrel", "volume": 164, "stock": 999}
        }

        container_menu = ttk.Combobox(select_frame, textvariable=self.container_var,
                                     values=list(self.container_options.keys()),
                                     width=30, state='readonly')
        container_menu.grid(row=1, column=0, sticky='w', pady=(0,10))

        ttk.Label(select_frame, text="Quantity:", font=('Arial', 10, 'bold')).grid(row=0, column=1, sticky='w', padx=(20,0), pady=(0,5))
        self.qty_entry = ttk.Entry(select_frame, font=('Arial', 10), width=10)
        self.qty_entry.grid(row=1, column=1, sticky='w', padx=(20,0), pady=(0,10))

        ttk.Button(select_frame, text="Add Container", bootstyle="success",
                  command=self.add_container).grid(row=1, column=2, padx=(20,0))

        # Container list
        list_frame = ttk.Frame(container_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)

        # Scrollbar for list
        vsb = ttk.Scrollbar(list_frame, orient="vertical")
        vsb.pack(side=tk.RIGHT, fill=tk.Y)

        cols = ('Qty', 'Type', 'Unit Vol', 'Total Vol', 'Action')
        self.container_tree = ttk.Treeview(list_frame, columns=cols, show='headings',
                                          height=5, yscrollcommand=vsb.set)

        self.container_tree.heading('Qty', text='Qty')
        self.container_tree.heading('Type', text='Type')
        self.container_tree.heading('Unit Vol', text='Unit Vol')
        self.container_tree.heading('Total Vol', text='Total Vol')
        self.container_tree.heading('Action', text='')

        self.container_tree.column('Qty', width=60)
        self.container_tree.column('Type', width=150)
        self.container_tree.column('Unit Vol', width=100)
        self.container_tree.column('Total Vol', width=100)
        self.container_tree.column('Action', width=80)

        self.container_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb.config(command=self.container_tree.yview)

        # Total label
        self.total_label = ttk.Label(container_frame, text="Total: 0L", font=('Arial', 12, 'bold'))
        self.total_label.pack(pady=(10,0))

        # Bind remove action
        self.container_tree.bind('<Button-1>', self.on_tree_click)

        # Buttons
        button_frame = ttk.Frame(self, padding=10)
        button_frame.pack(fill=tk.X, padx=20, pady=(0,20))

        ttk.Button(button_frame, text="Cancel", bootstyle="secondary",
                  command=self.destroy).pack(side=tk.RIGHT, padx=(10,0))
        ttk.Button(button_frame, text="Save & Package", bootstyle="success",
                  command=self.save).pack(side=tk.RIGHT)

    def add_container(self):
        """Add selected container to list"""
        container_display = self.container_var.get()
        if not container_display:
            messagebox.showwarning("No Selection", "Please select a container type.")
            return

        try:
            qty = int(self.qty_entry.get().strip())
            if qty <= 0:
                raise ValueError()
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid quantity.")
            return

        container = self.container_options[container_display]

        # TODO: Check stock when brewery inventory implemented
        # if qty > container['stock']:
        #     messagebox.showerror("Insufficient Stock",
        #         f"Insufficient stock. Only {container['stock']} available.")
        #     return

        # Add to list
        unit_vol = container['volume']
        total_vol = qty * unit_vol

        item_id = self.container_tree.insert('', 'end', values=(
            qty,
            container['name'],
            f"{unit_vol:.1f}L",
            f"{total_vol:.1f}L",
            "[Remove]"
        ))

        self.selected_containers.append({
            'item_id': item_id,
            'name': container['name'],
            'qty': qty,
            'volume': unit_vol,
            'total': total_vol
        })

        # Update total
        self.update_total()

        # Clear inputs
        self.container_var.set('')
        self.qty_entry.delete(0, tk.END)

    def on_tree_click(self, event):
        """Handle click on remove button"""
        region = self.container_tree.identify_region(event.x, event.y)
        if region == "cell":
            column = self.container_tree.identify_column(event.x)
            if column == '#5':  # Action column
                item = self.container_tree.identify_row(event.y)
                if item:
                    # Remove from tree and list
                    self.container_tree.delete(item)
                    self.selected_containers = [c for c in self.selected_containers if c['item_id'] != item]
                    self.update_total()

    def update_total(self):
        """Update total volume label"""
        total = sum(c['total'] for c in self.selected_containers)
        self.total_label.config(text=f"Total: {total:.1f}L")

    def save(self):
        """Save packaging information"""
        # Validate F.G.
        fg_str = self.fg_entry.get().strip()
        if not fg_str:
            messagebox.showerror("Error", "Final Gravity (F.G.) is required.")
            return

        try:
            fg = float(fg_str)
            if fg < 0.990 or fg > 1.100:
                messagebox.showerror("Error", "F.G. should be between 0.990 and 1.100")
                return
        except ValueError:
            messagebox.showerror("Error", "Invalid F.G. format. Example: 1.010")
            return

        # Validate date
        package_date_db = parse_display_date(self.package_date_entry.get())
        if not package_date_db:
            messagebox.showerror("Error", "Invalid date format. Please use DD/MM/YYYY.")
            return

        # Check package date not before brew date
        brew_date_db = self.batch.get('brew_date')
        if package_date_db < brew_date_db:
            brew_date_display = format_date_for_display(brew_date_db)
            messagebox.showerror("Invalid Date",
                f"Package date cannot be before brew date ({brew_date_display})")
            return

        # Validate containers selected
        if not self.selected_containers:
            messagebox.showerror("Error", "Please add at least one container.")
            return

        # TODO: Validate stock levels when brewery inventory implemented
        # for container in self.selected_containers:
        #     if container['qty'] > stock_level:
        #         messagebox.showerror("Insufficient Stock", ...)
        #         return

        # Calculate ABV
        og = self.batch.get('original_gravity')
        actual_abv = calculate_abv_from_gravity(og, fg)

        if actual_abv is None:
            messagebox.showerror("Error", "Could not calculate ABV. Check O.G. and F.G. values.")
            return

        # Get expected ABV from recipe
        expected_abv = 0
        if self.batch.get('recipe_id'):
            self.cache.connect()
            recipes = self.cache.get_all_records('recipes', f"recipe_id = '{self.batch['recipe_id']}'")
            self.cache.close()
            if recipes:
                expected_abv = recipes[0].get('target_abv', 0)

        # Duty ABV = higher of expected or actual
        duty_abv = max(expected_abv, actual_abv)

        # Update batch record
        data = {
            'final_gravity': fg,
            'actual_abv': actual_abv,
            'duty_abv': duty_abv,
            'packaged_date': package_date_db,
            'status': 'packaged',
            'last_modified': get_now_db(),
            'sync_status': 'pending'
        }

        self.cache.connect()
        self.cache.update_record('batches', self.batch['batch_id'], data, 'batch_id')

        # TODO: Deduct containers from brewery inventory when implemented
        # TODO: Add to finished goods inventory when table created
        # for container in self.selected_containers:
        #     self.cache.execute(f"UPDATE containers SET stock_level = stock_level - {container['qty']}")
        #     self.cache.insert_record('finished_goods', {
        #         'gyle_number': self.batch['gyle_number'],
        #         'container_type': container['name'],
        #         'quantity': container['qty'],
        #         'date_packaged': package_date_db
        #     })

        self.cache.close()

        messagebox.showinfo("Success",
            f"Batch packaged!\n\nActual ABV: {actual_abv:.2f}%\nDuty ABV: {duty_abv:.2f}%")
        self.destroy()


class EditPackagedBatchDialog(tk.Toplevel):
    """Dialog for editing an already-packaged batch"""

    def __init__(self, parent, cache_manager, current_user, batch):
        super().__init__(parent)
        self.cache = cache_manager
        self.current_user = current_user
        self.batch = batch
        self.selected_containers = []

        self.title(f"Edit Packaged Batch: {batch.get('gyle_number', 'Unknown')}")
        self.transient(parent)
        self.grab_set()

        wm = get_window_manager()
        if wm:
            wm.setup_dialog(self, 'edit_packaged_dialog', width_pct=0.5, height_pct=0.75,
                          add_grip=True, save_on_close=True, resizable=True)
        else:
            self.geometry("700x750")
            self.resizable(True, True)

        self.create_widgets()

    def create_widgets(self):
        """Create widgets"""
        frame = ttk.Frame(self, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)

        # Header - Read-only batch info
        header_frame = ttk.LabelFrame(frame, text="Batch Information (Read-Only)", padding=15)
        header_frame.pack(fill=tk.X, pady=(0,20))

        # Get recipe info
        recipe_name = "Unknown"
        if self.batch.get('recipe_id'):
            self.cache.connect()
            recipes = self.cache.get_all_records('recipes', f"recipe_id = '{self.batch['recipe_id']}'")
            self.cache.close()
            if recipes:
                recipe_name = recipes[0]['recipe_name']

        info_text = f"""Gyle: {self.batch.get('gyle_number', 'N/A')}
Recipe: {recipe_name}
Brew Date: {format_date_for_display(self.batch.get('brew_date', ''))}
Brewer: {self.batch.get('brewer_name', 'N/A')}
Batch Size: {self.batch.get('actual_batch_size', 0):.0f}L
Current O.G.: {self.batch.get('original_gravity', 0):.3f}
Current Actual ABV: {self.batch.get('actual_abv', 0):.2f}%
Current Duty ABV: {self.batch.get('duty_abv', 0):.2f}%"""

        ttk.Label(header_frame, text=info_text, font=('Arial', 10), justify=tk.LEFT).pack(anchor='w')

        # Editable: Date Packaged
        date_frame = ttk.Frame(frame)
        date_frame.pack(fill=tk.X, pady=(0,15))
        ttk.Label(date_frame, text="Date Packaged (DD/MM/YYYY) *", font=('Arial', 10, 'bold')).pack(anchor='w', pady=(0,5))
        self.package_date_entry = ttk.Entry(date_frame, font=('Arial', 10), width=15)
        current_date = format_date_for_display(self.batch.get('packaged_date', ''))
        self.package_date_entry.insert(0, current_date if current_date else get_today_display())
        self.package_date_entry.pack(anchor='w')

        # Editable: Final Gravity
        fg_frame = ttk.Frame(frame)
        fg_frame.pack(fill=tk.X, pady=(0,20))
        ttk.Label(fg_frame, text="Final Gravity (F.G.) *", font=('Arial', 10, 'bold')).pack(anchor='w', pady=(0,5))
        self.fg_entry = ttk.Entry(fg_frame, font=('Arial', 10), width=15)
        if self.batch.get('final_gravity'):
            self.fg_entry.insert(0, str(self.batch['final_gravity']))
        self.fg_entry.pack(anchor='w')

        # Containers Section (same as PackageDialog)
        container_frame = ttk.LabelFrame(frame, text="Containers (Re-select all)", padding=15)
        container_frame.pack(fill=tk.BOTH, expand=True, pady=(0,10))

        # Container selection
        select_frame = ttk.Frame(container_frame)
        select_frame.pack(fill=tk.X, pady=(0,10))

        ttk.Label(select_frame, text="Container Type:", font=('Arial', 10, 'bold')).grid(row=0, column=0, sticky='w', pady=(0,5))

        self.container_var = tk.StringVar()
        self.container_options = {
            "Firkin (40.9L)": {"name": "Firkin", "volume": 40.9, "stock": 999},
            "Kilderkin (82L)": {"name": "Kilderkin", "volume": 82, "stock": 999},
            "Pin (20.5L)": {"name": "Pin", "volume": 20.5, "stock": 999},
            "Barrel (164L)": {"name": "Barrel", "volume": 164, "stock": 999}
        }

        container_menu = ttk.Combobox(select_frame, textvariable=self.container_var,
                                     values=list(self.container_options.keys()),
                                     width=30, state='readonly')
        container_menu.grid(row=1, column=0, sticky='w', pady=(0,10))

        ttk.Label(select_frame, text="Quantity:", font=('Arial', 10, 'bold')).grid(row=0, column=1, sticky='w', padx=(20,0), pady=(0,5))
        self.qty_entry = ttk.Entry(select_frame, font=('Arial', 10), width=10)
        self.qty_entry.grid(row=1, column=1, sticky='w', padx=(20,0), pady=(0,10))

        ttk.Button(select_frame, text="Add Container", bootstyle="success",
                  command=self.add_container).grid(row=1, column=2, padx=(20,0))

        # Container list
        list_frame = ttk.Frame(container_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)

        vsb = ttk.Scrollbar(list_frame, orient="vertical")
        vsb.pack(side=tk.RIGHT, fill=tk.Y)

        cols = ('Qty', 'Type', 'Unit Vol', 'Total Vol', 'Action')
        self.container_tree = ttk.Treeview(list_frame, columns=cols, show='headings',
                                          height=5, yscrollcommand=vsb.set)

        self.container_tree.heading('Qty', text='Qty')
        self.container_tree.heading('Type', text='Type')
        self.container_tree.heading('Unit Vol', text='Unit Vol')
        self.container_tree.heading('Total Vol', text='Total Vol')
        self.container_tree.heading('Action', text='')

        self.container_tree.column('Qty', width=60)
        self.container_tree.column('Type', width=150)
        self.container_tree.column('Unit Vol', width=100)
        self.container_tree.column('Total Vol', width=100)
        self.container_tree.column('Action', width=80)

        self.container_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb.config(command=self.container_tree.yview)

        # Total label
        self.total_label = ttk.Label(container_frame, text="Total: 0L", font=('Arial', 12, 'bold'))
        self.total_label.pack(pady=(10,0))

        # Bind remove action
        self.container_tree.bind('<Button-1>', self.on_tree_click)

        # Note about transaction handling
        note_frame = ttk.Frame(frame)
        note_frame.pack(fill=tk.X, pady=(10,0))
        note_text = "Note: Saving will reverse the old container transactions and apply the new selection."
        ttk.Label(note_frame, text=note_text, font=('Arial', 9, 'italic'),
                 foreground='#666').pack(anchor='w')

        # Buttons
        button_frame = ttk.Frame(self, padding=10)
        button_frame.pack(fill=tk.X, padx=20, pady=(0,20))

        ttk.Button(button_frame, text="Cancel", bootstyle="secondary",
                  command=self.destroy).pack(side=tk.RIGHT, padx=(10,0))
        ttk.Button(button_frame, text="Save Changes", bootstyle="success",
                  command=self.save).pack(side=tk.RIGHT)

    def add_container(self):
        """Add selected container to list"""
        container_display = self.container_var.get()
        if not container_display:
            messagebox.showwarning("No Selection", "Please select a container type.")
            return

        try:
            qty = int(self.qty_entry.get().strip())
            if qty <= 0:
                raise ValueError()
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid quantity.")
            return

        container = self.container_options[container_display]

        unit_vol = container['volume']
        total_vol = qty * unit_vol

        item_id = self.container_tree.insert('', 'end', values=(
            qty,
            container['name'],
            f"{unit_vol:.1f}L",
            f"{total_vol:.1f}L",
            "[Remove]"
        ))

        self.selected_containers.append({
            'item_id': item_id,
            'name': container['name'],
            'qty': qty,
            'volume': unit_vol,
            'total': total_vol
        })

        self.update_total()

        # Clear inputs
        self.container_var.set('')
        self.qty_entry.delete(0, tk.END)

    def on_tree_click(self, event):
        """Handle click on remove button"""
        region = self.container_tree.identify_region(event.x, event.y)
        if region == "cell":
            column = self.container_tree.identify_column(event.x)
            if column == '#5':  # Action column
                item = self.container_tree.identify_row(event.y)
                if item:
                    self.container_tree.delete(item)
                    self.selected_containers = [c for c in self.selected_containers if c['item_id'] != item]
                    self.update_total()

    def update_total(self):
        """Update total volume label"""
        total = sum(c['total'] for c in self.selected_containers)
        self.total_label.config(text=f"Total: {total:.1f}L")

    def save(self):
        """Save changes with transaction reversal"""
        # Validate F.G.
        fg_str = self.fg_entry.get().strip()
        if not fg_str:
            messagebox.showerror("Error", "Final Gravity (F.G.) is required.")
            return

        try:
            fg = float(fg_str)
            if fg < 0.990 or fg > 1.100:
                messagebox.showerror("Error", "F.G. should be between 0.990 and 1.100")
                return
        except ValueError:
            messagebox.showerror("Error", "Invalid F.G. format. Example: 1.010")
            return

        # Validate date
        package_date_db = parse_display_date(self.package_date_entry.get())
        if not package_date_db:
            messagebox.showerror("Error", "Invalid date format. Please use DD/MM/YYYY.")
            return

        # Check package date not before brew date
        brew_date_db = self.batch.get('brew_date')
        if package_date_db < brew_date_db:
            brew_date_display = format_date_for_display(brew_date_db)
            messagebox.showerror("Invalid Date",
                f"Package date cannot be before brew date ({brew_date_display})")
            return

        # Validate containers selected
        if not self.selected_containers:
            messagebox.showerror("Error", "Please add at least one container.")
            return

        # Store old values for transaction reversal
        old_fg = self.batch.get('final_gravity')
        old_actual_abv = self.batch.get('actual_abv')
        # old_containers = get_old_containers_from_db(self.batch['batch_id'])  # TODO when finished_goods table exists

        # Calculate new ABV
        og = self.batch.get('original_gravity')
        new_actual_abv = calculate_abv_from_gravity(og, fg)

        if new_actual_abv is None:
            messagebox.showerror("Error", "Could not calculate ABV. Check O.G. and F.G. values.")
            return

        # Get expected ABV from recipe
        expected_abv = 0
        if self.batch.get('recipe_id'):
            self.cache.connect()
            recipes = self.cache.get_all_records('recipes', f"recipe_id = '{self.batch['recipe_id']}'")
            self.cache.close()
            if recipes:
                expected_abv = recipes[0].get('target_abv', 0)

        # New duty ABV
        new_duty_abv = max(expected_abv, new_actual_abv)

        # TODO: Transaction handling when brewery inventory and finished goods exist
        # 1. Reverse old container transactions (add back to brewery inventory)
        # 2. Delete old finished goods entries
        # 3. Deduct new containers from brewery inventory
        # 4. Insert new finished goods entries

        # Update batch record with new values
        data = {
            'final_gravity': fg,
            'actual_abv': new_actual_abv,
            'duty_abv': new_duty_abv,
            'packaged_date': package_date_db,
            'last_modified': get_now_db(),
            'sync_status': 'pending'
        }

        self.cache.connect()
        self.cache.update_record('batches', self.batch['batch_id'], data, 'batch_id')
        self.cache.close()

        messagebox.showinfo("Success",
            f"Batch updated!\n\nNew Actual ABV: {new_actual_abv:.2f}%\nNew Duty ABV: {new_duty_abv:.2f}%")
        self.destroy()
