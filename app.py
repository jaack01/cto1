"""
Order Management System - Main Application
"""
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import webbrowser

from database import Database
from validation import (
    validate_order_form, show_error, show_success, 
    show_info, confirm_action
)
from notifications import NotificationManager, NotificationConfig
from dashboard import DashboardFrame
from reporting import ReportingFrame


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
        ttk.Button(toolbar_frame, text="Refresh", 
                  command=self.load_orders).pack(side=tk.LEFT, padx=2)
        
        ttk.Label(toolbar_frame, text="Filter:").pack(side=tk.LEFT, padx=(20, 5))
        self.filter_var = tk.StringVar(value="all")
        filter_combo = ttk.Combobox(toolbar_frame, textvariable=self.filter_var, 
                                    state='readonly', width=15)
        filter_combo['values'] = ('all', 'pending', 'ready', 'completed')
        filter_combo.pack(side=tk.LEFT, padx=2)
        filter_combo.bind('<<ComboboxSelected>>', lambda e: self.filter_orders(
            None if self.filter_var.get() == 'all' else self.filter_var.get()))
        
        tree_frame = ttk.Frame(orders_container)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        tree_scroll_y = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL)
        tree_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        
        tree_scroll_x = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL)
        tree_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        
        columns = ('ID', 'Customer', 'Email', 'Phone', 'Item', 'Qty', 'Price', 'Total', 'Status', 'Created')
        self.tree = ttk.Treeview(tree_frame, columns=columns, show='headings',
                                yscrollcommand=tree_scroll_y.set,
                                xscrollcommand=tree_scroll_x.set)
        
        tree_scroll_y.config(command=self.tree.yview)
        tree_scroll_x.config(command=self.tree.xview)
        
        self.tree.heading('ID', text='ID')
        self.tree.heading('Customer', text='Customer Name')
        self.tree.heading('Email', text='Email')
        self.tree.heading('Phone', text='Phone')
        self.tree.heading('Item', text='Item Description')
        self.tree.heading('Qty', text='Qty')
        self.tree.heading('Price', text='Price')
        self.tree.heading('Total', text='Total')
        self.tree.heading('Status', text='Status')
        self.tree.heading('Created', text='Created At')
        
        self.tree.column('ID', width=50, anchor=tk.CENTER)
        self.tree.column('Customer', width=120)
        self.tree.column('Email', width=150)
        self.tree.column('Phone', width=100)
        self.tree.column('Item', width=150)
        self.tree.column('Qty', width=50, anchor=tk.CENTER)
        self.tree.column('Price', width=70, anchor=tk.E)
        self.tree.column('Total', width=80, anchor=tk.E)
        self.tree.column('Status', width=80, anchor=tk.CENTER)
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
        
        for order in orders:
            created_at = datetime.fromisoformat(order['created_at']).strftime('%Y-%m-%d %H:%M')
            
            values = (
                order['id'],
                order['customer_name'],
                order['customer_email'],
                order['customer_phone'] or '',
                order['item_description'],
                order['quantity'],
                f"${order['price']:.2f}",
                f"${order['total_price']:.2f}",
                order['status'].upper(),
                created_at
            )
            
            self.tree.insert('', tk.END, values=values, tags=(order['status'],))
        
        self.tree.tag_configure('pending', foreground='orange')
        self.tree.tag_configure('ready', foreground='green')
        self.tree.tag_configure('completed', foreground='blue')
        
        self.update_statistics()
        self.status_label.config(text=f"Loaded {len(orders)} orders")
    
    def filter_orders(self, status):
        """Filter orders by status."""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        orders = self.db.get_all_orders(status)
        
        for order in orders:
            created_at = datetime.fromisoformat(order['created_at']).strftime('%Y-%m-%d %H:%M')
            
            values = (
                order['id'],
                order['customer_name'],
                order['customer_email'],
                order['customer_phone'] or '',
                order['item_description'],
                order['quantity'],
                f"${order['price']:.2f}",
                f"${order['total_price']:.2f}",
                order['status'].upper(),
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
    
    def show_new_order_dialog(self):
        """Show dialog to create new order."""
        dialog = tk.Toplevel(self.root)
        dialog.title("New Order")
        dialog.geometry("500x400")
        dialog.transient(self.root)
        dialog.grab_set()
        
        frame = ttk.Frame(dialog, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="Create New Order", style='Header.TLabel').grid(
            row=0, column=0, columnspan=2, pady=(0, 20))
        
        ttk.Label(frame, text="Customer Name:").grid(row=1, column=0, sticky=tk.W, pady=5)
        name_entry = ttk.Entry(frame, width=30)
        name_entry.grid(row=1, column=1, pady=5)
        
        ttk.Label(frame, text="Customer Email:").grid(row=2, column=0, sticky=tk.W, pady=5)
        email_entry = ttk.Entry(frame, width=30)
        email_entry.grid(row=2, column=1, pady=5)
        
        ttk.Label(frame, text="Customer Phone:").grid(row=3, column=0, sticky=tk.W, pady=5)
        phone_entry = ttk.Entry(frame, width=30)
        phone_entry.grid(row=3, column=1, pady=5)
        
        ttk.Label(frame, text="Item Description:").grid(row=4, column=0, sticky=tk.W, pady=5)
        item_entry = ttk.Entry(frame, width=30)
        item_entry.grid(row=4, column=1, pady=5)
        
        ttk.Label(frame, text="Quantity:").grid(row=5, column=0, sticky=tk.W, pady=5)
        qty_entry = ttk.Entry(frame, width=30)
        qty_entry.grid(row=5, column=1, pady=5)
        
        ttk.Label(frame, text="Price per Item:").grid(row=6, column=0, sticky=tk.W, pady=5)
        price_entry = ttk.Entry(frame, width=30)
        price_entry.grid(row=6, column=1, pady=5)
        
        def save_order():
            customer_name = name_entry.get()
            customer_email = email_entry.get()
            customer_phone = phone_entry.get()
            item_description = item_entry.get()
            quantity = qty_entry.get()
            price = price_entry.get()
            
            if not validate_order_form(customer_name, customer_email, customer_phone,
                                      item_description, quantity, price):
                return
            
            try:
                order_id = self.db.create_order(
                    customer_name, customer_email, customer_phone,
                    item_description, int(quantity), float(price)
                )
                show_success(f"Order #{order_id} created successfully!")
                dialog.destroy()
                self.load_orders()
            except Exception as e:
                show_error(f"Error creating order: {str(e)}")
        
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=7, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="Save", command=save_order).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
    
    def edit_selected_order(self):
        """Edit the selected order."""
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
        dialog.geometry("500x400")
        dialog.transient(self.root)
        dialog.grab_set()
        
        frame = ttk.Frame(dialog, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text=f"Edit Order #{order_id}", style='Header.TLabel').grid(
            row=0, column=0, columnspan=2, pady=(0, 20))
        
        ttk.Label(frame, text="Customer Name:").grid(row=1, column=0, sticky=tk.W, pady=5)
        name_entry = ttk.Entry(frame, width=30)
        name_entry.insert(0, order['customer_name'])
        name_entry.grid(row=1, column=1, pady=5)
        
        ttk.Label(frame, text="Customer Email:").grid(row=2, column=0, sticky=tk.W, pady=5)
        email_entry = ttk.Entry(frame, width=30)
        email_entry.insert(0, order['customer_email'])
        email_entry.grid(row=2, column=1, pady=5)
        
        ttk.Label(frame, text="Customer Phone:").grid(row=3, column=0, sticky=tk.W, pady=5)
        phone_entry = ttk.Entry(frame, width=30)
        phone_entry.insert(0, order['customer_phone'] or '')
        phone_entry.grid(row=3, column=1, pady=5)
        
        ttk.Label(frame, text="Item Description:").grid(row=4, column=0, sticky=tk.W, pady=5)
        item_entry = ttk.Entry(frame, width=30)
        item_entry.insert(0, order['item_description'])
        item_entry.grid(row=4, column=1, pady=5)
        
        ttk.Label(frame, text="Quantity:").grid(row=5, column=0, sticky=tk.W, pady=5)
        qty_entry = ttk.Entry(frame, width=30)
        qty_entry.insert(0, str(order['quantity']))
        qty_entry.grid(row=5, column=1, pady=5)
        
        ttk.Label(frame, text="Price per Item:").grid(row=6, column=0, sticky=tk.W, pady=5)
        price_entry = ttk.Entry(frame, width=30)
        price_entry.insert(0, str(order['price']))
        price_entry.grid(row=6, column=1, pady=5)
        
        def save_changes():
            customer_name = name_entry.get()
            customer_email = email_entry.get()
            customer_phone = phone_entry.get()
            item_description = item_entry.get()
            quantity = qty_entry.get()
            price = price_entry.get()
            
            if not validate_order_form(customer_name, customer_email, customer_phone,
                                      item_description, quantity, price):
                return
            
            try:
                self.db.update_order(
                    order_id, customer_name, customer_email, customer_phone,
                    item_description, int(quantity), float(price)
                )
                show_success(f"Order #{order_id} updated successfully!")
                dialog.destroy()
                self.load_orders()
            except Exception as e:
                show_error(f"Error updating order: {str(e)}")
        
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=7, column=0, columnspan=2, pady=20)
        
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
