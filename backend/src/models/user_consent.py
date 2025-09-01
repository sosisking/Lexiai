"""
User consent model for GDPR compliance.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from src.models import db


class UserConsent(db.Model):
    """
    Model for storing user consent records for GDPR compliance.
    """
    __tablename__ = 'user_consents'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    consent_type = Column(String(50), nullable=False)
    consented = Column(Boolean, default=False, nullable=False)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship('User', back_populates='consents')
    
    def __repr__(self):
        return f'<UserConsent {self.id}: {self.user_id} - {self.consent_type}>'
    
    def to_dict(self):
        """
        Convert the model instance to a dictionary.
        
        Returns:
            dict: Dictionary representation of the model
        """
        return {
            'id': self.id,
            'user_id': self.user_id,
            'consent_type': self.consent_type,
            'consented': self.consented,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

