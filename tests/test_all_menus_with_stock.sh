#!/bin/bash

# Test All Restaurant Menus with Stock
echo "🧪 Testing All Restaurant Menus with Stock"
echo "==========================================="
echo ""

BACKEND_URL="http://localhost:8000"

# Get all restaurants
RESTAURANTS=$(curl -s "${BACKEND_URL}/restaurants/")

echo "$RESTAURANTS" | python3 - <<'PYTHON_SCRIPT'
import sys
import json
import requests

backend_url = "http://localhost:8000"
restaurants_json = sys.stdin.read()
restaurants = json.loads(restaurants_json)

print(f"Found {len(restaurants)} restaurants\n")
print("=" * 70)

total_items = 0
total_stock = 0

for idx, restaurant in enumerate(restaurants, 1):
    rest_id = restaurant['id']
    rest_name = restaurant['name']
    cuisine = restaurant.get('cuisine', 'N/A')
    
    # Fetch menu
    menu_response = requests.get(f"{backend_url}/restaurants/{rest_id}/menu")
    menu_items = menu_response.json()
    
    print(f"\n{idx}. {rest_name}")
    print(f"   Cuisine: {cuisine}")
    print(f"   📋 Menu Items: {len(menu_items)}")
    
    if len(menu_items) > 0:
        restaurant_stock = 0
        print(f"   Items with stock:")
        for item in menu_items[:3]:  # Show first 3 items
            stock = item.get('inventory', {}).get('quantity', 0)
            restaurant_stock += stock
            print(f"      • {item['name']}: ₹{item['price']} - Stock: {stock}")
        
        if len(menu_items) > 3:
            remaining_stock = sum([item.get('inventory', {}).get('quantity', 0) for item in menu_items[3:]])
            restaurant_stock += remaining_stock
            print(f"      ... and {len(menu_items) - 3} more items")
        
        print(f"   📦 Total Stock Units: {restaurant_stock}")
        total_items += len(menu_items)
        total_stock += restaurant_stock
    else:
        print(f"   ⚠️  No menu items found!")
    
    print("   " + "-" * 66)

print("\n" + "=" * 70)
print(f"📊 SUMMARY")
print("=" * 70)
print(f"Total Restaurants: {len(restaurants)}")
print(f"Total Menu Items: {total_items}")
print(f"Total Stock Units: {total_stock}")
print(f"\n✅ All restaurants have menu items with stock!" if total_items > 0 else "\n❌ Some restaurants are missing menu items!")

PYTHON_SCRIPT

echo ""
echo "🎉 Test Complete!"
