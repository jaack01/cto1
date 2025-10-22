"""
Database module for order management.
"""
import sqlite3
import json
from datetime import datetime, timedelta
from contextlib import contextmanager


class Database:
    """SQLite database manager for orders."""
    
    def __init__(self, db_path='orders.db'):
        self.db_path = db_path
        self.init_database()
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()
    
    def init_database(self):
        """Initialize database schema."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS orders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    customer_name TEXT NOT NULL,
                    customer_email TEXT NOT NULL,
                    customer_phone TEXT,
                    item_description TEXT NOT NULL,
                    quantity INTEGER NOT NULL,
                    price REAL NOT NULL,
                    total_price REAL NOT NULL,
                    status TEXT DEFAULT 'pending',
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    ready_at TEXT
                )
            ''')
            conn.commit()
    
    def create_order(self, customer_name, customer_email, customer_phone,
                    item_description, quantity, price):
        """
        Create a new order.
        
        Args:
            customer_name: Customer name
            customer_email: Customer email
            customer_phone: Customer phone (optional)
            item_description: Description of ordered item
            quantity: Quantity ordered
            price: Price per item
            
        Returns:
            int: ID of created order
        """
        total_price = quantity * price
        now = datetime.now().isoformat()
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO orders (
                    customer_name, customer_email, customer_phone,
                    item_description, quantity, price, total_price,
                    status, created_at, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, 'pending', ?, ?)
            ''', (customer_name, customer_email, customer_phone,
                  item_description, quantity, price, total_price,
                  now, now))
            conn.commit()
            return cursor.lastrowid
    
    def get_order(self, order_id):
        """
        Get order by ID.
        
        Args:
            order_id: Order ID
            
        Returns:
            dict: Order data or None if not found
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM orders WHERE id = ?', (order_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def get_all_orders(self, status=None):
        """
        Get all orders, optionally filtered by status.
        
        Args:
            status: Filter by status (optional)
            
        Returns:
            list: List of order dictionaries
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if status:
                cursor.execute('SELECT * FROM orders WHERE status = ? ORDER BY created_at DESC', (status,))
            else:
                cursor.execute('SELECT * FROM orders ORDER BY created_at DESC')
            return [dict(row) for row in cursor.fetchall()]
    
    def update_order_status(self, order_id, status):
        """
        Update order status.
        
        Args:
            order_id: Order ID
            status: New status
            
        Returns:
            bool: True if updated successfully
        """
        now = datetime.now().isoformat()
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            if status == 'ready':
                cursor.execute('''
                    UPDATE orders 
                    SET status = ?, updated_at = ?, ready_at = ?
                    WHERE id = ?
                ''', (status, now, now, order_id))
            else:
                cursor.execute('''
                    UPDATE orders 
                    SET status = ?, updated_at = ?
                    WHERE id = ?
                ''', (status, now, order_id))
            
            conn.commit()
            return cursor.rowcount > 0
    
    def update_order(self, order_id, customer_name=None, customer_email=None,
                    customer_phone=None, item_description=None, quantity=None,
                    price=None):
        """
        Update order details.
        
        Args:
            order_id: Order ID
            customer_name: Customer name (optional)
            customer_email: Customer email (optional)
            customer_phone: Customer phone (optional)
            item_description: Item description (optional)
            quantity: Quantity (optional)
            price: Price per item (optional)
            
        Returns:
            bool: True if updated successfully
        """
        order = self.get_order(order_id)
        if not order:
            return False
        
        updates = {}
        if customer_name is not None:
            updates['customer_name'] = customer_name
        if customer_email is not None:
            updates['customer_email'] = customer_email
        if customer_phone is not None:
            updates['customer_phone'] = customer_phone
        if item_description is not None:
            updates['item_description'] = item_description
        if quantity is not None:
            updates['quantity'] = quantity
        if price is not None:
            updates['price'] = price
        
        if 'quantity' in updates or 'price' in updates:
            qty = updates.get('quantity', order['quantity'])
            prc = updates.get('price', order['price'])
            updates['total_price'] = qty * prc
        
        updates['updated_at'] = datetime.now().isoformat()
        
        set_clause = ', '.join([f"{k} = ?" for k in updates.keys()])
        values = list(updates.values()) + [order_id]
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f'UPDATE orders SET {set_clause} WHERE id = ?', values)
            conn.commit()
            return cursor.rowcount > 0
    
    def delete_order(self, order_id):
        """
        Delete an order.
        
        Args:
            order_id: Order ID
            
        Returns:
            bool: True if deleted successfully
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM orders WHERE id = ?', (order_id,))
            conn.commit()
            return cursor.rowcount > 0
    
    def get_statistics(self):
        """
        Get order statistics.
        
        Returns:
            dict: Statistics including counts and totals
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('SELECT COUNT(*) as count FROM orders')
            total_orders = cursor.fetchone()['count']
            
            cursor.execute("SELECT COUNT(*) as count FROM orders WHERE status = 'pending'")
            pending_orders = cursor.fetchone()['count']
            
            cursor.execute("SELECT COUNT(*) as count FROM orders WHERE status = 'ready'")
            ready_orders = cursor.fetchone()['count']
            
            cursor.execute("SELECT COUNT(*) as count FROM orders WHERE status = 'completed'")
            completed_orders = cursor.fetchone()['count']
            
            cursor.execute('SELECT COALESCE(SUM(total_price), 0) as total FROM orders')
            total_revenue = cursor.fetchone()['total']
            
            return {
                'total_orders': total_orders,
                'pending_orders': pending_orders,
                'ready_orders': ready_orders,
                'completed_orders': completed_orders,
                'total_revenue': total_revenue
            }

    def get_daily_revenue(self):
        """Get total revenue for the current day."""
        today = datetime.now().strftime('%Y-%m-%d')
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COALESCE(SUM(total_price), 0) as total FROM orders WHERE date(created_at) = ?", (today,))
            return cursor.fetchone()['total']

    def get_pending_orders_count(self):
        """Get the count of pending orders."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) as count FROM orders WHERE status = 'pending'")
            return cursor.fetchone()['count']

    def get_new_customers_count(self):
        """Get the count of new customers in the last 24 hours."""
        yesterday = (datetime.now() - timedelta(days=1)).isoformat()
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(DISTINCT customer_email) as count FROM orders WHERE created_at >= ?", (yesterday,))
            return cursor.fetchone()['count']

    def get_popular_items(self, limit=5):
        """Get the most popular items."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT item_description as item, COUNT(*) as orders
                FROM orders
                GROUP BY item_description
                ORDER BY orders DESC
                LIMIT ?
            """, (limit,))
            return [dict(row) for row in cursor.fetchall()]

    def get_sales_report(self, start_date, end_date):
        """Get a sales report for a given date range."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            query = "SELECT * FROM orders WHERE date(created_at) BETWEEN ? AND ?"
            cursor.execute(query, (start_date, end_date))
            orders = [dict(row) for row in cursor.fetchall()]

            total_revenue = sum(o['total_price'] for o in orders)
            completed_orders = sum(1 for o in orders if o['status'] == 'completed')
            pending_orders = sum(1 for o in orders if o['status'] == 'pending')

            return {
                'total_orders': len(orders),
                'total_revenue': total_revenue,
                'completed_orders': completed_orders,
                'pending_orders': pending_orders
            }

    def get_all_customers(self):
        """Get all unique customers."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT DISTINCT customer_name, customer_email, customer_phone FROM orders")
            return [dict(row) for row in cursor.fetchall()]

    def get_completed_orders(self):
        """Get all completed orders."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM orders WHERE status = 'completed'")
            return [dict(row) for row in cursor.fetchall()]
