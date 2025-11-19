from sqlalchemy import Column, String, Integer, Boolean, Text, CheckConstraint
from sqlalchemy.types import Numeric
from sqlalchemy.dialects.postgresql import UUID, TIMESTAMP
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid


from models.base import Base


class Borrower(Base):
    __tablename__ = "borrowers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    full_name = Column(String(255), nullable=False)
    age = Column(Integer, CheckConstraint('age >= 18 AND age <= 80'))
    gender = Column(String(20), default='Female')

    # Location
    village = Column(String(255))
    district = Column(String(255))
    province = Column(String(255))

    # Business Info
    business_type = Column(String(100), nullable=False)
    business_description = Column(Text)
    claimed_monthly_income = Column(Numeric(12, 2), nullable=False)
    years_in_business = Column(Numeric(4, 1))

    # Demographics
    marital_status = Column(String(50))
    num_dependents = Column(Integer, default=0)
    education_level = Column(String(100))
    phone_number = Column(String(20))

    # Financial Literacy
    has_bank_account = Column(Boolean, default=False)
    keeps_financial_records = Column(Boolean, default=False)
    financial_literacy_score = Column(Integer, CheckConstraint('financial_literacy_score BETWEEN 0 AND 100'))

    # Metadata
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    loans = relationship("Loan", back_populates="borrower", cascade="all, delete-orphan")
    photos = relationship("Photo", back_populates="borrower", cascade="all, delete-orphan")
    field_notes = relationship("FieldNote", back_populates="borrower", cascade="all, delete-orphan")
    credit_assessments = relationship("CreditAssessment", back_populates="borrower", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Borrower(id={self.id}, name='{self.full_name}', business='{self.business_type}')>"
