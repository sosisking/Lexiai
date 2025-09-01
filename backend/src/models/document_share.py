from datetime import datetime
from src.models import db

class DocumentShare(db.Model):
    """Document share model for managing document sharing between users."""
    
    __tablename__ = 'document_shares'
    
    id = db.Column(db.Integer, primary_key=True)
    document_id = db.Column(db.Integer, db.ForeignKey('documents.id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    permission_level = db.Column(db.String(20), default='read', nullable=False)  # 'read', 'comment', 'edit'
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    __table_args__ = (
        db.UniqueConstraint('document_id', 'user_id', name='uix_document_user'),
    )
    
    def __init__(self, document_id, user_id, permission_level='read'):
        self.document_id = document_id
        self.user_id = user_id
        self.permission_level = permission_level
    
    def can_read(self):
        """Check if user can read the document."""
        return True  # All permission levels can read
    
    def can_comment(self):
        """Check if user can comment on the document."""
        return self.permission_level in ['comment', 'edit']
    
    def can_edit(self):
        """Check if user can edit the document."""
        return self.permission_level == 'edit'
    
    def to_dict(self):
        """Convert document share to dictionary."""
        return {
            'id': self.id,
            'document_id': self.document_id,
            'user_id': self.user_id,
            'permission_level': self.permission_level,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<DocumentShare {self.document_id} - {self.user_id} - {self.permission_level}>'

