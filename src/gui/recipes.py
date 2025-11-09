"""
Recipes Module for Brewery Management System - COMPLETE REWRITE
Fully integrated with Brewery Inventory for ingredient management
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import uuid
from datetime import datetime


class RecipesModule(tk.Frame):
    """Recipes module with full inventory integration"""

    def __init__(self, parent, cache_manager, current_user):
        super().__init__(parent, bg='white')
        self.cache = cache_manager
        self.current_user = current_user

        self.create_widgets()
        self.load_recipes()

    def create_widgets(self):
        """Create recipe list widgets"""
        # Toolbar
        toolbar = tk.Frame(self, bg='white')
        toolbar.pack(fill=tk.X, padx=20, pady=(0, 10))

        add_btn = tk.Button(toolbar, text="➕ New Recipe", font=('Arial', 10, 'bold'),
                           bg='#4CAF50', fg='white', cursor='hand2',
                           command=self.add_recipe, padx=15, pady=8)
        add_btn.pack(side=tk.LEFT, padx=(0, 10))

        edit_btn = tk.Button(toolbar, text="✏️ Edit", font=('Arial', 10),
                            bg='#2196F3', fg='white', cursor='hand2',
                            command=self.edit_recipe, padx=15, pady=8)
        edit_btn.pack(side=tk.LEFT, padx=(0, 10))

        view_btn = tk.Button(toolbar, text="👁️ View Recipe", font=('Arial', 10),
                            bg='#9C27B0', fg='white', cursor='hand2',
                            command=self.view_recipe, padx=15, pady=8)
        view_btn.pack(side=tk.LEFT, padx=(0, 10))

        delete_btn = tk.Button(toolbar, text="🗑️ Delete", font=('Arial', 10),
                              bg='#f44336', fg='white', cursor='hand2',
                              command=self.delete_recipe, padx=15, pady=8)
        delete_btn.pack(side=tk.LEFT, padx=(0, 10))

        refresh_btn = tk.Button(toolbar, text="🔄 Refresh", font=('Arial', 10),
                               bg='#607D8B', fg='white', cursor='hand2',
                               command=self.load_recipes, padx=15, pady=8)
        refresh_btn.pack(side=tk.LEFT)

        # Recipe list
        list_frame = tk.Frame(self, bg='white', relief=tk.SOLID, borderwidth=1)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))

        vsb = tk.Scrollbar(list_frame, orient="vertical")
        vsb.pack(side=tk.RIGHT, fill=tk.Y)

        columns = ('Recipe Name', 'Style', 'ABV%', 'Batch Size (L)', 'Version', 'Modified')
        self.tree = ttk.Treeview(list_frame, columns=columns, show='headings',
                                yscrollcommand=vsb.set)

        for col in columns:
            self.tree.heading(col, text=col)

        self.tree.column('Recipe Name', width=250)
        self.tree.column('Style', width=150)
        self.tree.column('ABV%', width=80)
        self.tree.column('Batch Size (L)', width=120)
        self.tree.column('Version', width=80)
        self.tree.column('Modified', width=120)

        self.tree.pack(fill=tk.BOTH, expand=True)
        vsb.config(command=self.tree.yview)

        # Double-click to view
        self.tree.bind('<Double-Button-1>', lambda e: self.view_recipe())

    def load_recipes(self):
        """Load recipes from database"""
        for item in self.tree.get_children():
            self.tree.delete(item)

        self.cache.connect()
        recipes = self.cache.get_all_records('recipes', order_by='recipe_name')
        self.cache.close()

        for recipe in recipes:
            if recipe.get('is_active', 1):
                values = (
                    recipe.get('recipe_name', ''),
                    recipe.get('style', ''),
                    f"{recipe.get('target_abv', 0):.1f}%",
                    f"{recipe.get('target_batch_size_litres', 0):.0f}",
                    f"v{recipe.get('version', 1)}",
                    recipe.get('last_modified', '')[:10] if recipe.get('last_modified') else ''
                )
                self.tree.insert('', 'end', values=values, tags=(recipe['recipe_id'],))

    def add_recipe(self):
        """Add new recipe"""
        dialog = RecipeDialog(self, self.cache, self.current_user, mode='add')
        self.wait_window(dialog)
        self.load_recipes()

    def edit_recipe(self):
        """Edit selected recipe"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a recipe.")
            return

        recipe_id = self.tree.item(selection[0], 'tags')[0]
        self.cache.connect()
        recipes = self.cache.get_all_records('recipes', f"recipe_id = '{recipe_id}'")
        self.cache.close()

        if recipes:
            dialog = RecipeDialog(self, self.cache, self.current_user, mode='edit', recipe=recipes[0])
            self.wait_window(dialog)
            self.load_recipes()

    def view_recipe(self):
        """View recipe details"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a recipe.")
            return

        recipe_id = self.tree.item(selection[0], 'tags')[0]
        dialog = RecipeViewDialog(self, self.cache, recipe_id)
        self.wait_window(dialog)

    def delete_recipe(self):
        """Delete recipe (mark as inactive)"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a recipe.")
            return

        result = messagebox.askyesno("Confirm Delete", "Mark this recipe as inactive?")
        if result:
            recipe_id = self.tree.item(selection[0], 'tags')[0]
            self.cache.connect()
            self.cache.update_record('recipes', recipe_id, {'is_active': 0}, 'recipe_id')
            self.cache.close()
            messagebox.showinfo("Success", "Recipe marked as inactive.")
            self.load_recipes()


class RecipeDialog(tk.Toplevel):
    """Dialog for creating/editing recipes with inventory integration"""

    def __init__(self, parent, cache_manager, current_user, mode='add', recipe=None):
        super().__init__(parent)
        self.cache = cache_manager
        self.current_user = current_user
        self.mode = mode
        self.recipe = recipe

        self.title("New Recipe" if mode == 'add' else "Edit Recipe")
        self.geometry("1000x700")
        self.resizable(True, True)
        self.transient(parent)
        self.grab_set()

        # Ingredient data storage
        self.grains = []
        self.hops = []
        self.yeasts = []
        self.adjuncts = []

        self.create_widgets()
        if mode == 'edit' and recipe:
            self.populate_fields()

    def create_widgets(self):
        """Create dialog widgets"""
        # Main container with scrollbar
        main_frame = tk.Frame(self, bg='white')
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Basic info section
        info_frame = tk.Frame(main_frame, bg='white', padx=20, pady=10)
        info_frame.pack(fill=tk.X)

        # Row 1
        tk.Label(info_frame, text="Recipe Name *", font=('Arial', 10, 'bold'), bg='white').grid(row=0, column=0, sticky='w', pady=(0,5))
        self.name_entry = tk.Entry(info_frame, font=('Arial', 10), width=40)
        self.name_entry.grid(row=1, column=0, columnspan=2, sticky='ew', pady=(0,10))

        tk.Label(info_frame, text="Style", font=('Arial', 10, 'bold'), bg='white').grid(row=0, column=2, sticky='w', pady=(0,5), padx=(20,0))
        self.style_entry = tk.Entry(info_frame, font=('Arial', 10), width=30)
        self.style_entry.grid(row=1, column=2, sticky='ew', pady=(0,10), padx=(20,0))

        # Row 2
        tk.Label(info_frame, text="Target ABV %", font=('Arial', 10, 'bold'), bg='white').grid(row=2, column=0, sticky='w', pady=(0,5))
        self.abv_entry = tk.Entry(info_frame, font=('Arial', 10), width=15)
        self.abv_entry.grid(row=3, column=0, sticky='w', pady=(0,10))

        tk.Label(info_frame, text="Batch Size (Litres)", font=('Arial', 10, 'bold'), bg='white').grid(row=2, column=1, sticky='w', pady=(0,5), padx=(20,0))
        self.batch_size_entry = tk.Entry(info_frame, font=('Arial', 10), width=15)
        self.batch_size_entry.grid(row=3, column=1, sticky='w', pady=(0,10), padx=(20,0))

        tk.Label(info_frame, text="Version", font=('Arial', 10, 'bold'), bg='white').grid(row=2, column=2, sticky='w', pady=(0,5), padx=(20,0))
        self.version_entry = tk.Entry(info_frame, font=('Arial', 10), width=10)
        self.version_entry.insert(0, "1")
        self.version_entry.grid(row=3, column=2, sticky='w', pady=(0,10), padx=(20,0))

        info_frame.grid_columnconfigure(0, weight=1)
        info_frame.grid_columnconfigure(1, weight=1)
        info_frame.grid_columnconfigure(2, weight=1)

        # Notebook for ingredients
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0,10))

        # Grains tab
        self.grains_tab = IngredientTab(notebook, self.cache, 'grain', self.grains, self)
        notebook.add(self.grains_tab, text='Grain Bill')

        # Hops tab
        self.hops_tab = HopsTab(notebook, self.cache, self.hops, self)
        notebook.add(self.hops_tab, text='Hops Schedule')

        # Yeast tab
        self.yeast_tab = YeastTab(notebook, self.cache, self.yeasts, self)
        notebook.add(self.yeast_tab, text='Yeast')

        # Adjuncts tab
        self.adjuncts_tab = IngredientTab(notebook, self.cache, 'adjunct', self.adjuncts, self)
        notebook.add(self.adjuncts_tab, text='Adjuncts & Sundries')

        # Notes tab
        notes_tab = tk.Frame(notebook, bg='white')
        notebook.add(notes_tab, text='Brewing Notes')
        tk.Label(notes_tab, text="Brewing Instructions & Notes:", font=('Arial', 10, 'bold'), bg='white').pack(anchor='w', padx=20, pady=(20,5))
        self.notes_text = scrolledtext.ScrolledText(notes_tab, font=('Arial', 10), width=80, height=20, wrap=tk.WORD)
        self.notes_text.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0,20))

        # Buttons
        button_frame = tk.Frame(self, bg='white', pady=10)
        button_frame.pack(fill=tk.X, padx=20, pady=(0,10))

        tk.Button(button_frame, text="Cancel", font=('Arial', 10), bg='#757575', fg='white',
                 command=self.destroy, padx=20, pady=8).pack(side=tk.RIGHT, padx=(10,0))
        tk.Button(button_frame, text="Save Recipe", font=('Arial', 10, 'bold'), bg='#4CAF50', fg='white',
                 command=self.save, padx=20, pady=8).pack(side=tk.RIGHT)

    def populate_fields(self):
        """Populate fields with recipe data"""
        self.name_entry.insert(0, self.recipe.get('recipe_name', ''))
        self.style_entry.insert(0, self.recipe.get('style', ''))
        self.abv_entry.insert(0, str(self.recipe.get('target_abv', '')))
        self.batch_size_entry.insert(0, str(self.recipe.get('target_batch_size_litres', '')))
        self.version_entry.delete(0, tk.END)
        self.version_entry.insert(0, str(self.recipe.get('version', 1)))
        self.notes_text.insert('1.0', self.recipe.get('brewing_notes', ''))

        # Load ingredients
        recipe_id = self.recipe['recipe_id']
        self.cache.connect()

        # Load grains
        grains = self.cache.get_all_records('recipe_grains', f"recipe_id = '{recipe_id}'")
        for grain in grains:
            material = self.cache.get_all_records('inventory_materials', f"material_id = '{grain['material_id']}'")
            if material:
                self.grains.append({
                    'material_id': grain['material_id'],
                    'material_name': material[0]['material_name'],
                    'quantity': grain['quantity'],
                    'unit': grain['unit'],
                    'notes': grain.get('mash_notes', '')
                })
        self.grains_tab.refresh_list()

        # Load hops
        hops = self.cache.get_all_records('recipe_hops', f"recipe_id = '{recipe_id}'")
        for hop in hops:
            material = self.cache.get_all_records('inventory_materials', f"material_id = '{hop['material_id']}'")
            if material:
                self.hops.append({
                    'material_id': hop['material_id'],
                    'material_name': material[0]['material_name'],
                    'quantity': hop['quantity'],
                    'unit': hop['unit'],
                    'boil_time': hop.get('boil_time_minutes', 0),
                    'alpha_acid': hop.get('alpha_acid_percent', 0),
                    'addition_type': hop.get('addition_type', 'Boil')
                })
        self.hops_tab.refresh_list()

        # Load yeast
        yeasts = self.cache.get_all_records('recipe_yeast', f"recipe_id = '{recipe_id}'")
        for yeast in yeasts:
            material = self.cache.get_all_records('inventory_materials', f"material_id = '{yeast['material_id']}'")
            if material:
                self.yeasts.append({
                    'material_id': yeast['material_id'],
                    'material_name': material[0]['material_name'],
                    'quantity': yeast['quantity'],
                    'unit': yeast['unit'],
                    'notes': yeast.get('notes', '')
                })
        self.yeast_tab.refresh_list()

        # Load adjuncts
        adjuncts = self.cache.get_all_records('recipe_adjuncts', f"recipe_id = '{recipe_id}'")
        for adjunct in adjuncts:
            material = self.cache.get_all_records('inventory_materials', f"material_id = '{adjunct['material_id']}'")
            if material:
                self.adjuncts.append({
                    'material_id': adjunct['material_id'],
                    'material_name': material[0]['material_name'],
                    'quantity': adjunct['quantity'],
                    'unit': adjunct['unit'],
                    'notes': adjunct.get('timing', '')
                })
        self.adjuncts_tab.refresh_list()

        self.cache.close()

    def save(self):
        """Save recipe"""
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showerror("Error", "Recipe name is required.")
            return

        try:
            abv = float(self.abv_entry.get() or 0)
            batch_size = float(self.batch_size_entry.get() or 0)
            version = int(self.version_entry.get() or 1)
        except ValueError:
            messagebox.showerror("Error", "Invalid number format in ABV, Batch Size, or Version.")
            return

        recipe_data = {
            'recipe_name': name,
            'style': self.style_entry.get().strip(),
            'version': version,
            'target_abv': abv,
            'target_batch_size_litres': batch_size,
            'brewing_notes': self.notes_text.get('1.0', tk.END).strip(),
            'last_modified': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'sync_status': 'pending'
        }

        self.cache.connect()

        if self.mode == 'add':
            recipe_id = str(uuid.uuid4())
            recipe_data['recipe_id'] = recipe_id
            recipe_data['created_date'] = datetime.now().strftime('%Y-%m-%d')
            recipe_data['created_by'] = self.current_user.username
            recipe_data['is_active'] = 1
            self.cache.insert_record('recipes', recipe_data)
        else:
            recipe_id = self.recipe['recipe_id']
            self.cache.update_record('recipes', recipe_id, recipe_data, 'recipe_id')

            # Delete existing ingredients
            self.cache.cursor.execute(f"DELETE FROM recipe_grains WHERE recipe_id = '{recipe_id}'")
            self.cache.cursor.execute(f"DELETE FROM recipe_hops WHERE recipe_id = '{recipe_id}'")
            self.cache.cursor.execute(f"DELETE FROM recipe_yeast WHERE recipe_id = '{recipe_id}'")
            self.cache.cursor.execute(f"DELETE FROM recipe_adjuncts WHERE recipe_id = '{recipe_id}'")

        # Save grains
        for grain in self.grains:
            grain_data = {
                'grain_id': str(uuid.uuid4()),
                'recipe_id': recipe_id,
                'material_id': grain['material_id'],
                'quantity': grain['quantity'],
                'unit': grain['unit'],
                'mash_notes': grain.get('notes', ''),
                'sync_status': 'pending'
            }
            self.cache.insert_record('recipe_grains', grain_data)

        # Save hops
        for hop in self.hops:
            hop_data = {
                'hop_id': str(uuid.uuid4()),
                'recipe_id': recipe_id,
                'material_id': hop['material_id'],
                'quantity': hop['quantity'],
                'unit': hop['unit'],
                'boil_time_minutes': hop.get('boil_time', 0),
                'alpha_acid_percent': hop.get('alpha_acid', 0),
                'addition_type': hop.get('addition_type', 'Boil'),
                'sync_status': 'pending'
            }
            self.cache.insert_record('recipe_hops', hop_data)

        # Save yeast
        for yeast in self.yeasts:
            yeast_data = {
                'yeast_id': str(uuid.uuid4()),
                'recipe_id': recipe_id,
                'material_id': yeast['material_id'],
                'quantity': yeast['quantity'],
                'unit': yeast['unit'],
                'notes': yeast.get('notes', ''),
                'sync_status': 'pending'
            }
            self.cache.insert_record('recipe_yeast', yeast_data)

        # Save adjuncts
        for adjunct in self.adjuncts:
            adjunct_data = {
                'adjunct_id': str(uuid.uuid4()),
                'recipe_id': recipe_id,
                'material_id': adjunct['material_id'],
                'quantity': adjunct['quantity'],
                'unit': adjunct['unit'],
                'timing': adjunct.get('notes', ''),
                'sync_status': 'pending'
            }
            self.cache.insert_record('recipe_adjuncts', adjunct_data)

        self.cache.connection.commit()
        self.cache.close()

        messagebox.showinfo("Success", "Recipe saved successfully!")
        self.destroy()


class IngredientTab(tk.Frame):
    """Tab for grains or adjuncts ingredients"""

    def __init__(self, parent, cache, ingredient_type, ingredient_list, dialog):
        super().__init__(parent, bg='white')
        self.cache = cache
        self.ingredient_type = ingredient_type  # 'grain' or 'adjunct'
        self.ingredient_list = ingredient_list
        self.dialog = dialog

        self.create_widgets()

    def create_widgets(self):
        """Create ingredient tab widgets"""
        # Toolbar
        toolbar = tk.Frame(self, bg='white')
        toolbar.pack(fill=tk.X, padx=20, pady=15)

        tk.Button(toolbar, text=f"➕ Add {self.ingredient_type.capitalize()}", font=('Arial', 10, 'bold'),
                 bg='#4CAF50', fg='white', cursor='hand2',
                 command=self.add_ingredient, padx=15, pady=8).pack(side=tk.LEFT, padx=(0,10))

        tk.Button(toolbar, text="🗑️ Remove", font=('Arial', 10),
                 bg='#f44336', fg='white', cursor='hand2',
                 command=self.remove_ingredient, padx=15, pady=8).pack(side=tk.LEFT)

        # Ingredient list
        list_frame = tk.Frame(self, bg='white', relief=tk.SOLID, borderwidth=1)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0,20))

        vsb = tk.Scrollbar(list_frame, orient="vertical")
        vsb.pack(side=tk.RIGHT, fill=tk.Y)

        if self.ingredient_type == 'grain':
            columns = ('Material', 'Quantity', 'Unit', 'Mash Notes')
        else:
            columns = ('Material', 'Quantity', 'Unit', 'Timing')

        self.tree = ttk.Treeview(list_frame, columns=columns, show='headings',
                                yscrollcommand=vsb.set, height=10)

        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=200)

        self.tree.pack(fill=tk.BOTH, expand=True)
        vsb.config(command=self.tree.yview)

    def add_ingredient(self):
        """Add ingredient from inventory"""
        # Get available materials
        self.cache.connect()
        if self.ingredient_type == 'grain':
            materials = self.cache.get_all_records('inventory_materials', f"material_type = 'grain'", order_by='material_name')
        else:
            materials = self.cache.get_all_records('inventory_materials', f"material_type IN ('adjunct', 'sundries')", order_by='material_name')
        self.cache.close()

        if not materials:
            messagebox.showinfo("No Materials", f"No {self.ingredient_type}s found in inventory. Please add materials first.")
            return

        dialog = AddIngredientDialog(self, materials, self.ingredient_type)
        self.wait_window(dialog)

        if hasattr(dialog, 'result') and dialog.result:
            self.ingredient_list.append(dialog.result)
            self.refresh_list()

    def remove_ingredient(self):
        """Remove selected ingredient"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select an ingredient to remove.")
            return

        index = self.tree.index(selection[0])
        del self.ingredient_list[index]
        self.refresh_list()

    def refresh_list(self):
        """Refresh ingredient list"""
        for item in self.tree.get_children():
            self.tree.delete(item)

        for ing in self.ingredient_list:
            values = (
                ing['material_name'],
                f"{ing['quantity']:.2f}",
                ing['unit'],
                ing.get('notes', '')
            )
            self.tree.insert('', 'end', values=values)


class HopsTab(tk.Frame):
    """Tab for hops ingredients with brewing-specific fields"""

    def __init__(self, parent, cache, hops_list, dialog):
        super().__init__(parent, bg='white')
        self.cache = cache
        self.hops_list = hops_list
        self.dialog = dialog

        self.create_widgets()

    def create_widgets(self):
        """Create hops tab widgets"""
        # Toolbar
        toolbar = tk.Frame(self, bg='white')
        toolbar.pack(fill=tk.X, padx=20, pady=15)

        tk.Button(toolbar, text="➕ Add Hops", font=('Arial', 10, 'bold'),
                 bg='#4CAF50', fg='white', cursor='hand2',
                 command=self.add_hops, padx=15, pady=8).pack(side=tk.LEFT, padx=(0,10))

        tk.Button(toolbar, text="🗑️ Remove", font=('Arial', 10),
                 bg='#f44336', fg='white', cursor='hand2',
                 command=self.remove_hops, padx=15, pady=8).pack(side=tk.LEFT)

        # Hops list
        list_frame = tk.Frame(self, bg='white', relief=tk.SOLID, borderwidth=1)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0,20))

        vsb = tk.Scrollbar(list_frame, orient="vertical")
        vsb.pack(side=tk.RIGHT, fill=tk.Y)

        columns = ('Hop Variety', 'Quantity', 'Unit', 'Boil Time (min)', 'AA%', 'Addition Type')
        self.tree = ttk.Treeview(list_frame, columns=columns, show='headings',
                                yscrollcommand=vsb.set, height=10)

        for col in columns:
            self.tree.heading(col, text=col)

        self.tree.column('Hop Variety', width=200)
        self.tree.column('Quantity', width=100)
        self.tree.column('Unit', width=80)
        self.tree.column('Boil Time (min)', width=120)
        self.tree.column('AA%', width=80)
        self.tree.column('Addition Type', width=150)

        self.tree.pack(fill=tk.BOTH, expand=True)
        vsb.config(command=self.tree.yview)

    def add_hops(self):
        """Add hops from inventory"""
        self.cache.connect()
        hops = self.cache.get_all_records('inventory_materials', "material_type = 'hops'", order_by='material_name')
        self.cache.close()

        if not hops:
            messagebox.showinfo("No Hops", "No hops found in inventory. Please add hops to inventory first.")
            return

        dialog = AddHopsDialog(self, hops)
        self.wait_window(dialog)

        if hasattr(dialog, 'result') and dialog.result:
            self.hops_list.append(dialog.result)
            self.refresh_list()

    def remove_hops(self):
        """Remove selected hops"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select hops to remove.")
            return

        index = self.tree.index(selection[0])
        del self.hops_list[index]
        self.refresh_list()

    def refresh_list(self):
        """Refresh hops list"""
        for item in self.tree.get_children():
            self.tree.delete(item)

        for hop in self.hops_list:
            values = (
                hop['material_name'],
                f"{hop['quantity']:.2f}",
                hop['unit'],
                f"{hop.get('boil_time', 0):.0f}",
                f"{hop.get('alpha_acid', 0):.1f}%",
                hop.get('addition_type', 'Boil')
            )
            self.tree.insert('', 'end', values=values)


class YeastTab(tk.Frame):
    """Tab for yeast"""

    def __init__(self, parent, cache, yeast_list, dialog):
        super().__init__(parent, bg='white')
        self.cache = cache
        self.yeast_list = yeast_list
        self.dialog = dialog

        self.create_widgets()

    def create_widgets(self):
        """Create yeast tab widgets"""
        # Toolbar
        toolbar = tk.Frame(self, bg='white')
        toolbar.pack(fill=tk.X, padx=20, pady=15)

        tk.Button(toolbar, text="➕ Add Yeast", font=('Arial', 10, 'bold'),
                 bg='#4CAF50', fg='white', cursor='hand2',
                 command=self.add_yeast, padx=15, pady=8).pack(side=tk.LEFT, padx=(0,10))

        tk.Button(toolbar, text="🗑️ Remove", font=('Arial', 10),
                 bg='#f44336', fg='white', cursor='hand2',
                 command=self.remove_yeast, padx=15, pady=8).pack(side=tk.LEFT)

        # Yeast list
        list_frame = tk.Frame(self, bg='white', relief=tk.SOLID, borderwidth=1)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0,20))

        vsb = tk.Scrollbar(list_frame, orient="vertical")
        vsb.pack(side=tk.RIGHT, fill=tk.Y)

        columns = ('Yeast Strain', 'Quantity', 'Unit', 'Notes')
        self.tree = ttk.Treeview(list_frame, columns=columns, show='headings',
                                yscrollcommand=vsb.set, height=10)

        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=200)

        self.tree.pack(fill=tk.BOTH, expand=True)
        vsb.config(command=self.tree.yview)

    def add_yeast(self):
        """Add yeast from inventory"""
        self.cache.connect()
        yeasts = self.cache.get_all_records('inventory_materials', "material_type = 'yeast'", order_by='material_name')
        self.cache.close()

        if not yeasts:
            messagebox.showinfo("No Yeast", "No yeast found in inventory. Please add yeast to inventory first.")
            return

        dialog = AddIngredientDialog(self, yeasts, 'yeast')
        self.wait_window(dialog)

        if hasattr(dialog, 'result') and dialog.result:
            self.yeast_list.append(dialog.result)
            self.refresh_list()

    def remove_yeast(self):
        """Remove selected yeast"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select yeast to remove.")
            return

        index = self.tree.index(selection[0])
        del self.yeast_list[index]
        self.refresh_list()

    def refresh_list(self):
        """Refresh yeast list"""
        for item in self.tree.get_children():
            self.tree.delete(item)

        for yeast in self.yeast_list:
            values = (
                yeast['material_name'],
                f"{yeast['quantity']:.2f}",
                yeast['unit'],
                yeast.get('notes', '')
            )
            self.tree.insert('', 'end', values=values)


class AddIngredientDialog(tk.Toplevel):
    """Dialog for adding ingredient (grain/adjunct/yeast)"""

    def __init__(self, parent, materials, ingredient_type):
        super().__init__(parent)
        self.materials = materials
        self.ingredient_type = ingredient_type
        self.result = None

        self.title(f"Add {ingredient_type.capitalize()}")
        self.geometry("500x350")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        self.create_widgets()

    def create_widgets(self):
        """Create dialog widgets"""
        frame = tk.Frame(self, bg='white', padx=20, pady=20)
        frame.pack(fill=tk.BOTH, expand=True)

        # Material selection
        tk.Label(frame, text=f"Select {self.ingredient_type.capitalize()} *", font=('Arial', 10, 'bold'), bg='white').pack(anchor='w', pady=(0,5))

        self.material_var = tk.StringVar()
        material_names = [f"{m['material_name']} ({m['current_stock']:.1f} {m['unit']} in stock)" for m in self.materials]
        material_combo = ttk.Combobox(frame, textvariable=self.material_var, values=material_names,
                                     font=('Arial', 10), width=50, state='readonly')
        material_combo.pack(fill=tk.X, pady=(0,15))

        # Quantity
        tk.Label(frame, text="Quantity *", font=('Arial', 10, 'bold'), bg='white').pack(anchor='w', pady=(0,5))
        self.qty_entry = tk.Entry(frame, font=('Arial', 10), width=20)
        self.qty_entry.pack(anchor='w', pady=(0,15))

        # Unit
        tk.Label(frame, text="Unit *", font=('Arial', 10, 'bold'), bg='white').pack(anchor='w', pady=(0,5))
        self.unit_var = tk.StringVar(value='kg')
        units = ['kg', 'g', 'lb', 'oz', 'L', 'ml', 'packets', 'tsp', 'tbsp']
        unit_combo = ttk.Combobox(frame, textvariable=self.unit_var, values=units,
                                 font=('Arial', 10), width=15, state='readonly')
        unit_combo.pack(anchor='w', pady=(0,15))

        # Notes
        notes_label = "Mash Notes" if self.ingredient_type == 'grain' else "Timing/Notes" if self.ingredient_type == 'adjunct' else "Starter Notes"
        tk.Label(frame, text=notes_label, font=('Arial', 10, 'bold'), bg='white').pack(anchor='w', pady=(0,5))
        self.notes_entry = tk.Entry(frame, font=('Arial', 10), width=50)
        self.notes_entry.pack(fill=tk.X, pady=(0,15))

        # Buttons
        button_frame = tk.Frame(self, bg='white', pady=10)
        button_frame.pack(fill=tk.X, padx=20)

        tk.Button(button_frame, text="Cancel", font=('Arial', 10), bg='#757575', fg='white',
                 command=self.destroy, padx=20, pady=8).pack(side=tk.RIGHT, padx=(10,0))
        tk.Button(button_frame, text="Add", font=('Arial', 10, 'bold'), bg='#4CAF50', fg='white',
                 command=self.add, padx=20, pady=8).pack(side=tk.RIGHT)

    def add(self):
        """Add ingredient"""
        if not self.material_var.get():
            messagebox.showerror("Error", "Please select a material.")
            return

        try:
            qty = float(self.qty_entry.get())
        except ValueError:
            messagebox.showerror("Error", "Invalid quantity.")
            return

        # Get selected material
        material_index = [f"{m['material_name']} ({m['current_stock']:.1f} {m['unit']} in stock)"
                         for m in self.materials].index(self.material_var.get())
        material = self.materials[material_index]

        self.result = {
            'material_id': material['material_id'],
            'material_name': material['material_name'],
            'quantity': qty,
            'unit': self.unit_var.get(),
            'notes': self.notes_entry.get().strip()
        }
        self.destroy()


class AddHopsDialog(tk.Toplevel):
    """Dialog for adding hops with brewing-specific fields"""

    def __init__(self, parent, hops):
        super().__init__(parent)
        self.hops = hops
        self.result = None

        self.title("Add Hops")
        self.geometry("500x450")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        self.create_widgets()

    def create_widgets(self):
        """Create dialog widgets"""
        frame = tk.Frame(self, bg='white', padx=20, pady=20)
        frame.pack(fill=tk.BOTH, expand=True)

        # Hop selection
        tk.Label(frame, text="Select Hop Variety *", font=('Arial', 10, 'bold'), bg='white').pack(anchor='w', pady=(0,5))

        self.hop_var = tk.StringVar()
        hop_names = [f"{h['material_name']} ({h['current_stock']:.1f} {h['unit']} in stock)" for h in self.hops]
        hop_combo = ttk.Combobox(frame, textvariable=self.hop_var, values=hop_names,
                                font=('Arial', 10), width=50, state='readonly')
        hop_combo.pack(fill=tk.X, pady=(0,15))

        # Quantity
        tk.Label(frame, text="Quantity *", font=('Arial', 10, 'bold'), bg='white').pack(anchor='w', pady=(0,5))
        self.qty_entry = tk.Entry(frame, font=('Arial', 10), width=20)
        self.qty_entry.pack(anchor='w', pady=(0,15))

        # Unit
        tk.Label(frame, text="Unit *", font=('Arial', 10, 'bold'), bg='white').pack(anchor='w', pady=(0,5))
        self.unit_var = tk.StringVar(value='g')
        units = ['kg', 'g', 'oz', 'lb']
        unit_combo = ttk.Combobox(frame, textvariable=self.unit_var, values=units,
                                 font=('Arial', 10), width=15, state='readonly')
        unit_combo.pack(anchor='w', pady=(0,15))

        # Boil time
        tk.Label(frame, text="Boil Time (minutes) *", font=('Arial', 10, 'bold'), bg='white').pack(anchor='w', pady=(0,5))
        self.boil_time_entry = tk.Entry(frame, font=('Arial', 10), width=15)
        self.boil_time_entry.insert(0, "60")
        self.boil_time_entry.pack(anchor='w', pady=(0,15))

        # Alpha acid
        tk.Label(frame, text="Alpha Acid % *", font=('Arial', 10, 'bold'), bg='white').pack(anchor='w', pady=(0,5))
        self.aa_entry = tk.Entry(frame, font=('Arial', 10), width=15)
        self.aa_entry.insert(0, "5.0")
        self.aa_entry.pack(anchor='w', pady=(0,15))

        # Addition type
        tk.Label(frame, text="Addition Type *", font=('Arial', 10, 'bold'), bg='white').pack(anchor='w', pady=(0,5))
        self.addition_var = tk.StringVar(value='Boil')
        addition_types = ['First Wort', 'Boil', 'Whirlpool', 'Dry Hop']
        addition_combo = ttk.Combobox(frame, textvariable=self.addition_var, values=addition_types,
                                     font=('Arial', 10), width=20, state='readonly')
        addition_combo.pack(anchor='w', pady=(0,15))

        # Buttons
        button_frame = tk.Frame(self, bg='white', pady=10)
        button_frame.pack(fill=tk.X, padx=20)

        tk.Button(button_frame, text="Cancel", font=('Arial', 10), bg='#757575', fg='white',
                 command=self.destroy, padx=20, pady=8).pack(side=tk.RIGHT, padx=(10,0))
        tk.Button(button_frame, text="Add", font=('Arial', 10, 'bold'), bg='#4CAF50', fg='white',
                 command=self.add, padx=20, pady=8).pack(side=tk.RIGHT)

    def add(self):
        """Add hops"""
        if not self.hop_var.get():
            messagebox.showerror("Error", "Please select a hop variety.")
            return

        try:
            qty = float(self.qty_entry.get())
            boil_time = float(self.boil_time_entry.get())
            aa = float(self.aa_entry.get())
        except ValueError:
            messagebox.showerror("Error", "Invalid number format.")
            return

        # Get selected hop
        hop_index = [f"{h['material_name']} ({h['current_stock']:.1f} {h['unit']} in stock)"
                    for h in self.hops].index(self.hop_var.get())
        hop = self.hops[hop_index]

        self.result = {
            'material_id': hop['material_id'],
            'material_name': hop['material_name'],
            'quantity': qty,
            'unit': self.unit_var.get(),
            'boil_time': boil_time,
            'alpha_acid': aa,
            'addition_type': self.addition_var.get()
        }
        self.destroy()


class RecipeViewDialog(tk.Toplevel):
    """Dialog for viewing complete recipe details"""

    def __init__(self, parent, cache, recipe_id):
        super().__init__(parent)
        self.cache = cache
        self.recipe_id = recipe_id

        self.title("Recipe Details")
        self.geometry("800x600")
        self.resizable(True, True)
        self.transient(parent)

        self.create_widgets()
        self.load_recipe()

    def create_widgets(self):
        """Create view dialog widgets"""
        # Text area with scrollbar
        text_frame = tk.Frame(self)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        vsb = tk.Scrollbar(text_frame, orient="vertical")
        vsb.pack(side=tk.RIGHT, fill=tk.Y)

        self.text = tk.Text(text_frame, font=('Courier', 10), wrap=tk.WORD,
                           yscrollcommand=vsb.set, state=tk.DISABLED)
        self.text.pack(fill=tk.BOTH, expand=True)
        vsb.config(command=self.text.yview)

        # Close button
        tk.Button(self, text="Close", font=('Arial', 10), bg='#757575', fg='white',
                 command=self.destroy, padx=20, pady=8).pack(pady=(0,20))

    def load_recipe(self):
        """Load and display recipe"""
        self.cache.connect()

        # Get recipe
        recipes = self.cache.get_all_records('recipes', f"recipe_id = '{self.recipe_id}'")
        if not recipes:
            self.cache.close()
            return

        recipe = recipes[0]

        # Build recipe text
        text = f"{'='*70}\n"
        text += f"  {recipe['recipe_name'].upper()}\n"
        text += f"{'='*70}\n\n"
        text += f"Style: {recipe.get('style', 'N/A')}\n"
        text += f"Target ABV: {recipe.get('target_abv', 0):.1f}%\n"
        text += f"Batch Size: {recipe.get('target_batch_size_litres', 0):.0f} L\n"
        text += f"Version: {recipe.get('version', 1)}\n"
        text += f"\n{'-'*70}\n\n"

        # Grains
        grains = self.cache.get_all_records('recipe_grains', f"recipe_id = '{self.recipe_id}'")
        if grains:
            text += "GRAIN BILL:\n\n"
            for grain in grains:
                material = self.cache.get_all_records('inventory_materials', f"material_id = '{grain['material_id']}'")
                if material:
                    text += f"  • {material[0]['material_name']}: {grain['quantity']:.2f} {grain['unit']}"
                    if grain.get('mash_notes'):
                        text += f" ({grain['mash_notes']})"
                    text += "\n"
            text += f"\n{'-'*70}\n\n"

        # Hops
        hops = self.cache.get_all_records('recipe_hops', f"recipe_id = '{self.recipe_id}'")
        if hops:
            text += "HOPS SCHEDULE:\n\n"
            for hop in hops:
                material = self.cache.get_all_records('inventory_materials', f"material_id = '{hop['material_id']}'")
                if material:
                    text += f"  • {material[0]['material_name']}: {hop['quantity']:.2f} {hop['unit']}"
                    if hop.get('addition_type') == 'Boil':
                        text += f" @ {hop.get('boil_time_minutes', 0):.0f} min"
                    else:
                        text += f" ({hop.get('addition_type', 'Boil')})"
                    text += f" - {hop.get('alpha_acid_percent', 0):.1f}% AA"
                    text += "\n"
            text += f"\n{'-'*70}\n\n"

        # Yeast
        yeasts = self.cache.get_all_records('recipe_yeast', f"recipe_id = '{self.recipe_id}'")
        if yeasts:
            text += "YEAST:\n\n"
            for yeast in yeasts:
                material = self.cache.get_all_records('inventory_materials', f"material_id = '{yeast['material_id']}'")
                if material:
                    text += f"  • {material[0]['material_name']}: {yeast['quantity']:.2f} {yeast['unit']}"
                    if yeast.get('notes'):
                        text += f" ({yeast['notes']})"
                    text += "\n"
            text += f"\n{'-'*70}\n\n"

        # Adjuncts
        adjuncts = self.cache.get_all_records('recipe_adjuncts', f"recipe_id = '{self.recipe_id}'")
        if adjuncts:
            text += "ADJUNCTS & SUNDRIES:\n\n"
            for adjunct in adjuncts:
                material = self.cache.get_all_records('inventory_materials', f"material_id = '{adjunct['material_id']}'")
                if material:
                    text += f"  • {material[0]['material_name']}: {adjunct['quantity']:.2f} {adjunct['unit']}"
                    if adjunct.get('timing'):
                        text += f" ({adjunct['timing']})"
                    text += "\n"
            text += f"\n{'-'*70}\n\n"

        # Brewing notes
        if recipe.get('brewing_notes'):
            text += "BREWING NOTES:\n\n"
            text += f"{recipe['brewing_notes']}\n"
            text += f"\n{'-'*70}\n\n"

        text += f"\nCreated: {recipe.get('created_date', 'N/A')} by {recipe.get('created_by', 'N/A')}\n"
        text += f"Last Modified: {recipe.get('last_modified', 'N/A')}\n"

        self.cache.close()

        # Display text
        self.text.config(state=tk.NORMAL)
        self.text.insert('1.0', text)
        self.text.config(state=tk.DISABLED)
