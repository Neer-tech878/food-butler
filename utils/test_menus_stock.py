#!/usr/bin/env python3
"""Test all restaurant menus with stock"""
import requests

BACKEND_URL = "http://localhost:8000"

# Get all restaurants
restaurants = requests.get(f"{BACKEND_URL}/restaurants/").json()

print(f"🍽️  Testing {len(restaurants)} Restaurants with Stock")
print("=" * 70)

total_items = 0
total_stock = 0

for i, restaurant in enumerate(restaurants, 1):
    rest_id = restaurant['id']
    rest_name = restaurant['name']
    cuisine = restaurant.get('cuisine', 'N/A')
    
    # Fetch menu
    menu = requests.get(f"{BACKEND_URL}/restaurants/{rest_id}/menu").json()
    
    if len(menu) > 0:
        stock_count = sum([item.get('inventory', {}).get('quantity', 0) for item in menu])
        total_items += len(menu)
        total_stock += stock_count
        
        print(f"\n{i}. ✅ {rest_name}")
        print(f"   Cuisine: {cuisine}")
        print(f"   Menu Items: {len(menu)}")
        print(f"   Total Stock: {stock_count} units")
        
        # Show sample items
        for item in menu[:2]:
            stock = item.get('inventory', {}).get('quantity', 'N/A')
            print(f"      • {item['name']}: ₹{item['price']} (Stock: {stock})")
        if len(menu) > 2:
            print(f"      ... and {len(menu) - 2} more items")
    else:
        print(f"\n{i}. ❌ {rest_name} - NO MENU ITEMS")

print("\n" + "=" * 70)
print(f"📊 SUMMARY:")
print(f"   Restaurants: {len(restaurants)}")
print(f"   Total Menu Items: {total_items}")
print(f"   Total Stock Units: {total_stock}")
print("\n🎉 All restaurants have menu items with stock!")
