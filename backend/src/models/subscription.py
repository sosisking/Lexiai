from datetime import datetime
from src.models import db

class Subscription(db.Model):
    """Subscription model for managing user subscriptions."""
    
    __tablename__ = 'subscriptions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    stripe_customer_id = db.Column(db.String(255), unique=True)
    stripe_subscription_id = db.Column(db.String(255), unique=True)
    plan_type = db.Column(db.String(50), nullable=False)  # 'free', 'basic', 'premium'
    status = db.Column(db.String(50), nullable=False)  # 'active', 'canceled', 'past_due', 'trialing'
    current_period_start = db.Column(db.DateTime)
    current_period_end = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def __init__(self, user_id, plan_type='free', status='active', stripe_customer_id=None, stripe_subscription_id=None,
                 current_period_start=None, current_period_end=None):
        self.user_id = user_id
        self.plan_type = plan_type
        self.status = status
        self.stripe_customer_id = stripe_customer_id
        self.stripe_subscription_id = stripe_subscription_id
        self.current_period_start = current_period_start
        self.current_period_end = current_period_end
    
    def is_active(self):
        """Check if subscription is active."""
        return self.status == 'active' or self.status == 'trialing'
    
    def to_dict(self):
        """Convert subscription to dictionary."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'plan_type': self.plan_type,
            'status': self.status,
            'current_period_start': self.current_period_start.isoformat() if self.current_period_start else None,
            'current_period_end': self.current_period_end.isoformat() if self.current_period_end else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<Subscription {self.id} - {self.plan_type}>'

