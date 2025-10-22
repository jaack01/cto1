from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from models import db, InventoryItem, InventoryTransaction, ServiceOrder, utcnow
from forms import InventoryItemForm, AdjustmentForm
from config import Config
import os

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)


@app.route('/')
def index():
    return redirect(url_for('dashboard'))


@app.route('/dashboard')
def dashboard():
    low_stock_items = InventoryItem.query.filter(
        InventoryItem.quantity <= InventoryItem.reorder_level
    ).all()
    
    total_items = InventoryItem.query.count()
    low_stock_count = len(low_stock_items)
    recent_transactions = InventoryTransaction.query.order_by(
        InventoryTransaction.created_at.desc()
    ).limit(10).all()
    
    return render_template('dashboard.html',
                         low_stock_items=low_stock_items,
                         low_stock_count=low_stock_count,
                         total_items=total_items,
                         recent_transactions=recent_transactions)


@app.route('/inventory')
def inventory_list():
    category = request.args.get('category', '')
    search = request.args.get('search', '')
    
    query = InventoryItem.query
    
    if category:
        query = query.filter(InventoryItem.category == category)
    
    if search:
        query = query.filter(InventoryItem.name.ilike(f'%{search}%'))
    
    items = query.order_by(InventoryItem.name).all()
    
    return render_template('inventory_list.html', items=items, category=category, search=search)


@app.route('/inventory/new', methods=['GET', 'POST'])
def inventory_new():
    form = InventoryItemForm()
    
    if form.validate_on_submit():
        item = InventoryItem(
            name=form.name.data,
            category=form.category.data,
            description=form.description.data,
            quantity=form.quantity.data,
            unit=form.unit.data,
            reorder_level=form.reorder_level.data,
            cost_per_unit=form.cost_per_unit.data,
            supplier=form.supplier.data
        )
        db.session.add(item)
        
        transaction = InventoryTransaction(
            item=item,
            transaction_type='initial',
            quantity=form.quantity.data,
            notes='Initial stock entry'
        )
        db.session.add(transaction)
        
        db.session.commit()
        flash(f'Inventory item "{item.name}" created successfully!', 'success')
        return redirect(url_for('inventory_list'))
    
    return render_template('inventory_form.html', form=form, title='New Inventory Item')


@app.route('/inventory/<int:id>/edit', methods=['GET', 'POST'])
def inventory_edit(id):
    item = InventoryItem.query.get_or_404(id)
    form = InventoryItemForm(obj=item)
    
    if form.validate_on_submit():
        old_quantity = item.quantity
        
        item.name = form.name.data
        item.category = form.category.data
        item.description = form.description.data
        item.quantity = form.quantity.data
        item.unit = form.unit.data
        item.reorder_level = form.reorder_level.data
        item.cost_per_unit = form.cost_per_unit.data
        item.supplier = form.supplier.data
        item.updated_at = utcnow()
        
        if old_quantity != form.quantity.data:
            diff = form.quantity.data - old_quantity
            transaction = InventoryTransaction(
                item=item,
                transaction_type='adjustment',
                quantity=diff,
                notes=f'Updated from edit form (from {old_quantity} to {form.quantity.data})'
            )
            db.session.add(transaction)
        
        db.session.commit()
        flash(f'Inventory item "{item.name}" updated successfully!', 'success')
        return redirect(url_for('inventory_list'))
    
    return render_template('inventory_form.html', form=form, title='Edit Inventory Item', item=item)


@app.route('/inventory/<int:id>')
def inventory_detail(id):
    item = InventoryItem.query.get_or_404(id)
    transactions = InventoryTransaction.query.filter_by(item_id=id).order_by(
        InventoryTransaction.created_at.desc()
    ).all()
    
    return render_template('inventory_detail.html', item=item, transactions=transactions)


@app.route('/inventory/<int:id>/delete', methods=['POST'])
def inventory_delete(id):
    item = InventoryItem.query.get_or_404(id)
    name = item.name
    db.session.delete(item)
    db.session.commit()
    flash(f'Inventory item "{name}" deleted successfully!', 'success')
    return redirect(url_for('inventory_list'))


@app.route('/inventory/<int:id>/adjust', methods=['GET', 'POST'])
def inventory_adjust(id):
    item = InventoryItem.query.get_or_404(id)
    form = AdjustmentForm()
    
    if form.validate_on_submit():
        quantity_change = form.quantity.data
        
        if form.transaction_type.data in ['usage', 'damage', 'return']:
            quantity_change = -abs(quantity_change)
        else:
            quantity_change = abs(quantity_change)
        
        item.quantity += quantity_change
        item.updated_at = utcnow()
        
        transaction = InventoryTransaction(
            item=item,
            transaction_type=form.transaction_type.data,
            quantity=quantity_change,
            reference_type=form.reference_type.data,
            reference_id=form.reference_id.data,
            notes=form.notes.data
        )
        
        db.session.add(transaction)
        db.session.commit()
        
        flash(f'Inventory adjusted successfully! New quantity: {item.quantity} {item.unit}', 'success')
        return redirect(url_for('inventory_detail', id=id))
    
    return render_template('inventory_adjust.html', form=form, item=item)


@app.route('/api/inventory', methods=['GET'])
def api_inventory_list():
    items = InventoryItem.query.all()
    return jsonify([item.to_dict() for item in items])


@app.route('/api/inventory/<int:id>', methods=['GET'])
def api_inventory_get(id):
    item = InventoryItem.query.get_or_404(id)
    return jsonify(item.to_dict())


@app.route('/api/inventory', methods=['POST'])
def api_inventory_create():
    data = request.get_json()
    
    item = InventoryItem(
        name=data['name'],
        category=data['category'],
        description=data.get('description'),
        quantity=data['quantity'],
        unit=data['unit'],
        reorder_level=data['reorder_level'],
        cost_per_unit=data.get('cost_per_unit'),
        supplier=data.get('supplier')
    )
    
    db.session.add(item)
    
    transaction = InventoryTransaction(
        item=item,
        transaction_type='initial',
        quantity=data['quantity'],
        notes='Created via API'
    )
    db.session.add(transaction)
    
    db.session.commit()
    
    return jsonify(item.to_dict()), 201


@app.route('/api/inventory/<int:id>', methods=['PUT'])
def api_inventory_update(id):
    item = InventoryItem.query.get_or_404(id)
    data = request.get_json()
    
    old_quantity = item.quantity
    
    item.name = data.get('name', item.name)
    item.category = data.get('category', item.category)
    item.description = data.get('description', item.description)
    item.quantity = data.get('quantity', item.quantity)
    item.unit = data.get('unit', item.unit)
    item.reorder_level = data.get('reorder_level', item.reorder_level)
    item.cost_per_unit = data.get('cost_per_unit', item.cost_per_unit)
    item.supplier = data.get('supplier', item.supplier)
    item.updated_at = utcnow()
    
    if old_quantity != item.quantity:
        diff = item.quantity - old_quantity
        transaction = InventoryTransaction(
            item=item,
            transaction_type='adjustment',
            quantity=diff,
            notes='Updated via API'
        )
        db.session.add(transaction)
    
    db.session.commit()
    
    return jsonify(item.to_dict())


@app.route('/api/inventory/<int:id>', methods=['DELETE'])
def api_inventory_delete(id):
    item = InventoryItem.query.get_or_404(id)
    db.session.delete(item)
    db.session.commit()
    return '', 204


@app.route('/api/inventory/<int:id>/adjust', methods=['POST'])
def api_inventory_adjust(id):
    item = InventoryItem.query.get_or_404(id)
    data = request.get_json()
    
    quantity_change = data['quantity']
    transaction_type = data['transaction_type']
    
    if transaction_type in ['usage', 'damage', 'return']:
        quantity_change = -abs(quantity_change)
    else:
        quantity_change = abs(quantity_change)
    
    item.quantity += quantity_change
    item.updated_at = utcnow()
    
    transaction = InventoryTransaction(
        item=item,
        transaction_type=transaction_type,
        quantity=quantity_change,
        reference_type=data.get('reference_type'),
        reference_id=data.get('reference_id'),
        notes=data.get('notes')
    )
    
    db.session.add(transaction)
    db.session.commit()
    
    return jsonify(item.to_dict())


@app.route('/api/inventory/low-stock', methods=['GET'])
def api_low_stock():
    items = InventoryItem.query.filter(
        InventoryItem.quantity <= InventoryItem.reorder_level
    ).all()
    return jsonify([item.to_dict() for item in items])


@app.route('/api/inventory/<int:id>/consume', methods=['POST'])
def api_inventory_consume(id):
    item = InventoryItem.query.get_or_404(id)
    data = request.get_json()
    
    quantity = data['quantity']
    reference_type = data.get('reference_type', 'service_order')
    reference_id = data.get('reference_id')
    
    item.quantity -= quantity
    item.updated_at = utcnow()
    
    transaction = InventoryTransaction(
        item=item,
        transaction_type='usage',
        quantity=-quantity,
        reference_type=reference_type,
        reference_id=reference_id,
        notes=data.get('notes', f'Consumed by {reference_type} {reference_id}')
    )
    
    db.session.add(transaction)
    db.session.commit()
    
    return jsonify(item.to_dict())


def init_db():
    with app.app_context():
        db.create_all()
        print("Database initialized successfully!")


if __name__ == '__main__':
    if not os.path.exists('inventory.db'):
        init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)
