from datetime import datetime
from src.models import db

class Organization(db.Model):
    """Organization model for multi-tenant architecture."""
    
    __tablename__ = 'organizations'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    users = db.relationship('OrganizationUser', back_populates='organization', lazy=True)
    documents = db.relationship('Document', backref='organization', lazy=True)
    
    def __init__(self, name):
        self.name = name
    
    def to_dict(self):
        """Convert organization to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<Organization {self.name}>'


class OrganizationUser(db.Model):
    """Junction table for many-to-many relationship between users and organizations."""
    
    __tablename__ = 'organization_users'
    
    id = db.Column(db.Integer, primary_key=True)
    organization_id = db.Column(db.Integer, db.ForeignKey('organizations.id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    role = db.Column(db.String(50), default='member', nullable=False)  # 'owner', 'admin', 'member'
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    organization = db.relationship('Organization', back_populates='users')
    user = db.relationship('User', back_populates='organizations')
    
    __table_args__ = (
        db.UniqueConstraint('organization_id', 'user_id', name='uix_org_user'),
    )
    
    def __init__(self, organization_id, user_id, role='member'):
        self.organization_id = organization_id
        self.user_id = user_id
        self.role = role
    
    def is_owner(self):
        """Check if user is an owner of the organization."""
        return self.role == 'owner'
    
    def is_admin(self):
        """Check if user is an admin of the organization."""
        return self.role == 'owner' or self.role == 'admin'
    
    def to_dict(self):
        """Convert organization user to dictionary."""
        return {
            'id': self.id,
            'organization_id': self.organization_id,
            'user_id': self.user_id,
            'role': self.role,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<OrganizationUser {self.user_id} - {self.organization_id} - {self.role}>'

