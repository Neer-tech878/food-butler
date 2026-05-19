#!/usr/bin/env python3
"""Test the full login flow"""

import sys
import os as _os

# Add backend package path relative to this tests folder
repo_root = _os.path.abspath(_os.path.join(_os.path.dirname(__file__), '..'))
backend_path = _os.path.join(repo_root, 'backend')
sys.path.insert(0, backend_path)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# Load environment variables from common locations (project root, backend/.env)
possible_envs = [
    _os.path.join(repo_root, '.env'),
    _os.path.join(backend_path, '.env'),
]
loaded = False
for p in possible_envs:
    if _os.path.exists(p):
        load_dotenv(p)
        loaded = True
        break
if not loaded:
    # fall back to default load (e.g., environment variables already set)
    load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print("DATABASE_URL not set — skipping full login test (set DATABASE_URL or provide a .env file)")
    raise SystemExit(0)

# Database connection
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

try:
    from app import models, security, crud
    
    # Test the login flow
    email = "admin@foodbutler.com"
    password = "admin123"
    
    print(f"Testing login for: {email}")
    
    # Step 1: Get customer by email
    customer = crud.get_customer_by_email(db, email=email)
    
    if not customer:
        print("✗ Customer not found")
    else:
        print(f"✓ Customer found: {customer.email}")
        print(f"  Name: {customer.name}")
        print(f"  Has password: {bool(customer.hashed_password)}")
        
        # Step 2: Verify password
        try:
            is_valid = security.verify_password(password, customer.hashed_password)
            print(f"✓ Password verification: {is_valid}")
            
            if is_valid:
                # Step 3: Create access token
                from datetime import timedelta
                access_token_expires = timedelta(minutes=security.ACCESS_TOKEN_EXPIRE_MINUTES)
                access_token = security.create_access_token(
                    data={"sub": customer.email}, 
                    expires_delta=access_token_expires
                )
                print(f"✓ Access token created (first 50 chars): {access_token[:50]}")
                print(f"\n✓✓✓ Full login flow successful!")
                print(f"\nToken: {access_token}")
            else:
                print("✗ Password verification failed")
                
        except Exception as e:
            print(f"✗ Error during password verification: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
    
except Exception as e:
    print(f"\n✗ Error: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
finally:
    db.close()
