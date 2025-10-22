"""
Reporting and data export functionality.
"""
import tkinter as tk
from tkinter import ttk, filedialog
from datetime import datetime, timedelta
import csv

class ReportingFrame(ttk.Frame):
    """Reporting and data export frame."""
    
    def __init__(self, parent, db):
        super().__init__(parent, padding="10")
        self.db = db
        
        self.create_widgets()

    def create_widgets(self):
        """Create and arrange widgets in the frame."""
        # Reporting Section
        reporting_frame = ttk.LabelFrame(self, text="Generate Reports", padding="15")
        reporting_frame.pack(fill=tk.X, expand=True, pady=10)

        ttk.Label(reporting_frame, text="Start Date:").grid(row=0, column=0, padx=5, pady=5)
        self.start_date_entry = ttk.Entry(reporting_frame)
        self.start_date_entry.grid(row=0, column=1, padx=5, pady=5)
        self.start_date_entry.insert(0, (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'))
        
        ttk.Label(reporting_frame, text="End Date:").grid(row=0, column=2, padx=5, pady=5)
        self.end_date_entry = ttk.Entry(reporting_frame)
        self.end_date_entry.grid(row=0, column=3, padx=5, pady=5)
        self.end_date_entry.insert(0, datetime.now().strftime('%Y-%m-%d'))

        generate_button = ttk.Button(reporting_frame, text="Generate Report", command=self.generate_report)
        generate_button.grid(row=0, column=4, padx=10, pady=5)

        self.report_results = tk.Text(self, height=10, width=80)
        self.report_results.pack(pady=10, fill=tk.BOTH, expand=True)

        # CSV Export Section
        export_frame = ttk.LabelFrame(self, text="Export Data", padding="15")
        export_frame.pack(fill=tk.X, expand=True, pady=10)

        ttk.Button(export_frame, text="Export Customers", command=self.export_customers).pack(side=tk.LEFT, padx=5)
        ttk.Button(export_frame, text="Export Orders", command=self.export_orders).pack(side=tk.LEFT, padx=5)
        ttk.Button(export_frame, text="Export Payments", command=self.export_payments).pack(side=tk.LEFT, padx=5)

    def generate_report(self):
        """Generate a sales report for the given date range."""
        start_date = self.start_date_entry.get()
        end_date = self.end_date_entry.get()
        
        try:
            report_data = self.db.get_sales_report(start_date, end_date)
            
            self.report_results.delete(1.0, tk.END)
            self.report_results.insert(tk.END, f"Sales Report from {start_date} to {end_date}\\n")
            self.report_results.insert(tk.END, "="*40 + "\\n")
            self.report_results.insert(tk.END, f"Total Orders: {report_data['total_orders']}\\n")
            self.report_results.insert(tk.END, f"Total Revenue: ${report_data['total_revenue']:.2f}\\n")
            self.report_results.insert(tk.END, f"Completed Orders: {report_data['completed_orders']}\\n")
            self.report_results.insert(tk.END, f"Pending Orders: {report_data['pending_orders']}\\n")
        except Exception as e:
            self.report_results.delete(1.0, tk.END)
            self.report_results.insert(tk.END, f"Error generating report: {e}")

    def export_customers(self):
        """Export customer data to a CSV file."""
        customers = self.db.get_all_customers()
        self._export_to_csv('customers', customers)

    def export_orders(self):
        """Export order data to a CSV file."""
        orders = self.db.get_all_orders()
        self._export_to_csv('orders', orders)
    
    def export_payments(self):
        """Export payment data (completed orders) to a CSV file."""
        payments = self.db.get_completed_orders()
        self._export_to_csv('payments', payments)

    def _export_to_csv(self, name, data):
        """Helper to write data to a CSV file."""
        if not data:
            return

        filepath = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            initialfile=f"{name}_{datetime.now().strftime('%Y%m%d')}.csv"
        )
        if not filepath:
            return

        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)
