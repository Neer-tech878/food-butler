#!/bin/bash
# fix_401_and_restart.sh - Apply 401 Fix and Restart Services

echo "🔧 Fixing 401 Authentication Error and Restarting Services"
echo "============================================================"
echo ""

# Check if Docker is available
if ! command -v docker &> /dev/null; then
    echo "❌ Docker not found. Please install Docker first."
    exit 1
fi

echo "📋 Step 1: Checking current status..."
docker compose ps
echo ""

echo "🔨 Step 2: Rebuilding AI agent with fixes..."
docker compose build agent-1
echo ""

echo "🚀 Step 3: Restarting AI agent..."
docker compose up -d agent-1
echo ""

echo "⏳ Step 4: Waiting for service to start (5 seconds)..."
sleep 5
echo ""

echo "📊 Step 5: Checking logs for successful startup..."
docker compose logs --tail=30 agent-1 | grep -E "SECRET_KEY|Application startup|Uvicorn running"
echo ""

echo "🧪 Step 6: Testing health endpoint..."
HEALTH_RESPONSE=$(curl -s http://localhost:8080/health)
if echo "$HEALTH_RESPONSE" | grep -q "healthy"; then
    echo "✅ Health check passed!"
    echo "$HEALTH_RESPONSE" | jq . 2>/dev/null || echo "$HEALTH_RESPONSE"
else
    echo "❌ Health check failed"
    echo "Response: $HEALTH_RESPONSE"
fi
echo ""

echo "✅ Service restarted with 401 fixes applied!"
echo ""
echo "📝 What was fixed:"
echo "   1. Extended CORS to allow all localhost ports"
echo "   2. Added request logging middleware"
echo "   3. Enhanced JWT error logging"
echo "   4. Fixed duplicate code in security.py"
echo "   5. Added /health and /test-auth endpoints"
echo ""
echo "🧪 Test authentication:"
echo "   ./test_ai_auth.sh"
echo ""
echo "📊 View logs:"
echo "   docker compose logs -f agent-1"
echo ""
echo "🌐 Try the chat now in your browser!"
