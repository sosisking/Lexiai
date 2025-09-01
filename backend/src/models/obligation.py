from datetime import datetime
from src.models import db

class Obligation(db.Model):
    """Obligation model for tracking obligations and deadlines extracted from contracts."""
    
    __tablename__ = 'obligations'
    
    id = db.Column(db.Integer, primary_key=True)
    document_id = db.Column(db.Integer, db.ForeignKey('documents.id', ondelete='CASCADE'), nullable=False)
    clause_id = db.Column(db.Integer, db.ForeignKey('clauses.id', ondelete='SET NULL'), nullable=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    due_date = db.Column(db.Date)
    status = db.Column(db.String(20), default='pending', nullable=False)  # 'pending', 'completed', 'overdue'
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def __init__(self, document_id, title, description, clause_id=None, due_date=None, status='pending'):
        self.document_id = document_id
        self.clause_id = clause_id
        self.title = title
        self.description = description
        self.due_date = due_date
        self.status = status
    
    def to_dict(self):
        """Convert obligation to dictionary."""
        return {
            'id': self.id,
            'document_id': self.document_id,
            'clause_id': self.clause_id,
            'title': self.title,
            'description': self.description,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<Obligation {self.title}>'

