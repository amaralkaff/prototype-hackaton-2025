#!/bin/bash
# Complete Automated Setup for Amara AI
# Runs everything end-to-end

set -e  # Exit on error

echo "🚀 AMARA AI - COMPLETE AUTOMATED SETUP"
echo "======================================"
echo ""

# Step 1: Check/create virtual environment
if [ ! -d "backend/venv" ]; then
    echo "📦 Creating virtual environment..."
    cd backend
    python3 -m venv venv
    cd ..
else
    echo "✅ Virtual environment exists"
fi

# Step 2: Activate virtual environment and install dependencies
echo "🔌 Activating virtual environment..."
source backend/venv/bin/activate

echo "📚 Installing dependencies..."
pip install --quiet --upgrade pip
pip install --quiet faker supabase python-dotenv

# Step 3: Generate CSV data if not exists
if [ ! -f "data/seed/borrowers_seed.csv" ]; then
    echo ""
    echo "🎲 Generating CSV dummy data..."
    python3 scripts/generate_dummy_data_csv.py
else
    echo "✅ CSV data already generated"
fi

# Step 4: Check database tables
echo ""
echo "🔍 Checking database status..."
python3 scripts/auto_setup_database.py

# Check if tables exist by running the check
if python3 -c "
import os, sys
from pathlib import Path
from supabase import create_client
from dotenv import load_dotenv

load_dotenv(Path('backend/.env'))
client = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_SERVICE_KEY'))

try:
    client.table('borrowers').select('id').limit(1).execute()
    sys.exit(0)  # Tables exist
except:
    sys.exit(1)  # Tables don't exist
" 2>/dev/null; then
    echo "✅ Database tables exist!"
    echo ""
    echo "🌱 Seeding database with CSV data..."
    python3 scripts/seed_database_csv.py

    echo ""
    echo "======================================"
    echo "✨ SETUP COMPLETE!"
    echo "======================================"
    echo ""
    echo "🎯 Next step: Start the server"
    echo ""
    echo "Run: cd backend/src && python3 app.py"
    echo "Then visit: http://localhost:8000"
    echo ""
else
    echo ""
    echo "======================================"
    echo "⚠️  ONE-TIME MANUAL STEP REQUIRED"
    echo "======================================"
    echo ""
    echo "Database tables need to be created (one-time only):"
    echo ""
    echo "Option 1 - Via Supabase Dashboard (Recommended):"
    echo "  1. Visit: https://supabase.com/dashboard/project/ogddxxdlhgjvgxfwmyjz"
    echo "  2. Click 'SQL Editor' in left sidebar"
    echo "  3. Click 'New Query'"
    echo "  4. Copy all contents from: docs/database_schema.sql"
    echo "  5. Paste and click 'Run'"
    echo ""
    echo "Option 2 - Quick Command (if you have database password):"
    echo "  Open docs/database_schema.sql in Supabase SQL Editor"
    echo ""
    echo "After completing either option, run this script again:"
    echo "  ./run_all.sh"
    echo ""
    echo "======================================"
fi
