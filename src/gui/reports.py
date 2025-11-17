"""
Reports Module - Historical Duty Returns Viewer
Module 11: View past monthly duty returns and export data
"""

import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import tkinter as tk
from tkinter import messagebox
from datetime import datetime
from decimal import Decimal


class ReportsModule(ttk.Frame):
    """Reports module for viewing historical duty returns"""

    def __init__(self, parent, cache_manager, current_user):
        super().__init__(parent)
        self.cache = cache_manager
        self.current_user = current_user

        self.create_widgets()

    def create_widgets(self):
        """Create the module interface"""
        # Title
        title_frame = ttk.Frame(self)
        title_frame.pack(fill=X, padx=20, pady=(20, 10))

        title_label = ttk.Label(
            title_frame,
            text="📊 Historical Duty Reports",
            font=("Helvetica", 16, "bold")
        )
        title_label.pack(side=LEFT)

        # Info label
        info_label = ttk.Label(
            title_frame,
            text="View past monthly HMRC duty returns",
            font=("Helvetica", 10)
        )
        info_label.pack(side=LEFT, padx=(15, 0))

        # Notebook for tabs
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=BOTH, expand=True, padx=20, pady=10)

        # Create tabs
        self.duty_reports_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.duty_reports_tab, text="Duty Reports")

        self.create_duty_reports_tab()

    def create_duty_reports_tab(self):
        """Create the duty reports tab showing all past returns"""

        # Control frame
        control_frame = ttk.Frame(self.duty_reports_tab)
        control_frame.pack(fill=X, padx=10, pady=10)

        # Filter by year
        ttk.Label(control_frame, text="Filter by Year:").pack(side=LEFT, padx=(0, 5))

        self.year_filter = ttk.Combobox(
            control_frame,
            width=10,
            state='readonly'
        )
        self.year_filter.pack(side=LEFT, padx=(0, 20))
        self.year_filter.bind('<<ComboboxSelected>>', lambda e: self.load_duty_returns())

        # Refresh button
        ttk.Button(
            control_frame,
            text="🔄 Refresh",
            command=self.load_duty_returns,
            bootstyle=INFO
        ).pack(side=LEFT, padx=5)

        # Export button (placeholder)
        ttk.Button(
            control_frame,
            text="📥 Export to Excel",
            command=self.export_to_excel,
            bootstyle=SUCCESS
        ).pack(side=LEFT, padx=5)

        # Annual summary button
        ttk.Button(
            control_frame,
            text="📈 Annual Summary",
            command=self.show_annual_summary,
            bootstyle=PRIMARY
        ).pack(side=LEFT, padx=5)

        # Returns list frame
        list_frame = ttk.Frame(self.duty_reports_tab)
        list_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)

        # Scrollbars
        y_scroll = ttk.Scrollbar(list_frame, orient=VERTICAL)
        y_scroll.pack(side=RIGHT, fill=Y)

        x_scroll = ttk.Scrollbar(list_frame, orient=HORIZONTAL)
        x_scroll.pack(side=BOTTOM, fill=X)

        # Treeview for duty returns
        columns = (
            'month', 'status', 'total_litres', 'total_lpa',
            'production_duty', 'spoilt_reclaim', 'net_payable',
            'submitted_date', 'payment_date'
        )

        self.returns_tree = ttk.Treeview(
            list_frame,
            columns=columns,
            show='headings',
            yscrollcommand=y_scroll.set,
            xscrollcommand=x_scroll.set
        )

        y_scroll.config(command=self.returns_tree.yview)
        x_scroll.config(command=self.returns_tree.xview)

        # Configure columns
        self.returns_tree.heading('month', text='Duty Month')
        self.returns_tree.heading('status', text='Status')
        self.returns_tree.heading('total_litres', text='Total Litres')
        self.returns_tree.heading('total_lpa', text='Total LPA')
        self.returns_tree.heading('production_duty', text='Production Duty')
        self.returns_tree.heading('spoilt_reclaim', text='Spoilt Reclaim')
        self.returns_tree.heading('net_payable', text='Net Payable')
        self.returns_tree.heading('submitted_date', text='Submitted')
        self.returns_tree.heading('payment_date', text='Payment Date')

        self.returns_tree.column('month', width=100, anchor=W)
        self.returns_tree.column('status', width=100, anchor=CENTER)
        self.returns_tree.column('total_litres', width=100, anchor=E)
        self.returns_tree.column('total_lpa', width=100, anchor=E)
        self.returns_tree.column('production_duty', width=120, anchor=E)
        self.returns_tree.column('spoilt_reclaim', width=120, anchor=E)
        self.returns_tree.column('net_payable', width=120, anchor=E)
        self.returns_tree.column('submitted_date', width=100, anchor=CENTER)
        self.returns_tree.column('payment_date', width=100, anchor=CENTER)

        self.returns_tree.pack(fill=BOTH, expand=True)

        # Bind double-click to view details
        self.returns_tree.bind('<Double-Button-1>', self.view_return_details)

        # Context menu
        self.context_menu = tk.Menu(self.returns_tree, tearoff=0)
        self.context_menu.add_command(label="View Details", command=self.view_return_details)
        self.context_menu.add_command(label="View Packaging Lines", command=self.view_packaging_lines)
        self.context_menu.add_command(label="View Spoilt Beer", command=self.view_spoilt_beer)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Export This Return", command=self.export_single_return)

        self.returns_tree.bind('<Button-3>', self.show_context_menu)

        # Summary frame at bottom
        summary_frame = ttk.LabelFrame(
            self.duty_reports_tab,
            text="Summary",
            padding=10
        )
        summary_frame.pack(fill=X, padx=10, pady=(0, 10))

        self.summary_label = ttk.Label(
            summary_frame,
            text="No returns loaded",
            font=("Helvetica", 10)
        )
        self.summary_label.pack()

        # Load initial data
        self.populate_year_filter()
        self.load_duty_returns()

    def populate_year_filter(self):
        """Populate the year filter dropdown"""
        self.cache.connect()

        cursor = self.cache.cursor

        cursor.execute('''
            SELECT DISTINCT substr(duty_month, 1, 4) as year
            FROM duty_returns
            ORDER BY year DESC
        ''')

        years = [row[0] for row in cursor.fetchall()]

        # Add "All Years" option
        years.insert(0, "All Years")

        self.year_filter['values'] = years
        if years:
            self.year_filter.current(0)

    def load_duty_returns(self):
        """Load all duty returns from database"""
        # Clear existing items
        for item in self.returns_tree.get_children():
            self.returns_tree.delete(item)

        self.cache.connect()


        cursor = self.cache.cursor

        # Build query with optional year filter
        year_filter = self.year_filter.get()
        if year_filter and year_filter != "All Years":
            where_clause = f"WHERE duty_month LIKE '{year_filter}-%'"
        else:
            where_clause = ""

        cursor.execute(f'''
            SELECT
                duty_month,
                status,
                draught_low_litres + draught_std_litres + non_draught_litres + high_abv_litres as total_litres,
                draught_low_lpa + draught_std_lpa + non_draught_lpa + high_abv_lpa as total_lpa,
                production_duty_total,
                spoilt_duty_reclaim,
                net_duty_payable,
                submitted_date,
                payment_date
            FROM duty_returns
            {where_clause}
            ORDER BY duty_month DESC
        ''')

        rows = cursor.fetchall()

        total_production = 0.0
        total_reclaim = 0.0
        total_net = 0.0

        for row in rows:
            month, status, litres, lpa, prod_duty, reclaim, net, submitted, payment = row

            # Format values
            litres_str = f"{litres:.2f}L" if litres else "0.00L"
            lpa_str = f"{lpa:.2f}" if lpa else "0.00"
            prod_str = f"£{prod_duty:.2f}" if prod_duty else "£0.00"
            reclaim_str = f"£{reclaim:.2f}" if reclaim else "£0.00"
            net_str = f"£{net:.2f}" if net else "£0.00"

            submitted_str = submitted if submitted else "-"
            payment_str = payment if payment else "-"

            # Status badge
            status_display = status.upper() if status else "IN PROGRESS"

            self.returns_tree.insert('', END, values=(
                month,
                status_display,
                litres_str,
                lpa_str,
                prod_str,
                reclaim_str,
                net_str,
                submitted_str,
                payment_str
            ))

            # Sum totals
            total_production += prod_duty or 0
            total_reclaim += reclaim or 0
            total_net += net or 0

        # Update summary
        count = len(rows)
        summary_text = (
            f"Showing {count} return(s)  |  "
            f"Total Production Duty: £{total_production:.2f}  |  "
            f"Total Spoilt Reclaim: £{total_reclaim:.2f}  |  "
            f"Total Net Payable: £{total_net:.2f}"
        )
        self.summary_label.config(text=summary_text)

    def show_context_menu(self, event):
        """Show context menu on right-click"""
        item = self.returns_tree.identify_row(event.y)
        if item:
            self.returns_tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)

    def view_return_details(self, event=None):
        """View detailed breakdown of a selected return"""
        selection = self.returns_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a duty return to view.")
            return

        item = selection[0]
        values = self.returns_tree.item(item, 'values')
        duty_month = values[0]

        # Fetch full details from database
        self.cache.connect()

        cursor = self.cache.cursor

        cursor.execute('''
            SELECT * FROM duty_returns WHERE duty_month = ?
        ''', (duty_month,))

        row = cursor.fetchone()
        if not row:
            messagebox.showerror("Error", "Could not find duty return details.")
            return

        # Show details dialog
        DutyReturnDetailsDialog(self, duty_month, row)

    def view_packaging_lines(self):
        """View all packaging lines for selected month"""
        selection = self.returns_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a duty return to view packaging lines.")
            return

        item = selection[0]
        values = self.returns_tree.item(item, 'values')
        duty_month = values[0]

        PackagingLinesDialog(self, duty_month)

    def view_spoilt_beer(self):
        """View all spoilt beer for selected month"""
        selection = self.returns_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a duty return to view spoilt beer.")
            return

        item = selection[0]
        values = self.returns_tree.item(item, 'values')
        duty_month = values[0]

        SpoiltBeerDialog(self, duty_month)

    def show_annual_summary(self):
        """Show annual summary of duty returns"""
        AnnualSummaryDialog(self, self.cache)

    def export_to_excel(self):
        """Export all visible returns to Excel (placeholder)"""
        messagebox.showinfo(
            "Export to Excel",
            "Excel export functionality will be implemented in a future update.\n\n"
            "This will export all duty returns to an Excel workbook with separate sheets for:\n"
            "• Monthly returns summary\n"
            "• Packaging lines detail\n"
            "• Spoilt beer records\n"
            "• Annual totals"
        )

    def export_single_return(self):
        """Export selected return to Excel (placeholder)"""
        selection = self.returns_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a duty return to export.")
            return

        item = selection[0]
        values = self.returns_tree.item(item, 'values')
        duty_month = values[0]

        messagebox.showinfo(
            "Export Return",
            f"Excel export for {duty_month} will be implemented in a future update.\n\n"
            "This will create a detailed workbook with all data for this return period."
        )


class DutyReturnDetailsDialog(tk.Toplevel):
    """Dialog to show full breakdown of a duty return"""

    def __init__(self, parent, duty_month, return_data):
        super().__init__(parent)
        self.duty_month = duty_month
        self.return_data = return_data

        self.title(f"Duty Return Details - {duty_month}")
        self.geometry("800x700")

        # Make modal
        self.transient(parent)
        self.grab_set()

        self.create_widgets()

    def create_widgets(self):
        """Create the dialog widgets"""
        # Unpack data (matches duty_returns table structure)
        (id, duty_month,
         dl_litres, dl_lpa, dl_duty,
         ds_litres, ds_lpa, ds_duty,
         nd_litres, nd_lpa, nd_duty,
         ha_litres, ha_lpa, ha_duty,
         production_total,
         spoilt_reclaim, under_decl, over_decl,
         net_payable,
         status, submitted_date, payment_date, payment_ref,
         created_at, updated_at) = self.return_data

        # Scrollable frame
        canvas = tk.Canvas(self)
        scrollbar = ttk.Scrollbar(self, orient=VERTICAL, command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Title
        title_label = ttk.Label(
            scrollable_frame,
            text=f"HMRC Duty Return - {duty_month}",
            font=("Helvetica", 14, "bold")
        )
        title_label.pack(pady=10)

        # Category 1: Draught <3.5% ABV
        cat1_frame = ttk.LabelFrame(
            scrollable_frame,
            text="Category 1: Draught <3.5% ABV (SPR Low)",
            padding=10
        )
        cat1_frame.pack(fill=X, padx=20, pady=5)

        ttk.Label(cat1_frame, text=f"Volume: {dl_litres:.2f} litres").pack(anchor=W)
        ttk.Label(cat1_frame, text=f"Pure Alcohol: {dl_lpa:.2f} LPA").pack(anchor=W)
        ttk.Label(cat1_frame, text=f"Duty: £{dl_duty:.2f}", font=("Helvetica", 10, "bold")).pack(anchor=W)

        # Category 2: Draught 3.5-8.4% ABV
        cat2_frame = ttk.LabelFrame(
            scrollable_frame,
            text="Category 2: Draught 3.5-8.4% ABV (SPR Standard)",
            padding=10
        )
        cat2_frame.pack(fill=X, padx=20, pady=5)

        ttk.Label(cat2_frame, text=f"Volume: {ds_litres:.2f} litres").pack(anchor=W)
        ttk.Label(cat2_frame, text=f"Pure Alcohol: {ds_lpa:.2f} LPA").pack(anchor=W)
        ttk.Label(cat2_frame, text=f"Duty: £{ds_duty:.2f}", font=("Helvetica", 10, "bold")).pack(anchor=W)

        # Category 3: Non-Draught 3.5-8.4% ABV
        cat3_frame = ttk.LabelFrame(
            scrollable_frame,
            text="Category 3: Non-Draught 3.5-8.4% ABV (SPR Standard)",
            padding=10
        )
        cat3_frame.pack(fill=X, padx=20, pady=5)

        ttk.Label(cat3_frame, text=f"Volume: {nd_litres:.2f} litres").pack(anchor=W)
        ttk.Label(cat3_frame, text=f"Pure Alcohol: {nd_lpa:.2f} LPA").pack(anchor=W)
        ttk.Label(cat3_frame, text=f"Duty: £{nd_duty:.2f}", font=("Helvetica", 10, "bold")).pack(anchor=W)

        # Category 4: High ABV 8.5-22% (No SPR)
        cat4_frame = ttk.LabelFrame(
            scrollable_frame,
            text="Category 4: High ABV 8.5-22% (No SPR)",
            padding=10
        )
        cat4_frame.pack(fill=X, padx=20, pady=5)

        ttk.Label(cat4_frame, text=f"Volume: {ha_litres:.2f} litres").pack(anchor=W)
        ttk.Label(cat4_frame, text=f"Pure Alcohol: {ha_lpa:.2f} LPA").pack(anchor=W)
        ttk.Label(cat4_frame, text=f"Duty: £{ha_duty:.2f}", font=("Helvetica", 10, "bold")).pack(anchor=W)

        # Production total
        prod_frame = ttk.LabelFrame(
            scrollable_frame,
            text="Production Duty Total",
            padding=10
        )
        prod_frame.pack(fill=X, padx=20, pady=10)

        ttk.Label(
            prod_frame,
            text=f"£{production_total:.2f}",
            font=("Helvetica", 12, "bold")
        ).pack()

        # Adjustments
        adj_frame = ttk.LabelFrame(
            scrollable_frame,
            text="Adjustments",
            padding=10
        )
        adj_frame.pack(fill=X, padx=20, pady=5)

        ttk.Label(adj_frame, text=f"Spoilt Beer Duty Reclaim: -£{spoilt_reclaim:.2f}").pack(anchor=W)
        ttk.Label(adj_frame, text=f"Under Declarations (previous): +£{under_decl:.2f}").pack(anchor=W)
        ttk.Label(adj_frame, text=f"Over Declarations (previous): -£{over_decl:.2f}").pack(anchor=W)

        # Net payable
        net_frame = ttk.LabelFrame(
            scrollable_frame,
            text="NET DUTY PAYABLE TO HMRC",
            padding=10
        )
        net_frame.pack(fill=X, padx=20, pady=10)

        ttk.Label(
            net_frame,
            text=f"£{net_payable:.2f}",
            font=("Helvetica", 14, "bold"),
            foreground="red" if net_payable > 0 else "green"
        ).pack()

        # Status information
        status_frame = ttk.LabelFrame(
            scrollable_frame,
            text="Return Status",
            padding=10
        )
        status_frame.pack(fill=X, padx=20, pady=5)

        ttk.Label(status_frame, text=f"Status: {status.upper() if status else 'IN PROGRESS'}").pack(anchor=W)
        ttk.Label(status_frame, text=f"Submitted: {submitted_date if submitted_date else 'Not submitted'}").pack(anchor=W)
        ttk.Label(status_frame, text=f"Payment Date: {payment_date if payment_date else 'Not paid'}").pack(anchor=W)
        ttk.Label(status_frame, text=f"Payment Reference: {payment_ref if payment_ref else 'N/A'}").pack(anchor=W)

        # Metadata
        meta_frame = ttk.LabelFrame(
            scrollable_frame,
            text="Metadata",
            padding=10
        )
        meta_frame.pack(fill=X, padx=20, pady=5)

        ttk.Label(meta_frame, text=f"Created: {created_at}").pack(anchor=W)
        ttk.Label(meta_frame, text=f"Last Updated: {updated_at if updated_at else 'Never'}").pack(anchor=W)

        # Close button
        ttk.Button(
            scrollable_frame,
            text="Close",
            command=self.destroy,
            bootstyle=SECONDARY
        ).pack(pady=20)

        # Pack canvas and scrollbar
        canvas.pack(side=LEFT, fill=BOTH, expand=True)
        scrollbar.pack(side=RIGHT, fill=Y)


class PackagingLinesDialog(tk.Toplevel):
    """Dialog to show all packaging lines for a duty month"""

    def __init__(self, parent, duty_month):
        super().__init__(parent)
        self.duty_month = duty_month

        self.title(f"Packaging Lines - {duty_month}")
        self.geometry("1200x600")

        # Make modal
        self.transient(parent)
        self.grab_set()

        self.create_widgets()
        self.load_packaging_lines()

    def create_widgets(self):
        """Create the dialog widgets"""
        # Title
        title_label = ttk.Label(
            self,
            text=f"All Packaging Lines for {self.duty_month}",
            font=("Helvetica", 12, "bold")
        )
        title_label.pack(pady=10)

        # Tree frame
        tree_frame = ttk.Frame(self)
        tree_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)

        # Scrollbars
        y_scroll = ttk.Scrollbar(tree_frame, orient=VERTICAL)
        y_scroll.pack(side=RIGHT, fill=Y)

        x_scroll = ttk.Scrollbar(tree_frame, orient=HORIZONTAL)
        x_scroll.pack(side=BOTTOM, fill=X)

        # Treeview
        columns = (
            'date', 'batch_id', 'container', 'qty', 'duty_vol',
            'abv', 'lpa', 'spr_cat', 'rate', 'duty'
        )

        self.tree = ttk.Treeview(
            tree_frame,
            columns=columns,
            show='headings',
            yscrollcommand=y_scroll.set,
            xscrollcommand=x_scroll.set
        )

        y_scroll.config(command=self.tree.yview)
        x_scroll.config(command=self.tree.xview)

        # Configure columns
        self.tree.heading('date', text='Date')
        self.tree.heading('batch_id', text='Batch ID')
        self.tree.heading('container', text='Container')
        self.tree.heading('qty', text='Qty')
        self.tree.heading('duty_vol', text='Duty Vol')
        self.tree.heading('abv', text='ABV')
        self.tree.heading('lpa', text='LPA')
        self.tree.heading('spr_cat', text='SPR Category')
        self.tree.heading('rate', text='Rate')
        self.tree.heading('duty', text='Duty')

        self.tree.column('date', width=100)
        self.tree.column('batch_id', width=120)
        self.tree.column('container', width=120)
        self.tree.column('qty', width=60)
        self.tree.column('duty_vol', width=100)
        self.tree.column('abv', width=60)
        self.tree.column('lpa', width=80)
        self.tree.column('spr_cat', width=150)
        self.tree.column('rate', width=80)
        self.tree.column('duty', width=100)

        self.tree.pack(fill=BOTH, expand=True)

        # Close button
        ttk.Button(
            self,
            text="Close",
            command=self.destroy,
            bootstyle=SECONDARY
        ).pack(pady=10)

    def load_packaging_lines(self):
        """Load all packaging lines for this duty month"""
        # Parse duty month (YYYY-MM format)
        year, month = self.duty_month.split('-')

        # Get parent's cache manager
        cache = self.master.cache
        cache.connect()
        cursor = cache.cursor

        # Query packaging lines from this month
        cursor.execute('''
            SELECT
                packaging_date,
                batch_id,
                container_type,
                quantity,
                total_duty_volume,
                batch_abv,
                pure_alcohol_litres,
                spr_category,
                effective_duty_rate,
                duty_payable
            FROM batch_packaging_lines
            WHERE strftime('%Y-%m', packaging_date) = ?
            ORDER BY packaging_date DESC, batch_id
        ''', (self.duty_month,))

        rows = cursor.fetchall()

        for row in rows:
            date, batch, container, qty, duty_vol, abv, lpa, spr_cat, rate, duty = row

            self.tree.insert('', END, values=(
                date,
                batch,
                container,
                qty,
                f"{duty_vol:.2f}L",
                f"{abv:.1f}%",
                f"{lpa:.2f}",
                spr_cat or "N/A",
                f"£{rate:.2f}" if rate else "£0.00",
                f"£{duty:.2f}" if duty else "£0.00"
            ))


class SpoiltBeerDialog(tk.Toplevel):
    """Dialog to show all spoilt beer for a duty month"""

    def __init__(self, parent, duty_month):
        super().__init__(parent)
        self.duty_month = duty_month

        self.title(f"Spoilt Beer - {duty_month}")
        self.geometry("1000x500")

        # Make modal
        self.transient(parent)
        self.grab_set()

        self.create_widgets()
        self.load_spoilt_beer()

    def create_widgets(self):
        """Create the dialog widgets"""
        # Title
        title_label = ttk.Label(
            self,
            text=f"Spoilt Beer Records for {self.duty_month}",
            font=("Helvetica", 12, "bold")
        )
        title_label.pack(pady=10)

        # Tree frame
        tree_frame = ttk.Frame(self)
        tree_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)

        # Scrollbars
        y_scroll = ttk.Scrollbar(tree_frame, orient=VERTICAL)
        y_scroll.pack(side=RIGHT, fill=Y)

        x_scroll = ttk.Scrollbar(tree_frame, orient=HORIZONTAL)
        x_scroll.pack(side=BOTTOM, fill=X)

        # Treeview
        columns = (
            'date', 'batch_id', 'container', 'qty', 'volume',
            'lpa', 'rate', 'reclaim', 'reason', 'status'
        )

        self.tree = ttk.Treeview(
            tree_frame,
            columns=columns,
            show='headings',
            yscrollcommand=y_scroll.set,
            xscrollcommand=x_scroll.set
        )

        y_scroll.config(command=self.tree.yview)
        x_scroll.config(command=self.tree.xview)

        # Configure columns
        self.tree.heading('date', text='Date Found')
        self.tree.heading('batch_id', text='Batch ID')
        self.tree.heading('container', text='Container')
        self.tree.heading('qty', text='Qty')
        self.tree.heading('volume', text='Volume')
        self.tree.heading('lpa', text='LPA')
        self.tree.heading('rate', text='Rate')
        self.tree.heading('reclaim', text='Reclaim')
        self.tree.heading('reason', text='Reason')
        self.tree.heading('status', text='Status')

        self.tree.column('date', width=100)
        self.tree.column('batch_id', width=120)
        self.tree.column('container', width=100)
        self.tree.column('qty', width=60)
        self.tree.column('volume', width=80)
        self.tree.column('lpa', width=80)
        self.tree.column('rate', width=80)
        self.tree.column('reclaim', width=100)
        self.tree.column('reason', width=120)
        self.tree.column('status', width=80)

        self.tree.pack(fill=BOTH, expand=True)

        # Close button
        ttk.Button(
            self,
            text="Close",
            command=self.destroy,
            bootstyle=SECONDARY
        ).pack(pady=10)

    def load_spoilt_beer(self):
        """Load all spoilt beer records for this duty month"""
        # Get parent's cache manager
        cache = self.master.cache
        cache.connect()
        cursor = cache.cursor

        cursor.execute('''
            SELECT
                date_discovered,
                batch_id,
                container_type,
                quantity,
                duty_paid_volume,
                pure_alcohol_litres,
                original_duty_rate,
                duty_to_reclaim,
                reason_category,
                status
            FROM spoilt_beer
            WHERE duty_month = ?
            ORDER BY date_discovered DESC
        ''', (self.duty_month,))

        rows = cursor.fetchall()

        for row in rows:
            date, batch, container, qty, vol, lpa, rate, reclaim, reason, status = row

            self.tree.insert('', END, values=(
                date,
                batch or "N/A",
                container,
                qty,
                f"{vol:.2f}L" if vol else "0.00L",
                f"{lpa:.2f}" if lpa else "0.00",
                f"£{rate:.2f}" if rate else "£0.00",
                f"£{reclaim:.2f}" if reclaim else "£0.00",
                reason or "N/A",
                status or "pending"
            ))


class AnnualSummaryDialog(tk.Toplevel):
    """Dialog to show annual summary of all returns"""

    def __init__(self, parent, cache_manager):
        super().__init__(parent)
        self.cache = cache_manager

        self.title("Annual Duty Summary")
        self.geometry("700x600")

        # Make modal
        self.transient(parent)
        self.grab_set()

        self.create_widgets()

    def create_widgets(self):
        """Create the dialog widgets"""
        # Title
        title_label = ttk.Label(
            self,
            text="Annual Duty Summary",
            font=("Helvetica", 14, "bold")
        )
        title_label.pack(pady=10)

        # Year selector
        year_frame = ttk.Frame(self)
        year_frame.pack(fill=X, padx=20, pady=10)

        ttk.Label(year_frame, text="Select Year:").pack(side=LEFT, padx=(0, 10))

        self.year_var = tk.StringVar()
        year_combo = ttk.Combobox(
            year_frame,
            textvariable=self.year_var,
            width=10,
            state='readonly'
        )
        year_combo.pack(side=LEFT)
        year_combo.bind('<<ComboboxSelected>>', lambda e: self.load_summary())

        # Populate years
        self.cache.connect()

        cursor = self.cache.cursor
        cursor.execute('''
            SELECT DISTINCT substr(duty_month, 1, 4) as year
            FROM duty_returns
            ORDER BY year DESC
        ''')
        years = [row[0] for row in cursor.fetchall()]
        year_combo['values'] = years
        if years:
            year_combo.current(0)

        # Summary text
        self.summary_text = tk.Text(
            self,
            wrap=tk.WORD,
            width=70,
            height=30,
            font=("Courier", 10)
        )
        self.summary_text.pack(fill=BOTH, expand=True, padx=20, pady=10)

        # Close button
        ttk.Button(
            self,
            text="Close",
            command=self.destroy,
            bootstyle=SECONDARY
        ).pack(pady=10)

        # Load initial data
        if years:
            self.load_summary()

    def load_summary(self):
        """Load annual summary for selected year"""
        year = self.year_var.get()
        if not year:
            return

        self.summary_text.delete('1.0', END)

        self.cache.connect()


        cursor = self.cache.cursor

        # Get all returns for this year
        cursor.execute('''
            SELECT
                duty_month,
                draught_low_litres, draught_low_lpa, draught_low_duty,
                draught_std_litres, draught_std_lpa, draught_std_duty,
                non_draught_litres, non_draught_lpa, non_draught_duty,
                high_abv_litres, high_abv_lpa, high_abv_duty,
                production_duty_total,
                spoilt_duty_reclaim,
                net_duty_payable
            FROM duty_returns
            WHERE duty_month LIKE ?
            ORDER BY duty_month
        ''', (f"{year}-%",))

        rows = cursor.fetchall()

        if not rows:
            self.summary_text.insert(END, f"No duty returns found for {year}")
            return

        # Build summary report
        report = f"ANNUAL DUTY SUMMARY - {year}\n"
        report += "=" * 70 + "\n\n"

        # Totals
        total_dl_litres = sum(r[1] or 0 for r in rows)
        total_dl_duty = sum(r[3] or 0 for r in rows)
        total_ds_litres = sum(r[4] or 0 for r in rows)
        total_ds_duty = sum(r[6] or 0 for r in rows)
        total_nd_litres = sum(r[7] or 0 for r in rows)
        total_nd_duty = sum(r[9] or 0 for r in rows)
        total_ha_litres = sum(r[10] or 0 for r in rows)
        total_ha_duty = sum(r[12] or 0 for r in rows)
        total_production_duty = sum(r[13] or 0 for r in rows)
        total_spoilt_reclaim = sum(r[14] or 0 for r in rows)
        total_net_payable = sum(r[15] or 0 for r in rows)

        report += "CATEGORY TOTALS:\n"
        report += "-" * 70 + "\n"
        report += f"Draught <3.5% ABV:        {total_dl_litres:>10.2f}L    Duty: £{total_dl_duty:>10.2f}\n"
        report += f"Draught 3.5-8.4% ABV:     {total_ds_litres:>10.2f}L    Duty: £{total_ds_duty:>10.2f}\n"
        report += f"Non-Draught 3.5-8.4% ABV: {total_nd_litres:>10.2f}L    Duty: £{total_nd_duty:>10.2f}\n"
        report += f"High ABV 8.5-22%:         {total_ha_litres:>10.2f}L    Duty: £{total_ha_duty:>10.2f}\n"
        report += "-" * 70 + "\n"
        report += f"TOTAL PRODUCTION:         {total_dl_litres + total_ds_litres + total_nd_litres + total_ha_litres:>10.2f}L    "
        report += f"Duty: £{total_production_duty:>10.2f}\n\n"

        report += f"Spoilt Beer Reclaim:      £{total_spoilt_reclaim:>10.2f}\n"
        report += f"NET DUTY PAYABLE:         £{total_net_payable:>10.2f}\n\n"

        # Monthly breakdown
        report += "\nMONTHLY BREAKDOWN:\n"
        report += "=" * 70 + "\n"

        for row in rows:
            month = row[0]
            prod_duty = row[13] or 0
            reclaim = row[14] or 0
            net = row[15] or 0

            report += f"{month}:  Production £{prod_duty:>8.2f}  |  Reclaim £{reclaim:>8.2f}  |  Net £{net:>8.2f}\n"

        self.summary_text.insert(END, report)
