# Amara AI - Multimodal Credit Scoring System

**AI-powered credit assessment for micro-entrepreneurs in rural Indonesia**

Amara AI combines Machine Learning, Google Gemini Vision, and NLP to provide fair, accurate, and explainable credit scoring for women-led micro-businesses.

## 🎯 Key Features

- **Adaptive Credit Scoring Engine**: Fuses ML predictions with AI-generated insights
- **Income Reality Check**: Compares claimed vs AI-estimated income
- **Visual Socioeconomic Indicators**: Analyzes business/house photos
- **Risk Explanation Layer**: Generates human-readable explanations
- **Loan Recommendation Engine**: Suggests optimal loan amounts

## 🏗️ Architecture

```
┌─────────────────┐
│  Borrower Data  │
│  Photos         │◄──────┐
│  Field Notes    │       │
└────────┬────────┘       │
         │                │
         ▼                │
┌─────────────────────────┴──────┐
│   Adaptive Scoring Engine      │
│                                 │
│  ┌──────────────────────────┐  │
│  │  ML Risk Model           │  │
│  │  (Scikit-learn)          │  │
│  └──────────────────────────┘  │
│           │                     │
│           ▼                     │
│  ┌──────────────────────────┐  │
│  │  Gemini Vision API       │  │
│  │  (Photo Analysis)        │  │
│  └──────────────────────────┘  │
│           │                     │
│           ▼                     │
│  ┌──────────────────────────┐  │
│  │  Gemini NLP API          │  │
│  │  (Field Note Extraction) │  │
│  └──────────────────────────┘  │
│           │                     │
│           ▼                     │
│  ┌──────────────────────────┐  │
│  │  Score Fusion Logic      │  │
│  └──────────────────────────┘  │
└─────────────┬───────────────────┘
              │
              ▼
┌─────────────────────────────────┐
│   Credit Assessment Result      │
│  - Final Score (0-100)          │
│  - Risk Category                │
│  - Income Validation            │
│  - Loan Recommendation          │
│  - Risk Explanation             │
└─────────────────────────────────┘
```

## 📋 Prerequisites

- **Python 3.9+**
- **PostgreSQL** (via Supabase)
- **Google Gemini API Key** ([Get it here](https://makersuite.google.com/app/apikey))
- **Supabase Account** ([Sign up](https://supabase.com))

## 🚀 Quick Start

### 1. Clone & Navigate

```bash
cd prototype-amarta-ai
```

### 2. Set Up Python Environment

```bash
cd backend

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies (using install script - easier than requirements.txt)
./install.sh

# OR install manually:
# pip install fastapi "uvicorn[standard]" pydantic pydantic-settings
# pip install sqlalchemy supabase google-generativeai
# pip install scikit-learn pandas numpy faker python-dotenv loguru
```

### 3. Configure Environment Variables

```bash
# Copy example env file
cp backend/.env.example backend/.env

# Edit .env with your credentials
nano backend/.env
```

**Required Environment Variables:**

```env
# Supabase (Get from https://supabase.com/dashboard/project/YOUR_PROJECT/settings/api)
SUPABASE_URL=https://YOUR_PROJECT.supabase.co
SUPABASE_KEY=your-supabase-anon-key
SUPABASE_SERVICE_KEY=your-supabase-service-role-key
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@db.YOUR_PROJECT.supabase.co:5432/postgres

# Google Gemini AI (Get from https://makersuite.google.com/app/apikey)
GOOGLE_API_KEY=your-google-gemini-api-key

# Security
SECRET_KEY=your-secret-key-change-this-in-production
```

### 4. Set Up Database

**Option A: Using Supabase Dashboard (Recommended)**

1. Go to your Supabase project dashboard
2. Navigate to **SQL Editor**
3. Copy and paste the contents of `docs/database_schema.sql`
4. Click **Run** to execute

**Option B: Using psql CLI**

```bash
psql $DATABASE_URL -f docs/database_schema.sql
```

### 5. Generate Dummy Data

```bash
python3 scripts/generate_dummy_data.py
```

This creates:
- 75 diverse borrower profiles
- Realistic loan histories (good, medium, risky)
- Field agent narratives in Indonesian
- Photo metadata

Output files in `data/seed/`:
- `borrowers_seed.json`
- `loans_seed.json`
- `repayments_seed.json`
- `photos_seed.json`
- `field_notes_seed.json`

### 6. Seed Database

```bash
# TODO: Create seeding script
python3 scripts/seed_database.py
```

### 7. Run the API Server

```bash
cd backend/src
python3 app.py
```

Server starts at: **http://localhost:8000**

### 8. Test the API

```bash
# Health check
curl http://localhost:8000/health

# API info
curl http://localhost:8000/api/v1/info

# Test credit scoring (after seeding data)
curl -X POST http://localhost:8000/api/v1/credit-scoring/assess \
  -H "Content-Type: application/json" \
  -d '{"borrower_id": "uuid-here", "include_vision": true, "include_nlp": true}'
```

## 📁 Project Structure

```
prototype-amarta-ai/
├── backend/
│   ├── src/
│   │   ├── api/routes/          # API endpoints
│   │   ├── services/
│   │   │   ├── ml_model/        # Credit risk ML model
│   │   │   ├── gemini/          # Vision & NLP services
│   │   │   └── scoring/         # Adaptive scoring engine
│   │   ├── models/              # SQLAlchemy ORM models
│   │   ├── utils/               # Config, validators, logger
│   │   └── app.py               # FastAPI application
│   ├── requirements.txt
│   └── .env.example
├── data/
│   ├── seed/                    # Generated dummy data (JSON)
│   └── sample_images/           # Sample business/house photos
├── scripts/
│   ├── generate_dummy_data.py   # Data generation script
│   └── seed_database.py         # Database seeding script
├── docs/
│   ├── database_schema.sql      # Complete DB schema
│   └── API_SPEC.md              # API documentation (TODO)
└── README.md
```

## 🔑 Core Services

### 1. **ML Credit Risk Model** (`services/ml_model/credit_risk_model.py`)

- **Algorithm**: Random Forest Classifier
- **Features**: Repayment history, demographics, business type, financial literacy
- **Fallback**: Rule-based scoring when model unavailable
- **Output**: Baseline score (0-100), risk category, confidence

### 2. **Gemini Vision Analyzer** (`services/gemini/vision_analyzer.py`)

- **Input**: Business/house photos
- **Analysis**:
  - Business scale (small/medium/large)
  - Inventory density (low/moderate/high)
  - Asset quality (poor/fair/good/excellent)
  - Socioeconomic indicators
- **Output**: Score adjustment (-15 to +15), confidence, insights

### 3. **Gemini NLP Extractor** (`services/gemini/nlp_extractor.py`)

- **Input**: Field agent notes (Indonesian text)
- **Analysis**:
  - Income estimation from narratives
  - Sentiment analysis
  - Risk flags extraction
  - Behavioral insights
- **Output**: Score adjustment (-15 to +15), confidence, insights

### 4. **Adaptive Scoring Engine** (`services/scoring/adaptive_engine.py`)

- **Orchestration**: Combines ML + Vision + NLP
- **Fusion Logic**: `Final = Baseline + (Vision * 0.5) + (NLP * 0.5)`
- **Features**:
  - Income validation (claimed vs AI-estimated)
  - Loan recommendation with justification
  - Risk explanation generation
  - Risk & positive factors extraction

## 📊 API Endpoints

### Borrowers

```bash
POST   /api/v1/borrowers              # Create borrower
GET    /api/v1/borrowers              # List borrowers
GET    /api/v1/borrowers/:id          # Get borrower details
PUT    /api/v1/borrowers/:id          # Update borrower
DELETE /api/v1/borrowers/:id          # Delete borrower
```

### Credit Scoring

```bash
POST   /api/v1/credit-scoring/assess  # Perform comprehensive assessment
GET    /api/v1/credit-scoring/:id     # Get assessment results
```

**Example Assessment Request:**

```json
{
  "borrower_id": "uuid-here",
  "include_vision": true,
  "include_nlp": true
}
```

**Example Assessment Response:**

```json
{
  "borrower_id": "uuid-here",
  "ml_baseline_score": 68.5,
  "ml_model_version": "1.0.0",
  "vision_score_adjustment": 5.2,
  "vision_confidence": 0.82,
  "nlp_score_adjustment": -3.1,
  "nlp_confidence": 0.78,
  "final_credit_score": 70.6,
  "risk_category": "medium",
  "income_validation": {
    "claimed_income": 2500000,
    "ai_estimated_income": 2100000,
    "income_consistency_score": 62,
    "variance_percentage": -16,
    "assessment": "Claimed income slightly higher than AI estimate"
  },
  "loan_recommendation": {
    "recommended_loan_amount": 4000000,
    "max_safe_loan_amount": 5000000,
    "recommended_term_weeks": 20,
    "weekly_repayment": 200000,
    "repayment_to_income_ratio": 20.5,
    "recommendation_confidence": 0.75,
    "justification": "Based on medium risk profile..."
  },
  "risk_explanation": "Ibu Ratna menunjukkan profil risiko menengah...",
  "risk_factors": [...],
  "positive_factors": [...]
}
```

## 🧪 Testing

### Manual Testing

```bash
# Test ML model (rule-based fallback)
python3 backend/src/services/ml_model/credit_risk_model.py

# Test Vision analysis (requires API key)
python3 backend/src/services/gemini/vision_analyzer.py

# Test NLP extraction (requires API key)
python3 backend/src/services/gemini/nlp_extractor.py
```

### API Testing

Use tools like:
- **Postman** ([Download](https://www.postman.com/downloads/))
- **Insomnia** ([Download](https://insomnia.rest/download))
- **curl** (command line)

## 📈 Next Steps

### Immediate (Week 1-2)

- [ ] Create database seeding script (`scripts/seed_database.py`)
- [ ] Implement API routes (`backend/src/api/routes/`)
- [ ] Add sample business/house images (`data/sample_images/`)
- [ ] Test end-to-end credit scoring flow
- [ ] Document API endpoints (`docs/API_SPEC.md`)

### Short-term (Week 3-4)

- [ ] Train ML model with real data
- [ ] Build simple React/Next.js dashboard
- [ ] Add authentication & authorization
- [ ] Implement audit logging
- [ ] Performance optimization

### Medium-term (Month 2-3)

- [ ] Deploy to production (GCP/AWS)
- [ ] Add monitoring & alerting
- [ ] Batch processing for large assessments
- [ ] Integration with Amartha systems
- [ ] User acceptance testing

## 🔒 Security Notes

- **Never commit `.env` file** (already in `.gitignore`)
- **Rotate API keys regularly**
- **Use service role key only in backend** (never expose to frontend)
- **Implement rate limiting** for production
- **Add request validation** for all endpoints

## 🐛 Troubleshooting

### Import Errors

```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r backend/requirements.txt --force-reinstall
```

### Database Connection Issues

```bash
# Test connection
psql $DATABASE_URL -c "SELECT 1;"

# Verify credentials in .env
cat backend/.env | grep DATABASE_URL
```

### Gemini API Errors

```bash
# Verify API key
curl "https://generativelanguage.googleapis.com/v1/models?key=YOUR_API_KEY"

# Check quota
# Visit: https://makersuite.google.com/app/apikey
```

## 📚 Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Google Gemini API](https://ai.google.dev/)
- [Supabase Documentation](https://supabase.com/docs)
- [Scikit-learn Guide](https://scikit-learn.org/stable/user_guide.html)

## 👥 Team

- **Luctfy Alkatiri Moehtar** - Project Lead
- **Farissthira S.** - Data Engineer
- **Gede Davon Ananda P.** - Data Scientist
- **Abu Ammar** - Full Stack Developer
- **Rajib Kurniawan** - Business Strategist

## 📄 License

Internal use only - Amartha X GDG Jakarta Hackathon Project

---

**Built with ❤️ for financial inclusion in rural Indonesia**
