#!/bin/bash
# test_ai_auth.sh - Test AI Agent Authentication

echo "🔧 Testing Food Butler AI Agent Authentication"
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test 1: Health Check (no auth required)
echo "📊 Test 1: Health Check (no authentication)"
echo "curl http://localhost:8080/health"
HEALTH_RESPONSE=$(curl -s http://localhost:8080/health)
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Health check passed${NC}"
    echo "$HEALTH_RESPONSE" | jq . 2>/dev/null || echo "$HEALTH_RESPONSE"
else
    echo -e "${RED}❌ Health check failed - is the service running?${NC}"
    echo "Start the service with: docker compose up agent-1"
    exit 1
fi
echo ""

# Test 2: Check if user is logged in
echo "📋 Test 2: Checking for stored auth token"
if [ -f ~/.food_butler_test_token ]; then
    TOKEN=$(cat ~/.food_butler_test_token)
    echo -e "${GREEN}✅ Found test token${NC}"
    echo "Token preview: ${TOKEN:0:30}..."
else
    echo -e "${YELLOW}⚠️  No test token found. You need to log in first.${NC}"
    echo ""
    echo "Open your browser, log in to the app, and then:"
    echo "1. Open browser DevTools (F12)"
    echo "2. Go to Console tab"
    echo "3. Run: localStorage.getItem('foodButlerToken')"
    echo "4. Copy the token (without quotes)"
    echo "5. Save it: echo 'YOUR_TOKEN_HERE' > ~/.food_butler_test_token"
    echo ""
    read -p "Press Enter after saving the token, or Ctrl+C to exit: "
    
    if [ -f ~/.food_butler_test_token ]; then
        TOKEN=$(cat ~/.food_butler_test_token)
    else
        echo -e "${RED}❌ Token file not found${NC}"
        exit 1
    fi
fi
echo ""

# Test 3: Test authentication endpoint
echo "🔐 Test 3: Testing authentication with token"
echo "curl -H 'Authorization: Bearer TOKEN' http://localhost:8080/test-auth"
AUTH_RESPONSE=$(curl -s -H "Authorization: Bearer $TOKEN" http://localhost:8080/test-auth)
AUTH_STATUS=$?

if [ $AUTH_STATUS -eq 0 ]; then
    # Check if response contains "authenticated"
    if echo "$AUTH_RESPONSE" | grep -q "authenticated"; then
        echo -e "${GREEN}✅ Authentication test passed${NC}"
        echo "$AUTH_RESPONSE" | jq . 2>/dev/null || echo "$AUTH_RESPONSE"
    else
        echo -e "${RED}❌ Authentication failed${NC}"
        echo "Response: $AUTH_RESPONSE"
        echo ""
        echo "Possible issues:"
        echo "1. Token expired - log in again"
        echo "2. SECRET_KEY mismatch between backend and AI agent"
        echo "3. Token format incorrect"
    fi
else
    echo -e "${RED}❌ Request failed${NC}"
fi
echo ""

# Test 4: Test chat endpoint
echo "💬 Test 4: Testing chat endpoint with authentication"
echo "curl -H 'Authorization: Bearer TOKEN' -H 'Content-Type: application/json' \\"
echo "     -d '{\"user_input\":\"hello\",\"session_id\":\"test123\"}' \\"
echo "     http://localhost:8080/chat"

CHAT_RESPONSE=$(curl -s -X POST \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"user_input":"hello","session_id":"test123"}' \
    http://localhost:8080/chat)
CHAT_STATUS=$?

if [ $CHAT_STATUS -eq 0 ]; then
    if echo "$CHAT_RESPONSE" | grep -q "response"; then
        echo -e "${GREEN}✅ Chat endpoint test passed${NC}"
        echo "$CHAT_RESPONSE" | jq . 2>/dev/null || echo "$CHAT_RESPONSE"
    else
        echo -e "${RED}❌ Chat endpoint test failed${NC}"
        echo "Response: $CHAT_RESPONSE"
    fi
else
    echo -e "${RED}❌ Chat request failed${NC}"
fi
echo ""

echo "📊 Test Summary"
echo "==============="
echo "If all tests passed, authentication is working correctly! ✅"
echo "If tests failed, check the agent-1 logs: docker compose logs agent-1"
echo ""
echo "Common fixes:"
echo "1. Restart AI agent: docker compose restart agent-1"
echo "2. Check SECRET_KEY matches: docker compose exec agent-1 printenv SECRET_KEY"
echo "3. Get fresh token: Log out and log in again in the app"
