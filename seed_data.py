from app import app
from models import db, InventoryItem, InventoryTransaction
from datetime import datetime


def seed_sample_data():
    with app.app_context():
        db.create_all()
        
        if InventoryItem.query.count() > 0:
            print("Database already contains data. Skipping seed.")
            return
        
        print("Seeding sample inventory data...")
        
        items = [
            {
                'name': 'Tide Liquid Detergent',
                'category': 'detergent',
                'description': 'High-efficiency liquid laundry detergent, 5L bottles',
                'quantity': 45.0,
                'unit': 'liters',
                'reorder_level': 20.0,
                'cost_per_unit': 12.50,
                'supplier': 'P&G Distributors'
            },
            {
                'name': 'Persil Powder Detergent',
                'category': 'detergent',
                'description': 'Heavy-duty powder detergent for commercial use',
                'quantity': 8.0,
                'unit': 'kg',
                'reorder_level': 15.0,
                'cost_per_unit': 25.00,
                'supplier': 'Unilever Supply Co.'
            },
            {
                'name': 'Downy Fabric Softener',
                'category': 'softener',
                'description': 'Concentrated fabric softener',
                'quantity': 30.0,
                'unit': 'liters',
                'reorder_level': 15.0,
                'cost_per_unit': 8.75,
                'supplier': 'P&G Distributors'
            },
            {
                'name': 'Clorox Bleach',
                'category': 'bleach',
                'description': 'Regular bleach for white fabrics',
                'quantity': 12.0,
                'unit': 'liters',
                'reorder_level': 10.0,
                'cost_per_unit': 5.50,
                'supplier': 'Clorox Direct'
            },
            {
                'name': 'OxiClean Stain Remover',
                'category': 'stain_remover',
                'description': 'Oxygen-based stain remover powder',
                'quantity': 5.0,
                'unit': 'kg',
                'reorder_level': 8.0,
                'cost_per_unit': 15.00,
                'supplier': 'Chemical Supplies Ltd.'
            },
            {
                'name': 'Dryer Sheets',
                'category': 'supplies',
                'description': 'Anti-static dryer sheets, 200 count boxes',
                'quantity': 15.0,
                'unit': 'boxes',
                'reorder_level': 10.0,
                'cost_per_unit': 6.00,
                'supplier': 'General Supplies Inc.'
            },
            {
                'name': 'Laundry Bags - Large',
                'category': 'supplies',
                'description': 'Heavy-duty mesh laundry bags',
                'quantity': 45.0,
                'unit': 'pieces',
                'reorder_level': 20.0,
                'cost_per_unit': 2.50,
                'supplier': 'Textile Wholesale'
            },
            {
                'name': 'Plastic Garment Bags',
                'category': 'packaging',
                'description': 'Clear plastic garment bags for finished items',
                'quantity': 250.0,
                'unit': 'pieces',
                'reorder_level': 100.0,
                'cost_per_unit': 0.35,
                'supplier': 'Packaging Solutions'
            },
            {
                'name': 'Clothes Hangers',
                'category': 'supplies',
                'description': 'Standard plastic hangers',
                'quantity': 180.0,
                'unit': 'pieces',
                'reorder_level': 50.0,
                'cost_per_unit': 0.50,
                'supplier': 'General Supplies Inc.'
            },
            {
                'name': 'Spot Treatment Spray',
                'category': 'stain_remover',
                'description': 'Pre-treatment spray for tough stains',
                'quantity': 3.0,
                'unit': 'bottles',
                'reorder_level': 6.0,
                'cost_per_unit': 9.99,
                'supplier': 'Chemical Supplies Ltd.'
            }
        ]
        
        for item_data in items:
            item = InventoryItem(**item_data)
            db.session.add(item)
            
            transaction = InventoryTransaction(
                item=item,
                transaction_type='initial',
                quantity=item_data['quantity'],
                notes='Initial inventory stock'
            )
            db.session.add(transaction)
        
        db.session.commit()
        print(f"Successfully seeded {len(items)} inventory items!")
        
        print("\nLow stock items:")
        low_stock = InventoryItem.query.filter(
            InventoryItem.quantity <= InventoryItem.reorder_level
        ).all()
        for item in low_stock:
            print(f"  - {item.name}: {item.quantity} {item.unit} (reorder at {item.reorder_level})")


if __name__ == '__main__':
    seed_sample_data()
