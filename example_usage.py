#!/usr/bin/env python3
"""
Example usage script demonstrating Order Management System API.
This script shows how to use the modules programmatically.
"""
from database import Database
from notifications import NotificationManager, NotificationConfig
from validation import validate_email, validate_phone, validate_order_form

print("=" * 70)
print("Order Management System - Example Usage")
print("=" * 70)
print()

print("1. Initialize Database")
print("-" * 70)
db = Database('example_orders.db')
print("✓ Database initialized at 'example_orders.db'")
print()

print("2. Create Sample Orders")
print("-" * 70)
orders_data = [
    {
        'customer_name': 'Alice Johnson',
        'customer_email': 'alice@example.com',
        'customer_phone': '+1234567890',
        'item_description': 'Custom Widget Pro',
        'quantity': 3,
        'price': 99.99
    },
    {
        'customer_name': 'Bob Smith',
        'customer_email': 'bob@example.com',
        'customer_phone': '+9876543210',
        'item_description': 'Premium Gadget',
        'quantity': 1,
        'price': 299.99
    },
    {
        'customer_name': 'Carol White',
        'customer_email': 'carol@example.com',
        'customer_phone': None,
        'item_description': 'Standard Tool Set',
        'quantity': 5,
        'price': 49.99
    }
]

order_ids = []
for order_data in orders_data:
    order_id = db.create_order(**order_data)
    order_ids.append(order_id)
    print(f"✓ Created order #{order_id} for {order_data['customer_name']}")

print()
print("3. Retrieve and Display Orders")
print("-" * 70)
all_orders = db.get_all_orders()
print(f"Total orders in system: {len(all_orders)}")
print()
for order in all_orders:
    print(f"  Order #{order['id']}: {order['customer_name']}")
    print(f"    Item: {order['item_description']}")
    print(f"    Quantity: {order['quantity']} @ ${order['price']:.2f}")
    print(f"    Total: ${order['total_price']:.2f}")
    print(f"    Status: {order['status']}")
    print()

print("4. Validate Customer Data")
print("-" * 70)
test_emails = [
    'valid@example.com',
    'invalid.email',
    'another.valid@domain.co.uk'
]
for email in test_emails:
    result = "✓ Valid" if validate_email(email) else "✗ Invalid"
    print(f"  {email}: {result}")

print()
test_phones = [
    '+1234567890',
    '123-456-7890',
    '(555) 123-4567',
    'not-a-phone'
]
for phone in test_phones:
    result = "✓ Valid" if validate_phone(phone) else "✗ Invalid"
    print(f"  {phone}: {result}")

print()
print("5. Update Order Status")
print("-" * 70)
if order_ids:
    first_order_id = order_ids[0]
    print(f"Marking order #{first_order_id} as ready...")
    db.update_order_status(first_order_id, 'ready')
    updated_order = db.get_order(first_order_id)
    print(f"✓ Order #{first_order_id} status: {updated_order['status']}")
    print()

print("6. Configure Notifications")
print("-" * 70)
config = NotificationConfig(
    smtp_server='smtp.gmail.com',
    smtp_port=587,
    smtp_username='your-email@gmail.com',  # Replace with actual email
    smtp_password='your-app-password',      # Replace with actual password
    smtp_from='Order System <your-email@gmail.com>'
)
notification_manager = NotificationManager(config)
print("✓ Notification manager configured")
print(f"  SMTP Server: {config.smtp_server}:{config.smtp_port}")
print(f"  From: {config.smtp_from}")
print(f"  SMS Enabled: {config.sms_enabled}")
print()

print("7. Send Order Ready Notification (Demo)")
print("-" * 70)
if order_ids:
    order_to_notify = db.get_order(order_ids[0])
    print(f"Sending notification for order #{order_to_notify['id']}...")
    results = notification_manager.notify_order_ready(order_to_notify)
    print(f"  Email sent: {results['email_sent']}")
    print(f"  SMS sent: {results['sms_sent']}")
    print()
    if not results['email_sent']:
        print("  Note: Email not sent. Update SMTP credentials in code to enable.")
    print()

print("8. View Statistics")
print("-" * 70)
stats = db.get_statistics()
print(f"Total Orders: {stats['total_orders']}")
print(f"Pending Orders: {stats['pending_orders']}")
print(f"Ready Orders: {stats['ready_orders']}")
print(f"Completed Orders: {stats['completed_orders']}")
print(f"Total Revenue: ${stats['total_revenue']:.2f}")
print()

print("9. Filter Orders by Status")
print("-" * 70)
pending_orders = db.get_all_orders('pending')
ready_orders = db.get_all_orders('ready')
print(f"Pending orders: {len(pending_orders)}")
print(f"Ready orders: {len(ready_orders)}")
print()

print("10. Update Order Details")
print("-" * 70)
if order_ids and len(order_ids) > 1:
    order_id = order_ids[1]
    print(f"Updating order #{order_id}...")
    db.update_order(
        order_id,
        quantity=2,
        price=349.99
    )
    updated = db.get_order(order_id)
    print(f"✓ Order #{order_id} updated")
    print(f"  New quantity: {updated['quantity']}")
    print(f"  New price: ${updated['price']:.2f}")
    print(f"  New total: ${updated['total_price']:.2f}")
    print()

print("=" * 70)
print("Example completed successfully!")
print("=" * 70)
print()
print("Next steps:")
print("1. Review the created database: example_orders.db")
print("2. Run the GUI application: python3 app.py")
print("3. Explore the code in app.py, database.py, validation.py, notifications.py")
print("4. Configure SMTP credentials for email notifications")
print()
print("To clean up: rm example_orders.db")
print()
