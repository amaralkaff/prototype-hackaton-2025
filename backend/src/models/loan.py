from sqlalchemy import Column, String, Decimal, Integer, Date, ForeignKey, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID, TIMESTAMP
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid

from models.base import Base


class Loan(Base):
    __tablename__ = "loans"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    borrower_id = Column(UUID(as_uuid=True), ForeignKey('borrowers.id', ondelete='CASCADE'), nullable=False)

    # Loan Details
    loan_amount = Column(Decimal(12, 2), nullable=False)
    loan_purpose = Column(String(255))
    interest_rate = Column(Decimal(5, 2), nullable=False)
    loan_term_weeks = Column(Integer, nullable=False)
    disbursement_date = Column(Date)
    maturity_date = Column(Date)

    # Status
    loan_status = Column(String(50), nullable=False, default='pending',
                        CheckConstraint("loan_status IN ('pending', 'active', 'completed', 'defaulted', 'written_off')"))
    approval_status = Column(String(50), default='pending_review',
                           CheckConstraint("approval_status IN ('pending_review', 'approved', 'rejected')"))
    approved_at = Column(TIMESTAMP(timezone=True))

    # Risk Assessment
    initial_credit_score = Column(Decimal(5, 2))
    risk_category = Column(String(50),
                         CheckConstraint("risk_category IN ('low', 'medium', 'high', 'very_high')"))

    # Metadata
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    borrower = relationship("Borrower", back_populates="loans")
    repayments = relationship("Repayment", back_populates="loan", cascade="all, delete-orphan")
    field_notes = relationship("FieldNote", back_populates="loan")
    credit_assessments = relationship("CreditAssessment", back_populates="loan")

    def __repr__(self):
        return f"<Loan(id={self.id}, amount={self.loan_amount}, status='{self.loan_status}')>"


class Repayment(Base):
    __tablename__ = "repayments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    loan_id = Column(UUID(as_uuid=True), ForeignKey('loans.id', ondelete='CASCADE'), nullable=False)

    # Payment Details
    due_date = Column(Date, nullable=False)
    paid_date = Column(Date)
    expected_amount = Column(Decimal(12, 2), nullable=False)
    paid_amount = Column(Decimal(12, 2), default=0)

    # Payment Status
    payment_status = Column(String(50), nullable=False, default='pending',
                          CheckConstraint("payment_status IN ('pending', 'paid', 'partial', 'late', 'missed')"))
    days_overdue = Column(Integer, default=0)

    # Tracking
    payment_method = Column(String(50))
    notes = Column(String)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    # Relationships
    loan = relationship("Loan", back_populates="repayments")

    def __repr__(self):
        return f"<Repayment(id={self.id}, due_date={self.due_date}, status='{self.payment_status}')>"
