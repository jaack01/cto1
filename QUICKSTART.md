# Quick Start Guide

Get up and running with the Inventory Management System in 5 minutes!

## Prerequisites

- Python 3.7 or higher
- pip (Python package manager)

## Installation & Setup

### Option 1: Automated Setup (Recommended)

```bash
# Make the run script executable (if not already)
chmod +x run.sh

# Run the application (creates venv, installs dependencies, seeds data)
./run.sh
```

The application will be available at: http://localhost:5000

### Option 2: Manual Setup

```bash
# 1. Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Seed sample data (optional but recommended for first-time users)
python seed_data.py

# 4. Run the application
python app.py
```

The application will be available at: http://localhost:5000

## First Steps

### 1. Access the Dashboard
Navigate to http://localhost:5000/dashboard

You'll see:
- Total inventory items count
- Low-stock alerts (items needing restock)
- Recent transaction history
- Overall stock level percentage

### 2. View Inventory
Click "Inventory" in the sidebar or visit http://localhost:5000/inventory

Features:
- View all inventory items
- Filter by category
- Search by name
- See stock status (In Stock, Low Stock, Out of Stock)

### 3. Add Your First Item
Click "Add New Item" or visit http://localhost:5000/inventory/new

Example:
- **Name**: Tide Liquid Detergent
- **Category**: Detergent
- **Quantity**: 50
- **Unit**: liters
- **Reorder Level**: 20 (alert triggers when stock reaches this level)
- **Cost Per Unit**: 12.50 (optional)
- **Supplier**: P&G Distributors (optional)

### 4. Adjust Inventory
From any item's detail page:
1. Click "Adjust Stock"
2. Choose transaction type:
   - **Purchase/Restock**: Receiving new inventory
   - **Usage/Consumption**: Using inventory for services
   - **Manual Adjustment**: Corrections
   - **Damage/Loss**: Recording damaged items
   - **Return to Supplier**: Returning defective items
3. Enter quantity and optional notes
4. Submit

## Using the API

### List all items
```bash
curl http://localhost:5000/api/inventory
```

### Get low-stock items
```bash
curl http://localhost:5000/api/inventory/low-stock
```

### Create new item
```bash
curl -X POST http://localhost:5000/api/inventory \
  -H "Content-Type: application/json" \
  -d '{
    "name": "New Product",
    "category": "detergent",
    "quantity": 100,
    "unit": "liters",
    "reorder_level": 25
  }'
```

### Consume inventory (for service orders)
```bash
curl -X POST http://localhost:5000/api/inventory/1/consume \
  -H "Content-Type: application/json" \
  -d '{
    "quantity": 5.0,
    "reference_type": "service_order",
    "reference_id": "SO-123",
    "notes": "Used for customer order"
  }'
```

See [API_DOCUMENTATION.md](API_DOCUMENTATION.md) for complete API reference.

## Sample Data

The system comes with 10 pre-seeded items including:
- Tide Liquid Detergent (45 liters)
- Persil Powder Detergent (8 kg) - **LOW STOCK**
- Downy Fabric Softener (30 liters)
- Clorox Bleach (12 liters)
- OxiClean Stain Remover (5 kg) - **LOW STOCK**
- Dryer Sheets (15 boxes)
- Laundry Bags (45 pieces)
- Plastic Garment Bags (250 pieces)
- Clothes Hangers (180 pieces)
- Spot Treatment Spray (3 bottles) - **LOW STOCK**

Notice: 3 items are intentionally set at low stock to demonstrate the alert system!

## Integration Example

See how to integrate with your service order system:

```bash
python service_order_example.py
```

This demonstrates:
- Creating service orders
- Automatically consuming inventory
- Tracking transactions with reference IDs
- Monitoring low-stock alerts

## Testing

Run API tests (requires app to be running):
```bash
# In terminal 1: Start the app
python app.py

# In terminal 2: Run tests
python test_api.py
```

## Configuration

Edit `config.py` or create a `.env` file:

```env
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///inventory.db
```

## Common Tasks

### Reset Database
```bash
rm -f inventory.db
python seed_data.py
```

### Backup Database
```bash
cp inventory.db inventory_backup_$(date +%Y%m%d).db
```

### View Database Content
```bash
python -c "from app import app; from models import db, InventoryItem; 
with app.app_context():
    for item in InventoryItem.query.all():
        print(f'{item.name}: {item.quantity} {item.unit}')
"
```

## Troubleshooting

### Port 5000 already in use
Change the port in `app.py`:
```python
app.run(debug=True, host='0.0.0.0', port=8080)  # Use port 8080 instead
```

### Module not found errors
Make sure virtual environment is activated:
```bash
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

### Database locked error
Close any other processes using the database:
```bash
fuser inventory.db  # Linux: shows processes using the file
```

## Next Steps

1. **Customize Categories**: Edit `forms.py` to add your specific categories
2. **Set Realistic Reorder Levels**: Based on your actual usage patterns
3. **Integrate with Orders**: Use the API to automatically consume inventory when processing orders
4. **Set Up Monitoring**: Create a cron job to check low-stock items daily
5. **Add Authentication**: Implement user authentication for production use

## Documentation

- [README.md](README.md) - Complete system overview
- [API_DOCUMENTATION.md](API_DOCUMENTATION.md) - Full API reference
- [USAGE_EXAMPLES.md](USAGE_EXAMPLES.md) - Detailed usage scenarios

## Support

For questions or issues:
1. Check the documentation files
2. Review the example scripts
3. Examine the sample data and code comments

Happy inventory tracking! 📦
