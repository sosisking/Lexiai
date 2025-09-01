from datetime import datetime
from src.models import db
from sqlalchemy.dialects.postgresql import JSONB

class AuditLog(db.Model):
    """Audit log model for tracking important system events."""
    
    __tablename__ = 'audit_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    action = db.Column(db.String(100), nullable=False)
    entity_type = db.Column(db.String(50), nullable=False)  # 'user', 'document', 'clause', etc.
    entity_id = db.Column(db.Integer)
    details = db.Column(db.JSON)  # Using JSON type for flexibility
    ip_address = db.Column(db.String(45))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    def __init__(self, action, entity_type, entity_id=None, user_id=None, details=None, ip_address=None):
        self.action = action
        self.entity_type = entity_type
        self.entity_id = entity_id
        self.user_id = user_id
        self.details = details
        self.ip_address = ip_address
    
    def to_dict(self):
        """Convert audit log to dictionary."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'action': self.action,
            'entity_type': self.entity_type,
            'entity_id': self.entity_id,
            'details': self.details,
            'ip_address': self.ip_address,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<AuditLog {self.action} - {self.entity_type}>'

