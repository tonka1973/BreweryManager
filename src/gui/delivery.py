
import tkinter as tk
import ttkbootstrap as ttk
from tkinter import messagebox
from ..utilities.window_manager import get_window_manager, enable_mousewheel_scrolling
from ..utilities.date_utils import format_date_for_display
from .components import ScrollableFrame
try:
    import tkintermapview
except ImportError:
    tkintermapview = None

class DeliveryModule(ttk.Frame):
    """Delivery management module"""

    def __init__(self, parent, cache_manager, current_user, sync_callback=None):
        super().__init__(parent)
        self.cache = cache_manager
        self.current_user = current_user
        self.sync_callback = sync_callback
        
        self.create_widgets()
        self.load_deliveries()

    def create_widgets(self):
        """Create module content"""
        # Toolbar
        toolbar = ttk.Frame(self)
        toolbar.pack(fill=tk.X, padx=20, pady=(0, 10))

        ttk.Button(toolbar, text="🔄 Refresh", 
                  bootstyle="secondary", 
                  command=self.load_deliveries).pack(side=tk.LEFT)
        
        ttk.Button(toolbar, text="🚚 Create Run / Manifest", 
                  bootstyle="primary", 
                  command=self.create_run).pack(side=tk.LEFT, padx=10)

        # Main Content - Split View (List | Map)
        paned = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))

        # Left: List of Pending Deliveries
        list_frame = ttk.LabelFrame(paned, text="Pending Deliveries", padding=10)
        paned.add(list_frame, weight=1)

        columns = ('Date', 'Customer', 'Area', 'Items', 'Total')
        self.tree = ttk.Treeview(list_frame, columns=columns, show='headings')
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)
        
        self.tree.pack(fill=tk.BOTH, expand=True)
        enable_mousewheel_scrolling(self.tree)

        # Right: Map View
        map_frame = ttk.LabelFrame(paned, text="Route Planning", padding=10)
        paned.add(map_frame, weight=2)
        
        if tkintermapview:
            self.map_widget = tkintermapview.TkinterMapView(map_frame, width=600, height=400, corner_radius=0)
            self.map_widget.pack(fill=tk.BOTH, expand=True)
            # Default to UK roughly
            self.map_widget.set_position(54.0, -2.0) 
            self.map_widget.set_zoom(6)
        else:
            ttk.Label(map_frame, text="Map library not installed.\nrun: pip install tkintermapview", 
                     background="lightyellow", foreground="red").pack(expand=True)

    def load_deliveries(self):
        """Load pending deliveries"""
        self.tree.delete(*self.tree.get_children())
        if hasattr(self, 'map_widget') and self.map_widget:
            self.map_widget.delete_all_marker()

        self.cache.connect()
        try:
            # Get pending sales
            sales = self.cache.get_all_records('sales', "status = 'reserved'", "delivery_date ASC")
            
            for sale in sales:
                customer_name = 'Unknown'
                postcode = None
                if sale.get('customer_id'):
                    customers = self.cache.get_all_records('customers', f"customer_id = '{sale['customer_id']}'")
                    if customers:
                        customer = customers[0]
                        customer_name = customer.get('customer_name', 'Unknown')
                        # Extract postcode from address for map (simple extraction)
                        address = customer.get('delivery_address', '')
                        if address:
                             # Very basic check, ideally we have a separate postcode field
                             lines = address.split('\n')
                             postcode = lines[-1] 

                values = (
                    format_date_for_display(sale.get('delivery_date')),
                    customer_name,
                    "TBD", # Area
                    f"{sale.get('quantity')} x {sale.get('beer_name')}",
                    f"£{sale.get('line_total', 0):.2f}"
                )
                self.tree.insert('', 'end', values=values)

                # Add Marker to map (Simulated for now as we need geocoding)
                # In real app, we'd cache geocodes in the DB to avoid hitting API limits
                if self.map_widget and postcode:
                    # self.map_widget.set_address(postcode, marker=True, text=customer_name)
                    # For now just log it or skip to avoid freezing UI with HTTP calls
                    pass
                    
        finally:
            self.cache.close()

    def create_run(self):
        """Create a delivery run/manifest"""
        messagebox.showinfo("Coming Soon", "Route Builder coming in next update!")

