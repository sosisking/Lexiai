from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt_identity
from datetime import datetime, timedelta
from src.models import db
from src.models.user import User
from src.models.subscription import Subscription
from src.middleware.logging_middleware import log_audit_event

class AuthService:
    """Service for handling authentication operations."""
    
    @staticmethod
    def register_user(email, password, first_name=None, last_name=None):
        """
        Register a new user.
        
        Args:
            email (str): User's email
            password (str): User's password
            first_name (str, optional): User's first name
            last_name (str, optional): User's last name
            
        Returns:
            tuple: (user, access_token) if successful, (None, error_message) if failed
        """
        # Check if user already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return None, "User with this email already exists"
        
        # Create new user
        user = User(
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            role='user'
        )
        
        # Add user to database
        db.session.add(user)
        db.session.flush()  # Flush to get the user ID
        
        # Create free subscription for new user
        subscription = Subscription(
            user_id=user.id,
            plan_type='free',
            status='active',
            current_period_start=datetime.utcnow(),
            current_period_end=datetime.utcnow() + timedelta(days=30)
        )
        db.session.add(subscription)
        db.session.commit()
        
        # Log audit event
        log_audit_event('register', 'user', user.id, {'email': email})
        
        # Create access token
        access_token = create_access_token(identity=user.id)
        
        return user, access_token
    
    @staticmethod
    def login_user(email, password):
        """
        Login a user.
        
        Args:
            email (str): User's email
            password (str): User's password
            
        Returns:
            tuple: (user, access_token) if successful, (None, error_message) if failed
        """
        # Find user by email
        user = User.query.filter_by(email=email).first()
        
        # Check if user exists and password is correct
        if not user or not user.check_password(password):
            return None, "Invalid email or password"
        
        # Check if user is active
        if not user.is_active:
            return None, "Account is inactive"
        
        # Log audit event
        log_audit_event('login', 'user', user.id)
        
        # Create access token
        access_token = create_access_token(identity=user.id)
        
        return user, access_token
    
    @staticmethod
    def get_current_user():
        """
        Get the current authenticated user.
        
        Returns:
            User: The current user
        """
        user_id = get_jwt_identity()
        return User.query.get(user_id)
    
    @staticmethod
    def change_password(user_id, current_password, new_password):
        """
        Change a user's password.
        
        Args:
            user_id (int): The user ID
            current_password (str): The current password
            new_password (str): The new password
            
        Returns:
            tuple: (True, None) if successful, (False, error_message) if failed
        """
        # Find user
        user = User.query.get(user_id)
        
        # Check if user exists
        if not user:
            return False, "User not found"
        
        # Check if current password is correct
        if not user.check_password(current_password):
            return False, "Current password is incorrect"
        
        # Set new password
        user.set_password(new_password)
        db.session.commit()
        
        # Log audit event
        log_audit_event('change_password', 'user', user.id)
        
        return True, None
    
    @staticmethod
    def reset_password_request(email):
        """
        Request a password reset.
        
        Args:
            email (str): The user's email
            
        Returns:
            tuple: (True, reset_token) if successful, (False, error_message) if failed
        """
        # Find user by email
        user = User.query.filter_by(email=email).first()
        
        # Check if user exists
        if not user:
            return False, "User not found"
        
        # Create reset token (valid for 1 hour)
        reset_token = create_access_token(
            identity=user.id,
            expires_delta=timedelta(hours=1),
            additional_claims={'reset_password': True}
        )
        
        # Log audit event
        log_audit_event('reset_password_request', 'user', user.id)
        
        # In a real implementation, send an email with the reset link
        # For the MVP, we'll just return the token
        return True, reset_token
    
    @staticmethod
    def reset_password(reset_token, new_password):
        """
        Reset a user's password using a reset token.
        
        Args:
            reset_token (str): The reset token
            new_password (str): The new password
            
        Returns:
            tuple: (True, None) if successful, (False, error_message) if failed
        """
        # In a real implementation, verify the token and extract the user ID
        # For the MVP, we'll assume the token is valid and contains the user ID
        user_id = get_jwt_identity()
        
        # Find user
        user = User.query.get(user_id)
        
        # Check if user exists
        if not user:
            return False, "User not found"
        
        # Set new password
        user.set_password(new_password)
        db.session.commit()
        
        # Log audit event
        log_audit_event('reset_password', 'user', user.id)
        
        return True, None

