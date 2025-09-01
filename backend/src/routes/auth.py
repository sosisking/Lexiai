from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.models import db
from src.models.user import User
from src.services.auth_service import AuthService

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user."""
    data = request.json
    
    # Validate required fields
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Email and password are required'}), 400
    
    # Register user
    user, result = AuthService.register_user(
        email=data['email'],
        password=data['password'],
        first_name=data.get('first_name'),
        last_name=data.get('last_name')
    )
    
    if not user:
        return jsonify({'error': result}), 409
    
    return jsonify({
        'message': 'User registered successfully',
        'user': user.to_dict(),
        'access_token': result
    }), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    """Login a user."""
    data = request.json
    
    # Validate required fields
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Email and password are required'}), 400
    
    # Login user
    user, result = AuthService.login_user(
        email=data['email'],
        password=data['password']
    )
    
    if not user:
        return jsonify({'error': result}), 401
    
    return jsonify({
        'message': 'Login successful',
        'user': user.to_dict(),
        'access_token': result
    }), 200


@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Get current authenticated user."""
    user = AuthService.get_current_user()
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify({
        'user': user.to_dict()
    }), 200


@auth_bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    """Change user's password."""
    current_user_id = get_jwt_identity()
    data = request.json
    
    # Validate required fields
    if not data or not data.get('current_password') or not data.get('new_password'):
        return jsonify({'error': 'Current password and new password are required'}), 400
    
    # Change password
    success, message = AuthService.change_password(
        user_id=current_user_id,
        current_password=data['current_password'],
        new_password=data['new_password']
    )
    
    if not success:
        return jsonify({'error': message}), 400
    
    return jsonify({
        'message': 'Password changed successfully'
    }), 200


@auth_bp.route('/reset-password-request', methods=['POST'])
def reset_password_request():
    """Request a password reset."""
    data = request.json
    
    # Validate required fields
    if not data or not data.get('email'):
        return jsonify({'error': 'Email is required'}), 400
    
    # Request password reset
    success, result = AuthService.reset_password_request(
        email=data['email']
    )
    
    if not success:
        return jsonify({'error': result}), 404
    
    return jsonify({
        'message': 'Password reset link sent',
        'reset_token': result  # In a real implementation, this would be sent via email
    }), 200


@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    """Reset user's password using a reset token."""
    data = request.json
    
    # Validate required fields
    if not data or not data.get('reset_token') or not data.get('new_password'):
        return jsonify({'error': 'Reset token and new password are required'}), 400
    
    # Reset password
    success, message = AuthService.reset_password(
        reset_token=data['reset_token'],
        new_password=data['new_password']
    )
    
    if not success:
        return jsonify({'error': message}), 400
    
    return jsonify({
        'message': 'Password reset successfully'
    }), 200


@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """Logout a user."""
    # JWT tokens are stateless, so we don't need to do anything server-side
    # The client should remove the token from storage
    return jsonify({
        'message': 'Logout successful'
    }), 200

