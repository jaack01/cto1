"""
Database module for order and service management with pricing and scheduling.
Implements backward-compatible APIs while adding advanced workflows.
"""
import sqlite3
import json
from datetime import datetime, timedelta
from contextlib import contextmanager


def _now_iso():
    return datetime.now().isoformat()


class Database:
    """SQLite database manager for orders and related data."""

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

    # --------------------------- Schema Management ---------------------------
    def init_database(self):
        """Initialize database schema and seed reference data."""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Core orders table (legacy + new fields)
            cursor.execute(
                '''
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
                '''
            )

            # New tables
            cursor.execute(
                '''
                CREATE TABLE IF NOT EXISTS customers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    email TEXT NOT NULL,
                    phone TEXT,
                    address TEXT,
                    created_at TEXT NOT NULL
                )
                '''
            )

            cursor.execute(
                '''
                CREATE TABLE IF NOT EXISTS service_types (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    rate REAL NOT NULL
                )
                '''
            )

            cursor.execute(
                '''
                CREATE TABLE IF NOT EXISTS garment_types (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    multiplier REAL NOT NULL
                )
                '''
            )

            # Add new columns to orders if missing (backward compatible migration)
            self._ensure_column(conn, 'orders', 'service_type', 'TEXT')
            self._ensure_column(conn, 'orders', 'items_json', 'TEXT')
            self._ensure_column(conn, 'orders', 'instructions', 'TEXT')
            self._ensure_column(conn, 'orders', 'scheduled_pickup', 'TEXT')
            self._ensure_column(conn, 'orders', 'scheduled_delivery', 'TEXT')
            self._ensure_column(conn, 'orders', 'customer_id', 'INTEGER')

            conn.commit()

            # Seed reference data if empty
            self._seed_reference_data(conn)
            conn.commit()

    def _ensure_column(self, conn, table, column, col_type):
        cur = conn.cursor()
        cur.execute(f"PRAGMA table_info({table})")
        cols = [row[1] for row in cur.fetchall()]
        if column not in cols:
            cur.execute(f"ALTER TABLE {table} ADD COLUMN {column} {col_type}")

    def _seed_reference_data(self, conn):
        cur = conn.cursor()
        # Service types
        cur.execute('SELECT COUNT(*) as c FROM service_types')
        if cur.fetchone()['c'] == 0:
            cur.executemany(
                'INSERT INTO service_types (id, name, rate) VALUES (?, ?, ?)',
                [
                    ('dry_cleaning', 'Dry Cleaning', 5.0),
                    ('wash_fold', 'Wash & Fold', 3.0),
                    ('alterations', 'Alterations', 8.0),
                ],
            )
        # Garment types
        cur.execute('SELECT COUNT(*) as c FROM garment_types')
        if cur.fetchone()['c'] == 0:
            cur.executemany(
                'INSERT INTO garment_types (id, name, multiplier) VALUES (?, ?, ?)',
                [
                    ('shirt', 'Shirt', 1.0),
                    ('pants', 'Pants', 1.2),
                    ('dress', 'Dress', 1.5),
                    ('jacket', 'Jacket', 1.8),
                ],
            )

    # ----------------------------- Reference Data ----------------------------
    def get_service_types(self):
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute('SELECT id, name, rate FROM service_types ORDER BY name')
            return [dict(r) for r in cur.fetchall()]

    def get_garment_types(self):
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute('SELECT id, name, multiplier FROM garment_types ORDER BY name')
            return [dict(r) for r in cur.fetchall()]

    # -------------------------------- Customers ------------------------------
    def create_or_get_customer(self, name, email, phone=None, address=None):
        """Create a customer if not existing; return customer id.
        Matching is done by email.
        """
        now = _now_iso()
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute('SELECT id FROM customers WHERE email = ?', (email,))
            row = cur.fetchone()
            if row:
                cust_id = row['id']
                # Optionally update recent info
                cur.execute(
                    'UPDATE customers SET name = ?, phone = ?, address = ? WHERE id = ?',
                    (name, phone, address, cust_id),
                )
                conn.commit()
                return cust_id
            cur.execute(
                'INSERT INTO customers (name, email, phone, address, created_at) VALUES (?, ?, ?, ?, ?)',
                (name, email, phone, address, now),
            )
            conn.commit()
            return cur.lastrowid

    def get_customer(self, customer_id):
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute('SELECT * FROM customers WHERE id = ?', (customer_id,))
            row = cur.fetchone()
            return dict(row) if row else None

    def list_customers(self):
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute('SELECT * FROM customers ORDER BY created_at DESC')
            return [dict(r) for r in cur.fetchall()]

    # --------------------------------- Orders --------------------------------
    def _calculate_items_total(self, service_type_id, items):
        """Calculate total price for given items and service type.
        items: list of dicts: {garment_type: str, quantity: int}
        """
        if not items:
            return 0.0
        with self.get_connection() as conn:
            cur = conn.cursor()
            # Get rate for service
            cur.execute('SELECT rate FROM service_types WHERE id = ?', (service_type_id,))
            row = cur.fetchone()
            rate = float(row['rate']) if row else 0.0
            # Build garment multipliers map
            cur.execute('SELECT id, multiplier FROM garment_types')
            gmap = {r['id']: float(r['multiplier']) for r in cur.fetchall()}
        total = 0.0
        for it in items:
            qty = int(it.get('quantity') or 0)
            gtype = it.get('garment_type')
            mult = gmap.get(gtype, 1.0)
            total += qty * rate * mult
        return round(total, 2)

    def _summarize_items(self, items):
        if not items:
            return ''
        # Summarize like "2x Shirt; 1x Pants"
        parts = []
        # We need garment name; fetch once
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute('SELECT id, name FROM garment_types')
            name_map = {r['id']: r['name'] for r in cur.fetchall()}
        for it in items:
            qty = int(it.get('quantity') or 0)
            if qty <= 0:
                continue
            gname = name_map.get(it.get('garment_type'), it.get('garment_type'))
            parts.append(f"{qty}x {gname}")
        return '; '.join(parts) if parts else ''

    def create_order(
        self,
        customer_name,
        customer_email,
        customer_phone,
        item_description,
        quantity,
        price,
        service_type=None,
        items=None,
        instructions=None,
        scheduled_pickup=None,
        scheduled_delivery=None,
        customer_id=None,
        address=None,
    ):
        """
        Create a new order. Backward-compatible with legacy signature.

        Args (legacy):
            customer_name: Customer name
            customer_email: Customer email
            customer_phone: Customer phone (optional)
            item_description: Description of ordered item
            quantity: Quantity ordered
            price: Price per item

        New optional args:
            service_type: Service type id
            items: List of item dicts {garment_type, quantity, instructions}
            instructions: Optional order-level notes
            scheduled_pickup: ISO timestamp string
            scheduled_delivery: ISO timestamp string
            customer_id: Optional existing customer id
            address: Optional customer address (used if creating customer)
        Returns:
            int: ID of created order
        """
        now = _now_iso()

        # If advanced items provided, compute pricing and summarize
        items_json = None
        svc = service_type
        total_price = None
        prc = float(price)
        qty_total = int(quantity)
        desc = item_description

        if items:
            # Normalize items list
            norm_items = []
            for it in items:
                if not it:
                    continue
                try:
                    q = int(it.get('quantity') or 0)
                except Exception:
                    q = 0
                if q <= 0:
                    continue
                norm_items.append({
                    'garment_type': it.get('garment_type'),
                    'quantity': q,
                    'instructions': it.get('instructions') or ''
                })
            items = norm_items
            items_json = json.dumps(items)
            if svc:
                total_price = self._calculate_items_total(svc, items)
                desc = self._summarize_items(items) or item_description
                qty_total = sum(int(it.get('quantity') or 0) for it in items) or qty_total
                # Set price to base service rate for display purposes
                with self.get_connection() as conn:
                    cur = conn.cursor()
                    cur.execute('SELECT rate FROM service_types WHERE id = ?', (svc,))
                    row = cur.fetchone()
                    if row:
                        prc = float(row['rate'])
            else:
                # If service type missing, fall back to legacy total computation
                total_price = qty_total * prc
        else:
            total_price = qty_total * prc

        # Ensure a customer_id exists
        cust_id = customer_id
        if not cust_id:
            cust_id = self.create_or_get_customer(customer_name, customer_email, customer_phone, address)

        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                '''
                INSERT INTO orders (
                    customer_name, customer_email, customer_phone,
                    item_description, quantity, price, total_price,
                    status, created_at, updated_at, ready_at,
                    service_type, items_json, instructions,
                    scheduled_pickup, scheduled_delivery, customer_id
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, 'pending', ?, ?, NULL, ?, ?, ?, ?, ?, ?)
                ''',
                (
                    customer_name,
                    customer_email,
                    customer_phone,
                    desc,
                    qty_total,
                    prc,
                    total_price,
                    now,
                    now,
                    svc,
                    items_json,
                    instructions,
                    scheduled_pickup,
                    scheduled_delivery,
                    cust_id,
                ),
            )
            conn.commit()
            return cursor.lastrowid

    def get_order(self, order_id):
        """Get order by ID.
        Returns dict or None.
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM orders WHERE id = ?', (order_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def get_all_orders(self, status=None, date_from=None, date_to=None, date_field='created_at'):
        """Get all orders, optionally filtered by status and date range.
        date_field can be 'created_at', 'scheduled_pickup', or 'scheduled_delivery'.
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            query = 'SELECT * FROM orders'
            clauses = []
            params = []
            if status:
                clauses.append('status = ?')
                params.append(status)
            if date_from:
                clauses.append(f"date({date_field}) >= ?")
                params.append(date_from)
            if date_to:
                clauses.append(f"date({date_field}) <= ?")
                params.append(date_to)
            if clauses:
                query += ' WHERE ' + ' AND '.join(clauses)
            query += ' ORDER BY created_at DESC'
            cursor.execute(query, tuple(params))
            return [dict(row) for row in cursor.fetchall()]

    def update_order_status(self, order_id, status):
        """Update order status and timestamps."""
        now = _now_iso()

        with self.get_connection() as conn:
            cursor = conn.cursor()

            if status == 'ready':
                cursor.execute(
                    '''
                    UPDATE orders
                    SET status = ?, updated_at = ?, ready_at = ?
                    WHERE id = ?
                    ''',
                    (status, now, now, order_id),
                )
            else:
                cursor.execute(
                    '''
                    UPDATE orders
                    SET status = ?, updated_at = ?
                    WHERE id = ?
                    ''',
                    (status, now, order_id),
                )

            conn.commit()
            return cursor.rowcount > 0

    def update_order(
        self,
        order_id,
        customer_name=None,
        customer_email=None,
        customer_phone=None,
        item_description=None,
        quantity=None,
        price=None,
        service_type=None,
        items=None,
        instructions=None,
        scheduled_pickup=None,
        scheduled_delivery=None,
        status=None,
    ):
        """Update order details. Backward-compatible with legacy fields."""
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
        if service_type is not None:
            updates['service_type'] = service_type
        if instructions is not None:
            updates['instructions'] = instructions
        if scheduled_pickup is not None:
            updates['scheduled_pickup'] = scheduled_pickup
        if scheduled_delivery is not None:
            updates['scheduled_delivery'] = scheduled_delivery
        if status is not None:
            updates['status'] = status
        if items is not None:
            # Recalculate price based on items and service type (fallback to existing)
            norm_items = []
            for it in items:
                if not it:
                    continue
                try:
                    q = int(it.get('quantity') or 0)
                except Exception:
                    q = 0
                if q <= 0:
                    continue
                norm_items.append({
                    'garment_type': it.get('garment_type'),
                    'quantity': q,
                    'instructions': it.get('instructions') or ''
                })
            items = norm_items
            updates['items_json'] = json.dumps(items)
            if service_type is None:
                service_type = order.get('service_type')
            if service_type:
                updates['total_price'] = self._calculate_items_total(service_type, items)
                updates['quantity'] = sum(it.get('quantity', 0) for it in items)
                # If price not set explicitly, set to base rate
                if 'price' not in updates:
                    with self.get_connection() as conn:
                        cur = conn.cursor()
                        cur.execute('SELECT rate FROM service_types WHERE id = ?', (service_type,))
                        row = cur.fetchone()
                        if row:
                            updates['price'] = float(row['rate'])
            else:
                # Fall back to quantity * price
                qty = updates.get('quantity', order['quantity'])
                prc = updates.get('price', order['price'])
                updates['total_price'] = qty * prc

        # If items didn't change but price/quantity changed, recompute total
        if 'items_json' not in updates and ('quantity' in updates or 'price' in updates):
            qty = updates.get('quantity', order['quantity'])
            prc = updates.get('price', order['price'])
            updates['total_price'] = qty * prc

        updates['updated_at'] = _now_iso()

        set_clause = ', '.join([f"{k} = ?" for k in updates.keys()])
        values = list(updates.values()) + [order_id]

        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f'UPDATE orders SET {set_clause} WHERE id = ?', values)
            conn.commit()
            return cursor.rowcount > 0

    def delete_order(self, order_id):
        """Delete an order."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM orders WHERE id = ?', (order_id,))
            conn.commit()
            return cursor.rowcount > 0

    # ------------------------------ Analytics --------------------------------
    def get_statistics(self):
        """Get order statistics."""
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
                'total_revenue': total_revenue,
            }

    def get_daily_revenue(self):
        """Get total revenue for the current day."""
        today = datetime.now().strftime('%Y-%m-%d')
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                'SELECT COALESCE(SUM(total_price), 0) as total FROM orders WHERE date(created_at) = ?',
                (today,),
            )
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
            cursor.execute(
                'SELECT COUNT(*) as count FROM customers WHERE created_at >= ?', (yesterday,)
            )
            return cursor.fetchone()['count']

    def get_popular_items(self, limit=5):
        """Get the most popular items by description (legacy metric)."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                '''
                SELECT item_description as item, COUNT(*) as orders
                FROM orders
                GROUP BY item_description
                ORDER BY orders DESC
                LIMIT ?
                ''',
                (limit,),
            )
            return [dict(row) for row in cursor.fetchall()]

    def get_sales_report(self, start_date, end_date):
        """Get a sales report for a given date range."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            query = 'SELECT * FROM orders WHERE date(created_at) BETWEEN ? AND ?'
            cursor.execute(query, (start_date, end_date))
            orders = [dict(row) for row in cursor.fetchall()]

            total_revenue = sum(o['total_price'] for o in orders)
            completed_orders = sum(1 for o in orders if o['status'] == 'completed')
            pending_orders = sum(1 for o in orders if o['status'] == 'pending')

            return {
                'total_orders': len(orders),
                'total_revenue': total_revenue,
                'completed_orders': completed_orders,
                'pending_orders': pending_orders,
            }

    def get_all_customers(self):
        """Get all unique customers (legacy export)."""
        # For backward compatibility, return distinct from orders if customers table is unused
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                'SELECT DISTINCT customer_name, customer_email, customer_phone FROM orders'
            )
            return [dict(row) for row in cursor.fetchall()]

    def get_completed_orders(self):
        """Get all completed orders."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM orders WHERE status = 'completed'")
            return [dict(row) for row in cursor.fetchall()]
