"""
Credit Scoring API Routes
Multimodal credit assessment using ML + Gemini AI
"""
from fastapi import APIRouter, HTTPException
from typing import Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime

from utils.config import get_settings
from supabase import create_client

# Try to import scoring engine, but make it optional
try:
    from services.scoring.adaptive_engine import AdaptiveScoringEngine
    SCORING_AVAILABLE = True
except ImportError as e:
    SCORING_AVAILABLE = False
    print(f"Warning: Scoring engine not available - {e}")

settings = get_settings()
supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)

router = APIRouter(prefix="/credit-scoring", tags=["Credit Scoring"])

# Initialize scoring engine if available
scoring_engine = AdaptiveScoringEngine() if SCORING_AVAILABLE else None


# Pydantic models
class CreditAssessmentRequest(BaseModel):
    borrower_id: str
    include_photos: bool = True
    include_field_notes: bool = True
    save_to_database: bool = True


class CreditAssessmentResponse(BaseModel):
    borrower_id: str
    assessment_date: datetime
    ml_baseline_score: float
    vision_score_adjustment: float
    nlp_score_adjustment: float
    final_credit_score: float
    risk_category: str
    vision_insights: Optional[Dict[str, Any]]
    nlp_insights: Optional[Dict[str, Any]]
    income_validation: Optional[Dict[str, Any]]
    loan_recommendation: Optional[Dict[str, Any]]
    risk_explanation: Optional[str]
    model_version: str


# Routes
@router.post("/assess", response_model=CreditAssessmentResponse)
async def assess_borrower(request: CreditAssessmentRequest):
    """
    Perform comprehensive credit assessment for a borrower

    Uses multimodal AI approach:
    1. ML baseline score (rule-based or trained model)
    2. Gemini Vision analysis of photos
    3. Gemini NLP extraction from field notes
    4. Adaptive fusion of all scores
    5. Income validation
    6. Loan recommendation

    - **borrower_id**: UUID of the borrower
    - **include_photos**: Include photo analysis (default: True)
    - **include_field_notes**: Include field note analysis (default: True)
    - **save_to_database**: Save assessment to credit_assessments table (default: True)
    """
    # Check if scoring engine is available
    if not SCORING_AVAILABLE or scoring_engine is None:
        raise HTTPException(
            status_code=503,
            detail="Credit scoring engine not available. ML dependencies (scikit-learn) not installed."
        )

    try:
        # Get borrower data
        borrower_response = supabase.table('borrowers').select('*').eq('id', request.borrower_id).execute()
        if not borrower_response.data:
            raise HTTPException(status_code=404, detail="Borrower not found")

        borrower_data = borrower_response.data[0]

        # Get loans and repayments
        loans_response = supabase.table('loans').select('*').eq('borrower_id', request.borrower_id).execute()
        borrower_data['loans'] = loans_response.data

        # Get repayments for each loan
        all_repayments = []
        for loan in loans_response.data:
            repayments_response = supabase.table('repayments').select('*').eq('loan_id', loan['id']).execute()
            all_repayments.extend(repayments_response.data)

        borrower_data['repayments'] = all_repayments

        # Calculate loan history statistics
        borrower_data['loan_history'] = {
            'num_loans': len(loans_response.data),
            'avg_loan_amount': sum(loan['loan_amount'] for loan in loans_response.data) / len(loans_response.data) if loans_response.data else 0,
            'total_borrowed': sum(loan['loan_amount'] for loan in loans_response.data)
        }

        # Calculate repayment history statistics
        if all_repayments:
            on_time = sum(1 for r in all_repayments if r['days_overdue'] == 0)
            total_repayments = len(all_repayments)
            avg_overdue = sum(r['days_overdue'] for r in all_repayments) / total_repayments

            borrower_data['repayment_history'] = {
                'num_loans': len(loans_response.data),
                'on_time_rate': on_time / total_repayments,
                'avg_days_overdue': avg_overdue,
                'default_rate': 0.0,  # Can be enhanced with actual default tracking
                'total_repayments': total_repayments
            }
        else:
            borrower_data['repayment_history'] = {
                'num_loans': 0,
                'on_time_rate': 0.5,
                'avg_days_overdue': 0.0,
                'default_rate': 0.0,
                'total_repayments': 0
            }

        # Get photos if requested
        photos = None
        if request.include_photos:
            photos_response = supabase.table('photos').select('*').eq('borrower_id', request.borrower_id).execute()
            photos = photos_response.data

        # Get field notes if requested
        field_notes = None
        if request.include_field_notes:
            notes_response = supabase.table('field_notes').select('*').eq('borrower_id', request.borrower_id).execute()
            field_notes = notes_response.data

        # Perform assessment
        assessment_result = await scoring_engine.assess_borrower(
            borrower_data=borrower_data,
            photos=photos,
            field_notes=field_notes,
            options={'save_to_db': False}  # We'll save manually
        )

        # Save to database if requested
        # Note: Only saving basic fields that exist in the database schema
        if request.save_to_database:
            assessment_data = {
                'borrower_id': request.borrower_id,
                'ml_baseline_score': assessment_result['ml_baseline_score'],
                'vision_score_adjustment': assessment_result.get('vision_score_adjustment', 0.0),
                'nlp_score_adjustment': assessment_result.get('nlp_score_adjustment', 0.0),
                'final_credit_score': assessment_result['final_credit_score'],
                'risk_category': assessment_result['risk_category']
            }

            try:
                supabase.table('credit_assessments').insert(assessment_data).execute()
            except Exception as db_error:
                # Log error but don't fail the assessment
                print(f"Warning: Could not save to database: {db_error}")

        return {
            "borrower_id": request.borrower_id,
            "assessment_date": datetime.now(),
            **assessment_result
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Assessment error: {str(e)}")


@router.get("/{borrower_id}/history")
async def get_assessment_history(borrower_id: str, limit: int = 10):
    """
    Get credit assessment history for a borrower

    - **borrower_id**: UUID of the borrower
    - **limit**: Number of recent assessments to return (default: 10)
    """
    try:
        response = supabase.table('credit_assessments')\
            .select('*')\
            .eq('borrower_id', borrower_id)\
            .order('assessment_date', desc=True)\
            .limit(limit)\
            .execute()

        return {
            "borrower_id": borrower_id,
            "total_assessments": len(response.data),
            "assessments": response.data
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.get("/{borrower_id}/latest")
async def get_latest_assessment(borrower_id: str):
    """
    Get the most recent credit assessment for a borrower

    - **borrower_id**: UUID of the borrower
    """
    try:
        response = supabase.table('credit_assessments')\
            .select('*')\
            .eq('borrower_id', borrower_id)\
            .order('assessment_date', desc=True)\
            .limit(1)\
            .execute()

        if not response.data:
            raise HTTPException(status_code=404, detail="No assessments found for this borrower")

        return response.data[0]

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.get("/statistics/risk-distribution")
async def get_risk_distribution():
    """
    Get distribution of borrowers by risk category
    """
    try:
        # Get latest assessment for each borrower
        response = supabase.table('credit_assessments')\
            .select('borrower_id, risk_category, final_credit_score')\
            .execute()

        assessments = response.data

        # Group by risk category
        risk_counts = {}
        for assessment in assessments:
            category = assessment['risk_category']
            risk_counts[category] = risk_counts.get(category, 0) + 1

        total = len(assessments)

        return {
            "total_assessments": total,
            "risk_distribution": {
                category: {
                    "count": count,
                    "percentage": round((count / total * 100) if total > 0 else 0, 2)
                }
                for category, count in risk_counts.items()
            },
            "average_score": round(sum(a['final_credit_score'] for a in assessments) / total if total > 0 else 0, 2)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.post("/batch-assess")
async def batch_assess_borrowers(borrower_ids: list[str], save_to_database: bool = True):
    """
    Perform credit assessment for multiple borrowers

    - **borrower_ids**: List of borrower UUIDs
    - **save_to_database**: Save assessments to database (default: True)
    """
    try:
        results = []
        errors = []

        for borrower_id in borrower_ids:
            try:
                request = CreditAssessmentRequest(
                    borrower_id=borrower_id,
                    include_photos=True,
                    include_field_notes=True,
                    save_to_database=save_to_database
                )

                assessment = await assess_borrower(request)
                results.append(assessment)

            except Exception as e:
                errors.append({
                    "borrower_id": borrower_id,
                    "error": str(e)
                })

        return {
            "total_requested": len(borrower_ids),
            "successful": len(results),
            "failed": len(errors),
            "results": results,
            "errors": errors
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch assessment error: {str(e)}")
