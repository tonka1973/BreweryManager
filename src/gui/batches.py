"""
Batches Module for Brewery Management System
Tracks batch production with gyle numbers and full traceability
"""

import tkinter as tk
from tkinter import messagebox
import ttkbootstrap as ttk
import uuid
from datetime import datetime
from ..utilities.date_utils import format_date_for_display, format_datetime_for_display, parse_display_date, get_today_display, get_today_db, get_now_db


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

        view_btn = ttk.Button(toolbar, text="👁️ View Details",
                             bootstyle="secondary",
                             command=self.view_batch)
        view_btn.pack(side=tk.LEFT, padx=(0, 10))

        status_btn = ttk.Button(toolbar, text="📊 Update Status",
                               bootstyle="warning",
                               command=self.update_status)
        status_btn.pack(side=tk.LEFT, padx=(0, 10))

        refresh_btn = ttk.Button(toolbar, text="🔄 Refresh",
                                bootstyle="secondary",
                                command=self.load_batches)
        refresh_btn.pack(side=tk.LEFT)

        # Filter by status
        ttk.Label(toolbar, text="Status:").pack(side=tk.RIGHT, padx=(0,5))
        self.filter_var = tk.StringVar(value='all')
        self.filter_var.trace('w', lambda *args: self.load_batches())
        filter_menu = ttk.Combobox(toolbar, textvariable=self.filter_var,
                                   values=['all', 'brewing', 'fermenting', 'conditioning', 'ready', 'packaged'],
                                   width=12, state='readonly')
        filter_menu.pack(side=tk.RIGHT, padx=(10,0))

        # Batches list
        list_frame = ttk.Frame(self, relief=tk.SOLID, borderwidth=1)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))

        vsb = ttk.Scrollbar(list_frame, orient="vertical")
        vsb.pack(side=tk.RIGHT, fill=tk.Y)

        columns = ('Gyle', 'Recipe', 'Brew Date', 'ABV', 'Volume (L)', 'Status', 'Brewer')
        self.tree = ttk.Treeview(list_frame, columns=columns, show='headings', yscrollcommand=vsb.set)

        for col in columns:
            self.tree.heading(col, text=col)

        self.tree.column('Gyle', width=140)
        self.tree.column('Recipe', width=180)
        self.tree.column('Brew Date', width=100)
        self.tree.column('ABV', width=80)
        self.tree.column('Volume (L)', width=100)
        self.tree.column('Status', width=120)
        self.tree.column('Brewer', width=120)

        self.tree.pack(fill=tk.BOTH, expand=True)
        vsb.config(command=self.tree.yview)

        self.tree.bind('<Double-1>', lambda e: self.view_batch())

    def load_batches(self):
        """Load batches from database"""
        for item in self.tree.get_children():
            self.tree.delete(item)

        status_filter = self.filter_var.get()
        where = None if status_filter == 'all' else f"status = '{status_filter}'"

        self.cache.connect()
        batches = self.cache.get_all_records('batches', where, 'brew_date DESC')
        self.cache.close()

        for batch in batches:
            recipe_name = 'Unknown'
            if batch.get('recipe_id'):
                self.cache.connect()
                recipes = self.cache.get_all_records('recipes', f"recipe_id = '{batch['recipe_id']}'")
                self.cache.close()
                if recipes:
                    recipe_name = recipes[0].get('recipe_name', 'Unknown')

            abv = batch.get('measured_abv') or batch.get('target_abv', 0)
            values = (
                batch.get('gyle_number', ''),
                recipe_name,
                format_date_for_display(batch.get('brew_date', '')),
                f"{abv:.1f}%" if abv else 'N/A',
                f"{batch.get('actual_batch_size', 0):.0f}",
                batch.get('status', '').capitalize(),
                batch.get('brewer_name', 'N/A')
            )

            status = batch.get('status', 'unknown')
            self.tree.insert('', 'end', values=values, tags=(f'status_{status}', batch['batch_id']))

        self.tree.tag_configure('status_brewing', background='#e3f2fd')
        self.tree.tag_configure('status_fermenting', background='#fff3e0')
        self.tree.tag_configure('status_conditioning', background='#f3e5f5')
        self.tree.tag_configure('status_ready', background='#e8f5e9')
        self.tree.tag_configure('status_packaged', background='#f5f5f5')

    def add_batch(self):
        """Add new batch"""
        dialog = BatchDialog(self, self.cache, self.current_user, mode='add')
        self.wait_window(dialog)
        self.load_batches()

    def edit_batch(self):
        """Edit selected batch"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a batch.")
            return

        tags = self.tree.item(selection[0], 'tags')
        batch_id = tags[1] if len(tags) > 1 else None

        self.cache.connect()
        batches = self.cache.get_all_records('batches', f"batch_id = '{batch_id}'")
        self.cache.close()

        if batches:
            dialog = BatchDialog(self, self.cache, self.current_user, mode='edit', batch=batches[0])
            self.wait_window(dialog)
            self.load_batches()

    def view_batch(self):
        """View batch details"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a batch.")
            return

        tags = self.tree.item(selection[0], 'tags')
        batch_id = tags[1] if len(tags) > 1 else None

        self.cache.connect()
        batches = self.cache.get_all_records('batches', f"batch_id = '{batch_id}'")
        self.cache.close()

        if batches:
            dialog = BatchDetailsDialog(self, batches[0], self.cache)
            self.wait_window(dialog)

    def update_status(self):
        """Update batch status"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a batch.")
            return

        tags = self.tree.item(selection[0], 'tags')
        batch_id = tags[1] if len(tags) > 1 else None

        self.cache.connect()
        batches = self.cache.get_all_records('batches', f"batch_id = '{batch_id}'")
        self.cache.close()

        if batches:
            dialog = StatusUpdateDialog(self, self.cache, batches[0])
            self.wait_window(dialog)
            self.load_batches()


class BatchDialog(tk.Toplevel):
    """Dialog for adding/editing batches"""

    def __init__(self, parent, cache_manager, current_user, mode='add', batch=None):
        super().__init__(parent)
        self.cache = cache_manager
        self.current_user = current_user
        self.mode = mode
        self.batch = batch

        self.title("New Batch" if mode == 'add' else "Edit Batch")
        self.geometry("600x500")
        self.resizable(True, True)
        self.transient(parent)
        self.grab_set()

        self.create_widgets()
        if mode == 'edit' and batch:
            self.populate_fields()

    def create_widgets(self):
        """Create widgets"""
        frame = ttk.Frame(self, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)

        # Recipe selection
        ttk.Label(frame, text="Recipe *", font=('Arial', 10, 'bold')).grid(row=0, column=0, sticky='w', pady=(0,5))
        self.recipe_var = tk.StringVar()
        self.cache.connect()
        recipes = self.cache.get_all_records('recipes', 'is_active = 1', 'recipe_name')
        self.cache.close()
        self.recipe_list = {r['recipe_name']: r['recipe_id'] for r in recipes}
        recipe_menu = ttk.Combobox(frame, textvariable=self.recipe_var,
                                   values=list(self.recipe_list.keys()), width=37, state='readonly')
        recipe_menu.grid(row=1, column=0, columnspan=2, sticky='ew', pady=(0,15))

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

        # Batch Size
        ttk.Label(frame, text="Batch Size (L) *", font=('Arial', 10, 'bold')).grid(row=4, column=1, sticky='w', pady=(0,5), padx=(20,0))
        self.size_entry = ttk.Entry(frame, font=('Arial', 10), width=15)
        self.size_entry.grid(row=5, column=1, sticky='w', pady=(0,15), padx=(20,0))

        # Measured ABV
        ttk.Label(frame, text="Measured ABV %", font=('Arial', 10, 'bold')).grid(row=6, column=0, sticky='w', pady=(0,5))
        self.abv_entry = ttk.Entry(frame, font=('Arial', 10), width=15)
        self.abv_entry.grid(row=7, column=0, sticky='w', pady=(0,15))

        # Brewing Notes
        ttk.Label(frame, text="Brewing Notes", font=('Arial', 10, 'bold')).grid(row=8, column=0, sticky='w', pady=(0,5))
        self.notes_text = tk.Text(frame, font=('Arial', 10), width=40, height=6)
        self.notes_text.grid(row=9, column=0, columnspan=2, sticky='ew', pady=(0,15))

        frame.grid_columnconfigure(0, weight=1)
        frame.grid_columnconfigure(1, weight=1)

        # Buttons
        button_frame = ttk.Frame(self, padding=10)
        button_frame.pack(fill=tk.X, padx=20, pady=(0,20))

        ttk.Button(button_frame, text="Cancel", bootstyle="secondary",
                  command=self.destroy).pack(side=tk.RIGHT, padx=(10,0))
        ttk.Button(button_frame, text="Save Batch", bootstyle="success",
                  command=self.save).pack(side=tk.RIGHT)

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
                self.recipe_var.set(recipes[0]['recipe_name'])

        self.gyle_entry.delete(0, tk.END)
        self.gyle_entry.insert(0, self.batch.get('gyle_number', ''))
        self.brew_date_entry.delete(0, tk.END)
        self.brew_date_entry.insert(0, format_date_for_display(self.batch.get('brew_date', '')))
        self.brewer_entry.delete(0, tk.END)
        self.brewer_entry.insert(0, self.batch.get('brewer_name', ''))
        self.size_entry.insert(0, str(self.batch.get('actual_batch_size', '')))
        if self.batch.get('measured_abv'):
            self.abv_entry.insert(0, str(self.batch['measured_abv']))
        if self.batch.get('brewing_notes'):
            self.notes_text.insert('1.0', self.batch['brewing_notes'])

    def save(self):
        """Save batch"""
        recipe_name = self.recipe_var.get()
        if not recipe_name or recipe_name not in self.recipe_list:
            messagebox.showerror("Error", "Please select a recipe.")
            return

        gyle = self.gyle_entry.get().strip()
        if not gyle:
            messagebox.showerror("Error", "Gyle number is required.")
            return

        try:
            batch_size = float(self.size_entry.get())
            abv = float(self.abv_entry.get() or 0)
        except ValueError:
            messagebox.showerror("Error", "Invalid number format.")
            return

        # Convert date from display format (DD/MM/YYYY) to database format (YYYY-MM-DD)
        brew_date_db = parse_display_date(self.brew_date_entry.get())
        if not brew_date_db:
            messagebox.showerror("Error", "Invalid date format. Please use DD/MM/YYYY.")
            return

        # For new batches, default to 'brewing'. For edits, preserve existing status
        batch_status = 'brewing' if self.mode == 'add' else self.batch.get('status', 'brewing')

        data = {
            'recipe_id': self.recipe_list[recipe_name],
            'gyle_number': gyle,
            'brew_date': brew_date_db,
            'brewer_name': self.brewer_entry.get().strip(),
            'actual_batch_size': batch_size,
            'measured_abv': abv if abv > 0 else None,
            'status': batch_status,
            'brewing_notes': self.notes_text.get('1.0', tk.END).strip(),
            'last_modified': get_now_db(),
            'created_by': self.current_user.username,
            'sync_status': 'pending'
        }

        if abv and batch_size:
            data['pure_alcohol_litres'] = (abv / 100) * batch_size

        self.cache.connect()
        if self.mode == 'add':
            data['batch_id'] = str(uuid.uuid4())
            self.cache.insert_record('batches', data)
        else:
            self.cache.update_record('batches', self.batch['batch_id'], data, 'batch_id')
        self.cache.close()

        messagebox.showinfo("Success", "Batch saved!")
        self.destroy()


class BatchDetailsDialog(tk.Toplevel):
    """Dialog for viewing batch details"""

    def __init__(self, parent, batch, cache):
        super().__init__(parent)
        self.batch = batch
        self.cache = cache

        self.title(f"Batch: {batch.get('gyle_number', 'Unknown')}")
        self.geometry("600x500")
        self.transient(parent)
        self.grab_set()

        self.create_widgets()

    def create_widgets(self):
        """Create widgets"""
        frame = ttk.Frame(self, padding=30)
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text=self.batch.get('gyle_number', 'Unknown'),
                 font=('Arial', 18, 'bold')).pack(anchor='w', pady=(0,10))

        recipe_name = 'Unknown'
        if self.batch.get('recipe_id'):
            self.cache.connect()
            recipes = self.cache.get_all_records('recipes', f"recipe_id = '{self.batch['recipe_id']}'")
            self.cache.close()
            if recipes:
                recipe_name = recipes[0]['recipe_name']

        info = f"""
Recipe: {recipe_name}
Brew Date: {format_date_for_display(self.batch.get('brew_date')) or 'N/A'}
Brewer: {self.batch.get('brewer_name', 'N/A')}
Batch Size: {self.batch.get('actual_batch_size', 0):.1f} litres
ABV: {self.batch.get('measured_abv', 0):.1f}%
Pure Alcohol: {self.batch.get('pure_alcohol_litres', 0):.2f} litres
Status: {self.batch.get('status', 'N/A').capitalize()}

Fermenting Start: {format_date_for_display(self.batch.get('fermenting_start')) or 'Not started'}
Conditioning Start: {format_date_for_display(self.batch.get('conditioning_start')) or 'Not started'}
Ready Date: {format_date_for_display(self.batch.get('ready_date')) or 'Not ready'}
Packaged Date: {format_date_for_display(self.batch.get('packaged_date')) or 'Not packaged'}
        """

        ttk.Label(frame, text=info.strip(), font=('Arial', 10),
                 justify=tk.LEFT).pack(anchor='w', pady=(0,20))

        if self.batch.get('brewing_notes'):
            ttk.Label(frame, text="Brewing Notes:", font=('Arial', 11, 'bold')).pack(anchor='w', pady=(0,5))
            # Keep tk.Frame here for specific background color
            notes_frame = tk.Frame(frame, bg='#f5f5f5', relief=tk.SOLID, borderwidth=1)
            notes_frame.pack(fill=tk.X, pady=(0,20))
            tk.Label(notes_frame, text=self.batch['brewing_notes'], font=('Arial', 10),
                    bg='#f5f5f5', justify=tk.LEFT, wraplength=500).pack(padx=10, pady=10, anchor='w')

        ttk.Button(self, text="Close", bootstyle="secondary",
                  command=self.destroy).pack(pady=(0,20))


class StatusUpdateDialog(tk.Toplevel):
    """Dialog for updating batch status"""

    def __init__(self, parent, cache, batch):
        super().__init__(parent)
        self.cache = cache
        self.batch = batch

        self.title(f"Update Status: {batch.get('gyle_number', 'Unknown')}")
        self.geometry("400x300")
        self.transient(parent)
        self.grab_set()

        self.create_widgets()

    def create_widgets(self):
        """Create widgets"""
        frame = ttk.Frame(self, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text=f"Current Status: {self.batch.get('status', 'unknown').capitalize()}",
                 font=('Arial', 12, 'bold')).pack(pady=(0,20))

        ttk.Label(frame, text="New Status", font=('Arial', 10, 'bold')).pack(anchor='w', pady=(0,5))
        self.status_var = tk.StringVar(value=self.batch.get('status', 'brewing'))
        status_menu = ttk.Combobox(frame, textvariable=self.status_var,
                                   values=['brewing', 'fermenting', 'conditioning', 'ready', 'packaged'],
                                   width=25, state='readonly', font=('Arial', 10))
        status_menu.pack(anchor='w', pady=(0,20))

        button_frame = ttk.Frame(self, padding=10)
        button_frame.pack(fill=tk.X, padx=20)

        ttk.Button(button_frame, text="Cancel", bootstyle="secondary",
                  command=self.destroy).pack(side=tk.RIGHT, padx=(10,0))
        ttk.Button(button_frame, text="Update", bootstyle="warning",
                  command=self.update).pack(side=tk.RIGHT)

    def update(self):
        """Update status"""
        new_status = self.status_var.get()
        data = {'status': new_status, 'last_modified': get_now_db()}

        # Set date fields based on status
        today = get_today_db()
        if new_status == 'fermenting' and not self.batch.get('fermenting_start'):
            data['fermenting_start'] = today
        elif new_status == 'conditioning' and not self.batch.get('conditioning_start'):
            data['conditioning_start'] = today
        elif new_status == 'ready' and not self.batch.get('ready_date'):
            data['ready_date'] = today
        elif new_status == 'packaged' and not self.batch.get('packaged_date'):
            data['packaged_date'] = today

        self.cache.connect()
        self.cache.update_record('batches', self.batch['batch_id'], data, 'batch_id')
        self.cache.close()

        messagebox.showinfo("Success", f"Status updated to {new_status}!")
        self.destroy()
