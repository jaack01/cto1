"""
Order Management System - Main Application
"""
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import webbrowser
import json

from database import Database
from validation import (
    validate_order_form, validate_email, validate_required,
    show_error, show_success, show_info, confirm_action
)
from notifications import NotificationManager, NotificationConfig
from dashboard import DashboardFrame
from reporting import ReportingFrame
from laundry_crm.gui.customer_management import CustomerManagementFrame


class OrderManagementApp:
    """Main application window for Order Management System."""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Order Management System")
        self.root.geometry("1200x800")
        
        self.db = Database()
        self.notification_manager = NotificationManager()
        
        self.setup_theme()
        self.create_menu()
        self.create_main_layout()
        self.load_orders()
        
    def setup_theme(self):
        """Setup application theme and styling."""
        style = ttk.Style()
        
        available_themes = style.theme_names()
        if 'clam' in available_themes:
            style.theme_use('clam')
        elif 'alt' in available_themes:
            style.theme_use('alt')
        
        style.configure('Header.TLabel', font=('Arial', 14, 'bold'))
        style.configure('Title.TLabel', font=('Arial', 16, 'bold'))
        style.configure('Status.Pending.TLabel', foreground='orange')
        style.configure('Status.Ready.TLabel', foreground='green')
        style.configure('Status.Completed.TLabel', foreground='blue')
        
        style.configure('Treeview', rowheight=25)
        style.configure('Treeview.Heading', font=('Arial', 10, 'bold'))
    
    def create_menu(self):
        """Create application menu bar."""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New Order", command=self.show_new_order_dialog)
        file_menu.add_command(label="Refresh", command=self.load_orders)
        file_menu.add_separator()
        file_menu.add_command(label="Settings", command=self.show_settings_dialog)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="All Orders", command=lambda: self.filter_orders(None))
        view_menu.add_command(label="Pending Orders", command=lambda: self.filter_orders('pending'))
        view_menu.add_command(label="Ready Orders", command=lambda: self.filter_orders('ready'))
        view_menu.add_command(label="Completed Orders", command=lambda: self.filter_orders('completed'))
        
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="Help", command=self.show_help_dialog)
        help_menu.add_separator()
        help_menu.add_command(label="About", command=self.show_about_dialog)
    
    def create_main_layout(self):
        """Create main application layout."""
        main_container = ttk.Frame(self.root, padding="10")
        main_container.pack(fill=tk.BOTH, expand=True)

        notebook = ttk.Notebook(main_container)
        notebook.pack(fill=tk.BOTH, expand=True)

        # Dashboard Tab
        dashboard_tab = DashboardFrame(notebook, self.db)
        notebook.add(dashboard_tab, text="Dashboard")

        # Orders Tab
        orders_tab = self.create_orders_tab(notebook)
        notebook.add(orders_tab, text="Orders")

        # Customers Tab
        customer_tab = CustomerManagementFrame(notebook, self.db, self)
        notebook.add(customer_tab, text="Customers")

        # Reporting Tab
        reporting_tab = ReportingFrame(notebook, self.db)
        notebook.add(reporting_tab, text="Reporting")

    def create_orders_tab(self, parent):
        """Create the orders tab content."""
        orders_container = ttk.Frame(parent, padding="10")
        
        title_frame = ttk.Frame(orders_container)
        title_frame.pack(fill=tk.X, pady=(0, 10))
        
        title_label = ttk.Label(title_frame, text="Order Management", 
                               style='Title.TLabel')
        title_label.pack(side=tk.LEFT)
        
        self.stats_label = ttk.Label(title_frame, text="")
        self.stats_label.pack(side=tk.RIGHT)
        
        toolbar_frame = ttk.Frame(orders_container)
        toolbar_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(toolbar_frame, text="New Order", 
                  command=self.show_new_order_dialog).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar_frame, text="Edit Order", 
                  command=self.edit_selected_order).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar_frame, text="Mark Ready", 
                  command=self.mark_order_ready).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar_frame, text="Mark Completed", 
                  command=self.mark_order_completed).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar_frame, text="Delete Order",
                  command=self.delete_selected_order).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar_frame, text="Manage Payments",
                   command=self.show_payment_dialog).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar_frame, text="Refresh",
                  command=self.load_orders).pack(side=tk.LEFT, padx=2)

        ttk.Label(toolbar_frame, text="Filter:").pack(side=tk.LEFT, padx=(20, 5))
        self.filter_var = tk.StringVar(value="all")
        filter_combo = ttk.Combobox(toolbar_frame, textvariable=self.filter_var,
                                    state='readonly', width=15)
        filter_combo['values'] = ('all', 'pending', 'scheduled', 'in_progress', 'ready', 'completed', 'cancelled')
        filter_combo.pack(side=tk.LEFT, padx=2)
        filter_combo.bind('<<ComboboxSelected>>', lambda e: self.filter_orders(
            None if self.filter_var.get() == 'all' else self.filter_var.get()))
        
        ttk.Label(toolbar_frame, text="Date field:").pack(side=tk.LEFT, padx=(20, 5))
        self.date_field_var = tk.StringVar(value='created_at')
        date_field_combo = ttk.Combobox(toolbar_frame, textvariable=self.date_field_var,
                                        state='readonly', width=18)
        date_field_combo['values'] = ('created_at', 'scheduled_pickup', 'scheduled_delivery')
        date_field_combo.pack(side=tk.LEFT, padx=2)
        
        ttk.Label(toolbar_frame, text="From:").pack(side=tk.LEFT, padx=(10, 5))
        self.from_date_entry = ttk.Entry(toolbar_frame, width=12)
        self.from_date_entry.pack(side=tk.LEFT)
        
        ttk.Label(toolbar_frame, text="To:").pack(side=tk.LEFT, padx=(10, 5))
        self.to_date_entry = ttk.Entry(toolbar_frame, width=12)
        self.to_date_entry.pack(side=tk.LEFT)
        
        ttk.Button(toolbar_frame, text="Apply Filters", command=lambda: self.filter_orders(
            None if self.filter_var.get() == 'all' else self.filter_var.get()
        )).pack(side=tk.LEFT, padx=5)
        
        tree_frame = ttk.Frame(orders_container)
        tree_frame.pack(fill=tk.BOTH, expand=True)

        tree_scroll_y = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL)
        tree_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)

        tree_scroll_x = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL)
        tree_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        
        columns = ('ID', 'Customer', 'Email', 'Phone', 'Service', 'Item', 'Qty', 'Price', 'Total', 'Status', 'Pickup', 'Delivery', 'Created')
        self.tree = ttk.Treeview(tree_frame, columns=columns, show='headings',
                                yscrollcommand=tree_scroll_y.set,
                                xscrollcommand=tree_scroll_x.set)

        tree_scroll_y.config(command=self.tree.yview)
        tree_scroll_x.config(command=self.tree.xview)

        self.tree.heading('ID', text='ID')
        self.tree.heading('Customer', text='Customer Name')
        self.tree.heading('Email', text='Email')
        self.tree.heading('Phone', text='Phone')
        self.tree.heading('Service', text='Service')
        self.tree.heading('Item', text='Items')
        self.tree.heading('Qty', text='Qty')
        self.tree.heading('Price', text='Price')
        self.tree.heading('Total', text='Total')
        self.tree.heading('Status', text='Status')
        self.tree.heading('Pickup', text='Pickup')
        self.tree.heading('Delivery', text='Delivery')
        self.tree.heading('Created', text='Created At')

        self.tree.column('ID', width=50, anchor=tk.CENTER)
        self.tree.column('Customer', width=120)
        self.tree.column('Email', width=150)
        self.tree.column('Phone', width=100)
        self.tree.column('Service', width=120)
        self.tree.column('Item', width=180)
        self.tree.column('Qty', width=50, anchor=tk.CENTER)
        self.tree.column('Price', width=70, anchor=tk.E)
        self.tree.column('Total', width=80, anchor=tk.E)
        self.tree.column('Status', width=100, anchor=tk.CENTER)
        self.tree.column('Pickup', width=130)
        self.tree.column('Delivery', width=130)
        self.tree.column('Created', width=130)

        self.tree.pack(fill=tk.BOTH, expand=True)
        
        self.tree.bind('<Double-1>', lambda e: self.edit_selected_order())
        
        status_bar = ttk.Frame(orders_container)
        status_bar.pack(fill=tk.X, pady=(10, 0))
        self.status_label = ttk.Label(status_bar, text="Ready")
        self.status_label.pack(side=tk.LEFT)

        return orders_container
    
    def load_orders(self):
        """Load orders from database and display in tree view."""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        orders = self.db.get_all_orders()
        service_map = {s['id']: s['name'] for s in self.db.get_service_types()}
        
        for order in orders:
            created_at = datetime.fromisoformat(order['created_at']).strftime('%Y-%m-%d %H:%M') if order.get('created_at') else ''
            pickup = order.get('scheduled_pickup')
            pickup_fmt = datetime.fromisoformat(pickup).strftime('%Y-%m-%d %H:%M') if pickup else ''
            delivery = order.get('scheduled_delivery')
            delivery_fmt = datetime.fromisoformat(delivery).strftime('%Y-%m-%d %H:%M') if delivery else ''
            service_name = service_map.get(order.get('service_type')) or ''
            
            values = (
                order['id'],
                order['customer_name'],
                order['customer_email'],
                order['customer_phone'] or '',
                service_name,
                order['item_description'],
                order['quantity'],
                f"${order['price']:.2f}",
                f"${order['total_price']:.2f}",
                order['status'].upper(),
                pickup_fmt,
                delivery_fmt,
                created_at
            )
            
            self.tree.insert('', tk.END, values=values, tags=(order['status'],))
        
        self.tree.tag_configure('pending', foreground='orange')
        self.tree.tag_configure('ready', foreground='green')
        self.tree.tag_configure('completed', foreground='blue')
        
        self.update_statistics()
        self.status_label.config(text=f"Loaded {len(orders)} orders")
    
    def filter_orders(self, status):
        """Filter orders by status and optional date range."""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Read optional date filters
        date_from = getattr(self, 'from_date_entry', None)
        date_to = getattr(self, 'to_date_entry', None)
        df = date_from.get().strip() if date_from and date_from.get().strip() else None
        dt = date_to.get().strip() if date_to and date_to.get().strip() else None
        date_field = getattr(self, 'date_field_var', None)
        dfield = date_field.get() if date_field else 'created_at'
        
        orders = self.db.get_all_orders(status, df, dt, dfield)
        service_map = {s['id']: s['name'] for s in self.db.get_service_types()}
        
        for order in orders:
            created_at = datetime.fromisoformat(order['created_at']).strftime('%Y-%m-%d %H:%M') if order.get('created_at') else ''
            pickup = order.get('scheduled_pickup')
            pickup_fmt = datetime.fromisoformat(pickup).strftime('%Y-%m-%d %H:%M') if pickup else ''
            delivery = order.get('scheduled_delivery')
            delivery_fmt = datetime.fromisoformat(delivery).strftime('%Y-%m-%d %H:%M') if delivery else ''
            service_name = service_map.get(order.get('service_type')) or ''
            
            values = (
                order['id'],
                order['customer_name'],
                order['customer_email'],
                order['customer_phone'] or '',
                service_name,
                order['item_description'],
                order['quantity'],
                f"${order['price']:.2f}",
                f"${order['total_price']:.2f}",
                order['status'].upper(),
                pickup_fmt,
                delivery_fmt,
                created_at
                )

                self.tree.insert('', tk.END, values=values, tags=(order['status'],))
        
        self.status_label.config(text=f"Showing {len(orders)} orders")
    
    def update_statistics(self):
        """Update statistics display."""
        stats = self.db.get_statistics()
        stats_text = (f"Total: {stats['total_orders']} | "
                     f"Pending: {stats['pending_orders']} | "
                     f"Ready: {stats['ready_orders']} | "
                     f"Completed: {stats['completed_orders']} | "
                     f"Revenue: ${stats['total_revenue']:.2f}")
        self.stats_label.config(text=stats_text)
    
    def show_new_order_dialog(self, customer=None):
        """Show dialog to create new order with service type, items, and scheduling."""
        dialog = tk.Toplevel(self.root)
        dialog.title("New Order")
        dialog.geometry("800x650")
        dialog.transient(self.root)
        dialog.grab_set()
        
        frame = ttk.Frame(dialog, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="Create New Order", style='Header.TLabel').grid(
            row=0, column=0, columnspan=4, pady=(0, 20), sticky=tk.W)
        
        # Load reference data
        service_types = self.db.get_service_types()
        garment_types = self.db.get_garment_types()
        service_name_to_id = {s['name']: s['id'] for s in service_types}
        service_id_to_name = {s['id']: s['name'] for s in service_types}
        garment_name_to_id = {g['name']: g['id'] for g in garment_types}
        garment_id_to_name = {g['id']: g['name'] for g in garment_types}
        garment_multiplier = {g['id']: g['multiplier'] for g in garment_types}
        service_rate = {s['id']: s['rate'] for s in service_types}
        
        # Customer fields
        ttk.Label(frame, text="Customer Name:").grid(row=1, column=0, sticky=tk.W, pady=5)
        name_entry = ttk.Entry(frame, width=30)
        name_entry.grid(row=1, column=1, pady=5, sticky=tk.W)
        if customer:
            name_entry.insert(0, customer.get('name', ''))
        
        ttk.Label(frame, text="Customer Email:").grid(row=1, column=2, sticky=tk.W, pady=5)
        email_entry = ttk.Entry(frame, width=30)
        email_entry.grid(row=1, column=3, pady=5, sticky=tk.W)
        if customer:
            email_entry.insert(0, customer.get('email', ''))
        
        ttk.Label(frame, text="Customer Phone:").grid(row=2, column=0, sticky=tk.W, pady=5)
        phone_entry = ttk.Entry(frame, width=30)
        phone_entry.grid(row=2, column=1, pady=5, sticky=tk.W)
        if customer:
            phone_entry.insert(0, customer.get('phone', ''))
        
        ttk.Label(frame, text="Address:").grid(row=2, column=2, sticky=tk.W, pady=5)
        address_entry = ttk.Entry(frame, width=30)
        address_entry.grid(row=2, column=3, pady=5, sticky=tk.W)
        if customer:
            address_entry.insert(0, customer.get('address', ''))
        
        # Service selection
        ttk.Label(frame, text="Service Type:").grid(row=3, column=0, sticky=tk.W, pady=5)
        service_var = tk.StringVar()
        service_combo = ttk.Combobox(frame, textvariable=service_var, state='readonly', width=28)
        service_combo['values'] = [s['name'] for s in service_types]
        if service_types:
            service_combo.set(service_types[0]['name'])
        service_combo.grid(row=3, column=1, pady=5, sticky=tk.W)
        
        # Items section
        ttk.Label(frame, text="Items:").grid(row=4, column=0, sticky=tk.W, pady=(10, 5))
        items_frame = ttk.Frame(frame)
        items_frame.grid(row=5, column=0, columnspan=4, sticky='ew')
        items_frame.grid_columnconfigure(0, weight=1)
        items_frame.grid_columnconfigure(1, weight=1)
        items_frame.grid_columnconfigure(2, weight=1)
        items_frame.grid_columnconfigure(3, weight=0)
        
        header = ttk.Frame(items_frame)
        header.grid(row=0, column=0, columnspan=4, sticky='ew')
        ttk.Label(header, text='Garment Type', width=25).grid(row=0, column=0, padx=5)
        ttk.Label(header, text='Quantity', width=10).grid(row=0, column=1, padx=5)
        ttk.Label(header, text='Instructions', width=40).grid(row=0, column=2, padx=5)
        
        item_rows = []
        
        def recalc_total(*args):
            svc_name = service_var.get()
            svc_id = service_name_to_id.get(svc_name)
            total = 0.0
            if not svc_id:
                total = 0.0
            else:
                rate = float(service_rate.get(svc_id, 0.0))
                for row in item_rows:
                    if not row.get('active', True):
                        continue
                    gname = row['garment_var'].get()
                    gid = garment_name_to_id.get(gname)
                    try:
                        qty = int(row['qty_var'].get() or '0')
                    except Exception:
                        qty = 0
                    mult = float(garment_multiplier.get(gid, 1.0))
                    total += qty * rate * mult
            total_var.set(f"${total:.2f}")
            return total
        
        def add_item_row(default_garment=None, default_qty='1', default_instr=''):
            rindex = len(item_rows) + 1
            row_frame = ttk.Frame(items_frame)
            row_frame.grid(row=rindex, column=0, columnspan=4, sticky='ew', pady=2)
            
            garment_var = tk.StringVar(value=default_garment or (garment_types[0]['name'] if garment_types else ''))
            garment_combo = ttk.Combobox(row_frame, textvariable=garment_var, state='readonly', width=25)
            garment_combo['values'] = [g['name'] for g in garment_types]
            garment_combo.grid(row=0, column=0, padx=5)
            garment_combo.bind('<<ComboboxSelected>>', recalc_total)
            
            qty_var = tk.StringVar(value=str(default_qty))
            qty_entry = ttk.Entry(row_frame, textvariable=qty_var, width=8)
            qty_entry.grid(row=0, column=1, padx=5)
            qty_entry.bind('<KeyRelease>', recalc_total)
            
            instr_entry = ttk.Entry(row_frame, width=50)
            instr_entry.insert(0, default_instr)
            instr_entry.grid(row=0, column=2, padx=5)
            
            def remove_row():
                row_frame.grid_forget()
                row['active'] = False
                recalc_total()
            remove_btn = ttk.Button(row_frame, text='Remove', command=remove_row)
            remove_btn.grid(row=0, column=3, padx=5)
            
            row = {
                'frame': row_frame,
                'garment_var': garment_var,
                'qty_var': qty_var,
                'instr_entry': instr_entry,
                'active': True
            }
            item_rows.append(row)
            recalc_total()
        
        add_item_row()
        
        add_item_btn = ttk.Button(frame, text="Add Item", command=lambda: add_item_row())
        add_item_btn.grid(row=4, column=1, sticky=tk.W, pady=(10, 5))
        
        # Scheduling fields
        ttk.Label(frame, text="Scheduled Pickup (YYYY-MM-DD HH:MM):").grid(row=6, column=0, sticky=tk.W, pady=10)
        pickup_entry = ttk.Entry(frame, width=25)
        pickup_entry.grid(row=6, column=1, sticky=tk.W, pady=10)
        
        ttk.Label(frame, text="Scheduled Delivery (YYYY-MM-DD HH:MM):").grid(row=6, column=2, sticky=tk.W, pady=10)
        delivery_entry = ttk.Entry(frame, width=25)
        delivery_entry.grid(row=6, column=3, sticky=tk.W, pady=10)
        
        # Total display
        total_var = tk.StringVar(value="$0.00")
        ttk.Label(frame, text="Total:", font=('Arial', 12, 'bold')).grid(row=7, column=2, sticky=tk.E)
        total_label = ttk.Label(frame, textvariable=total_var, font=('Arial', 12, 'bold'))
        total_label.grid(row=7, column=3, sticky=tk.W)
        
        def save_order():
            customer_name = name_entry.get().strip()
            customer_email = email_entry.get().strip()
            customer_phone = phone_entry.get().strip()
            address = address_entry.get().strip()
            svc_name = service_var.get()
            svc_id = service_name_to_id.get(svc_name)
            if not validate_required(customer_name, "Customer name"):
                return
            if not validate_required(customer_email, "Customer email") or not validate_email(customer_email):
                show_error("Invalid email address format")
                return
            # Build items list
            items = []
            for row in item_rows:
                if not row.get('active', True):
                    continue
                gname = row['garment_var'].get()
                gid = garment_name_to_id.get(gname)
                try:
                    qty = int(row['qty_var'].get() or '0')
                except Exception:
                    qty = 0
                instr = row['instr_entry'].get().strip()
                if gid and qty > 0:
                    items.append({'garment_type': gid, 'quantity': qty, 'instructions': instr})
            if not items:
                show_error("Please add at least one item with quantity > 0")
                return
            # Compute totals and summary
            total_amount = recalc_total()
            summary = "; ".join([f"{it['quantity']}x {garment_id_to_name.get(it['garment_type'], it['garment_type'])}" for it in items])
            total_qty = sum(it['quantity'] for it in items)
            pickup = pickup_entry.get().strip() or None
            delivery = delivery_entry.get().strip() or None
            # Basic datetime validation if provided
            def _parse_dt(s):
                if not s:
                    return None
                try:
                    return datetime.strptime(s, '%Y-%m-%d %H:%M').isoformat()
                except Exception:
                    show_error("Invalid datetime format. Use YYYY-MM-DD HH:MM")
                    return None
            pickup_iso = _parse_dt(pickup)
            if pickup and not pickup_iso:
                return
            delivery_iso = _parse_dt(delivery)
            if delivery and not delivery_iso:
                return
            try:
                order_id = self.db.create_order(
                    customer_name=customer_name,
                    customer_email=customer_email,
                    customer_phone=customer_phone,
                    item_description=summary or 'Service Order',
                    quantity=total_qty,
                    price=service_rate.get(svc_id, 0.0) if svc_id else 0.0,
                    service_type=svc_id,
                    items=items,
                    instructions=None,
                    scheduled_pickup=pickup_iso,
                    scheduled_delivery=delivery_iso,
                    customer_id=None,
                    address=address
                )
                show_success(f"Order #{order_id} created successfully!")
                dialog.destroy()
                self.load_orders()
            except Exception as e:
                show_error(f"Error creating order: {str(e)}")
        
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=8, column=0, columnspan=4, pady=20)
        
        ttk.Button(button_frame, text="Save", command=save_order).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
    
    def edit_selected_order(self):
        """Edit the selected order with service, items, status, and scheduling."""
        selection = self.tree.selection()
        if not selection:
            show_error("Please select an order to edit")
            return
        
        item = self.tree.item(selection[0])
        order_id = item['values'][0]
        order = self.db.get_order(order_id)
        
        if not order:
            show_error("Order not found")
            return
        
        dialog = tk.Toplevel(self.root)
        dialog.title(f"Edit Order #{order_id}")
        dialog.geometry("850x700")
        dialog.transient(self.root)
        dialog.grab_set()
        
        frame = ttk.Frame(dialog, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text=f"Edit Order #{order_id}", style='Header.TLabel').grid(
            row=0, column=0, columnspan=4, pady=(0, 20), sticky=tk.W)
        
        # Reference data
        service_types = self.db.get_service_types()
        garment_types = self.db.get_garment_types()
        service_id_to_name = {s['id']: s['name'] for s in service_types}
        service_name_to_id = {s['name']: s['id'] for s in service_types}
        garment_id_to_name = {g['id']: g['name'] for g in garment_types}
        garment_name_to_id = {g['name']: g['id'] for g in garment_types}
        garment_multiplier = {g['id']: g['multiplier'] for g in garment_types}
        service_rate = {s['id']: s['rate'] for s in service_types}
        
        # Customer fields
        ttk.Label(frame, text="Customer Name:").grid(row=1, column=0, sticky=tk.W, pady=5)
        name_entry = ttk.Entry(frame, width=30)
        name_entry.insert(0, order['customer_name'])
        name_entry.grid(row=1, column=1, pady=5, sticky=tk.W)
        
        ttk.Label(frame, text="Customer Email:").grid(row=1, column=2, sticky=tk.W, pady=5)
        email_entry = ttk.Entry(frame, width=30)
        email_entry.insert(0, order['customer_email'])
        email_entry.grid(row=1, column=3, pady=5, sticky=tk.W)
        
        ttk.Label(frame, text="Customer Phone:").grid(row=2, column=0, sticky=tk.W, pady=5)
        phone_entry = ttk.Entry(frame, width=30)
        phone_entry.insert(0, order['customer_phone'] or '')
        phone_entry.grid(row=2, column=1, pady=5, sticky=tk.W)
        
        # Service selection
        ttk.Label(frame, text="Service Type:").grid(row=3, column=0, sticky=tk.W, pady=5)
        service_var = tk.StringVar()
        service_combo = ttk.Combobox(frame, textvariable=service_var, state='readonly', width=28)
        service_combo['values'] = [s['name'] for s in service_types]
        current_service_name = service_id_to_name.get(order.get('service_type')) if order.get('service_type') else (service_types[0]['name'] if service_types else '')
        if current_service_name:
            service_combo.set(current_service_name)
        service_combo.grid(row=3, column=1, pady=5, sticky=tk.W)
        
        # Items section
        ttk.Label(frame, text="Items:").grid(row=4, column=0, sticky=tk.W, pady=(10, 5))
        items_frame = ttk.Frame(frame)
        items_frame.grid(row=5, column=0, columnspan=4, sticky='ew')
        items_frame.grid_columnconfigure(0, weight=1)
        items_frame.grid_columnconfigure(1, weight=1)
        items_frame.grid_columnconfigure(2, weight=1)
        items_frame.grid_columnconfigure(3, weight=0)
        
        header = ttk.Frame(items_frame)
        header.grid(row=0, column=0, columnspan=4, sticky='ew')
        ttk.Label(header, text='Garment Type', width=25).grid(row=0, column=0, padx=5)
        ttk.Label(header, text='Quantity', width=10).grid(row=0, column=1, padx=5)
        ttk.Label(header, text='Instructions', width=40).grid(row=0, column=2, padx=5)
        
        item_rows = []
        
        def recalc_total(*args):
            svc_name = service_var.get()
            svc_id = service_name_to_id.get(svc_name)
            total = 0.0
            if not svc_id:
                total = 0.0
            else:
                rate = float(service_rate.get(svc_id, 0.0))
                for row in item_rows:
                    if not row.get('active', True):
                        continue
                    gname = row['garment_var'].get()
                    gid = garment_name_to_id.get(gname)
                    try:
                        qty = int(row['qty_var'].get() or '0')
                    except Exception:
                        qty = 0
                    mult = float(garment_multiplier.get(gid, 1.0))
                    total += qty * rate * mult
            total_var.set(f"${total:.2f}")
            return total
        
        def add_item_row(default_garment=None, default_qty='1', default_instr=''):
            rindex = len(item_rows) + 1
            row_frame = ttk.Frame(items_frame)
            row_frame.grid(row=rindex, column=0, columnspan=4, sticky='ew', pady=2)
            
            garment_var = tk.StringVar(value=default_garment or (garment_types[0]['name'] if garment_types else ''))
            garment_combo = ttk.Combobox(row_frame, textvariable=garment_var, state='readonly', width=25)
            garment_combo['values'] = [g['name'] for g in garment_types]
            garment_combo.grid(row=0, column=0, padx=5)
            garment_combo.bind('<<ComboboxSelected>>', recalc_total)
            
            qty_var = tk.StringVar(value=str(default_qty))
            qty_entry = ttk.Entry(row_frame, textvariable=qty_var, width=8)
            qty_entry.grid(row=0, column=1, padx=5)
            qty_entry.bind('<KeyRelease>', recalc_total)
            
            instr_entry = ttk.Entry(row_frame, width=50)
            instr_entry.insert(0, default_instr)
            instr_entry.grid(row=0, column=2, padx=5)
            
            def remove_row():
                row_frame.grid_forget()
                row['active'] = False
                recalc_total()
            remove_btn = ttk.Button(row_frame, text='Remove', command=remove_row)
            remove_btn.grid(row=0, column=3, padx=5)
            
            row = {
                'frame': row_frame,
                'garment_var': garment_var,
                'qty_var': qty_var,
                'instr_entry': instr_entry,
                'active': True
            }
            item_rows.append(row)
            recalc_total()
        
        # Populate existing items if present
        try:
            existing_items = json.loads(order.get('items_json') or '[]')
        except Exception:
            existing_items = []
        if existing_items:
            for it in existing_items:
                add_item_row(
                    default_garment=garment_id_to_name.get(it.get('garment_type')),
                    default_qty=str(it.get('quantity', 1)),
                    default_instr=it.get('instructions', '')
                )
        else:
            add_item_row()
        
        add_item_btn = ttk.Button(frame, text="Add Item", command=lambda: add_item_row())
        add_item_btn.grid(row=4, column=1, sticky=tk.W, pady=(10, 5))
        
        # Scheduling fields
        ttk.Label(frame, text="Scheduled Pickup (YYYY-MM-DD HH:MM):").grid(row=6, column=0, sticky=tk.W, pady=10)
        pickup_entry = ttk.Entry(frame, width=25)
        pickup_val = order.get('scheduled_pickup')
        pickup_entry.insert(0, datetime.fromisoformat(pickup_val).strftime('%Y-%m-%d %H:%M') if pickup_val else '')
        pickup_entry.grid(row=6, column=1, sticky=tk.W, pady=10)
        
        ttk.Label(frame, text="Scheduled Delivery (YYYY-MM-DD HH:MM):").grid(row=6, column=2, sticky=tk.W, pady=10)
        delivery_entry = ttk.Entry(frame, width=25)
        delivery_val = order.get('scheduled_delivery')
        delivery_entry.insert(0, datetime.fromisoformat(delivery_val).strftime('%Y-%m-%d %H:%M') if delivery_val else '')
        delivery_entry.grid(row=6, column=3, sticky=tk.W, pady=10)
        
        # Status selection
        ttk.Label(frame, text="Status:").grid(row=7, column=0, sticky=tk.W, pady=5)
        status_var = tk.StringVar(value=order.get('status', 'pending'))
        status_combo = ttk.Combobox(frame, textvariable=status_var, state='readonly', width=20)
        status_combo['values'] = ('pending', 'scheduled', 'in_progress', 'ready', 'completed', 'cancelled')
        status_combo.grid(row=7, column=1, sticky=tk.W, pady=5)
        
        # Total display
        total_var = tk.StringVar(value=f"${order.get('total_price', 0.0):.2f}")
        ttk.Label(frame, text="Total:", font=('Arial', 12, 'bold')).grid(row=8, column=2, sticky=tk.E)
        total_label = ttk.Label(frame, textvariable=total_var, font=('Arial', 12, 'bold'))
        total_label.grid(row=8, column=3, sticky=tk.W)
        
        def save_changes():
            customer_name = name_entry.get().strip()
            customer_email = email_entry.get().strip()
            customer_phone = phone_entry.get().strip()
            svc_name = service_var.get()
            svc_id = service_name_to_id.get(svc_name)
            if not validate_required(customer_name, "Customer name"):
                return
            if not validate_required(customer_email, "Customer email") or not validate_email(customer_email):
                show_error("Invalid email address format")
                return
            # Build items list
            items = []
            for row in item_rows:
                if not row.get('active', True):
                    continue
                gname = row['garment_var'].get()
                gid = garment_name_to_id.get(gname)
                try:
                    qty = int(row['qty_var'].get() or '0')
                except Exception:
                    qty = 0
                instr = row['instr_entry'].get().strip()
                if gid and qty > 0:
                    items.append({'garment_type': gid, 'quantity': qty, 'instructions': instr})
            if not items:
                show_error("Please add at least one item with quantity > 0")
                return
            # Compute totals and summary
            total_amount = recalc_total()
            summary = "; ".join([f"{it['quantity']}x {garment_id_to_name.get(it['garment_type'], it['garment_type'])}" for it in items])
            total_qty = sum(it['quantity'] for it in items)
            pickup = pickup_entry.get().strip() or None
            delivery = delivery_entry.get().strip() or None
            def _parse_dt(s):
                if not s:
                    return None
                try:
                    return datetime.strptime(s, '%Y-%m-%d %H:%M').isoformat()
                except Exception:
                    show_error("Invalid datetime format. Use YYYY-MM-DD HH:MM")
                    return None
            pickup_iso = _parse_dt(pickup)
            if pickup and not pickup_iso:
                return
            delivery_iso = _parse_dt(delivery)
            if delivery and not delivery_iso:
                return
            try:
                self.db.update_order(
                    order_id=order_id,
                    customer_name=customer_name,
                    customer_email=customer_email,
                    customer_phone=customer_phone,
                    item_description=summary or order['item_description'],
                    quantity=total_qty,
                    price=service_rate.get(svc_id, 0.0) if svc_id else order['price'],
                    service_type=svc_id,
                    items=items,
                    scheduled_pickup=pickup_iso,
                    scheduled_delivery=delivery_iso,
                    status=status_var.get()
                )
                show_success(f"Order #{order_id} updated successfully!")
                dialog.destroy()
                self.load_orders()
            except Exception as e:
                show_error(f"Error updating order: {str(e)}")
        
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=9, column=0, columnspan=4, pady=20)
        
        ttk.Button(button_frame, text="Save", command=save_changes).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
    
    def mark_order_ready(self):
        """Mark selected order as ready and send notifications."""
        selection = self.tree.selection()
        if not selection:
            show_error("Please select an order to mark as ready")
            return
        
        item = self.tree.item(selection[0])
        order_id = item['values'][0]
        order = self.db.get_order(order_id)
        
        if not order:
            show_error("Order not found")
            return
        
        if order['status'] == 'ready':
            show_info("Order is already marked as ready")
            return
        
        if not confirm_action(f"Mark order #{order_id} as ready and notify customer?"):
            return
        
        try:
            self.db.update_order_status(order_id, 'ready')
            
            updated_order = self.db.get_order(order_id)
            results = self.notification_manager.notify_order_ready(updated_order)
            
            msg = f"Order #{order_id} marked as ready!"
            if results['email_sent']:
                msg += "\nEmail notification sent."
            else:
                msg += "\nEmail notification skipped (not configured)."
            
            if results['sms_sent']:
                msg += "\nSMS notification sent."
            
            show_success(msg)
            self.load_orders()
        except Exception as e:
            show_error(f"Error marking order as ready: {str(e)}")
    
    def mark_order_completed(self):
        """Mark selected order as completed."""
        selection = self.tree.selection()
        if not selection:
            show_error("Please select an order to mark as completed")
            return
        
        item = self.tree.item(selection[0])
        order_id = item['values'][0]
        order = self.db.get_order(order_id)
        
        if not order:
            show_error("Order not found")
            return
        
        if order['status'] == 'completed':
            show_info("Order is already marked as completed")
            return
        
        if not confirm_action(f"Mark order #{order_id} as completed?"):
            return
        
        try:
            self.db.update_order_status(order_id, 'completed')
            show_success(f"Order #{order_id} marked as completed!")
            self.load_orders()
        except Exception as e:
            show_error(f"Error marking order as completed: {str(e)}")
    
    def delete_selected_order(self):
        """Delete the selected order."""
        selection = self.tree.selection()
        if not selection:
            show_error("Please select an order to delete")
            return
        
        item = self.tree.item(selection[0])
        order_id = item['values'][0]
        
        if not confirm_action(f"Delete order #{order_id}? This action cannot be undone."):
            return
        
        try:
            self.db.delete_order(order_id)
            show_success(f"Order #{order_id} deleted successfully!")
            self.load_orders()
        except Exception as e:
            show_error(f"Error deleting order: {str(e)}")

    def show_payment_dialog(self):
        """Show payment management dialog for the selected order."""
        selection = self.tree.selection()
        if not selection:
            show_error("Please select an order to manage payments")
            return

        item = self.tree.item(selection[0])
        order_id = item['values'][0]
        order = self.db.get_order(order_id)

        dialog = tk.Toplevel(self.root)
        dialog.title(f"Payments for Order #{order_id}")
        dialog.geometry("600x500")
        dialog.transient(self.root)
        dialog.grab_set()

        frame = ttk.Frame(dialog, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text=f"Manage Payments for Order #{order_id}", style='Header.TLabel').pack(pady=(0, 10))

        # Payment details
        total_price = order['total_price']
        payments = self.db.get_payments_for_order(order_id)
        total_paid = sum(p['amount_paid'] for p in payments)
        balance_due = total_price - total_paid

        ttk.Label(frame, text=f"Total Amount: ${total_price:.2f}").pack(anchor=tk.W)
        ttk.Label(frame, text=f"Amount Paid: ${total_paid:.2f}").pack(anchor=tk.W)
        ttk.Label(frame, text=f"Balance Due: ${balance_due:.2f}").pack(anchor=tk.W, pady=(0, 20))

        # Payment history
        history_frame = ttk.LabelFrame(frame, text="Payment History", padding="10")
        history_frame.pack(fill=tk.BOTH, expand=True)

        cols = ('ID', 'Amount', 'Method', 'Date')
        tree = ttk.Treeview(history_frame, columns=cols, show='headings', height=5)
        tree.pack(fill=tk.BOTH, expand=True)
        for col in cols:
            tree.heading(col, text=col)
        
        for p in payments:
            tree.insert('', 'end', values=(p['id'], f"${p['amount_paid']:.2f}", p['payment_method'], p['payment_date']))

        # Add payment
        payment_frame = ttk.LabelFrame(frame, text="Add Payment", padding="10")
        payment_frame.pack(fill=tk.X, pady=10)

        ttk.Label(payment_frame, text="Amount:").grid(row=0, column=0, padx=5, pady=5)
        amount_entry = ttk.Entry(payment_frame)
        amount_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(payment_frame, text="Method:").grid(row=0, column=2, padx=5, pady=5)
        method_combo = ttk.Combobox(payment_frame, values=['Cash', 'Credit Card', 'Bank Transfer'])
        method_combo.grid(row=0, column=3, padx=5, pady=5)

        def add_payment():
            amount = amount_entry.get()
            method = method_combo.get()
            if not amount or not method:
                show_error("Amount and method are required.")
                return
            try:
                amount_val = float(amount)
                self.db.add_payment(order_id, amount_val, method)
                show_success("Payment added.")
                dialog.destroy()
                self.load_orders()
            except ValueError:
                show_error("Invalid amount.")
            except Exception as e:
                show_error(f"Error: {e}")

        ttk.Button(payment_frame, text="Add Payment", command=add_payment).grid(row=0, column=4, padx=5, pady=5)

        # Actions
        action_frame = ttk.Frame(frame)
        action_frame.pack(pady=10)

        def print_receipt():
            receipt_content = self.generate_receipt(order, payments)
            self.show_printable_output("Receipt", receipt_content)

        def print_invoice():
            invoice_content = self.generate_invoice(order, payments)
            self.show_printable_output("Invoice", invoice_content)

        ttk.Button(action_frame, text="Print Receipt", command=print_receipt).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="Print Invoice", command=print_invoice).pack(side=tk.LEFT, padx=5)

    def generate_receipt(self, order, payments):
        total_paid = sum(p['amount_paid'] for p in payments)
        return f"""
        *** RECEIPT ***
        Order ID: {order['id']}
        Customer: {order['customer_name']}
        Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}
        --------------------
        Item: {order['item_description']}
        Qty: {order['quantity']}
        Price: ${order['price']:.2f}
        Total: ${order['total_price']:.2f}
        --------------------
        Amount Paid: ${total_paid:.2f}
        Balance Due: ${order['total_price'] - total_paid:.2f}

        Thank you for your business!
        """

    def generate_invoice(self, order, payments):
        total_paid = sum(p['amount_paid'] for p in payments)
        return f"""
        *** INVOICE ***
        Order ID: {order['id']}
        Customer: {order['customer_name']}
        Email: {order['customer_email']}
        Date: {datetime.now().strftime('%Y-%m-%d')}
        --------------------
        Description: {order['item_description']}
        Quantity: {order['quantity']}
        Unit Price: ${order['price']:.2f}
        Total: ${order['total_price']:.2f}
        --------------------
        Amount Paid: ${total_paid:.2f}
        Balance Due: ${order['total_price'] - total_paid:.2f}

        Please remit payment to...
        """

    def show_printable_output(self, title, content):
        output_dialog = tk.Toplevel(self.root)
        output_dialog.title(title)
        output_dialog.geometry("400x500")
        
        text_widget = tk.Text(output_dialog, wrap='word', font=("Courier", 10))
        text_widget.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        text_widget.insert('1.0', content)
        text_widget.config(state='disabled')
        
        ttk.Button(output_dialog, text="Close", command=output_dialog.destroy).pack(pady=10)
    
    def show_settings_dialog(self):
        """Show settings dialog for configuring notifications."""
        dialog = tk.Toplevel(self.root)
        dialog.title("Settings")
        dialog.geometry("500x450")
        dialog.transient(self.root)
        dialog.grab_set()
        
        frame = ttk.Frame(dialog, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="Notification Settings", style='Header.TLabel').grid(
            row=0, column=0, columnspan=2, pady=(0, 20))
        
        ttk.Label(frame, text="SMTP Configuration", style='Header.TLabel').grid(
            row=1, column=0, columnspan=2, sticky=tk.W, pady=(10, 10))
        
        ttk.Label(frame, text="SMTP Server:").grid(row=2, column=0, sticky=tk.W, pady=5)
        smtp_server_entry = ttk.Entry(frame, width=30)
        smtp_server_entry.insert(0, self.notification_manager.config.smtp_server)
        smtp_server_entry.grid(row=2, column=1, pady=5)
        
        ttk.Label(frame, text="SMTP Port:").grid(row=3, column=0, sticky=tk.W, pady=5)
        smtp_port_entry = ttk.Entry(frame, width=30)
        smtp_port_entry.insert(0, str(self.notification_manager.config.smtp_port))
        smtp_port_entry.grid(row=3, column=1, pady=5)
        
        ttk.Label(frame, text="SMTP Username:").grid(row=4, column=0, sticky=tk.W, pady=5)
        smtp_user_entry = ttk.Entry(frame, width=30)
        smtp_user_entry.insert(0, self.notification_manager.config.smtp_username)
        smtp_user_entry.grid(row=4, column=1, pady=5)
        
        ttk.Label(frame, text="SMTP Password:").grid(row=5, column=0, sticky=tk.W, pady=5)
        smtp_pass_entry = ttk.Entry(frame, width=30, show="*")
        smtp_pass_entry.insert(0, self.notification_manager.config.smtp_password)
        smtp_pass_entry.grid(row=5, column=1, pady=5)
        
        ttk.Label(frame, text="From Email:").grid(row=6, column=0, sticky=tk.W, pady=5)
        smtp_from_entry = ttk.Entry(frame, width=30)
        smtp_from_entry.insert(0, self.notification_manager.config.smtp_from)
        smtp_from_entry.grid(row=6, column=1, pady=5)
        
        ttk.Label(frame, text="SMS Configuration", style='Header.TLabel').grid(
            row=7, column=0, columnspan=2, sticky=tk.W, pady=(20, 10))
        
        sms_enabled_var = tk.BooleanVar(value=self.notification_manager.config.sms_enabled)
        ttk.Checkbutton(frame, text="Enable SMS Notifications", 
                       variable=sms_enabled_var).grid(row=8, column=0, columnspan=2, 
                                                     sticky=tk.W, pady=5)
        
        ttk.Label(frame, text="SMS API Key:").grid(row=9, column=0, sticky=tk.W, pady=5)
        sms_api_entry = ttk.Entry(frame, width=30)
        sms_api_entry.insert(0, self.notification_manager.config.sms_api_key)
        sms_api_entry.grid(row=9, column=1, pady=5)
        
        def save_settings():
            try:
                self.notification_manager.update_config(
                    smtp_server=smtp_server_entry.get(),
                    smtp_port=int(smtp_port_entry.get()),
                    smtp_username=smtp_user_entry.get(),
                    smtp_password=smtp_pass_entry.get(),
                    smtp_from=smtp_from_entry.get(),
                    sms_enabled=sms_enabled_var.get(),
                    sms_api_key=sms_api_entry.get()
                )
                show_success("Settings saved successfully!")
                dialog.destroy()
            except Exception as e:
                show_error(f"Error saving settings: {str(e)}")
        
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=10, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="Save", command=save_settings).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
    
    def show_help_dialog(self):
        """Show help dialog."""
        help_text = """
Order Management System - Help

CREATING ORDERS:
1. Click "New Order" button or use File > New Order
2. Fill in customer details and item information
3. Click "Save" to create the order

MANAGING ORDERS:
- Edit: Select an order and click "Edit Order" or double-click
- Mark Ready: Select an order and click "Mark Ready" to notify customer
- Mark Completed: Select an order and click "Mark Completed"
- Delete: Select an order and click "Delete Order"

FILTERING:
Use the filter dropdown to view orders by status:
- All: Show all orders
- Pending: Show pending orders only
- Ready: Show ready orders only
- Completed: Show completed orders only

NOTIFICATIONS:
Configure email and SMS notifications in File > Settings
When an order is marked as ready, notifications are sent to:
- Customer email (if SMTP is configured)
- Customer phone (if SMS is enabled)

KEYBOARD SHORTCUTS:
- Double-click: Edit selected order
- F5: Refresh order list
        """
        
        dialog = tk.Toplevel(self.root)
        dialog.title("Help")
        dialog.geometry("600x500")
        dialog.transient(self.root)
        
        frame = ttk.Frame(dialog, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        text_widget = tk.Text(frame, wrap=tk.WORD, font=('Arial', 10))
        text_widget.pack(fill=tk.BOTH, expand=True)
        text_widget.insert('1.0', help_text)
        text_widget.config(state=tk.DISABLED)
        
        ttk.Button(frame, text="Close", command=dialog.destroy).pack(pady=(10, 0))
    
    def show_about_dialog(self):
        """Show about dialog."""
        about_text = """
Order Management System
Version 1.0.0

A comprehensive order management application with:
- Order creation and tracking
- Customer notification system (Email/SMS)
- Order status management
- Statistics and reporting

Features:
✓ Input validation
✓ Email notifications (SMTP)
✓ SMS notification stubs
✓ Modern GUI with ttk themes
✓ Order filtering and search
✓ Database persistence

Developed with Python and Tkinter
        """
        
        messagebox.showinfo("About", about_text)


def main():
    """Main entry point for the application."""
    root = tk.Tk()
    app = OrderManagementApp(root)
    
    root.bind('<F5>', lambda e: app.load_orders())
    
    root.mainloop()


if __name__ == '__main__':
    main()
