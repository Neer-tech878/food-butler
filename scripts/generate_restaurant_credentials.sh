#!/bin/bash

# Generate Restaurant Credentials Script
# Creates unique login credentials for each restaurant

echo "🏪 Restaurant Credentials Generator"
echo "===================================="
echo ""

BACKEND_URL="http://localhost:8000"

# Login as admin
echo "Step 1: Authenticating as admin..."
ADMIN_EMAIL="admin@foodbutler.com"
ADMIN_PASSWORD="admin123"

LOGIN_RESPONSE=$(curl -s -X POST "${BACKEND_URL}/token" \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"${ADMIN_EMAIL}\",\"password\":\"${ADMIN_PASSWORD}\"}")

TOKEN=$(echo $LOGIN_RESPONSE | grep -o '"access_token":"[^"]*' | grep -o '[^"]*$')

if [ -z "$TOKEN" ]; then
    echo "❌ Failed to authenticate as admin"
    exit 1
fi

echo "✅ Authenticated successfully"
echo ""

# Fetch all restaurants
echo "Step 2: Fetching restaurants..."
RESTAURANTS=$(curl -s -H "Authorization: Bearer ${TOKEN}" "${BACKEND_URL}/restaurants/")

# Parse and process each restaurant
python3 - <<PYTHON_SCRIPT
import sys
import json
import re
import requests
import os

backend_url = "${BACKEND_URL}"
token = "${TOKEN}"

restaurants_json = '''${RESTAURANTS}'''
restaurants = json.loads(restaurants_json)

print(f"\nFound {len(restaurants)} restaurants\n")
print("=" * 80)

credentials_list = []

for idx, restaurant in enumerate(restaurants, 1):
    name = restaurant.get('name', '')
    rest_id = restaurant.get('id', '')
    current_email = restaurant.get('restaurant_admin_email')
    
    # Generate username from restaurant name
    # Remove special characters and spaces, convert to lowercase
    clean_name = re.sub(r'[^a-zA-Z0-9]', '', name.lower())
    
    # Create unique code (last 4 chars of restaurant ID)
    unique_code = rest_id[-4:]
    
    # Generate credentials
    username = f"{clean_name}_{unique_code}"
    email = f"{username}@foodbutler.com"
    password = f"{clean_name}@{unique_code}"
    
    print(f"\n{idx}. {name}")
    print(f"   ID: {rest_id}")
    print(f"   📧 Email: {email}")
    print(f"   🔑 Password: {password}")
    
    # Update restaurant with admin credentials (only if not already set)
    if not current_email or current_email == email:
        try:
            update_data = {
                "name": restaurant['name'],
                "cuisine": restaurant.get('cuisine', ''),
                "location": restaurant.get('location', ''),
                "address": restaurant.get('address', ''),
                "phone": restaurant.get('phone'),
                "email": restaurant.get('email'),
                "restaurant_admin_email": email,
                "restaurant_admin_password": password
            }
            
            response = requests.put(
                f"{backend_url}/admin/restaurants/{rest_id}",
                headers={
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json"
                },
                json=update_data
            )
            
            if response.status_code == 200:
                print(f"   ✅ Credentials updated in database")
            else:
                print(f"   ⚠️  Could not update: {response.status_code}")
                print(f"      Response: {response.text[:100]}")
        except Exception as e:
            print(f"   ⚠️  Error: {str(e)}")
    else:
        print(f"   ℹ️  Already has credentials: {current_email}")
    
    credentials_list.append({
        'name': name,
        'email': email,
        'password': password,
        'id': rest_id
    })
    print("-" * 80)

# Save credentials to file
print("\n" + "=" * 80)
print("Saving credentials to file...")

with open('restaurant_credentials.txt', 'w') as f:
    f.write("=" * 80 + "\n")
    f.write("RESTAURANT MANAGEMENT LOGIN CREDENTIALS\n")
    f.write("=" * 80 + "\n\n")
    f.write("URL: http://localhost:5500/frontend/restaurant_management.html\n\n")
    f.write("=" * 80 + "\n\n")
    
    for idx, cred in enumerate(credentials_list, 1):
        f.write(f"{idx}. {cred['name']}\n")
        f.write(f"   Email: {cred['email']}\n")
        f.write(f"   Password: {cred['password']}\n")
        f.write(f"   Restaurant ID: {cred['id']}\n")
        f.write("\n" + "-" * 80 + "\n\n")

print("✅ Credentials saved to: restaurant_credentials.txt")

# Create formatted credentials table
with open('restaurant_credentials.md', 'w') as f:
    f.write("# Restaurant Management Credentials\n\n")
    f.write("**Login URL:** http://localhost:5500/frontend/restaurant_management.html\n\n")
    f.write("## All Restaurant Admin Accounts\n\n")
    f.write("| # | Restaurant Name | Email | Password | Restaurant ID |\n")
    f.write("|---|----------------|-------|----------|---------------|\n")
    
    for idx, cred in enumerate(credentials_list, 1):
        f.write(f"| {idx} | {cred['name']} | `{cred['email']}` | `{cred['password']}` | `{cred['id'][-8:]}...` |\n")
    
    f.write("\n## Quick Copy Credentials\n\n")
    for idx, cred in enumerate(credentials_list, 1):
        f.write(f"### {idx}. {cred['name']}\n")
        f.write(f"```\n")
        f.write(f"Email: {cred['email']}\n")
        f.write(f"Password: {cred['password']}\n")
        f.write(f"```\n\n")

print("✅ Markdown credentials saved to: restaurant_credentials.md")
print("\n" + "=" * 80)

PYTHON_SCRIPT

echo ""
echo "🎉 Credential generation complete!"
echo ""
echo "📁 Files created:"
echo "  - restaurant_credentials.txt (Plain text)"
echo "  - restaurant_credentials.md (Markdown format)"
echo ""
echo "🔐 All restaurants now have unique login credentials"
echo ""
