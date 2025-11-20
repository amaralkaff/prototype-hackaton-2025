// API Response Types

export interface Borrower {
  id: string
  full_name: string
  age: number
  gender?: string
  village?: string
  district?: string
  province?: string
  business_type: string
  business_description?: string
  claimed_monthly_income: number
  years_in_business?: number
  marital_status?: string
  num_dependents?: number
  education_level?: string
  phone_number?: string
  has_bank_account: boolean
  keeps_financial_records: boolean
  financial_literacy_score?: number
  created_at: string
  updated_at: string
}

export interface Loan {
  id: string
  borrower_id: string
  loan_amount: number
  interest_rate: number
  loan_term_weeks: number
  disbursement_date: string
  expected_repayment_date: string
  loan_status: "active" | "completed" | "defaulted"
  purpose?: string
  created_at: string
  updated_at: string
}

export interface CreditAssessment {
  id: string
  borrower_id: string
  assessment_date: string
  ml_baseline_score: number
  vision_score_adjustment: number
  nlp_score_adjustment: number
  final_credit_score: number
  risk_category: string
  vision_insights?: Record<string, any>
  nlp_insights?: Record<string, any>
  income_validation?: Record<string, any>
  loan_recommendation?: Record<string, any>
  risk_explanation?: string
  model_version: string
  created_at: string
}

export interface Photo {
  id: string
  borrower_id: string
  photo_type: string
  file_path: string
  upload_date: string
  caption?: string
  gemini_analysis?: Record<string, any>
  created_at: string
}

export interface FieldNote {
  id: string
  borrower_id: string
  officer_name: string
  visit_date: string
  notes_text: string
  gemini_extraction?: Record<string, any>
  created_at: string
  updated_at: string
}

export interface LoansStatistics {
  total_loans: number
  total_amount_disbursed: number
  total_amount_repaid: number
  avg_loan_amount: number
  active_loans: number
  completed_loans: number
  defaulted_loans: number
}

export interface BorrowerSummary {
  borrower: Borrower
  loans: {
    total: number
    items: Loan[]
  }
  photos: {
    total: number
    items: Photo[]
  }
  field_notes: {
    total: number
    items: FieldNote[]
  }
  credit_assessments: {
    total: number
    items: CreditAssessment[]
  }
}
