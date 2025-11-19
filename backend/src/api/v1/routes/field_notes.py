"""
Field Notes API Routes
Handles field agent notes and observations
"""
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
from typing import List, Optional
from pydantic import BaseModel, UUID4
from datetime import datetime, date
from models.field_note import FieldNote
from models.base import get_db

from utils.config import get_settings
from utils.logger import logger

settings = get_settings()
router = APIRouter(prefix="/field-notes", tags=["field-notes"])


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


@router.post("/", response_model=FieldNoteResponse, status_code=201)
async def create_field_note(note: FieldNoteCreate, db=Depends(get_db)):
    """
    Create a new field note

    Args:
        note: Field note data including borrower_id, note_text, note_type, etc.

    Returns:
        Created field note with assigned ID
    """
    try:
        field_note = FieldNote(
            borrower_id=note.borrower_id,
            loan_id=note.loan_id,
            note_text=note.note_text,
            note_type=note.note_type,
            visit_date=note.visit_date or datetime.now().date(),
            field_agent_name=note.field_agent_name,
            nlp_analysis_status='pending'
        )

        db.add(field_note)
        db.commit()
        db.refresh(field_note)

        logger.info(f"Field note created: {field_note.id}")

        return FieldNoteResponse(
            id=field_note.id,
            borrower_id=field_note.borrower_id,
            loan_id=field_note.loan_id,
            note_text=field_note.note_text,
            note_type=field_note.note_type,
            visit_date=field_note.visit_date,
            field_agent_name=field_note.field_agent_name,
            nlp_analysis_status=field_note.nlp_analysis_status,
            created_at=field_note.created_at
        )

    except Exception as e:
        logger.error(f"Error creating field note: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/borrower/{borrower_id}", response_model=List[FieldNoteResponse])
async def get_borrower_field_notes(borrower_id: str, db=Depends(get_db)):
    """Get all field notes for a borrower"""
    try:
        notes = db.query(FieldNote).filter(FieldNote.borrower_id == borrower_id).order_by(FieldNote.created_at.desc()).all()

        return [
            FieldNoteResponse(
                id=note.id,
                borrower_id=note.borrower_id,
                loan_id=note.loan_id,
                note_text=note.note_text,
                note_type=note.note_type,
                visit_date=note.visit_date,
                field_agent_name=note.field_agent_name,
                nlp_analysis_status=note.nlp_analysis_status,
                created_at=note.created_at
            )
            for note in notes
        ]

    except Exception as e:
        logger.error(f"Error fetching field notes: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{note_id}")
async def delete_field_note(note_id: str, db=Depends(get_db)):
    """Delete a field note"""
    try:
        note = db.query(FieldNote).filter(FieldNote.id == note_id).first()
        if not note:
            raise HTTPException(status_code=404, detail="Field note not found")

        db.delete(note)
        db.commit()

        return {"message": "Field note deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting field note: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
