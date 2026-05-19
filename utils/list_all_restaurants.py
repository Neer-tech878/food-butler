#!/usr/bin/env python3
"""List all restaurants and their IDs"""
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
    restaurants = db.query(models.Restaurant).all()
    print(f"📊 Total Restaurants in Database: {len(restaurants)}\n")
    
    for i, rest in enumerate(restaurants, 1):
        menu_count = db.query(models.MenuItem).filter(
            models.MenuItem.restaurant_id == rest.id
        ).count()
        print(f"{i}. {rest.name}")
        print(f"   ID: {rest.id}")
        print(f"   Cuisine: {rest.cuisine}")
        print(f"   Menu Items: {menu_count}")
        print()
    
finally:
    db.close()
