# Amarta AI - Credit Scoring System

AI-powered credit assessment for micro-entrepreneurs using ML, Google Gemini Vision, and NLP.

## Quick Setup

### Backend Setup

```bash
# Navigate to backend
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
./install.sh

# Configure environment
cp .env.example .env
# Edit .env with your credentials (Supabase, Google Gemini API)

# Run backend
cd src
python3 app.py
```

Backend runs at: **http://localhost:8000**

### Frontend Setup

```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Configure environment
cp .env.example .env.local
# Edit .env.local with your API URL

# Run frontend
npm run dev
```

Frontend runs at: **http://localhost:3000**

## Environment Variables

### Backend (.env)
```env
SUPABASE_URL=https://YOUR_PROJECT.supabase.co
SUPABASE_KEY=your-supabase-anon-key
SUPABASE_SERVICE_KEY=your-supabase-service-role-key
DATABASE_URL=postgresql://postgres:PASSWORD@db.PROJECT.supabase.co:5432/postgres
GOOGLE_API_KEY=your-google-gemini-api-key
SECRET_KEY=your-secret-key
```

### Frontend (.env.local)
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Database Setup

1. Go to Supabase Dashboard → SQL Editor
2. Run the SQL from `docs/database_schema.sql`
3. Generate seed data: `python3 scripts/generate_dummy_data.py`
4. Seed database: `python3 scripts/seed_database.py`

## API Endpoints

- `POST /api/v1/credit-scoring/assess` - Credit assessment
- `GET /api/v1/borrowers` - List borrowers
- `GET /api/v1/loans` - List loans
- `GET /health` - Health check

## Team

- Luctfy Alkatiri Moehtar - Project Lead
- Farissthira S. - Data Engineer
- Gede Davon Ananda P. - Data Scientist
- Abu Ammar - Full Stack Developer
- Rajib Kurniawan - Business Strategist
