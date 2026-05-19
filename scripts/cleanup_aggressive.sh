#!/bin/bash
# cleanup_aggressive.sh - More aggressive cleanup (optional)

echo "🧹 Food Butler Platform - AGGRESSIVE Cleanup"
echo "============================================="
echo ""
echo "⚠️  WARNING: This will remove:"
echo "   - All test files"
echo "   - Duplicate startup scripts"
echo "   - All virtual environments"
echo "   - pythagora-core directory"
echo ""
read -p "Are you sure? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo "❌ Cancelled"
    exit 0
fi

cd /Users/jaswanthyamana/food_butler_platform

echo ""
echo "🗑️  Step 1: Removing test files..."
rm -f test_*.py test_*.sh test_system.sh
echo "✅ Removed test files"

echo ""
echo "🗑️  Step 2: Removing duplicate startup scripts..."
rm -f start_services.sh run_backend_manually.sh run_ai_agent.sh run_docker_migration.sh
rm -f run_address_migration.sh run_profile_address_migration.sh start_venv.sh
echo "✅ Kept: start_platform.sh, start_with_docker_db.sh, stop_services.sh"

echo ""
echo "🗑️  Step 3: Removing virtual environments..."
rm -rf venv
rm -rf backend/venv
rm -rf backend/.venv
rm -rf ai_agent/venv
rm -rf ai_agent/.venv
echo "✅ Removed all venv directories"

echo ""
echo "🗑️  Step 4: Removing pythagora-core..."
rm -rf pythagora-core
echo "✅ Removed pythagora-core directory"

echo ""
echo "🗑️  Step 5: Removing old SQL migration files..."
rm -f add_delivery_columns.sql
echo "✅ Removed one-time migration files"

echo ""
echo "🗑️  Step 6: Removing admin scripts (use web interface instead)..."
rm -f create_admin.py create_restaurant_admin.py make_admin.py
echo "✅ Removed admin creation scripts"

echo ""
echo "📁 Step 7: Organizing documentation..."
mkdir -p docs
mv *.md docs/ 2>/dev/null
echo "✅ Moved all .md files to docs/ directory"

echo ""
echo "=========================================="
echo "✅ Aggressive Cleanup Complete!"
echo ""
echo "📊 Final Project Structure:"
tree -L 2 -I 'node_modules|*.pyc|__pycache__|alembic' . 2>/dev/null || find . -maxdepth 2 -not -path '*/\.*' -type f -o -type d | head -30
echo ""
echo "💡 Your project is now much cleaner!"
echo ""
