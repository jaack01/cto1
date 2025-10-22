
import tkinter as tk
from tkinter import ttk, messagebox
from database import Database
from validation import validate_required, validate_email, show_error, show_success

class CustomerManagementFrame(ttk.Frame):
    """Frame for customer management."""
    
    def __init__(self, parent, db: Database, app):
        super().__init__(parent)
        self.db = db
        self.app = app
        self.create_widgets()
        self.load_customers()

    def create_widgets(self):
        """Create and arrange widgets for the customer management frame."""
        main_container = ttk.Frame(self, padding="10")
        main_container.pack(fill=tk.BOTH, expand=True)

        # Title
        title_label = ttk.Label(main_container, text="Customer Management", style='Title.TLabel')
        title_label.pack(side=tk.TOP, anchor=tk.W, pady=(0, 10))

        # Toolbar for search and filter
        toolbar_frame = ttk.Frame(main_container)
        toolbar_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(toolbar_frame, text="Search:").pack(side=tk.LEFT, padx=(0, 5))
        self.search_entry = ttk.Entry(toolbar_frame, width=30)
        self.search_entry.pack(side=tk.LEFT, padx=(0, 10))
        self.search_entry.bind('<KeyRelease>', lambda e: self.filter_customers())
        
        ttk.Button(toolbar_frame, text="Add Customer", command=self.add_customer_dialog).pack(side=tk.RIGHT)

        # Customer list
        tree_frame = ttk.Frame(main_container)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        columns = ('id', 'name', 'email', 'phone', 'address', 'created_at')
        self.tree = ttk.Treeview(tree_frame, columns=columns, show='headings')
        
        self.tree.heading('id', text='ID')
        self.tree.heading('name', text='Name')
        self.tree.heading('email', text='Email')
        self.tree.heading('phone', text='Phone')
        self.tree.heading('address', text='Address')
        self.tree.heading('created_at', text='Member Since')
        
        self.tree.column('id', width=50, anchor=tk.CENTER)
        self.tree.column('name', width=150)
        self.tree.column('email', width=200)
        self.tree.column('phone', width=120)
        self.tree.column('address', width=300)
        self.tree.column('created_at', width=150)
        
        self.tree.pack(fill=tk.BOTH, expand=True)
        self.tree.bind('<Double-1>', lambda e: self.edit_customer_dialog())
        
        # Action buttons
        action_frame = ttk.Frame(main_container)
        action_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(action_frame, text="Edit Selected", command=self.edit_customer_dialog).pack(side=tk.LEFT)
        ttk.Button(action_frame, text="Delete Selected", command=self.delete_customer).pack(side=tk.LEFT, padx=10)
        ttk.Button(action_frame, text="View History", command=self.view_customer_history).pack(side=tk.LEFT)
        ttk.Button(action_frame, text="Preferences", command=self.customer_preferences_dialog).pack(side=tk.LEFT, padx=10)
        ttk.Button(action_frame, text="Create Order for Customer", command=self.create_order_for_customer).pack(side=tk.RIGHT)

    def load_customers(self):
        """Load customers from the database and display them in the treeview."""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        customers = self.db.get_all_customers()
        for customer in customers:
            self.tree.insert('', tk.END, values=(
                customer['id'],
                customer['name'],
                customer['email'],
                customer['phone'],
                customer['address'],
                customer['created_at']
            ))

    def filter_customers(self):
        """Filter customers based on search query."""
        search_term = self.search_entry.get().strip().lower()
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        customers = self.db.search_customers(search_term)
        for customer in customers:
            self.tree.insert('', tk.END, values=(
                customer['id'],
                customer['name'],
                customer['email'],
                customer['phone'],
                customer['address'],
                customer['created_at']
            ))

    def add_customer_dialog(self):
        """Show a dialog to add a new customer."""
        self.customer_dialog("Add New Customer", self.save_new_customer)

    def edit_customer_dialog(self):
        """Show a dialog to edit the selected customer."""
        selected_item = self.tree.selection()
        if not selected_item:
            show_error("Please select a customer to edit.")
            return
        
        customer_id = self.tree.item(selected_item)['values'][0]
        customer = self.db.get_customer_by_id(customer_id)
        
        self.customer_dialog("Edit Customer", lambda data: self.save_updated_customer(customer_id, data), customer)

    def customer_dialog(self, title, save_command, customer=None):
        """Generic dialog for adding/editing a customer."""
        dialog = tk.Toplevel(self)
        dialog.title(title)
        dialog.transient(self)
        dialog.grab_set()

        frame = ttk.Frame(dialog, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text="Name:").grid(row=0, column=0, sticky=tk.W, pady=5)
        name_entry = ttk.Entry(frame, width=40)
        name_entry.grid(row=0, column=1, pady=5)
        if customer:
            name_entry.insert(0, customer['name'])

        ttk.Label(frame, text="Email:").grid(row=1, column=0, sticky=tk.W, pady=5)
        email_entry = ttk.Entry(frame, width=40)
        email_entry.grid(row=1, column=1, pady=5)
        if customer:
            email_entry.insert(0, customer['email'])

        ttk.Label(frame, text="Phone:").grid(row=2, column=0, sticky=tk.W, pady=5)
        phone_entry = ttk.Entry(frame, width=40)
        phone_entry.grid(row=2, column=1, pady=5)
        if customer:
            phone_entry.insert(0, customer.get('phone', ''))

        ttk.Label(frame, text="Address:").grid(row=3, column=0, sticky=tk.W, pady=5)
        address_entry = ttk.Entry(frame, width=40)
        address_entry.grid(row=3, column=1, pady=5)
        if customer:
            address_entry.insert(0, customer.get('address', ''))

        def on_save():
            data = {
                'name': name_entry.get().strip(),
                'email': email_entry.get().strip(),
                'phone': phone_entry.get().strip(),
                'address': address_entry.get().strip(),
            }
            if not validate_required(data['name'], "Name") or not validate_required(data['email'], "Email"):
                return
            if not validate_email(data['email']):
                show_error("Invalid email format.")
                return
            
            save_command(data)
            dialog.destroy()
            self.load_customers()

        save_button = ttk.Button(frame, text="Save", command=on_save)
        save_button.grid(row=4, column=0, columnspan=2, pady=10)

    def save_new_customer(self, data):
        """Save a new customer to the database."""
        self.db.add_customer(data)
        show_success("Customer added successfully.")

    def save_updated_customer(self, customer_id, data):
        """Save an updated customer to the database."""
        self.db.update_customer(customer_id, data)
        show_success("Customer updated successfully.")

    def delete_customer(self):
        """Delete the selected customer."""
        selected_item = self.tree.selection()
        if not selected_item:
            show_error("Please select a customer to delete.")
            return

        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete the selected customer?"):
            customer_id = self.tree.item(selected_item)['values'][0]
            self.db.delete_customer(customer_id)
            show_success("Customer deleted successfully.")
            self.load_customers()

    def view_customer_history(self):
        """View the order history of the selected customer."""
        selected_item = self.tree.selection()
        if not selected_item:
            show_error("Please select a customer to view their history.")
            return

        customer_id = self.tree.item(selected_item)['values'][0]
        history = self.db.get_customer_order_history(customer_id)
        
        dialog = tk.Toplevel(self)
        dialog.title("Customer Order History")
        dialog.transient(self)
        dialog.grab_set()

        if not history:
            ttk.Label(dialog, text="No order history found for this customer.").pack(padx=20, pady=20)
            return

        tree = ttk.Treeview(dialog, columns=('order_id', 'date', 'total', 'status'), show='headings')
        tree.heading('order_id', text='Order ID')
        tree.heading('date', text='Date')
        tree.heading('total', text='Total')
        tree.heading('status', text='Status')
        tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        for order in history:
            tree.insert('', tk.END, values=(
                order['id'],
                order['created_at'],
                f"${order['total_price']:.2f}",
                order['status']
            ))

    def customer_preferences_dialog(self):
        """Show a dialog for managing customer preferences."""
        selected_item = self.tree.selection()
        if not selected_item:
            show_error("Please select a customer to manage preferences.")
            return

        customer_id = self.tree.item(selected_item)['values'][0]
        preferences = self.db.get_customer_preferences(customer_id)

        dialog = tk.Toplevel(self)
        dialog.title("Customer Preferences")
        dialog.transient(self)
        dialog.grab_set()

        frame = ttk.Frame(dialog, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text="Starch Level:").grid(row=0, column=0, sticky=tk.W, pady=5)
        starch_var = tk.StringVar(value=preferences.get('starch_level', 'None'))
        starch_combo = ttk.Combobox(frame, textvariable=starch_var, state='readonly', values=['None', 'Light', 'Medium', 'Heavy'])
        starch_combo.grid(row=0, column=1, pady=5)

        ttk.Label(frame, text="Packaging:").grid(row=1, column=0, sticky=tk.W, pady=5)
        packaging_var = tk.StringVar(value=preferences.get('packaging', 'Hanger'))
        packaging_combo = ttk.Combobox(frame, textvariable=packaging_var, state='readonly', values=['Hanger', 'Folded'])
        packaging_combo.grid(row=1, column=1, pady=5)

        def on_save():
            new_preferences = {
                'starch_level': starch_var.get(),
                'packaging': packaging_var.get()
            }
            self.db.update_customer_preferences(customer_id, new_preferences)
            show_success("Preferences updated successfully.")
            dialog.destroy()

        save_button = ttk.Button(frame, text="Save", command=on_save)
        save_button.grid(row=2, column=0, columnspan=2, pady=10)

    def create_order_for_customer(self):
        """Create a new order for the selected customer."""
        selected_item = self.tree.selection()
        if not selected_item:
            show_error("Please select a customer to create an order for.")
            return

        customer_id = self.tree.item(selected_item)['values'][0]
        customer = self.db.get_customer_by_id(customer_id)
        
        if customer:
            self.app.show_new_order_dialog(customer=customer)
        else:
            show_error("Could not retrieve customer details.")
