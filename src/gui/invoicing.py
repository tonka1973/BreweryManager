"""
Invoicing Module for Brewery Management System
Generate invoices and track payments
"""

import tkinter as tk
import ttkbootstrap as ttk
from tkinter import messagebox
import uuid
from datetime import datetime, timedelta
from ..utilities.date_utils import format_date_for_display, parse_display_date, get_today_display, get_today_db


class InvoicingModule(ttk.Frame):
    """Invoicing module for invoice generation and payment tracking"""

    def __init__(self, parent, cache_manager, current_user):
        super().__init__(parent)
        self.cache = cache_manager
        self.current_user = current_user

        self.create_widgets()
        self.load_invoices()

    def create_widgets(self):
        """Create invoicing widgets"""
        toolbar = ttk.Frame(self)
        toolbar.pack(fill=tk.X, padx=20, pady=(0, 10))

        ttk.Button(toolbar, text="➕ Create Invoice",
                  bootstyle="success",
                  command=self.create_invoice).pack(side=tk.LEFT, padx=(0, 10))

        ttk.Button(toolbar, text="💰 Record Payment",
                  bootstyle="primary",
                  command=self.record_payment).pack(side=tk.LEFT, padx=(0, 10))

        ttk.Button(toolbar, text="👁️ View Invoice",
                  bootstyle="info",
                  command=self.view_invoice).pack(side=tk.LEFT, padx=(0, 10))

        ttk.Button(toolbar, text="🔄 Refresh",
                  bootstyle="secondary",
                  command=self.load_invoices).pack(side=tk.LEFT)

        # Filter
        ttk.Label(toolbar, text="Status:").pack(side=tk.RIGHT, padx=(0,5))
        self.filter_var = tk.StringVar(value='all')
        self.filter_var.trace('w', lambda *args: self.load_invoices())
        ttk.Combobox(toolbar, textvariable=self.filter_var,
                    values=['all', 'unpaid', 'partially_paid', 'paid'],
                    width=12, state='readonly').pack(side=tk.RIGHT, padx=(10,0))

        # Invoice list
        list_frame = ttk.Frame(self)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))

        vsb = ttk.Scrollbar(list_frame, orient="vertical")
        vsb.pack(side=tk.RIGHT, fill=tk.Y)

        columns = ('Invoice #', 'Date', 'Customer', 'Subtotal', 'VAT', 'Total', 'Paid', 'Outstanding', 'Status')
        self.tree = ttk.Treeview(list_frame, columns=columns, show='headings', yscrollcommand=vsb.set)

        for col in columns:
            self.tree.heading(col, text=col)

        self.tree.column('Invoice #', width=120)
        self.tree.column('Date', width=100)
        self.tree.column('Customer', width=150)
        self.tree.column('Subtotal', width=80)
        self.tree.column('VAT', width=70)
        self.tree.column('Total', width=80)
        self.tree.column('Paid', width=80)
        self.tree.column('Outstanding', width=100)
        self.tree.column('Status', width=100)

        self.tree.pack(fill=tk.BOTH, expand=True)
        vsb.config(command=self.tree.yview)

    def load_invoices(self):
        """Load invoices from database"""
        for item in self.tree.get_children():
            self.tree.delete(item)

        status_filter = self.filter_var.get()
        where = None if status_filter == 'all' else f"payment_status = '{status_filter}'"

        self.cache.connect()
        invoices = self.cache.get_all_records('invoices', where, 'invoice_date DESC')
        self.cache.close()

        for inv in invoices:
            # Get customer name
            customer_name = 'Unknown'
            if inv.get('customer_id'):
                self.cache.connect()
                customers = self.cache.get_all_records('customers', f"customer_id = '{inv['customer_id']}'")
                self.cache.close()
                if customers:
                    customer_name = customers[0]['customer_name']

            values = (
                inv.get('invoice_number', ''),
                format_date_for_display(inv.get('invoice_date', '')),
                customer_name,
                f"£{inv.get('subtotal', 0):.2f}",
                f"£{inv.get('vat_amount', 0):.2f}",
                f"£{inv.get('total', 0):.2f}",
                f"£{inv.get('amount_paid', 0):.2f}",
                f"£{inv.get('amount_outstanding', 0):.2f}",
                inv.get('payment_status', '').replace('_', ' ').title()
            )

            status = inv.get('payment_status', 'unpaid')
            self.tree.insert('', 'end', values=values, tags=(f'status_{status}', inv['invoice_id']))

        self.tree.tag_configure('status_unpaid', background='#ffebee')
        self.tree.tag_configure('status_partially_paid', background='#fff3e0')
        self.tree.tag_configure('status_paid', background='#e8f5e9')

    def create_invoice(self):
        """Create new invoice from delivered sales"""
        dialog = InvoiceCreateDialog(self, self.cache, self.current_user)
        self.wait_window(dialog)
        self.load_invoices()

    def record_payment(self):
        """Record payment for invoice"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select an invoice.")
            return

        tags = self.tree.item(selection[0], 'tags')
        invoice_id = tags[1] if len(tags) > 1 else None

        self.cache.connect()
        invoices = self.cache.get_all_records('invoices', f"invoice_id = '{invoice_id}'")
        self.cache.close()

        if invoices:
            dialog = PaymentDialog(self, self.cache, self.current_user, invoices[0])
            self.wait_window(dialog)
            self.load_invoices()

    def view_invoice(self):
        """View invoice details"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select an invoice.")
            return

        tags = self.tree.item(selection[0], 'tags')
        invoice_id = tags[1] if len(tags) > 1 else None

        self.cache.connect()
        invoices = self.cache.get_all_records('invoices', f"invoice_id = '{invoice_id}'")
        lines = self.cache.get_all_records('invoice_lines', f"invoice_id = '{invoice_id}'")
        self.cache.close()

        if invoices:
            dialog = InvoiceViewDialog(self, invoices[0], lines, self.cache)
            self.wait_window(dialog)


class InvoiceCreateDialog(tk.Toplevel):
    """Dialog for creating invoice from sales"""

    def __init__(self, parent, cache_manager, current_user):
        super().__init__(parent)
        self.cache = cache_manager
        self.current_user = current_user

        self.title("Create Invoice")
        self.geometry("700x600")
        self.transient(parent)
        self.grab_set()

        self.create_widgets()

    def create_widgets(self):
        """Create widgets"""
        frame = ttk.Frame(self, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text="Create Invoice from Delivered Sales",
                 font=('Arial', 14, 'bold')).pack(pady=(0,20))

        # Customer selection
        ttk.Label(frame, text="Customer *", font=('Arial', 10, 'bold')).pack(anchor='w', pady=(0,5))
        self.customer_var = tk.StringVar()
        self.cache.connect()
        customers = self.cache.get_all_records('customers', 'is_active = 1', 'customer_name')
        self.cache.close()
        self.customer_list = {c['customer_name']: c['customer_id'] for c in customers}
        customer_combo = ttk.Combobox(frame, textvariable=self.customer_var,
                                     values=list(self.customer_list.keys()),
                                     width=40, state='readonly')
        customer_combo.pack(anchor='w', pady=(0,15))
        customer_combo.bind('<<ComboboxSelected>>', self.load_sales)

        # Sales list
        ttk.Label(frame, text="Delivered Sales (not yet invoiced):",
                 font=('Arial', 10, 'bold')).pack(anchor='w', pady=(0,5))

        sales_frame = ttk.Frame(frame)
        sales_frame.pack(fill=tk.BOTH, expand=True, pady=(0,15))

        vsb = ttk.Scrollbar(sales_frame, orient="vertical")
        vsb.pack(side=tk.RIGHT, fill=tk.Y)

        columns = ('Select', 'Date', 'Beer', 'Qty', 'Price', 'Total')
        self.sales_tree = ttk.Treeview(sales_frame, columns=columns,
                                       show='tree headings', yscrollcommand=vsb.set)

        self.sales_tree.heading('#0', text='')
        self.sales_tree.column('#0', width=30)
        for col in columns[1:]:
            self.sales_tree.heading(col, text=col)
            self.sales_tree.column(col, width=100)

        self.sales_tree.pack(fill=tk.BOTH, expand=True)
        vsb.config(command=self.sales_tree.yview)

        # VAT Rate
        vat_frame = ttk.Frame(frame)
        vat_frame.pack(fill=tk.X, pady=(10,0))

        ttk.Label(vat_frame, text="VAT Rate:", font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=(0,10))
        self.vat_var = tk.StringVar(value="20")
        ttk.Entry(vat_frame, textvariable=self.vat_var, font=('Arial', 10),
                 width=10).pack(side=tk.LEFT)
        ttk.Label(vat_frame, text="%", font=('Arial', 10)).pack(side=tk.LEFT, padx=(5,0))

        # Buttons
        button_frame = ttk.Frame(self, padding=(20, 10))
        button_frame.pack(fill=tk.X)

        ttk.Button(button_frame, text="Cancel",
                  bootstyle="secondary",
                  command=self.destroy).pack(side=tk.RIGHT, padx=(10,0))
        ttk.Button(button_frame, text="Create Invoice",
                  bootstyle="success",
                  command=self.create).pack(side=tk.RIGHT)

    def load_sales(self, event=None):
        """Load uninvoiced sales for customer"""
        for item in self.sales_tree.get_children():
            self.sales_tree.delete(item)

        customer_name = self.customer_var.get()
        if not customer_name or customer_name not in self.customer_list:
            return

        customer_id = self.customer_list[customer_name]

        self.cache.connect()
        sales = self.cache.get_all_records('sales',
                                          f"customer_id = '{customer_id}' AND status = 'delivered' AND (invoice_id IS NULL OR invoice_id = '')",
                                          'delivery_date DESC')
        self.cache.close()

        for sale in sales:
            values = ('☐', format_date_for_display(sale.get('delivery_date', '')), sale.get('beer_name', ''),
                     sale.get('quantity', 0), f"£{sale.get('unit_price', 0):.2f}",
                     f"£{sale.get('line_total', 0):.2f}")
            self.sales_tree.insert('', 'end', text='', values=values, tags=(sale['sale_id'],))

        self.sales_tree.bind('<Button-1>', self.toggle_select)

    def toggle_select(self, event):
        """Toggle selection checkmark"""
        region = self.sales_tree.identify("region", event.x, event.y)
        if region == "cell":
            item = self.sales_tree.identify_row(event.y)
            if item:
                values = list(self.sales_tree.item(item, 'values'))
                values[0] = '☑' if values[0] == '☐' else '☐'
                self.sales_tree.item(item, values=values)

    def create(self):
        """Create invoice"""
        customer_name = self.customer_var.get()
        if not customer_name:
            messagebox.showerror("Error", "Please select a customer.")
            return

        # Get selected sales
        selected_sales = []
        for item in self.sales_tree.get_children():
            values = self.sales_tree.item(item, 'values')
            if values[0] == '☑':
                tags = self.sales_tree.item(item, 'tags')
                selected_sales.append(tags[0])

        if not selected_sales:
            messagebox.showerror("Error", "Please select at least one sale.")
            return

        # Calculate totals
        self.cache.connect()
        subtotal = 0
        for sale_id in selected_sales:
            sales = self.cache.get_all_records('sales', f"sale_id = '{sale_id}'")
            if sales:
                subtotal += sales[0].get('line_total', 0)

        vat_rate = float(self.vat_var.get()) / 100
        vat_amount = subtotal * vat_rate
        total = subtotal + vat_amount

        # Generate invoice number
        year = datetime.now().year
        invoices = self.cache.get_all_records('invoices', f"invoice_number LIKE 'INV-{year}-%'")
        next_num = len(invoices) + 1
        invoice_number = f"INV-{year}-{next_num:04d}"

        # Create invoice
        invoice_id = str(uuid.uuid4())
        invoice_data = {
            'invoice_id': invoice_id,
            'invoice_number': invoice_number,
            'invoice_date': get_today_db(),
            'customer_id': self.customer_list[customer_name],
            'subtotal': subtotal,
            'vat_rate': vat_rate,
            'vat_amount': vat_amount,
            'total': total,
            'payment_status': 'unpaid',
            'amount_paid': 0,
            'amount_outstanding': total,
            'due_date': parse_display_date((datetime.now() + timedelta(days=30)).strftime('%d/%m/%Y')),
            'created_by': self.current_user.username,
            'created_date': get_today_db(),
            'sync_status': 'pending'
        }
        self.cache.insert_record('invoices', invoice_data)

        # Create invoice lines
        for sale_id in selected_sales:
            sales = self.cache.get_all_records('sales', f"sale_id = '{sale_id}'")
            if sales:
                sale = sales[0]
                line_data = {
                    'line_id': str(uuid.uuid4()),
                    'invoice_id': invoice_id,
                    'sale_id': sale_id,
                    'description': f"{sale.get('beer_name', '')} - {sale.get('container_type', '')}",
                    'quantity': sale.get('quantity', 0),
                    'unit_price': sale.get('unit_price', 0),
                    'line_total': sale.get('line_total', 0),
                    'gyle_number': sale.get('gyle_number', ''),
                    'sync_status': 'pending'
                }
                self.cache.insert_record('invoice_lines', line_data)

                # Update sale with invoice_id
                self.cache.update_record('sales', sale_id, {'invoice_id': invoice_id}, 'sale_id')

        self.cache.close()

        messagebox.showinfo("Success", f"Invoice {invoice_number} created!\n\nTotal: £{total:.2f}")
        self.destroy()


class PaymentDialog(tk.Toplevel):
    """Dialog for recording payment"""

    def __init__(self, parent, cache_manager, current_user, invoice):
        super().__init__(parent)
        self.cache = cache_manager
        self.current_user = current_user
        self.invoice = invoice

        self.title(f"Record Payment: {invoice.get('invoice_number', '')}")
        self.geometry("450x400")
        self.transient(parent)
        self.grab_set()

        self.create_widgets()

    def create_widgets(self):
        """Create widgets"""
        frame = ttk.Frame(self, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)

        outstanding = self.invoice.get('amount_outstanding', 0)
        ttk.Label(frame, text=f"Outstanding: £{outstanding:.2f}",
                 font=('Arial', 14, 'bold'),
                 bootstyle="danger").pack(pady=(0,20))

        # Payment Amount
        ttk.Label(frame, text="Payment Amount (£) *", font=('Arial', 10, 'bold')).pack(anchor='w', pady=(0,5))
        self.amount_entry = ttk.Entry(frame, font=('Arial', 11), width=20)
        self.amount_entry.insert(0, f"{outstanding:.2f}")
        self.amount_entry.pack(anchor='w', pady=(0,15))

        # Payment Method
        ttk.Label(frame, text="Payment Method", font=('Arial', 10, 'bold')).pack(anchor='w', pady=(0,5))
        self.method_var = tk.StringVar(value='bank_transfer')
        ttk.Combobox(frame, textvariable=self.method_var,
                    values=['cash', 'cheque', 'bank_transfer', 'card', 'other'],
                    width=17, state='readonly').pack(anchor='w', pady=(0,15))

        # Payment Date
        ttk.Label(frame, text="Payment Date (DD/MM/YYYY)", font=('Arial', 10, 'bold')).pack(anchor='w', pady=(0,5))
        self.date_entry = ttk.Entry(frame, font=('Arial', 10), width=20)
        self.date_entry.insert(0, get_today_display())
        self.date_entry.pack(anchor='w', pady=(0,15))

        # Reference
        ttk.Label(frame, text="Reference", font=('Arial', 10, 'bold')).pack(anchor='w', pady=(0,5))
        self.ref_entry = ttk.Entry(frame, font=('Arial', 10), width=30)
        self.ref_entry.pack(anchor='w', pady=(0,15))

        # Buttons
        button_frame = ttk.Frame(self, padding=(20, 10))
        button_frame.pack(fill=tk.X)

        ttk.Button(button_frame, text="Cancel",
                  bootstyle="secondary",
                  command=self.destroy).pack(side=tk.RIGHT, padx=(10,0))
        ttk.Button(button_frame, text="Record Payment",
                  bootstyle="success",
                  command=self.record).pack(side=tk.RIGHT)

    def record(self):
        """Record payment"""
        try:
            amount = float(self.amount_entry.get())
        except ValueError:
            messagebox.showerror("Error", "Invalid amount.")
            return

        if amount <= 0:
            messagebox.showerror("Error", "Amount must be positive.")
            return

        outstanding = self.invoice.get('amount_outstanding', 0)
        if amount > outstanding:
            messagebox.showerror("Error", f"Amount exceeds outstanding balance (£{outstanding:.2f}).")
            return

        # Convert date from display format to database format
        payment_date_db = parse_display_date(self.date_entry.get())
        if not payment_date_db:
            messagebox.showerror("Error", "Invalid payment date format. Please use DD/MM/YYYY.")
            return

        # Create payment record
        payment_data = {
            'payment_id': str(uuid.uuid4()),
            'invoice_id': self.invoice['invoice_id'],
            'payment_date': payment_date_db,
            'payment_amount': amount,
            'payment_method': self.method_var.get(),
            'payment_reference': self.ref_entry.get().strip(),
            'recorded_by': self.current_user.username,
            'recorded_date': get_today_db(),
            'sync_status': 'pending'
        }

        # Update invoice
        new_paid = self.invoice.get('amount_paid', 0) + amount
        new_outstanding = outstanding - amount

        if new_outstanding <= 0.01:  # Fully paid (accounting for rounding)
            status = 'paid'
            new_outstanding = 0
        else:
            status = 'partially_paid'

        invoice_update = {
            'amount_paid': new_paid,
            'amount_outstanding': new_outstanding,
            'payment_status': status,
            'sync_status': 'pending'
        }

        self.cache.connect()
        self.cache.insert_record('payments', payment_data)
        self.cache.update_record('invoices', self.invoice['invoice_id'], invoice_update, 'invoice_id')
        self.cache.close()

        messagebox.showinfo("Success", f"Payment of £{amount:.2f} recorded!")
        self.destroy()


class InvoiceViewDialog(tk.Toplevel):
    """Dialog for viewing invoice"""

    def __init__(self, parent, invoice, lines, cache):
        super().__init__(parent)
        self.invoice = invoice
        self.lines = lines
        self.cache = cache

        self.title(f"Invoice: {invoice.get('invoice_number', '')}")
        self.geometry("650x650")
        self.transient(parent)
        self.grab_set()

        self.create_widgets()

    def create_widgets(self):
        """Create widgets"""
        frame = ttk.Frame(self, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text=self.invoice.get('invoice_number', ''),
                 font=('Arial', 18, 'bold')).pack(anchor='w', pady=(0,10))

        # Customer
        customer_name = 'Unknown'
        if self.invoice.get('customer_id'):
            self.cache.connect()
            customers = self.cache.get_all_records('customers', f"customer_id = '{self.invoice['customer_id']}'")
            self.cache.close()
            if customers:
                customer_name = customers[0]['customer_name']

        info = f"""
Customer: {customer_name}
Invoice Date: {format_date_for_display(self.invoice.get('invoice_date')) or 'N/A'}
Due Date: {format_date_for_display(self.invoice.get('due_date')) or 'N/A'}
Status: {self.invoice.get('payment_status', '').replace('_', ' ').title()}
        """

        ttk.Label(frame, text=info.strip(), font=('Arial', 10),
                 justify=tk.LEFT).pack(anchor='w', pady=(0,20))

        # Line items
        ttk.Label(frame, text="Items:", font=('Arial', 11, 'bold')).pack(anchor='w', pady=(0,10))

        for line in self.lines:
            # Keep tk.Frame for colored line items background
            line_frame = tk.Frame(frame, bg='#e3f2fd')
            line_frame.pack(fill=tk.X, pady=2)

            line_text = f"{line.get('description', '')} x {line.get('quantity', 0)} @ £{line.get('unit_price', 0):.2f} = £{line.get('line_total', 0):.2f}"
            if line.get('gyle_number'):
                line_text += f" ({line['gyle_number']})"

            tk.Label(line_frame, text=line_text, font=('Arial', 10),
                    bg='#e3f2fd').pack(padx=10, pady=5, anchor='w')

        # Totals
        totals = f"""
Subtotal: £{self.invoice.get('subtotal', 0):.2f}
VAT ({self.invoice.get('vat_rate', 0)*100:.0f}%): £{self.invoice.get('vat_amount', 0):.2f}
Total: £{self.invoice.get('total', 0):.2f}

Amount Paid: £{self.invoice.get('amount_paid', 0):.2f}
Outstanding: £{self.invoice.get('amount_outstanding', 0):.2f}
        """

        # Keep tk.Frame for colored totals background
        totals_frame = tk.Frame(frame, bg='#fff3e0', relief=tk.SOLID, borderwidth=1)
        totals_frame.pack(fill=tk.X, pady=(20,0))

        tk.Label(totals_frame, text=totals.strip(), font=('Arial', 10, 'bold'),
                bg='#fff3e0', justify=tk.RIGHT).pack(padx=10, pady=10, anchor='e')

        ttk.Button(self, text="Close",
                  bootstyle="secondary",
                  command=self.destroy).pack(pady=(0,20))
