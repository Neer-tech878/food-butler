#!/bin/bash

# Food Butler Platform - Service Stop Script

echo "🛑 Stopping Food Butler Services..."

# Read PIDs from file if exists
if [ -f /tmp/food_butler_pids.txt ]; then
    PIDS=$(cat /tmp/food_butler_pids.txt)
    echo "Stopping services with PIDs: $PIDS"
    kill $PIDS 2>/dev/null
    rm /tmp/food_butler_pids.txt
fi

# Kill by port as backup
lsof -ti:8000 | xargs kill -9 2>/dev/null
lsof -ti:8080 | xargs kill -9 2>/dev/null
lsof -ti:5500 | xargs kill -9 2>/dev/null

echo "✅ All services stopped"
