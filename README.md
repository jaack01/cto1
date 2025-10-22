# Inventory Management System

A comprehensive inventory management system designed for laundry and cleaning service businesses to track detergent, supplies, and materials with automated low-stock alerts.

## Features

### 1. Inventory Management
- **CRUD Operations**: Create, read, update, and delete inventory items
- **Categorization**: Organize items by category (detergent, fabric softener, bleach, stain remover, supplies, packaging, etc.)
- **Detailed Tracking**: Track quantity, unit of measurement, reorder levels, cost per unit, and supplier information

### 2. Stock Adjustments
- **Multiple Transaction Types**:
  - Purchase/Restock: Add inventory from purchases
  - Usage/Consumption: Deduct inventory used in services
  - Manual Adjustment: Correct inventory levels
  - Damage/Loss: Record damaged or lost items
  - Return to Supplier: Track returns
- **Transaction History**: Full audit trail of all inventory movements
- **Reference Linking**: Link adjustments to service orders or purchase orders

### 3. Low-Stock Alerts
- **Dashboard Alerts**: Visual alerts on the dashboard for items at or below reorder level
- **Color-Coded Status**: Easy identification of stock levels
  - Red: Out of stock
  - Yellow: Low stock (at or below reorder level)
  - Blue: Normal stock
  - Green: Well-stocked
- **Alert Count**: Quick overview of total low-stock items

### 4. Dashboard & Reporting
- **Key Metrics**: Total items, low-stock count, overall stock level percentage
- **Recent Transactions**: View the 10 most recent inventory transactions
- **Low-Stock Summary Table**: Detailed list of all items needing attention

### 5. REST API
Full REST API for integration with other systems:
- `GET /api/inventory` - List all inventory items
- `POST /api/inventory` - Create new item
- `GET /api/inventory/<id>` - Get item details
- `PUT /api/inventory/<id>` - Update item
- `DELETE /api/inventory/<id>` - Delete item
- `POST /api/inventory/<id>/adjust` - Adjust inventory quantity
- `GET /api/inventory/low-stock` - Get low-stock items
- `POST /api/inventory/<id>/consume` - Consume inventory for service orders

## Technology Stack

- **Backend**: Python 3.x with Flask web framework
- **Database**: SQLite (easily upgradable to PostgreSQL)
- **ORM**: SQLAlchemy
- **Frontend**: Bootstrap 5 with Jinja2 templates
- **Icons**: Bootstrap Icons

## Installation

### Prerequisites
- Python 3.7 or higher
- pip (Python package manager)

### Setup Steps

1. Clone the repository:
```bash
git clone <repository-url>
cd <repository-name>
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create environment configuration (optional):
```bash
cp .env.example .env
# Edit .env with your configurations if needed
```

5. Initialize the database and run the application:
```bash
python app.py
```

The application will be available at `http://localhost:5000`

## Usage

### Adding Inventory Items

1. Navigate to **Inventory** in the sidebar
2. Click **Add New Item**
3. Fill in the form:
   - **Name**: Item name (e.g., "Tide Liquid Detergent")
   - **Category**: Select appropriate category
   - **Description**: Optional detailed description
   - **Quantity**: Current stock quantity
   - **Unit**: Unit of measurement (kg, liters, pieces, etc.)
   - **Reorder Level**: When to trigger low-stock alert
   - **Cost Per Unit**: Optional cost tracking
   - **Supplier**: Optional supplier information
4. Click **Save Item**

### Adjusting Stock

1. Navigate to an item's detail page
2. Click **Adjust Stock**
3. Select transaction type:
   - **Purchase/Restock**: When receiving new inventory
   - **Usage/Consumption**: When inventory is used in services
   - **Manual Adjustment**: For corrections
   - **Damage/Loss**: For damaged or lost items
   - **Return to Supplier**: For returns
4. Enter quantity (always enter positive value; system handles direction)
5. Optionally add reference information (e.g., "Service Order: SO-123")
6. Add notes for audit trail
7. Click **Apply Adjustment**

### Monitoring Low Stock

The **Dashboard** automatically displays:
- Total number of items below reorder level
- Highlighted alert banner when low-stock items exist
- Detailed table of all low-stock items with quick restock buttons

### Consuming Inventory via API

For automated consumption when processing service orders:

```bash
curl -X POST http://localhost:5000/api/inventory/<item_id>/consume \
  -H "Content-Type: application/json" \
  -d '{
    "quantity": 2.5,
    "reference_type": "service_order",
    "reference_id": "SO-12345",
    "notes": "Used for customer order"
  }'
```

## Database Schema

### InventoryItem
- `id`: Primary key
- `name`: Item name
- `category`: Item category
- `description`: Optional description
- `quantity`: Current stock level
- `unit`: Unit of measurement
- `reorder_level`: Threshold for low-stock alerts
- `cost_per_unit`: Optional cost per unit
- `supplier`: Optional supplier name
- `created_at`: Creation timestamp
- `updated_at`: Last update timestamp

### InventoryTransaction
- `id`: Primary key
- `item_id`: Foreign key to InventoryItem
- `transaction_type`: Type of transaction
- `quantity`: Quantity changed (positive or negative)
- `reference_type`: Optional reference type (e.g., "service_order")
- `reference_id`: Optional reference ID
- `notes`: Optional notes
- `created_at`: Transaction timestamp

### ServiceOrder
- `id`: Primary key
- `order_number`: Unique order number
- `customer_name`: Customer name
- `service_type`: Type of service
- `status`: Order status
- `created_at`: Creation timestamp
- `completed_at`: Completion timestamp

## Configuration

Edit `config.py` or create a `.env` file to customize:

- `SECRET_KEY`: Flask secret key for sessions
- `DATABASE_URL`: Database connection string (default: SQLite)
- `LOW_STOCK_THRESHOLD_PERCENTAGE`: Percentage threshold for warnings (default: 10%)

## API Documentation

### List All Items
```
GET /api/inventory
Response: Array of inventory items with full details
```

### Get Single Item
```
GET /api/inventory/<id>
Response: Single inventory item with details
```

### Create Item
```
POST /api/inventory
Body: {
  "name": "Item Name",
  "category": "detergent",
  "quantity": 100,
  "unit": "kg",
  "reorder_level": 20,
  "description": "Optional",
  "cost_per_unit": 10.50,
  "supplier": "Supplier Name"
}
Response: Created item with ID
```

### Update Item
```
PUT /api/inventory/<id>
Body: Partial or full item data
Response: Updated item
```

### Delete Item
```
DELETE /api/inventory/<id>
Response: 204 No Content
```

### Adjust Inventory
```
POST /api/inventory/<id>/adjust
Body: {
  "transaction_type": "usage",
  "quantity": 5.5,
  "reference_type": "service_order",
  "reference_id": "SO-123",
  "notes": "Optional notes"
}
Response: Updated item
```

### Consume Inventory
```
POST /api/inventory/<id>/consume
Body: {
  "quantity": 2.5,
  "reference_type": "service_order",
  "reference_id": "SO-123",
  "notes": "Optional"
}
Response: Updated item
```

### Get Low-Stock Items
```
GET /api/inventory/low-stock
Response: Array of items at or below reorder level
```

## Best Practices

1. **Set Realistic Reorder Levels**: Base reorder levels on actual usage patterns and supplier lead times
2. **Regular Audits**: Periodically verify physical inventory matches system quantities
3. **Document Adjustments**: Always add notes when making manual adjustments
4. **Link Transactions**: Use reference fields to link inventory changes to orders or purchases
5. **Monitor Dashboard**: Check the dashboard regularly for low-stock alerts

## License

This project is provided as-is for inventory management purposes.

## Support

For issues or questions, please refer to the project documentation or contact the development team.
