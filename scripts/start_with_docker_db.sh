#!/bin/bash

# Start only PostgreSQL with Docker Compose
echo "🗄️  Starting PostgreSQL database with Docker..."

# Create a minimal docker-compose file for just the database
cat > docker-compose.db-only.yml << 'EOF'
services:
  db:
    image: postgres:15
    volumes:
      - postgres_data:/var/lib/postgresql/data/
    environment:
      - POSTGRES_DB=food_butler_db
      - POSTGRES_USER=food_butler_user
      - POSTGRES_PASSWORD=Jashwanth_2004
    ports:
      - "5432:5432"

volumes:
  postgres_data:
EOF

# Check if Docker Desktop is running
if ! docker ps > /dev/null 2>&1; then
    echo "❌ Docker Desktop is not running"
    echo "   Please start Docker Desktop and try again"
    exit 1
fi

# Start the database
docker compose -f docker-compose.db-only.yml up -d

echo "✅ PostgreSQL is starting..."
sleep 5

# Check if database is running
if docker ps | grep postgres:15 > /dev/null 2>&1; then
    echo "✅ PostgreSQL is running on port 5432"
else
    echo "❌ PostgreSQL failed to start"
    exit 1
fi

# Now start the backend locally
echo ""
echo "🚀 Starting backend..."
cd backend

# Kill any existing backend
lsof -ti:8000 | xargs kill -9 2>/dev/null || true
sleep 2

# Start backend
nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 > backend.log 2>&1 &
BACKEND_PID=$!

echo "   Backend PID: $BACKEND_PID"
sleep 3

# Check if backend is running
if lsof -i:8000 > /dev/null 2>&1; then
    echo "✅ Backend is running on port 8000"
else
    echo "❌ Backend failed to start"
    echo "   Check backend/backend.log for errors"
    exit 1
fi

cd ..

echo ""
echo "=================================="
echo "✅ Food Butler Platform is ready!"
echo "=================================="
echo ""
echo "📊 Services:"
echo "   Database: postgresql://localhost:5432/food_butler_db"
echo "   Backend API: http://localhost:8000"
echo "   Admin Panel: http://127.0.0.1:5500/frontend/admin.html"
echo ""
echo "🔐 Admin Credentials:"
echo "   Email: admin@foodbutler.com"
echo "   Password: admin123"
echo ""
echo "📝 Logs:"
echo "   Backend: backend/backend.log"
echo "   Database: docker compose -f docker-compose.db-only.yml logs db"
echo ""
echo "🛑 To stop services:"
echo "   lsof -ti:8000 | xargs kill -9"
echo "   docker compose -f docker-compose.db-only.yml down"
echo ""
