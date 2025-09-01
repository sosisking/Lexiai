import time
import logging
from flask import request, g
from src.models.audit_log import AuditLog
from src.models import db
from flask_jwt_extended import get_jwt_identity

# Configure logger
logger = logging.getLogger('api')

def init_logging(app):
    """Initialize request logging middleware."""
    
    @app.before_request
    def before_request():
        """Log request details and start timer."""
        g.start_time = time.time()
        
        # Log request details
        logger.info(f"Request: {request.method} {request.path}")
        
        # Log request headers (excluding sensitive information)
        headers = {k: v for k, v in request.headers.items() if k.lower() not in ['authorization', 'cookie']}
        logger.debug(f"Headers: {headers}")
        
        # Log request body for non-GET requests (excluding sensitive information)
        if request.method != 'GET' and request.is_json:
            body = request.get_json(silent=True)
            if body:
                # Mask sensitive fields
                if isinstance(body, dict):
                    masked_body = body.copy()
                    for key in ['password', 'token', 'secret', 'key']:
                        if key in masked_body:
                            masked_body[key] = '******'
                    logger.debug(f"Body: {masked_body}")
    
    @app.after_request
    def after_request(response):
        """Log response details and calculate request duration."""
        # Calculate request duration
        duration = time.time() - g.start_time
        
        # Log response details
        logger.info(f"Response: {response.status_code} (took {duration:.2f}s)")
        
        return response


def log_audit_event(action, entity_type, entity_id=None, details=None):
    """
    Log an audit event to the database.
    
    Args:
        action (str): The action performed (e.g., 'create', 'update', 'delete')
        entity_type (str): The type of entity (e.g., 'user', 'document', 'clause')
        entity_id (int, optional): The ID of the entity
        details (dict, optional): Additional details about the action
    """
    try:
        # Get user ID from JWT token if available
        user_id = get_jwt_identity()
    except:
        user_id = None
    
    # Get IP address from request
    ip_address = request.remote_addr
    
    # Create audit log entry
    audit_log = AuditLog(
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        user_id=user_id,
        details=details,
        ip_address=ip_address
    )
    
    # Add to database
    db.session.add(audit_log)
    db.session.commit()
    
    return audit_log

