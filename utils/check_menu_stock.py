#!/usr/bin/env python3
"""Check menu items and inventory in database"""
import sys
sys.path.insert(0, '/Users/jaswanthyamana/food_butler_platform/food_butler_backend')

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app import models
import os
from dotenv import load_dotenv

load_dotenv('/Users/jaswanthyamana/food_butler_platform/food_butler_backend/.env')

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

db = SessionLocal()

try:
    # Count restaurants
    rest_count = db.query(models.Restaurant).count()
    print(f"📊 Total Restaurants: {rest_count}")
    
    # Count menu items
    menu_count = db.query(models.MenuItem).count()
    print(f"🍽️  Total Menu Items: {menu_count}")
    
    # Count inventory
    inv_count = db.query(models.Inventory).count()
    print(f"📦 Total Inventory Records: {inv_count}")
    
    # Get a sample restaurant
    restaurant = db.query(models.Restaurant).filter(
        models.Restaurant.name == "Test Restaurant"
    ).first()
    
    if restaurant:
        print(f"\n✅ Found Restaurant: {restaurant.name} (ID: {restaurant.id})")
        
        # Get its menu items
        menu_items = db.query(models.MenuItem).filter(
            models.MenuItem.restaurant_id == restaurant.id
        ).all()
        
        print(f"   Menu Items: {len(menu_items)}")
        for item in menu_items[:3]:
            inv = db.query(models.Inventory).filter(
                models.Inventory.menu_item_id == item.id
            ).first()
            stock = inv.quantity if inv else "No inventory"
            print(f"   • {item.name}: ₹{item.price} - Stock: {stock} - Available: {item.is_available}")
    
finally:
    db.close()
