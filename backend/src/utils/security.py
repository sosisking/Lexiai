import re
import secrets
import string
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import decode_token
from jwt.exceptions import PyJWTError

def hash_password(password):
    """
    Hash a password using Werkzeug's generate_password_hash.
    
    Args:
        password (str): The password to hash
        
    Returns:
        str: The hashed password
    """
    return generate_password_hash(password)


def check_password(password_hash, password):
    """
    Check if a password matches a hash using Werkzeug's check_password_hash.
    
    Args:
        password_hash (str): The hashed password
        password (str): The password to check
        
    Returns:
        bool: True if the password matches the hash, False otherwise
    """
    return check_password_hash(password_hash, password)


def validate_password_strength(password):
    """
    Validate password strength.
    
    Args:
        password (str): The password to validate
        
    Returns:
        tuple: (bool, str) - (True, None) if valid, (False, error_message) if invalid
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    
    if not re.search(r'[0-9]', password):
        return False, "Password must contain at least one digit"
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "Password must contain at least one special character"
    
    return True, None


def generate_secure_token(length=32):
    """
    Generate a secure random token.
    
    Args:
        length (int, optional): The length of the token. Defaults to 32.
        
    Returns:
        str: The generated token
    """
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))


def validate_token(token):
    """
    Validate a JWT token.
    
    Args:
        token (str): The token to validate
        
    Returns:
        tuple: (bool, dict|str) - (True, payload) if valid, (False, error_message) if invalid
    """
    try:
        payload = decode_token(token)
        return True, payload
    except PyJWTError as e:
        return False, str(e)


def sanitize_input(input_str):
    """
    Sanitize user input to prevent XSS attacks.
    
    Args:
        input_str (str): The input string to sanitize
        
    Returns:
        str: The sanitized string
    """
    if not input_str:
        return input_str
    
    # Replace potentially dangerous characters
    sanitized = input_str.replace('<', '&lt;').replace('>', '&gt;')
    sanitized = sanitized.replace('"', '&quot;').replace("'", '&#x27;')
    
    return sanitized

