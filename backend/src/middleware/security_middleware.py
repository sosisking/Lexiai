"""
Security middleware for the LexiAI application.
Implements various security headers and protections.
"""

from flask import request, g, current_app
import time
import re
from functools import wraps
import uuid

def setup_security_middleware(app):
    """
    Configure security middleware for the Flask application.
    
    Args:
        app: Flask application instance
    """
    @app.after_request
    def add_security_headers(response):
        """
        Add security headers to all responses.
        
        Args:
            response: Flask response object
        
        Returns:
            Modified response with security headers
        """
        # Security Headers
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        
        # Content Security Policy
        csp = (
            "default-src 'self'; "
            "script-src 'self' https://js.stripe.com; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self'; "
            "connect-src 'self' https://api.openai.com https://api.stripe.com; "
            "frame-src https://js.stripe.com; "
            "object-src 'none'; "
            "base-uri 'self'; "
            "form-action 'self'; "
            "frame-ancestors 'self';"
        )
        response.headers['Content-Security-Policy'] = csp
        
        # HSTS (only in production)
        if not current_app.debug:
            response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        
        # Cache Control for API endpoints
        if request.path.startswith('/api/'):
            response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
            response.headers['Pragma'] = 'no-cache'
            response.headers['Expires'] = '0'
        
        return response
    
    @app.before_request
    def log_request_info():
        """
        Log request information and set request ID.
        """
        # Generate a unique request ID
        request_id = str(uuid.uuid4())
        g.request_id = request_id
        g.request_start_time = time.time()
        
        # Log basic request info
        current_app.logger.info(
            f"Request {request_id}: {request.method} {request.path} "
            f"from {request.remote_addr}"
        )
        
        # Check for suspicious patterns
        check_suspicious_patterns(request)
    
    @app.after_request
    def log_response_info(response):
        """
        Log response information including timing.
        
        Args:
            response: Flask response object
        
        Returns:
            Unmodified response
        """
        if hasattr(g, 'request_start_time'):
            duration = time.time() - g.request_start_time
            current_app.logger.info(
                f"Request {g.request_id} completed in {duration:.2f}s "
                f"with status {response.status_code}"
            )
        return response


def check_suspicious_patterns(request):
    """
    Check for suspicious patterns in the request.
    
    Args:
        request: Flask request object
    """
    # SQL Injection patterns
    sql_patterns = [
        r"(\%27)|(\')|(\-\-)|(\%23)|(#)",
        r"((\%3D)|(=))[^\n]*((\%27)|(\')|(\-\-)|(\%3B)|(;))",
        r"((\%27)|(\'))(\s*)((\%6F)|o|(\%4F))((\%72)|r|(\%52))",
        r"((\%27)|(\'))(\s*)((\%61)|a|(\%41))((\%6E)|n|(\%4E))((\%64)|d|(\%44))",
        r"((\%27)|(\'))(\s*)((\%6F)|o|(\%4F))((\%72)|r|(\%52))",
        r"((\%27)|(\'))(\s*)((\%73)|s|(\%53))((\%65)|e|(\%45))((\%6C)|l|(\%4C))((\%65)|e|(\%45))((\%63)|c|(\%43))((\%74)|t|(\%54))"
    ]
    
    # XSS patterns
    xss_patterns = [
        r"<script[^>]*>.*?</script>",
        r"javascript:",
        r"onerror=",
        r"onload=",
        r"eval\(",
        r"document\.cookie",
        r"<img[^>]+src[^>]*>",
        r"<iframe[^>]*>.*?</iframe>"
    ]
    
    # Path traversal patterns
    path_patterns = [
        r"\.\.\/",
        r"\.\.\\",
        r"%2e%2e%2f",
        r"%252e%252e%252f",
        r"\.\.%2f",
        r"%2e%2e/"
    ]
    
    # Check URL, query parameters, and form data
    check_url = request.path
    check_query = str(request.args)
    check_form = str(request.form) if request.form else ""
    check_json = str(request.get_json(silent=True)) if request.is_json else ""
    
    check_data = check_url + check_query + check_form + check_json
    
    # Check all patterns
    for pattern_list in [sql_patterns, xss_patterns, path_patterns]:
        for pattern in pattern_list:
            if re.search(pattern, check_data, re.IGNORECASE):
                current_app.logger.warning(
                    f"Suspicious pattern detected in request {g.request_id}: {pattern}"
                )
                # We log but don't block - in production you might want to block these requests
                break


def rate_limit(limit=100, per=60, scope_func=lambda: request.remote_addr):
    """
    Rate limiting decorator for API endpoints.
    
    Args:
        limit: Maximum number of requests allowed
        per: Time period in seconds
        scope_func: Function to determine the scope (e.g., IP address)
    
    Returns:
        Decorated function
    """
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            # In a real implementation, we would use Redis or a similar store
            # For the MVP, we'll just use a simple in-memory store with cleanup
            if not hasattr(current_app, 'rate_limit_store'):
                current_app.rate_limit_store = {}
            
            # Clean up old entries
            now = time.time()
            for key in list(current_app.rate_limit_store.keys()):
                if current_app.rate_limit_store[key]['reset'] < now:
                    del current_app.rate_limit_store[key]
            
            # Get the scope
            scope = scope_func()
            key = f"{f.__name__}:{scope}"
            
            # Check if the key exists
            if key not in current_app.rate_limit_store:
                current_app.rate_limit_store[key] = {
                    'count': 1,
                    'reset': now + per
                }
            else:
                # Check if we've exceeded the limit
                if current_app.rate_limit_store[key]['count'] >= limit:
                    from flask import jsonify
                    response = jsonify({
                        'error': 'Too many requests',
                        'retry_after': int(current_app.rate_limit_store[key]['reset'] - now)
                    })
                    response.status_code = 429
                    response.headers['Retry-After'] = int(current_app.rate_limit_store[key]['reset'] - now)
                    return response
                
                # Increment the counter
                current_app.rate_limit_store[key]['count'] += 1
            
            # Add rate limit headers
            response = f(*args, **kwargs)
            response.headers['X-RateLimit-Limit'] = str(limit)
            response.headers['X-RateLimit-Remaining'] = str(limit - current_app.rate_limit_store[key]['count'])
            response.headers['X-RateLimit-Reset'] = str(int(current_app.rate_limit_store[key]['reset']))
            
            return response
        return wrapped
    return decorator

