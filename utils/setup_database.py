#!/usr/bin/env python3
"""Create database tables and admin user for Food Butler"""

import sys
sys.path.insert(0, '/Users/jaswanthyamana/Downloads/food_butler_platform1/food_butler_backend')

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/Users/jaswanthyamana/Downloads/food_butler_platform1/food_butler_backend/.env')

DATABASE_URL = os.getenv("DATABASE_URL")
print(f"Using database: {DATABASE_URL}")

# Database connection
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

try:
    from app import models, security
    from app.database import Base
    
    print("\n🔨 Creating all database tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ Tables created successfully!")
    
    # Create admin user
    db = SessionLocal()
    try:
        admin_email = "admin@foodbutler.com"
        admin_password = "admin123"
        
        # Check if admin exists
        admin = db.query(models.Customer).filter(models.Customer.email == admin_email).first()
        
        if not admin:
            print(f"\n👤 Creating admin user: {admin_email}")
            admin = models.Customer(
                name="Admin User",
                email=admin_email,
                hashed_password=security.get_password_hash(admin_password),
                is_admin=True
            )
            db.add(admin)
            db.commit()
            print("✅ Admin user created successfully!")
        else:
            print(f"\n✓ Admin user already exists: {admin_email}")
            # Update password to ensure it's correct
            admin.hashed_password = security.get_password_hash(admin_password)
            db.commit()
            print("✅ Admin password updated!")
        
        print("\n" + "="*50)
        print("✅ Database setup complete!")
        print("="*50)
        print("\n📝 Login Credentials:")
        print(f"   Email:    {admin_email}")
        print(f"   Password: {admin_password}")
        print("\n🌐 Access the app at:")
        print("   http://127.0.0.1:5502/frontend/index.html")
        print("\n")
        
    finally:
        db.close()
        
except Exception as e:
    print(f"\n❌ Error: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
