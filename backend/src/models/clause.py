from datetime import datetime
from src.models import db

class Clause(db.Model):
    """Clause model for storing extracted clauses from documents."""
    
    __tablename__ = 'clauses'
    
    id = db.Column(db.Integer, primary_key=True)
    document_id = db.Column(db.Integer, db.ForeignKey('documents.id', ondelete='CASCADE'), nullable=False)
    clause_type = db.Column(db.String(100), nullable=False)  # 'termination', 'liability', 'confidentiality', etc.
    title = db.Column(db.String(255))
    content = db.Column(db.Text, nullable=False)
    page_number = db.Column(db.Integer)
    start_position = db.Column(db.Integer)  # character position in document
    end_position = db.Column(db.Integer)  # character position in document
    risk_level = db.Column(db.String(20))  # 'low', 'medium', 'high'
    risk_explanation = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    categories = db.relationship('ClauseCategoryMapping', back_populates='clause', lazy=True, cascade='all, delete-orphan')
    comments = db.relationship('Comment', backref='clause', lazy=True, cascade='all, delete-orphan')
    obligations = db.relationship('Obligation', backref='clause', lazy=True)
    
    def __init__(self, document_id, clause_type, content, title=None, page_number=None, 
                 start_position=None, end_position=None, risk_level=None, risk_explanation=None):
        self.document_id = document_id
        self.clause_type = clause_type
        self.title = title
        self.content = content
        self.page_number = page_number
        self.start_position = start_position
        self.end_position = end_position
        self.risk_level = risk_level
        self.risk_explanation = risk_explanation
    
    def to_dict(self):
        """Convert clause to dictionary."""
        return {
            'id': self.id,
            'document_id': self.document_id,
            'clause_type': self.clause_type,
            'title': self.title,
            'content': self.content,
            'page_number': self.page_number,
            'start_position': self.start_position,
            'end_position': self.end_position,
            'risk_level': self.risk_level,
            'risk_explanation': self.risk_explanation,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<Clause {self.id} - {self.clause_type}>'


class ClauseCategory(db.Model):
    """Predefined categories for clause classification."""
    
    __tablename__ = 'clause_categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    clauses = db.relationship('ClauseCategoryMapping', back_populates='category', lazy=True)
    
    def __init__(self, name, description=None):
        self.name = name
        self.description = description
    
    def to_dict(self):
        """Convert clause category to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<ClauseCategory {self.name}>'


class ClauseCategoryMapping(db.Model):
    """Maps clauses to categories (many-to-many)."""
    
    __tablename__ = 'clause_category_mappings'
    
    id = db.Column(db.Integer, primary_key=True)
    clause_id = db.Column(db.Integer, db.ForeignKey('clauses.id', ondelete='CASCADE'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('clause_categories.id', ondelete='CASCADE'), nullable=False)
    confidence_score = db.Column(db.Float)  # AI confidence in this categorization
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    clause = db.relationship('Clause', back_populates='categories')
    category = db.relationship('ClauseCategory', back_populates='clauses')
    
    __table_args__ = (
        db.UniqueConstraint('clause_id', 'category_id', name='uix_clause_category'),
    )
    
    def __init__(self, clause_id, category_id, confidence_score=None):
        self.clause_id = clause_id
        self.category_id = category_id
        self.confidence_score = confidence_score
    
    def to_dict(self):
        """Convert clause category mapping to dictionary."""
        return {
            'id': self.id,
            'clause_id': self.clause_id,
            'category_id': self.category_id,
            'confidence_score': self.confidence_score,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<ClauseCategoryMapping {self.clause_id} - {self.category_id}>'

