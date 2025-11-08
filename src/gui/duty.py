"""
Duty Calculator Module for Brewery Management System
HMRC-compliant UK alcohol duty calculations with SPR and Draught Relief
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from src.config.constants import DUTY_RATES, DRAUGHT_RELIEF_BEER_CIDER, VAT_RATE


class DutyModule(tk.Frame):
    """Duty Calculator module for HMRC-compliant calculations"""

    def __init__(self, parent, cache_manager, current_user):
        super().__init__(parent, bg='white')
        self.cache = cache_manager
        self.current_user = current_user

        self.create_widgets()

    def create_widgets(self):
        """Create duty calculator widgets"""
        # Header
        header = tk.Frame(self, bg='white')
        header.pack(fill=tk.X, padx=20, pady=(0, 20))

        tk.Label(header, text="UK Alcohol Duty Calculator",
                font=('Arial', 16, 'bold'), bg='white',
                fg='#2c3e50').pack(side=tk.LEFT)

        tk.Label(header, text="HMRC Compliant | February 2025 Rates",
                font=('Arial', 9, 'italic'), bg='white',
                fg='#7f8c8d').pack(side=tk.RIGHT)

        # Two-column layout
        content = tk.Frame(self, bg='white')
        content.pack(fill=tk.BOTH, expand=True, padx=20)

        # Left: Calculator
        left = tk.Frame(content, bg='white')
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        self.create_calculator(left)

        # Right: Rates Reference
        right = tk.Frame(content, bg='white')
        right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0))

        self.create_rates_reference(right)

    def create_calculator(self, parent):
        """Create calculator section"""
        calc_frame = tk.Frame(parent, bg='white', relief=tk.SOLID, borderwidth=1)
        calc_frame.pack(fill=tk.BOTH, expand=True)

        # Title
        tk.Label(calc_frame, text="Calculate Duty", font=('Arial', 13, 'bold'),
                bg='white', fg='#2c3e50').pack(pady=15)

        form = tk.Frame(calc_frame, bg='white', padx=20, pady=10)
        form.pack(fill=tk.BOTH, expand=True)

        # Volume
        tk.Label(form, text="Volume (Litres) *", font=('Arial', 10, 'bold'),
                bg='white').grid(row=0, column=0, sticky='w', pady=(0,5))
        self.volume_entry = tk.Entry(form, font=('Arial', 11), width=20)
        self.volume_entry.grid(row=1, column=0, sticky='ew', pady=(0,15))

        # ABV
        tk.Label(form, text="ABV % *", font=('Arial', 10, 'bold'),
                bg='white').grid(row=2, column=0, sticky='w', pady=(0,5))
        self.abv_entry = tk.Entry(form, font=('Arial', 11), width=20)
        self.abv_entry.grid(row=3, column=0, sticky='ew', pady=(0,15))

        # Draught
        self.draught_var = tk.IntVar(value=1)
        tk.Checkbutton(form, text="Draught (cask ≥20L)", variable=self.draught_var,
                      font=('Arial', 10), bg='white',
                      command=self.calculate).grid(row=4, column=0, sticky='w', pady=(0,15))

        # SPR Rate
        tk.Label(form, text="SPR Rate (£/hl) *", font=('Arial', 10, 'bold'),
                bg='white').grid(row=5, column=0, sticky='w', pady=(0,5))
        self.spr_entry = tk.Entry(form, font=('Arial', 11), width=20)
        self.spr_entry.insert(0, "4.87")
        self.spr_entry.grid(row=6, column=0, sticky='ew', pady=(0,15))

        tk.Label(form, text="(Current small brewery rate)", font=('Arial', 9, 'italic'),
                bg='white', fg='#7f8c8d').grid(row=7, column=0, sticky='w', pady=(0,15))

        # Calculate button
        tk.Button(form, text="Calculate Duty", font=('Arial', 11, 'bold'),
                 bg='#4CAF50', fg='white', cursor='hand2',
                 command=self.calculate, padx=20, pady=10).grid(row=8, column=0, pady=(10,20))

        form.grid_columnconfigure(0, weight=1)

        # Results
        self.results_frame = tk.Frame(calc_frame, bg='#e8f5e9', relief=tk.SOLID, borderwidth=1)
        self.results_frame.pack(fill=tk.X, padx=20, pady=(0,20))

        self.results_label = tk.Label(self.results_frame, text="Enter values and click Calculate",
                                      font=('Arial', 10), bg='#e8f5e9',
                                      fg='#2c3e50', justify=tk.LEFT, pady=15)
        self.results_label.pack()

    def create_rates_reference(self, parent):
        """Create rates reference section"""
        ref_frame = tk.Frame(parent, bg='white', relief=tk.SOLID, borderwidth=1)
        ref_frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(ref_frame, text="Duty Rates Reference", font=('Arial', 13, 'bold'),
                bg='white', fg='#2c3e50').pack(pady=15)

        info = tk.Frame(ref_frame, bg='white', padx=20, pady=10)
        info.pack(fill=tk.BOTH, expand=True)

        # Standard rates
        tk.Label(info, text="Beer Rates (Feb 2025)", font=('Arial', 11, 'bold'),
                bg='white', fg='#34495e').pack(anchor='w', pady=(0,10))

        rates_text = """
Non-Draught:
• 1.3-3.4% ABV: £9.61/hl
• 3.5-8.4% ABV: £21.78/hl
• 8.5-22% ABV: £29.54/hl

Draught (≥20L containers):
• 1.3-3.4% ABV: £8.28/hl (13.9% relief)
• 3.5-8.4% ABV: £18.76/hl (13.9% relief)
• 8.5-22% ABV: £29.54/hl (no relief)

Small Producer Relief (SPR):
Reduces duty rate based on annual
production volume (up to 4,500 hl).

Current rate varies by brewery size.
Typical range: £4-£10 per hectolitre.
        """

        tk.Label(info, text=rates_text.strip(), font=('Arial', 9),
                bg='white', fg='#555', justify=tk.LEFT).pack(anchor='w', pady=(0,15))

        # Example
        example_frame = tk.Frame(info, bg='#fff3e0', relief=tk.SOLID, borderwidth=1)
        example_frame.pack(fill=tk.X, pady=(10,0))

        example_text = """
Example Calculation:

800L batch at 4.2% ABV (draught)
Pure alcohol: 33.6L (800 × 0.042)

Base rate: £18.76/hl
SPR rate: £4.87/hl
Effective rate: £18.76 - £4.87 = £13.89/hl

Duty: 3.36 hl × £13.89 = £46.67
        """

        tk.Label(example_frame, text=example_text.strip(),
                font=('Arial', 9), bg='#fff3e0',
                fg='#333', justify=tk.LEFT).pack(padx=10, pady=10, anchor='w')

    def calculate(self):
        """Calculate duty"""
        try:
            volume_l = float(self.volume_entry.get())
            abv = float(self.abv_entry.get())
            spr_rate = float(self.spr_entry.get())
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers.")
            return

        if volume_l <= 0 or abv <= 0:
            messagebox.showerror("Error", "Volume and ABV must be positive.")
            return

        # Calculate pure alcohol in hectolitres
        pure_alcohol_l = volume_l * (abv / 100)
        pure_alcohol_hl = pure_alcohol_l / 100

        # Determine base duty rate
        is_draught = self.draught_var.get() == 1
        duty_type = 'beer_draught' if is_draught else 'beer_non_draught'

        base_rate = self.get_duty_rate(abv, duty_type)

        # Apply SPR
        effective_rate = max(0, base_rate - spr_rate)

        # Calculate duty
        duty_payable = pure_alcohol_hl * effective_rate

        # Build results
        results = f"""
DUTY CALCULATION RESULTS

Volume: {volume_l:.1f} litres
ABV: {abv:.1f}%
Type: {'Draught (cask)' if is_draught else 'Non-draught (bottles/kegs)'}

Pure Alcohol: {pure_alcohol_l:.2f} litres ({pure_alcohol_hl:.4f} hl)

Base Duty Rate: £{base_rate:.2f}/hl
SPR Discount: £{spr_rate:.2f}/hl
Effective Rate: £{effective_rate:.2f}/hl

DUTY PAYABLE: £{duty_payable:.2f}

(Rates valid February 2025)
        """

        self.results_label.config(text=results.strip(), font=('Arial', 10, 'bold'))

        # Highlight based on amount
        if duty_payable > 100:
            self.results_frame.config(bg='#ffebee')
            self.results_label.config(bg='#ffebee')
        else:
            self.results_frame.config(bg='#e8f5e9')
            self.results_label.config(bg='#e8f5e9')

    def get_duty_rate(self, abv, duty_type):
        """Get duty rate for ABV and type"""
        rates = DUTY_RATES.get(duty_type, {})

        for (min_abv, max_abv), rate in rates.items():
            if min_abv <= abv <= max_abv:
                return rate

        return 0.0


class DutyBatchCalculator(tk.Toplevel):
    """Calculate duty for specific batch"""

    def __init__(self, parent, cache, batch):
        super().__init__(parent)
        self.cache = cache
        self.batch = batch

        self.title(f"Duty Calculator: {batch.get('gyle_number', 'Unknown')}")
        self.geometry("500x400")
        self.transient(parent)
        self.grab_set()

        self.create_widgets()
        self.calculate_duty()

    def create_widgets(self):
        """Create widgets"""
        frame = tk.Frame(self, bg='white', padx=30, pady=20)
        frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(frame, text=f"Batch: {self.batch.get('gyle_number', 'Unknown')}",
                font=('Arial', 16, 'bold'), bg='white').pack(pady=(0,20))

        self.info_label = tk.Label(frame, text="Calculating...",
                                   font=('Arial', 10), bg='white',
                                   justify=tk.LEFT)
        self.info_label.pack(pady=20)

        tk.Button(self, text="Close", font=('Arial', 10), bg='#607D8B',
                 fg='white', command=self.destroy, padx=20, pady=8).pack(pady=(0,20))

    def calculate_duty(self):
        """Calculate duty for batch"""
        volume = self.batch.get('actual_batch_size', 0)
        abv = self.batch.get('measured_abv', 0)
        pure_alcohol = self.batch.get('pure_alcohol_litres', 0)
        is_draught = self.batch.get('is_draught', 1)
        spr_rate = self.batch.get('spr_rate_applied', 4.87)

        if not abv or not volume:
            self.info_label.config(text="Batch missing ABV or volume data.")
            return

        pure_alcohol_hl = pure_alcohol / 100

        duty_type = 'beer_draught' if is_draught else 'beer_non_draught'
        rates = DUTY_RATES.get(duty_type, {})

        base_rate = 0.0
        for (min_abv, max_abv), rate in rates.items():
            if min_abv <= abv <= max_abv:
                base_rate = rate
                break

        effective_rate = max(0, base_rate - spr_rate)
        duty = pure_alcohol_hl * effective_rate

        info = f"""
Volume: {volume:.1f} litres
ABV: {abv:.1f}%
Pure Alcohol: {pure_alcohol:.2f} litres

Type: {'Draught' if is_draught else 'Non-draught'}
Base Rate: £{base_rate:.2f}/hl
SPR Rate: £{spr_rate:.2f}/hl
Effective Rate: £{effective_rate:.2f}/hl

DUTY PAYABLE: £{duty:.2f}
        """

        self.info_label.config(text=info.strip())
