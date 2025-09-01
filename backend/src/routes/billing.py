from flask import Blueprint, jsonify, request, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.models import db
from src.models.user import User
from src.models.subscription import Subscription
from src.services.billing_service import BillingService
from src.middleware.auth_middleware import admin_required

billing_bp = Blueprint('billing', __name__)

@billing_bp.route('/plans', methods=['GET'])
def get_plans():
    """Get available subscription plans."""
    plans = BillingService.get_subscription_plans()
    return jsonify({
        'plans': plans
    }), 200


@billing_bp.route('/create-subscription', methods=['POST'])
@jwt_required()
def create_subscription():
    """Create a subscription for the current user."""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    data = request.json
    
    # Validate required fields
    if not data or not data.get('plan_id'):
        return jsonify({'error': 'Plan ID is required'}), 400
    
    # Create subscription
    try:
        subscription_details = BillingService.create_subscription(
            user,
            data['plan_id'],
            data.get('payment_method_id')
        )
        
        return jsonify({
            'message': 'Subscription created successfully',
            'subscription': subscription_details
        }), 201
    except Exception as e:
        current_app.logger.error(f"Error creating subscription: {str(e)}")
        return jsonify({'error': str(e)}), 400


@billing_bp.route('/cancel-subscription', methods=['POST'])
@jwt_required()
def cancel_subscription():
    """Cancel the current user's subscription."""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Get user's subscription
    subscription = Subscription.query.filter_by(user_id=current_user_id).first()
    
    if not subscription or not subscription.stripe_subscription_id:
        return jsonify({'error': 'No active subscription found'}), 404
    
    # Cancel subscription
    try:
        cancellation_details = BillingService.cancel_subscription(
            subscription.stripe_subscription_id
        )
        
        return jsonify({
            'message': 'Subscription canceled successfully',
            'subscription': cancellation_details
        }), 200
    except Exception as e:
        current_app.logger.error(f"Error canceling subscription: {str(e)}")
        return jsonify({'error': str(e)}), 400


@billing_bp.route('/update-subscription', methods=['POST'])
@jwt_required()
def update_subscription():
    """Update the current user's subscription."""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    data = request.json
    
    # Validate required fields
    if not data or not data.get('plan_id'):
        return jsonify({'error': 'Plan ID is required'}), 400
    
    # Get user's subscription
    subscription = Subscription.query.filter_by(user_id=current_user_id).first()
    
    if not subscription or not subscription.stripe_subscription_id:
        return jsonify({'error': 'No active subscription found'}), 404
    
    # Update subscription
    try:
        update_details = BillingService.update_subscription(
            subscription.stripe_subscription_id,
            data['plan_id']
        )
        
        return jsonify({
            'message': 'Subscription updated successfully',
            'subscription': update_details
        }), 200
    except Exception as e:
        current_app.logger.error(f"Error updating subscription: {str(e)}")
        return jsonify({'error': str(e)}), 400


@billing_bp.route('/webhook', methods=['POST'])
def webhook():
    """Handle Stripe webhook events."""
    payload = request.data
    signature = request.headers.get('Stripe-Signature')
    
    if not signature:
        return jsonify({'error': 'Stripe signature is missing'}), 400
    
    try:
        result = BillingService.handle_webhook_event(payload, signature)
        return jsonify(result), 200
    except Exception as e:
        current_app.logger.error(f"Error handling webhook: {str(e)}")
        return jsonify({'error': str(e)}), 400


@billing_bp.route('/admin/subscriptions', methods=['GET'])
@jwt_required()
@admin_required()
def admin_get_subscriptions():
    """Get all subscriptions (admin only)."""
    subscriptions = Subscription.query.all()
    
    result = []
    for subscription in subscriptions:
        user = User.query.get(subscription.user_id)
        if user:
            result.append({
                'subscription': subscription.to_dict(),
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'full_name': user.full_name
                }
            })
    
    return jsonify({
        'subscriptions': result
    }), 200


@billing_bp.route('/admin/subscriptions/<int:subscription_id>', methods=['PUT'])
@jwt_required()
@admin_required()
def admin_update_subscription(subscription_id):
    """Update a subscription (admin only)."""
    subscription = Subscription.query.get(subscription_id)
    
    if not subscription:
        return jsonify({'error': 'Subscription not found'}), 404
    
    data = request.json
    
    # Update subscription fields
    if 'plan_type' in data:
        subscription.plan_type = data['plan_type']
    if 'status' in data:
        subscription.status = data['status']
    if 'current_period_end' in data:
        subscription.current_period_end = datetime.fromisoformat(data['current_period_end'])
    
    db.session.commit()
    
    return jsonify({
        'message': 'Subscription updated successfully',
        'subscription': subscription.to_dict()
    }), 200

