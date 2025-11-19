#!/bin/bash

# Amara AI - Complete Setup Script
# Run this from the project root directory

set -e  # Exit on error

echo "🚀 Amara AI - Setup Script"
echo "=========================="
echo ""

# Check if virtual environment exists
if [ ! -d "backend/venv" ]; then
    echo "📦 Creating virtual environment..."
    cd backend
    python3 -m venv venv
    cd ..
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source backend/venv/bin/activate

# Install dependencies
echo "📚 Installing dependencies..."
pip install --quiet --upgrade pip
pip install --quiet faker supabase python-dotenv

echo ""
echo "✅ Dependencies installed!"
echo ""

# Check if .env exists
if [ ! -f "backend/.env" ]; then
    echo "⚠️  Warning: backend/.env file not found!"
    echo "Please copy backend/.env.example to backend/.env and configure it."
    echo ""
    read -p "Press Enter to continue or Ctrl+C to exit..."
fi

# Generate dummy data
echo "🎲 Generating dummy data (CSV format)..."
python3 scripts/generate_dummy_data_csv.py

echo ""
echo "=========================="
echo "✨ Setup Complete!"
echo "=========================="
echo ""
echo "Next steps:"
echo "1. Configure backend/.env with your Supabase and Gemini API credentials"
echo "2. Run the database schema in Supabase SQL Editor:"
echo "   - Copy contents of docs/database_schema.sql"
echo "   - Paste in Supabase SQL Editor and Run"
echo "3. Seed the database: python3 scripts/seed_database_csv.py"
echo "4. Start the server: cd backend/src && python3 app.py"
echo ""
echo "Note: Always activate the virtual environment first:"
echo "  source backend/venv/bin/activate"
echo ""
