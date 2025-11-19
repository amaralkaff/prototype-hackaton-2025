"""
Field Notes API Routes
Handles field agent notes and observations
"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from typing import List, Optional
from pydantic import BaseModel, UUID4
from datetime import datetime, date
from supabase import create_client

from utils.config import get_settings
from utils.logger import logger

settings = get_settings()
router = APIRouter(prefix="/field-notes", tags=["field-notes"])
supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)


class FieldNoteCreate(BaseModel):
    borrower_id: UUID4
    loan_id: Optional[UUID4] = None
    note_text: str
    note_type: str
    visit_date: Optional[date] = None
    field_agent_name: Optional[str] = None


class FieldNoteResponse(BaseModel):
    id: UUID4
    borrower_id: UUID4
    loan_id: Optional[UUID4]
    note_text: str
    note_type: str
    visit_date: Optional[date]
    field_agent_name: Optional[str]
    nlp_analysis_status: str
    created_at: datetime


@router.post("/", status_code=201)
async def create_field_note(note: FieldNoteCreate):
    """
    Create a new field note

    Args:
        note: Field note data including borrower_id, note_text, note_type, etc.

    Returns:
        Created field note with assigned ID
    """
    try:
        note_data = {
            "borrower_id": str(note.borrower_id),
            "loan_id": str(note.loan_id) if note.loan_id else None,
            "note_text": note.note_text,
            "note_type": note.note_type,
            "visit_date": note.visit_date.isoformat() if note.visit_date else datetime.now().date().isoformat(),
            "field_agent_name": note.field_agent_name,
            "nlp_analysis_status": "pending"
        }

        response = supabase.table('field_notes').insert(note_data).execute()

        if response.data and len(response.data) > 0:
            logger.info(f"Field note created successfully for borrower {note.borrower_id}")
            return response.data[0]
        else:
            raise HTTPException(status_code=500, detail="Failed to create field note")

    except Exception as e:
        logger.error(f"Error creating field note: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/borrower/{borrower_id}")
async def get_borrower_field_notes(borrower_id: str):
    """
    Get all field notes for a borrower

    Args:
        borrower_id: UUID of the borrower

    Returns:
        List of field notes ordered by creation date (most recent first)
    """
    try:
        response = supabase.table('field_notes').select('*').eq('borrower_id', borrower_id).order('created_at', desc=True).execute()

        if response.data:
            logger.info(f"Retrieved {len(response.data)} field notes for borrower {borrower_id}")
            return response.data
        else:
            return []

    except Exception as e:
        logger.error(f"Error retrieving field notes for borrower {borrower_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{note_id}")
async def delete_field_note(note_id: str):
    """
    Delete a field note

    Args:
        note_id: UUID of the field note to delete

    Returns:
        Success message
    """
    try:
        # Check if note exists
        response = supabase.table('field_notes').select('id').eq('id', note_id).execute()

        if not response.data or len(response.data) == 0:
            raise HTTPException(status_code=404, detail="Field note not found")

        # Delete the note
        delete_response = supabase.table('field_notes').delete().eq('id', note_id).execute()

        logger.info(f"Field note {note_id} deleted successfully")
        return {"message": "Field note deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting field note {note_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
