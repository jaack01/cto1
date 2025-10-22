import sqlite3
from sqlite3 import Error

def create_connection(db_file):
    """Create a database connection to the SQLite database specified by db_file."""
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)
    return conn

def create_table(conn, create_table_sql):
    """Create a table from the create_table_sql statement."""
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)

def initialize_database(db_file):
    """Create a database connection and create tables."""
    sql_create_customers_table = """
    CREATE TABLE IF NOT EXISTS customers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        phone TEXT,
        email TEXT,
        address TEXT
    );
    """

    sql_create_orders_table = """
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER NOT NULL,
        order_date TEXT NOT NULL,
        due_date TEXT NOT NULL,
        status TEXT NOT NULL,
        total_amount REAL,
        FOREIGN KEY (customer_id) REFERENCES customers (id)
    );
    """

    sql_create_services_table = """
    CREATE TABLE IF NOT EXISTS services (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT,
        price REAL NOT NULL
    );
    """

    sql_create_order_items_table = """
    CREATE TABLE IF NOT EXISTS order_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER NOT NULL,
        service_id INTEGER NOT NULL,
        quantity INTEGER NOT NULL,
        price REAL NOT NULL,
        FOREIGN KEY (order_id) REFERENCES orders (id),
        FOREIGN KEY (service_id) REFERENCES services (id)
    );
    """

    sql_create_payments_table = """
    CREATE TABLE IF NOT EXISTS payments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER NOT NULL,
        payment_date TEXT NOT NULL,
        amount REAL NOT NULL,
        payment_method TEXT,
        FOREIGN KEY (order_id) REFERENCES orders (id)
    );
    """

    sql_create_inventory_table = """
    CREATE TABLE IF NOT EXISTS inventory (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        item_name TEXT NOT NULL,
        quantity INTEGER NOT NULL,
        supplier TEXT
    );
    """

    sql_create_notification_settings_table = """
    CREATE TABLE IF NOT EXISTS notification_settings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER NOT NULL,
        notification_type TEXT NOT NULL,
        is_enabled BOOLEAN NOT NULL DEFAULT 1,
        FOREIGN KEY (customer_id) REFERENCES customers (id)
    );
    """

    conn = create_connection(db_file)
    if conn is not None:
        create_table(conn, sql_create_customers_table)
        create_table(conn, sql_create_orders_table)
        create_table(conn, sql_create_services_table)
        create_table(conn, sql_create_order_items_table)
        create_table(conn, sql_create_payments_table)
        create_table(conn, sql_create_inventory_table)
        create_table(conn, sql_create_notification_settings_table)
        conn.close()
    else:
        print("Error! cannot create the database connection.")

def execute_query(db_file, query, params=()):
    """Execute a single query."""
    conn = create_connection(db_file)
    try:
        c = conn.cursor()
        c.execute(query, params)
        conn.commit()
        return c.lastrowid
    except Error as e:
        print(e)
    finally:
        if conn:
            conn.close()

def fetch_query(db_file, query, params=()):
    """Execute a fetch query and return results."""
    conn = create_connection(db_file)
    try:
        c = conn.cursor()
        c.execute(query, params)
        return c.fetchall()
    except Error as e:
        print(e)
    finally:
        if conn:
            conn.close()

# CRUD for Customers
def create_customer(db_file, customer):
    sql = ''' INSERT INTO customers(name,phone,email,address)
              VALUES(?,?,?,?) '''
    return execute_query(db_file, sql, customer)

def get_customer(db_file, customer_id):
    sql = "SELECT * FROM customers WHERE id = ?"
    return fetch_query(db_file, sql, (customer_id,))

def get_all_customers(db_file):
    sql = "SELECT * FROM customers"
    return fetch_query(db_file, sql)

def update_customer(db_file, customer):
    sql = ''' UPDATE customers
              SET name = ? ,
                  phone = ? ,
                  email = ? ,
                  address = ?
              WHERE id = ?'''
    return execute_query(db_file, sql, customer)

def delete_customer(db_file, customer_id):
    sql = 'DELETE FROM customers WHERE id = ?'
    return execute_query(db_file, sql, (customer_id,))

# CRUD for Orders
def create_order(db_file, order):
    sql = ''' INSERT INTO orders(customer_id, order_date, due_date, status, total_amount)
              VALUES(?,?,?,?,?) '''
    return execute_query(db_file, sql, order)

def get_order(db_file, order_id):
    sql = "SELECT * FROM orders WHERE id = ?"
    return fetch_query(db_file, sql, (order_id,))

def get_all_orders(db_file):
    sql = "SELECT * FROM orders"
    return fetch_query(db_file, sql)

def update_order(db_file, order):
    sql = ''' UPDATE orders
              SET customer_id = ?,
                  order_date = ?,
                  due_date = ?,
                  status = ?,
                  total_amount = ?
              WHERE id = ?'''
    return execute_query(db_file, sql, order)

def delete_order(db_file, order_id):
    sql = 'DELETE FROM orders WHERE id = ?'
    return execute_query(db_file, sql, (order_id,))

# CRUD for Services
def create_service(db_file, service):
    sql = ''' INSERT INTO services(name, description, price)
              VALUES(?,?,?) '''
    return execute_query(db_file, sql, service)

def get_service(db_file, service_id):
    sql = "SELECT * FROM services WHERE id = ?"
    return fetch_query(db_file, sql, (service_id,))

def get_all_services(db_file):
    sql = "SELECT * FROM services"
    return fetch_query(db_file, sql)

def update_service(db_file, service):
    sql = ''' UPDATE services
              SET name = ?,
                  description = ?,
                  price = ?
              WHERE id = ?'''
    return execute_query(db_file, sql, service)

def delete_service(db_file, service_id):
    sql = 'DELETE FROM services WHERE id = ?'
    return execute_query(db_file, sql, (service_id,))

# CRUD for Order Items
def create_order_item(db_file, order_item):
    sql = ''' INSERT INTO order_items(order_id, service_id, quantity, price)
              VALUES(?,?,?,?) '''
    return execute_query(db_file, sql, order_item)

def get_order_items(db_file, order_id):
    sql = "SELECT * FROM order_items WHERE order_id = ?"
    return fetch_query(db_file, sql, (order_id,))

# CRUD for Payments
def create_payment(db_file, payment):
    sql = ''' INSERT INTO payments(order_id, payment_date, amount, payment_method)
              VALUES(?,?,?,?) '''
    return execute_query(db_file, sql, payment)

def get_payments_for_order(db_file, order_id):
    sql = "SELECT * FROM payments WHERE order_id = ?"
    return fetch_query(db_file, sql, (order_id,))

# CRUD for Inventory
def create_inventory_item(db_file, item):
    sql = ''' INSERT INTO inventory(item_name, quantity, supplier)
              VALUES(?,?,?) '''
    return execute_query(db_file, sql, item)

def get_inventory_item(db_file, item_id):
    sql = "SELECT * FROM inventory WHERE id = ?"
    return fetch_query(db_file, sql, (item_id,))

def get_all_inventory_items(db_file):
    sql = "SELECT * FROM inventory"
    return fetch_query(db_file, sql)

def update_inventory_item(db_file, item):
    sql = ''' UPDATE inventory
              SET item_name = ?,
                  quantity = ?,
                  supplier = ?
              WHERE id = ?'''
    return execute_query(db_file, sql, item)

def delete_inventory_item(db_file, item_id):
    sql = 'DELETE FROM inventory WHERE id = ?'
    return execute_query(db_file, sql, (item_id,))

