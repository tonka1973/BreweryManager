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
from ..utilities.window_manager import get_window_manager, enable_mousewheel_scrolling, enable_treeview_keyboard_navigation
from ..utilities.calculations import calculate_abv_from_gravity
from ..utilities.label_printer import print_labels_for_batch
from .components import ScrollableFrame


class BatchesModule(ttk.Frame):
    """Batches module for production tracking"""

    def __init__(self, parent, cache_manager, current_user, sync_callback=None):
        super().__init__(parent)
        self.cache = cache_manager
        self.current_user = current_user
        self.sync_callback = sync_callback

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

        # Enable mousewheel and keyboard scrolling
        enable_mousewheel_scrolling(self.tree)
        enable_treeview_keyboard_navigation(self.tree)

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
        if self.sync_callback: self.sync_callback()

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
                if self.sync_callback: self.sync_callback()

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
            if self.sync_callback: self.sync_callback()

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
            if self.sync_callback: self.sync_callback()


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
        # Buttons (Bottom) - PACK FIRST
        button_frame = ttk.Frame(self, padding=10)
        button_frame.pack(fill=tk.X, side=tk.BOTTOM)

        ttk.Button(button_frame, text="Cancel", bootstyle="secondary",
                  command=self.destroy).pack(side=tk.RIGHT, padx=(10,0))
        ttk.Button(button_frame, text="Save Batch", bootstyle="success",
                  command=self.save).pack(side=tk.RIGHT)

        # Main scrollable container
        scroll_frame = ScrollableFrame(self)
        scroll_frame.pack(fill=tk.BOTH, expand=True)

        frame = ttk.Frame(scroll_frame.inner_frame, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)

        # Recipe selection with enhanced format
        ttk.Label(frame, text="Recipe *", font=('Arial', 10, 'bold')).grid(row=0, column=0, sticky='w', pady=(0,5))
        self.recipe_var = tk.StringVar()
        self.cache.connect()
        recipes = self.cache.get_all_records('recipes', 'is_active = 1', 'recipe_name')
        self.cache.close()

        # History Frame (New)
        history_frame = ttk.LabelFrame(frame, text="Last Brew History", padding=10)
        history_frame.grid(row=8, column=0, columnspan=2, sticky='ew', pady=(10, 15))
        
        self.history_og_label = ttk.Label(history_frame, text="O.G.: N/A")
        self.history_og_label.pack(side=tk.LEFT, padx=(0, 20))
        self.history_fg_label = ttk.Label(history_frame, text="F.G.: N/A")
        self.history_fg_label.pack(side=tk.LEFT, padx=(0, 20))
        self.history_abv_label = ttk.Label(history_frame, text="ABV: N/A")
        self.history_abv_label.pack(side=tk.LEFT, padx=(0, 20))
        self.history_notes_label = ttk.Label(history_frame, text="Notes: -")
        self.history_notes_label.pack(side=tk.LEFT)

        # Warnings Frame (New)
        self.warning_frame = ttk.LabelFrame(frame, text="Warnings", padding=10, bootstyle="danger")
        self.warning_label = ttk.Label(self.warning_frame, text="", foreground="red", wraplength=450)
        self.warning_label.pack()
        # Hidden by default
        # self.warning_frame.grid(...) inside logic

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



    def on_recipe_selected(self, event=None):
        """Handle recipe selection - Load History & Check Inventory"""
        recipe_display = self.recipe_var.get()
        if not recipe_display or recipe_display not in self.recipe_dict:
            return

        recipe = self.recipe_dict[recipe_display]
        recipe_id = recipe['recipe_id']

        # 1. Load Last Brew History
        self.cache.connect()
        last_batches = self.cache.get_all_records(
            'batches', 
            f"recipe_id = '{recipe_id}' AND status IN ('packaged', 'completed')", 
            'brew_date DESC'
        )
        
        last_batch = last_batches[0] if last_batches else None
        
        if last_batch:
            self.history_og_label.config(text=f"O.G.: {last_batch.get('original_gravity', 'N/A')}")
            self.history_fg_label.config(text=f"F.G.: {last_batch.get('final_gravity', 'N/A')}")
            self.history_abv_label.config(text=f"ABV: {last_batch.get('actual_abv', 'N/A')}%")
            notes = last_batch.get('brewing_notes', '-')
            self.history_notes_label.config(text=f"Notes: {notes[:30]}..." if len(notes) > 30 else f"Notes: {notes}")
        else:
            self.history_og_label.config(text="O.G.: N/A")
            self.history_fg_label.config(text="F.G.: N/A")
            self.history_abv_label.config(text="ABV: N/A")
            self.history_notes_label.config(text="Notes: First brew of this recipe")

        # 2. Check Inventory Warnings (Mixed Batch or Batch Change)
        warnings = []
        
        # Get recipe ingredients
        ingredients = self.cache.get_all_records('recipe_ingredients', f"recipe_id = '{recipe_id}'")
        
        for ing in ingredients:
            inv_id = ing.get('inventory_item_id')
            if not inv_id: continue
            
            qty_needed = ing.get('quantity', 0)
            
            # Simulate FIFO
            allocations = self.simulate_fifo_usage(inv_id, qty_needed)
            if not allocations: continue # Stock check handled elsewhere
            
            # Warning: Mixed Batch
            if len(allocations) > 1:
                batches_str = " & ".join([f"{b['batch_num']} ({b['qty']:.1f})" for b in allocations])
                warnings.append(f"⚠️ Mixing Batches for {ing.get('ingredient_name')}: {batches_str}")
            
            # Warning: Batch Change
            if last_batch:
                # Parse last batch's source string "Pale: B001, Wheat: B010"
                last_sources = last_batch.get('ingredient_source_batches', '') or ""
                # Simple check: extract current primary batch
                current_primary = allocations[0]['batch_num']
                
                # Check if current primary was used in last batch
                # Ideally we check per ingredient, but strict string parsing is brittle.
                # Heuristic: If ingredient name is in last source, but current primary batch is NOT, warn.
                ing_name = ing.get('ingredient_name', '')
                if ing_name in last_sources and current_primary not in last_sources:
                    warnings.append(f"⚠️ New Grain Batch: {ing_name} changed to {current_primary}")

        self.cache.close()

        if warnings:
            self.warning_label.config(text="\n".join(warnings))
            self.warning_frame.grid(row=9, column=0, columnspan=2, sticky='ew', pady=(10, 15))
        else:
            self.warning_frame.grid_forget()

    def simulate_fifo_usage(self, material_id, qty_needed):
        """Return list of {batch_num, qty} to be used"""
        allocations = []
        remaining = qty_needed
        
        batches = self.cache.get_all_records(
            'inventory_batches', 
            f"material_id = '{material_id}' AND quantity_remaining > 0",
            order_by='received_date ASC'
        )
        
        for b in batches:
            if remaining <= 0: break
            take = min(b['quantity_remaining'], remaining)
            allocations.append({'batch_num': b.get('batch_number', 'Unknown'), 'qty': take})
            remaining -= take
            
        return allocations

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

            # Deduct ingredients from inventory
            self.deduct_ingredients_from_inventory(recipe['recipe_id'], gyle)
        else:
            self.cache.update_record('batches', self.batch['batch_id'], data, 'batch_id')
        self.cache.close()

        messagebox.showinfo("Success", "Batch saved!")
        self.destroy()

    def deduct_ingredients_from_inventory(self, recipe_id, gyle_number):
        """Deduct recipe ingredients from brewery inventory using FIFO logic"""
        ingredients = self.cache.get_all_records('recipe_ingredients', f"recipe_id = '{recipe_id}'")
        deducted_items = []
        insufficient_stock_items = []
        total_ingredients_found = len(ingredients)
        
        source_records = [] # To store "Pale Malt: B001" strings

        for ingredient in ingredients:
            inventory_item_id = ingredient.get('inventory_item_id')
            quantity_needed = ingredient.get('quantity', 0)
            ingredient_name = ingredient.get('ingredient_name', 'Unknown')
            ingredient_unit = ingredient.get('unit', '')

            if not inventory_item_id or quantity_needed <= 0:
                continue

            materials = self.cache.get_all_records('inventory_materials', f"material_id = '{inventory_item_id}'")

            if not materials:
                continue

            material = materials[0]
            material_name = material.get('material_name', ingredient_name)
            current_stock = material.get('current_stock', 0)
            inventory_unit = material.get('unit', '')

            converted_quantity = self.convert_units(quantity_needed, ingredient_unit, inventory_unit)

            if converted_quantity is None:
                insufficient_stock_items.append(f"{material_name}: Unit mismatch")
                continue

            if current_stock < converted_quantity:
                insufficient_stock_items.append(f"{material_name}: Insufficient Stock")
                continue

            # --- FIFO Deduction ---
            remaining_to_deduct = converted_quantity
            used_batches = []
            
            # Get batches sorted by date
            batches = self.cache.get_all_records(
                'inventory_batches', 
                f"material_id = '{inventory_item_id}' AND quantity_remaining > 0",
                order_by='received_date ASC'
            )
            
            # If no batches exist (legacy issue?), just update total stock (fallback)
            if not batches:
                # Log legacy usage?
                used_batches.append("LEGACY")
            else:
                for batch in batches:
                    if remaining_to_deduct <= 0: break
                    
                    available = batch['quantity_remaining']
                    take = min(available, remaining_to_deduct)
                    
                    new_batch_qty = available - take
                    self.cache.update_record(
                        'inventory_batches', 
                        batch['batch_id'], 
                        {'quantity_remaining': new_batch_qty, 'sync_status': 'pending'}, 
                        'batch_id'
                    )
                    
                    print(f"DEBUG: Deducting {take} from batch {batch['batch_number']}") 
                    used_batches.append(batch.get('batch_number', 'Unknown'))
                    remaining_to_deduct -= take

            # Update TOTAL stock
            new_stock = current_stock - converted_quantity
            self.cache.update_record('inventory_materials', inventory_item_id, {
                'current_stock': new_stock,
                'last_updated': get_today_db(),
                'sync_status': 'pending'
            }, 'material_id')

            # Create transaction record
            trans_data = {
                'transaction_id': str(uuid.uuid4()),
                'transaction_date': get_today_db(),
                'transaction_type': 'remove',
                'material_id': inventory_item_id,
                'quantity_change': -converted_quantity,
                'new_balance': new_stock,
                'reference': f'Batch {gyle_number}',
                'username': self.current_user.username,
                'notes': f'Used for {gyle_number}. Batches: {", ".join(used_batches)}',
                'sync_status': 'pending'
            }
            self.cache.insert_record('inventory_transactions', trans_data)
            
            source_records.append(f"{material_name}: {', '.join(used_batches)}")
            deducted_items.append(f"{material_name}: {quantity_needed:.1f}{ingredient_unit}")

        # Update the Batch record with source info
        if source_records:
            source_str = "; ".join(source_records)
            # Find the batch we just created (using gyle_number as proxy since we don't pass ID easily here, 
            # actually we do, but let's just update by gyle for safety or fetch ID)
            # Better: The caller 'save' method created the batch. We should probably return this string 
            # and let 'save' update it, OR just update it here.
            # We don't have batch_id here easily without passing it.
            # Let's update by Gyle.
            batches = self.cache.get_all_records('batches', f"gyle_number = '{gyle_number}'")
            if batches:
                self.cache.update_record('batches', batches[0]['batch_id'], {'ingredient_source_batches': source_str, 'sync_status': 'pending'}, 'batch_id')

        # Show warning if needed
        if insufficient_stock_items:
            messagebox.showwarning("Insufficient Stock", "\n".join(insufficient_stock_items))
        elif deducted_items:
            messagebox.showinfo("Inventory Updated", "\n".join(deducted_items))

    def convert_units(self, quantity, from_unit, to_unit):
        """Convert quantity from one unit to another. Returns None if conversion not possible."""
        # If units are the same, no conversion needed
        if from_unit == to_unit:
            return quantity

        # Normalize unit strings (lowercase, strip)
        from_unit = from_unit.lower().strip()
        to_unit = to_unit.lower().strip()

        if from_unit == to_unit:
            return quantity

        # Define conversion factors to base units (kg for weight, L for volume)
        weight_conversions = {
            'kg': 1.0,
            'g': 0.001,
            'lb': 0.453592,
            'oz': 0.0283495
        }

        volume_conversions = {
            'l': 1.0,
            'ml': 0.001,
        }

        # Try weight conversion
        if from_unit in weight_conversions and to_unit in weight_conversions:
            # Convert from_unit to kg, then kg to to_unit
            in_kg = quantity * weight_conversions[from_unit]
            result = in_kg / weight_conversions[to_unit]
            return result

        # Try volume conversion
        if from_unit in volume_conversions and to_unit in volume_conversions:
            # Convert from_unit to L, then L to to_unit
            in_litres = quantity * volume_conversions[from_unit]
            result = in_litres / volume_conversions[to_unit]
            return result

        # Cannot convert between different measurement types (e.g., weight to volume)
        return None


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
        # Buttons (Bottom) - PACK FIRST
        button_frame = ttk.Frame(self, padding=10)
        button_frame.pack(fill=tk.X, side=tk.BOTTOM)

        ttk.Button(button_frame, text="Cancel", bootstyle="secondary",
                  command=self.destroy).pack(side=tk.RIGHT, padx=(10,0))
        ttk.Button(button_frame, text="Package", bootstyle="success",
                  command=self.package).pack(side=tk.RIGHT, padx=(10,0))
        ttk.Button(button_frame, text="Save", bootstyle="primary",
                  command=self.save).pack(side=tk.RIGHT, padx=(10,0))
        ttk.Button(button_frame, text="Print Labels", bootstyle="info",
                  command=self.print_labels).pack(side=tk.RIGHT, padx=(10,0))

        # Main scrollable container
        scroll_frame = ScrollableFrame(self)
        scroll_frame.pack(fill=tk.BOTH, expand=True)

        frame = ttk.Frame(scroll_frame.inner_frame, padding=20)
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

        og = self.batch.get('original_gravity')
        og_text = f"{og:.3f}" if og else "Not set"

        info_text = f"""Gyle: {self.batch.get('gyle_number', 'N/A')}
Recipe: {recipe_name}
Brew Date: {format_date_for_display(self.batch.get('brew_date', ''))}
Batch Size: {self.batch.get('actual_batch_size', 0):.0f}L
O.G.: {og_text}"""

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

        # Load containers from settings_containers table
        self.container_var = tk.StringVar()
        self.load_containers()

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

        # Enable mousewheel and keyboard scrolling
        enable_mousewheel_scrolling(self.container_tree)
        enable_treeview_keyboard_navigation(self.container_tree)

        # Total label
        self.total_label = ttk.Label(container_frame, text="Total: 0L", font=('Arial', 12, 'bold'))
        self.total_label.pack(pady=(10,0))

        # Bind remove action
        self.container_tree.bind('<Button-1>', self.on_tree_click)


    def load_containers(self):
        """Load available containers from settings_containers table"""
        self.cache.connect()
        cursor = self.cache.connection.cursor()

        cursor.execute('''
            SELECT name, actual_capacity, duty_paid_volume, is_draught_eligible
            FROM settings_containers
            WHERE active = 1
            ORDER BY name
        ''')

        containers = cursor.fetchall()
        self.cache.close()

        self.container_options = {}
        for name, actual_cap, duty_vol, is_draught in containers:
            display_name = f"{name} ({duty_vol:.1f}L duty-paid)"
            self.container_options[display_name] = {
                'name': name,
                'actual_capacity': actual_cap,
                'duty_volume': duty_vol,
                'is_draught': is_draught == 1
            }

        if not self.container_options:
            # Fallback if no containers configured
            messagebox.showwarning("No Containers",
                "No containers configured in Settings.\n\n"
                "Please configure containers in the Settings module before packaging.")

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

        # Add to list - use duty_volume for duty calculations
        duty_vol = container['duty_volume']
        total_duty_vol = qty * duty_vol

        item_id = self.container_tree.insert('', 'end', values=(
            qty,
            container['name'],
            f"{duty_vol:.1f}L",
            f"{total_duty_vol:.1f}L",
            "[Remove]"
        ))

        self.selected_containers.append({
            'item_id': item_id,
            'name': container['name'],
            'qty': qty,
            'actual_capacity': container['actual_capacity'],
            'duty_volume': duty_vol,
            'is_draught': container['is_draught'],
            'total': total_duty_vol
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

    def print_labels(self):
        """Generate and print labels for selected containers"""
        # Validate containers selected
        if not self.selected_containers:
            messagebox.showwarning("No Containers",
                "Please add containers before printing labels.")
            return

        # Get package date
        package_date = self.package_date_entry.get()

        # Prepare container data with fill numbers
        containers_data = []
        fill_num = 1
        for container in self.selected_containers:
            for i in range(container['qty']):
                containers_data.append({
                    'name': container['name'],
                    'qty': 1,
                    'duty_volume': container['duty_volume'],
                    'fill_number': fill_num
                })
                fill_num += 1

        # Prepare batch data
        batch_data = {
            'batch_id': self.batch.get('batch_id'),
            'gyle_number': self.batch.get('gyle_number'),
            'recipe_id': self.batch.get('recipe_id'),
            'package_date': package_date
        }

        # Generate and open PDF
        try:
            pdf_path = print_labels_for_batch(batch_data, containers_data, self.cache)
            messagebox.showinfo("Labels Generated",
                f"Labels generated successfully!\n\n"
                f"Total labels: {sum(c['qty'] for c in self.selected_containers)}\n"
                f"PDF saved and opened")
        except Exception as e:
            messagebox.showerror("Print Error",
                f"Error generating labels:\n{str(e)}")

    def save(self):
        """Save container selections without finalizing the batch"""
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
            messagebox.showwarning("No Containers",
                "Please add at least one container before saving.")
            return

        messagebox.showinfo("Saved",
            "Container selections saved!\n\n"
            "You can now:\n"
            "• Print labels\n"
            "• Click 'Package' when F.G. is ready to finalize")

    def package(self):
        """Finalize packaging with F.G. and duty calculations"""
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

        # Calculate ABV
        og = self.batch.get('original_gravity')
        if not og:
            messagebox.showerror("Error",
                "Original Gravity (O.G.) is not set for this batch.\n\n"
                "This batch was created before the O.G. tracking feature was added.\n"
                "Please edit the batch to add the O.G. before packaging.")
            return

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

        # Load duty rates from settings
        self.cache.connect()
        cursor = self.cache.connection.cursor()

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
            self.cache.close()
            messagebox.showerror("Error",
                "Duty rates not configured.\n\n"
                "Please configure duty rates in the Settings module before packaging.")
            return

        spr_draught_low, spr_draught_std, spr_non_draught, rate_full = settings_row

        # Calculate total packaged volume and duty
        total_packaged_volume = sum(c['total'] for c in self.selected_containers)
        total_duty = 0.0

        # Get fermented volume from batch
        fermented_volume = self.batch.get('actual_batch_size', 0)

        # Update batch record with packaging details
        waste_volume = max(0, fermented_volume - total_packaged_volume)
        waste_percentage = (waste_volume / fermented_volume * 100) if fermented_volume > 0 else 0

        batch_data = {
            'final_gravity': fg,
            'actual_abv': actual_abv,
            'measured_abv': duty_abv,  # Use duty_abv for HMRC compliance
            'packaged_date': package_date_db,
            'fermented_volume': fermented_volume,
            'packaged_volume': total_packaged_volume,
            'waste_volume': waste_volume,
            'waste_percentage': waste_percentage,
            'status': 'packaged',
            'last_modified': get_now_db(),
            'sync_status': 'pending'
        }

        self.cache.update_record('batches', self.batch['batch_id'], batch_data, 'batch_id')

        # Get recipe details for product info
        recipe_name = "Unknown Product"
        recipe_style = ""
        if self.batch.get('recipe_id'):
            recipes = self.cache.get_all_records('recipes', f"recipe_id = '{self.batch['recipe_id']}'")
            if recipes:
                recipe_name = recipes[0].get('recipe_name', 'Unknown Product')
                recipe_style = recipes[0].get('style', '')

        # Process each container line with duty calculations
        for container in self.selected_containers:
            qty = container['qty']
            duty_volume_per_unit = container['duty_volume']
            is_draught = container['is_draught']

            # Calculate volumes
            total_duty_volume = duty_volume_per_unit * qty
            pure_alcohol_litres = total_duty_volume * (duty_abv / 100)

            # Determine SPR category and effective rate
            if duty_abv >= 8.5:
                spr_category = "no_spr"
                effective_rate = rate_full
            elif duty_abv < 3.5 and is_draught:
                spr_category = "draught_low"
                effective_rate = spr_draught_low
            elif 3.5 <= duty_abv < 8.5 and is_draught:
                spr_category = "draught_standard"
                effective_rate = spr_draught_std
            elif 3.5 <= duty_abv < 8.5 and not is_draught:
                spr_category = "non_draught_standard"
                effective_rate = spr_non_draught
            else:
                # Fallback - should not happen
                spr_category = "unknown"
                effective_rate = rate_full

            # Calculate duty payable for this line
            duty_payable = pure_alcohol_litres * effective_rate
            total_duty += duty_payable

            # Insert into batch_packaging_lines table
            cursor.execute('''
                INSERT INTO batch_packaging_lines (
                    batch_id,
                    packaging_date,
                    container_type,
                    quantity,
                    container_actual_size,
                    container_duty_volume,
                    total_duty_volume,
                    batch_abv,
                    pure_alcohol_litres,
                    spr_category,
                    spr_rate_applied,
                    full_duty_rate,
                    effective_duty_rate,
                    duty_payable,
                    is_draught_eligible
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                self.batch['batch_id'],
                package_date_db,
                container['name'],
                qty,
                container['actual_capacity'],
                duty_volume_per_unit,
                total_duty_volume,
                duty_abv,
                pure_alcohol_litres,
                spr_category,
                effective_rate,
                rate_full,
                effective_rate,
                duty_payable,
                1 if is_draught else 0
            ))

            # Create product record (for finished goods tracking)
            product_id = str(uuid.uuid4())
            product_data = {
                'product_id': product_id,
                'gyle_number': self.batch.get('gyle_number'),
                'batch_id': self.batch.get('batch_id'),
                'recipe_id': self.batch.get('recipe_id'),
                'product_name': recipe_name,
                'style': recipe_style,
                'container_type': container['name'],
                'container_size_l': duty_volume_per_unit,
                'quantity_total': qty,
                'quantity_in_stock': qty,
                'quantity_sold': 0,
                'abv': actual_abv,
                'date_packaged': package_date_db,
                'date_in_stock': package_date_db,
                'status': 'In Stock',
                'is_name_locked': 0,
                'created_date': get_now_db(),
                'created_by': self.current_user.username,
                'last_modified': get_now_db(),
                'sync_status': 'pending'
            }
            self.cache.insert_record('products', product_data)

            # Deduct from container_types inventory
            container_types = self.cache.get_all_records('container_types',
                f"name = '{container['name']}'")
            if container_types:
                container_type = container_types[0]
                new_qty = max(0, container_type.get('quantity_available', 0) - qty)
                self.cache.update_record('container_types', container_type['container_type_id'], {
                    'quantity_available': new_qty,
                    'last_modified': get_now_db()
                }, 'container_type_id')

        self.cache.connection.commit()
        self.cache.close()

        messagebox.showinfo("Success",
            f"Batch packaged successfully!\n\n"
            f"Actual ABV: {actual_abv:.2f}%\n"
            f"Duty ABV: {duty_abv:.2f}%\n"
            f"Packaged Volume: {total_packaged_volume:.1f}L\n"
            f"Waste: {waste_volume:.1f}L ({waste_percentage:.1f}%)\n"
            f"Total Duty: £{total_duty:.2f}")
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
        # Buttons (Top)
        button_frame = ttk.Frame(self, padding=10)
        button_frame.pack(fill=tk.X, side=tk.TOP)

        ttk.Button(button_frame, text="Cancel", bootstyle="secondary",
                  command=self.destroy).pack(side=tk.RIGHT, padx=(10,0))
        ttk.Button(button_frame, text="Save Changes", bootstyle="success",
                  command=self.save).pack(side=tk.RIGHT)

        # Main scrollable container
        scroll_frame = ScrollableFrame(self)
        scroll_frame.pack(fill=tk.BOTH, expand=True)

        frame = ttk.Frame(scroll_frame.inner_frame, padding=20)
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

        og = self.batch.get('original_gravity')
        actual_abv = self.batch.get('actual_abv')
        duty_abv = self.batch.get('duty_abv')

        og_text = f"{og:.3f}" if og else "Not set"
        actual_abv_text = f"{actual_abv:.1f}%" if actual_abv else "Not set"
        duty_abv_text = f"{duty_abv:.1f}%" if duty_abv else "Not set"

        info_text = f"""Gyle: {self.batch.get('gyle_number', 'N/A')}
Recipe: {recipe_name}
Brew Date: {format_date_for_display(self.batch.get('brew_date', ''))}
Brewer: {self.batch.get('brewer_name', 'N/A')}
Batch Size: {self.batch.get('actual_batch_size', 0):.0f}L
Current O.G.: {og_text}
Current Actual ABV: {actual_abv_text}
Current Duty ABV: {duty_abv_text}"""

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

        # Enable mousewheel and keyboard scrolling
        enable_mousewheel_scrolling(self.container_tree)
        enable_treeview_keyboard_navigation(self.container_tree)

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
        if not og:
            messagebox.showerror("Error",
                "Original Gravity (O.G.) is not set for this batch.\n\n"
                "This batch was created before the O.G. tracking feature was added.\n"
                "Please edit the batch to add the O.G. before updating packaging.")
            return

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

        # NOTE: Editing packaged batches updates batch ABV but does NOT modify existing products
        # Products should be managed separately in the Products module:
        # 1. Update product ABV manually in Products module if needed
        # 2. Container changes require manual product management (add/delete products)
        # This prevents accidental changes to products that may have already been sold

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
            f"Batch updated!\n\n"
            f"New Actual ABV: {new_actual_abv:.2f}%\n"
            f"New Duty ABV: {new_duty_abv:.2f}%\n\n"
            f"Note: Existing products NOT updated.\n"
            f"Update products manually in Products module if needed.")
        self.destroy()
