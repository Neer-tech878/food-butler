#!/bin/bash
# cleanup_project.sh - Remove unnecessary files from the project

echo "🧹 Food Butler Platform - Project Cleanup"
echo "=========================================="
echo ""

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

TOTAL_REMOVED=0
TOTAL_SIZE=0

# Function to safely remove file
remove_file() {
    local file="$1"
    if [ -f "$file" ]; then
        size=$(du -h "$file" | cut -f1)
        echo "  ❌ Removing: $file ($size)"
        rm "$file"
        TOTAL_REMOVED=$((TOTAL_REMOVED + 1))
    fi
}

# Function to safely remove directory
remove_dir() {
    local dir="$1"
    if [ -d "$dir" ]; then
        size=$(du -sh "$dir" | cut -f1)
        echo "  ❌ Removing: $dir/ ($size)"
        rm -rf "$dir"
        TOTAL_REMOVED=$((TOTAL_REMOVED + 1))
    fi
}

echo "📋 Category 1: Old Backup Files"
echo "--------------------------------"
cd /Users/jaswanthyamana/food_butler_platform/frontend
remove_file "admin_old_backup.html"
remove_file "demo_old_backup.html"
remove_file "index_old_backup.html"
echo ""

echo "📋 Category 2: Duplicate/Obsolete Documentation"
echo "------------------------------------------------"
cd /Users/jaswanthyamana/food_butler_platform
# Keep only the most comprehensive/recent docs, remove duplicates
remove_file "AI_BUTLER_401_FIX.md"  # Superseded by AUTH_401_FIX.md
remove_file "AI_BUTLER_FIXES.md"  # General fixes, covered by specific docs
remove_file "CART_500_FIX.md"  # Old fix
remove_file "CART_PRICE_FIX.md"  # Superseded by CART_DISPLAY_FIX.md
remove_file "CART_TOKEN_FIX.md"  # Old fix
remove_file "LOGIN_ISSUES_FIX.md"  # Covered by AUTH_401_FIX.md
remove_file "RESTAURANT_LOOP_FIX.md"  # Specific issue, already fixed
remove_file "STOCK_AVAILABILITY_FIX.md"  # Specific issue, already fixed
remove_file "DIRECT_ORDER_FIX.md"  # Specific issue, already fixed
remove_file "TOOL_CALLING_FIX.md"  # Old troubleshooting
remove_file "MIGRATION_FIX_GUIDE.md"  # Superseded by specific migration docs
remove_file "PROFILE_ADDRESS_SUMMARY.md"  # Duplicate of PROFILE_ADDRESS_FEATURE.md
remove_file "MANDATORY_ADDRESSES_SUMMARY.md"  # Duplicate of MANDATORY_ADDRESSES_MIGRATION.md
remove_file "DELIVERY_FEATURE_SUMMARY.md"  # Covered by DELIVERY_TRACKING_DOCUMENTATION.md
remove_file "UI_BEFORE_AFTER.md"  # Covered by UI_TRANSFORMATION_SUMMARY.md
echo ""

echo "📋 Category 3: Old Migration/Fix Scripts"
echo "-----------------------------------------"
remove_file "fix_customer_columns.sh"  # One-time fix, already applied
remove_file "quick_fix_database.sh"  # One-time fix
remove_file "quick_fix_customer_address.sql"  # One-time fix
remove_file "manual_address_migration.sql"  # One-time migration
remove_file "add_sample_tracking_data.py"  # Test data script, not needed in prod
remove_file "clear_database.py"  # Dangerous script, use with caution
echo ""

echo "📋 Category 4: Test Files (Keep if actively testing)"
echo "----------------------------------------------------"
echo "  ℹ️  Test files found (keeping for now):"
echo "     - test_*.py (6 files)"
echo "     - test_*.sh (2 files)"
echo "  💡 Remove manually if not needed: rm test_*.py test_*.sh"
echo ""

echo "📋 Category 5: Multiple Run Scripts (Consolidating)"
echo "---------------------------------------------------"
echo "  ℹ️  Multiple startup scripts found:"
echo "     - start_platform.sh (main)"
echo "     - start_services.sh"
echo "     - start_with_docker_db.sh"
echo "     - run_backend_manually.sh"
echo "     - run_ai_agent.sh"
echo "  💡 Consider keeping only: start_platform.sh"
echo ""

echo "📋 Category 6: System Files"
echo "---------------------------"
remove_file ".DS_Store"
remove_file "frontend/.DS_Store"
remove_file "ai_agent/.DS_Store"
remove_file "backend/.DS_Store"
echo ""

echo "📋 Category 7: Duplicate Virtual Environments"
echo "---------------------------------------------"
echo "  ⚠️  Found multiple venv directories:"
if [ -d "venv" ]; then
    echo "     - ./venv (project root)"
fi
if [ -d "backend/venv" ]; then
    echo "     - backend/venv"
fi
if [ -d "backend/.venv" ]; then
    echo "     - backend/.venv"
fi
if [ -d "ai_agent/venv" ]; then
    echo "     - ai_agent/venv"
fi
if [ -d "ai_agent/.venv" ]; then
    echo "     - ai_agent/.venv"
fi
echo "  💡 Recommendation: Use Docker instead of local venvs"
echo "  💡 To remove all venvs: find . -type d -name 'venv' -o -name '.venv' | xargs rm -rf"
echo ""

echo "📋 Category 8: Compiled Python Cache"
echo "------------------------------------"
cd /Users/jaswanthyamana/food_butler_platform
remove_dir ".pytest_cache"
remove_dir "ai_agent/__pycache__"
echo ""

echo "📋 Category 9: Unnecessary Test/Demo Files"
echo "------------------------------------------"
cd /Users/jaswanthyamana/food_butler_platform/frontend
remove_file "test_login.html"  # Test file, use main app instead
remove_file "demo.html"  # Demo file, use index.html instead
echo ""

echo "📋 Category 10: Pythagora Artifacts (External Tool)"
echo "---------------------------------------------------"
cd /Users/jaswanthyamana/food_butler_platform
if [ -d "pythagora-core" ]; then
    echo "  ⚠️  Found pythagora-core/ directory"
    echo "  💡 This appears to be from an external tool"
    echo "  💡 Safe to remove if not using Pythagora: rm -rf pythagora-core"
fi
echo ""

echo "=========================================="
echo "✅ Cleanup Complete!"
echo ""
echo "📊 Summary:"
echo "   Files/Dirs Removed: $TOTAL_REMOVED"
echo ""
echo "📝 Remaining Items to Review:"
echo "   1. Test files (test_*.py, test_*.sh)"
echo "   2. Multiple startup scripts"
echo "   3. Virtual environments (if using Docker)"
echo "   4. pythagora-core directory"
echo ""
echo "🎯 Recommended Project Structure After Cleanup:"
echo ""
echo "food_butler_platform/"
echo "├── docker-compose.yml           # Main Docker config"
echo "├── .env                          # Environment variables"
echo "├── start_platform.sh            # Main startup script"
echo "├── fix_401_and_restart.sh      # Auth fix script"
echo "├── test_ai_auth.sh             # Auth testing"
echo "├── ai_agent/              # AI service"
echo "│   ├── main_orchestrator.py"
echo "│   ├── tools.py"
echo "│   ├── security.py"
echo "│   ├── api_clients.py"
echo "│   ├── requirements.txt"
echo "│   └── Dockerfile.orchestrator"
echo "├── backend/         # Backend service"
echo "│   ├── app/"
echo "│   ├── alembic/"
echo "│   ├── requirements.txt"
echo "│   └── Dockerfile.backend"
echo "├── frontend/                    # Frontend"
echo "│   ├── index.html              # Main app"
echo "│   ├── admin.html              # Admin panel"
echo "│   └── restaurant_admin.html   # Restaurant admin"
echo "└── docs/                        # Documentation (optional)"
echo "    ├── AUTH_401_FIX.md"
echo "    ├── QUOTA_FIX_APPLIED.md"
echo "    ├── DELIVERY_TRACKING_DOCUMENTATION.md"
echo "    └── TWO_TIER_ADMIN_GUIDE.md"
echo ""
echo "💡 Optional: Create docs/ directory and move .md files there"
echo "   mkdir docs && mv *.md docs/"
echo ""
