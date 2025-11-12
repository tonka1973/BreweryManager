"""
Label Printing Module for Brewery Management System
Generate professional cask labels with brewery logo and beer details
"""

import tkinter as tk
from tkinter import messagebox, filedialog
import ttkbootstrap as ttk
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
import os


class LabelsModule(ttk.Frame):
    """Label printing module for cask labels"""

    def __init__(self, parent, cache_manager, current_user):
        super().__init__(parent)
        self.cache = cache_manager
        self.current_user = current_user

        self.create_widgets()

    def create_widgets(self):
        """Create label printing widgets"""
        # Header
        header = ttk.Frame(self)
        header.pack(fill=tk.X, padx=20, pady=(0, 20))

        ttk.Label(header, text="Cask Label Printing",
                font=('Arial', 16, 'bold')).pack(side=tk.LEFT)

        ttk.Label(header, text="Professional PDF Labels",
                font=('Arial', 9, 'italic')).pack(side=tk.RIGHT)

        # Content in center
        content = ttk.Frame(self)
        content.pack(expand=True)

        # Label configuration
        config_frame = ttk.Frame(content, relief=tk.SOLID, borderwidth=1, padding=(30, 30))
        config_frame.pack()

        ttk.Label(config_frame, text="Create Cask Labels",
                font=('Arial', 14, 'bold')).grid(row=0, column=0, columnspan=2, pady=(0,20))

        # Batch selection
        ttk.Label(config_frame, text="Select Batch (Gyle) *",
                font=('Arial', 10, 'bold')).grid(row=1, column=0, sticky='w', pady=(0,5))

        self.batch_var = tk.StringVar()
        self.cache.connect()
        batches = self.cache.get_all_records('batches', "status IN ('ready', 'packaged')", 'gyle_number DESC')
        self.cache.close()
        self.batch_list = {b['gyle_number']: b for b in batches}

        batch_combo = ttk.Combobox(config_frame, textvariable=self.batch_var,
                                   values=list(self.batch_list.keys()),
                                   width=30, state='readonly', font=('Arial', 10))
        batch_combo.grid(row=2, column=0, columnspan=2, sticky='ew', pady=(0,15))
        batch_combo.bind('<<ComboboxSelected>>', self.on_batch_selected)

        # Beer name (auto-filled)
        ttk.Label(config_frame, text="Beer Name",
                font=('Arial', 10, 'bold')).grid(row=3, column=0, sticky='w', pady=(0,5))
        self.beer_label = ttk.Label(config_frame, text="Select a batch",
                                   font=('Arial', 10))
        self.beer_label.grid(row=4, column=0, columnspan=2, sticky='w', pady=(0,15))

        # ABV (auto-filled)
        ttk.Label(config_frame, text="ABV %",
                font=('Arial', 10, 'bold')).grid(row=5, column=0, sticky='w', pady=(0,5))
        self.abv_label = ttk.Label(config_frame, text="-",
                                 font=('Arial', 10))
        self.abv_label.grid(row=6, column=0, sticky='w', pady=(0,15))

        # Container type
        ttk.Label(config_frame, text="Container Type *",
                font=('Arial', 10, 'bold')).grid(row=7, column=0, sticky='w', pady=(0,5))
        self.container_var = tk.StringVar(value='firkin')
        ttk.Combobox(config_frame, textvariable=self.container_var,
                    values=['pin', 'firkin', 'kilderkin', '30l_keg', '50l_keg'],
                    width=20, state='readonly', font=('Arial', 10)).grid(row=8, column=0, sticky='w', pady=(0,15))

        # Quantity
        ttk.Label(config_frame, text="Number of Labels",
                font=('Arial', 10, 'bold')).grid(row=9, column=0, sticky='w', pady=(0,5))
        self.qty_spinbox = tk.Spinbox(config_frame, from_=1, to=50, width=10, font=('Arial', 10))
        self.qty_spinbox.delete(0, tk.END)
        self.qty_spinbox.insert(0, "1")
        self.qty_spinbox.grid(row=10, column=0, sticky='w', pady=(0,20))

        # Brewery name
        ttk.Label(config_frame, text="Brewery Name",
                font=('Arial', 10, 'bold')).grid(row=11, column=0, sticky='w', pady=(0,5))
        self.brewery_entry = ttk.Entry(config_frame, font=('Arial', 10), width=30)
        self.brewery_entry.insert(0, "Your Brewery Name")
        self.brewery_entry.grid(row=12, column=0, columnspan=2, sticky='ew', pady=(0,15))

        # Brewery address
        ttk.Label(config_frame, text="Brewery Address",
                font=('Arial', 10, 'bold')).grid(row=13, column=0, sticky='w', pady=(0,5))
        self.address_text = tk.Text(config_frame, font=('Arial', 9), width=35, height=3)
        self.address_text.insert('1.0', "123 Brewery Lane\nAnytown, AB1 2CD\nUnited Kingdom")
        self.address_text.grid(row=14, column=0, columnspan=2, sticky='ew', pady=(0,20))

        config_frame.grid_columnconfigure(0, weight=1)

        # Generate button
        ttk.Button(config_frame, text="📄 Generate PDF Labels",
                 bootstyle="success",
                 cursor='hand2', command=self.generate_labels).grid(row=15, column=0, columnspan=2, pady=(10,0))

    def on_batch_selected(self, event=None):
        """Auto-fill beer details when batch selected"""
        gyle = self.batch_var.get()
        if gyle in self.batch_list:
            batch = self.batch_list[gyle]

            # Get recipe name
            recipe_id = batch.get('recipe_id')
            if recipe_id:
                self.cache.connect()
                recipes = self.cache.get_all_records('recipes', f"recipe_id = '{recipe_id}'")
                self.cache.close()
                if recipes:
                    self.beer_label.config(text=recipes[0]['recipe_name'])

            # Get ABV
            abv = batch.get('measured_abv', 0)
            self.abv_label.config(text=f"{abv:.1f}%")

    def generate_labels(self):
        """Generate PDF cask labels"""
        gyle = self.batch_var.get()
        if not gyle or gyle not in self.batch_list:
            messagebox.showerror("Error", "Please select a batch.")
            return

        batch = self.batch_list[gyle]

        # Get beer name
        beer_name = "Unknown Beer"
        recipe_id = batch.get('recipe_id')
        if recipe_id:
            self.cache.connect()
            recipes = self.cache.get_all_records('recipes', f"recipe_id = '{recipe_id}'")
            self.cache.close()
            if recipes:
                beer_name = recipes[0]['recipe_name']

        abv = batch.get('measured_abv', 0)
        container = self.container_var.get()
        qty = int(self.qty_spinbox.get())
        brewery_name = self.brewery_entry.get().strip()
        brewery_address = self.address_text.get('1.0', tk.END).strip()

        # Ask for save location
        filename = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
            initialfile=f"{gyle}_labels.pdf"
        )

        if not filename:
            return

        try:
            self.create_pdf_labels(filename, gyle, beer_name, abv, container, qty,
                                  brewery_name, brewery_address)
            messagebox.showinfo("Success", f"Labels generated!\n\nSaved to:\n{filename}")

            # Ask to open
            result = messagebox.askyesno("Open PDF?", "Would you like to open the PDF now?")
            if result:
                os.startfile(filename)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate labels:\n{str(e)}")

    def create_pdf_labels(self, filename, gyle, beer_name, abv, container, qty,
                         brewery_name, brewery_address):
        """Create PDF with cask labels"""
        c = canvas.Canvas(filename, pagesize=A4)
        width, height = A4

        # Container sizes
        container_sizes = {
            'pin': '4.5 gal (20.5L)',
            'firkin': '9 gal (40.9L)',
            'kilderkin': '18 gal (81.8L)',
            '30l_keg': '30 litres',
            '50l_keg': '50 litres'
        }

        container_size = container_sizes.get(container, container)

        # Label dimensions (A4 width, about 100mm height)
        label_height = 100 * mm
        margin = 20 * mm

        labels_per_page = 2
        label_count = 0

        for i in range(qty):
            if label_count > 0 and label_count % labels_per_page == 0:
                c.showPage()

            # Calculate position
            y_pos = height - margin - (label_count % labels_per_page) * (label_height + 20*mm)

            # Draw label border
            c.setLineWidth(2)
            c.rect(margin, y_pos - label_height, width - 2*margin, label_height)

            # Brewery name (top, large)
            c.setFont("Helvetica-Bold", 24)
            c.drawCentredString(width/2, y_pos - 25*mm, brewery_name)

            # Beer name (center, very large)
            c.setFont("Helvetica-Bold", 36)
            c.drawCentredString(width/2, y_pos - 45*mm, beer_name)

            # ABV (large, prominent)
            c.setFont("Helvetica-Bold", 28)
            c.drawCentredString(width/2, y_pos - 65*mm, f"ABV: {abv:.1f}%")

            # Container type and Gyle
            c.setFont("Helvetica", 14)
            c.drawCentredString(width/2, y_pos - 78*mm,
                              f"{container.replace('_', ' ').title()} ({container_size}) | {gyle}")

            # Brewery address (bottom, small)
            c.setFont("Helvetica", 9)
            address_lines = brewery_address.split('\n')
            y_addr = y_pos - 90*mm
            for line in address_lines[:3]:  # Max 3 lines
                c.drawCentredString(width/2, y_addr, line.strip())
                y_addr -= 10

            label_count += 1

        c.save()


class LabelPreviewDialog(tk.Toplevel):
    """Dialog to preview label before printing"""

    def __init__(self, parent, beer_name, abv, container, gyle):
        super().__init__(parent)
        self.title("Label Preview")
        self.geometry("400x300")
        self.transient(parent)
        self.grab_set()

        frame = ttk.Frame(self, relief=tk.SOLID, borderwidth=2, padding=(20, 20))
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        ttk.Label(frame, text="Your Brewery Name",
                font=('Arial', 16, 'bold')).pack(pady=(0,10))

        ttk.Label(frame, text=beer_name,
                font=('Arial', 24, 'bold')).pack(pady=(10,10))

        ttk.Label(frame, text=f"ABV: {abv:.1f}%",
                font=('Arial', 18, 'bold')).pack(pady=(0,10))

        ttk.Label(frame, text=f"{container.replace('_', ' ').title()} | {gyle}",
                font=('Arial', 11)).pack(pady=(0,10))

        ttk.Label(frame, text="123 Brewery Lane\nAnytown, AB1 2CD",
                font=('Arial', 9)).pack(pady=(10,0))

        ttk.Button(self, text="Close Preview",
                 bootstyle="secondary",
                 command=self.destroy).pack(pady=(0,20))
