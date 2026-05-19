#!/bin/bash
# restart_ai_agent.sh - Restart AI Agent with Quota Fixes

echo "🔧 Restarting Food Butler AI Agent with Quota Fixes..."
echo ""

# Check if running in Docker or manually
if command -v docker &> /dev/null; then
    echo "📦 Docker detected - restarting container..."
    docker compose restart agent-1
    echo "✅ Container restarted!"
    echo ""
    echo "📊 Checking logs..."
    docker compose logs --tail=20 agent-1
else
    echo "💻 Running manually - stopping and restarting..."
    
    # Kill existing process
    pkill -f "main_orchestrator.py" || echo "No existing process found"
    
    # Activate venv and restart
    cd /Users/jaswanthyamana/food_butler_platform
    source venv/bin/activate
    
    echo "🚀 Starting AI agent on port 8080..."
    cd ai_agent
    nohup python main_orchestrator.py > ai_agent.log 2>&1 &
    
    echo "✅ AI Agent started! PID: $!"
    echo ""
    echo "📊 Checking logs..."
    sleep 2
    tail -n 20 ai_agent.log
fi

echo ""
echo "✅ All done! AI Agent is running with these improvements:"
echo "   - 5 retry attempts (was 3)"
echo "   - Longer delays: 3s, 6s, 12s, 24s, 48s"
echo "   - Response caching (5 minute TTL)"
echo "   - Intelligent fallback messages"
echo ""
echo "Test it at: http://localhost:8080/chat"
