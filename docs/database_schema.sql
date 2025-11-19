-- ============================================
-- AMARA AI - DATABASE SCHEMA
-- PostgreSQL (Supabase)
-- ============================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================
-- BORROWERS TABLE
-- ============================================
CREATE TABLE borrowers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    full_name VARCHAR(255) NOT NULL,
    age INTEGER CHECK (age >= 18 AND age <= 80),
    gender VARCHAR(20) DEFAULT 'Female',

    -- Location
    village VARCHAR(255),
    district VARCHAR(255),
    province VARCHAR(255),

    -- Business Info
    business_type VARCHAR(100) NOT NULL,
    business_description TEXT,
    claimed_monthly_income DECIMAL(12, 2) NOT NULL,
    years_in_business DECIMAL(4, 1),

    -- Demographics
    marital_status VARCHAR(50),
    num_dependents INTEGER DEFAULT 0,
    education_level VARCHAR(100),
    phone_number VARCHAR(20),

    -- Financial Literacy
    has_bank_account BOOLEAN DEFAULT FALSE,
    keeps_financial_records BOOLEAN DEFAULT FALSE,
    financial_literacy_score INTEGER CHECK (financial_literacy_score BETWEEN 0 AND 100),

    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    -- Constraints
    CONSTRAINT valid_phone CHECK (phone_number ~ '^[0-9+\-() ]+$')
);

CREATE INDEX idx_borrowers_business_type ON borrowers(business_type);
CREATE INDEX idx_borrowers_village ON borrowers(village);
CREATE INDEX idx_borrowers_created_at ON borrowers(created_at);

-- ============================================
-- LOANS TABLE
-- ============================================
CREATE TABLE loans (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    borrower_id UUID NOT NULL REFERENCES borrowers(id) ON DELETE CASCADE,

    -- Loan Details
    loan_amount DECIMAL(12, 2) NOT NULL,
    loan_purpose VARCHAR(255),
    interest_rate DECIMAL(5, 2) NOT NULL,
    loan_term_weeks INTEGER NOT NULL,
    disbursement_date DATE,
    maturity_date DATE,

    -- Status
    loan_status VARCHAR(50) NOT NULL DEFAULT 'pending',
    approval_status VARCHAR(50) DEFAULT 'pending_review',
    approved_at TIMESTAMPTZ,

    -- Risk Assessment
    initial_credit_score DECIMAL(5, 2),
    risk_category VARCHAR(50),

    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    CONSTRAINT valid_loan_status CHECK (
        loan_status IN ('pending', 'active', 'completed', 'defaulted', 'written_off')
    ),
    CONSTRAINT valid_approval_status CHECK (
        approval_status IN ('pending_review', 'approved', 'rejected')
    ),
    CONSTRAINT valid_risk_category CHECK (
        risk_category IN ('low', 'medium', 'high', 'very_high')
    )
);

CREATE INDEX idx_loans_borrower_id ON loans(borrower_id);
CREATE INDEX idx_loans_status ON loans(loan_status);
CREATE INDEX idx_loans_disbursement_date ON loans(disbursement_date);

-- ============================================
-- REPAYMENTS TABLE
-- ============================================
CREATE TABLE repayments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    loan_id UUID NOT NULL REFERENCES loans(id) ON DELETE CASCADE,

    -- Payment Details
    due_date DATE NOT NULL,
    paid_date DATE,
    expected_amount DECIMAL(12, 2) NOT NULL,
    paid_amount DECIMAL(12, 2) DEFAULT 0,

    -- Payment Status
    payment_status VARCHAR(50) NOT NULL DEFAULT 'pending',
    days_overdue INTEGER DEFAULT 0,

    -- Tracking
    payment_method VARCHAR(50),
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),

    CONSTRAINT valid_payment_status CHECK (
        payment_status IN ('pending', 'paid', 'partial', 'late', 'missed')
    )
);

CREATE INDEX idx_repayments_loan_id ON repayments(loan_id);
CREATE INDEX idx_repayments_due_date ON repayments(due_date);
CREATE INDEX idx_repayments_status ON repayments(payment_status);

-- ============================================
-- PHOTOS TABLE
-- ============================================
CREATE TABLE photos (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    borrower_id UUID NOT NULL REFERENCES borrowers(id) ON DELETE CASCADE,

    -- Photo Details
    photo_type VARCHAR(50) NOT NULL,
    photo_url TEXT NOT NULL,
    storage_path TEXT,
    file_size_kb INTEGER,

    -- Gemini Vision Analysis
    vision_analysis_status VARCHAR(50) DEFAULT 'pending',
    vision_analysis_result JSONB,

    -- Extracted Features (from Gemini Vision)
    business_scale VARCHAR(50),
    inventory_density VARCHAR(50),
    asset_quality VARCHAR(50),
    socioeconomic_indicators JSONB,

    -- Metadata
    uploaded_at TIMESTAMPTZ DEFAULT NOW(),
    analyzed_at TIMESTAMPTZ,

    CONSTRAINT valid_photo_type CHECK (
        photo_type IN ('business_exterior', 'business_interior', 'inventory',
                       'house_exterior', 'house_interior', 'assets')
    ),
    CONSTRAINT valid_analysis_status CHECK (
        vision_analysis_status IN ('pending', 'processing', 'completed', 'failed')
    )
);

CREATE INDEX idx_photos_borrower_id ON photos(borrower_id);
CREATE INDEX idx_photos_type ON photos(photo_type);
CREATE INDEX idx_photos_analysis_status ON photos(vision_analysis_status);

-- ============================================
-- FIELD NOTES TABLE
-- ============================================
CREATE TABLE field_notes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    borrower_id UUID NOT NULL REFERENCES borrowers(id) ON DELETE CASCADE,
    loan_id UUID REFERENCES loans(id),

    -- Note Content
    note_text TEXT NOT NULL,
    note_type VARCHAR(50) NOT NULL,
    visit_date DATE,

    -- Gemini NLP Extraction
    nlp_analysis_status VARCHAR(50) DEFAULT 'pending',
    nlp_analysis_result JSONB,

    -- Extracted Insights (from Gemini NLP)
    extracted_income_estimate DECIMAL(12, 2),
    sentiment_score DECIMAL(3, 2),
    risk_flags JSONB,
    behavioral_insights JSONB,

    -- Agent Info
    field_agent_name VARCHAR(255),

    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    analyzed_at TIMESTAMPTZ,

    CONSTRAINT valid_note_type CHECK (
        note_type IN ('initial_visit', 'follow_up', 'repayment_collection',
                      'business_observation', 'risk_assessment', 'general')
    ),
    CONSTRAINT valid_nlp_status CHECK (
        nlp_analysis_status IN ('pending', 'processing', 'completed', 'failed')
    )
);

CREATE INDEX idx_field_notes_borrower_id ON field_notes(borrower_id);
CREATE INDEX idx_field_notes_loan_id ON field_notes(loan_id);
CREATE INDEX idx_field_notes_type ON field_notes(note_type);
CREATE INDEX idx_field_notes_visit_date ON field_notes(visit_date);

-- ============================================
-- CREDIT ASSESSMENTS TABLE
-- ============================================
CREATE TABLE credit_assessments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    borrower_id UUID NOT NULL REFERENCES borrowers(id) ON DELETE CASCADE,
    loan_id UUID REFERENCES loans(id),

    -- ML Model Scores
    ml_baseline_score DECIMAL(5, 2) NOT NULL,
    ml_model_version VARCHAR(50),
    ml_features_used JSONB,

    -- Gemini Vision Contribution
    vision_score_adjustment DECIMAL(5, 2) DEFAULT 0,
    vision_confidence DECIMAL(3, 2),
    vision_insights JSONB,

    -- Gemini NLP Contribution
    nlp_score_adjustment DECIMAL(5, 2) DEFAULT 0,
    nlp_confidence DECIMAL(3, 2),
    nlp_insights JSONB,

    -- Final Adaptive Score
    final_credit_score DECIMAL(5, 2) NOT NULL,
    risk_category VARCHAR(50) NOT NULL,

    -- Income Validation
    claimed_income DECIMAL(12, 2),
    ai_estimated_income DECIMAL(12, 2),
    income_consistency_score DECIMAL(5, 2),
    income_variance_percentage DECIMAL(5, 2),

    -- Loan Recommendation
    recommended_loan_amount DECIMAL(12, 2),
    max_safe_loan_amount DECIMAL(12, 2),
    recommended_term_weeks INTEGER,
    recommendation_confidence DECIMAL(3, 2),

    -- Risk Explanation
    risk_explanation TEXT,
    risk_factors JSONB,
    positive_factors JSONB,

    -- Metadata
    assessed_at TIMESTAMPTZ DEFAULT NOW(),
    assessment_version VARCHAR(50),

    CONSTRAINT valid_risk_category CHECK (
        risk_category IN ('low', 'medium', 'high', 'very_high')
    ),
    CONSTRAINT valid_scores CHECK (
        ml_baseline_score BETWEEN 0 AND 100 AND
        final_credit_score BETWEEN 0 AND 100 AND
        income_consistency_score BETWEEN 0 AND 100
    )
);

CREATE INDEX idx_credit_assessments_borrower_id ON credit_assessments(borrower_id);
CREATE INDEX idx_credit_assessments_loan_id ON credit_assessments(loan_id);
CREATE INDEX idx_credit_assessments_risk_category ON credit_assessments(risk_category);
CREATE INDEX idx_credit_assessments_assessed_at ON credit_assessments(assessed_at);

-- ============================================
-- AUDIT LOG TABLE
-- ============================================
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    table_name VARCHAR(100) NOT NULL,
    record_id UUID NOT NULL,
    action VARCHAR(50) NOT NULL,
    old_values JSONB,
    new_values JSONB,
    timestamp TIMESTAMPTZ DEFAULT NOW(),

    CONSTRAINT valid_action CHECK (
        action IN ('INSERT', 'UPDATE', 'DELETE')
    )
);

CREATE INDEX idx_audit_logs_table_record ON audit_logs(table_name, record_id);
CREATE INDEX idx_audit_logs_timestamp ON audit_logs(timestamp);

-- ============================================
-- UPDATE TRIGGER FOR updated_at
-- ============================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_borrowers_updated_at BEFORE UPDATE ON borrowers
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_loans_updated_at BEFORE UPDATE ON loans
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- VIEWS FOR ANALYTICS
-- ============================================

-- View: Borrower Credit Summary
CREATE VIEW borrower_credit_summary AS
SELECT
    b.id,
    b.full_name,
    b.business_type,
    b.claimed_monthly_income,
    COUNT(DISTINCT l.id) as total_loans,
    AVG(ca.final_credit_score) as avg_credit_score,
    MAX(ca.assessed_at) as last_assessment_date,
    STRING_AGG(DISTINCT ca.risk_category, ', ') as risk_categories
FROM borrowers b
LEFT JOIN loans l ON b.id = l.borrower_id
LEFT JOIN credit_assessments ca ON b.id = ca.borrower_id
GROUP BY b.id, b.full_name, b.business_type, b.claimed_monthly_income;

-- View: Loan Performance
CREATE VIEW loan_performance AS
SELECT
    l.id as loan_id,
    b.full_name as borrower_name,
    l.loan_amount,
    l.loan_status,
    l.risk_category,
    COUNT(r.id) as total_repayments,
    SUM(CASE WHEN r.payment_status = 'paid' THEN 1 ELSE 0 END) as paid_on_time,
    AVG(r.days_overdue) as avg_days_overdue,
    (SUM(r.paid_amount) / NULLIF(SUM(r.expected_amount), 0)) * 100 as repayment_rate
FROM loans l
JOIN borrowers b ON l.borrower_id = b.id
LEFT JOIN repayments r ON l.id = r.loan_id
GROUP BY l.id, b.full_name, l.loan_amount, l.loan_status, l.risk_category;

-- View: Business Type Analysis
CREATE VIEW business_type_analysis AS
SELECT
    business_type,
    COUNT(DISTINCT b.id) as total_borrowers,
    AVG(b.claimed_monthly_income) as avg_income,
    AVG(ca.final_credit_score) as avg_credit_score,
    COUNT(DISTINCT l.id) as total_loans,
    SUM(CASE WHEN l.loan_status = 'completed' THEN 1 ELSE 0 END) as successful_loans,
    SUM(CASE WHEN l.loan_status = 'defaulted' THEN 1 ELSE 0 END) as defaulted_loans
FROM borrowers b
LEFT JOIN loans l ON b.id = l.borrower_id
LEFT JOIN credit_assessments ca ON b.id = ca.borrower_id
GROUP BY business_type;
