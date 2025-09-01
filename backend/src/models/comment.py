from datetime import datetime
from src.models import db

class Comment(db.Model):
    """Comment model for storing user comments on clauses."""
    
    __tablename__ = 'comments'
    
    id = db.Column(db.Integer, primary_key=True)
    clause_id = db.Column(db.Integer, db.ForeignKey('clauses.id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def __init__(self, clause_id, user_id, content):
        self.clause_id = clause_id
        self.user_id = user_id
        self.content = content
    
    def to_dict(self):
        """Convert comment to dictionary."""
        return {
            'id': self.id,
            'clause_id': self.clause_id,
            'user_id': self.user_id,
            'content': self.content,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<Comment {self.id}>'

