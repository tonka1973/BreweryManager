"""
Recipes Module for Brewery Management System
Manages beer recipes with ingredients and scaling
"""

import tkinter as tk
from tkinter import messagebox, simpledialog
import ttkbootstrap as ttk
import uuid
from datetime import datetime
from typing import Optional
from ..utilities.date_utils import format_date_for_display, format_datetime_for_display, get_today_db, get_now_db
from ..utilities.window_manager import get_window_manager, enable_mousewheel_scrolling, enable_treeview_keyboard_navigation, enable_canvas_scrolling
from .components import ScrollableFrame
import logging
import re

logger = logging.getLogger(__name__)


class RecipesModule(ttk.Frame):
    """Recipes module for creating and managing beer recipes"""

    def __init__(self, parent, cache_manager, current_user, sync_callback=None):
        """
        Initialize the Recipes module.

        Args:
            parent: Parent widget
            cache_manager: SQLiteCacheManager instance
            current_user: Current logged-in user
            sync_callback: Optional callback to trigger sync after changes
        """
        super().__init__(parent)
        self.cache = cache_manager
        self.current_user = current_user
        self.sync_callback = sync_callback

        # Create module layout
        self.create_widgets()
        self.load_recipes()

    def create_widgets(self):
        """Create all recipe widgets"""
        # Toolbar
        toolbar = ttk.Frame(self)
        toolbar.pack(fill=tk.X, padx=20, pady=(0, 10))

        # Add Recipe button
        add_btn = ttk.Button(
            toolbar,
            text="+ New Recipe",
            bootstyle="success",
            command=self.add_recipe
        )
        add_btn.pack(side=tk.LEFT, padx=(0, 10))

        # Refresh button
        refresh_btn = ttk.Button(
            toolbar,
            text="Refresh",
            bootstyle="secondary",
            command=self.load_recipes
        )
        refresh_btn.pack(side=tk.LEFT)

        # Search box
        search_frame = ttk.Frame(toolbar)
        search_frame.pack(side=tk.RIGHT)

        search_label = ttk.Label(
            search_frame,
            text="Search:",
            font=('Arial', 10)
        )
        search_label.pack(side=tk.LEFT, padx=(0, 5))

        self.search_var = tk.StringVar()
        self.search_var.trace('w', lambda *args: self.load_recipes())

        search_entry = ttk.Entry(
            search_frame,
            textvariable=self.search_var,
            font=('Arial', 10),
            width=20
        )
        search_entry.pack(side=tk.LEFT)

        # Container for list and info panel
        content_container = ttk.Frame(self)
        content_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))

        # Recipes list (top half)
        list_frame = ttk.Frame(content_container)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # Scrollbars
        vsb = ttk.Scrollbar(list_frame, orient="vertical")
        vsb.pack(side=tk.RIGHT, fill=tk.Y)

        hsb = ttk.Scrollbar(list_frame, orient="horizontal")
        hsb.pack(side=tk.BOTTOM, fill=tk.X)

        # Treeview
        columns = ('Name', 'Style', 'ABV %', 'Batch Size (L)', 'Version', 'Created', 'Status', 'Edit', 'Delete')
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
        self.recipes_tree.heading('Created', text='Created Date')
        self.recipes_tree.heading('Status', text='Status')
        self.recipes_tree.heading('Edit', text='Edit')
        self.recipes_tree.heading('Delete', text='Delete')

        # Column widths
        self.recipes_tree.column('Name', width=200)
        self.recipes_tree.column('Style', width=130)
        self.recipes_tree.column('ABV %', width=80)
        self.recipes_tree.column('Batch Size (L)', width=100)
        self.recipes_tree.column('Version', width=60)
        self.recipes_tree.column('Created', width=100)
        self.recipes_tree.column('Status', width=80)
        self.recipes_tree.column('Edit', width=50, anchor='center')
        self.recipes_tree.column('Delete', width=50, anchor='center')

        self.recipes_tree.pack(fill=tk.BOTH, expand=True)

        vsb.config(command=self.recipes_tree.yview)
        hsb.config(command=self.recipes_tree.xview)

        enable_mousewheel_scrolling(self.recipes_tree)
        enable_treeview_keyboard_navigation(self.recipes_tree)

        # Double-click to edit recipe
        self.recipes_tree.bind('<Double-1>', lambda e: self.edit_recipe())

        # Single-click to handle edit/delete buttons and show info
        self.recipes_tree.bind('<Button-1>', self.on_tree_click)

        # Selection change to show info
        self.recipes_tree.bind('<<TreeviewSelect>>', self.on_recipe_select)

        # Recipe info panel (bottom half)
        info_frame = ttk.Frame(content_container)
        info_frame.pack(fill=tk.BOTH, expand=True)

        # Info panel header
        info_header = ttk.Frame(info_frame)
        info_header.pack(fill=tk.X)

        ttk.Label(
            info_header,
            text="Recipe Information",
            font=('Arial', 11, 'bold')
        ).pack(side=tk.LEFT, padx=10, pady=5)

        # Scrollable info content
        info_canvas = tk.Canvas(info_frame, highlightthickness=0)
        info_scrollbar = ttk.Scrollbar(info_frame, orient="vertical", command=info_canvas.yview)
        self.info_content = ttk.Frame(info_canvas)

        self.info_content.bind(
            "<Configure>",
            lambda e: info_canvas.configure(scrollregion=info_canvas.bbox("all"))
        )

        info_canvas.create_window((0, 0), window=self.info_content, anchor="nw")
        info_canvas.configure(yscrollcommand=info_scrollbar.set)

        info_canvas.pack(side="left", fill="both", expand=True)
        info_scrollbar.pack(side="right", fill="y")

        enable_canvas_scrolling(info_canvas)

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

            # Format created date
            created_date = recipe.get('created_date', '')
            if created_date:
                try:
                    # Convert YYYY-MM-DD to DD/MM/YYYY
                    if '-' in created_date:
                        parts = created_date.split('-')
                        created_display = f"{parts[2]}/{parts[1]}/{parts[0]}"
                    else:
                        created_display = created_date
                except:
                    created_display = created_date
            else:
                created_display = 'N/A'

            values = (name, style, f"{abv:.1f}", f"{batch_size:.0f}", version, created_display, status, '✏️', '🗑️')

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

        ttk.Label(
            self.info_content,
            text="Select a recipe to view its details",
            font=('Arial', 11, 'italic')
        ).pack(padx=20, pady=40)

    def update_recipe_info(self, recipe, ingredients):
        """Update the info panel with recipe details"""
        # Clear info content
        for widget in self.info_content.winfo_children():
            widget.destroy()

        content = ttk.Frame(self.info_content)
        content.pack(fill=tk.BOTH, expand=True, padx=20, pady=15)

        # Recipe name
        ttk.Label(
            content,
            text=recipe.get('recipe_name', 'Unknown'),
            font=('Arial', 14, 'bold')
        ).pack(anchor='w', pady=(0, 10))

        # Recipe details in a grid
        details_frame = ttk.Frame(content)
        details_frame.pack(fill=tk.X, pady=(0, 10))

        info_items = [
            ("Style:", recipe.get('style', 'N/A')),
            ("Target ABV:", f"{recipe.get('target_abv', 0.0)}%"),
            ("Batch Size:", f"{recipe.get('target_batch_size_litres', 0.0)} litres"),
            ("Version:", str(recipe.get('version', 1))),
            ("Status:", 'Active' if recipe.get('is_active') else 'Inactive'),
            ("Created:", f"{format_date_for_display(recipe.get('created_date')) or 'N/A'} by {recipe.get('created_by', 'Unknown')}"),
            ("Last Modified:", format_datetime_for_display(recipe.get('last_modified')) or 'N/A')
        ]

        for i, (label, value) in enumerate(info_items):
            row = i // 2
            col = (i % 2) * 2

            ttk.Label(
                details_frame,
                text=label,
                font=('Arial', 9, 'bold')
            ).grid(row=row, column=col, sticky='w', padx=(0, 5), pady=2)

            ttk.Label(
                details_frame,
                text=value,
                font=('Arial', 9)
            ).grid(row=row, column=col+1, sticky='w', padx=(0, 20), pady=2)

        # Brewing Notes
        if recipe.get('brewing_notes'):
            ttk.Label(
                content,
                text="Brewing Notes:",
                font=('Arial', 10, 'bold')
            ).pack(anchor='w', pady=(10, 5))

            notes_frame = ttk.Frame(content)
            notes_frame.pack(fill=tk.X, pady=(0, 10))

            ttk.Label(
                notes_frame,
                text=recipe.get('brewing_notes', ''),
                font=('Arial', 9),
                justify=tk.LEFT,
                wraplength=500
            ).pack(padx=10, pady=8, anchor='w')

        # Ingredients
        ttk.Label(
            content,
            text="Ingredients:",
            font=('Arial', 10, 'bold')
        ).pack(anchor='w', pady=(10, 5))

        if ingredients:
            for ing in ingredients:
                ing_frame = ttk.Frame(content)
                ing_frame.pack(fill=tk.X, pady=2)

                ing_text = f"{ing.get('ingredient_name', 'Unknown')} - {ing.get('quantity', 0)} {ing.get('unit', '')} ({ing.get('ingredient_type', 'N/A')})"
                if ing.get('timing'):
                    ing_text += f" - {ing.get('timing')}"

                ttk.Label(
                    ing_frame,
                    text=ing_text,
                    font=('Arial', 9)
                ).pack(padx=8, pady=4, fill=tk.X)

                if ing.get('notes'):
                    ttk.Label(
                        ing_frame,
                        text=f"  Note: {ing.get('notes')}",
                        font=('Arial', 8, 'italic')
                    ).pack(padx=16, pady=(0, 4), fill=tk.X)
        else:
            ttk.Label(
                content,
                text="No ingredients added yet.",
                font=('Arial', 9, 'italic')
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
            if self.sync_callback: self.sync_callback()

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
            if self.sync_callback: self.sync_callback()

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
        if self.sync_callback: self.sync_callback()


class RecipeDialog(tk.Toplevel):
    """Dialog for adding/editing recipes"""

    def __init__(self, parent, cache_manager, current_user, mode='add', recipe=None):
        super().__init__(parent)
        self.cache = cache_manager
        self.current_user = current_user
        self.mode = mode
        self.recipe = recipe

        self.title("Add Recipe" if mode == 'add' else "Edit Recipe")
        self.transient(parent)
        self.grab_set()

        # Store ingredients list
        self.ingredients = []

        # Use window manager for sizing if available
        wm = get_window_manager()
        if wm:
            wm.setup_dialog(self, 'recipe_dialog', width_pct=0.5, height_pct=0.7,
                          add_grip=True, save_on_close=True, resizable=True)
        else:
            # Fallback to hardcoded size
            self.geometry("700x600")
            self.resizable(True, True)

        self.create_widgets()

        if mode == 'edit' and recipe:
            self.populate_fields()
            self.load_ingredients()

    def create_widgets(self):
        """Create dialog widgets"""
        # Create button frame first (pack at top)
        button_frame = ttk.Frame(self)
        button_frame.pack(side=tk.TOP, fill=tk.X, padx=20, pady=(0, 20))

        scroll_frame = ScrollableFrame(self)
        scroll_frame.pack(fill=tk.BOTH, expand=True)

        main_frame = ttk.Frame(scroll_frame.inner_frame)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Recipe Name
        ttk.Label(main_frame, text="Recipe Name *", font=('Arial', 10, 'bold')).grid(row=0, column=0, sticky='w', pady=(0, 5), padx=20)
        self.name_entry = ttk.Entry(main_frame, font=('Arial', 10), width=40)
        self.name_entry.grid(row=1, column=0, columnspan=2, sticky='ew', pady=(0, 15), padx=20)

        # Style
        ttk.Label(main_frame, text="Style *", font=('Arial', 10, 'bold')).grid(row=2, column=0, sticky='w', pady=(0, 5), padx=20)
        self.style_entry = ttk.Entry(main_frame, font=('Arial', 10), width=40)
        self.style_entry.grid(row=3, column=0, columnspan=2, sticky='ew', pady=(0, 15), padx=20)

        # Target ABV
        ttk.Label(main_frame, text="Target ABV % *", font=('Arial', 10, 'bold')).grid(row=4, column=0, sticky='w', pady=(0, 5), padx=20)
        self.abv_entry = ttk.Entry(main_frame, font=('Arial', 10), width=15)
        self.abv_entry.grid(row=5, column=0, sticky='w', pady=(0, 15), padx=20)

        # Target Batch Size
        ttk.Label(main_frame, text="Target Batch Size (Litres) *", font=('Arial', 10, 'bold')).grid(row=4, column=1, sticky='w', pady=(0, 5), padx=(20, 0))
        self.batch_size_entry = ttk.Entry(main_frame, font=('Arial', 10), width=15)
        self.batch_size_entry.grid(row=5, column=1, sticky='w', pady=(0, 15), padx=(20, 0))

        # Version
        ttk.Label(main_frame, text="Version", font=('Arial', 10, 'bold')).grid(row=6, column=0, sticky='w', pady=(0, 5), padx=20)
        self.version_entry = ttk.Entry(main_frame, font=('Arial', 10), width=15)
        self.version_entry.insert(0, "1")
        self.version_entry.grid(row=7, column=0, sticky='w', pady=(0, 15), padx=20)

        # Active checkbox
        self.active_var = tk.IntVar(value=1)
        active_check = ttk.Checkbutton(
            main_frame,
            text="Active Recipe",
            variable=self.active_var
        )
        active_check.grid(row=7, column=1, sticky='w', pady=(0, 15), padx=(20, 0))

        # Brewing Notes
        ttk.Label(main_frame, text="Brewing Notes", font=('Arial', 10, 'bold')).grid(row=8, column=0, sticky='w', pady=(0, 5), padx=20)
        self.notes_text = tk.Text(main_frame, font=('Arial', 10), width=40, height=4)
        self.notes_text.grid(row=9, column=0, columnspan=2, sticky='ew', pady=(0, 15), padx=20)

        # Allergens
        ttk.Label(main_frame, text="Allergens (for labels)", font=('Arial', 10, 'bold')).grid(row=10, column=0, sticky='w', pady=(0, 5), padx=20)
        self.allergens_text = tk.Text(main_frame, font=('Arial', 10), width=40, height=2)
        self.allergens_text.grid(row=11, column=0, columnspan=2, sticky='ew', pady=(0, 15), padx=20)
        # Add placeholder hint
        ttk.Label(main_frame, text="e.g., Gluten (Barley), Sulphites", font=('Arial', 9), foreground='gray').grid(row=12, column=0, columnspan=2, sticky='w', padx=20)

        # Ingredients Section
        ttk.Label(main_frame, text="Ingredients", font=('Arial', 11, 'bold')).grid(row=13, column=0, columnspan=2, sticky='w', pady=(10, 5), padx=20)

        # Add ingredient button
        add_ing_btn = ttk.Button(
            main_frame,
            text="+ Add Ingredient",
            bootstyle="success",
            command=self.add_ingredient
        )
        add_ing_btn.grid(row=14, column=0, sticky='w', pady=(0, 5), padx=20)

        # Ingredients list frame
        ing_frame = ttk.Frame(main_frame)
        ing_frame.grid(row=15, column=0, columnspan=2, sticky='ew', pady=(0, 15), padx=20)

        # Scrollbar for ingredients
        ing_scroll = ttk.Scrollbar(ing_frame, orient="vertical")
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
        ing_btn_frame = ttk.Frame(main_frame)
        ing_btn_frame.grid(row=13, column=0, columnspan=2, sticky='w', pady=(0, 15), padx=20)

        edit_ing_btn = ttk.Button(
            ing_btn_frame,
            text="Edit Selected",
            bootstyle="primary",
            command=self.edit_ingredient
        )
        edit_ing_btn.pack(side=tk.LEFT, padx=(0, 5))

        delete_ing_btn = ttk.Button(
            ing_btn_frame,
            text="Delete Selected",
            bootstyle="danger",
            command=self.delete_ingredient
        )
        delete_ing_btn.pack(side=tk.LEFT)

        # Configure grid
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_columnconfigure(1, weight=1)

        # Costing Section
        cost_frame = ttk.LabelFrame(main_frame, text="Cost Estimation", padding=10)
        cost_frame.grid(row=16, column=0, columnspan=2, sticky='ew', pady=(0, 20), padx=20)

        # Cost Inputs
        ttk.Label(cost_frame, text="Labor Cost (£)", font=('Arial', 9)).grid(row=0, column=0, sticky='w', padx=5, pady=5)
        self.labor_cost_entry = ttk.Entry(cost_frame, font=('Arial', 9), width=10)
        self.labor_cost_entry.insert(0, "0.00")
        self.labor_cost_entry.grid(row=0, column=1, sticky='w', padx=5, pady=5)

        ttk.Label(cost_frame, text="Energy Cost (£)", font=('Arial', 9)).grid(row=0, column=2, sticky='w', padx=5, pady=5)
        self.energy_cost_entry = ttk.Entry(cost_frame, font=('Arial', 9), width=10)
        self.energy_cost_entry.insert(0, "0.00")
        self.energy_cost_entry.grid(row=0, column=3, sticky='w', padx=5, pady=5)

        ttk.Label(cost_frame, text="Misc Cost (£)", font=('Arial', 9)).grid(row=0, column=4, sticky='w', padx=5, pady=5)
        self.misc_cost_entry = ttk.Entry(cost_frame, font=('Arial', 9), width=10)
        self.misc_cost_entry.insert(0, "0.00")
        self.misc_cost_entry.grid(row=0, column=5, sticky='w', padx=5, pady=5)

        # Calculate Button
        calc_btn = ttk.Button(cost_frame, text="Calculate Cost", bootstyle="info-outline", command=self.calculate_cost)
        calc_btn.grid(row=0, column=6, rowspan=2, padx=20, sticky='ns')

        # Results
        self.total_cost_label = ttk.Label(cost_frame, text="Total Batch Cost: £0.00", font=('Arial', 11, 'bold'))
        self.total_cost_label.grid(row=1, column=0, columnspan=3, sticky='w', padx=5, pady=5)

        self.cost_per_litre_label = ttk.Label(cost_frame, text="Cost Per Litre: £0.00", font=('Arial', 11, 'bold'))
        self.cost_per_litre_label.grid(row=1, column=3, columnspan=3, sticky='w', padx=5, pady=5)

        # Add buttons to the button_frame created at the top
        cancel_btn = ttk.Button(
            button_frame,
            text="Cancel",
            bootstyle="secondary",
            command=self.destroy
        )
        cancel_btn.pack(side=tk.RIGHT, padx=(10, 0))

        save_btn = ttk.Button(
            button_frame,
            text="Save Recipe",
            bootstyle="success",
            command=self.save_recipe
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
        
        # Populate costs
        self.labor_cost_entry.delete(0, tk.END)
        self.labor_cost_entry.insert(0, f"{self.recipe.get('labor_cost', 0.0):.2f}")
        
        self.energy_cost_entry.delete(0, tk.END)
        self.energy_cost_entry.insert(0, f"{self.recipe.get('energy_cost', 0.0):.2f}")
        
        self.misc_cost_entry.delete(0, tk.END)
        self.misc_cost_entry.insert(0, f"{self.recipe.get('misc_cost', 0.0):.2f}")

        notes = self.recipe.get('brewing_notes', '')
        if notes:
            self.notes_text.insert('1.0', notes)

        allergens = self.recipe.get('allergens', '')
        if allergens:
            self.allergens_text.insert('1.0', allergens)

    def calculate_cost(self):
        """Calculate estimated cost of recipe"""
        try:
            labor = float(self.labor_cost_entry.get() or 0)
            energy = float(self.energy_cost_entry.get() or 0)
            misc = float(self.misc_cost_entry.get() or 0)
            batch_size = float(self.batch_size_entry.get() or 0)
        except ValueError:
            messagebox.showerror("Error", "Invalid cost or batch size values.")
            return

        ingredient_cost = 0.0
        
        self.cache.connect()
        
        for ing in self.ingredients:
            # Check if linked to inventory
            if ing.get('inventory_item_id'):
                materials = self.cache.get_all_records('inventory_materials', f"material_id = '{ing['inventory_item_id']}'")
                if materials:
                    mat = materials[0]
                    cost_per_unit = float(mat.get('cost_per_unit', 0) or 0)
                    inv_unit = mat.get('unit', '').lower()
                    
                    recipe_qty = float(ing.get('quantity', 0) or 0)
                    recipe_unit = ing.get('unit', '').lower()
                    
                    # Unit Conversion
                    factor = 1.0
                    
                    # Same unit
                    if recipe_unit == inv_unit:
                        factor = 1.0
                    # Mass
                    elif recipe_unit == 'g' and inv_unit == 'kg':
                        factor = 0.001
                    elif recipe_unit == 'kg' and inv_unit == 'g':
                        factor = 1000.0
                    elif recipe_unit == 'oz' and inv_unit == 'kg': # Approx
                        factor = 0.0283495
                    elif recipe_unit == 'lb' and inv_unit == 'kg':
                        factor = 0.453592
                    # Volume
                    elif recipe_unit == 'ml' and inv_unit == 'l':
                        factor = 0.001
                    elif recipe_unit == 'l' and inv_unit == 'ml':
                        factor = 1000.0
                    
                    cost = recipe_qty * factor * cost_per_unit
                    ingredient_cost += cost
            else:
                # Try to find by name if no ID (fallback for old data)
                name = ing.get('name', '')
                if name:
                    # Logic to find by name could go here, but safest to rely on ID
                    pass

        self.cache.close()
        
        total = labor + energy + misc + ingredient_cost
        cost_per_litre = total / batch_size if batch_size > 0 else 0

        self.total_cost_label.config(text=f"Total Batch Cost: £{total:.2f}")
        self.cost_per_litre_label.config(text=f"Cost Per Litre: £{cost_per_litre:.2f}")

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
        # Auto-calculate cost significantly improves UX on load
        self.after(500, self.calculate_cost)

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
            self.calculate_cost() 

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
            self.calculate_cost()

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
            self.calculate_cost()

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
        allergens = self.allergens_text.get('1.0', tk.END).strip()
        
        # Costing data
        try:
            labor_cost = float(self.labor_cost_entry.get() or 0)
            energy_cost = float(self.energy_cost_entry.get() or 0)
            misc_cost = float(self.misc_cost_entry.get() or 0)
        except ValueError:
            labor_cost = 0.0
            energy_cost = 0.0
            misc_cost = 0.0

        # Check if version is changing (only relevant in edit mode)
        version_changing = False
        if self.mode == 'edit':
            original_version = self.recipe.get('version', 1)
            version_changing = (version != original_version)

        # If setting this recipe to active, deactivate all other versions with same name
        if self.active_var.get() == 1:
            self.cache.connect()
            # Find all recipes with the same name
            all_same_name = self.cache.get_all_records('recipes', f"recipe_name = '{name.replace("'", "''")}'")
            # Deactivate all of them
            for other_recipe in all_same_name:
                # Skip the current recipe being edited ONLY if version is NOT changing
                # (if version IS changing, we're creating a new recipe, so deactivate the original)
                if self.mode == 'edit' and not version_changing and other_recipe['recipe_id'] == self.recipe['recipe_id']:
                    # Skip the current recipe being edited (will be set to active below)
                    continue
                self.cache.update_record('recipes', other_recipe['recipe_id'],
                                       {'is_active': 0, 'sync_status': 'pending'},
                                       id_column='recipe_id')
            self.cache.close()

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
                'created_date': get_today_db(),
                'created_by': self.current_user.username,
                'last_modified': get_now_db(),
                'is_active': self.active_var.get(),
                'brewing_notes': notes,
                'allergens': allergens,
                'labor_cost': labor_cost,
                'energy_cost': energy_cost,
                'misc_cost': misc_cost,
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
            # Edit mode - check if version has changed
            original_version = self.recipe.get('version', 1)

            if version != original_version:
                # Version changed - create NEW recipe (new version)
                recipe_id = str(uuid.uuid4())
                recipe_data = {
                    'recipe_id': recipe_id,
                    'recipe_name': name,
                    'style': style,
                    'version': version,
                    'target_abv': abv,
                    'target_batch_size_litres': batch_size,
                    'created_date': get_today_db(),  # New version gets new created date
                    'created_by': self.current_user.username,
                    'last_modified': get_now_db(),
                    'is_active': self.active_var.get(),
                    'brewing_notes': notes,
                    'allergens': allergens,
                    'labor_cost': labor_cost,
                    'energy_cost': energy_cost,
                    'misc_cost': misc_cost,
                    'sync_status': 'pending'
                }

                self.cache.connect()
                self.cache.insert_record('recipes', recipe_data)
                self.save_ingredients(recipe_id)
                self.cache.close()

                # Store recipe_id so parent can re-select it
                self.saved_recipe_id = recipe_id

                messagebox.showinfo("Success", f"New recipe version {version} created successfully!\n\nThe original version {original_version} is preserved.")

            else:
                # Version unchanged - update existing recipe
                logger.info(f"Updating existing recipe: {self.recipe['recipe_id']}")
                recipe_id = self.recipe['recipe_id']
                recipe_data = {
                    'recipe_name': name,
                    'style': style,
                    'version': version,
                    'target_abv': abv,
                    'target_batch_size_litres': batch_size,
                    'last_modified': get_now_db(),
                    'is_active': self.active_var.get(),
                    'brewing_notes': notes,
                    'allergens': allergens,
                    'labor_cost': labor_cost,
                    'energy_cost': energy_cost,
                    'misc_cost': misc_cost,
                    'sync_status': 'pending'
                }

                self.cache.connect()
                success = self.cache.update_record('recipes', recipe_id, recipe_data, id_column='recipe_id')
                if not success:
                    logger.error(f"Failed to update recipe record {recipe_id}")
                    messagebox.showerror("Error", "Failed to update recipe in database.")
                    self.cache.close()
                    return

                # Delete old ingredients and save new ones
                try:
                    self.cache.cursor.execute("DELETE FROM recipe_ingredients WHERE recipe_id = ?", (recipe_id,))
                    self.cache.connection.commit()
                except Exception as e:
                    logger.error(f"Failed to delete old ingredients: {e}")
                
                self.save_ingredients(recipe_id)

                self.cache.close()

                # Store recipe_id so parent can re-select it
                self.saved_recipe_id = recipe_id
                
                logger.info("Recipe updated successfully")
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
        self.transient(parent)
        self.grab_set()

        # Use window manager for sizing if available
        wm = get_window_manager()
        if wm:
            wm.setup_dialog(self, 'recipe_details_dialog', width_pct=0.5, height_pct=0.7,
                          add_grip=True, save_on_close=True, resizable=True)
        else:
            # Fallback to hardcoded size
            self.geometry("700x600")
            self.resizable(True, True)

        self.create_widgets()

    def create_widgets(self):
        """Create dialog widgets"""
        # Buttons (Top)
        button_frame = ttk.Frame(self, padding=10)
        button_frame.pack(fill=tk.X, side=tk.TOP)

        ttk.Button(button_frame, text="Close", bootstyle="secondary",
                  command=self.destroy).pack(side=tk.RIGHT, padx=(10, 0))

        scroll_frame = ScrollableFrame(self)
        scroll_frame.pack(fill=tk.BOTH, expand=True)

        # Content
        content = ttk.Frame(scroll_frame.inner_frame)
        content.pack(fill=tk.BOTH, expand=True, padx=30, pady=20)

        # Recipe info
        ttk.Label(
            content,
            text=self.recipe.get('recipe_name', 'Unknown'),
            font=('Arial', 18, 'bold')
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

        ttk.Label(
            content,
            text=info_text.strip(),
            font=('Arial', 10),
            justify=tk.LEFT
        ).pack(anchor='w', pady=(0, 20))

        # Brewing Notes
        if self.recipe.get('brewing_notes'):
            ttk.Label(
                content,
                text="Brewing Notes:",
                font=('Arial', 11, 'bold')
            ).pack(anchor='w', pady=(0, 5))

            notes_frame = ttk.Frame(content)
            notes_frame.pack(fill=tk.X, pady=(0, 20))

            ttk.Label(
                notes_frame,
                text=self.recipe.get('brewing_notes', ''),
                font=('Arial', 10),
                justify=tk.LEFT,
                wraplength=600
            ).pack(padx=10, pady=10, anchor='w')

        # Ingredients
        ttk.Label(
            content,
            text="Ingredients:",
            font=('Arial', 11, 'bold')
        ).pack(anchor='w', pady=(0, 10))

        if self.ingredients:
            for ing in self.ingredients:
                ing_frame = ttk.Frame(content)
                ing_frame.pack(fill=tk.X, pady=2)

                ing_text = f"{ing.get('ingredient_name', 'Unknown')} - {ing.get('quantity', 0)} {ing.get('unit', '')} ({ing.get('ingredient_type', 'N/A')})"
                if ing.get('timing'):
                    ing_text += f" - {ing.get('timing')}"

                ttk.Label(
                    ing_frame,
                    text=ing_text,
                    font=('Arial', 10)
                ).pack(padx=10, pady=5, fill=tk.X)

                if ing.get('notes'):
                    ttk.Label(
                        ing_frame,
                        text=f"  Note: {ing.get('notes')}",
                        font=('Arial', 9, 'italic')
                    ).pack(padx=20, pady=(0, 5), fill=tk.X)
        else:
            ttk.Label(
                content,
                text="No ingredients added yet.",
                font=('Arial', 10, 'italic')
            ).pack(anchor='w')




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
        self.transient(parent)
        self.grab_set()

        # Use window manager for sizing if available
        wm = get_window_manager()
        if wm:
            wm.setup_dialog(self, 'ingredient_dialog', width_pct=0.35, height_pct=0.6,
                          add_grip=True, save_on_close=True, resizable=True)
        else:
            # Fallback to hardcoded size
            self.geometry("500x600")
            self.resizable(True, True)

        self.create_widgets()
        self.load_inventory_items()

        if mode == 'edit' and ingredient:
            self.populate_fields()

    def create_widgets(self):
        """Create dialog widgets"""
        # Buttons (Top)
        button_frame = ttk.Frame(self, padding=10)
        button_frame.pack(fill=tk.X, side=tk.TOP)

        ttk.Button(button_frame, text="Cancel", bootstyle="secondary",
                  command=self.destroy).pack(side=tk.RIGHT, padx=(10, 0))
        ttk.Button(button_frame, text="Save", bootstyle="success",
                  command=self.save_ingredient).pack(side=tk.RIGHT)

        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Type buttons (instead of dropdown)
        ttk.Label(main_frame, text="Type *", font=('Arial', 10, 'bold')).grid(row=0, column=0, columnspan=2, sticky='w', pady=(0, 5))

        self.type_var = tk.StringVar(value='Malt')
        type_button_frame = ttk.Frame(main_frame)
        type_button_frame.grid(row=1, column=0, columnspan=2, sticky='w', pady=(0, 15))

        # Create type buttons
        self.type_buttons = {}
        types = ['Malt', 'Hops', 'Yeast', 'Adjunct', 'Other']
        for i, type_name in enumerate(types):
            btn = ttk.Button(
                type_button_frame,
                text=type_name,
                bootstyle="secondary-outline",
                command=lambda t=type_name: self.select_type(t)
            )
            btn.pack(side=tk.LEFT, padx=(0, 5) if i < len(types) - 1 else 0)
            self.type_buttons[type_name] = btn

        # Ingredient Name (autocomplete from inventory)
        ttk.Label(main_frame, text="Ingredient Name *", font=('Arial', 10, 'bold')).grid(row=2, column=0, sticky='w', pady=(0, 5))

        name_frame = ttk.Frame(main_frame)
        name_frame.grid(row=3, column=0, columnspan=2, sticky='ew', pady=(0, 5))

        self.name_var = tk.StringVar()
        self.name_combo = ttk.Combobox(
            name_frame,
            textvariable=self.name_var,
            font=('Arial', 10),
            width=37,
            state='readonly'  # Only allow selection from inventory
        )
        self.name_combo.pack(fill=tk.X)

        # Make dropdown open when clicking anywhere on the combobox
        self.name_combo.bind('<Button-1>', lambda e: self.name_combo.event_generate('<Down>'))

        # Info label
        self.inventory_info_label = ttk.Label(
            main_frame,
            text="Select ingredient from inventory",
            font=('Arial', 8, 'italic')
        )
        self.inventory_info_label.grid(row=4, column=0, columnspan=2, sticky='w', pady=(0, 15))

        # Quantity
        ttk.Label(main_frame, text="Quantity *", font=('Arial', 10, 'bold')).grid(row=5, column=0, sticky='w', pady=(0, 5))
        self.quantity_entry = ttk.Entry(main_frame, font=('Arial', 10), width=15)
        self.quantity_entry.grid(row=6, column=0, sticky='w', pady=(0, 15))

        # Unit
        ttk.Label(main_frame, text="Unit *", font=('Arial', 10, 'bold')).grid(row=5, column=1, sticky='w', pady=(0, 5), padx=(20, 0))
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

        # Stage
        ttk.Label(main_frame, text="Stage", font=('Arial', 10, 'bold')).grid(row=7, column=0, sticky='w', pady=(0, 5))
        self.stage_var = tk.StringVar()
        stage_combo = ttk.Combobox(
            main_frame,
            textvariable=self.stage_var,
            values=['Mash', 'Boil', 'Whirlpool', 'Fermentation', 'Dry Hop', 'Conditioning', 'Primary', 'Secondary', 'Bottle/Keg'],
            font=('Arial', 10),
            width=20
        )
        stage_combo.grid(row=8, column=0, sticky='w', pady=(0, 15))

        # Duration
        ttk.Label(main_frame, text="Duration", font=('Arial', 10, 'bold')).grid(row=7, column=1, sticky='w', pady=(0, 5), padx=(20, 0))
        
        duration_frame = ttk.Frame(main_frame)
        duration_frame.grid(row=8, column=1, sticky='w', pady=(0, 15), padx=(20, 0))
        
        self.duration_var = tk.StringVar()
        duration_entry = ttk.Entry(duration_frame, textvariable=self.duration_var, font=('Arial', 10), width=10)
        duration_entry.pack(side=tk.LEFT, padx=(0, 5))

        self.duration_unit_var = tk.StringVar(value='min')
        duration_unit_combo = ttk.Combobox(
            duration_frame,
            textvariable=self.duration_unit_var,
            values=['min', 'days', 'hours'],
            font=('Arial', 10),
            width=8,
            state='readonly'
        )
        duration_unit_combo.pack(side=tk.LEFT)

        # Notes
        ttk.Label(main_frame, text="Notes", font=('Arial', 10, 'bold')).grid(row=9, column=0, sticky='w', pady=(0, 5))
        self.notes_text = tk.Text(main_frame, font=('Arial', 10), width=40, height=4)
        self.notes_text.grid(row=10, column=0, columnspan=2, sticky='ew', pady=(0, 15))

        # Configure grid
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_columnconfigure(1, weight=1)


        # Set initial type selection (done after all widgets are created)
        self.select_type('Malt')

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

    def select_type(self, type_name):
        """Handle type button selection"""
        # Update the type variable
        self.type_var.set(type_name)

        # Update button appearance - highlight selected, unhighlight others
        for btn_type, btn in self.type_buttons.items():
            if btn_type == type_name:
                # Selected button - use success style
                btn.configure(bootstyle="success")
            else:
                # Unselected button - use outline style
                btn.configure(bootstyle="secondary-outline")

        # Update the inventory items shown
        self.on_type_change()

    def on_type_change(self, event=None):
        """Update name options when type changes"""
        self.update_name_options()

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
                text=f"Found {len(items)} {selected_type} items in inventory"
            )
        else:
            self.inventory_info_label.config(
                text=f"No {selected_type} items in inventory - add items in Inventory module first",
                foreground='red'
            )

    def populate_fields(self):
        """Populate fields with existing ingredient data"""
        if not self.ingredient:
            return

        # Set the type first (this will update buttons and inventory)
        ing_type = self.ingredient.get('type', 'Malt')
        self.select_type(ing_type)

        # Then populate other fields
        self.name_var.set(self.ingredient.get('name', ''))
        self.quantity_entry.insert(0, str(self.ingredient.get('quantity', '')))
        self.unit_var.set(self.ingredient.get('unit', 'kg'))
        # Parse timing string into Stage, Duration, Unit
        timing_str = self.ingredient.get('timing', '')
        
        # Pattern match "Stage (Duration Unit)" e.g. "Boil (60 min)"
        match = re.match(r'^(.*?) \((\d+(?:\.\d+)?) (\w+)\)$', timing_str)
        
        if match:
            self.stage_var.set(match.group(1))
            self.duration_var.set(match.group(2))
            self.duration_unit_var.set(match.group(3))
        else:
            # Fallback - just text or basic "90 min"
            # If it looks like just a duration "90 min", put it in duration
            match_simple = re.match(r'^(\d+(?:\.\d+)?)\s*(min|mins|day|days|hour|hours)$', timing_str, re.IGNORECASE)
            if match_simple:
                self.stage_var.set('Boil') 
                self.duration_var.set(match_simple.group(1))
                # Normalize unit
                unit = match_simple.group(2).lower()
                if 'min' in unit: unit = 'min'
                elif 'day' in unit: unit = 'days'
                elif 'hour' in unit: unit = 'hours'
                self.duration_unit_var.set(unit)
            else:
                self.stage_var.set(timing_str)
                self.duration_var.set('')

        notes = self.ingredient.get('notes', '')
        if notes:
            self.notes_text.insert('1.0', notes)

    def save_ingredient(self):
        """Validate and save ingredient"""
        name = self.name_var.get().strip()
        ing_type = self.type_var.get()
        quantity_str = self.quantity_entry.get().strip()
        unit = self.unit_var.get()
        stage = self.stage_var.get().strip()
        duration_str = self.duration_var.get().strip()
        duration_unit = self.duration_unit_var.get()
        
        # Construct timing string
        timing = stage
        if duration_str:
            try:
                duration = float(duration_str)
                # Remove .0 if integer
                if duration.is_integer():
                    duration = int(duration)
                timing = f"{stage} ({duration} {duration_unit})"
            except ValueError:
                messagebox.showerror("Validation Error", "Duration must be a number.")
                return
        notes = self.notes_text.get('1.0', tk.END).strip()

        if not name:
            messagebox.showerror("Validation Error", "Please select an ingredient from inventory.")
            return

        if not quantity_str:
            messagebox.showerror("Validation Error", "Please enter a quantity.")
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

        # Ingredient must be in inventory
        if not inventory_item_id:
            messagebox.showerror(
                "Not in Inventory",
                f"'{name}' is not in your inventory.\n\n"
                f"Please add it to the Inventory module first before using it in recipes."
            )
            return

        self.result = {
            'name': name,
            'type': ing_type,
            'quantity': quantity,
            'unit': unit,
            'timing': timing,
            'notes': notes,
            'inventory_item_id': inventory_item_id  # Link to inventory
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
