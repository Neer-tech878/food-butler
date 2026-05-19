#!/bin/bash

# Test All Restaurant Logins
# Verifies that each restaurant can login and their name is returned correctly

echo "🧪 Testing All Restaurant Login Credentials"
echo "============================================"
echo ""

BACKEND_URL="http://localhost:8000"

# Array of restaurant credentials
declare -a RESTAURANTS=(
    "testrestaurant_7427@foodbutler.com:testrestaurant@7427:Test Restaurant"
    "chandrikafamilyrestaurant_7491@foodbutler.com:chandrikafamilyrestaurant@7491:Chandrika Family Restaurant"
    "spicemagic_4c34@foodbutler.com:spicemagic@4c34:Spice Magic"
    "chandrikatiffins_c8bb@foodbutler.com:chandrikatiffins@c8bb:Chandrika Tiffins"
    "deccanspice_ae5a@foodbutler.com:deccanspice@ae5a:Deccan Spice"
    "chandrikagrand_e1f6@foodbutler.com:chandrikagrand@e1f6:Chandrika Grand"
    "manager@testrestaurant.com:manager123:Test Restaurant Manager"
    "chef@demorestaurant.com:chef123:Demo Restaurant"
)

# Counter for successful logins
SUCCESS_COUNT=0
TOTAL_COUNT=${#RESTAURANTS[@]}

# Test each restaurant
for restaurant in "${RESTAURANTS[@]}"; do
    IFS=':' read -r email password expected_name <<< "$restaurant"
    
    echo "Testing: $expected_name"
    echo "  Email: $email"
    
    # Attempt login
    LOGIN_RESPONSE=$(curl -s -X POST "${BACKEND_URL}/restaurant-admin/token" \
        -H "Content-Type: application/json" \
        -d "{\"username\":\"${email}\",\"password\":\"${password}\"}")
    
    # Check if login successful
    TOKEN=$(echo $LOGIN_RESPONSE | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)
    
    if [ -z "$TOKEN" ]; then
        echo "  ❌ LOGIN FAILED"
        echo "  Response: $LOGIN_RESPONSE"
        echo ""
        continue
    fi
    
    echo "  ✅ Login successful"
    
    # Decode token to get restaurant ID
    PAYLOAD=$(echo $TOKEN | cut -d'.' -f2)
    # Add padding if needed
    PADDING=$((${#PAYLOAD} % 4))
    if [ $PADDING -ne 0 ]; then
        PAYLOAD="${PAYLOAD}$(printf '=%.0s' $(seq 1 $((4 - PADDING))))"
    fi
    
    RESTAURANT_ID=$(echo $PAYLOAD | base64 -d 2>/dev/null | grep -o '"restaurant_id":"[^"]*' | cut -d'"' -f4)
    
    if [ -z "$RESTAURANT_ID" ]; then
        echo "  ⚠️  Could not decode restaurant ID from token"
        echo ""
        continue
    fi
    
    echo "  Restaurant ID: $RESTAURANT_ID"
    
    # Fetch restaurant details
    RESTAURANT_DATA=$(curl -s "${BACKEND_URL}/restaurants/${RESTAURANT_ID}" \
        -H "Authorization: Bearer ${TOKEN}")
    
    # Extract restaurant name
    ACTUAL_NAME=$(echo $RESTAURANT_DATA | grep -o '"name":"[^"]*' | cut -d'"' -f4)
    
    if [ -z "$ACTUAL_NAME" ]; then
        echo "  ⚠️  Could not fetch restaurant name"
        echo "  Response: $RESTAURANT_DATA"
        echo ""
        continue
    fi
    
    echo "  📝 Restaurant Name: $ACTUAL_NAME"
    
    # Verify name matches
    if [ "$ACTUAL_NAME" = "$expected_name" ]; then
        echo "  ✅ NAME MATCHES EXPECTED!"
        SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
    else
        echo "  ⚠️  Name mismatch - Expected: $expected_name"
    fi
    
    echo "  ---"
    echo ""
done

echo "============================================"
echo "📊 Test Results: $SUCCESS_COUNT / $TOTAL_COUNT restaurants verified"
echo "============================================"
echo ""

if [ $SUCCESS_COUNT -eq $TOTAL_COUNT ]; then
    echo "🎉 SUCCESS! All restaurants can login and display their names correctly!"
else
    echo "⚠️  Some restaurants failed verification. Please check the output above."
fi
