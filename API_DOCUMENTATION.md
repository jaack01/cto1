# Inventory Management API Documentation

## Base URL
```
http://localhost:5000/api
```

## Response Format
All API endpoints return JSON data with appropriate HTTP status codes.

## Endpoints

### 1. List All Inventory Items

**GET** `/inventory`

Returns a list of all inventory items in the system.

**Response**
```json
[
  {
    "id": 1,
    "name": "Tide Liquid Detergent",
    "category": "detergent",
    "description": "High-efficiency liquid laundry detergent",
    "quantity": 45.0,
    "unit": "liters",
    "reorder_level": 20.0,
    "cost_per_unit": 12.50,
    "supplier": "P&G Distributors",
    "is_low_stock": false,
    "stock_percentage": 225.0,
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z"
  }
]
```

**Status Codes**
- `200 OK`: Success

---

### 2. Get Single Inventory Item

**GET** `/inventory/:id`

Returns details for a specific inventory item.

**Parameters**
- `id` (path): Integer - Inventory item ID

**Response**
```json
{
  "id": 1,
  "name": "Tide Liquid Detergent",
  "category": "detergent",
  "description": "High-efficiency liquid laundry detergent",
  "quantity": 45.0,
  "unit": "liters",
  "reorder_level": 20.0,
  "cost_per_unit": 12.50,
  "supplier": "P&G Distributors",
  "is_low_stock": false,
  "stock_percentage": 225.0,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

**Status Codes**
- `200 OK`: Success
- `404 Not Found`: Item does not exist

---

### 3. Create Inventory Item

**POST** `/inventory`

Creates a new inventory item.

**Request Body**
```json
{
  "name": "New Detergent",
  "category": "detergent",
  "description": "Optional description",
  "quantity": 100.0,
  "unit": "liters",
  "reorder_level": 25.0,
  "cost_per_unit": 15.00,
  "supplier": "ABC Suppliers"
}
```

**Required Fields**
- `name`: String
- `category`: String (detergent, softener, bleach, stain_remover, supplies, packaging, other)
- `quantity`: Float
- `unit`: String (kg, liters, pieces, bottles, boxes, packs)
- `reorder_level`: Float

**Optional Fields**
- `description`: String
- `cost_per_unit`: Float
- `supplier`: String

**Response**
```json
{
  "id": 11,
  "name": "New Detergent",
  ...
}
```

**Status Codes**
- `201 Created`: Item created successfully
- `400 Bad Request`: Invalid data

**Note**: Creating an item automatically creates an `initial` transaction for the starting quantity.

---

### 4. Update Inventory Item

**PUT** `/inventory/:id`

Updates an existing inventory item. Can update any fields.

**Parameters**
- `id` (path): Integer - Inventory item ID

**Request Body**
```json
{
  "name": "Updated Name",
  "quantity": 150.0,
  "reorder_level": 30.0
}
```

**Response**
```json
{
  "id": 1,
  "name": "Updated Name",
  "quantity": 150.0,
  ...
}
```

**Status Codes**
- `200 OK`: Success
- `404 Not Found`: Item does not exist
- `400 Bad Request`: Invalid data

**Note**: If quantity is changed, an `adjustment` transaction is automatically created.

---

### 5. Delete Inventory Item

**DELETE** `/inventory/:id`

Deletes an inventory item and all its transaction history.

**Parameters**
- `id` (path): Integer - Inventory item ID

**Response**
No content

**Status Codes**
- `204 No Content`: Successfully deleted
- `404 Not Found`: Item does not exist

---

### 6. Adjust Inventory

**POST** `/inventory/:id/adjust`

Adjusts the inventory quantity with a specific transaction type.

**Parameters**
- `id` (path): Integer - Inventory item ID

**Request Body**
```json
{
  "transaction_type": "purchase",
  "quantity": 50.0,
  "reference_type": "Purchase Order",
  "reference_id": "PO-2024-001",
  "notes": "Received shipment from supplier"
}
```

**Transaction Types**
- `purchase`: Adds to inventory
- `usage`: Deducts from inventory
- `adjustment`: Manual adjustment (can add or remove based on sign)
- `damage`: Deducts from inventory
- `return`: Deducts from inventory (return to supplier)

**Required Fields**
- `transaction_type`: String
- `quantity`: Float (always positive; direction determined by transaction type)

**Optional Fields**
- `reference_type`: String
- `reference_id`: String
- `notes`: String

**Response**
```json
{
  "id": 1,
  "quantity": 95.0,
  ...
}
```

**Status Codes**
- `200 OK`: Success
- `404 Not Found`: Item does not exist
- `400 Bad Request`: Invalid data

**Behavior**
- `purchase`: `quantity = +abs(quantity)`
- `usage`, `damage`, `return`: `quantity = -abs(quantity)`

---

### 7. Consume Inventory

**POST** `/inventory/:id/consume`

Specialized endpoint for consuming inventory (typically used by service order processing).
Always deducts from inventory.

**Parameters**
- `id` (path): Integer - Inventory item ID

**Request Body**
```json
{
  "quantity": 2.5,
  "reference_type": "service_order",
  "reference_id": "SO-2024-100",
  "notes": "Used for customer order"
}
```

**Required Fields**
- `quantity`: Float (amount to consume)

**Optional Fields**
- `reference_type`: String (defaults to "service_order")
- `reference_id`: String
- `notes`: String

**Response**
```json
{
  "id": 1,
  "quantity": 42.5,
  ...
}
```

**Status Codes**
- `200 OK`: Success
- `404 Not Found`: Item does not exist
- `400 Bad Request`: Invalid data

**Note**: This always creates a `usage` transaction type.

---

### 8. Get Low-Stock Items

**GET** `/inventory/low-stock`

Returns all items that are at or below their reorder level.

**Response**
```json
[
  {
    "id": 2,
    "name": "Persil Powder Detergent",
    "quantity": 8.0,
    "reorder_level": 15.0,
    "is_low_stock": true,
    ...
  }
]
```

**Status Codes**
- `200 OK`: Success (returns empty array if no low-stock items)

---

## Error Responses

All error responses follow this format:

```json
{
  "error": "Error message description"
}
```

Common HTTP Status Codes:
- `200 OK`: Request succeeded
- `201 Created`: Resource created successfully
- `204 No Content`: Request succeeded with no content to return
- `400 Bad Request`: Invalid request data
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

---

## Examples

### Example 1: Create and Stock Management Flow

```bash
# 1. Create new item
curl -X POST http://localhost:5000/api/inventory \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Eco Detergent",
    "category": "detergent",
    "quantity": 0,
    "unit": "liters",
    "reorder_level": 20.0,
    "cost_per_unit": 14.00,
    "supplier": "Green Supplies"
  }'

# 2. Receive shipment (add stock)
curl -X POST http://localhost:5000/api/inventory/1/adjust \
  -H "Content-Type: application/json" \
  -d '{
    "transaction_type": "purchase",
    "quantity": 100,
    "reference_type": "Purchase Order",
    "reference_id": "PO-001",
    "notes": "Initial stock"
  }'

# 3. Check current stock
curl http://localhost:5000/api/inventory/1

# 4. Consume for service order
curl -X POST http://localhost:5000/api/inventory/1/consume \
  -H "Content-Type: application/json" \
  -d '{
    "quantity": 5.0,
    "reference_type": "service_order",
    "reference_id": "SO-123"
  }'

# 5. Check for low stock
curl http://localhost:5000/api/inventory/low-stock
```

### Example 2: Bulk Import Script

```python
import requests
import csv

BASE_URL = 'http://localhost:5000/api'

def import_inventory_from_csv(filename):
    with open(filename, 'r') as f:
        reader = csv.DictReader(f)
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
            
            response = requests.post(f'{BASE_URL}/inventory', json=item_data)
            
            if response.status_code == 201:
                print(f"✓ Created: {item_data['name']}")
            else:
                print(f"✗ Failed: {item_data['name']} - {response.text}")

import_inventory_from_csv('inventory.csv')
```

### Example 3: Automated Low-Stock Monitoring

```python
import requests
import smtplib
from email.mime.text import MIMEText

BASE_URL = 'http://localhost:5000/api'

def check_and_alert_low_stock():
    response = requests.get(f'{BASE_URL}/inventory/low-stock')
    low_stock_items = response.json()
    
    if low_stock_items:
        message = "Low Stock Alert!\n\n"
        message += "The following items need restocking:\n\n"
        
        for item in low_stock_items:
            message += f"- {item['name']}: {item['quantity']} {item['unit']} "
            message += f"(reorder level: {item['reorder_level']} {item['unit']})\n"
            if item['supplier']:
                message += f"  Supplier: {item['supplier']}\n"
        
        send_email_alert(message)
        print(f"Alert sent for {len(low_stock_items)} items")
    else:
        print("All items adequately stocked")

def send_email_alert(message):
    # Implement email sending logic
    pass

# Run daily
check_and_alert_low_stock()
```

### Example 4: Service Order Integration

```python
import requests

BASE_URL = 'http://localhost:5000/api'

def process_laundry_order(order_id, num_loads):
    """Process a laundry order and consume inventory"""
    
    # Define per-load consumption rates
    consumption_rates = {
        'Tide Liquid Detergent': 0.25,  # liters per load
        'Downy Fabric Softener': 0.15,  # liters per load
    }
    
    # Get all inventory items
    items_response = requests.get(f'{BASE_URL}/inventory')
    items = {item['name']: item for item in items_response.json()}
    
    # Consume inventory for each item
    for item_name, rate_per_load in consumption_rates.items():
        if item_name in items:
            item = items[item_name]
            quantity_needed = rate_per_load * num_loads
            
            if item['quantity'] >= quantity_needed:
                consume_data = {
                    'quantity': quantity_needed,
                    'reference_type': 'service_order',
                    'reference_id': order_id,
                    'notes': f'Consumed for {num_loads} loads of laundry'
                }
                
                response = requests.post(
                    f'{BASE_URL}/inventory/{item["id"]}/consume',
                    json=consume_data
                )
                
                if response.status_code == 200:
                    print(f"✓ Consumed {quantity_needed} {item['unit']} of {item_name}")
                else:
                    print(f"✗ Failed to consume {item_name}")
            else:
                print(f"⚠ Insufficient stock of {item_name}")

# Example usage
process_laundry_order("SO-2024-100", num_loads=3)
```

---

## Rate Limiting

Currently, there is no rate limiting implemented. For production use, consider implementing rate limiting to prevent abuse.

## Authentication

Currently, the API does not require authentication. For production use, implement appropriate authentication and authorization mechanisms.

## Versioning

This is version 1 of the API. Future versions may include the version in the URL path (e.g., `/api/v2/inventory`).

---

## Support

For issues or questions about the API, please refer to the main README.md or contact the development team.
