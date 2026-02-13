import tkinter as tk
import ttkbootstrap as ttk
from tkinter import messagebox
from ..utilities.date_utils import format_date_for_display, get_today_display
from ..utilities.window_manager import get_window_manager, enable_mousewheel_scrolling
from .invoicing import create_invoice_for_sales, PaymentDialog
from .sales_screen import SaleDialog

class OrderDetailsDialog(tk.Toplevel):
    def __init__(self, parent, cache_manager, current_user, sale_id):
        super().__init__(parent)
        self.cache = cache_manager
        self.current_user = current_user
        self.sale_id = sale_id
        
        self.title("Order Details")
        self.transient(parent)
        self.grab_set()

        wm = get_window_manager()
        if wm:
             wm.setup_dialog(self, 'order_details_dialog', width_pct=0.6, height_pct=0.7,
                          add_grip=True, save_on_close=True, resizable=True)
        else:
             self.geometry("800x600")
             self.resizable(True, True)

        self.sale_data = self.fetch_sale_data()
        if not self.sale_data:
             messagebox.showerror("Error", "Could not load order details.")
             self.destroy()
             return

        self.create_widgets()

    def fetch_sale_data(self):
        try:
            self.cache.connect()
            # 1. Fetch Target Sale
            sales = self.cache.get_all_records('sales', f"sale_id = '{self.sale_id}'")
            
            if not sales:
                self.cache.close()
                return None
                
            target_sale = sales[0]
            customer_id = target_sale.get('customer_id')
            sale_date = target_sale.get('sale_date')
            invoice_id = target_sale.get('invoice_id')
            
            # 2. Fetch Related Sales (The "Order Group")
            related_sales = []
            if invoice_id and invoice_id not in ['None', 'NULL', '']:
                # If invoiced, get complete invoice
                related_sales = self.cache.get_all_records('sales', f"invoice_id = '{invoice_id}'")
            else:
                # If not invoiced, get by Customer + Date + Uninvoiced
                related_sales = self.cache.get_all_records('sales', 
                    f"customer_id = '{customer_id}' AND sale_date = '{sale_date}' AND (invoice_id IS NULL OR invoice_id = '' OR invoice_id = 'None' OR invoice_id = 'NULL')")
            
            # 3. Fetch Customer Details
            customer = {}
            if customer_id:
                customers = self.cache.get_all_records('customers', f"customer_id = '{customer_id}'")
                if customers:
                    customer = customers[0]
            
            self.cache.close()
            
            if related_sales:
                return {'sales': related_sales, 'customer': customer}
            return None
        except Exception as e:
            print(f"Error fetching sale: {e}")
            if self.cache and self.cache.connection:
                self.cache.close()
            return None

    def create_widgets(self):
        # Header
        header_frame = ttk.Frame(self, padding=20)
        header_frame.pack(fill=tk.X)
        
        sales = self.sale_data['sales']
        primary_sale = sales[0]
        cust = self.sale_data['customer']

        # Title
        ttk.Label(header_frame, text="Order Details", font=('Arial', 18, 'bold')).pack(side=tk.LEFT)
        
        # Order Info
        info_frame = ttk.Frame(header_frame)
        info_frame.pack(side=tk.RIGHT)
        
        ttk.Label(info_frame, text=f"Order Date: {format_date_for_display(primary_sale.get('sale_date'))}", font=('Arial', 10)).pack(anchor='e')
        # Show first sale ID or "Multiple Items"
        ttk.Label(info_frame, text=f"Order #: {primary_sale.get('sale_id')[:8]}...", font=('Arial', 10)).pack(anchor='e')
        ttk.Label(info_frame, text=f"Status: {primary_sale.get('status', '').title()}", font=('Arial', 10, 'bold')).pack(anchor='e')

        ttk.Separator(self).pack(fill=tk.X, padx=20)

        # Customer Info
        cust_frame = ttk.Frame(self, padding=20)
        cust_frame.pack(fill=tk.X)
        
        ttk.Label(cust_frame, text="Customer:", font=('Arial', 12, 'bold')).pack(anchor='w')
        ttk.Label(cust_frame, text=cust.get('customer_name', 'Unknown'), font=('Arial', 11)).pack(anchor='w')
        ttk.Label(cust_frame, text=cust.get('delivery_address', ''), font=('Arial', 10)).pack(anchor='w')
        
        # Items Table
        list_frame = ttk.Frame(self, padding=20)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        columns = ('Item', 'Quantity', 'Unit Price', 'Total')
        tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=10)
        
        tree.heading('Item', text='Item')
        tree.heading('Quantity', text='Quantity')
        tree.heading('Unit Price', text='Unit Price')
        tree.heading('Total', text='Total')
        
        tree.column('Item', width=300)
        tree.column('Quantity', width=100)
        tree.column('Unit Price', width=100)
        tree.column('Total', width=100)
        
        total_net = 0.0
        
        for sale in sales:
            line_total = sale.get('line_total', 0)
            total_net += line_total
            values = (
                f"{sale.get('beer_name', '')} {sale.get('container_type', '')} {sale.get('container_size', '')}",
                sale.get('quantity', 0),
                f"£{sale.get('unit_price', 0):.2f}",
                f"£{line_total:.2f}"
            )
            tree.insert('', 'end', values=values)
        
        tree.pack(fill=tk.BOTH, expand=True)

        # Totals
        total_frame = ttk.Frame(self, padding=20)
        total_frame.pack(fill=tk.X)
        
        # Assuming standard VAT for now, can be sophisticated later
        vat_rate = 0.20
        vat = total_net * vat_rate
        grand_total = total_net + vat 
        
        # Just showing line total as Subtotal for now
        ttk.Label(total_frame, text=f"Subtotal: £{total_net:.2f}", font=('Arial', 10)).pack(anchor='e')
        ttk.Label(total_frame, text=f"VAT (20% est): £{vat:.2f}", font=('Arial', 10)).pack(anchor='e')
        ttk.Label(total_frame, text=f"Total: £{grand_total:.2f}", font=('Arial', 12, 'bold')).pack(anchor='e')

        # Action Buttons
        btn_frame = ttk.Frame(self, padding=20)
        btn_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        invoice_id = primary_sale.get('invoice_id')
        
        if not invoice_id:
            ttk.Button(btn_frame, text="Create Invoice", bootstyle="success", command=self.create_invoice).pack(side=tk.RIGHT, padx=5)
        else:
            ttk.Label(btn_frame, text=f"Invoiced: {invoice_id}", bootstyle="secondary").pack(side=tk.RIGHT, padx=5)
            # Add Payment Button if invoiced
            ttk.Button(btn_frame, text="Make Payment", bootstyle="warning", command=self.make_payment).pack(side=tk.RIGHT, padx=5)

        ttk.Button(btn_frame, text="Edit Order", bootstyle="info", command=self.edit_order).pack(side=tk.RIGHT, padx=5)
        ttk.Button(btn_frame, text="Print", bootstyle="secondary", state='disabled').pack(side=tk.RIGHT, padx=5) # Placeholder
        ttk.Button(btn_frame, text="Close", bootstyle="secondary", command=self.destroy).pack(side=tk.LEFT)

    def make_payment(self):
        sales = self.sale_data['sales']
        if not sales: return
        invoice_id = sales[0].get('invoice_id')
        
        if not invoice_id: return

        # Fetch invoice
        self.cache.connect()
        invoices = self.cache.get_all_records('invoices', f"invoice_id = '{invoice_id}'")
        self.cache.close()

        if invoices:
            dialog = PaymentDialog(self, self.cache, self.current_user, invoices[0])
            self.wait_window(dialog)
            # Refresh? Ideally yes, but this is a static view dialog.
            # Best to close and let dashboard refresh, or re-fetch logic.
            self.destroy()

    def create_invoice(self):
        if messagebox.askyesno("Confirm", "Create invoice for this order?"):
            sales = self.sale_data['sales']
            cust = self.sale_data['customer']
            
            # Collect ALL sale IDs
            sale_ids = [s['sale_id'] for s in sales]
            
            success, msg, inv_id = create_invoice_for_sales(
                self.cache, 
                self.current_user, 
                cust['customer_id'], 
                sale_ids
            )
            
            if success:
                messagebox.showinfo("Success", "Invoice Created!")
                self.destroy()
            else:
                messagebox.showerror("Error", msg)

    def edit_order(self):
        self.destroy()
        # Handle edit dialog opening
        try:
            from .sales_screen import SaleDialog
            # Pass the list of sales (the order group) to the edit dialog
            sales = self.sale_data['sales']
            dialog = SaleDialog(self.master, self.cache, self.current_user, mode='edit', 
                              sale=None, sales_list=sales)
            self.master.wait_window(dialog)
            
            # Refresh parent view
            if hasattr(self.master, 'load_dashboard_data'):
                self.master.load_dashboard_data()
            elif hasattr(self.master, 'load_sales'):
                 self.master.load_sales()
        except Exception as e:
            messagebox.showerror("Error", f"Could not open edit dialog: {e}")
