from datetime import datetime
from src.models import db

class Document(db.Model):
    """Document model for storing metadata about uploaded contracts."""
    
    __tablename__ = 'documents'
    
    id = db.Column(db.Integer, primary_key=True)
    organization_id = db.Column(db.Integer, db.ForeignKey('organizations.id', ondelete='CASCADE'), nullable=False)
    uploaded_by_user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    file_path = db.Column(db.String(512), nullable=False)
    file_type = db.Column(db.String(10), nullable=False)  # 'pdf', 'docx', 'txt'
    file_size = db.Column(db.Integer, nullable=False)  # in bytes
    status = db.Column(db.String(20), default='processing', nullable=False)  # 'processing', 'processed', 'error'
    processing_error = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    versions = db.relationship('DocumentVersion', backref='document', lazy=True, cascade='all, delete-orphan')
    clauses = db.relationship('Clause', backref='document', lazy=True, cascade='all, delete-orphan')
    obligations = db.relationship('Obligation', backref='document', lazy=True, cascade='all, delete-orphan')
    shares = db.relationship('DocumentShare', backref='document', lazy=True, cascade='all, delete-orphan')
    summary = db.relationship('DocumentSummary', backref='document', uselist=False, lazy=True, cascade='all, delete-orphan')
    
    def __init__(self, organization_id, uploaded_by_user_id, title, file_path, file_type, file_size, description=None):
        self.organization_id = organization_id
        self.uploaded_by_user_id = uploaded_by_user_id
        self.title = title
        self.description = description
        self.file_path = file_path
        self.file_type = file_type
        self.file_size = file_size
    
    def to_dict(self):
        """Convert document to dictionary."""
        return {
            'id': self.id,
            'organization_id': self.organization_id,
            'uploaded_by_user_id': self.uploaded_by_user_id,
            'title': self.title,
            'description': self.description,
            'file_path': self.file_path,
            'file_type': self.file_type,
            'file_size': self.file_size,
            'status': self.status,
            'processing_error': self.processing_error,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<Document {self.title}>'


class DocumentVersion(db.Model):
    """Document version model for tracking document versions."""
    
    __tablename__ = 'document_versions'
    
    id = db.Column(db.Integer, primary_key=True)
    document_id = db.Column(db.Integer, db.ForeignKey('documents.id', ondelete='CASCADE'), nullable=False)
    version_number = db.Column(db.Integer, nullable=False)
    file_path = db.Column(db.String(512), nullable=False)
    created_by_user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationship
    created_by_user = db.relationship('User', backref='document_versions')
    
    __table_args__ = (
        db.UniqueConstraint('document_id', 'version_number', name='uix_doc_version'),
    )
    
    def __init__(self, document_id, version_number, file_path, created_by_user_id=None):
        self.document_id = document_id
        self.version_number = version_number
        self.file_path = file_path
        self.created_by_user_id = created_by_user_id
    
    def to_dict(self):
        """Convert document version to dictionary."""
        return {
            'id': self.id,
            'document_id': self.document_id,
            'version_number': self.version_number,
            'file_path': self.file_path,
            'created_by_user_id': self.created_by_user_id,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<DocumentVersion {self.document_id} - v{self.version_number}>'

