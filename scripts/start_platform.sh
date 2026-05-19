#!/bin/bash

# Food Butler Platform Startup Script
# This script starts all services needed for the platform

echo "🚀 Starting Food Butler Platform..."
echo "=================================="

# Check if PostgreSQL is running
if ! lsof -i:5432 > /dev/null 2>&1; then
    echo "❌ PostgreSQL is not running on port 5432"
    echo ""
    echo "Please start PostgreSQL first:"
    echo "  - If using Homebrew: brew services start postgresql"
    echo "  - If using Postgres.app: Open the app and start the server"
    echo "  - If using system PostgreSQL: sudo systemctl start postgresql"
    echo ""
    exit 1
else
    echo "✅ PostgreSQL is running"
fi

# Kill any existing backend process
echo "🔄 Stopping existing backend..."
lsof -ti:8000 | xargs kill -9 2>/dev/null || true
sleep 2

# Start backend
echo "🚀 Starting backend on port 8000..."
cd backend
nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 > backend.log 2>&1 &
BACKEND_PID=$!
echo "   Backend PID: $BACKEND_PID"

# Wait for backend to start
sleep 3

# Check if backend is running
if lsof -i:8000 > /dev/null 2>&1; then
    echo "✅ Backend is running"
else
    echo "❌ Backend failed to start"
    echo "   Check backend.log for errors"
    exit 1
fi

echo ""
echo "=================================="
echo "✅ Food Butler Platform is ready!"
echo "=================================="
echo ""
echo "📊 Services:"
echo "   Backend API: http://localhost:8000"
echo "   Admin Panel: http://127.0.0.1:5500/frontend/admin.html"
echo ""
echo "🔐 Admin Credentials:"
echo "   Email: admin@foodbutler.com"
echo "   Password: admin123"
echo ""
echo "📝 Logs:"
echo "   Backend: backend/backend.log"
echo ""
echo "🛑 To stop services:"
echo "   lsof -ti:8000 | xargs kill -9"
echo ""
