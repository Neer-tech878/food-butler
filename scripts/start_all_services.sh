#!/bin/bash

# Food Butler Complete Platform Startup Script
# Starts Backend + AI Agent

echo "🚀 Starting Complete Food Butler Platform..."
echo "=============================================="
echo ""

# Check PostgreSQL
if ! lsof -i:5432 > /dev/null 2>&1; then
    echo "❌ PostgreSQL is not running on port 5432"
    echo "Please start PostgreSQL first"
    exit 1
else
    echo "✅ PostgreSQL is running"
fi

# Stop existing services
echo ""
echo "🔄 Stopping existing services..."
lsof -ti:8000 | xargs kill -9 2>/dev/null || true
lsof -ti:8080 | xargs kill -9 2>/dev/null || true
pkill -f "main_orchestrator.py" 2>/dev/null || true
sleep 2

# Start Backend
echo ""
echo "🚀 Starting Backend on port 8000..."
cd backend
nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 > backend.log 2>&1 &
BACKEND_PID=$!
cd ..

# Wait for backend
sleep 3

if lsof -i:8000 > /dev/null 2>&1; then
    echo "✅ Backend is running (PID: $BACKEND_PID)"
else
    echo "❌ Backend failed to start"
    echo "Check backend/backend.log for errors"
    exit 1
fi

# Start AI Agent
echo ""
echo "🤖 Starting AI Agent on port 8080..."
cd ai_agent
nohup python main_orchestrator.py > ai_agent.log 2>&1 &
AI_PID=$!
cd ..

# Wait for AI agent
sleep 3

if lsof -i:8080 > /dev/null 2>&1; then
    echo "✅ AI Agent is running (PID: $AI_PID)"
else
    echo "❌ AI Agent failed to start"
    echo "Check ai_agent/ai_agent.log for errors"
    exit 1
fi

echo ""
echo "=============================================="
echo "✅ Food Butler Platform is fully ready!"
echo "=============================================="
echo ""
echo "📊 Services:"
echo "   Backend API:  http://localhost:8000"
echo "   AI Agent:     http://localhost:8080"
echo "   Frontend:     http://127.0.0.1:5502/frontend/index.html"
echo "   Admin Panel:  http://127.0.0.1:5502/frontend/admin.html"
echo ""
echo "🔐 Admin Credentials:"
echo "   Email:    admin@foodbutler.com"
echo "   Password: admin123"
echo ""
echo "📝 Logs:"
echo "   Backend:  backend/backend.log"
echo "   AI Agent: ai_agent/ai_agent.log"
echo ""
echo "🛑 To stop all services:"
echo "   lsof -ti:8000 | xargs kill -9"
echo "   lsof -ti:8080 | xargs kill -9"
echo ""
