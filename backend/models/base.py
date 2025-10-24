"""
Base SQLAlchemy model with common fields
"""

from datetime import datetime
from sqlalchemy import Column, DateTime, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import UUID
import uuid

Base = declarative_base()

class BaseModel(Base):
    """Base model with common fields"""
    __abstract__ = True
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    deleted_at = Column(DateTime, nullable=True)  # Soft delete
    is_active = Column(Boolean, default=True, nullable=False)
    
    def soft_delete(self):
        """Soft delete the record"""
        self.deleted_at = datetime.utcnow()
        self.is_active = False
    
    def restore(self):
        """Restore soft deleted record"""
        self.deleted_at = None
        self.is_active = True