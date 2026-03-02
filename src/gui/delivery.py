
import tkinter as tk
import ttkbootstrap as ttk
from tkinter import messagebox, colorchooser
from ..utilities.window_manager import get_window_manager, enable_mousewheel_scrolling
from ..utilities.date_utils import format_date_for_display
from .components import ScrollableFrame
try:
    import tkintermapview
except ImportError:
    tkintermapview = None

try:
    import pgeocode
except ImportError:
    pgeocode = None

import webbrowser
import urllib.parse
from datetime import datetime, timedelta
import math

class DeliveryModule(ttk.Frame):
    """Delivery management module for planning runs and managing dispatches"""

    def __init__(self, parent, cache_manager, current_user, sync_callback=None):
        super().__init__(parent)
        self.cache = cache_manager
        self.current_user = current_user
        self.sync_callback = sync_callback
        self.nomi = pgeocode.Nominatim('gb') if pgeocode else None
        
        self.create_widgets()
        self.load_deliveries()

    def create_widgets(self):
        """Create module content"""
        # Toolbar
        toolbar = ttk.Frame(self)
        toolbar.pack(fill=tk.X, padx=20, pady=(0, 10))

        # Filter
        ttk.Label(toolbar, text="Filter Date:").pack(side=tk.LEFT, padx=(0, 5))
        self.filter_var = tk.StringVar(value='All Pending')
        self.filter_cb = ttk.Combobox(toolbar, textvariable=self.filter_var, 
                                     values=['All Pending', 'Today', 'Tomorrow'], 
                                     state='readonly', width=15)
        self.filter_cb.pack(side=tk.LEFT, padx=(0, 10))
        self.filter_cb.bind('<<ComboboxSelected>>', lambda e: self.load_deliveries())

        ttk.Button(toolbar, text="🔄 Refresh", 
                  bootstyle="secondary", 
                  command=self.load_deliveries).pack(side=tk.LEFT, padx=(0, 10))
        
        # Action Buttons
        ttk.Button(toolbar, text="📍 Manage Zones", 
                  bootstyle="warning", 
                  command=self.manage_zones).pack(side=tk.LEFT, padx=(0, 5))

        ttk.Button(toolbar, text="📋 Picking List", 
                  bootstyle="info", 
                  command=self.print_picking_list).pack(side=tk.LEFT, padx=(0, 5))

        ttk.Button(toolbar, text="🚚 Run Sheet", 
                  bootstyle="primary", 
                  command=self.print_run_sheet).pack(side=tk.LEFT, padx=(0, 5))

        ttk.Button(toolbar, text="🗺️ Plan Route", 
                  bootstyle="success", 
                  command=self.plan_route).pack(side=tk.LEFT, padx=(0, 5))

        # Main Content - Split View (List | Map)
        paned = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))

        # Left: List of Pending Deliveries
        list_frame = ttk.LabelFrame(paned, text="Delivery Runs", padding=10)
        paned.add(list_frame, weight=1)

        columns = ('Date', 'Area', 'Customer', 'Items', 'Total')
        self.tree = ttk.Treeview(list_frame, columns=columns, show='headings')
        
        # Configure Headers for Sorting
        for col in columns:
            self.tree.heading(col, text=col, command=lambda c=col: self.treeview_sort_column(self.tree, c, False))
            self.tree.column(col, width=100)
        
        # Adjust column widths
        self.tree.column('Date', width=90)
        self.tree.column('Area', width=100)
        self.tree.column('Customer', width=180)
        self.tree.column('Items', width=250)
        self.tree.column('Total', width=80)

        self.tree.pack(fill=tk.BOTH, expand=True)
        enable_mousewheel_scrolling(self.tree)

        # Right: Map View
        map_frame = ttk.LabelFrame(paned, text="Map Visualization", padding=10)
        paned.add(map_frame, weight=2)
        
        if tkintermapview:
            self.map_widget = tkintermapview.TkinterMapView(map_frame, width=600, height=400, corner_radius=0)
            self.map_widget.pack(fill=tk.BOTH, expand=True)
            # Bind Double-Click Zoom Globally
            self.map_widget.canvas.bind("<Double-Button-1>", self._global_double_click_zoom)
            
            # Default to UK
            self.map_widget.set_position(54.0, -2.0) 
            self.map_widget.set_zoom(6)
        else:
            ttk.Label(map_frame, text="Map library not installed.\nrun: pip install tkintermapview", 
                     background="lightyellow", foreground="red").pack(expand=True)
    def _global_double_click_zoom(self, event):
        """Zoom in on double click everywhere on the map"""
        if hasattr(self, 'map_widget') and self.map_widget:
            current_zoom = self.map_widget.zoom
            self.map_widget.set_zoom(current_zoom + 1)

    def load_deliveries(self):
        """Load pending deliveries based on filter"""
        self.tree.delete(*self.tree.get_children())
        if hasattr(self, 'map_widget') and self.map_widget:
            self.map_widget.delete_all_marker()
            self.map_widget.delete_all_polygon()

        filter_mode = self.filter_var.get()
        today = datetime.now().date()
        tomorrow = today + timedelta(days=1)

        self.cache.connect()
        try:
            # 1. Fetch Zones
            zones = self.cache.get_all_records('delivery_zones')
            zone_map = {z['zone_name']: z for z in zones} # Name -> Data
            
            # Map of Postcode Prefix -> Zone Name
            # We iterate zones and their prefixes
            pc_to_zone = {}
            for z in zones:
                prefixes = [p.strip().upper() for p in z.get('postcode_prefixes', '').split(',')]
                for p in prefixes:
                    if p: pc_to_zone[p] = z

            # 2. Draw Zones on Map
            if self.map_widget and self.nomi:
                self.draw_zones_on_map(zones)

            # 3. Fetch Data
            sales = self.cache.get_all_records('sales', "status = 'reserved'", "delivery_date ASC")
            all_customers = {c['customer_id']: c for c in self.cache.get_all_records('customers')}

            # 4. Group by (Date, Area, Customer)
            grouped_deliveries = {} 

            for sale in sales:
                # Date Filter
                del_date_str = sale.get('delivery_date')
                if not del_date_str: continue 

                try:
                    del_date = datetime.strptime(del_date_str, '%Y-%m-%d').date()
                    if filter_mode == 'Today' and del_date != today: continue
                    if filter_mode == 'Tomorrow' and del_date != tomorrow: continue
                except: continue 

                # Customer Data
                cust_id = sale.get('customer_id')
                customer = all_customers.get(cust_id, {})
                cust_name = customer.get('customer_name', 'Unknown')
                
                # Determine Area (Zone > Manual Area > TBD)
                manual_area = customer.get('delivery_area')
                
                # Auto-detect Zone from Postcode
                detected_zone = None
                postcode = None
                address = customer.get('delivery_address', '')
                if address:
                    lines = address.split('\n')
                    postcode = lines[-1].strip().upper()
                    
                    # Check prefix matching
                    # Iterate pc_to_zone keys, verify if postcode STARTS with it
                    # Sort keys by length desc to match longest prefix first (e.g., M11 vs M1)
                    for prefix, zone_data in sorted(pc_to_zone.items(), key=lambda x: len(x[0]), reverse=True):
                         if postcode.startswith(prefix):
                             detected_zone = zone_data['zone_name']
                             break
                
                final_area = detected_zone if detected_zone else (manual_area or 'TBD')

                # Group Key
                key = (del_date_str, final_area, cust_id)

                if key not in grouped_deliveries:
                    grouped_deliveries[key] = {
                        'customer_name': cust_name,
                        'items': [],
                        'total': 0.0,
                        'postcode': postcode,
                        'address': address
                    }
                
                item_desc = f"{sale.get('quantity')} x {sale.get('beer_name')} ({sale.get('container_type')})"
                grouped_deliveries[key]['items'].append(item_desc)
                grouped_deliveries[key]['total'] += sale.get('line_total', 0)

            # 5. Display Data
            for key, data in grouped_deliveries.items():
                date_str, area, _ = key
                items_text = ", ".join(data['items'])
                
                values = (
                    format_date_for_display(date_str),
                    area,
                    f"{data['customer_name']} ({len(data['items'])} items)",
                    items_text,
                    f"£{data['total']:.2f}"
                )
                
                route_data = f"{data['customer_name']}|{data['postcode']}|{data['address']}"
                self.tree.insert('', 'end', values=values, tags=(route_data,))

                # Add Simple Marker for Delivery
                if self.map_widget and data['postcode'] and self.nomi:
                    # Async or Cached Geocoding would be better
                    # For prototype, we do it inline but catch errors
                    try:
                        location = self.nomi.query_postal_code(data['postcode'])
                        if not math.isnan(location.latitude):
                             self.map_widget.set_marker(location.latitude, location.longitude, text=data['customer_name'])
                    except: pass

        finally:
            self.cache.close()

    def draw_zones_on_map(self, zones):
        """Draw polygons for zones based on their prefixes"""
        all_zone_points = []
        
        for zone in zones:
            points = []
            color = zone.get('color', 'blue')
            # Extract prefixes, handling comma/space separation
            prefixes = [p.strip().upper() for p in zone.get('postcode_prefixes', '').replace(';',',').split(',')]
            
            # 0. Check for Custom Polygon
            import json
            custom_coords = None
            if zone.get('polygon_coords'):
                try: 
                    custom_coords = json.loads(zone.get('polygon_coords'))
                    if custom_coords and len(custom_coords) >= 3:
                         print(f"DEBUG: Drawing Custom Polygon for {zone['zone_name']}")
                         self.map_widget.set_polygon(custom_coords, fill_color=color, border_width=2, name=zone['zone_name'])
                         # Add marker at first point or centroid
                         c = custom_coords[0] 
                         self.map_widget.set_marker(c[0], c[1], text=zone['zone_name'], marker_color_circle=color, marker_color_outside=color)
                         all_zone_points.extend(custom_coords)
                         continue # Skip auto-generation
                except Exception as e:
                    print(f"DEBUG: Error loading custom coords: {e}")

            # 1. Get Lat/Lon for prefixes (centroids)
            if self.nomi:
                for p in prefixes:
                    if not p: continue
                    print(f"DEBUG: Processing prefix '{p}' for zone '{zone.get('zone_name')}'")
                    try:
                        query = p.split(' ')[0]
                        loc = self.nomi.query_postal_code(query)
                        
                        if not math.isnan(loc.latitude):
                             print(f"DEBUG: Found Coords: {loc.latitude}, {loc.longitude}")
                             points.append((loc.latitude, loc.longitude))
                             all_zone_points.append((loc.latitude, loc.longitude))
                        else:
                             print(f"DEBUG: Invalid coordinate for prefix: {query}")
                    except Exception as e: 
                        print(f"DEBUG: Geocode error {p}: {e}")

            print(f"DEBUG: Points for zone: {len(points)}")
            if len(points) >= 3:
                # Draw Convex Hull
                try:
                    hull_points = self.convex_hull(points)
                    print(f"DEBUG: Drawing Polygon with {len(hull_points)} points")
                    self.map_widget.set_polygon(hull_points, fill_color=color, border_width=2, name=zone['zone_name'])
                    # Also add a label marker in the center
                    center = self.get_centroid(points)
                    self.map_widget.set_marker(center[0], center[1], text=zone['zone_name'], marker_color_circle=color, marker_color_outside=color)
                except Exception as e:
                    print(f"DEBUG: Polygon error: {e}")
            elif len(points) == 1:
                # Single point - Draw a circle approximation (Radius ~3km)
                print("DEBUG: Single point zone - Generating circle")
                center = points[0]
                circle_points = []
                radius = 0.03 # Approx 3km in degrees
                for i in range(12): # 12 points for a rough circle
                    angle = math.radians(float(i) * 30)
                    dx = radius * math.cos(angle)
                    dy = radius * math.sin(angle)
                    circle_points.append((center[0] + dx, center[1] + dy))
                
                self.map_widget.set_polygon(circle_points, fill_color=color, border_width=2, name=zone['zone_name'])
                self.map_widget.set_marker(center[0], center[1], text=zone['zone_name'], marker_color_circle=color, marker_color_outside=color)
                all_zone_points.extend(circle_points) # Add to auto-zoom calculation


        # Auto-zoom to show all zones
        if all_zone_points:
            print(f"DEBUG: All Zone Points: {len(all_zone_points)}")
            try:
                lats = [p[0] for p in all_zone_points]
                lons = [p[1] for p in all_zone_points]
                # Add padding
                lat_min, lat_max = min(lats), max(lats)
                lon_min, lon_max = min(lons), max(lons)
                # Ensure some spread even for single item
                if lat_min == lat_max: lat_min -= 0.05; lat_max += 0.05
                if lon_min == lon_max: lon_min -= 0.05; lon_max += 0.05
                
                print(f"DEBUG: Fitting Bounds: {lat_min}, {lon_min} to {lat_max}, {lon_max}")
                self.map_widget.fit_bounding_box((lat_max, lon_min), (lat_min, lon_max))
            except Exception as e:
                print(f"DEBUG: Zoom error: {e}")

    def get_centroid(self, points):
        x = [p[0] for p in points]
        y = [p[1] for p in points]
        return (sum(x) / len(points), sum(y) / len(points))

    def convex_hull(self, points):
        """Compute the convex hull of a set of 2D points using Monotone Chain algorithm."""
        points = sorted(set(points)) # Remove duplicates and sort
        if len(points) <= 1: return points

        def cross(o, a, b):
            return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

        lower = []
        for p in points:
            while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 0:
                lower.pop()
            lower.append(p)

        upper = []
        for p in reversed(points):
            while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= 0:
                upper.pop()
            upper.append(p)

        return lower[:-1] + upper[:-1]

    def manage_zones(self):
        """Open Zone Manager Dialog"""
        dialog = ZoneManagerDialog(self, self.cache)
        self.wait_window(dialog)
        self.load_deliveries() # Refresh after close

    # ... [Keep existing treeview_sort_column, parse_date_sort, get_visible_deliveries, 
    #      print_picking_list, print_run_sheet, plan_route, show_report_dialog methods] ...
    def treeview_sort_column(self, tv, col, reverse):
        l = [(tv.set(k, col), k) for k in tv.get_children('')]
        if col == 'Date': l.sort(key=lambda t: self.parse_date_sort(t[0]), reverse=reverse)
        elif col == 'Total':
             try: l.sort(key=lambda t: float(t[0].replace('£','').replace(',','')), reverse=reverse)
             except ValueError: l.sort(reverse=reverse)
        else: l.sort(reverse=reverse)
        for index, (val, k) in enumerate(l): tv.move(k, '', index)
        tv.heading(col, command=lambda: self.treeview_sort_column(tv, col, not reverse))

    def parse_date_sort(self, date_str):
        if not date_str or date_str == 'TBD': return datetime.min
        try: return datetime.strptime(date_str, '%d/%m/%Y')
        except: return datetime.min

    def get_visible_deliveries(self):
        deliveries = []
        for item in self.tree.get_children():
            vals = self.tree.item(item, 'values')
            tags = self.tree.item(item, 'tags')
            deliveries.append({
                'date': vals[0], 'area': vals[1], 'customer': vals[2],
                'items': vals[3], 'address_data': tags[0] if tags else "||"
            })
        return deliveries

    def print_picking_list(self):
        deliveries = self.get_visible_deliveries()
        if not deliveries: return messagebox.showinfo("Empty", "No deliveries.")
        totals = {}
        for d in deliveries:
            raw_items = d['items'].split(', ')
            for raw in raw_items:
                try:
                    parts = raw.split(' x ')
                    if len(parts) == 2:
                        qty, name = int(parts[0]), parts[1]
                        totals[name] = totals.get(name, 0) + qty
                except: pass
        report = f"PICKING LIST\n{'='*30}\nDate: {datetime.now():%d/%m/%Y}\nFilter: {self.filter_var.get()}\n{'='*30}\n\n"
        for name, qty in sorted(totals.items()): report += f"[ ] {qty} x {name}\n"
        self.show_report_dialog("Picking List", report)

    def print_run_sheet(self):
        deliveries = self.get_visible_deliveries()
        if not deliveries: return messagebox.showinfo("Empty", "No deliveries.")
        report = f"DELIVERY RUN SHEET\n{'='*40}\nDate: {datetime.now():%d/%m/%Y %H:%M}\n{'='*40}\n\n"
        for i, d in enumerate(deliveries, 1):
            name, postcode, address = d['address_data'].split('|')
            report += f"STOP {i}: {d['customer']}\nArea: {d['area']} | Date: {d['date']}\nAddress: {address.replace(chr(10), ', ')}\nItems: {d['items']}\n{'-'*40}\n"
        self.show_report_dialog("Run Sheet", report)

    def plan_route(self):
        deliveries = self.get_visible_deliveries()
        if not deliveries: return
        if len(deliveries) > 10:
             if not messagebox.askyesno("Limit Warning", "Google Maps URL works best with < 10 stops. Continue with first 10?"): return
             deliveries = deliveries[:10]
        params = {'origin': "My Brewery", 'destination': deliveries[-1]['address_data'].split('|')[1] or deliveries[-1]['address_data'].split('|')[2], 'travelmode': 'driving'}
        waypoints = [d['address_data'].split('|')[1] or d['address_data'].split('|')[2] for d in deliveries[:-1]]
        if waypoints: params['waypoints'] = '|'.join(waypoints)
        webbrowser.open(f"https://www.google.com/maps/dir/?api=1&{urllib.parse.urlencode(params)}")

    def show_report_dialog(self, title, text):
        top = tk.Toplevel(self)
        top.title(title)
        top.geometry("400x600")
        txt = tk.Text(top, wrap=tk.WORD, font=('Consolas', 10))
        txt.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        txt.insert('1.0', text)
        txt.config(state='disabled')
        ttk.Button(top, text="Print / Close", command=top.destroy).pack(pady=10)


class ZoneManagerDialog(tk.Toplevel):
    """Dialog to manage Delivery Zones"""
    
    def __init__(self, parent, cache_manager):
        super().__init__(parent)
        self.title("Manage Delivery Zones")
        self.geometry("900x600") # Resized for visibility
        self.cache = cache_manager
        self.parent = parent # To access parent methods if needed (e.g. nominator)
        
        self.transient(parent) # Restored to keep window on top without stealing canvas events
        # self.grab_set() # Removed to allow map clicks to register
        self.focus_force()
        
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        self.create_widgets()
        self.load_zones()
        self.new_zone() # Start in "New" mode
        
    def on_closing(self):
        # Clear map editing state by re-drawing normal zones
        if hasattr(self.parent, 'map_widget') and self.parent.map_widget:
            self.parent.map_widget.map_click_callback = None
            self.parent.map_widget.canvas.unbind("<Double-Button-1>")
            
        if hasattr(self.parent, 'load_deliveries'):
            self.parent.load_deliveries()
            
        self.destroy()
        
    def create_widgets(self):
        # Main Layout: Paned Window (List | Form)
        paned = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left: List of Zones
        left_frame = ttk.LabelFrame(paned, text="Existing Zones", padding=10)
        paned.add(left_frame, weight=1)
        
        self.zone_list = tk.Listbox(left_frame, font=('Arial', 10))
        self.zone_list.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        self.zone_list.bind('<<ListboxSelect>>', self.on_select)
        
        ttk.Label(left_frame, text="Select a zone to edit.", font=('Arial', 9, 'italic')).pack(side=tk.BOTTOM, anchor='w')
        
        # Right: Edit Form
        right_frame = ttk.LabelFrame(paned, text="Zone Details", padding=10)
        paned.add(right_frame, weight=2)
        
        # Form Fields
        ttk.Label(right_frame, text="Zone Name:", font=('Arial', 10, 'bold')).pack(anchor='w')
        self.name_entry = ttk.Entry(right_frame)
        self.name_entry.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(right_frame, text="Postcodes (e.g., M1, M2):", font=('Arial', 10, 'bold')).pack(anchor='w')
        ttk.Label(right_frame, text="Enter the start of the postcode (prefix).", font=('Arial', 8)).pack(anchor='w')
        self.prefixes_entry = ttk.Entry(right_frame)
        self.prefixes_entry.pack(fill=tk.X, pady=(0, 5))
        
        # Verify Button
        ttk.Button(right_frame, text="🔍 Verify Postcodes on Map", 
                  bootstyle="info-outline", 
                  command=self.verify_postcodes).pack(fill=tk.X, pady=(0, 15))
        
        # Color Picker
        ttk.Label(right_frame, text="Zone Color:", font=('Arial', 10, 'bold')).pack(anchor='w')
        color_frame = ttk.Frame(right_frame)
        color_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.color_label = tk.Label(color_frame, text="     ", bg="blue", relief="sunken", width=10)
        self.color_label.pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(color_frame, text="Change Color", command=self.pick_color).pack(side=tk.LEFT)
        
        # Separate Frame for Shape Editing Buttons (Above Main Actions)
        self.shape_btn_frame = ttk.Frame(right_frame)
        self.shape_btn_frame.pack(fill=tk.X, pady=(10, 0)) # Spacing
        
        # Edit / Reset Shape Buttons (Visible only when editing)
        self.edit_shape_btn = ttk.Button(self.shape_btn_frame, text="✏️ Edit Boundary", bootstyle="warning-outline", command=self.toggle_edit_mode)
        self.reset_shape_btn = ttk.Button(self.shape_btn_frame, text="🔄 Reset Boundary", bootstyle="danger-outline", command=self.reset_shape)
        
        # Buttons Area (Main Actions)
        btn_frame = ttk.Frame(right_frame)
        btn_frame.pack(fill=tk.X, side=tk.BOTTOM, pady=10)
        
        # Dynamic Main Action Button
        self.save_btn = ttk.Button(btn_frame, text="✅ Needs Logic", bootstyle="success", command=self.save_zone)
        self.save_btn.pack(side=tk.RIGHT, padx=5)
        
        # Clear / New Button
        ttk.Button(btn_frame, text="✨ Clear / New", bootstyle="secondary", command=self.new_zone).pack(side=tk.RIGHT, padx=5)
        
        # Delete Button (Visible only when editing)
        self.delete_btn = ttk.Button(btn_frame, text="🗑️ Delete", bootstyle="danger", command=self.delete_zone)
        
        self.selected_zone_id = None
        self.current_color = "blue"
        
    def load_zones(self):
        self.zone_list.delete(0, tk.END)
        self.cache.connect()
        self.zones = self.cache.get_all_records('delivery_zones')
        self.cache.close()
        
        for z in self.zones:
            self.zone_list.insert(tk.END, f"{z['zone_name']}")
            
        
    def new_zone(self):
        # Reset State -> Add Mode
        self.selected_zone_id = None
        self.name_entry.delete(0, tk.END)
        self.prefixes_entry.delete(0, tk.END)
        self.current_color = 'blue'
        self.color_label.config(bg='blue')
        
        if hasattr(self, 'current_polygon_coords'):
            del self.current_polygon_coords
        
        self.zone_list.selection_clear(0, tk.END)
        
        # Update UI State
        self.save_btn.config(text="➕ Add New Zone", bootstyle="success")
        self.delete_btn.pack_forget()
        
        # Hide shape buttons
        self.edit_shape_btn.pack_forget()
        self.reset_shape_btn.pack_forget()
        
        # Clear map editing state by re-drawing normal zones
        if hasattr(self.parent, 'map_widget') and self.parent.map_widget:
            # tkintermapview doesn't have an unbind method, but it stores the callback here
            self.parent.map_widget.map_click_callback = None
            self.parent.map_widget.canvas.unbind("<Double-Button-1>")
        
        if hasattr(self.parent, 'load_deliveries'):
            self.parent.load_deliveries()
        
    def pick_color(self):
        color = colorchooser.askcolor(color=self.current_color, parent=self)[1]
        if color:
            self.current_color = color
            self.color_label.config(bg=color)
            
    def verify_postcodes(self):
        """Check if postcodes are valid in pgeocode"""
        input_text = self.prefixes_entry.get().strip()
        if not input_text:
            messagebox.showinfo("Verify", "Enter some postcodes first.")
            return

        prefixes = [p.strip().upper() for p in input_text.replace(';',',').split(',')]
        
        if not hasattr(self.parent, 'nomi') or not self.parent.nomi:
             messagebox.showerror("Error", "Geocoding library (pgeocode) not loaded.")
             return

        nomi = self.parent.nomi
        valid = []
        invalid = []
        
        for p in prefixes:
            if not p: continue
            try:
                # Query outward code
                query = p.split(' ')[0]
                loc = nomi.query_postal_code(query)
                if not math.isnan(loc.latitude):
                    valid.append(f"{p} -> {loc.place_name}")
                else:
                    invalid.append(p)
            except:
                invalid.append(p)
                
        msg = f"Found {len(valid)} valid areas.\n"
        if valid: msg += "\n".join(valid[:5]) + ("..." if len(valid)>5 else "")
        if invalid: 
            msg += f"\n\n❌ Invalid/Not Found: {', '.join(invalid)}"
            msg += "\nTry standard outward codes like 'M1' or 'GL51'."
            
        messagebox.showinfo("Verification Result", msg, parent=self)

    def save_zone(self):
        name = self.name_entry.get().strip()
        if not name: 
            messagebox.showerror("Error", "Zone Name required", parent=self)
            return
        
        prefixes = self.prefixes_entry.get().strip().upper()
        
        import uuid
        data = {
            'zone_name': name,
            'postcode_prefixes': prefixes,
            'color': self.current_color,
            'sync_status': 'pending'
        }
        
        self.cache.connect()
        try:
            if self.selected_zone_id:
                self.cache.update_record('delivery_zones', self.selected_zone_id, data, 'zone_id')
                messagebox.showinfo("Success", "Zone Updated", parent=self)
            else:
                data['zone_id'] = str(uuid.uuid4())
                self.cache.insert_record('delivery_zones', data)
            
            # Save Polygon Coords (if any)
            if hasattr(self, 'current_polygon_coords') and self.current_polygon_coords:
                import json
                coords_json = json.dumps(self.current_polygon_coords)
                # Check if we can just update it
                id_to_update = self.selected_zone_id if self.selected_zone_id else data['zone_id']
                
                # Re-connect (cache might have closed)
                self.cache.connect() 
                try:
                    self.cache.cursor.execute("UPDATE delivery_zones SET polygon_coords=? WHERE zone_id=?", (coords_json, id_to_update))
                    self.cache.connection.commit()
                except Exception as e:
                    print(f"Error saving polygon coords: {e}")
                
            self.load_zones()
            self.new_zone()
            
            # Request parent map to refresh all zones to clear edit state
            if hasattr(self.parent, 'load_deliveries'):
                 self.parent.load_deliveries()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save: {e}", parent=self)
        finally:
            self.cache.close()

    def delete_zone(self):
        if not self.selected_zone_id: return
        if not messagebox.askyesno("Confirm", "Delete this zone?", parent=self): return
        
        self.cache.connect()
        try:
            self.cache.delete_record('delivery_zones', self.selected_zone_id, 'zone_id')
            self.load_zones()
            self.new_zone()
            if hasattr(self.parent, 'load_deliveries'):
                 self.parent.load_deliveries()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete: {e}", parent=self)
        finally:
            self.cache.close()
            
    # --- Interactive Map Editing ---
    # --- Interactive Map Editing ---
    def on_select(self, event):
        sel = self.zone_list.curselection()
        if not sel: return
        
        zone = self.zones[sel[0]]
        self.selected_zone_id = zone['zone_id']
        
        # Populate Form
        self.name_entry.delete(0, tk.END)
        self.name_entry.insert(0, zone['zone_name'])
        
        self.prefixes_entry.delete(0, tk.END)
        self.prefixes_entry.insert(0, zone.get('postcode_prefixes', ''))
        
        self.current_color = zone.get('color', 'blue')
        self.color_label.config(bg=self.current_color)
        
        # Update UI State -> Edit Mode
        self.save_btn.config(text="💾 Update Zone", bootstyle="primary")
        self.delete_btn.pack(side=tk.LEFT, padx=5)
        
        # Load Polygon Coords
        import json
        self.current_polygon_coords = []
        raw_coords = zone.get('polygon_coords')
        if raw_coords:
            try: self.current_polygon_coords = json.loads(raw_coords)
            except: pass
            
        # Add "Edit Shape" Button
        self.edit_shape_btn.pack(side=tk.LEFT, padx=5)
        self.reset_shape_btn.pack(side=tk.LEFT, padx=5)

    def toggle_edit_mode(self):
        """Enable interactive map editing"""
        if not hasattr(self.parent, 'map_widget') or not self.parent.map_widget:
            messagebox.showerror("Error", "Map not loaded.")
            return

        map_widget = self.parent.map_widget
        
        # 1. Clear existing map items to focus on this zone
        map_widget.delete_all_polygon()
        
        # 2. Draw current zone (or auto-generated if none)
        points = getattr(self, 'current_polygon_coords', [])
        if not points:
             # Generate default from prefixes
             points = self._generate_default_points()
             if points:
                 self.current_polygon_coords = points
             else:
                 self.current_polygon_coords = [] # Initialize empty list for manual drawing
        
        # Initialize editing state
        self.selected_vertex_index = None
        self.edit_markers = []
        
        # 3. Draw Editing Polygon & Markers
        self.redraw_editing_shape()
        
        msg = "EDIT MODE ACTIVE:\n• RIGHT-CLICK on Map: Add new point\n• LEFT-CLICK A POINT to Select -> Click Map to Move\n• DOUBLE-CLICK: Zoom In"
        
        # Only show the "No valid postcodes found" if we really have no points and prefixes were entered
        prefixes = self.prefixes_entry.get().strip()
        if not self.current_polygon_coords and prefixes:
            msg += "\n\n(No valid coordinates found for entered postcodes. Start drawing manually!)"
        elif not self.current_polygon_coords:
            msg += "\n\n(Start drawing manually by clicking on the map!)"

        messagebox.showinfo("Edit Mode", msg, parent=self)
                            
        # Enable Left-Click to select/move points
        map_widget.add_left_click_map_command(self.on_map_left_click)
        
        # Enable Right-Click to add new points natively on the canvas
        map_widget.canvas.bind("<Button-3>", self.on_map_right_click)
        
        # Cancel the left-click timer on double-click so they don't fight
        map_widget.canvas.bind("<Double-Button-1>", self.on_double_click_zoom, add="+")

    def redraw_editing_shape(self):
        """Redraw polygon and drag handles"""
        map_widget = self.parent.map_widget
        map_widget.delete_all_polygon()
        
        # Clear old markers
        if hasattr(self, 'edit_markers'):
             for m in self.edit_markers: m.delete()
        self.edit_markers = []
        
        points = getattr(self, 'current_polygon_coords', [])
        if not points: return

        # Draw Polygon if enough points
        if len(points) >= 3:
            map_widget.set_polygon(points, fill_color=self.current_color, border_width=2, name="editing_zone")
        
        # Draw Vertex Handles
        for i, p in enumerate(points):
            color_outside = "#FF0000" # Red default
            if getattr(self, 'selected_vertex_index', None) == i:
                color_outside = "#00FF00" # Green when selected
            
            m = map_widget.set_marker(p[0], p[1], text=str(i+1),
                                      marker_color_circle="white",
                                      marker_color_outside=color_outside,
                                      text_color="black",
                                      command=self.on_vertex_click)
            m.vertex_index = i # Attach index to marker
            self.edit_markers.append(m)

    def on_vertex_click(self, marker):
        """No-op. Handled by map pixel distance."""
        pass

    def on_map_left_click(self, coords):
        """Handle map click, debounced to allow for double-click zooms"""
        # Cancel any pending click
        if hasattr(self, '_click_timer') and self._click_timer:
            self.after_cancel(self._click_timer)
            
        self._pending_click_coords = coords
        self._click_timer = self.after(250, self._perform_map_click_action)
        
    def _perform_map_click_action(self):
        """Actual logic for a single left click on map after double-click timeout"""
        self._click_timer = None
        if not hasattr(self, 'current_polygon_coords'): return
        
        coords = self._pending_click_coords
        click_lat, click_lon = coords
        
        clicked_vertex_idx = None
        min_dist = float('inf')
        
        # We use a very simple distance approximation since we only care about "is it close?"
        # 1 degree of latitude is ~111km. 
        # A threshold of 0.005 is roughly 500 meters, which is a massive click radius at street level
        # but very small if zoomed all the way out. We scale the hit-box by zoom level!
        
        # Scale tolerance based on zoom: at zoom 15, we want ~0.0015 tolerance.
        map_widget = self.parent.map_widget
        zoom = map_widget.zoom
        
        # Exponentially increase tolerance as we zoom out
        # Zoom 15 -> ~0.0015, Zoom 14 -> ~0.003...
        tolerance = 0.0015 * (2 ** (15 - zoom))
        
        for i, p in enumerate(self.current_polygon_coords):
            # Simplistic distance ignoring spherical earth since we only care about screen-relative clicks
            d_lat = p[0] - click_lat
            # Approximate longitude scaling at this latitude
            import math
            d_lon = (p[1] - click_lon) * math.cos(click_lat * math.pi / 180)
            
            dist = (d_lat**2 + d_lon**2)**0.5
            
            if dist < tolerance and dist < min_dist:
                min_dist = dist
                clicked_vertex_idx = i
                
        if clicked_vertex_idx is not None:
             # Clicked a vertex
             if getattr(self, 'selected_vertex_index', None) == clicked_vertex_idx:
                 self.selected_vertex_index = None # Deselect
             else:
                 self.selected_vertex_index = clicked_vertex_idx # Select
             self.redraw_editing_shape()
             return
             
        # Did not click a vertex. If one is selected, move it
        if getattr(self, 'selected_vertex_index', None) is not None:
             if self.selected_vertex_index < len(self.current_polygon_coords):
                 self.current_polygon_coords[self.selected_vertex_index] = coords
                 self.selected_vertex_index = None # Deselect after move
             self.redraw_editing_shape()
        else:
             # Just deselect if clicking empty space
             self.selected_vertex_index = None
             self.redraw_editing_shape()
             
    def on_map_right_click(self, event):
        """Right click anywhere immediately adds a point"""
        if not hasattr(self, 'current_polygon_coords'): return
        coords = self.parent.map_widget.convert_canvas_coords_to_decimal_coords(event.x, event.y)
        self.current_polygon_coords.append(coords)
        self.redraw_editing_shape()
             
    def on_double_click_zoom(self, event):
        """Override zoom logic just to cancel left click timer if needed and zoom"""
        if hasattr(self, '_click_timer') and self._click_timer:
            self.after_cancel(self._click_timer)
            self._click_timer = None
            
        map_widget = self.parent.map_widget
        current_zoom = map_widget.zoom
        map_widget.set_zoom(current_zoom + 1)
             
    def _generate_default_points(self):
        """Helper to get points from current prefixes entry"""
        prefixes = [p.strip().upper() for p in self.prefixes_entry.get().replace(';',',').split(',')]
        points = []
        
        if not hasattr(self.parent, 'nomi') or not self.parent.nomi:
            print("DEBUG: Geocoder (nomi) not initialized in parent!")
            return []
            
        print(f"DEBUG: Generating points for prefixes: {prefixes}")
        for p in prefixes:
            if not p: continue
            try:
                loc = self.parent.nomi.query_postal_code(p.split(' ')[0])
                if not math.isnan(loc.latitude): 
                    points.append((loc.latitude, loc.longitude))
                    print(f"DEBUG: Found {p} -> {loc.latitude}, {loc.longitude}")
                else:
                    print(f"DEBUG: Invalid coord for {p}")
            except Exception as e:
                print(f"DEBUG: Geocode error for {p}: {e}")
        
        if len(points) >= 3:
             return self.parent.convex_hull(points)
        elif len(points) >= 1:
             # If 1 or 2 points, we can't make a hull, but we can return them
             # For 1 point, maybe make a circle
             if len(points) == 1:
                 center = points[0]
                 circle = []
                 radius = 0.03
                 for i in range(12):
                     angle = math.radians(float(i)*30)
                     circle.append((center[0] + radius*math.cos(angle), center[1] + radius*math.sin(angle)))
                 return circle
             return points # Return 2 points as is (line)
        return []


    def reset_shape(self):
        """Clear custom coords"""
        if messagebox.askyesno("Reset", "Revert to auto-generated shape?", parent=self):
            self.current_polygon_coords = []
            self.toggle_edit_mode() # Redraw default
        
        self.load_zones()
        self.new_zone() # Reset to new
        if hasattr(self.parent, 'load_deliveries'):
            self.parent.load_deliveries()

