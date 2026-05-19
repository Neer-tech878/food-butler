#!/bin/bash

# Restaurant Management Setup Script
# This script helps create a test restaurant with admin access

echo "🍽️ Food Butler - Restaurant Management Setup"
echo "=============================================="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Backend URL
BACKEND_URL="http://localhost:8000"

echo -e "${YELLOW}Step 1: Check if backend is running...${NC}"
if curl -s "${BACKEND_URL}/" > /dev/null; then
    echo -e "${GREEN}✓ Backend is running${NC}"
else
    echo -e "${RED}✗ Backend is not running on port 8000${NC}"
    echo "Please start the backend first:"
    echo "  cd backend"
    echo "  uvicorn app.main:app --reload"
    exit 1
fi

echo ""
echo -e "${YELLOW}Step 2: Login as Super Admin${NC}"
echo "Enter super admin credentials (default: admin@foodbutler.com / admin123)"
read -p "Email [admin@foodbutler.com]: " ADMIN_EMAIL
ADMIN_EMAIL=${ADMIN_EMAIL:-admin@foodbutler.com}

read -sp "Password [admin123]: " ADMIN_PASSWORD
ADMIN_PASSWORD=${ADMIN_PASSWORD:-admin123}
echo ""

# Login to get token
echo -e "${YELLOW}Logging in...${NC}"
LOGIN_RESPONSE=$(curl -s -X POST "${BACKEND_URL}/token" \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"${ADMIN_EMAIL}\",\"password\":\"${ADMIN_PASSWORD}\"}")

TOKEN=$(echo $LOGIN_RESPONSE | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

if [ -z "$TOKEN" ]; then
    echo -e "${RED}✗ Login failed. Please check credentials.${NC}"
    echo "Response: $LOGIN_RESPONSE"
    exit 1
fi

echo -e "${GREEN}✓ Logged in successfully${NC}"

echo ""
echo -e "${YELLOW}Step 3: Create Test Restaurant${NC}"
read -p "Restaurant Name [Test Restaurant]: " REST_NAME
REST_NAME=${REST_NAME:-Test Restaurant}

read -p "Cuisine [Multi-cuisine]: " CUISINE
CUISINE=${CUISINE:-Multi-cuisine}

read -p "Location [Downtown]: " LOCATION
LOCATION=${LOCATION:-Downtown}

read -p "Restaurant Admin Email [manager@testrestaurant.com]: " REST_ADMIN_EMAIL
REST_ADMIN_EMAIL=${REST_ADMIN_EMAIL:-manager@testrestaurant.com}

read -sp "Restaurant Admin Password [manager123]: " REST_ADMIN_PASSWORD
REST_ADMIN_PASSWORD=${REST_ADMIN_PASSWORD:-manager123}
echo ""

# Create restaurant
echo -e "${YELLOW}Creating restaurant...${NC}"
CREATE_RESPONSE=$(curl -s -X POST "${BACKEND_URL}/restaurants/" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d "{
    \"name\":\"${REST_NAME}\",
    \"cuisine\":\"${CUISINE}\",
    \"location\":\"${LOCATION}\",
    \"address\":\"123 Test Street, ${LOCATION}\",
    \"phone\":\"+1234567890\",
    \"email\":\"${REST_ADMIN_EMAIL}\",
    \"restaurant_admin_email\":\"${REST_ADMIN_EMAIL}\",
    \"restaurant_admin_password\":\"${REST_ADMIN_PASSWORD}\"
  }")

RESTAURANT_ID=$(echo $CREATE_RESPONSE | grep -o '"id":"[^"]*' | cut -d'"' -f4)

if [ -z "$RESTAURANT_ID" ]; then
    echo -e "${RED}✗ Failed to create restaurant${NC}"
    echo "Response: $CREATE_RESPONSE"
    exit 1
fi

echo -e "${GREEN}✓ Restaurant created successfully!${NC}"
echo "Restaurant ID: $RESTAURANT_ID"

echo ""
echo -e "${YELLOW}Step 4: Add Sample Menu Items${NC}"

# Add sample menu items
MENU_ITEMS=(
    '{"name":"Classic Burger","description":"Juicy beef patty with fresh vegetables","price":250,"is_available":true}'
    '{"name":"Margherita Pizza","description":"Traditional Italian pizza with fresh mozzarella","price":350,"is_available":true}'
    '{"name":"Caesar Salad","description":"Fresh romaine lettuce with caesar dressing","price":180,"is_available":true}'
    '{"name":"Pasta Carbonara","description":"Creamy pasta with bacon and parmesan","price":280,"is_available":true}'
    '{"name":"Grilled Chicken","description":"Tender grilled chicken with herbs","price":320,"is_available":true}'
)

for ITEM in "${MENU_ITEMS[@]}"; do
    ITEM_WITH_REST=$(echo $ITEM | sed "s/}$/,\"restaurant_id\":\"${RESTAURANT_ID}\"}/")
    
    ITEM_NAME=$(echo $ITEM | grep -o '"name":"[^"]*' | cut -d'"' -f4)
    echo -n "Adding $ITEM_NAME... "
    
    ITEM_RESPONSE=$(curl -s -X POST "${BACKEND_URL}/admin/menu-items/" \
      -H "Authorization: Bearer ${TOKEN}" \
      -H "Content-Type: application/json" \
      -d "${ITEM_WITH_REST}")
    
    if echo $ITEM_RESPONSE | grep -q '"id"'; then
        echo -e "${GREEN}✓${NC}"
    else
        echo -e "${RED}✗${NC}"
    fi
done

echo ""
echo -e "${GREEN}=========================================${NC}"
echo -e "${GREEN}🎉 Setup Complete!${NC}"
echo -e "${GREEN}=========================================${NC}"
echo ""
echo "Restaurant Details:"
echo "  Name: ${REST_NAME}"
echo "  ID: ${RESTAURANT_ID}"
echo "  Admin Email: ${REST_ADMIN_EMAIL}"
echo "  Admin Password: ${REST_ADMIN_PASSWORD}"
echo ""
echo "Next Steps:"
echo "  1. Open: http://localhost:5500/frontend/restaurant_management.html"
echo "  2. Login with:"
echo "     Email: ${REST_ADMIN_EMAIL}"
echo "     Password: ${REST_ADMIN_PASSWORD}"
echo "  3. Start managing your restaurant!"
echo ""
echo -e "${YELLOW}Important: Save these credentials!${NC}"
