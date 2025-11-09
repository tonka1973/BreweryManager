"""
Recipes Module for Brewery Management System
Manages beer recipes with ingredients and scaling
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import uuid
from datetime import datetime
from typing import Optional


class RecipesModule(tk.Frame):
    """Recipes module for creating and managing beer recipes"""

    def __init__(self, parent, cache_manager, current_user):
        """
        Initialize the Recipes module.

        Args:
            parent: Parent widget
            cache_manager: SQLiteCacheManager instance
            current_user: Current logged-in user
        """
        super().__init__(parent, bg='white')
        self.cache = cache_manager
        self.current_user = current_user

        # Create module layout
        self.create_widgets()
        self.load_recipes()

    def create_widgets(self):
        """Create all recipe widgets"""
        # Toolbar
        toolbar = tk.Frame(self, bg='white')
        toolbar.pack(fill=tk.X, padx=20, pady=(0, 10))

        # Add Recipe button
        add_btn = tk.Button(
            toolbar,
            text="➕ New Recipe",
            font=('Arial', 10, 'bold'),
            bg='#4CAF50',
            fg='white',
            cursor='hand2',
            command=self.add_recipe,
            padx=15,
            pady=8
        )
        add_btn.pack(side=tk.LEFT, padx=(0, 10))

        # Refresh button
        refresh_btn = tk.Button(
            toolbar,
            text="🔄 Refresh",
            font=('Arial', 10),
            bg='#607D8B',
            fg='white',
            cursor='hand2',
            command=self.load_recipes,
            padx=15,
            pady=8
        )
        refresh_btn.pack(side=tk.LEFT)

        # Search box
        search_frame = tk.Frame(toolbar, bg='white')
        search_frame.pack(side=tk.RIGHT)

        search_label = tk.Label(
            search_frame,
            text="Search:",
            font=('Arial', 10),
            bg='white'
        )
        search_label.pack(side=tk.LEFT, padx=(0, 5))

        self.search_var = tk.StringVar()
        self.search_var.trace('w', lambda *args: self.load_recipes())

        search_entry = tk.Entry(
            search_frame,
            textvariable=self.search_var,
            font=('Arial', 10),
            width=20
        )
        search_entry.pack(side=tk.LEFT)

        # Container for list and info panel
        content_container = tk.Frame(self, bg='white')
        content_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))

        # Recipes list (top half)
        list_frame = tk.Frame(content_container, bg='white', relief=tk.SOLID, borderwidth=1)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # Scrollbars
        vsb = tk.Scrollbar(list_frame, orient="vertical")
        vsb.pack(side=tk.RIGHT, fill=tk.Y)

        hsb = tk.Scrollbar(list_frame, orient="horizontal")
        hsb.pack(side=tk.BOTTOM, fill=tk.X)

        # Treeview
        columns = ('Name', 'Style', 'ABV %', 'Batch Size (L)', 'Version', 'Status', 'Edit', 'Delete')
        self.recipes_tree = ttk.Treeview(
            list_frame,
            columns=columns,
            show='headings',
            yscrollcommand=vsb.set,
            xscrollcommand=hsb.set
        )

        # Column headings
        self.recipes_tree.heading('Name', text='Recipe Name')
        self.recipes_tree.heading('Style', text='Style')
        self.recipes_tree.heading('ABV %', text='ABV %')
        self.recipes_tree.heading('Batch Size (L)', text='Batch Size (L)')
        self.recipes_tree.heading('Version', text='Version')
        self.recipes_tree.heading('Status', text='Status')
        self.recipes_tree.heading('Edit', text='Edit')
        self.recipes_tree.heading('Delete', text='Delete')

        # Column widths
        self.recipes_tree.column('Name', width=200)
        self.recipes_tree.column('Style', width=130)
        self.recipes_tree.column('ABV %', width=80)
        self.recipes_tree.column('Batch Size (L)', width=100)
        self.recipes_tree.column('Version', width=60)
        self.recipes_tree.column('Status', width=80)
        self.recipes_tree.column('Edit', width=50, anchor='center')
        self.recipes_tree.column('Delete', width=50, anchor='center')

        self.recipes_tree.pack(fill=tk.BOTH, expand=True)

        vsb.config(command=self.recipes_tree.yview)
        hsb.config(command=self.recipes_tree.xview)

        # Double-click to edit recipe
        self.recipes_tree.bind('<Double-1>', lambda e: self.edit_recipe())

        # Single-click to handle edit/delete buttons and show info
        self.recipes_tree.bind('<Button-1>', self.on_tree_click)

        # Selection change to show info
        self.recipes_tree.bind('<<TreeviewSelect>>', self.on_recipe_select)

        # Recipe info panel (bottom half)
        info_frame = tk.Frame(content_container, bg='white', relief=tk.SOLID, borderwidth=1)
        info_frame.pack(fill=tk.BOTH, expand=True)

        # Info panel header
        info_header = tk.Frame(info_frame, bg='#2196F3', height=35)
        info_header.pack(fill=tk.X)
        info_header.pack_propagate(False)

        tk.Label(
            info_header,
            text="Recipe Information",
            font=('Arial', 11, 'bold'),
            bg='#2196F3',
            fg='white'
        ).pack(side=tk.LEFT, padx=10, pady=5)

        # Scrollable info content
        info_canvas = tk.Canvas(info_frame, bg='white')
        info_scrollbar = tk.Scrollbar(info_frame, orient="vertical", command=info_canvas.yview)
        self.info_content = tk.Frame(info_canvas, bg='white')

        self.info_content.bind(
            "<Configure>",
            lambda e: info_canvas.configure(scrollregion=info_canvas.bbox("all"))
        )

        info_canvas.create_window((0, 0), window=self.info_content, anchor="nw")
        info_canvas.configure(yscrollcommand=info_scrollbar.set)

        info_canvas.pack(side="left", fill="both", expand=True)
        info_scrollbar.pack(side="right", fill="y")

        # Initial message
        self.show_no_selection_message()

    def load_recipes(self):
        """Load recipes from database"""
        # Clear existing
        for item in self.recipes_tree.get_children():
            self.recipes_tree.delete(item)

        # Get search term
        search = self.search_var.get().lower()

        # Get recipes
        self.cache.connect()
        recipes = self.cache.get_all_records('recipes', order_by='recipe_name')
        self.cache.close()

        # Filter and display
        for recipe in recipes:
            name = recipe.get('recipe_name', '')
            style = recipe.get('style', '')

            # Apply search filter
            if search and search not in name.lower() and search not in style.lower():
                continue

            abv = recipe.get('target_abv', 0.0)
            batch_size = recipe.get('target_batch_size_litres', 0.0)
            version = recipe.get('version', 1)
            is_active = recipe.get('is_active', 1)
            status = 'Active' if is_active else 'Inactive'

            values = (name, style, f"{abv:.1f}", f"{batch_size:.0f}", version, status, '✏️', '🗑️')

            # Color code by status
            tag = 'active' if is_active else 'inactive'
            item_id = self.recipes_tree.insert('', 'end', values=values, tags=(tag, recipe['recipe_id']))

        # Tag colors
        self.recipes_tree.tag_configure('active', background='#e8f5e9')
        self.recipes_tree.tag_configure('inactive', background='#ffebee')

    def select_recipe_by_id(self, recipe_id):
        """Find and select a recipe by its ID in the tree"""
        for item in self.recipes_tree.get_children():
            tags = self.recipes_tree.item(item, 'tags')
            if len(tags) > 1 and tags[1] == recipe_id:
                self.recipes_tree.selection_set(item)
                self.recipes_tree.see(item)  # Scroll to make it visible
                self.on_recipe_select()  # Update info panel
                break

    def on_tree_click(self, event):
        """Handle clicks on tree items, especially Edit and Delete columns"""
        region = self.recipes_tree.identify_region(event.x, event.y)
        if region != "cell":
            return

        column = self.recipes_tree.identify_column(event.x)
        row = self.recipes_tree.identify_row(event.y)

        if not row:
            return

        # Column #7 is Edit, #8 is Delete (0-indexed: #6 and #7)
        if column == '#7':  # Edit column
            self.recipes_tree.selection_set(row)
            self.edit_recipe()
        elif column == '#8':  # Delete column
            self.recipes_tree.selection_set(row)
            self.delete_recipe()

    def on_recipe_select(self, event=None):
        """Update info panel when a recipe is selected"""
        selection = self.recipes_tree.selection()
        if not selection:
            self.show_no_selection_message()
            return

        # Get recipe ID from tags
        tags = self.recipes_tree.item(selection[0], 'tags')
        recipe_id = tags[1] if len(tags) > 1 else None

        if not recipe_id:
            self.show_no_selection_message()
            return

        # Get recipe data
        self.cache.connect()
        recipes = self.cache.get_all_records('recipes', f"recipe_id = '{recipe_id}'")
        ingredients = self.cache.get_all_records('recipe_ingredients', f"recipe_id = '{recipe_id}'", order_by='timing, ingredient_type')
        self.cache.close()

        if not recipes:
            self.show_no_selection_message()
            return

        self.update_recipe_info(recipes[0], ingredients)

    def show_no_selection_message(self):
        """Show message when no recipe is selected"""
        # Clear info content
        for widget in self.info_content.winfo_children():
            widget.destroy()

        tk.Label(
            self.info_content,
            text="Select a recipe to view its details",
            font=('Arial', 11, 'italic'),
            fg='#999',
            bg='white'
        ).pack(padx=20, pady=40)

    def update_recipe_info(self, recipe, ingredients):
        """Update the info panel with recipe details"""
        # Clear info content
        for widget in self.info_content.winfo_children():
            widget.destroy()

        content = tk.Frame(self.info_content, bg='white', padx=20, pady=15)
        content.pack(fill=tk.BOTH, expand=True)

        # Recipe name
        tk.Label(
            content,
            text=recipe.get('recipe_name', 'Unknown'),
            font=('Arial', 14, 'bold'),
            bg='white'
        ).pack(anchor='w', pady=(0, 10))

        # Recipe details in a grid
        details_frame = tk.Frame(content, bg='white')
        details_frame.pack(fill=tk.X, pady=(0, 10))

        info_items = [
            ("Style:", recipe.get('style', 'N/A')),
            ("Target ABV:", f"{recipe.get('target_abv', 0.0)}%"),
            ("Batch Size:", f"{recipe.get('target_batch_size_litres', 0.0)} litres"),
            ("Version:", str(recipe.get('version', 1))),
            ("Status:", 'Active' if recipe.get('is_active') else 'Inactive'),
            ("Created:", f"{recipe.get('created_date', 'N/A')} by {recipe.get('created_by', 'Unknown')}"),
            ("Last Modified:", recipe.get('last_modified', 'N/A'))
        ]

        for i, (label, value) in enumerate(info_items):
            row = i // 2
            col = (i % 2) * 2

            tk.Label(
                details_frame,
                text=label,
                font=('Arial', 9, 'bold'),
                bg='white',
                fg='#555'
            ).grid(row=row, column=col, sticky='w', padx=(0, 5), pady=2)

            tk.Label(
                details_frame,
                text=value,
                font=('Arial', 9),
                bg='white'
            ).grid(row=row, column=col+1, sticky='w', padx=(0, 20), pady=2)

        # Brewing Notes
        if recipe.get('brewing_notes'):
            tk.Label(
                content,
                text="Brewing Notes:",
                font=('Arial', 10, 'bold'),
                bg='white'
            ).pack(anchor='w', pady=(10, 5))

            notes_frame = tk.Frame(content, bg='#f5f5f5', relief=tk.SOLID, borderwidth=1)
            notes_frame.pack(fill=tk.X, pady=(0, 10))

            tk.Label(
                notes_frame,
                text=recipe.get('brewing_notes', ''),
                font=('Arial', 9),
                bg='#f5f5f5',
                justify=tk.LEFT,
                wraplength=500
            ).pack(padx=10, pady=8, anchor='w')

        # Ingredients
        tk.Label(
            content,
            text="Ingredients:",
            font=('Arial', 10, 'bold'),
            bg='white'
        ).pack(anchor='w', pady=(10, 5))

        if ingredients:
            for ing in ingredients:
                ing_frame = tk.Frame(content, bg='#e3f2fd', relief=tk.FLAT, borderwidth=1)
                ing_frame.pack(fill=tk.X, pady=2)

                ing_text = f"{ing.get('ingredient_name', 'Unknown')} - {ing.get('quantity', 0)} {ing.get('unit', '')} ({ing.get('ingredient_type', 'N/A')})"
                if ing.get('timing'):
                    ing_text += f" - {ing.get('timing')}"

                tk.Label(
                    ing_frame,
                    text=ing_text,
                    font=('Arial', 9),
                    bg='#e3f2fd',
                    anchor='w'
                ).pack(padx=8, pady=4, fill=tk.X)

                if ing.get('notes'):
                    tk.Label(
                        ing_frame,
                        text=f"  Note: {ing.get('notes')}",
                        font=('Arial', 8, 'italic'),
                        bg='#e3f2fd',
                        fg='#555',
                        anchor='w'
                    ).pack(padx=16, pady=(0, 4), fill=tk.X)
        else:
            tk.Label(
                content,
                text="No ingredients added yet.",
                font=('Arial', 9, 'italic'),
                bg='white',
                fg='#999'
            ).pack(anchor='w')

    def add_recipe(self):
        """Open dialog to add new recipe"""
        dialog = RecipeDialog(self, self.cache, self.current_user, mode='add')
        self.wait_window(dialog)

        # Get the recipe_id that was just created (if any)
        recipe_id = getattr(dialog, 'saved_recipe_id', None)

        self.load_recipes()

        # Re-select the newly created recipe
        if recipe_id:
            self.select_recipe_by_id(recipe_id)

    def edit_recipe(self):
        """Edit selected recipe"""
        selection = self.recipes_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a recipe to edit.")
            return

        # Get recipe ID from tags
        tags = self.recipes_tree.item(selection[0], 'tags')
        recipe_id = tags[1] if len(tags) > 1 else None

        if not recipe_id:
            messagebox.showerror("Error", "Could not identify recipe.")
            return

        # Get recipe data
        self.cache.connect()
        recipes = self.cache.get_all_records('recipes', f"recipe_id = '{recipe_id}'")
        self.cache.close()

        if not recipes:
            messagebox.showerror("Error", "Recipe not found.")
            return

        recipe = recipes[0]
        dialog = RecipeDialog(self, self.cache, self.current_user, mode='edit', recipe=recipe)
        self.wait_window(dialog)

        # Get the recipe_id that was just edited (if saved)
        saved_recipe_id = getattr(dialog, 'saved_recipe_id', None)

        self.load_recipes()

        # Re-select the edited recipe
        if saved_recipe_id:
            self.select_recipe_by_id(saved_recipe_id)

    def view_recipe_details(self):
        """View detailed recipe information"""
        selection = self.recipes_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a recipe to view.")
            return

        # Get recipe ID from tags
        tags = self.recipes_tree.item(selection[0], 'tags')
        recipe_id = tags[1] if len(tags) > 1 else None

        if not recipe_id:
            messagebox.showerror("Error", "Could not identify recipe.")
            return

        # Get recipe data
        self.cache.connect()
        recipes = self.cache.get_all_records('recipes', f"recipe_id = '{recipe_id}'")
        ingredients = self.cache.get_all_records('recipe_ingredients', f"recipe_id = '{recipe_id}'", order_by='timing, ingredient_type')
        self.cache.close()

        if not recipes:
            messagebox.showerror("Error", "Recipe not found.")
            return

        recipe = recipes[0]
        dialog = RecipeDetailsDialog(self, recipe, ingredients)
        self.wait_window(dialog)

    def delete_recipe(self):
        """Delete selected recipe"""
        selection = self.recipes_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a recipe to delete.")
            return

        # Get recipe ID from tags
        tags = self.recipes_tree.item(selection[0], 'tags')
        recipe_id = tags[1] if len(tags) > 1 else None

        if not recipe_id:
            messagebox.showerror("Error", "Could not identify recipe.")
            return

        # Confirm deletion
        result = messagebox.askyesno(
            "Confirm Delete",
            "Are you sure you want to delete this recipe?\n\n"
            "This will also delete all associated ingredients.\n"
            "This action cannot be undone."
        )

        if not result:
            return

        # Delete recipe and ingredients
        self.cache.connect()
        self.cache.delete_record('recipes', recipe_id, 'recipe_id')

        # Delete ingredients
        self.cache.cursor.execute(f"DELETE FROM recipe_ingredients WHERE recipe_id = ?", (recipe_id,))
        self.cache.connection.commit()

        self.cache.close()

        messagebox.showinfo("Success", "Recipe deleted successfully.")
        self.load_recipes()


class RecipeDialog(tk.Toplevel):
    """Dialog for adding/editing recipes"""

    def __init__(self, parent, cache_manager, current_user, mode='add', recipe=None):
        super().__init__(parent)
        self.cache = cache_manager
        self.current_user = current_user
        self.mode = mode
        self.recipe = recipe

        self.title("Add Recipe" if mode == 'add' else "Edit Recipe")
        self.geometry("700x900")
        self.resizable(True, True)
        self.transient(parent)
        self.grab_set()

        # Store ingredients list
        self.ingredients = []

        self.create_widgets()

        if mode == 'edit' and recipe:
            self.populate_fields()
            self.load_ingredients()

    def create_widgets(self):
        """Create dialog widgets"""
        # Main container
        main_frame = tk.Frame(self, bg='white', padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Recipe Name
        tk.Label(main_frame, text="Recipe Name *", font=('Arial', 10, 'bold'), bg='white').grid(row=0, column=0, sticky='w', pady=(0, 5))
        self.name_entry = tk.Entry(main_frame, font=('Arial', 10), width=40)
        self.name_entry.grid(row=1, column=0, columnspan=2, sticky='ew', pady=(0, 15))

        # Style
        tk.Label(main_frame, text="Style *", font=('Arial', 10, 'bold'), bg='white').grid(row=2, column=0, sticky='w', pady=(0, 5))
        self.style_entry = tk.Entry(main_frame, font=('Arial', 10), width=40)
        self.style_entry.grid(row=3, column=0, columnspan=2, sticky='ew', pady=(0, 15))

        # Target ABV
        tk.Label(main_frame, text="Target ABV % *", font=('Arial', 10, 'bold'), bg='white').grid(row=4, column=0, sticky='w', pady=(0, 5))
        self.abv_entry = tk.Entry(main_frame, font=('Arial', 10), width=15)
        self.abv_entry.grid(row=5, column=0, sticky='w', pady=(0, 15))

        # Target Batch Size
        tk.Label(main_frame, text="Target Batch Size (Litres) *", font=('Arial', 10, 'bold'), bg='white').grid(row=4, column=1, sticky='w', pady=(0, 5), padx=(20, 0))
        self.batch_size_entry = tk.Entry(main_frame, font=('Arial', 10), width=15)
        self.batch_size_entry.grid(row=5, column=1, sticky='w', pady=(0, 15), padx=(20, 0))

        # Version
        tk.Label(main_frame, text="Version", font=('Arial', 10, 'bold'), bg='white').grid(row=6, column=0, sticky='w', pady=(0, 5))
        self.version_entry = tk.Entry(main_frame, font=('Arial', 10), width=15)
        self.version_entry.insert(0, "1")
        self.version_entry.grid(row=7, column=0, sticky='w', pady=(0, 15))

        # Active checkbox
        self.active_var = tk.IntVar(value=1)
        active_check = tk.Checkbutton(
            main_frame,
            text="Active Recipe",
            variable=self.active_var,
            font=('Arial', 10),
            bg='white'
        )
        active_check.grid(row=7, column=1, sticky='w', pady=(0, 15), padx=(20, 0))

        # Brewing Notes
        tk.Label(main_frame, text="Brewing Notes", font=('Arial', 10, 'bold'), bg='white').grid(row=8, column=0, sticky='w', pady=(0, 5))
        self.notes_text = tk.Text(main_frame, font=('Arial', 10), width=40, height=4)
        self.notes_text.grid(row=9, column=0, columnspan=2, sticky='ew', pady=(0, 15))

        # Ingredients Section
        tk.Label(main_frame, text="Ingredients", font=('Arial', 11, 'bold'), bg='white').grid(row=10, column=0, columnspan=2, sticky='w', pady=(10, 5))

        # Add ingredient button
        add_ing_btn = tk.Button(
            main_frame,
            text="+ Add Ingredient",
            font=('Arial', 9),
            bg='#4CAF50',
            fg='white',
            cursor='hand2',
            command=self.add_ingredient,
            padx=10,
            pady=5
        )
        add_ing_btn.grid(row=11, column=0, sticky='w', pady=(0, 5))

        # Ingredients list frame
        ing_frame = tk.Frame(main_frame, bg='white', relief=tk.SOLID, borderwidth=1)
        ing_frame.grid(row=12, column=0, columnspan=2, sticky='ew', pady=(0, 15))

        # Scrollbar for ingredients
        ing_scroll = tk.Scrollbar(ing_frame, orient="vertical")
        ing_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        # Ingredients listbox
        self.ingredients_listbox = tk.Listbox(
            ing_frame,
            font=('Arial', 9),
            height=8,
            yscrollcommand=ing_scroll.set
        )
        self.ingredients_listbox.pack(fill=tk.BOTH, expand=True)
        ing_scroll.config(command=self.ingredients_listbox.yview)

        # Ingredient action buttons
        ing_btn_frame = tk.Frame(main_frame, bg='white')
        ing_btn_frame.grid(row=13, column=0, columnspan=2, sticky='w', pady=(0, 15))

        edit_ing_btn = tk.Button(
            ing_btn_frame,
            text="Edit Selected",
            font=('Arial', 9),
            bg='#2196F3',
            fg='white',
            cursor='hand2',
            command=self.edit_ingredient,
            padx=10,
            pady=5
        )
        edit_ing_btn.pack(side=tk.LEFT, padx=(0, 5))

        delete_ing_btn = tk.Button(
            ing_btn_frame,
            text="Delete Selected",
            font=('Arial', 9),
            bg='#f44336',
            fg='white',
            cursor='hand2',
            command=self.delete_ingredient,
            padx=10,
            pady=5
        )
        delete_ing_btn.pack(side=tk.LEFT)

        # Configure grid
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_columnconfigure(1, weight=1)

        # Buttons
        button_frame = tk.Frame(self, bg='white', pady=10)
        button_frame.pack(fill=tk.X, padx=20, pady=(0, 20))

        cancel_btn = tk.Button(
            button_frame,
            text="Cancel",
            font=('Arial', 10),
            bg='#757575',
            fg='white',
            cursor='hand2',
            command=self.destroy,
            padx=20,
            pady=8
        )
        cancel_btn.pack(side=tk.RIGHT, padx=(10, 0))

        save_btn = tk.Button(
            button_frame,
            text="Save Recipe",
            font=('Arial', 10, 'bold'),
            bg='#4CAF50',
            fg='white',
            cursor='hand2',
            command=self.save_recipe,
            padx=20,
            pady=8
        )
        save_btn.pack(side=tk.RIGHT)

    def populate_fields(self):
        """Populate fields with existing recipe data"""
        if not self.recipe:
            return

        self.name_entry.insert(0, self.recipe.get('recipe_name', ''))
        self.style_entry.insert(0, self.recipe.get('style', ''))
        self.abv_entry.insert(0, str(self.recipe.get('target_abv', '')))
        self.batch_size_entry.insert(0, str(self.recipe.get('target_batch_size_litres', '')))
        self.version_entry.delete(0, tk.END)
        self.version_entry.insert(0, str(self.recipe.get('version', 1)))
        self.active_var.set(self.recipe.get('is_active', 1))

        notes = self.recipe.get('brewing_notes', '')
        if notes:
            self.notes_text.insert('1.0', notes)

    def load_ingredients(self):
        """Load ingredients for existing recipe"""
        if not self.recipe or 'recipe_id' not in self.recipe:
            return

        self.cache.connect()
        ingredients = self.cache.get_all_records(
            'recipe_ingredients',
            f"recipe_id = '{self.recipe['recipe_id']}'",
            order_by='timing, ingredient_type'
        )
        self.cache.close()

        self.ingredients = []
        for ing in ingredients:
            self.ingredients.append({
                'name': ing.get('ingredient_name', ''),
                'type': ing.get('ingredient_type', ''),
                'quantity': ing.get('quantity', 0),
                'unit': ing.get('unit', ''),
                'timing': ing.get('timing', ''),
                'notes': ing.get('notes', ''),
                'inventory_item_id': ing.get('inventory_item_id', None)
            })

        self.refresh_ingredients_list()

    def refresh_ingredients_list(self):
        """Refresh the ingredients listbox"""
        self.ingredients_listbox.delete(0, tk.END)
        for ing in self.ingredients:
            display = f"{ing['name']} - {ing['quantity']} {ing['unit']} ({ing['type']})"
            if ing.get('timing'):
                display += f" - {ing['timing']}"
            self.ingredients_listbox.insert(tk.END, display)

    def add_ingredient(self):
        """Open dialog to add new ingredient"""
        dialog = IngredientDialog(self, self.cache, mode='add')
        self.wait_window(dialog)

        if hasattr(dialog, 'result') and dialog.result:
            self.ingredients.append(dialog.result)
            self.refresh_ingredients_list()

    def edit_ingredient(self):
        """Edit selected ingredient"""
        selection = self.ingredients_listbox.curselection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select an ingredient to edit.")
            return

        index = selection[0]
        ingredient = self.ingredients[index]

        dialog = IngredientDialog(self, self.cache, mode='edit', ingredient=ingredient)
        self.wait_window(dialog)

        if hasattr(dialog, 'result') and dialog.result:
            self.ingredients[index] = dialog.result
            self.refresh_ingredients_list()

    def delete_ingredient(self):
        """Delete selected ingredient"""
        selection = self.ingredients_listbox.curselection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select an ingredient to delete.")
            return

        index = selection[0]
        result = messagebox.askyesno(
            "Confirm Delete",
            "Are you sure you want to delete this ingredient?"
        )

        if result:
            del self.ingredients[index]
            self.refresh_ingredients_list()

    def save_recipe(self):
        """Save recipe to database"""
        # Validate
        name = self.name_entry.get().strip()
        style = self.style_entry.get().strip()
        abv_str = self.abv_entry.get().strip()
        batch_size_str = self.batch_size_entry.get().strip()

        if not name or not style or not abv_str or not batch_size_str:
            messagebox.showerror("Validation Error", "Please fill in all required fields (*).")
            return

        try:
            abv = float(abv_str)
            batch_size = float(batch_size_str)
        except ValueError:
            messagebox.showerror("Validation Error", "ABV and Batch Size must be numbers.")
            return

        if abv < 0.5 or abv > 20:
            messagebox.showerror("Validation Error", "ABV must be between 0.5% and 20%.")
            return

        if batch_size < 1 or batch_size > 5000:
            messagebox.showerror("Validation Error", "Batch size must be between 1 and 5000 litres.")
            return

        # Prepare data
        version = int(self.version_entry.get() or 1)
        notes = self.notes_text.get('1.0', tk.END).strip()

        if self.mode == 'add':
            # Create new recipe
            recipe_id = str(uuid.uuid4())
            recipe_data = {
                'recipe_id': recipe_id,
                'recipe_name': name,
                'style': style,
                'version': version,
                'target_abv': abv,
                'target_batch_size_litres': batch_size,
                'created_date': datetime.now().strftime('%Y-%m-%d'),
                'created_by': self.current_user.username,
                'last_modified': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'is_active': self.active_var.get(),
                'brewing_notes': notes,
                'sync_status': 'pending'
            }

            self.cache.connect()
            self.cache.insert_record('recipes', recipe_data)

            # Save ingredients
            self.save_ingredients(recipe_id)

            self.cache.close()

            # Store recipe_id so parent can re-select it
            self.saved_recipe_id = recipe_id

            messagebox.showinfo("Success", "Recipe created successfully!")

        else:
            # Update existing recipe
            recipe_id = self.recipe['recipe_id']
            recipe_data = {
                'recipe_name': name,
                'style': style,
                'version': version,
                'target_abv': abv,
                'target_batch_size_litres': batch_size,
                'last_modified': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'is_active': self.active_var.get(),
                'brewing_notes': notes,
                'sync_status': 'pending'
            }

            self.cache.connect()
            self.cache.update_record('recipes', recipe_id, recipe_data, id_column='recipe_id')

            # Delete old ingredients and save new ones
            self.cache.cursor.execute("DELETE FROM recipe_ingredients WHERE recipe_id = ?", (recipe_id,))
            self.cache.connection.commit()
            self.save_ingredients(recipe_id)

            self.cache.close()

            # Store recipe_id so parent can re-select it
            self.saved_recipe_id = recipe_id

            messagebox.showinfo("Success", "Recipe updated successfully!")

        self.destroy()

    def save_ingredients(self, recipe_id):
        """Save ingredients to database"""
        for ing in self.ingredients:
            ingredient_data = {
                'ingredient_id': str(uuid.uuid4()),
                'recipe_id': recipe_id,
                'ingredient_name': ing['name'],
                'ingredient_type': ing['type'],
                'quantity': ing['quantity'],
                'unit': ing['unit'],
                'timing': ing.get('timing', ''),
                'notes': ing.get('notes', ''),
                'inventory_item_id': ing.get('inventory_item_id', None),  # Link to inventory
                'sync_status': 'pending'
            }
            self.cache.insert_record('recipe_ingredients', ingredient_data)


class RecipeDetailsDialog(tk.Toplevel):
    """Dialog for viewing recipe details"""

    def __init__(self, parent, recipe, ingredients):
        super().__init__(parent)
        self.recipe = recipe
        self.ingredients = ingredients

        self.title(f"Recipe: {recipe.get('recipe_name', 'Unknown')}")
        self.geometry("700x600")
        self.resizable(True, True)
        self.transient(parent)
        self.grab_set()

        self.create_widgets()

    def create_widgets(self):
        """Create dialog widgets"""
        # Main container with scrollbar
        canvas = tk.Canvas(self, bg='white')
        scrollbar = tk.Scrollbar(self, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='white')

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Content
        content = tk.Frame(scrollable_frame, bg='white', padx=30, pady=20)
        content.pack(fill=tk.BOTH, expand=True)

        # Recipe info
        tk.Label(
            content,
            text=self.recipe.get('recipe_name', 'Unknown'),
            font=('Arial', 18, 'bold'),
            bg='white'
        ).pack(anchor='w', pady=(0, 10))

        info_text = f"""
Style: {self.recipe.get('style', 'N/A')}
Target ABV: {self.recipe.get('target_abv', 0.0)}%
Batch Size: {self.recipe.get('target_batch_size_litres', 0.0)} litres
Version: {self.recipe.get('version', 1)}
Status: {'Active' if self.recipe.get('is_active') else 'Inactive'}

Created: {self.recipe.get('created_date', 'N/A')} by {self.recipe.get('created_by', 'Unknown')}
Last Modified: {self.recipe.get('last_modified', 'N/A')}
        """

        tk.Label(
            content,
            text=info_text.strip(),
            font=('Arial', 10),
            bg='white',
            justify=tk.LEFT
        ).pack(anchor='w', pady=(0, 20))

        # Brewing Notes
        if self.recipe.get('brewing_notes'):
            tk.Label(
                content,
                text="Brewing Notes:",
                font=('Arial', 11, 'bold'),
                bg='white'
            ).pack(anchor='w', pady=(0, 5))

            notes_frame = tk.Frame(content, bg='#f5f5f5', relief=tk.SOLID, borderwidth=1)
            notes_frame.pack(fill=tk.X, pady=(0, 20))

            tk.Label(
                notes_frame,
                text=self.recipe.get('brewing_notes', ''),
                font=('Arial', 10),
                bg='#f5f5f5',
                justify=tk.LEFT,
                wraplength=600
            ).pack(padx=10, pady=10, anchor='w')

        # Ingredients
        tk.Label(
            content,
            text="Ingredients:",
            font=('Arial', 11, 'bold'),
            bg='white'
        ).pack(anchor='w', pady=(0, 10))

        if self.ingredients:
            for ing in self.ingredients:
                ing_frame = tk.Frame(content, bg='#e3f2fd', relief=tk.FLAT)
                ing_frame.pack(fill=tk.X, pady=2)

                ing_text = f"{ing.get('ingredient_name', 'Unknown')} - {ing.get('quantity', 0)} {ing.get('unit', '')} ({ing.get('ingredient_type', 'N/A')})"
                if ing.get('timing'):
                    ing_text += f" - {ing.get('timing')}"

                tk.Label(
                    ing_frame,
                    text=ing_text,
                    font=('Arial', 10),
                    bg='#e3f2fd',
                    anchor='w'
                ).pack(padx=10, pady=5, fill=tk.X)

                if ing.get('notes'):
                    tk.Label(
                        ing_frame,
                        text=f"  Note: {ing.get('notes')}",
                        font=('Arial', 9, 'italic'),
                        bg='#e3f2fd',
                        fg='#555',
                        anchor='w'
                    ).pack(padx=20, pady=(0, 5), fill=tk.X)
        else:
            tk.Label(
                content,
                text="No ingredients added yet.",
                font=('Arial', 10, 'italic'),
                bg='white',
                fg='#999'
            ).pack(anchor='w')

        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Close button
        button_frame = tk.Frame(self, bg='white', pady=10)
        button_frame.pack(fill=tk.X, padx=20)

        close_btn = tk.Button(
            button_frame,
            text="Close",
            font=('Arial', 10),
            bg='#607D8B',
            fg='white',
            cursor='hand2',
            command=self.destroy,
            padx=20,
            pady=8
        )
        close_btn.pack(side=tk.RIGHT)


class IngredientDialog(tk.Toplevel):
    """Dialog for adding/editing ingredients"""

    def __init__(self, parent, cache_manager, mode='add', ingredient=None):
        super().__init__(parent)
        self.cache = cache_manager
        self.mode = mode
        self.ingredient = ingredient
        self.result = None
        self.inventory_items = {}  # Store inventory items by type

        self.title("Add Ingredient" if mode == 'add' else "Edit Ingredient")
        self.geometry("500x550")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        self.create_widgets()
        self.load_inventory_items()

        if mode == 'edit' and ingredient:
            self.populate_fields()

    def create_widgets(self):
        """Create dialog widgets"""
        main_frame = tk.Frame(self, bg='white', padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Type (moved to top so it can filter name options)
        tk.Label(main_frame, text="Type *", font=('Arial', 10, 'bold'), bg='white').grid(row=0, column=0, sticky='w', pady=(0, 5))
        self.type_var = tk.StringVar(value='Malt')
        type_combo = ttk.Combobox(
            main_frame,
            textvariable=self.type_var,
            values=['Malt', 'Hops', 'Yeast', 'Adjunct', 'Other'],
            font=('Arial', 10),
            state='readonly',
            width=15
        )
        type_combo.grid(row=1, column=0, sticky='w', pady=(0, 15))
        type_combo.bind('<<ComboboxSelected>>', self.on_type_change)

        # Ingredient Name (autocomplete from inventory)
        tk.Label(main_frame, text="Ingredient Name *", font=('Arial', 10, 'bold'), bg='white').grid(row=2, column=0, sticky='w', pady=(0, 5))

        name_frame = tk.Frame(main_frame, bg='white')
        name_frame.grid(row=3, column=0, columnspan=2, sticky='ew', pady=(0, 5))

        self.name_var = tk.StringVar()
        self.name_combo = ttk.Combobox(
            name_frame,
            textvariable=self.name_var,
            font=('Arial', 10),
            width=37
        )
        self.name_combo.pack(fill=tk.X)

        # Enable autocomplete filtering
        self.name_combo.bind('<KeyRelease>', self.on_name_keyrelease)

        # Info label
        self.inventory_info_label = tk.Label(
            main_frame,
            text="Select from inventory or type new name",
            font=('Arial', 8, 'italic'),
            bg='white',
            fg='#666'
        )
        self.inventory_info_label.grid(row=4, column=0, columnspan=2, sticky='w', pady=(0, 15))

        # Quantity
        tk.Label(main_frame, text="Quantity *", font=('Arial', 10, 'bold'), bg='white').grid(row=5, column=0, sticky='w', pady=(0, 5))
        self.quantity_entry = tk.Entry(main_frame, font=('Arial', 10), width=15)
        self.quantity_entry.grid(row=6, column=0, sticky='w', pady=(0, 15))

        # Unit
        tk.Label(main_frame, text="Unit *", font=('Arial', 10, 'bold'), bg='white').grid(row=5, column=1, sticky='w', pady=(0, 5), padx=(20, 0))
        self.unit_var = tk.StringVar(value='kg')
        unit_combo = ttk.Combobox(
            main_frame,
            textvariable=self.unit_var,
            values=['kg', 'g', 'L', 'mL', 'oz', 'lb', 'packets'],
            font=('Arial', 10),
            state='readonly',
            width=10
        )
        unit_combo.grid(row=6, column=1, sticky='w', pady=(0, 15), padx=(20, 0))

        # Timing
        tk.Label(main_frame, text="Timing", font=('Arial', 10, 'bold'), bg='white').grid(row=7, column=0, sticky='w', pady=(0, 5))
        self.timing_var = tk.StringVar()
        timing_combo = ttk.Combobox(
            main_frame,
            textvariable=self.timing_var,
            values=['Mash', '90 min', '60 min', '30 min', '15 min', '10 min', '5 min', 'Flameout', 'Whirlpool', 'Dry hop', 'Primary', 'Secondary'],
            font=('Arial', 10),
            width=15
        )
        timing_combo.grid(row=8, column=0, sticky='w', pady=(0, 15))

        # Notes
        tk.Label(main_frame, text="Notes", font=('Arial', 10, 'bold'), bg='white').grid(row=9, column=0, sticky='w', pady=(0, 5))
        self.notes_text = tk.Text(main_frame, font=('Arial', 10), width=40, height=4)
        self.notes_text.grid(row=10, column=0, columnspan=2, sticky='ew', pady=(0, 15))

        # Configure grid
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_columnconfigure(1, weight=1)

        # Buttons
        button_frame = tk.Frame(self, bg='white', pady=10)
        button_frame.pack(fill=tk.X, padx=20, pady=(0, 20))

        cancel_btn = tk.Button(
            button_frame,
            text="Cancel",
            font=('Arial', 10),
            bg='#757575',
            fg='white',
            cursor='hand2',
            command=self.destroy,
            padx=20,
            pady=8
        )
        cancel_btn.pack(side=tk.RIGHT, padx=(10, 0))

        save_btn = tk.Button(
            button_frame,
            text="Save",
            font=('Arial', 10, 'bold'),
            bg='#4CAF50',
            fg='white',
            cursor='hand2',
            command=self.save_ingredient,
            padx=20,
            pady=8
        )
        save_btn.pack(side=tk.RIGHT)

    def load_inventory_items(self):
        """Load all inventory items from database"""
        self.cache.connect()
        items = self.cache.get_all_records('inventory_materials', order_by='material_name')
        self.cache.close()

        # Map inventory types to recipe types
        type_mapping = {
            'grain': 'Malt',
            'malt': 'Malt',
            'hops': 'Hops',
            'yeast': 'Yeast',
            'adjunct': 'Adjunct',
            'other': 'Other'
        }

        # Organize by type
        for item in items:
            db_type = item.get('material_type', 'other').lower()
            # Map the database type to recipe type
            item_type = type_mapping.get(db_type, 'Other')

            if item_type not in self.inventory_items:
                self.inventory_items[item_type] = []

            self.inventory_items[item_type].append({
                'id': item.get('material_id'),
                'name': item.get('material_name', ''),
                'unit': item.get('unit', 'kg')
            })

        # Update name combo with current type
        self.update_name_options()

    def on_type_change(self, event=None):
        """Update name options when type changes"""
        self.update_name_options()

    def on_name_keyrelease(self, event):
        """Filter combobox values as user types"""
        typed = self.name_var.get().lower()
        if not typed:
            # If empty, show all items for this type
            self.update_name_options()
            return

        # Get all items for current type
        selected_type = self.type_var.get()
        all_items = self.inventory_items.get(selected_type, [])

        # Filter items that contain the typed text
        filtered = [item['name'] for item in all_items if typed in item['name'].lower()]

        # Update combobox with filtered values
        self.name_combo['values'] = filtered

    def update_name_options(self):
        """Update the name combobox based on selected type"""
        selected_type = self.type_var.get()

        # Get items for this type
        items = self.inventory_items.get(selected_type, [])
        item_names = [item['name'] for item in items]

        # Update combobox
        self.name_combo['values'] = item_names

        # Update info label
        if items:
            self.inventory_info_label.config(
                text=f"Found {len(items)} {selected_type} items in inventory - select or type new",
                fg='#2196F3'
            )
        else:
            self.inventory_info_label.config(
                text=f"No {selected_type} items in inventory - type new name",
                fg='#ff9800'
            )

    def populate_fields(self):
        """Populate fields with existing ingredient data"""
        if not self.ingredient:
            return

        self.name_var.set(self.ingredient.get('name', ''))
        self.type_var.set(self.ingredient.get('type', 'Malt'))
        self.quantity_entry.insert(0, str(self.ingredient.get('quantity', '')))
        self.unit_var.set(self.ingredient.get('unit', 'kg'))
        self.timing_var.set(self.ingredient.get('timing', ''))

        notes = self.ingredient.get('notes', '')
        if notes:
            self.notes_text.insert('1.0', notes)

    def save_ingredient(self):
        """Validate and save ingredient"""
        name = self.name_var.get().strip()
        ing_type = self.type_var.get()
        quantity_str = self.quantity_entry.get().strip()
        unit = self.unit_var.get()
        timing = self.timing_var.get().strip()
        notes = self.notes_text.get('1.0', tk.END).strip()

        if not name or not quantity_str:
            messagebox.showerror("Validation Error", "Please fill in name and quantity.")
            return

        try:
            quantity = float(quantity_str)
        except ValueError:
            messagebox.showerror("Validation Error", "Quantity must be a number.")
            return

        if quantity <= 0:
            messagebox.showerror("Validation Error", "Quantity must be greater than 0.")
            return

        # Check if ingredient exists in inventory
        inventory_item_id = self.check_inventory(name, ing_type)

        # If not in inventory, offer to add it
        if not inventory_item_id:
            result = messagebox.askyesno(
                "Add to Inventory?",
                f"'{name}' is not in your inventory.\n\n"
                f"Would you like to add it to your inventory now?\n\n"
                f"This will help track stock levels when using recipes."
            )

            if result:
                inventory_item_id = self.add_to_inventory(name, ing_type, unit)

        self.result = {
            'name': name,
            'type': ing_type,
            'quantity': quantity,
            'unit': unit,
            'timing': timing,
            'notes': notes,
            'inventory_item_id': inventory_item_id  # Link to inventory if exists
        }

        self.destroy()

    def check_inventory(self, name, ing_type):
        """Check if ingredient exists in inventory"""
        # Look in the loaded inventory items
        items = self.inventory_items.get(ing_type, [])
        for item in items:
            if item['name'].lower() == name.lower():
                return item['id']
        return None

    def add_to_inventory(self, name, ing_type, unit):
        """Add ingredient to inventory"""
        try:
            self.cache.connect()

            material_data = {
                'material_id': str(uuid.uuid4()),
                'material_name': name,
                'material_type': ing_type.lower(),
                'current_stock': 0.0,  # Start with zero stock
                'unit': unit,
                'reorder_level': 0.0,
                'supplier': '',
                'cost_per_unit': 0.0,
                'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'sync_status': 'pending'
            }

            self.cache.insert_record('inventory_materials', material_data)
            self.cache.close()

            messagebox.showinfo(
                "Added to Inventory",
                f"'{name}' has been added to your inventory with 0 {unit}.\n\n"
                f"You can add stock levels in the Inventory module."
            )

            return material_data['material_id']

        except Exception as e:
            self.cache.close()
            messagebox.showerror("Error", f"Failed to add to inventory: {str(e)}")
            return None
