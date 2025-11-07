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

        # Edit Recipe button
        edit_btn = tk.Button(
            toolbar,
            text="✏️ Edit Recipe",
            font=('Arial', 10),
            bg='#2196F3',
            fg='white',
            cursor='hand2',
            command=self.edit_recipe,
            padx=15,
            pady=8
        )
        edit_btn.pack(side=tk.LEFT, padx=(0, 10))

        # View Details button
        view_btn = tk.Button(
            toolbar,
            text="👁️ View Details",
            font=('Arial', 10),
            bg='#9C27B0',
            fg='white',
            cursor='hand2',
            command=self.view_recipe_details,
            padx=15,
            pady=8
        )
        view_btn.pack(side=tk.LEFT, padx=(0, 10))

        # Delete Recipe button
        delete_btn = tk.Button(
            toolbar,
            text="🗑️ Delete",
            font=('Arial', 10),
            bg='#f44336',
            fg='white',
            cursor='hand2',
            command=self.delete_recipe,
            padx=15,
            pady=8
        )
        delete_btn.pack(side=tk.LEFT, padx=(0, 10))

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

        # Recipes list
        list_frame = tk.Frame(self, bg='white', relief=tk.SOLID, borderwidth=1)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))

        # Scrollbars
        vsb = tk.Scrollbar(list_frame, orient="vertical")
        vsb.pack(side=tk.RIGHT, fill=tk.Y)

        hsb = tk.Scrollbar(list_frame, orient="horizontal")
        hsb.pack(side=tk.BOTTOM, fill=tk.X)

        # Treeview
        columns = ('Name', 'Style', 'ABV %', 'Batch Size (L)', 'Version', 'Status')
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

        # Column widths
        self.recipes_tree.column('Name', width=250)
        self.recipes_tree.column('Style', width=150)
        self.recipes_tree.column('ABV %', width=100)
        self.recipes_tree.column('Batch Size (L)', width=120)
        self.recipes_tree.column('Version', width=80)
        self.recipes_tree.column('Status', width=100)

        self.recipes_tree.pack(fill=tk.BOTH, expand=True)

        vsb.config(command=self.recipes_tree.yview)
        hsb.config(command=self.recipes_tree.xview)

        # Double-click to view details
        self.recipes_tree.bind('<Double-1>', lambda e: self.view_recipe_details())

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

            values = (name, style, f"{abv:.1f}", f"{batch_size:.0f}", version, status)

            # Color code by status
            tag = 'active' if is_active else 'inactive'
            item_id = self.recipes_tree.insert('', 'end', values=values, tags=(tag, recipe['recipe_id']))

        # Tag colors
        self.recipes_tree.tag_configure('active', background='#e8f5e9')
        self.recipes_tree.tag_configure('inactive', background='#ffebee')

    def add_recipe(self):
        """Open dialog to add new recipe"""
        dialog = RecipeDialog(self, self.cache, self.current_user, mode='add')
        self.wait_window(dialog)
        self.load_recipes()

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
        self.load_recipes()

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
        self.geometry("600x700")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        self.create_widgets()

        if mode == 'edit' and recipe:
            self.populate_fields()

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
        self.notes_text = tk.Text(main_frame, font=('Arial', 10), width=40, height=6)
        self.notes_text.grid(row=9, column=0, columnspan=2, sticky='ew', pady=(0, 15))

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
            self.cache.close()

            messagebox.showinfo("Success", "Recipe created successfully!")

        else:
            # Update existing recipe
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
            self.cache.update_record('recipes', self.recipe['recipe_id'], recipe_data, id_column='recipe_id')
            self.cache.close()

            messagebox.showinfo("Success", "Recipe updated successfully!")

        self.destroy()


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
