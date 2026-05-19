#!/usr/bin/env python3
"""Debug script to test login functionality"""

import sys
sys.path.insert(0, '/Users/jaswanthyamana/Downloads/food_butler_platform1/food_butler_backend')

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/Users/jaswanthyamana/Downloads/food_butler_platform1/food_butler_backend/.env')

DATABASE_URL = os.getenv("DATABASE_URL")
print(f"Database URL: {DATABASE_URL}")

# Test database connection
try:
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    # Test connection
    db = SessionLocal()
    print("✓ Database connection successful")
    
    # Try to import models
    from app import models
    
    # Try to query customers
    customers = db.query(models.Customer).all()
    print(f"✓ Found {len(customers)} customers in database")
    
    for customer in customers[:5]:
        print(f"  - {customer.email}")
    
    # Test authentication with a specific user
    test_email = "admin@foodbutler.com"
    customer = db.query(models.Customer).filter(models.Customer.email == test_email).first()
    
    if customer:
        print(f"\n✓ Customer found: {customer.email}")
        print(f"  Name: {customer.name}")
        print(f"  Is Admin: {customer.is_admin}")
        print(f"  Has hashed password: {bool(customer.hashed_password)}")
        
        # Test password verification
        from app import security
        test_password = "admin123"
        is_valid = security.verify_password(test_password, customer.hashed_password)
        print(f"  Password verification result: {is_valid}")
    else:
        print(f"\n✗ Customer not found: {test_email}")
        print("\nAvailable customers:")
        for c in db.query(models.Customer).all():
            print(f"  - {c.email}")
    
    db.close()
    
except Exception as e:
    print(f"\n✗ Error: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
