#!/usr/bin/env python3
"""
Test script for Order Management System functionality.
Tests database operations, validation, and notification components.
"""
import os
import sys
from datetime import datetime

print("=" * 60)
print("Order Management System - Functionality Tests")
print("=" * 60)
print()

print("1. Testing Database Module...")
print("-" * 60)
try:
    from database import Database
    
    test_db = Database('test_orders.db')
    
    print("✓ Database initialized")
    
    order_id = test_db.create_order(
        customer_name="John Doe",
        customer_email="john@example.com",
        customer_phone="+1234567890",
        item_description="Test Widget",
        quantity=2,
        price=49.99
    )
    print(f"✓ Created test order #{order_id}")
    
    order = test_db.get_order(order_id)
    assert order is not None
    assert order['customer_name'] == "John Doe"
    assert order['quantity'] == 2
    assert order['total_price'] == 99.98
    print(f"✓ Retrieved order: {order['customer_name']} - ${order['total_price']:.2f}")
    
    all_orders = test_db.get_all_orders()
    assert len(all_orders) > 0
    print(f"✓ Retrieved all orders: {len(all_orders)} order(s)")
    
    updated = test_db.update_order_status(order_id, 'ready')
    assert updated
    order = test_db.get_order(order_id)
    assert order['status'] == 'ready'
    print(f"✓ Updated order status to: {order['status']}")
    
    stats = test_db.get_statistics()
    print(f"✓ Statistics: {stats['total_orders']} orders, ${stats['total_revenue']:.2f} revenue")
    
    deleted = test_db.delete_order(order_id)
    assert deleted
    print(f"✓ Deleted test order #{order_id}")
    
    os.remove('test_orders.db')
    print("✓ Cleanup completed")
    
    print("\n✅ Database Module: ALL TESTS PASSED")
    
except Exception as e:
    print(f"\n❌ Database Module Error: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()
print("2. Testing Validation Module...")
print("-" * 60)
try:
    import re
    from validation import (
        validate_email, validate_phone, validate_required,
        validate_positive_number, validate_non_negative_number
    )
    
    assert validate_email("test@example.com") == True
    assert validate_email("invalid.email") == False
    assert validate_email("") == False
    print("✓ Email validation working correctly")
    
    assert validate_phone("+1234567890") == True
    assert validate_phone("123-456-7890") == True
    assert validate_phone("invalid") == False
    print("✓ Phone validation working correctly")
    
    assert validate_positive_number("10.5", "Test") == True
    assert validate_positive_number("-5", "Test") == False
    assert validate_positive_number("0", "Test") == False
    print("✓ Positive number validation working correctly")
    
    assert validate_non_negative_number("0", "Test") == True
    assert validate_non_negative_number("10", "Test") == True
    assert validate_non_negative_number("-1", "Test") == False
    print("✓ Non-negative number validation working correctly")
    
    print("\n✅ Validation Module: ALL TESTS PASSED")
    
except Exception as e:
    print(f"\n❌ Validation Module Error: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()
print("3. Testing Notification Module...")
print("-" * 60)
try:
    from notifications import NotificationConfig, NotificationManager
    
    config = NotificationConfig(
        smtp_server='smtp.gmail.com',
        smtp_port=587,
        smtp_username='test@example.com',
        smtp_password='test_password'
    )
    print("✓ Notification config created")
    
    notification_manager = NotificationManager(config)
    print("✓ Notification manager initialized")
    
    test_order = {
        'id': 1,
        'customer_name': 'John Doe',
        'customer_email': 'john@example.com',
        'customer_phone': '+1234567890',
        'item_description': 'Test Widget',
        'quantity': 2,
        'price': 49.99,
        'total_price': 99.98,
        'status': 'ready'
    }
    
    results = notification_manager.notify_order_ready(test_order)
    print(f"✓ Notification attempt results: Email={results['email_sent']}, SMS={results['sms_sent']}")
    
    notification_manager.update_config(
        smtp_username='new_user@example.com',
        sms_enabled=True
    )
    print("✓ Configuration updated successfully")
    
    print("\n✅ Notification Module: ALL TESTS PASSED")
    
except Exception as e:
    print(f"\n❌ Notification Module Error: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()
print("=" * 60)
print("🎉 ALL FUNCTIONALITY TESTS PASSED!")
print("=" * 60)
print()
print("Next steps:")
print("1. Run the application: python3 app.py")
print("2. Configure SMTP settings in File > Settings")
print("3. Create and manage orders")
print("4. Test notifications by marking orders as ready")
print()
print("Note: The GUI application requires a display environment.")
print("      Run on a system with X11/Wayland for full functionality.")
print()
