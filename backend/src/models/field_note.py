from sqlalchemy import Column, String, Text, Date, ForeignKey, CheckConstraint
from sqlalchemy.types import Numeric
from sqlalchemy.dialects.postgresql import UUID, TIMESTAMP, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid

from models.base import Base


class FieldNote(Base):
    __tablename__ = "field_notes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    borrower_id = Column(UUID(as_uuid=True), ForeignKey('borrowers.id', ondelete='CASCADE'), nullable=False)
    loan_id = Column(UUID(as_uuid=True), ForeignKey('loans.id'))

    # Note Content
    note_text = Column(Text, nullable=False)
    note_type = Column(String(50), CheckConstraint("note_type IN ('initial_visit', 'follow_up', 'repayment_collection', 'business_observation', 'risk_assessment', 'general')"), nullable=False)
    visit_date = Column(Date)

    # Gemini NLP Extraction
    nlp_analysis_status = Column(String(50), CheckConstraint("nlp_analysis_status IN ('pending', 'processing', 'completed', 'failed')"), default='pending')
    nlp_analysis_result = Column(JSONB)

    # Extracted Insights
    extracted_income_estimate = Column(Numeric(12, 2))
    sentiment_score = Column(Numeric(3, 2))
    risk_flags = Column(JSONB)
    behavioral_insights = Column(JSONB)

    # Agent Info
    field_agent_name = Column(String(255))

    # Metadata
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    analyzed_at = Column(TIMESTAMP(timezone=True))

    # Relationships
    borrower = relationship("Borrower", back_populates="field_notes")
    loan = relationship("Loan", back_populates="field_notes")

    def __repr__(self):
        return f"<FieldNote(id={self.id}, type='{self.note_type}', status='{self.nlp_analysis_status}')>"
