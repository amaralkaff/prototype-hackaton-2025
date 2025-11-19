# 🚀 Amara AI - Quick Start Guide

## Step 1: Activate Virtual Environment

```bash
cd backend
source venv/bin/activate
```

You should see `(venv)` in your terminal prompt.

## Step 2: Install Dependencies

```bash
pip install faker supabase python-dotenv
```

## Step 3: Go Back to Project Root

```bash
cd ..
```

## Step 4: Generate CSV Data

```bash
python3 scripts/generate_dummy_data_csv.py
```

Expected output:
```
🚀 Starting CSV data generation...
👤 Generating borrowers...
💰 Generating loans...
💳 Generating repayments...
📸 Generating photo metadata...
📝 Generating field notes...
✅ Generated 75 borrowers
✅ Generated ~150 loans
✅ Generated ~3000 repayments
✅ Generated ~200 photos
✅ Generated ~100 field notes
```

## Step 5: Verify CSV Files Were Created

```bash
ls -lh data/seed/
```

You should see:
- `borrowers_seed.csv`
- `loans_seed.csv`
- `repayments_seed.csv`
- `photos_seed.csv`
- `field_notes_seed.csv`

Open them in Excel or Numbers to inspect!

## Step 6: Configure .env File

```bash
nano backend/.env
```

Update these values:
```env
SUPABASE_URL=https://ogddxxdlhgjvgxfwmyjz.supabase.co
SUPABASE_KEY=your-anon-key-from-dashboard
SUPABASE_SERVICE_KEY=your-service-role-key
GOOGLE_API_KEY=AIzaSyDfMD4_j7eTuvpku8apQa0WvhvLenVtr3o
```

Get Supabase keys from:
https://supabase.com/dashboard/project/YOUR_PROJECT/settings/api

## Step 7: Setup Database Schema

1. Go to https://supabase.com/dashboard
2. Select your project
3. Click **SQL Editor** (left sidebar)
4. Copy entire contents of `docs/database_schema.sql`
5. Paste and click **Run**

This creates all tables.

## Step 8: Seed the Database

```bash
python3 scripts/seed_database_csv.py
```

Expected output:
```
🌱 STARTING DATABASE SEEDING (CSV)
Seeding borrowers...
✅ Successfully seeded 75 borrowers
Seeding loans...
✅ Successfully seeded ~150 loans
...
✨ DATABASE SEEDING COMPLETE!
```

## Step 9: Start the Server

```bash
cd backend/src
python3 app.py
```

Visit: http://localhost:8000

## Test the API

```bash
# Health check
curl http://localhost:8000/health

# API info
curl http://localhost:8000/api/v1/info
```

---

## Troubleshooting

### "pip: command not found"
**Fix**: Activate virtual environment first
```bash
cd backend
source venv/bin/activate
```

### "No module named 'faker'"
**Fix**: Install in virtual environment
```bash
source backend/venv/bin/activate
pip install faker supabase
```

### "SUPABASE_URL must be set"
**Fix**: Configure .env file
```bash
cp backend/.env.example backend/.env
nano backend/.env
```

### Database seeding fails
**Fix**: Check Supabase credentials
1. Verify SUPABASE_URL and SUPABASE_SERVICE_KEY in .env
2. Ensure database schema was created
3. Check logs for specific error

---

## Quick Command Reference

```bash
# Always activate venv first!
source backend/venv/bin/activate

# Generate data
python3 scripts/generate_dummy_data_csv.py

# Seed database
python3 scripts/seed_database_csv.py

# Clear and re-seed
python3 scripts/seed_database_csv.py --clear

# Start server
cd backend/src && python3 app.py

# Deactivate venv when done
deactivate
```

---

## Data Files Location

All CSV files are in `data/seed/`:
- Open in Excel/Numbers to view
- Edit manually if needed
- Re-run seeding script to update database

---

## Next: Add API Routes

Once basic setup works, you can add API endpoints for:
- Borrower CRUD
- Loan management
- Credit scoring assessment

See README.md for full documentation.
