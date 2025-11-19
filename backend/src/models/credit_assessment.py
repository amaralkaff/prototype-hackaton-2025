from sqlalchemy import Column, String, Text, Integer, Decimal, ForeignKey, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID, TIMESTAMP, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid

from models.base import Base


class CreditAssessment(Base):
    __tablename__ = "credit_assessments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    borrower_id = Column(UUID(as_uuid=True), ForeignKey('borrowers.id', ondelete='CASCADE'), nullable=False)
    loan_id = Column(UUID(as_uuid=True), ForeignKey('loans.id'))

    # ML Model Scores
    ml_baseline_score = Column(Decimal(5, 2), nullable=False)
    ml_model_version = Column(String(50))
    ml_features_used = Column(JSONB)

    # Gemini Vision Contribution
    vision_score_adjustment = Column(Decimal(5, 2), default=0)
    vision_confidence = Column(Decimal(3, 2))
    vision_insights = Column(JSONB)

    # Gemini NLP Contribution
    nlp_score_adjustment = Column(Decimal(5, 2), default=0)
    nlp_confidence = Column(Decimal(3, 2))
    nlp_insights = Column(JSONB)

    # Final Adaptive Score
    final_credit_score = Column(Decimal(5, 2), nullable=False,
                               CheckConstraint('final_credit_score BETWEEN 0 AND 100'))
    risk_category = Column(String(50), nullable=False,
                         CheckConstraint("risk_category IN ('low', 'medium', 'high', 'very_high')"))

    # Income Validation
    claimed_income = Column(Decimal(12, 2))
    ai_estimated_income = Column(Decimal(12, 2))
    income_consistency_score = Column(Decimal(5, 2),
                                     CheckConstraint('income_consistency_score BETWEEN 0 AND 100'))
    income_variance_percentage = Column(Decimal(5, 2))

    # Loan Recommendation
    recommended_loan_amount = Column(Decimal(12, 2))
    max_safe_loan_amount = Column(Decimal(12, 2))
    recommended_term_weeks = Column(Integer)
    recommendation_confidence = Column(Decimal(3, 2))

    # Risk Explanation
    risk_explanation = Column(Text)
    risk_factors = Column(JSONB)
    positive_factors = Column(JSONB)

    # Metadata
    assessed_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    assessment_version = Column(String(50))

    # Relationships
    borrower = relationship("Borrower", back_populates="credit_assessments")
    loan = relationship("Loan", back_populates="credit_assessments")

    def __repr__(self):
        return f"<CreditAssessment(id={self.id}, score={self.final_credit_score}, risk='{self.risk_category}')>"
