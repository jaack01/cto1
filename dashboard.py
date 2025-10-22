"""
Dashboard view for the Order Management System.
"""
import tkinter as tk
from tkinter import ttk
from datetime import datetime, timedelta

class DashboardFrame(ttk.Frame):
    """Dashboard frame showing key metrics."""
    
    def __init__(self, parent, db):
        super().__init__(parent, padding="10")
        self.db = db
        
        self.create_widgets()
        self.load_dashboard_data()
    
    def create_widgets(self):
        """Create and arrange widgets in the frame."""
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)
        self.grid_columnconfigure(3, weight=1)
        
        title = ttk.Label(self, text="Dashboard", style='Title.TLabel')
        title.grid(row=0, column=0, columnspan=4, sticky=tk.W, pady=(0, 20))
        
        self.revenue_frame = self.create_metric_frame("Daily Revenue", "$0.00")
        self.revenue_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        
        self.pending_orders_frame = self.create_metric_frame("Pending Orders", "0")
        self.pending_orders_frame.grid(row=1, column=1, padx=10, pady=10, sticky="ew")
        
        self.customer_count_frame = self.create_metric_frame("New Customers (24h)", "0")
        self.customer_count_frame.grid(row=1, column=2, padx=10, pady=10, sticky="ew")

        self.popular_services_frame = self.create_popular_services_frame()
        self.popular_services_frame.grid(row=2, column=0, columnspan=4, padx=10, pady=10, sticky="ewns")
        
        refresh_button = ttk.Button(self, text="Refresh", command=self.load_dashboard_data)
        refresh_button.grid(row=0, column=3, sticky=tk.E)

    def create_metric_frame(self, title, value):
        """Create a frame for a single metric."""
        frame = ttk.LabelFrame(self, text=title, padding="15")
        
        value_label = ttk.Label(frame, text=value, font=('Arial', 18, 'bold'))
        value_label.pack()
        
        frame.value_label = value_label
        return frame

    def create_popular_services_frame(self):
        """Create a frame for popular services."""
        frame = ttk.LabelFrame(self, text="Popular Services", padding="15")
        
        columns = ('item', 'orders')
        tree = ttk.Treeview(frame, columns=columns, show='headings', height=5)
        tree.heading('item', text='Item')
        tree.heading('orders', text='Number of Orders')
        tree.pack(fill=tk.BOTH, expand=True)
        
        frame.tree = tree
        return frame
    
    def load_dashboard_data(self):
        """Load and display dashboard data."""
        # Update metrics
        daily_revenue = self.db.get_daily_revenue()
        self.revenue_frame.value_label.config(text=f"${daily_revenue:.2f}")
        
        pending_orders = self.db.get_pending_orders_count()
        self.pending_orders_frame.value_label.config(text=str(pending_orders))
        
        new_customers = self.db.get_new_customers_count()
        self.customer_count_frame.value_label.config(text=str(new_customers))

        # Update popular services
        for item in self.popular_services_frame.tree.get_children():
            self.popular_services_frame.tree.delete(item)
            
        popular_items = self.db.get_popular_items()
        for item in popular_items:
            self.popular_services_frame.tree.insert('', tk.END, values=(item['item'], item['orders']))
