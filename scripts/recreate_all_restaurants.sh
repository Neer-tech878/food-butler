#!/bin/bash

# Recreate All Restaurants with Credentials
# This script will recreate all 8 restaurants with their unique login credentials

echo "🏪 Recreating All Restaurants with Credentials"
echo "==============================================="
echo ""

BACKEND_URL="http://localhost:8000"

# Login as admin
echo "Step 1: Authenticating as super admin..."
ADMIN_EMAIL="admin@foodbutler.com"
ADMIN_PASSWORD="admin123"

LOGIN_RESPONSE=$(curl -s -X POST "${BACKEND_URL}/token" \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"${ADMIN_EMAIL}\",\"password\":\"${ADMIN_PASSWORD}\"}")

TOKEN=$(echo $LOGIN_RESPONSE | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

if [ -z "$TOKEN" ]; then
    echo "❌ Failed to authenticate as admin"
    echo "Response: $LOGIN_RESPONSE"
    exit 1
fi

echo "✅ Authenticated successfully"
echo ""

# Restaurant data
declare -a RESTAURANTS=(
    "Test Restaurant|Indian Cuisine|Hyderabad|123 MG Road, Hyderabad|+91-40-1234-5678|test@restaurant.com|testrestaurant_7427@foodbutler.com|testrestaurant@7427"
    "Chandrika Family Restaurant|South Indian|Hyderabad|45 Jubilee Hills, Hyderabad|+91-40-2345-6789|contact@chandrikafamily.com|chandrikafamilyrestaurant_7491@foodbutler.com|chandrikafamilyrestaurant@7491"
    "Spice Magic|North Indian|Hyderabad|78 Banjara Hills, Hyderabad|+91-40-3456-7890|info@spicemagic.com|spicemagic_4c34@foodbutler.com|spicemagic@4c34"
    "Chandrika Tiffins|Breakfast & Snacks|Hyderabad|12 Ameerpet, Hyderabad|+91-40-4567-8901|orders@chandrikatiffins.com|chandrikatiffins_c8bb@foodbutler.com|chandrikatiffins@c8bb"
    "Deccan Spice|Hyderabadi Cuisine|Hyderabad|90 Somajiguda, Hyderabad|+91-40-5678-9012|hello@deccanspice.com|deccanspice_ae5a@foodbutler.com|deccanspice@ae5a"
    "Chandrika Grand|Multi-Cuisine|Hyderabad|56 Begumpet, Hyderabad|+91-40-6789-0123|reservations@chandrikagrand.com|chandrikagrand_e1f6@foodbutler.com|chandrikagrand@e1f6"
    "Test Restaurant Manager|International|Hyderabad|101 Hitech City, Hyderabad|+91-40-7890-1234|manager@testrestaurant.com|manager@testrestaurant.com|manager123"
    "Demo Restaurant|Italian & Continental|Hyderabad|202 Gachibowli, Hyderabad|+91-40-8901-2345|chef@demorestaurant.com|chef@demorestaurant.com|chef123"
)

echo "Step 2: Creating restaurants..."
echo ""

for restaurant_data in "${RESTAURANTS[@]}"; do
    IFS='|' read -r name cuisine location address phone email admin_email password <<< "$restaurant_data"
    
    echo "Creating: $name"
    
    # Create restaurant
    CREATE_RESPONSE=$(curl -s -X POST "${BACKEND_URL}/restaurants/" \
        -H "Authorization: Bearer ${TOKEN}" \
        -H "Content-Type: application/json" \
        -d "{
            \"name\": \"${name}\",
            \"cuisine\": \"${cuisine}\",
            \"location\": \"${location}\",
            \"address\": \"${address}\",
            \"phone\": \"${phone}\",
            \"email\": \"${email}\",
            \"restaurant_admin_email\": \"${admin_email}\",
            \"restaurant_admin_password\": \"${password}\"
        }")
    
    RESTAURANT_ID=$(echo $CREATE_RESPONSE | grep -o '"id":"[^"]*' | cut -d'"' -f4)
    
    if [ -z "$RESTAURANT_ID" ]; then
        echo "  ⚠️  Failed to create restaurant"
        echo "  Response: $CREATE_RESPONSE"
    else
        echo "  ✅ Created with ID: ${RESTAURANT_ID:0:8}..."
        echo "  📧 Admin Email: ${admin_email}"
        echo "  🔑 Password: ${password}"
    fi
    
    echo ""
done

echo "==============================================="
echo "🎉 All restaurants recreated successfully!"
echo "==============================================="
echo ""
echo "📝 Test login at: http://localhost:5500/frontend/restaurant_management.html"
echo ""
