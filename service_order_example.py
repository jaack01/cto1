"""
Example: Integrating Inventory Management with Service Order Processing

This script demonstrates how to integrate the inventory system with a
service order management system to automatically track inventory consumption.
"""

from app import app
from models import db, InventoryItem, InventoryTransaction, ServiceOrder, utcnow


def create_service_order(order_number, customer_name, service_type):
    """Create a new service order"""
    with app.app_context():
        order = ServiceOrder(
            order_number=order_number,
            customer_name=customer_name,
            service_type=service_type,
            status='pending'
        )
        db.session.add(order)
        db.session.commit()
        print(f"Created service order: {order_number}")
        return order.id


def consume_inventory_for_order(order_id, order_number, items_consumed):
    """
    Consume inventory items for a service order.
    
    items_consumed = [
        {'name': 'Tide Liquid Detergent', 'quantity': 2.5},
        {'name': 'Downy Fabric Softener', 'quantity': 1.0},
    ]
    """
    with app.app_context():
        for item_data in items_consumed:
            item = InventoryItem.query.filter_by(name=item_data['name']).first()
            
            if not item:
                print(f"Warning: Item '{item_data['name']}' not found in inventory")
                continue
            
            if item.quantity < item_data['quantity']:
                print(f"Warning: Insufficient stock for '{item.name}'. "
                      f"Available: {item.quantity} {item.unit}, "
                      f"Requested: {item_data['quantity']} {item.unit}")
                continue
            
            item.quantity -= item_data['quantity']
            item.updated_at = utcnow()
            
            transaction = InventoryTransaction(
                item=item,
                transaction_type='usage',
                quantity=-item_data['quantity'],
                reference_type='service_order',
                reference_id=order_number,
                notes=f"Consumed for service order {order_number}"
            )
            
            db.session.add(transaction)
            
            print(f"Consumed: {item_data['quantity']} {item.unit} of {item.name}")
            
            if item.is_low_stock():
                print(f"  ⚠️  LOW STOCK ALERT: {item.name} is at {item.quantity} {item.unit} "
                      f"(reorder level: {item.reorder_level} {item.unit})")
        
        db.session.commit()


def complete_service_order(order_number):
    """Mark a service order as completed"""
    with app.app_context():
        order = ServiceOrder.query.filter_by(order_number=order_number).first()
        if order:
            order.status = 'completed'
            order.completed_at = utcnow()
            db.session.commit()
            print(f"Completed service order: {order_number}")


def check_low_stock_items():
    """Check and display all low-stock items"""
    with app.app_context():
        low_stock_items = InventoryItem.query.filter(
            InventoryItem.quantity <= InventoryItem.reorder_level
        ).all()
        
        if low_stock_items:
            print("\n🚨 LOW STOCK ALERTS:")
            print("=" * 70)
            for item in low_stock_items:
                print(f"  • {item.name}")
                print(f"    Current: {item.quantity} {item.unit} | "
                      f"Reorder Level: {item.reorder_level} {item.unit}")
                if item.supplier:
                    print(f"    Supplier: {item.supplier}")
                print()
        else:
            print("\n✓ All items are adequately stocked!")


def process_laundry_order_example():
    """Example: Process a typical laundry service order"""
    
    print("\n" + "=" * 70)
    print("EXAMPLE: Processing a Laundry Service Order")
    print("=" * 70)
    
    # Step 1: Create service order
    order_number = "SO-2024-100"
    customer_name = "John Doe"
    service_type = "Laundry - 3 Loads"
    
    print(f"\n1. Creating service order for {customer_name}...")
    order_id = create_service_order(order_number, customer_name, service_type)
    
    # Step 2: Define items consumed (based on 3 loads of laundry)
    print(f"\n2. Processing {service_type}...")
    items_consumed = [
        {'name': 'Tide Liquid Detergent', 'quantity': 0.75},  # 0.25L per load
        {'name': 'Downy Fabric Softener', 'quantity': 0.45},   # 0.15L per load
        {'name': 'Dryer Sheets', 'quantity': 0.015},           # ~3 sheets from box
    ]
    
    # Step 3: Consume inventory
    print("\n3. Consuming inventory for this order...")
    consume_inventory_for_order(order_id, order_number, items_consumed)
    
    # Step 4: Complete the order
    print(f"\n4. Marking order as completed...")
    complete_service_order(order_number)
    
    # Step 5: Check for low stock
    print("\n5. Checking inventory status...")
    check_low_stock_items()
    
    print("\n" + "=" * 70)
    print("Order processing complete!")
    print("=" * 70 + "\n")


def process_dry_cleaning_order_example():
    """Example: Process a dry cleaning order"""
    
    print("\n" + "=" * 70)
    print("EXAMPLE: Processing a Dry Cleaning Order")
    print("=" * 70)
    
    order_number = "SO-2024-101"
    customer_name = "Jane Smith"
    service_type = "Dry Cleaning - 5 Items"
    
    print(f"\n1. Creating service order for {customer_name}...")
    order_id = create_service_order(order_number, customer_name, service_type)
    
    print(f"\n2. Processing {service_type}...")
    items_consumed = [
        {'name': 'Spot Treatment Spray', 'quantity': 0.05},  # Small amount for stains
        {'name': 'Plastic Garment Bags', 'quantity': 5},     # One per item
        {'name': 'Clothes Hangers', 'quantity': 5},          # One per item
    ]
    
    print("\n3. Consuming inventory for this order...")
    consume_inventory_for_order(order_id, order_number, items_consumed)
    
    print(f"\n4. Marking order as completed...")
    complete_service_order(order_number)
    
    print("\n5. Checking inventory status...")
    check_low_stock_items()
    
    print("\n" + "=" * 70)
    print("Order processing complete!")
    print("=" * 70 + "\n")


if __name__ == '__main__':
    print("\n" + "=" * 70)
    print("SERVICE ORDER & INVENTORY INTEGRATION DEMO")
    print("=" * 70)
    
    # Example 1: Laundry Order
    process_laundry_order_example()
    
    # Example 2: Dry Cleaning Order
    process_dry_cleaning_order_example()
    
    print("\nNote: These examples demonstrate how to integrate inventory tracking")
    print("with your service order management system. Adapt the consumption")
    print("quantities based on your actual usage patterns.")
