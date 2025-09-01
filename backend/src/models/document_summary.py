from datetime import datetime
from src.models import db

class DocumentSummary(db.Model):
    """Document summary model for storing AI-generated summaries of documents."""
    
    __tablename__ = 'document_summaries'
    
    id = db.Column(db.Integer, primary_key=True)
    document_id = db.Column(db.Integer, db.ForeignKey('documents.id', ondelete='CASCADE'), nullable=False)
    summary_text = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def __init__(self, document_id, summary_text):
        self.document_id = document_id
        self.summary_text = summary_text
    
    def to_dict(self):
        """Convert document summary to dictionary."""
        return {
            'id': self.id,
            'document_id': self.document_id,
            'summary_text': self.summary_text,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<DocumentSummary {self.document_id}>'

