import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from src.config import get_config
from src.models import init_app as init_db
from src.routes.user import user_bp
from src.routes.auth import auth_bp
from src.routes.subscription import subscription_bp
from src.routes.organization import organization_bp
from src.routes.billing import billing_bp
from src.routes.document import document_bp
from src.routes.ai import ai_bp
from src.middleware.error_handler import register_error_handlers
from src.middleware.logging_middleware import init_logging

def create_app(config_name='default'):
    """Create and configure the Flask application."""
    app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
    
    # Load configuration
    app.config.from_object(get_config(config_name))
    
    # Initialize extensions
    CORS(app, origins=app.config['CORS_ORIGINS'])
    jwt = JWTManager(app)
    init_db(app)
    
    # Initialize middleware
    register_error_handlers(app)
    init_logging(app)
    
    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(user_bp, url_prefix='/api/users')
    app.register_blueprint(subscription_bp, url_prefix='/api/subscriptions')
    app.register_blueprint(organization_bp, url_prefix='/api/organizations')
    app.register_blueprint(billing_bp, url_prefix='/api/billing')
    app.register_blueprint(document_bp, url_prefix='/api/documents')
    app.register_blueprint(ai_bp, url_prefix='/api/ai')
    
    # Serve static files (frontend)
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def serve(path):
        static_folder_path = app.static_folder
        if static_folder_path is None:
            return "Static folder not configured", 404

        if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
            return send_from_directory(static_folder_path, path)
        else:
            index_path = os.path.join(static_folder_path, 'index.html')
            if os.path.exists(index_path):
                return send_from_directory(static_folder_path, 'index.html')
            else:
                return "index.html not found", 404
    
    return app

app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)


