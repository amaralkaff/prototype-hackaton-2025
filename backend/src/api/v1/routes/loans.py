"""
Loans API Routes
Loan management and repayment tracking
"""
from fastapi import APIRouter, HTTPException
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime, date

from utils.config import get_settings
from supabase import create_client

settings = get_settings()
supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)

router = APIRouter(prefix="/loans", tags=["Loans"])


# Pydantic models
class LoanResponse(BaseModel):
    id: str
    borrower_id: str
    loan_amount: float
    interest_rate: float
    loan_term_weeks: int
    disbursement_date: date
    expected_repayment_date: date = Field(alias="maturity_date")
    actual_completion_date: Optional[date] = None
    loan_status: str
    purpose: Optional[str] = Field(default=None, alias="loan_purpose")
    initial_credit_score: Optional[float] = None
    created_at: datetime
    updated_at: datetime

    model_config = {
        "populate_by_name": True,
        "from_attributes": True
    }


class LoanCreate(BaseModel):
    borrower_id: str
    loan_amount: float
    interest_rate: float
    loan_term_weeks: int
    disbursement_date: date
    loan_status: str = "active"
    purpose: Optional[str] = None
    initial_credit_score: Optional[float] = None


class RepaymentResponse(BaseModel):
    id: str
    loan_id: str
    payment_date: date
    expected_amount: float
    paid_amount: float
    payment_method: Optional[str]
    days_overdue: int
    created_at: datetime


# Routes
@router.get("/", response_model=List[LoanResponse], response_model_by_alias=False)
async def list_loans(
    limit: int = 20,
    offset: int = 0,
    status: Optional[str] = None,
    borrower_id: Optional[str] = None
):
    """
    List all loans with optional filtering

    - **limit**: Number of results (default 20)
    - **offset**: Pagination offset (default 0)
    - **status**: Filter by loan status (active, completed, defaulted)
    - **borrower_id**: Filter by borrower UUID
    """
    try:
        query = supabase.table('loans').select('*')

        if status:
            query = query.eq('loan_status', status)

        if borrower_id:
            query = query.eq('borrower_id', borrower_id)

        response = query.range(offset, offset + limit - 1).execute()

        return response.data

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.get("/statistics")
async def get_loans_statistics():
    """
    Get overall loan portfolio statistics
    """
    try:
        # Get all loans
        loans_response = supabase.table('loans').select('*').execute()
        loans = loans_response.data

        # Get all repayments
        repayments_response = supabase.table('repayments').select('*').execute()
        repayments = repayments_response.data

        # Calculate statistics
        total_loans = len(loans)
        active_loans = sum(1 for l in loans if l['loan_status'] == 'active')
        completed_loans = sum(1 for l in loans if l['loan_status'] == 'completed')
        defaulted_loans = sum(1 for l in loans if l['loan_status'] == 'defaulted')

        total_disbursed = sum(l['loan_amount'] for l in loans)
        avg_loan_amount = total_disbursed / total_loans if total_loans > 0 else 0

        total_expected = sum(r['expected_amount'] for r in repayments)
        total_collected = sum(r['paid_amount'] for r in repayments)

        return {
            "total_loans": total_loans,
            "active_loans": active_loans,
            "completed_loans": completed_loans,
            "defaulted_loans": defaulted_loans,
            "total_amount_disbursed": total_disbursed,
            "total_amount_repaid": total_collected,
            "avg_loan_amount": avg_loan_amount
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.get("/{loan_id}", response_model=LoanResponse)
async def get_loan(loan_id: str):
    """
    Get a specific loan by ID

    - **loan_id**: UUID of the loan
    """
    try:
        response = supabase.table('loans').select('*').eq('id', loan_id).execute()

        if not response.data:
            raise HTTPException(status_code=404, detail="Loan not found")

        return response.data[0]

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.post("/", response_model=LoanResponse, status_code=201)
async def create_loan(loan: LoanCreate):
    """
    Create a new loan

    Accepts loan data and returns the created loan with assigned ID
    """
    try:
        # Verify borrower exists
        borrower_response = supabase.table('borrowers').select('id').eq('id', loan.borrower_id).execute()
        if not borrower_response.data:
            raise HTTPException(status_code=404, detail="Borrower not found")

        # Calculate expected repayment date
        from datetime import timedelta
        expected_date = loan.disbursement_date + timedelta(weeks=loan.loan_term_weeks)

        loan_data = loan.model_dump()
        loan_data['expected_repayment_date'] = expected_date.isoformat()

        response = supabase.table('loans').insert(loan_data).execute()

        return response.data[0]

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.get("/{loan_id}/repayments", response_model=List[RepaymentResponse])
async def get_loan_repayments(loan_id: str):
    """
    Get all repayments for a specific loan

    - **loan_id**: UUID of the loan
    """
    try:
        response = supabase.table('repayments').select('*').eq('loan_id', loan_id).order('payment_date').execute()

        return response.data

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.get("/{loan_id}/summary")
async def get_loan_summary(loan_id: str):
    """
    Get loan summary with repayment statistics

    - **loan_id**: UUID of the loan
    """
    try:
        # Get loan
        loan_response = supabase.table('loans').select('*').eq('id', loan_id).execute()
        if not loan_response.data:
            raise HTTPException(status_code=404, detail="Loan not found")

        loan = loan_response.data[0]

        # Get repayments
        repayments_response = supabase.table('repayments').select('*').eq('loan_id', loan_id).execute()
        repayments = repayments_response.data

        # Calculate statistics
        total_expected = sum(r['expected_amount'] for r in repayments)
        total_paid = sum(r['paid_amount'] for r in repayments)
        on_time_payments = sum(1 for r in repayments if r['days_overdue'] == 0)
        late_payments = sum(1 for r in repayments if r['days_overdue'] > 0)
        avg_days_overdue = sum(r['days_overdue'] for r in repayments) / len(repayments) if repayments else 0

        return {
            "loan": loan,
            "repayment_statistics": {
                "total_payments": len(repayments),
                "total_expected_amount": total_expected,
                "total_paid_amount": total_paid,
                "outstanding_amount": total_expected - total_paid,
                "on_time_payments": on_time_payments,
                "late_payments": late_payments,
                "average_days_overdue": round(avg_days_overdue, 2),
                "repayment_rate": round((total_paid / total_expected * 100) if total_expected > 0 else 0, 2)
            },
            "repayments": repayments
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


