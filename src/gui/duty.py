"""
Duty Module for Brewery Management System
Monthly HMRC Duty Returns with 4 SPR Categories
"""

import tkinter as tk
from tkinter import messagebox
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from datetime import datetime


class DutyModule(ttk.Frame):
    """Monthly HMRC duty return module"""

    def __init__(self, parent, cache_manager, current_user):
        super().__init__(parent)
        self.cache = cache_manager
        self.current_user = current_user

        self.current_month = datetime.now().strftime('%Y-%m')
        self.return_data = None

        self.create_widgets()
        self.load_duty_return()

    def create_widgets(self):
        """Create duty return widgets"""
        # Header
        header_frame = ttk.Frame(self)
        header_frame.pack(fill=X, padx=20, pady=(20, 10))

        ttk.Label(
            header_frame,
            text="📋 HMRC Duty Return",
            font=("Helvetica", 16, "bold")
        ).pack(side=LEFT)

        # Month selector
        month_frame = ttk.Frame(header_frame)
        month_frame.pack(side=RIGHT)

        ttk.Label(month_frame, text="Duty Month:").pack(side=LEFT, padx=(0, 5))

        self.month_combo = ttk.Combobox(
            month_frame,
            width=12,
            state='readonly'
        )
        self.month_combo.pack(side=LEFT, padx=(0, 10))
        self.month_combo.bind('<<ComboboxSelected>>', lambda e: self.load_duty_return())

        # Populate months
        self.populate_month_combo()

        # Action buttons
        ttk.Button(
            header_frame,
            text="🔄 Refresh",
            command=self.load_duty_return,
            bootstyle=INFO
        ).pack(side=RIGHT, padx=(0, 5))

        # Main content - scrollable
        canvas = tk.Canvas(self)
        scrollbar = ttk.Scrollbar(self, orient=VERTICAL, command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Create content sections
        self.create_content_sections()

        canvas.pack(side=LEFT, fill=BOTH, expand=True, padx=(20, 0))
        scrollbar.pack(side=RIGHT, fill=Y, padx=(0, 20))

    def create_content_sections(self):
        """Create all content sections"""
        frame = self.scrollable_frame

        # Category 1: Draught <3.5% ABV
        self.cat1_frame = ttk.LabelFrame(frame, text="Category 1: Draught <3.5% ABV (SPR Low)", padding=15)
        self.cat1_frame.pack(fill=X, padx=20, pady=(10, 5))

        self.cat1_litres = ttk.Label(self.cat1_frame, text="Volume: 0.00 litres", font=("Helvetica", 10))
        self.cat1_litres.pack(anchor=W)

        self.cat1_lpa = ttk.Label(self.cat1_frame, text="Pure Alcohol: 0.00 LPA", font=("Helvetica", 10))
        self.cat1_lpa.pack(anchor=W)

        self.cat1_duty = ttk.Label(self.cat1_frame, text="Duty: £0.00", font=("Helvetica", 11, "bold"))
        self.cat1_duty.pack(anchor=W, pady=(5, 0))

        # Category 2: Draught 3.5-8.4% ABV
        self.cat2_frame = ttk.LabelFrame(frame, text="Category 2: Draught 3.5-8.4% ABV (SPR Standard)", padding=15)
        self.cat2_frame.pack(fill=X, padx=20, pady=5)

        self.cat2_litres = ttk.Label(self.cat2_frame, text="Volume: 0.00 litres", font=("Helvetica", 10))
        self.cat2_litres.pack(anchor=W)

        self.cat2_lpa = ttk.Label(self.cat2_frame, text="Pure Alcohol: 0.00 LPA", font=("Helvetica", 10))
        self.cat2_lpa.pack(anchor=W)

        self.cat2_duty = ttk.Label(self.cat2_frame, text="Duty: £0.00", font=("Helvetica", 11, "bold"))
        self.cat2_duty.pack(anchor=W, pady=(5, 0))

        # Category 3: Non-Draught 3.5-8.4% ABV
        self.cat3_frame = ttk.LabelFrame(frame, text="Category 3: Non-Draught 3.5-8.4% ABV (SPR Standard)", padding=15)
        self.cat3_frame.pack(fill=X, padx=20, pady=5)

        self.cat3_litres = ttk.Label(self.cat3_frame, text="Volume: 0.00 litres", font=("Helvetica", 10))
        self.cat3_litres.pack(anchor=W)

        self.cat3_lpa = ttk.Label(self.cat3_frame, text="Pure Alcohol: 0.00 LPA", font=("Helvetica", 10))
        self.cat3_lpa.pack(anchor=W)

        self.cat3_duty = ttk.Label(self.cat3_frame, text="Duty: £0.00", font=("Helvetica", 11, "bold"))
        self.cat3_duty.pack(anchor=W, pady=(5, 0))

        # Category 4: High ABV 8.5-22% (No SPR)
        self.cat4_frame = ttk.LabelFrame(frame, text="Category 4: High ABV 8.5-22% (No SPR)", padding=15)
        self.cat4_frame.pack(fill=X, padx=20, pady=5)

        self.cat4_litres = ttk.Label(self.cat4_frame, text="Volume: 0.00 litres", font=("Helvetica", 10))
        self.cat4_litres.pack(anchor=W)

        self.cat4_lpa = ttk.Label(self.cat4_frame, text="Pure Alcohol: 0.00 LPA", font=("Helvetica", 10))
        self.cat4_lpa.pack(anchor=W)

        self.cat4_duty = ttk.Label(self.cat4_frame, text="Duty: £0.00", font=("Helvetica", 11, "bold"))
        self.cat4_duty.pack(anchor=W, pady=(5, 0))

        # Production Total
        self.prod_frame = ttk.LabelFrame(frame, text="Production Duty Total", padding=15)
        self.prod_frame.pack(fill=X, padx=20, pady=(5, 10))

        self.prod_duty = ttk.Label(
            self.prod_frame,
            text="£0.00",
            font=("Helvetica", 14, "bold")
        )
        self.prod_duty.pack()

        # Adjustments
        adj_frame = ttk.LabelFrame(frame, text="Adjustments", padding=15)
        adj_frame.pack(fill=X, padx=20, pady=(10, 5))

        # Spoilt beer (auto-calculated, read-only)
        spoilt_row = ttk.Frame(adj_frame)
        spoilt_row.pack(fill=X, pady=5)

        ttk.Label(spoilt_row, text="Spoilt Beer Duty Reclaim:", font=("Helvetica", 10)).pack(side=LEFT)
        self.spoilt_label = ttk.Label(spoilt_row, text="-£0.00", font=("Helvetica", 10, "bold"))
        self.spoilt_label.pack(side=RIGHT)

        # Under declarations (manual entry)
        under_row = ttk.Frame(adj_frame)
        under_row.pack(fill=X, pady=5)

        ttk.Label(under_row, text="Under Declarations (previous):", font=("Helvetica", 10)).pack(side=LEFT)
        self.under_entry = ttk.Entry(under_row, width=10)
        self.under_entry.insert(0, "0.00")
        self.under_entry.pack(side=RIGHT)
        self.under_entry.bind('<KeyRelease>', lambda e: self.calculate_net())

        # Over declarations (manual entry)
        over_row = ttk.Frame(adj_frame)
        over_row.pack(fill=X, pady=5)

        ttk.Label(over_row, text="Over Declarations (previous):", font=("Helvetica", 10)).pack(side=LEFT)
        self.over_entry = ttk.Entry(over_row, width=10)
        self.over_entry.insert(0, "0.00")
        self.over_entry.pack(side=RIGHT)
        self.over_entry.bind('<KeyRelease>', lambda e: self.calculate_net())

        # Net Payable
        net_frame = ttk.LabelFrame(frame, text="NET DUTY PAYABLE TO HMRC", padding=20)
        net_frame.pack(fill=X, padx=20, pady=(10, 10))

        self.net_label = ttk.Label(
            net_frame,
            text="£0.00",
            font=("Helvetica", 16, "bold"),
            foreground="red"
        )
        self.net_label.pack()

        # Status and Actions
        status_frame = ttk.LabelFrame(frame, text="Return Status", padding=15)
        status_frame.pack(fill=X, padx=20, pady=(10, 5))

        status_row1 = ttk.Frame(status_frame)
        status_row1.pack(fill=X, pady=5)

        ttk.Label(status_row1, text="Status:", font=("Helvetica", 10, "bold")).pack(side=LEFT)
        self.status_label = ttk.Label(status_row1, text="IN PROGRESS", font=("Helvetica", 10))
        self.status_label.pack(side=LEFT, padx=(10, 0))

        status_row2 = ttk.Frame(status_frame)
        status_row2.pack(fill=X, pady=5)

        ttk.Label(status_row2, text="Submitted Date:", font=("Helvetica", 10)).pack(side=LEFT)
        self.submitted_label = ttk.Label(status_row2, text="Not submitted", font=("Helvetica", 10))
        self.submitted_label.pack(side=LEFT, padx=(10, 0))

        status_row3 = ttk.Frame(status_frame)
        status_row3.pack(fill=X, pady=5)

        ttk.Label(status_row3, text="Payment Date:", font=("Helvetica", 10)).pack(side=LEFT)
        self.payment_date_entry = ttk.Entry(status_row3, width=15)
        self.payment_date_entry.pack(side=LEFT, padx=(10, 0))

        status_row4 = ttk.Frame(status_frame)
        status_row4.pack(fill=X, pady=5)

        ttk.Label(status_row4, text="Payment Reference:", font=("Helvetica", 10)).pack(side=LEFT)
        self.payment_ref_entry = ttk.Entry(status_row4, width=20)
        self.payment_ref_entry.pack(side=LEFT, padx=(10, 0))

        # Action buttons
        button_frame = ttk.Frame(frame)
        button_frame.pack(fill=X, padx=20, pady=(15, 20))

        ttk.Button(
            button_frame,
            text="💾 Save Changes",
            command=self.save_return,
            bootstyle=SUCCESS
        ).pack(side=LEFT, padx=(0, 10))

        ttk.Button(
            button_frame,
            text="📤 Submit to HMRC",
            command=self.submit_return,
            bootstyle=PRIMARY
        ).pack(side=LEFT, padx=(0, 10))

        ttk.Button(
            button_frame,
            text="✅ Mark as Paid",
            command=self.mark_paid,
            bootstyle=INFO
        ).pack(side=LEFT, padx=(0, 10))

        ttk.Button(
            button_frame,
            text="📊 View Packaging Lines",
            command=self.view_packaging_lines,
            bootstyle=SECONDARY
        ).pack(side=LEFT)

    def populate_month_combo(self):
        """Populate month selector with available months and future months"""
        self.cache.connect()

        cursor = self.cache.cursor

        # Get existing months from packaging lines
        cursor.execute('''
            SELECT DISTINCT strftime('%Y-%m', packaging_date) as month
            FROM batch_packaging_lines
            ORDER BY month DESC
        ''')

        months = [row[0] for row in cursor.fetchall()]

        # Add current month if not present
        current = datetime.now().strftime('%Y-%m')
        if current not in months:
            months.insert(0, current)

        # Add next month
        from datetime import datetime, timedelta
        next_month = (datetime.now().replace(day=1) + timedelta(days=32)).strftime('%Y-%m')
        if next_month not in months:
            months.insert(0, next_month)

        self.month_combo['values'] = months
        if months:
            # Set to current month if available, otherwise first
            if current in months:
                self.month_combo.set(current)
            else:
                self.month_combo.current(0)

    def load_duty_return(self):
        """Load or create duty return for selected month"""
        duty_month = self.month_combo.get()
        if not duty_month:
            return

        self.current_month = duty_month

        self.cache.connect()


        cursor = self.cache.cursor

        # Check if return exists
        cursor.execute('SELECT * FROM duty_returns WHERE duty_month = ?', (duty_month,))
        row = cursor.fetchone()

        if row:
            # Load existing return
            columns = [desc[0] for desc in cursor.description]
            self.return_data = dict(zip(columns, row))
            self.populate_from_database()
        else:
            # Calculate from packaging lines
            self.return_data = None
            self.calculate_from_packaging()

    def calculate_from_packaging(self):
        """Auto-calculate duty from packaging lines for current month"""
        self.cache.connect()

        cursor = self.cache.cursor

        # Query packaging lines for this month
        cursor.execute('''
            SELECT
                spr_category,
                SUM(total_duty_volume) as total_litres,
                SUM(pure_alcohol_litres) as total_lpa,
                SUM(duty_payable) as total_duty
            FROM batch_packaging_lines
            WHERE strftime('%Y-%m', packaging_date) = ?
            GROUP BY spr_category
        ''', (self.current_month,))

        results = cursor.fetchall()

        # Initialize totals
        cat_data = {
            'draught_low': {'litres': 0, 'lpa': 0, 'duty': 0},
            'draught_standard': {'litres': 0, 'lpa': 0, 'duty': 0},
            'non_draught_standard': {'litres': 0, 'lpa': 0, 'duty': 0},
            'no_spr': {'litres': 0, 'lpa': 0, 'duty': 0},
        }

        # Populate from query results
        for row in results:
            spr_cat, litres, lpa, duty = row
            if spr_cat in cat_data:
                cat_data[spr_cat] = {
                    'litres': litres or 0,
                    'lpa': lpa or 0,
                    'duty': duty or 0
                }

        # Update UI
        self.cat1_litres.config(text=f"Volume: {cat_data['draught_low']['litres']:.2f} litres")
        self.cat1_lpa.config(text=f"Pure Alcohol: {cat_data['draught_low']['lpa']:.2f} LPA")
        self.cat1_duty.config(text=f"Duty: £{cat_data['draught_low']['duty']:.2f}")

        self.cat2_litres.config(text=f"Volume: {cat_data['draught_standard']['litres']:.2f} litres")
        self.cat2_lpa.config(text=f"Pure Alcohol: {cat_data['draught_standard']['lpa']:.2f} LPA")
        self.cat2_duty.config(text=f"Duty: £{cat_data['draught_standard']['duty']:.2f}")

        self.cat3_litres.config(text=f"Volume: {cat_data['non_draught_standard']['litres']:.2f} litres")
        self.cat3_lpa.config(text=f"Pure Alcohol: {cat_data['non_draught_standard']['lpa']:.2f} LPA")
        self.cat3_duty.config(text=f"Duty: £{cat_data['non_draught_standard']['duty']:.2f}")

        self.cat4_litres.config(text=f"Volume: {cat_data['no_spr']['litres']:.2f} litres")
        self.cat4_lpa.config(text=f"Pure Alcohol: {cat_data['no_spr']['lpa']:.2f} LPA")
        self.cat4_duty.config(text=f"Duty: £{cat_data['no_spr']['duty']:.2f}")

        # Calculate production total
        production_total = sum(d['duty'] for d in cat_data.values())
        self.prod_duty.config(text=f"£{production_total:.2f}")

        # Query spoilt beer for this month
        cursor.execute('''
            SELECT SUM(duty_to_reclaim)
            FROM spoilt_beer
            WHERE duty_month = ?
        ''', (self.current_month,))

        spoilt_reclaim = cursor.fetchone()[0] or 0.0
        self.spoilt_label.config(text=f"-£{spoilt_reclaim:.2f}")

        # Reset adjustments if no existing return
        self.under_entry.delete(0, tk.END)
        self.under_entry.insert(0, "0.00")
        self.over_entry.delete(0, tk.END)
        self.over_entry.insert(0, "0.00")

        # Reset status fields
        self.status_label.config(text="IN PROGRESS")
        self.submitted_label.config(text="Not submitted")
        self.payment_date_entry.delete(0, tk.END)
        self.payment_ref_entry.delete(0, tk.END)

        # Calculate net
        self.calculate_net()

    def populate_from_database(self):
        """Populate UI from existing database record"""
        r = self.return_data

        # Category 1
        self.cat1_litres.config(text=f"Volume: {r['draught_low_litres']:.2f} litres")
        self.cat1_lpa.config(text=f"Pure Alcohol: {r['draught_low_lpa']:.2f} LPA")
        self.cat1_duty.config(text=f"Duty: £{r['draught_low_duty']:.2f}")

        # Category 2
        self.cat2_litres.config(text=f"Volume: {r['draught_std_litres']:.2f} litres")
        self.cat2_lpa.config(text=f"Pure Alcohol: {r['draught_std_lpa']:.2f} LPA")
        self.cat2_duty.config(text=f"Duty: £{r['draught_std_duty']:.2f}")

        # Category 3
        self.cat3_litres.config(text=f"Volume: {r['non_draught_litres']:.2f} litres")
        self.cat3_lpa.config(text=f"Pure Alcohol: {r['non_draught_lpa']:.2f} LPA")
        self.cat3_duty.config(text=f"Duty: £{r['non_draught_duty']:.2f}")

        # Category 4
        self.cat4_litres.config(text=f"Volume: {r['high_abv_litres']:.2f} litres")
        self.cat4_lpa.config(text=f"Pure Alcohol: {r['high_abv_lpa']:.2f} LPA")
        self.cat4_duty.config(text=f"Duty: £{r['high_abv_duty']:.2f}")

        # Production total
        self.prod_duty.config(text=f"£{r['production_duty_total']:.2f}")

        # Adjustments
        self.spoilt_label.config(text=f"-£{r['spoilt_duty_reclaim']:.2f}")

        self.under_entry.delete(0, tk.END)
        self.under_entry.insert(0, f"{r['under_declarations']:.2f}")

        self.over_entry.delete(0, tk.END)
        self.over_entry.insert(0, f"{r['over_declarations']:.2f}")

        # Net payable
        net = r['net_duty_payable']
        self.net_label.config(
            text=f"£{net:.2f}",
            foreground="red" if net > 0 else "green"
        )

        # Status
        status = r['status'] or 'in_progress'
        self.status_label.config(text=status.upper())

        submitted = r['submitted_date'] or 'Not submitted'
        self.submitted_label.config(text=submitted)

        self.payment_date_entry.delete(0, tk.END)
        if r['payment_date']:
            self.payment_date_entry.insert(0, r['payment_date'])

        self.payment_ref_entry.delete(0, tk.END)
        if r['payment_reference']:
            self.payment_ref_entry.insert(0, r['payment_reference'])

    def calculate_net(self):
        """Calculate net duty payable"""
        try:
            # Get production duty
            prod_str = self.prod_duty.cget('text').replace('£', '')
            production_duty = float(prod_str)

            # Get spoilt reclaim
            spoilt_str = self.spoilt_label.cget('text').replace('-£', '')
            spoilt_reclaim = float(spoilt_str)

            # Get adjustments
            under = float(self.under_entry.get() or 0)
            over = float(self.over_entry.get() or 0)

            # Calculate net
            net = production_duty - spoilt_reclaim + under - over

            # Update label
            self.net_label.config(
                text=f"£{net:.2f}",
                foreground="red" if net > 0 else "green"
            )

        except ValueError:
            pass

    def save_return(self):
        """Save duty return to database"""
        duty_month = self.current_month

        try:
            # Parse values from UI
            cat1_duty = float(self.cat1_duty.cget('text').replace('Duty: £', ''))
            cat2_duty = float(self.cat2_duty.cget('text').replace('Duty: £', ''))
            cat3_duty = float(self.cat3_duty.cget('text').replace('Duty: £', ''))
            cat4_duty = float(self.cat4_duty.cget('text').replace('Duty: £', ''))

            cat1_litres = float(self.cat1_litres.cget('text').replace('Volume: ', '').replace(' litres', ''))
            cat2_litres = float(self.cat2_litres.cget('text').replace('Volume: ', '').replace(' litres', ''))
            cat3_litres = float(self.cat3_litres.cget('text').replace('Volume: ', '').replace(' litres', ''))
            cat4_litres = float(self.cat4_litres.cget('text').replace('Volume: ', '').replace(' litres', ''))

            cat1_lpa = float(self.cat1_lpa.cget('text').replace('Pure Alcohol: ', '').replace(' LPA', ''))
            cat2_lpa = float(self.cat2_lpa.cget('text').replace('Pure Alcohol: ', '').replace(' LPA', ''))
            cat3_lpa = float(self.cat3_lpa.cget('text').replace('Pure Alcohol: ', '').replace(' LPA', ''))
            cat4_lpa = float(self.cat4_lpa.cget('text').replace('Pure Alcohol: ', '').replace(' LPA', ''))

            production_total = float(self.prod_duty.cget('text').replace('£', ''))
            spoilt_reclaim = float(self.spoilt_label.cget('text').replace('-£', ''))

            under_declarations = float(self.under_entry.get() or 0)
            over_declarations = float(self.over_entry.get() or 0)

            net_payable = float(self.net_label.cget('text').replace('£', ''))

            payment_date = self.payment_date_entry.get().strip() or None
            payment_ref = self.payment_ref_entry.get().strip() or None

        except ValueError as e:
            messagebox.showerror("Error", f"Invalid numeric value: {e}")
            return

        self.cache.connect()


        cursor = self.cache.cursor

        # Check if return exists
        cursor.execute('SELECT id, status FROM duty_returns WHERE duty_month = ?', (duty_month,))
        existing = cursor.fetchone()

        now = datetime.now().isoformat()

        if existing:
            # Update existing
            cursor.execute('''
                UPDATE duty_returns
                SET
                    draught_low_litres = ?,
                    draught_low_lpa = ?,
                    draught_low_duty = ?,
                    draught_std_litres = ?,
                    draught_std_lpa = ?,
                    draught_std_duty = ?,
                    non_draught_litres = ?,
                    non_draught_lpa = ?,
                    non_draught_duty = ?,
                    high_abv_litres = ?,
                    high_abv_lpa = ?,
                    high_abv_duty = ?,
                    production_duty_total = ?,
                    spoilt_duty_reclaim = ?,
                    under_declarations = ?,
                    over_declarations = ?,
                    net_duty_payable = ?,
                    payment_date = ?,
                    payment_reference = ?,
                    updated_at = ?
                WHERE duty_month = ?
            ''', (cat1_litres, cat1_lpa, cat1_duty,
                  cat2_litres, cat2_lpa, cat2_duty,
                  cat3_litres, cat3_lpa, cat3_duty,
                  cat4_litres, cat4_lpa, cat4_duty,
                  production_total, spoilt_reclaim,
                  under_declarations, over_declarations,
                  net_payable, payment_date, payment_ref,
                  now, duty_month))
        else:
            # Insert new
            cursor.execute('''
                INSERT INTO duty_returns (
                    duty_month,
                    draught_low_litres, draught_low_lpa, draught_low_duty,
                    draught_std_litres, draught_std_lpa, draught_std_duty,
                    non_draught_litres, non_draught_lpa, non_draught_duty,
                    high_abv_litres, high_abv_lpa, high_abv_duty,
                    production_duty_total,
                    spoilt_duty_reclaim,
                    under_declarations, over_declarations,
                    net_duty_payable,
                    payment_date, payment_reference,
                    status, created_at, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (duty_month,
                  cat1_litres, cat1_lpa, cat1_duty,
                  cat2_litres, cat2_lpa, cat2_duty,
                  cat3_litres, cat3_lpa, cat3_duty,
                  cat4_litres, cat4_lpa, cat4_duty,
                  production_total, spoilt_reclaim,
                  under_declarations, over_declarations,
                  net_payable, payment_date, payment_ref,
                  'in_progress', now, now))

        self.cache.connection.commit()

        messagebox.showinfo("Success", f"Duty return for {duty_month} saved successfully!")
        self.load_duty_return()  # Reload

    def submit_return(self):
        """Mark return as submitted to HMRC"""
        if not messagebox.askyesno("Confirm Submit",
                                   "Are you sure you want to submit this return to HMRC?\n\n"
                                   "This will save the return and mark it as submitted."):
            return

        # Save first
        self.save_return()

        # Update status
        self.cache.connect()

        cursor = self.cache.cursor

        now = datetime.now().isoformat()

        cursor.execute('''
            UPDATE duty_returns
            SET status = ?, submitted_date = ?, updated_at = ?
            WHERE duty_month = ?
        ''', ('submitted', now, now, self.current_month))

        self.cache.connection.commit()

        messagebox.showinfo("Submitted", f"Duty return for {self.current_month} marked as submitted!")
        self.load_duty_return()

    def mark_paid(self):
        """Mark return as paid"""
        payment_date = self.payment_date_entry.get().strip()
        payment_ref = self.payment_ref_entry.get().strip()

        if not payment_date:
            messagebox.showerror("Error", "Please enter payment date before marking as paid.")
            return

        # Save first
        self.save_return()

        # Update status
        self.cache.connect()

        cursor = self.cache.cursor

        now = datetime.now().isoformat()

        cursor.execute('''
            UPDATE duty_returns
            SET status = ?, updated_at = ?
            WHERE duty_month = ?
        ''', ('paid', now, self.current_month))

        self.cache.connection.commit()

        messagebox.showinfo("Success", f"Duty return for {self.current_month} marked as paid!")
        self.load_duty_return()

    def view_packaging_lines(self):
        """View all packaging lines for this month"""
        PackagingLinesDialog(self, self.cache, self.current_month)


class PackagingLinesDialog(tk.Toplevel):
    """Dialog showing all packaging lines for a duty month"""

    def __init__(self, parent, cache, duty_month):
        super().__init__(parent)
        self.cache = cache
        self.duty_month = duty_month

        self.title(f"Packaging Lines - {duty_month}")
        self.geometry("1200x600")
        self.transient(parent)
        self.grab_set()

        self.create_widgets()
        self.load_data()

    def create_widgets(self):
        """Create widgets"""
        # Title
        ttk.Label(
            self,
            text=f"All Packaging Lines for {self.duty_month}",
            font=("Helvetica", 12, "bold")
        ).pack(pady=10)

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

    def load_data(self):
        """Load packaging lines"""
        self.cache.connect()

        cursor = self.cache.cursor

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
