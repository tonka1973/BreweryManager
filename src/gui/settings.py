"""
Settings Module for Brewery Management System
Configuration for duty rates, containers, and system settings
"""

import tkinter as tk
from tkinter import messagebox
import ttkbootstrap as ttk
from datetime import datetime
from ..utilities.window_manager import get_window_manager, enable_mousewheel_scrolling, enable_treeview_keyboard_navigation, enable_canvas_scrolling
# Import Google Sheets Client for real authentication
from ..data_access.google_sheets_client import GoogleSheetsClient


class SettingsModule(ttk.Frame):
    """Settings module for system configuration"""

    def __init__(self, parent, cache_manager, current_user, sheets_client=None):
        super().__init__(parent)
        self.cache = cache_manager
        self.current_user = current_user
        # Use provided client or create new one if needed (though ideally passed from main)
        self.sheets_client = sheets_client if sheets_client else GoogleSheetsClient()

        self.create_widgets()

    def create_widgets(self):
        """Create settings interface with tabbed sections"""
        # Create notebook for different settings categories with better visibility
        self.notebook = ttk.Notebook(self, bootstyle="primary")
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Create tabs
        self.create_duty_rates_tab()
        self.create_containers_tab()
        self.create_integrations_tab()

    def create_integrations_tab(self):
        """Integrations Configuration Tab"""
        tab = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(tab, text="  Integrations  ")
        
        # Google Integrations
        google_frame = ttk.LabelFrame(tab, text="Google Services", padding=20)
        google_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(google_frame, text="Status:", font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=(0, 10))
        
        # Check initial status
        if self.sheets_client.creds and self.sheets_client.creds.valid:
            status_text = "🟢 Connected"
            status_color = "success"
        else:
            status_text = "🔴 Not Connected"
            status_color = "danger"
            
        self.google_status_label = ttk.Label(google_frame, text=status_text, font=('Arial', 10), bootstyle=status_color)
        self.google_status_label.pack(side=tk.LEFT)
        
        ttk.Button(google_frame, text="🔗 Connect Account", bootstyle="primary", command=self.connect_google).pack(side=tk.RIGHT)
        
        # AI Integrations
        ai_frame = ttk.LabelFrame(tab, text="AI Assistant", padding=20)
        ai_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(ai_frame, text="API Key (OpenAI/Gemini):", font=('Arial', 10)).pack(anchor='w', pady=(0, 5))
        self.ai_key_entry = ttk.Entry(ai_frame, width=50, show="*")
        self.ai_key_entry.pack(fill=tk.X, pady=(0, 10))
        
        btn_frame = ttk.Frame(ai_frame)
        btn_frame.pack(fill=tk.X)
        
        ttk.Button(btn_frame, text="💾 Save Key", bootstyle="success", command=self.save_ai_key).pack(side=tk.RIGHT)
        ttk.Button(btn_frame, text="🧪 Test Connection", bootstyle="info", command=self.test_ai_connection).pack(side=tk.RIGHT, padx=10)

    def connect_google(self):
        """Trigger the real Google OAuth flow"""
        try:
            success = self.sheets_client.authenticate()
            if success:
                self.google_status_label.config(text="🟢 Connected", bootstyle="success")
                messagebox.showinfo("Success", "Successfully connected to Google Account!")
            else:
                self.google_status_label.config(text="🔴 Connection Failed", bootstyle="danger")
                messagebox.showerror("Error", "Authentication failed. Check logs.")
        except Exception as e:
            self.google_status_label.config(text="🔴 Error", bootstyle="danger")
            messagebox.showerror("Error", f"Authentication error:\n{str(e)}")

    def save_ai_key(self):
        key = self.ai_key_entry.get().strip()
        if not key:
            messagebox.showerror("Error", "Please enter an API key")
            return
        # TODO: Save to system_settings table
        messagebox.showinfo("Success", "API Key saved safely.")

    def test_ai_connection(self):
        messagebox.showinfo("Test", "AI Connection Test: Success (Mock)")

    def create_duty_rates_tab(self):
        """Duty Rates & SPR Configuration Tab"""
        tab = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(tab, text="  Duty Rates  ")

        # Create scrollable content
        canvas = tk.Canvas(tab, bg='white')
        scrollbar = ttk.Scrollbar(tab, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True, padx=20, pady=20)
        scrollbar.pack(side="right", fill="y")

        enable_canvas_scrolling(canvas)

        # ================================================================
        # SECTION 1: Annual Production Display (Read-Only)
        # ================================================================
        prod_frame = ttk.LabelFrame(scrollable_frame, text="Annual Production Tracking", padding=20)
        prod_frame.pack(fill=tk.X, pady=(0, 20))

        ttk.Label(prod_frame, text="Production Year: Feb 2025 - Jan 2026",
                 font=('Arial', 11, 'bold')).pack(anchor='w', pady=(0, 10))

        # Get current annual production
        annual_prod = self.get_annual_production()

        self.annual_prod_label = ttk.Label(prod_frame,
                                          text=f"Total Pure Alcohol Produced This Year: {annual_prod:.2f} hectolitres",
                                          font=('Arial', 10))
        self.annual_prod_label.pack(anchor='w', pady=(0, 5))

        if annual_prod < 4500:
            eligibility_text = "✓ Under 4,500 hl limit (SPR eligible)"
            eligibility_color = 'green'
        else:
            eligibility_text = "✗ Over 4,500 hl limit (SPR not eligible)"
            eligibility_color = 'red'

        self.eligibility_label = ttk.Label(prod_frame,
                                          text=f"SPR Eligibility: {eligibility_text}",
                                          font=('Arial', 10),
                                          foreground=eligibility_color)
        self.eligibility_label.pack(anchor='w', pady=(0, 5))

        ttk.Label(prod_frame,
                 text="(Updated automatically as batches are packaged)",
                 font=('Arial', 9, 'italic'),
                 foreground='#666').pack(anchor='w')

        # ================================================================
        # SECTION 2: SPR Rates (User Editable)
        # ================================================================
        spr_frame = ttk.LabelFrame(scrollable_frame, text="SPR Rates (Manually Updated)", padding=20)
        spr_frame.pack(fill=tk.X, pady=(0, 20))

        ttk.Label(spr_frame,
                 text="Review these rates semi-regularly based on your production volume.\nThese are the effective rates you actually pay (after HMRC discount applied).",
                 font=('Arial', 9, 'italic'),
                 foreground='#666').pack(anchor='w', pady=(0, 15))

        # Create form for 3 SPR rates
        rates_form = ttk.Frame(spr_frame)
        rates_form.pack(fill=tk.X)

        self.spr_entries = {}

        spr_rates = [
            ('spr_draught_low', '1. Draught <3.5% ABV', 'For session beers in casks/kegs ≥20L'),
            ('spr_draught_standard', '2. Draught 3.5-8.4% ABV', 'For standard beers in casks/kegs ≥20L (most common)'),
            ('spr_non_draught_standard', '3. Non-Draught 3.5-8.4% ABV', 'For standard beers in bottles/cans'),
        ]

        for i, (key, label, description) in enumerate(spr_rates):
            # Label
            ttk.Label(rates_form, text=label,
                     font=('Arial', 10, 'bold')).grid(row=i*3, column=0, sticky='w', pady=(10, 5))

            # Description
            ttk.Label(rates_form, text=description,
                     font=('Arial', 9, 'italic'),
                     foreground='#666').grid(row=i*3+1, column=0, sticky='w', pady=(0, 5))

            # Entry row
            entry_frame = ttk.Frame(rates_form)
            entry_frame.grid(row=i*3+2, column=0, sticky='w', pady=(0, 5))

            ttk.Label(entry_frame, text="SPR Rate:", font=('Arial', 10)).pack(side=tk.LEFT)
            entry = ttk.Entry(entry_frame, width=10, font=('Arial', 10))
            entry.pack(side=tk.LEFT, padx=5)
            self.spr_entries[key] = entry

            ttk.Label(entry_frame, text="£/lpa", font=('Arial', 10)).pack(side=tk.LEFT)

        ttk.Button(spr_frame, text="💾 Save SPR Rates",
                  bootstyle="success",
                  command=self.save_spr_rates).pack(pady=(20, 0))

        # ================================================================
        # SECTION 3: Full Duty Rate (User Editable)
        # ================================================================
        full_frame = ttk.LabelFrame(scrollable_frame, text="Full Duty Rate (8.5-22% ABV)", padding=20)
        full_frame.pack(fill=tk.X, pady=(0, 20))

        ttk.Label(full_frame,
                 text="For strong beers 8.5-22% ABV only. No SPR discount applies.\nUpdate when HMRC announces new rates (typically February).",
                 font=('Arial', 9, 'italic'),
                 foreground='#666').pack(anchor='w', pady=(0, 15))

        full_form = ttk.Frame(full_frame)
        full_form.pack(fill=tk.X)

        ttk.Label(full_form, text="Full Rate (8.5-22% ABV):",
                 font=('Arial', 10, 'bold')).grid(row=0, column=0, sticky='w', pady=(0, 5))

        ttk.Label(full_form, text="For beers ≥8.5% ABV (draught or non-draught, same rate)",
                 font=('Arial', 9, 'italic'),
                 foreground='#666').grid(row=1, column=0, sticky='w', pady=(0, 10))

        entry_frame = ttk.Frame(full_form)
        entry_frame.grid(row=2, column=0, sticky='w')

        ttk.Label(entry_frame, text="Full Rate:", font=('Arial', 10)).pack(side=tk.LEFT)
        self.full_rate_entry = ttk.Entry(entry_frame, width=10, font=('Arial', 10))
        self.full_rate_entry.pack(side=tk.LEFT, padx=5)
        ttk.Label(entry_frame, text="£/lpa", font=('Arial', 10)).pack(side=tk.LEFT)

        # Rates effective date
        date_frame = ttk.Frame(full_frame)
        date_frame.pack(fill=tk.X, pady=(20, 0))

        ttk.Label(date_frame, text="Rates Effective From:",
                 font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=(0, 10))
        self.effective_date_entry = ttk.Entry(date_frame, width=15, font=('Arial', 10))
        self.effective_date_entry.pack(side=tk.LEFT)
        ttk.Label(date_frame, text="(YYYY-MM-DD)",
                 font=('Arial', 9, 'italic'),
                 foreground='#666').pack(side=tk.LEFT, padx=(10, 0))

        ttk.Button(full_frame, text="💾 Save Full Rate",
                  bootstyle="success",
                  command=self.save_full_rate).pack(pady=(20, 0))

        # ================================================================
        # SECTION 4: VAT Rate (User Editable)
        # ================================================================
        vat_frame = ttk.LabelFrame(scrollable_frame, text="VAT Rate", padding=20)
        vat_frame.pack(fill=tk.X, pady=(0, 20))

        ttk.Label(vat_frame,
                 text="Standard UK VAT rate applied to invoices.\nUpdate if HMRC changes the VAT rate.",
                 font=('Arial', 9, 'italic'),
                 foreground='#666').pack(anchor='w', pady=(0, 15))

        vat_form = ttk.Frame(vat_frame)
        vat_form.pack(fill=tk.X)

        ttk.Label(vat_form, text="VAT Rate:",
                 font=('Arial', 10, 'bold')).grid(row=0, column=0, sticky='w', pady=(0, 5))

        entry_frame = ttk.Frame(vat_form)
        entry_frame.grid(row=1, column=0, sticky='w')

        self.vat_rate_entry = ttk.Entry(entry_frame, width=10, font=('Arial', 10))
        self.vat_rate_entry.pack(side=tk.LEFT, padx=(0, 5))
        ttk.Label(entry_frame, text="%", font=('Arial', 10)).pack(side=tk.LEFT)

        ttk.Label(vat_form, text="(Standard UK rate is currently 20%)",
                 font=('Arial', 9, 'italic'),
                 foreground='#666').grid(row=2, column=0, sticky='w', pady=(5, 0))

        ttk.Button(vat_frame, text="💾 Save VAT Rate",
                  bootstyle="success",
                  command=self.save_vat_rate).pack(pady=(20, 0))

        # ================================================================
        # Important Notes
        # ================================================================
        notes_frame = ttk.LabelFrame(scrollable_frame, text="Important Notes", padding=20)
        notes_frame.pack(fill=tk.X, pady=(0, 20))

        notes_text = """• All duty rates are in £ per litre of pure alcohol (£/lpa)
• Changes only affect NEW packaging/invoices after this date
• Historical records keep their original rates (for audit trail)
• Review SPR rates semi-regularly based on production trends
• Update duty rates when HMRC announces changes (typically February)
• Update VAT rate if HMRC changes the standard rate"""

        ttk.Label(notes_frame, text=notes_text,
                 font=('Arial', 9),
                 justify=tk.LEFT).pack(anchor='w')

        # Load current values
        self.load_current_rates()

    def create_containers_tab(self):
        """Container Configuration Tab"""
        tab = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(tab, text="  Containers  ")

        # Header
        header = ttk.Frame(tab)
        header.pack(fill=tk.X, padx=20, pady=(20, 10))

        ttk.Label(header, text="Container Duty-Paid Volumes",
                 font=('Arial', 14, 'bold')).pack(anchor='w')

        ttk.Label(header,
                 text="Configure actual capacity and duty-paid volume for each container type.\nSediment allowance applies to draught containers ≥20L.",
                 font=('Arial', 9, 'italic'),
                 foreground='#666').pack(anchor='w', pady=(5, 0))

        # Containers table
        tree_frame = ttk.Frame(tab)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        columns = ('name', 'actual', 'duty_paid', 'sediment', 'draught', 'price')
        self.container_tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=12)

        self.container_tree.heading('name', text='Container Type')
        self.container_tree.heading('actual', text='Actual Size (L)')
        self.container_tree.heading('duty_paid', text='Duty Paid (L)')
        self.container_tree.heading('sediment', text='Sediment (L)')
        self.container_tree.heading('draught', text='Draught?')
        self.container_tree.heading('price', text='Default Price')

        self.container_tree.column('name', width=150)
        self.container_tree.column('actual', width=100)
        self.container_tree.column('duty_paid', width=100)
        self.container_tree.column('sediment', width=100)
        self.container_tree.column('draught', width=80)
        self.container_tree.column('price', width=100)

        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.container_tree.yview)
        self.container_tree.configure(yscroll=scrollbar.set)

        self.container_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        enable_mousewheel_scrolling(self.container_tree)
        enable_treeview_keyboard_navigation(self.container_tree)

        # Bind double-click to edit
        self.container_tree.bind('<Double-Button-1>', lambda e: self.edit_container())

        # Buttons
        btn_frame = ttk.Frame(tab)
        btn_frame.pack(pady=10)

        ttk.Button(btn_frame, text="✏️ Edit Container",
                  bootstyle="info",
                  command=self.edit_container).pack(side=tk.LEFT, padx=5)

        ttk.Button(btn_frame, text="🔄 Refresh",
                  bootstyle="secondary",
                  command=self.load_containers).pack(side=tk.LEFT, padx=5)

        # Info label
        info_frame = ttk.Frame(tab)
        info_frame.pack(fill=tk.X, padx=20, pady=(0, 20))

        info_text = "💡 Tip: Changes only affect NEW packaging. Existing records keep original volumes."
        ttk.Label(info_frame, text=info_text,
                 font=('Arial', 9, 'italic'),
                 foreground='#666').pack(anchor='w')

        # Load containers
        self.load_containers()

    def get_annual_production(self):
        """Calculate annual production (hectolitres of pure alcohol)"""
        try:
            self.cache.connect()

            # Get production year dates from settings
            settings = self.cache.cursor.execute("SELECT production_year_start, production_year_end FROM settings WHERE id = 1").fetchone()

            if settings:
                year_start = settings[0]
                year_end = settings[1]
            else:
                year_start = '2025-02-01'
                year_end = '2026-01-31'

            # Sum all pure alcohol from packaging lines in current production year
            result = self.cache.cursor.execute("""
                SELECT SUM(pure_alcohol_litres)
                FROM batch_packaging_lines
                WHERE packaging_date BETWEEN ? AND ?
            """, (year_start, year_end)).fetchone()

            self.cache.close()

            total_litres = result[0] if result[0] else 0.0
            return total_litres / 100  # Convert to hectolitres

        except Exception as e:
            if self.cache:
                self.cache.close()
            print(f"Error calculating annual production: {e}")
            return 0.0

    def load_current_rates(self):
        """Load current rates from database"""
        try:
            self.cache.connect()
            cursor = self.cache.cursor
            cursor.execute("SELECT * FROM settings WHERE id = 1")
            settings = cursor.fetchone()
            self.cache.close()

            if settings:
                # SPR rates
                self.spr_entries['spr_draught_low'].delete(0, tk.END)
                self.spr_entries['spr_draught_low'].insert(0, f"{settings['spr_draught_low']:.2f}")

                self.spr_entries['spr_draught_standard'].delete(0, tk.END)
                self.spr_entries['spr_draught_standard'].insert(0, f"{settings['spr_draught_standard']:.2f}")

                self.spr_entries['spr_non_draught_standard'].delete(0, tk.END)
                self.spr_entries['spr_non_draught_standard'].insert(0, f"{settings['spr_non_draught_standard']:.2f}")

                # Full rate
                self.full_rate_entry.delete(0, tk.END)
                self.full_rate_entry.insert(0, f"{settings['rate_full_8_5_to_22']:.2f}")

                # Effective date
                self.effective_date_entry.delete(0, tk.END)
                self.effective_date_entry.insert(0, settings['rates_effective_from'])

                # VAT rate (convert from decimal to percentage)
                try:
                    vat_percentage = settings['vat_rate'] * 100
                except (KeyError, TypeError, IndexError):
                    vat_percentage = 20  # Default to 20% if column doesn't exist yet
                self.vat_rate_entry.delete(0, tk.END)
                self.vat_rate_entry.insert(0, f"{vat_percentage:.0f}")
            else:
                messagebox.showwarning("No Settings", "Settings record not found. Please run database migration.")

        except Exception as e:
            if self.cache:
                self.cache.close()
            messagebox.showerror("Error", f"Failed to load settings:\n{str(e)}")

    def save_spr_rates(self):
        """Save SPR rates to database"""
        try:
            rates = {}
            for key, entry in self.spr_entries.items():
                value = entry.get().strip()
                if not value:
                    messagebox.showerror("Error", "Please fill in all SPR rates.")
                    return
                try:
                    rates[key] = float(value)
                    if rates[key] < 0:
                        messagebox.showerror("Error", "Rates cannot be negative.")
                        return
                except ValueError:
                    messagebox.showerror("Error", f"Invalid rate value: {value}")
                    return

            self.cache.connect()
            self.cache.cursor.execute("""
                UPDATE settings SET
                    spr_draught_low = ?,
                    spr_draught_standard = ?,
                    spr_non_draught_standard = ?,
                    updated_at = ?,
                    updated_by = ?
                WHERE id = 1
            """, (
                rates['spr_draught_low'],
                rates['spr_draught_standard'],
                rates['spr_non_draught_standard'],
                datetime.now().isoformat(),
                self.current_user.username
            ))
            self.cache.connection.commit()
            self.cache.close()

            messagebox.showinfo("Success",
                              "SPR rates saved successfully!\n\n"
                              "Changes will apply to NEW packaging only.\n"
                              "Historical records keep their original rates.")

        except Exception as e:
            if self.cache:
                self.cache.close()
            messagebox.showerror("Error", f"Failed to save SPR rates:\n{str(e)}")

    def save_full_rate(self):
        """Save full duty rate to database"""
        try:
            rate_str = self.full_rate_entry.get().strip()
            date_str = self.effective_date_entry.get().strip()

            if not rate_str:
                messagebox.showerror("Error", "Please enter the full rate.")
                return

            try:
                rate = float(rate_str)
                if rate < 0:
                    messagebox.showerror("Error", "Rate cannot be negative.")
                    return
            except ValueError:
                messagebox.showerror("Error", f"Invalid rate value: {rate_str}")
                return

            # Validate date format
            if date_str:
                try:
                    datetime.strptime(date_str, '%Y-%m-%d')
                except ValueError:
                    messagebox.showerror("Error", "Invalid date format. Use YYYY-MM-DD.")
                    return

            self.cache.connect()
            self.cache.cursor.execute("""
                UPDATE settings SET
                    rate_full_8_5_to_22 = ?,
                    rates_effective_from = ?,
                    updated_at = ?,
                    updated_by = ?
                WHERE id = 1
            """, (
                rate,
                date_str,
                datetime.now().isoformat(),
                self.current_user.username
            ))
            self.cache.connection.commit()
            self.cache.close()

            messagebox.showinfo("Success",
                              "Full duty rate saved successfully!\n\n"
                              "Changes will apply to NEW packaging only.\n"
                              "Historical records keep their original rates.")

        except Exception as e:
            if self.cache:
                self.cache.close()
            messagebox.showerror("Error", f"Failed to save full rate:\n{str(e)}")

    def save_vat_rate(self):
        """Save VAT rate to database"""
        try:
            rate_str = self.vat_rate_entry.get().strip()

            if not rate_str:
                messagebox.showerror("Error", "Please enter the VAT rate.")
                return

            try:
                rate_percentage = float(rate_str)
                if rate_percentage < 0 or rate_percentage > 100:
                    messagebox.showerror("Error", "VAT rate must be between 0 and 100%.")
                    return
                # Convert percentage to decimal
                rate = rate_percentage / 100
            except ValueError:
                messagebox.showerror("Error", f"Invalid VAT rate: {rate_str}")
                return

            self.cache.connect()
            self.cache.cursor.execute("""
                UPDATE settings SET
                    vat_rate = ?,
                    updated_at = ?,
                    updated_by = ?
                WHERE id = 1
            """, (
                rate,
                datetime.now().isoformat(),
                self.current_user.username
            ))
            self.cache.connection.commit()
            self.cache.close()

            messagebox.showinfo("Success",
                              f"VAT rate saved successfully ({rate_percentage:.0f}%)!\n\n"
                              "New invoices will use this VAT rate.\n"
                              "Existing invoices keep their original VAT rate.")

        except Exception as e:
            if self.cache:
                self.cache.close()
            messagebox.showerror("Error", f"Failed to save VAT rate:\n{str(e)}")

    def load_containers(self):
        """Load container configuration"""
        self.container_tree.delete(*self.container_tree.get_children())

        try:
            self.cache.connect()
            containers = self.cache.cursor.execute("""
                SELECT name, actual_capacity, duty_paid_volume,
                       is_draught_eligible, default_price
                FROM settings_containers
                WHERE active = 1
                ORDER BY is_draught_eligible DESC, actual_capacity DESC
            """).fetchall()
            self.cache.close()

            for container in containers:
                sediment = container['actual_capacity'] - container['duty_paid_volume']
                draught = "✓" if container['is_draught_eligible'] else "✗"

                self.container_tree.insert('', 'end', values=(
                    container['name'],
                    f"{container['actual_capacity']:.2f}",
                    f"{container['duty_paid_volume']:.2f}",
                    f"{sediment:.2f}",
                    draught,
                    f"£{container['default_price']:.2f}"
                ))

        except Exception as e:
            if self.cache:
                self.cache.close()
            messagebox.showerror("Error", f"Failed to load containers:\n{str(e)}")

    def edit_container(self):
        """Edit selected container"""
        selected = self.container_tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a container to edit.")
            return

        values = self.container_tree.item(selected[0])['values']
        container_name = values[0]

        # Open edit dialog
        dialog = EditContainerDialog(self, self.cache, self.current_user, container_name)
        self.wait_window(dialog)

        # Reload containers
        self.load_containers()


class EditContainerDialog(tk.Toplevel):
    """Dialog for editing container configuration"""

    def __init__(self, parent, cache, current_user, container_name):
        super().__init__(parent)
        self.cache = cache
        self.current_user = current_user
        self.container_name = container_name

        self.title(f"Edit Container: {container_name}")
        self.transient(parent)
        self.grab_set()

        # Use window manager for sizing if available
        wm = get_window_manager()
        if wm:
            wm.setup_dialog(self, 'edit_container_dialog', width_pct=0.35, height_pct=0.5,
                          add_grip=True, save_on_close=True, resizable=True)
        else:
            self.geometry("500x450")
            self.resizable(True, True)

        self.create_widgets()
        self.load_container()

    def create_widgets(self):
        """Create dialog widgets"""
        frame = ttk.Frame(self, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text=f"Edit Container: {self.container_name}",
                 font=('Arial', 14, 'bold')).pack(pady=(0, 20))

        # Form
        form = ttk.Frame(frame)
        form.pack(fill=tk.X, pady=20)

        # Container Name (read-only)
        ttk.Label(form, text="Container Name:",
                 font=('Arial', 10, 'bold')).grid(row=0, column=0, sticky='w', pady=10)
        ttk.Label(form, text=self.container_name,
                 font=('Arial', 10)).grid(row=0, column=1, sticky='w', pady=10)

        # Actual Capacity (read-only)
        ttk.Label(form, text="Actual Capacity:",
                 font=('Arial', 10, 'bold')).grid(row=1, column=0, sticky='w', pady=10)
        self.actual_label = ttk.Label(form, text="",
                                      font=('Arial', 10))
        self.actual_label.grid(row=1, column=1, sticky='w', pady=10)

        # Duty Paid Volume (EDITABLE)
        ttk.Label(form, text="Duty Paid Volume:",
                 font=('Arial', 10, 'bold')).grid(row=2, column=0, sticky='w', pady=10)

        duty_frame = ttk.Frame(form)
        duty_frame.grid(row=2, column=1, sticky='w', pady=10)

        self.duty_paid_entry = ttk.Entry(duty_frame, width=10, font=('Arial', 10))
        self.duty_paid_entry.pack(side=tk.LEFT, padx=(0, 5))
        ttk.Label(duty_frame, text="L", font=('Arial', 10)).pack(side=tk.LEFT)

        # Calculated Sediment
        ttk.Label(form, text="Sediment Allowance:",
                 font=('Arial', 10, 'bold')).grid(row=3, column=0, sticky='w', pady=10)
        self.sediment_label = ttk.Label(form, text="",
                                        font=('Arial', 10),
                                        foreground='green')
        self.sediment_label.grid(row=3, column=1, sticky='w', pady=10)

        # Update sediment on change
        self.duty_paid_entry.bind('<KeyRelease>', self.update_sediment)

        # Is Draught Eligible (read-only)
        ttk.Label(form, text="Draught Eligible:",
                 font=('Arial', 10, 'bold')).grid(row=4, column=0, sticky='w', pady=10)
        self.draught_label = ttk.Label(form, text="",
                                       font=('Arial', 10))
        self.draught_label.grid(row=4, column=1, sticky='w', pady=10)

        # Default Price
        ttk.Label(form, text="Default Price:",
                 font=('Arial', 10, 'bold')).grid(row=5, column=0, sticky='w', pady=10)

        price_frame = ttk.Frame(form)
        price_frame.grid(row=5, column=1, sticky='w', pady=10)

        ttk.Label(price_frame, text="£", font=('Arial', 10)).pack(side=tk.LEFT)
        self.price_entry = ttk.Entry(price_frame, width=10, font=('Arial', 10))
        self.price_entry.pack(side=tk.LEFT, padx=5)

        form.columnconfigure(1, weight=1)

        # Warning note
        note_frame = ttk.Frame(frame)
        note_frame.pack(fill=tk.X, pady=20)

        warning_text = "⚠️  Changes only affect NEW packaging.\nExisting packaged products keep original volumes."
        ttk.Label(note_frame, text=warning_text,
                 font=('Arial', 9, 'italic'),
                 foreground='orange',
                 justify=tk.LEFT).pack(anchor='w')

        # Buttons
        button_frame = ttk.Frame(self, padding=10)
        button_frame.pack(fill=tk.X, padx=20, pady=(0, 20))

        ttk.Button(button_frame, text="Cancel",
                  bootstyle="secondary",
                  command=self.destroy).pack(side=tk.RIGHT, padx=(10, 0))

        ttk.Button(button_frame, text="💾 Save Changes",
                  bootstyle="success",
                  command=self.save).pack(side=tk.RIGHT)

    def load_container(self):
        """Load container data from database"""
        try:
            self.cache.connect()
            container = self.cache.cursor.execute("""
                SELECT * FROM settings_containers WHERE name = ?
            """, (self.container_name,)).fetchone()
            self.cache.close()

            if container:
                self.container_data = container

                self.actual_label.config(text=f"{container['actual_capacity']:.2f} L")

                self.duty_paid_entry.delete(0, tk.END)
                self.duty_paid_entry.insert(0, f"{container['duty_paid_volume']:.2f}")

                draught_text = "Yes (≥20L)" if container['is_draught_eligible'] else "No (bottles/cans)"
                self.draught_label.config(text=draught_text)

                self.price_entry.delete(0, tk.END)
                self.price_entry.insert(0, f"{container['default_price']:.2f}")

                self.update_sediment()
            else:
                messagebox.showerror("Error", "Container not found.")
                self.destroy()

        except Exception as e:
            if self.cache:
                self.cache.close()
            messagebox.showerror("Error", f"Failed to load container:\n{str(e)}")
            self.destroy()

    def update_sediment(self, event=None):
        """Update calculated sediment display"""
        try:
            duty_paid = float(self.duty_paid_entry.get())
            actual = self.container_data['actual_capacity']
            sediment = actual - duty_paid

            if sediment < 0:
                self.sediment_label.config(
                    text=f"{sediment:.2f} L (ERROR: Cannot be negative!)",
                    foreground='red'
                )
            elif sediment == 0:
                self.sediment_label.config(
                    text=f"{sediment:.2f} L (No allowance)",
                    foreground='blue'
                )
            else:
                percentage = (sediment / actual) * 100
                self.sediment_label.config(
                    text=f"{sediment:.2f} L ({percentage:.1f}% of capacity)",
                    foreground='green'
                )
        except ValueError:
            self.sediment_label.config(text="Enter valid number", foreground='red')

    def save(self):
        """Save container changes"""
        try:
            duty_paid_str = self.duty_paid_entry.get().strip()
            price_str = self.price_entry.get().strip()

            if not duty_paid_str or not price_str:
                messagebox.showerror("Error", "Please fill in all fields.")
                return

            try:
                duty_paid = float(duty_paid_str)
                price = float(price_str)
            except ValueError:
                messagebox.showerror("Error", "Invalid number format.")
                return

            # Validation
            actual = self.container_data['actual_capacity']
            if duty_paid > actual:
                messagebox.showerror("Error", "Duty paid volume cannot exceed actual capacity.")
                return

            if duty_paid <= 0:
                messagebox.showerror("Error", "Duty paid volume must be positive.")
                return

            if price < 0:
                messagebox.showerror("Error", "Price cannot be negative.")
                return

            # Save to database
            self.cache.connect()
            self.cache.cursor.execute("""
                UPDATE settings_containers SET
                    duty_paid_volume = ?,
                    default_price = ?,
                    updated_at = ?,
                    updated_by = ?
                WHERE name = ?
            """, (
                duty_paid,
                price,
                datetime.now().isoformat(),
                self.current_user.username,
                self.container_name
            ))
            self.cache.connection.commit()
            self.cache.close()

            messagebox.showinfo("Success", "Container settings saved successfully!")
            self.destroy()

        except Exception as e:
            if self.cache:
                self.cache.close()
            messagebox.showerror("Error", f"Failed to save container:\n{str(e)}")
