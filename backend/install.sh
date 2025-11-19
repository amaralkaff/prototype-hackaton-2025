#!/bin/bash

# Installation script for Amara AI backend
# Run this after activating your virtual environment

echo "🚀 Installing Amara AI Backend Dependencies..."
echo ""

# Core web framework
pip install fastapi==0.104.1
pip install "uvicorn[standard]==0.24.0"
pip install python-multipart==0.0.6

# Data validation
pip install pydantic==2.5.0
pip install pydantic-settings==2.1.0

# Database (without psycopg2 - using Supabase client instead)
pip install sqlalchemy==2.0.23
pip install supabase==2.3.0

# Machine Learning
pip install scikit-learn==1.3.2
pip install pandas==2.1.3
pip install numpy==1.26.2
pip install joblib==1.3.2

# Google Gemini AI
pip install google-generativeai==0.3.1

# Utilities
pip install python-dotenv==1.0.0
pip install faker==20.1.0
pip install httpx==0.25.2
pip install pillow==10.1.0
pip install aiofiles==23.2.1
pip install loguru==0.7.2

echo ""
echo "✅ Installation complete!"
echo ""
echo "Next steps:"
echo "1. Configure .env file with your credentials"
echo "2. Run: python3 ../scripts/generate_dummy_data.py"
echo "3. Setup database schema in Supabase"
echo "4. Run: python3 ../scripts/seed_database.py"
echo "5. Start server: cd src && python3 app.py"
