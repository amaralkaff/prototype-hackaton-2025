"""
Borrowers API Routes
CRUD operations for borrower management
"""
from fastapi import APIRouter, HTTPException
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from utils.config import get_settings
from supabase import create_client

settings = get_settings()
supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)

router = APIRouter(prefix="/borrowers", tags=["Borrowers"])


# Pydantic models
class BorrowerResponse(BaseModel):
    id: str
    full_name: str
    age: int
    gender: Optional[str]
    village: Optional[str]
    district: Optional[str]
    province: Optional[str]
    business_type: str
    business_description: Optional[str]
    claimed_monthly_income: float
    years_in_business: Optional[float]
    marital_status: Optional[str]
    num_dependents: Optional[int]
    education_level: Optional[str]
    phone_number: Optional[str]
    has_bank_account: bool
    keeps_financial_records: bool
    financial_literacy_score: Optional[int]
    created_at: datetime
    updated_at: datetime


class BorrowerCreate(BaseModel):
    full_name: str
    age: int
    business_type: str
    claimed_monthly_income: float
    gender: Optional[str] = None
    village: Optional[str] = None
    district: Optional[str] = None
    province: Optional[str] = None
    business_description: Optional[str] = None
    years_in_business: Optional[float] = None
    marital_status: Optional[str] = None
    num_dependents: Optional[int] = 0
    education_level: Optional[str] = None
    phone_number: Optional[str] = None
    has_bank_account: bool = False
    keeps_financial_records: bool = False
    financial_literacy_score: Optional[int] = None


# Routes
@router.get("/", response_model=List[BorrowerResponse])
async def list_borrowers(
    limit: int = 20,
    offset: int = 0,
    business_type: Optional[str] = None,
    province: Optional[str] = None
):
    """
    List all borrowers with optional filtering

    - **limit**: Number of results (default 20)
    - **offset**: Pagination offset (default 0)
    - **business_type**: Filter by business type
    - **province**: Filter by province
    """
    try:
        query = supabase.table('borrowers').select('*')

        if business_type:
            query = query.eq('business_type', business_type)

        if province:
            query = query.eq('province', province)

        response = query.range(offset, offset + limit - 1).execute()

        return response.data

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.get("/{borrower_id}", response_model=BorrowerResponse)
async def get_borrower(borrower_id: str):
    """
    Get a specific borrower by ID

    - **borrower_id**: UUID of the borrower
    """
    try:
        response = supabase.table('borrowers').select('*').eq('id', borrower_id).execute()

        if not response.data:
            raise HTTPException(status_code=404, detail="Borrower not found")

        return response.data[0]

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.post("/", response_model=BorrowerResponse, status_code=201)
async def create_borrower(borrower: BorrowerCreate):
    """
    Create a new borrower

    Accepts borrower data and returns the created borrower with assigned ID
    """
    try:
        borrower_data = borrower.model_dump()

        response = supabase.table('borrowers').insert(borrower_data).execute()

        return response.data[0]

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.get("/{borrower_id}/loans")
async def get_borrower_loans(borrower_id: str):
    """
    Get all loans for a specific borrower

    - **borrower_id**: UUID of the borrower
    """
    try:
        response = supabase.table('loans').select('*').eq('borrower_id', borrower_id).execute()

        return {
            "borrower_id": borrower_id,
            "total_loans": len(response.data),
            "loans": response.data
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.get("/{borrower_id}/photos")
async def get_borrower_photos(borrower_id: str):
    """
    Get all photos for a specific borrower

    - **borrower_id**: UUID of the borrower
    """
    try:
        response = supabase.table('photos').select('*').eq('borrower_id', borrower_id).execute()

        return {
            "borrower_id": borrower_id,
            "total_photos": len(response.data),
            "photos": response.data
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.get("/{borrower_id}/field-notes")
async def get_borrower_field_notes(borrower_id: str):
    """
    Get all field notes for a specific borrower

    - **borrower_id**: UUID of the borrower
    """
    try:
        response = supabase.table('field_notes').select('*').eq('borrower_id', borrower_id).execute()

        return {
            "borrower_id": borrower_id,
            "total_notes": len(response.data),
            "field_notes": response.data
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.get("/{borrower_id}/summary")
async def get_borrower_summary(borrower_id: str):
    """
    Get comprehensive summary of a borrower (profile + loans + photos + notes)

    - **borrower_id**: UUID of the borrower
    """
    try:
        # Get borrower
        borrower_response = supabase.table('borrowers').select('*').eq('id', borrower_id).execute()
        if not borrower_response.data:
            raise HTTPException(status_code=404, detail="Borrower not found")

        # Get loans
        loans_response = supabase.table('loans').select('*').eq('borrower_id', borrower_id).execute()

        # Get photos
        photos_response = supabase.table('photos').select('*').eq('borrower_id', borrower_id).execute()

        # Get field notes
        notes_response = supabase.table('field_notes').select('*').eq('borrower_id', borrower_id).execute()

        # Get credit assessments
        assessments_response = supabase.table('credit_assessments').select('*').eq('borrower_id', borrower_id).execute()

        return {
            "borrower": borrower_response.data[0],
            "loans": {
                "total": len(loans_response.data),
                "items": loans_response.data
            },
            "photos": {
                "total": len(photos_response.data),
                "items": photos_response.data
            },
            "field_notes": {
                "total": len(notes_response.data),
                "items": notes_response.data
            },
            "credit_assessments": {
                "total": len(assessments_response.data),
                "items": assessments_response.data
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
