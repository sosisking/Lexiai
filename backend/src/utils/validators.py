import re
import os
from flask import current_app

def validate_email(email):
    """
    Validate an email address.
    
    Args:
        email (str): The email address to validate
        
    Returns:
        tuple: (bool, str) - (True, None) if valid, (False, error_message) if invalid
    """
    if not email:
        return False, "Email is required"
    
    # Simple regex for email validation
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        return False, "Invalid email format"
    
    return True, None


def validate_file_type(filename, allowed_extensions=None):
    """
    Validate file type based on extension.
    
    Args:
        filename (str): The filename to validate
        allowed_extensions (set, optional): Set of allowed extensions. Defaults to None.
        
    Returns:
        tuple: (bool, str) - (True, None) if valid, (False, error_message) if invalid
    """
    if not filename:
        return False, "Filename is required"
    
    if allowed_extensions is None:
        allowed_extensions = current_app.config.get('ALLOWED_EXTENSIONS', {'pdf', 'docx', 'txt'})
    
    ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
    
    if ext not in allowed_extensions:
        return False, f"File type not allowed. Allowed types: {', '.join(allowed_extensions)}"
    
    return True, None


def validate_file_size(file, max_size=None):
    """
    Validate file size.
    
    Args:
        file: The file object to validate
        max_size (int, optional): Maximum file size in bytes. Defaults to None.
        
    Returns:
        tuple: (bool, str) - (True, None) if valid, (False, error_message) if invalid
    """
    if not file:
        return False, "File is required"
    
    if max_size is None:
        max_size = current_app.config.get('MAX_CONTENT_LENGTH', 16 * 1024 * 1024)  # Default to 16MB
    
    # Get file size
    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(0)  # Reset file pointer
    
    if file_size > max_size:
        return False, f"File too large. Maximum size is {max_size / (1024 * 1024):.1f}MB"
    
    return True, None


def validate_required_fields(data, required_fields):
    """
    Validate that all required fields are present in the data.
    
    Args:
        data (dict): The data to validate
        required_fields (list): List of required field names
        
    Returns:
        tuple: (bool, str) - (True, None) if valid, (False, error_message) if invalid
    """
    if not data:
        return False, "No data provided"
    
    missing_fields = [field for field in required_fields if field not in data or data[field] is None]
    
    if missing_fields:
        return False, f"Missing required fields: {', '.join(missing_fields)}"
    
    return True, None


def validate_string_length(value, field_name, min_length=None, max_length=None):
    """
    Validate string length.
    
    Args:
        value (str): The string to validate
        field_name (str): The name of the field (for error messages)
        min_length (int, optional): Minimum length. Defaults to None.
        max_length (int, optional): Maximum length. Defaults to None.
        
    Returns:
        tuple: (bool, str) - (True, None) if valid, (False, error_message) if invalid
    """
    if value is None:
        return True, None  # Skip validation if value is None (for optional fields)
    
    if not isinstance(value, str):
        return False, f"{field_name} must be a string"
    
    if min_length is not None and len(value) < min_length:
        return False, f"{field_name} must be at least {min_length} characters long"
    
    if max_length is not None and len(value) > max_length:
        return False, f"{field_name} must be at most {max_length} characters long"
    
    return True, None

