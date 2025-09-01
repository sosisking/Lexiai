from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from src.models import db

class User(db.Model):
    """User model for authentication and user management."""
    
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    role = db.Column(db.String(20), default='user', nullable=False)  # 'admin' or 'user'
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_login_at = db.Column(db.DateTime, nullable=True)
    anonymized_at = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    subscription = db.relationship('Subscription', backref='user', uselist=False, lazy=True)
    organizations = db.relationship('OrganizationUser', back_populates='user', lazy=True)
    documents = db.relationship('Document', backref='uploaded_by_user', lazy=True, foreign_keys='Document.uploaded_by_user_id')
    comments = db.relationship('Comment', backref='user', lazy=True)
    document_shares = db.relationship(\'DocumentShare\', backref=\'user\', lazy=True)
    search_queries = db.relationship(\'SearchQuery\', backref=\'user\', lazy=True)
    audit_logs = db.relationship(\'AuditLog\', backref=\'user\', lazy=True)
    consents = db.relationship(\'UserConsent\', back_populates=\'user\', lazy=True, cascade=\'all, delete-orphan\')
    def __init__(self, email, password, first_name=None, last_name=None, role='user'):
        self.email = email
        self.set_password(password)
        self.first_name = first_name
        self.last_name = last_name
        self.role = role
    
    def set_password(self, password):
        """Set password hash."""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check password against hash."""
        return check_password_hash(self.password_hash, password)
    
    def is_admin(self):
        """Check if user is an admin."""
        return self.role == 'admin'
    
    def update_last_login(self):
        """Update last login timestamp."""
        self.last_login_at = datetime.utcnow()
        db.session.commit()
    
    def is_anonymized(self):
        """Check if user has been anonymized."""
        return self.anonymized_at is not None
    
    @property
    def full_name(self):
        """Get user's full name."""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        elif self.first_name:
            return self.first_name
        elif self.last_name:
            return self.last_name
        return ""
    
    def to_dict(self):
        """Convert user to dictionary."""
        return {
            'id': self.id,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'full_name': self.full_name,
            'role': self.role,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'last_login_at': self.last_login_at.isoformat() if self.last_login_at else None
        }
    
    def __repr__(self):
        return f'<User {self.email}>'

