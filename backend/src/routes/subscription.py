from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.models import db
from src.models.user import User
from src.models.subscription import Subscription
from datetime import datetime, timedelta

subscription_bp = Blueprint('subscription', __name__)

@subscription_bp.route('', methods=['GET'])
@jwt_required()
def get_subscriptions():
    """Get all subscriptions (admin only)."""
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    
    # Check if user is admin
    if not current_user or not current_user.is_admin():
        return jsonify({'error': 'Unauthorized access'}), 403
    
    subscriptions = Subscription.query.all()
    return jsonify({
        'subscriptions': [subscription.to_dict() for subscription in subscriptions]
    }), 200


@subscription_bp.route('/<int:subscription_id>', methods=['GET'])
@jwt_required()
def get_subscription(subscription_id):
    """Get a specific subscription."""
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    
    subscription = Subscription.query.get(subscription_id)
    if not subscription:
        return jsonify({'error': 'Subscription not found'}), 404
    
    # Check if user is admin or owns the subscription
    if not current_user or (not current_user.is_admin() and current_user_id != subscription.user_id):
        return jsonify({'error': 'Unauthorized access'}), 403
    
    return jsonify({
        'subscription': subscription.to_dict()
    }), 200


@subscription_bp.route('', methods=['POST'])
@jwt_required()
def create_subscription():
    """Create a new subscription (admin only)."""
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    
    # Check if user is admin
    if not current_user or not current_user.is_admin():
        return jsonify({'error': 'Unauthorized access'}), 403
    
    data = request.json
    
    # Validate required fields
    if not data or not data.get('user_id') or not data.get('plan_type') or not data.get('status'):
        return jsonify({'error': 'User ID, plan type, and status are required'}), 400
    
    # Check if user exists
    user = User.query.get(data['user_id'])
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Check if user already has a subscription
    existing_subscription = Subscription.query.filter_by(user_id=data['user_id']).first()
    if existing_subscription:
        return jsonify({'error': 'User already has a subscription'}), 409
    
    # Create new subscription
    subscription = Subscription(
        user_id=data['user_id'],
        plan_type=data['plan_type'],
        status=data['status'],
        stripe_customer_id=data.get('stripe_customer_id'),
        stripe_subscription_id=data.get('stripe_subscription_id'),
        current_period_start=datetime.utcnow(),
        current_period_end=datetime.utcnow() + timedelta(days=30)
    )
    
    db.session.add(subscription)
    db.session.commit()
    
    return jsonify({
        'message': 'Subscription created successfully',
        'subscription': subscription.to_dict()
    }), 201


@subscription_bp.route('/<int:subscription_id>', methods=['PUT'])
@jwt_required()
def update_subscription(subscription_id):
    """Update a specific subscription (admin only)."""
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    
    # Check if user is admin
    if not current_user or not current_user.is_admin():
        return jsonify({'error': 'Unauthorized access'}), 403
    
    subscription = Subscription.query.get(subscription_id)
    if not subscription:
        return jsonify({'error': 'Subscription not found'}), 404
    
    data = request.json
    
    # Update subscription fields
    if 'plan_type' in data:
        subscription.plan_type = data['plan_type']
    if 'status' in data:
        subscription.status = data['status']
    if 'stripe_customer_id' in data:
        subscription.stripe_customer_id = data['stripe_customer_id']
    if 'stripe_subscription_id' in data:
        subscription.stripe_subscription_id = data['stripe_subscription_id']
    if 'current_period_start' in data:
        subscription.current_period_start = datetime.fromisoformat(data['current_period_start'])
    if 'current_period_end' in data:
        subscription.current_period_end = datetime.fromisoformat(data['current_period_end'])
    
    db.session.commit()
    
    return jsonify({
        'message': 'Subscription updated successfully',
        'subscription': subscription.to_dict()
    }), 200


@subscription_bp.route('/<int:subscription_id>', methods=['DELETE'])
@jwt_required()
def delete_subscription(subscription_id):
    """Delete a specific subscription (admin only)."""
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    
    # Check if user is admin
    if not current_user or not current_user.is_admin():
        return jsonify({'error': 'Unauthorized access'}), 403
    
    subscription = Subscription.query.get(subscription_id)
    if not subscription:
        return jsonify({'error': 'Subscription not found'}), 404
    
    db.session.delete(subscription)
    db.session.commit()
    
    return jsonify({
        'message': 'Subscription deleted successfully'
    }), 200

