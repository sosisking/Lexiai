from datetime import datetime
from src.models import db

class SearchQuery(db.Model):
    """Search query model for logging user search queries."""
    
    __tablename__ = 'search_queries'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    query_text = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    def __init__(self, user_id, query_text):
        self.user_id = user_id
        self.query_text = query_text
    
    def to_dict(self):
        """Convert search query to dictionary."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'query_text': self.query_text,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<SearchQuery {self.query_text}>'

