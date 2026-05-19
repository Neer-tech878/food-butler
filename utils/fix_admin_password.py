#!/usr/bin/env python3
"""Script to reset the admin password with proper hashing"""

import sys
sys.path.insert(0, '/Users/jaswanthyamana/Downloads/food_butler_platform1/food_butler_backend')

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/Users/jaswanthyamana/Downloads/food_butler_platform1/food_butler_backend/.env')

DATABASE_URL = os.getenv("DATABASE_URL")
print(f"Connecting to database...")

# Database connection
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

try:
    # Import after setting up path
    from app import models, security
    
    # Find the admin user
    admin_email = "admin@foodbutler.com"
    admin = db.query(models.Customer).filter(models.Customer.email == admin_email).first()
    
    if admin:
        print(f"Found admin user: {admin.email}")
        print(f"Current hashed password (first 50 chars): {admin.hashed_password[:50] if admin.hashed_password else 'None'}")
        
        # Generate a new proper hash for the password "admin123"
        new_password = "admin123"
        new_hash = security.get_password_hash(new_password)
        
        print(f"\nNew hash generated (first 50 chars): {new_hash[:50]}")
        
        # Update the password
        admin.hashed_password = new_hash
        db.commit()
        
        print(f"✓ Password updated successfully!")
        
        # Verify it works
        db.refresh(admin)
        is_valid = security.verify_password(new_password, admin.hashed_password)
        print(f"✓ Verification test: {is_valid}")
        
        if is_valid:
            print("\n✓✓✓ Admin password reset successfully!")
            print(f"Email: {admin_email}")
            print(f"Password: {new_password}")
        else:
            print("\n✗ Verification failed!")
    else:
        print(f"✗ Admin user not found: {admin_email}")
        print("\nCreating new admin user...")
        
        from app import models, security
        
        admin = models.Customer(
            name="Admin User",
            email=admin_email,
            hashed_password=security.get_password_hash("admin123"),
            is_admin=True
        )
        db.add(admin)
        db.commit()
        print("✓ Admin user created successfully!")
        
except Exception as e:
    print(f"\n✗ Error: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
    db.rollback()
finally:
    db.close()
