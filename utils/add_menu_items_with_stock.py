#!/usr/bin/env python3
"""
Add Menu Items with Stock/Inventory to All Restaurants
"""
import sys
sys.path.insert(0, '/Users/jaswanthyamana/food_butler_platform/food_butler_backend')

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app import models
import os
from dotenv import load_dotenv
import random

# Load environment variables
load_dotenv('/Users/jaswanthyamana/food_butler_platform/food_butler_backend/.env')

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def add_menu_items_with_stock():
    db = SessionLocal()
    
    try:
        print("🍽️  Adding Menu Items with Stock to All Restaurants")
        print("=" * 60)
        
        # Get all restaurants
        restaurants = db.query(models.Restaurant).all()
        
        # Menu items templates for different cuisines
        menu_templates = {
            "Indian Cuisine": [
                {"name": "Chicken Biryani", "description": "Aromatic basmati rice with tender chicken", "price": 299.00, "stock": 50},
                {"name": "Butter Chicken", "description": "Creamy tomato curry with tender chicken", "price": 349.00, "stock": 40},
                {"name": "Paneer Tikka Masala", "description": "Cottage cheese in rich tomato gravy", "price": 279.00, "stock": 45},
                {"name": "Dal Makhani", "description": "Slow-cooked black lentils with cream", "price": 199.00, "stock": 60},
                {"name": "Naan", "description": "Soft tandoor-baked flatbread", "price": 49.00, "stock": 100},
                {"name": "Gulab Jamun", "description": "Sweet milk dumplings in sugar syrup", "price": 89.00, "stock": 70},
            ],
            "South Indian": [
                {"name": "Masala Dosa", "description": "Crispy rice crepe with potato filling", "price": 129.00, "stock": 60},
                {"name": "Idli Sambar", "description": "Steamed rice cakes with lentil soup", "price": 99.00, "stock": 80},
                {"name": "Medu Vada", "description": "Crispy lentil fritters", "price": 79.00, "stock": 50},
                {"name": "Uttapam", "description": "Thick rice pancake with vegetables", "price": 119.00, "stock": 45},
                {"name": "Filter Coffee", "description": "Traditional South Indian coffee", "price": 49.00, "stock": 100},
                {"name": "Pongal", "description": "Rice and lentil comfort food", "price": 89.00, "stock": 55},
            ],
            "North Indian": [
                {"name": "Tandoori Chicken", "description": "Clay oven roasted spiced chicken", "price": 399.00, "stock": 35},
                {"name": "Rogan Josh", "description": "Kashmiri lamb curry", "price": 449.00, "stock": 30},
                {"name": "Chole Bhature", "description": "Chickpea curry with fried bread", "price": 179.00, "stock": 50},
                {"name": "Palak Paneer", "description": "Cottage cheese in spinach gravy", "price": 249.00, "stock": 40},
                {"name": "Kulcha", "description": "Stuffed flatbread", "price": 69.00, "stock": 60},
                {"name": "Lassi", "description": "Yogurt-based refreshing drink", "price": 79.00, "stock": 80},
            ],
            "Breakfast & Snacks": [
                {"name": "Poha", "description": "Flattened rice with spices", "price": 69.00, "stock": 70},
                {"name": "Upma", "description": "Semolina breakfast dish", "price": 79.00, "stock": 65},
                {"name": "Aloo Paratha", "description": "Potato stuffed flatbread", "price": 89.00, "stock": 55},
                {"name": "Samosa", "description": "Crispy pastry with potato filling", "price": 39.00, "stock": 100},
                {"name": "Pakora", "description": "Vegetable fritters", "price": 99.00, "stock": 80},
                {"name": "Chai", "description": "Indian spiced tea", "price": 29.00, "stock": 150},
            ],
            "Hyderabadi Cuisine": [
                {"name": "Hyderabadi Biryani", "description": "Authentic Hyderabadi dum biryani", "price": 349.00, "stock": 45},
                {"name": "Haleem", "description": "Slow-cooked wheat and meat stew", "price": 229.00, "stock": 35},
                {"name": "Mirchi ka Salan", "description": "Spicy chili curry", "price": 189.00, "stock": 40},
                {"name": "Double Ka Meetha", "description": "Bread pudding dessert", "price": 129.00, "stock": 50},
                {"name": "Keema Naan", "description": "Minced meat stuffed flatbread", "price": 99.00, "stock": 60},
                {"name": "Irani Chai", "description": "Traditional Hyderabadi tea", "price": 39.00, "stock": 120},
            ],
            "Multi-Cuisine": [
                {"name": "Grilled Chicken", "description": "Herb-marinated grilled chicken", "price": 329.00, "stock": 40},
                {"name": "Pasta Alfredo", "description": "Creamy fettuccine pasta", "price": 279.00, "stock": 45},
                {"name": "Caesar Salad", "description": "Fresh romaine with parmesan", "price": 199.00, "stock": 50},
                {"name": "Pizza Margherita", "description": "Classic tomato and cheese pizza", "price": 349.00, "stock": 35},
                {"name": "Burrito Bowl", "description": "Mexican rice bowl", "price": 299.00, "stock": 40},
                {"name": "Brownie Sundae", "description": "Chocolate brownie with ice cream", "price": 149.00, "stock": 60},
            ],
            "International": [
                {"name": "Club Sandwich", "description": "Triple-decker chicken sandwich", "price": 249.00, "stock": 45},
                {"name": "French Fries", "description": "Crispy golden fries", "price": 129.00, "stock": 80},
                {"name": "Chicken Wings", "description": "Spicy buffalo wings", "price": 299.00, "stock": 50},
                {"name": "Caesar Wrap", "description": "Grilled chicken Caesar wrap", "price": 219.00, "stock": 40},
                {"name": "Cheesecake", "description": "Classic New York cheesecake", "price": 179.00, "stock": 35},
                {"name": "Mojito", "description": "Refreshing mint mocktail", "price": 119.00, "stock": 70},
            ],
            "Italian & Continental": [
                {"name": "Spaghetti Carbonara", "description": "Creamy bacon pasta", "price": 299.00, "stock": 40},
                {"name": "Margherita Pizza", "description": "Fresh mozzarella and basil", "price": 329.00, "stock": 35},
                {"name": "Tiramisu", "description": "Classic Italian dessert", "price": 189.00, "stock": 45},
                {"name": "Bruschetta", "description": "Toasted bread with tomatoes", "price": 149.00, "stock": 55},
                {"name": "Risotto", "description": "Creamy Italian rice", "price": 319.00, "stock": 30},
                {"name": "Cappuccino", "description": "Italian espresso with foam", "price": 99.00, "stock": 90},
            ],
        }
        
        # Default menu for restaurants without matching cuisine
        default_menu = [
            {"name": "Special Thali", "description": "Complete meal platter", "price": 249.00, "stock": 50},
            {"name": "Fried Rice", "description": "Vegetable fried rice", "price": 159.00, "stock": 60},
            {"name": "Manchurian", "description": "Indo-Chinese vegetable balls", "price": 189.00, "stock": 45},
            {"name": "Spring Rolls", "description": "Crispy vegetable rolls", "price": 129.00, "stock": 55},
            {"name": "Ice Cream", "description": "Assorted flavors", "price": 89.00, "stock": 80},
        ]
        
        total_items_added = 0
        total_stock_added = 0
        
        for restaurant in restaurants:
            print(f"\n📍 {restaurant.name}")
            print(f"   Cuisine: {restaurant.cuisine}")
            
            # Check if restaurant already has menu items
            existing_items = db.query(models.MenuItem).filter(
                models.MenuItem.restaurant_id == restaurant.id
            ).count()
            
            if existing_items > 0:
                print(f"   ⏭️  Already has {existing_items} menu items")
                
                # Add inventory to existing items that don't have it
                existing_menu_items = db.query(models.MenuItem).filter(
                    models.MenuItem.restaurant_id == restaurant.id
                ).all()
                
                for item in existing_menu_items:
                    # Check if inventory exists
                    existing_inventory = db.query(models.Inventory).filter(
                        models.Inventory.menu_item_id == item.id
                    ).first()
                    
                    if not existing_inventory:
                        stock_qty = random.randint(30, 100)
                        inventory = models.Inventory(
                            menu_item_id=item.id,
                            quantity=stock_qty
                        )
                        db.add(inventory)
                        total_stock_added += stock_qty
                        print(f"   ✅ Added stock to '{item.name}': {stock_qty} units")
                
                db.commit()
                continue
            
            # Select menu template based on cuisine
            menu_items = menu_templates.get(restaurant.cuisine, default_menu)
            
            items_added = 0
            for item_data in menu_items:
                # Create menu item
                menu_item = models.MenuItem(
                    name=item_data["name"],
                    description=item_data["description"],
                    price=item_data["price"],
                    is_available=True,
                    restaurant_id=restaurant.id
                )
                db.add(menu_item)
                db.flush()  # Get the ID
                
                # Create inventory
                inventory = models.Inventory(
                    menu_item_id=menu_item.id,
                    quantity=item_data["stock"]
                )
                db.add(inventory)
                
                items_added += 1
                total_items_added += 1
                total_stock_added += item_data["stock"]
            
            db.commit()
            print(f"   ✅ Added {items_added} menu items with stock")
        
        print("\n" + "=" * 60)
        print(f"🎉 Successfully Added Menu Items with Stock!")
        print("=" * 60)
        print(f"📊 Summary:")
        print(f"   Total Restaurants: {len(restaurants)}")
        print(f"   New Menu Items: {total_items_added}")
        print(f"   Total Stock Units: {total_stock_added}")
        print("\n✨ All restaurants now have menu items with inventory!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        db.rollback()
        import traceback
        traceback.print_exc()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    add_menu_items_with_stock()
