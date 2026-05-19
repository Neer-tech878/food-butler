#!/usr/bin/env python3
"""
Initialize Database with Admin User and All Restaurants
"""
import sys
sys.path.insert(0, '/Users/jaswanthyamana/food_butler_platform/food_butler_backend')

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app import models, security
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/Users/jaswanthyamana/food_butler_platform/food_butler_backend/.env')

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_database():
    db = SessionLocal()
    
    try:
        print("🗄️  Initializing Database...")
        print("=" * 50)
        
        # Create admin user
        print("\n1️⃣  Creating Super Admin User...")
        admin_email = "admin@foodbutler.com"
        existing_admin = db.query(models.Customer).filter(models.Customer.email == admin_email).first()
        
        if existing_admin:
            print(f"   ✅ Admin already exists: {admin_email}")
        else:
            admin = models.Customer(
                email=admin_email,
                hashed_password=security.get_password_hash("admin123"),
                phone="+91-1234567890",
                is_admin=True
            )
            db.add(admin)
            db.commit()
            print(f"   ✅ Created admin: {admin_email} / admin123")
        
        # Restaurant data with credentials
        restaurants_data = [
            {
                "name": "Test Restaurant",
                "cuisine": "Indian Cuisine",
                "location": "Hyderabad",
                "address": "123 MG Road, Hyderabad",
                "phone": "+91-40-1234-5678",
                "email": "test@restaurant.com",
                "admin_email": "testrestaurant_7427@foodbutler.com",
                "admin_password": "testrestaurant@7427"
            },
            {
                "name": "Chandrika Family Restaurant",
                "cuisine": "South Indian",
                "location": "Hyderabad",
                "address": "45 Jubilee Hills, Hyderabad",
                "phone": "+91-40-2345-6789",
                "email": "contact@chandrikafamily.com",
                "admin_email": "chandrikafamilyrestaurant_7491@foodbutler.com",
                "admin_password": "chandrikafamilyrestaurant@7491"
            },
            {
                "name": "Spice Magic",
                "cuisine": "North Indian",
                "location": "Hyderabad",
                "address": "78 Banjara Hills, Hyderabad",
                "phone": "+91-40-3456-7890",
                "email": "info@spicemagic.com",
                "admin_email": "spicemagic_4c34@foodbutler.com",
                "admin_password": "spicemagic@4c34"
            },
            {
                "name": "Chandrika Tiffins",
                "cuisine": "Breakfast & Snacks",
                "location": "Hyderabad",
                "address": "12 Ameerpet, Hyderabad",
                "phone": "+91-40-4567-8901",
                "email": "orders@chandrikatiffins.com",
                "admin_email": "chandrikatiffins_c8bb@foodbutler.com",
                "admin_password": "chandrikatiffins@c8bb"
            },
            {
                "name": "Deccan Spice",
                "cuisine": "Hyderabadi Cuisine",
                "location": "Hyderabad",
                "address": "90 Somajiguda, Hyderabad",
                "phone": "+91-40-5678-9012",
                "email": "hello@deccanspice.com",
                "admin_email": "deccanspice_ae5a@foodbutler.com",
                "admin_password": "deccanspice@ae5a"
            },
            {
                "name": "Chandrika Grand",
                "cuisine": "Multi-Cuisine",
                "location": "Hyderabad",
                "address": "56 Begumpet, Hyderabad",
                "phone": "+91-40-6789-0123",
                "email": "reservations@chandrikagrand.com",
                "admin_email": "chandrikagrand_e1f6@foodbutler.com",
                "admin_password": "chandrikagrand@e1f6"
            },
            {
                "name": "Test Restaurant Manager",
                "cuisine": "International",
                "location": "Hyderabad",
                "address": "101 Hitech City, Hyderabad",
                "phone": "+91-40-7890-1234",
                "email": "manager@testrestaurant.com",
                "admin_email": "manager@testrestaurant.com",
                "admin_password": "manager123"
            },
            {
                "name": "Demo Restaurant",
                "cuisine": "Italian & Continental",
                "location": "Hyderabad",
                "address": "202 Gachibowli, Hyderabad",
                "phone": "+91-40-8901-2345",
                "email": "chef@demorestaurant.com",
                "admin_email": "chef@demorestaurant.com",
                "admin_password": "chef123"
            }
        ]
        
        print("\n2️⃣  Creating Restaurants...")
        for idx, rest_data in enumerate(restaurants_data, 1):
            # Check if restaurant already exists
            existing = db.query(models.Restaurant).filter(
                models.Restaurant.name == rest_data["name"]
            ).first()
            
            if existing:
                print(f"   ⏭️  {idx}. {rest_data['name']} already exists")
                continue
            
            restaurant = models.Restaurant(
                name=rest_data["name"],
                cuisine=rest_data["cuisine"],
                location=rest_data["location"],
                address=rest_data["address"],
                phone=rest_data["phone"],
                email=rest_data["email"],
                restaurant_admin_email=rest_data["admin_email"],
                restaurant_admin_hashed_password=security.get_password_hash(rest_data["admin_password"])
            )
            db.add(restaurant)
            db.commit()
            db.refresh(restaurant)
            
            print(f"   ✅ {idx}. {rest_data['name']}")
            print(f"      📧 {rest_data['admin_email']} / {rest_data['admin_password']}")
        
        print("\n" + "=" * 50)
        print("🎉 Database Initialized Successfully!")
        print("=" * 50)
        print("\n📝 Credentials Summary:")
        print("\nSuper Admin:")
        print("  Email: admin@foodbutler.com")
        print("  Password: admin123")
        print("\nRestaurant Admins: See restaurant_credentials.txt")
        print("\n🌐 Login URLs:")
        print("  Admin: http://127.0.0.1:5500/frontend/admin.html")
        print("  Restaurant: http://localhost:5500/frontend/restaurant_management.html")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    init_database()
