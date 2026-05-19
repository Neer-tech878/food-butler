#!/bin/bash

# Quick Restaurant Admin Creation Script
echo "🍽️ Creating Test Restaurant Admin..."

BACKEND_URL="http://localhost:8000"

# Use default super admin credentials
ADMIN_EMAIL="admin@foodbutler.com"
ADMIN_PASSWORD="admin123"

echo "Step 1: Logging in as super admin..."
LOGIN_RESPONSE=$(curl -s -X POST "${BACKEND_URL}/token" \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"${ADMIN_EMAIL}\",\"password\":\"${ADMIN_PASSWORD}\"}")

TOKEN=$(echo $LOGIN_RESPONSE | grep -o '"access_token":"[^"]*' | grep -o '[^"]*$')

if [ -z "$TOKEN" ]; then
    echo "❌ Could not login as super admin. Creating admin account first..."
    
    # Register admin account
    curl -s -X POST "${BACKEND_URL}/register" \
      -H "Content-Type: application/json" \
      -d "{\"name\":\"Admin\",\"email\":\"${ADMIN_EMAIL}\",\"password\":\"${ADMIN_PASSWORD}\"}" > /dev/null
    
    # Promote to admin
    curl -s -X POST "${BACKEND_URL}/promote-admin?email=${ADMIN_EMAIL}" > /dev/null
    
    # Login again
    LOGIN_RESPONSE=$(curl -s -X POST "${BACKEND_URL}/token" \
      -H "Content-Type: application/json" \
      -d "{\"username\":\"${ADMIN_EMAIL}\",\"password\":\"${ADMIN_PASSWORD}\"}")
    
    TOKEN=$(echo $LOGIN_RESPONSE | grep -o '"access_token":"[^"]*' | grep -o '[^"]*$')
fi

if [ -z "$TOKEN" ]; then
    echo "❌ Failed to authenticate. Please check backend is running."
    exit 1
fi

echo "✅ Authenticated successfully"

echo "Step 2: Creating restaurant..."

# Create restaurant with admin
CREATE_RESPONSE=$(curl -s -X POST "${BACKEND_URL}/restaurants/" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Demo Restaurant",
    "cuisine": "Multi-cuisine",
    "location": "Downtown",
    "address": "123 Main Street, Downtown",
    "phone": "+1234567890",
    "email": "contact@demorestaurant.com",
    "restaurant_admin_email": "chef@demorestaurant.com",
    "restaurant_admin_password": "chef123"
  }')

RESTAURANT_ID=$(echo $CREATE_RESPONSE | grep -o '"id":"[^"]*' | grep -o '[^"]*$')

if [ -z "$RESTAURANT_ID" ]; then
    echo "❌ Failed to create restaurant"
    echo "Response: $CREATE_RESPONSE"
    exit 1
fi

echo "✅ Restaurant created successfully!"
echo ""
echo "================================================"
echo "🎉 RESTAURANT ADMIN CREDENTIALS"
echo "================================================"
echo ""
echo "Restaurant Name: Demo Restaurant"
echo "Restaurant ID: $RESTAURANT_ID"
echo ""
echo "LOGIN CREDENTIALS:"
echo "  Email: chef@demorestaurant.com"
echo "  Password: chef123"
echo ""
echo "================================================"
echo ""
echo "Next Steps:"
echo "1. Open: http://localhost:5500/frontend/restaurant_management.html"
echo "2. Login with the credentials above"
echo "3. Start managing your restaurant!"
echo ""
echo "Alternative Pages:"
echo "- Super Admin: http://localhost:5500/frontend/admin.html"
echo "  Login: admin@foodbutler.com / admin123"
echo ""
echo "- Customer App: http://localhost:5500/frontend/index.html"
echo "  (Register a new account or login)"
echo ""

# Add some sample menu items
echo "Adding sample menu items..."

MENU_ITEMS='[
  {"name":"Classic Burger","description":"Juicy beef patty with fresh vegetables","price":250},
  {"name":"Margherita Pizza","description":"Traditional Italian pizza","price":350},
  {"name":"Caesar Salad","description":"Fresh romaine with caesar dressing","price":180},
  {"name":"Pasta Carbonara","description":"Creamy pasta with bacon","price":280},
  {"name":"Grilled Chicken","description":"Tender grilled chicken","price":320}
]'

echo "$MENU_ITEMS" | jq -c '.[]' | while read ITEM; do
    ITEM_NAME=$(echo $ITEM | jq -r '.name')
    ITEM_DESC=$(echo $ITEM | jq -r '.description')
    ITEM_PRICE=$(echo $ITEM | jq -r '.price')
    
    curl -s -X POST "${BACKEND_URL}/admin/menu-items/" \
      -H "Authorization: Bearer ${TOKEN}" \
      -H "Content-Type: application/json" \
      -d "{\"name\":\"${ITEM_NAME}\",\"description\":\"${ITEM_DESC}\",\"price\":${ITEM_PRICE},\"is_available\":true,\"restaurant_id\":\"${RESTAURANT_ID}\"}" > /dev/null
    
    echo "  ✓ Added: $ITEM_NAME"
done

echo ""
echo "✅ Setup complete! You can now login."
