# Usage Examples

## Common Scenarios

### Scenario 1: Receiving New Stock

When you receive a shipment from your supplier:

1. Go to the item detail page
2. Click "Adjust Stock"
3. Select transaction type: **Purchase/Restock**
4. Enter the quantity received (e.g., 50)
5. Enter reference info:
   - Reference Type: "Purchase Order"
   - Reference ID: "PO-2024-001"
6. Add notes: "Received from ABC Suppliers, Invoice #12345"
7. Click "Apply Adjustment"

**API equivalent:**
```bash
curl -X POST http://localhost:5000/api/inventory/1/adjust \
  -H "Content-Type: application/json" \
  -d '{
    "transaction_type": "purchase",
    "quantity": 50,
    "reference_type": "Purchase Order",
    "reference_id": "PO-2024-001",
    "notes": "Received from ABC Suppliers, Invoice #12345"
  }'
```

### Scenario 2: Consuming Inventory for Service Orders

When processing a laundry service order that uses detergent:

**Option A: Via Web Interface**
1. Navigate to the detergent item
2. Click "Adjust Stock"
3. Select transaction type: **Usage/Consumption**
4. Enter quantity used (e.g., 2.5 liters)
5. Reference Type: "Service Order"
6. Reference ID: "SO-2024-056"
7. Notes: "Customer: John Doe, 3 loads of laundry"
8. Click "Apply Adjustment"

**Option B: Via API (Recommended for automation)**
```bash
curl -X POST http://localhost:5000/api/inventory/1/consume \
  -H "Content-Type: application/json" \
  -d '{
    "quantity": 2.5,
    "reference_type": "service_order",
    "reference_id": "SO-2024-056",
    "notes": "Customer: John Doe, 3 loads of laundry"
  }'
```

### Scenario 3: Handling Damaged Inventory

When inventory is damaged or spoiled:

1. Go to the item detail page
2. Click "Adjust Stock"
3. Select transaction type: **Damage/Loss**
4. Enter the quantity lost (e.g., 5)
5. Add notes: "Bottle leaked during storage"
6. Click "Apply Adjustment"

### Scenario 4: Physical Inventory Count

When doing a physical inventory audit and finding discrepancies:

1. Go to the item detail page
2. Note the current system quantity
3. Count the physical inventory
4. If different, click "Adjust Stock"
5. Select transaction type: **Manual Adjustment**
6. Enter the difference (positive if more, will be calculated automatically)
7. Add notes: "Physical count audit - found 55 units instead of 50"
8. Click "Apply Adjustment"

**Tip:** You can also edit the item directly and change the quantity field. The system will create an adjustment transaction automatically.

### Scenario 5: Monitoring Low Stock Daily

Best practice for daily stock monitoring:

1. Start your day by visiting the Dashboard
2. Check the "Low Stock Alerts" card
3. If there are alerts, click through to see the detailed list
4. For each low-stock item:
   - Check if reorder is already in progress
   - If not, contact supplier or place order
   - Use the quick "Restock" button when you receive the shipment

**API equivalent for monitoring:**
```bash
# Get low-stock items
curl http://localhost:5000/api/inventory/low-stock

# Example automation script (pseudo-code)
low_stock_items = api.get_low_stock()
for item in low_stock_items:
    if not has_pending_order(item):
        create_purchase_order(item)
        send_alert_to_manager(item)
```

### Scenario 6: Setting Up a New Inventory Item

When adding a new product to your inventory:

1. Click "Add New Item" from the Inventory page
2. Fill in all fields:
   - **Name**: Be specific (e.g., "Tide HE Liquid - Mountain Spring 5L")
   - **Category**: Choose the most appropriate category
   - **Description**: Include important details (scent, size, special uses)
   - **Quantity**: Starting quantity
   - **Unit**: Choose appropriate measurement
   - **Reorder Level**: Calculate based on:
     - Average daily usage × lead time + safety stock
     - Example: If you use 5L/day and supplier takes 5 days: 5 × 5 + 10 = 35L
   - **Cost Per Unit**: For reporting and value tracking
   - **Supplier**: For quick reference when reordering
3. Click "Save Item"

### Scenario 7: Bulk Operations via API

For integrating with existing systems:

**Creating multiple items from a CSV:**
```python
import csv
import requests

with open('inventory.csv', 'r') as file:
    reader = csv.DictReader(file)
    for row in reader:
        item_data = {
            'name': row['name'],
            'category': row['category'],
            'quantity': float(row['quantity']),
            'unit': row['unit'],
            'reorder_level': float(row['reorder_level']),
            'cost_per_unit': float(row['cost_per_unit']) if row['cost_per_unit'] else None,
            'supplier': row['supplier']
        }
        response = requests.post('http://localhost:5000/api/inventory', json=item_data)
        print(f"Created: {row['name']} - Status: {response.status_code}")
```

**Automated consumption from order processing system:**
```python
def process_service_order(order_id, items_used):
    """
    items_used = [
        {'item_id': 1, 'quantity': 2.5},  # Detergent
        {'item_id': 3, 'quantity': 1.0},  # Fabric softener
        {'item_id': 6, 'quantity': 2}     # Dryer sheets (boxes)
    ]
    """
    for item in items_used:
        consume_data = {
            'quantity': item['quantity'],
            'reference_type': 'service_order',
            'reference_id': order_id,
            'notes': f'Automated consumption for order {order_id}'
        }
        response = requests.post(
            f'http://localhost:5000/api/inventory/{item["item_id"]}/consume',
            json=consume_data
        )
        if response.status_code != 200:
            print(f"Warning: Failed to consume item {item['item_id']}")
    
    # Check for low stock after consumption
    low_stock = requests.get('http://localhost:5000/api/inventory/low-stock').json()
    if low_stock:
        send_alert_email(low_stock)
```

### Scenario 8: Generating Reports

**Getting inventory valuation:**
```python
import requests

items = requests.get('http://localhost:5000/api/inventory').json()

total_value = 0
report = []

for item in items:
    if item['cost_per_unit']:
        item_value = item['quantity'] * item['cost_per_unit']
        total_value += item_value
        report.append({
            'name': item['name'],
            'quantity': item['quantity'],
            'unit': item['unit'],
            'cost_per_unit': item['cost_per_unit'],
            'total_value': item_value
        })

print(f"Total Inventory Value: ${total_value:.2f}")
for item in sorted(report, key=lambda x: x['total_value'], reverse=True):
    print(f"  {item['name']}: {item['quantity']} {item['unit']} = ${item['total_value']:.2f}")
```

## Best Practices

1. **Always use reference IDs**: Link every transaction to a source document (PO, SO, etc.)
2. **Add detailed notes**: Future you will thank you for the context
3. **Regular audits**: Conduct physical counts at least monthly
4. **Monitor alerts**: Check the dashboard daily for low-stock warnings
5. **Adjust reorder levels**: Review and adjust based on actual consumption patterns
6. **Automate consumption**: Integrate with your order management system to auto-deduct inventory
7. **Track suppliers**: Keep supplier info updated for quick reordering

## Troubleshooting

### Stock levels don't match physical count
- Use "Manual Adjustment" transaction type
- Add detailed notes about the discrepancy
- Investigate why (theft, spillage, measurement error, etc.)

### Low-stock alerts not appearing
- Check that reorder level is set correctly (not 0)
- Verify current quantity is actually below reorder level
- Refresh the dashboard page

### API returns 404 for item
- Verify the item ID is correct
- Check that item hasn't been deleted
- Use GET /api/inventory to list all items and their IDs

### Cannot delete an item
- Check if you have the correct permissions
- Deletion also removes all transaction history
- Consider setting quantity to 0 and archiving instead
