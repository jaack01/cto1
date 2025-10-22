import requests
import json

BASE_URL = 'http://localhost:5000/api'


def print_response(title, response):
    print(f"\n{'='*60}")
    print(f"{title}")
    print(f"{'='*60}")
    print(f"Status Code: {response.status_code}")
    if response.status_code != 204:
        print(f"Response: {json.dumps(response.json(), indent=2)}")


def test_inventory_api():
    print("Testing Inventory Management API")
    print("="*60)
    
    print("\n1. Getting all inventory items...")
    response = requests.get(f'{BASE_URL}/inventory')
    print_response("GET /api/inventory", response)
    
    if response.json():
        first_item = response.json()[0]
        item_id = first_item['id']
        
        print(f"\n2. Getting single item (ID: {item_id})...")
        response = requests.get(f'{BASE_URL}/inventory/{item_id}')
        print_response(f"GET /api/inventory/{item_id}", response)
        
        print(f"\n3. Adjusting inventory (consuming 5 units)...")
        adjustment_data = {
            'transaction_type': 'usage',
            'quantity': 5.0,
            'reference_type': 'service_order',
            'reference_id': 'SO-12345',
            'notes': 'Test consumption for demo service order'
        }
        response = requests.post(
            f'{BASE_URL}/inventory/{item_id}/adjust',
            json=adjustment_data
        )
        print_response(f"POST /api/inventory/{item_id}/adjust", response)
        
        print(f"\n4. Consuming inventory directly...")
        consume_data = {
            'quantity': 2.5,
            'reference_type': 'service_order',
            'reference_id': 'SO-12346',
            'notes': 'Another test consumption'
        }
        response = requests.post(
            f'{BASE_URL}/inventory/{item_id}/consume',
            json=consume_data
        )
        print_response(f"POST /api/inventory/{item_id}/consume", response)
    
    print("\n5. Getting low-stock items...")
    response = requests.get(f'{BASE_URL}/inventory/low-stock')
    print_response("GET /api/inventory/low-stock", response)
    
    print("\n6. Creating a new inventory item...")
    new_item = {
        'name': 'Test Detergent',
        'category': 'detergent',
        'description': 'Test item created via API',
        'quantity': 50.0,
        'unit': 'liters',
        'reorder_level': 15.0,
        'cost_per_unit': 10.00,
        'supplier': 'Test Supplier'
    }
    response = requests.post(f'{BASE_URL}/inventory', json=new_item)
    print_response("POST /api/inventory", response)
    
    if response.status_code == 201:
        created_item = response.json()
        created_id = created_item['id']
        
        print(f"\n7. Updating the created item (ID: {created_id})...")
        update_data = {
            'quantity': 55.0,
            'cost_per_unit': 11.50
        }
        response = requests.put(
            f'{BASE_URL}/inventory/{created_id}',
            json=update_data
        )
        print_response(f"PUT /api/inventory/{created_id}", response)
        
        print(f"\n8. Deleting the created item (ID: {created_id})...")
        response = requests.delete(f'{BASE_URL}/inventory/{created_id}')
        print_response(f"DELETE /api/inventory/{created_id}", response)
    
    print("\n" + "="*60)
    print("API Testing Complete!")
    print("="*60)


if __name__ == '__main__':
    try:
        test_inventory_api()
    except requests.exceptions.ConnectionError:
        print("\nError: Could not connect to the API.")
        print("Make sure the Flask application is running on http://localhost:5000")
        print("\nTo start the application, run: python app.py")
