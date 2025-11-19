from sqlalchemy import Column, String, Integer, Text, ForeignKey, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID, TIMESTAMP, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid

from models.base import Base


class Photo(Base):
    __tablename__ = "photos"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    borrower_id = Column(UUID(as_uuid=True), ForeignKey('borrowers.id', ondelete='CASCADE'), nullable=False)

    # Photo Details
    photo_type = Column(String(50), CheckConstraint("photo_type IN ('business_exterior', 'business_interior', 'inventory', 'house_exterior', 'house_interior', 'assets')"), nullable=False)
    photo_url = Column(Text, nullable=False)
    storage_path = Column(Text)
    file_size_kb = Column(Integer)

    # Gemini Vision Analysis
    vision_analysis_status = Column(String(50), CheckConstraint("vision_analysis_status IN ('pending', 'processing', 'completed', 'failed')"), default='pending')
    vision_analysis_result = Column(JSONB)

    # Extracted Features
    business_scale = Column(String(50))
    inventory_density = Column(String(50))
    asset_quality = Column(String(50))
    socioeconomic_indicators = Column(JSONB)

    # Metadata
    uploaded_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    analyzed_at = Column(TIMESTAMP(timezone=True))

    # Relationships
    borrower = relationship("Borrower", back_populates="photos")

    def __repr__(self):
        return f"<Photo(id={self.id}, type='{self.photo_type}', status='{self.vision_analysis_status}')>"
