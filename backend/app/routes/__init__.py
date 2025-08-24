from .auth import auth_bp
from .admin import admin_bp
from .bd import bd_bp
from .documents import documents_bp

def register_blueprints(app):
    """Register all blueprint routes with the Flask app"""
    
    # Authentication routes
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    
    # Admin routes  
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    
    # Business Developer routes
    app.register_blueprint(bd_bp, url_prefix='/api/bd')
    
    # Document routes
    app.register_blueprint(documents_bp, url_prefix='/api/documents')
    
    print("✅ All blueprints registered successfully")