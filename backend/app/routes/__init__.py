from .auth import auth_bp
from .admin import admin_bp
from .bd import bd_bp
from .documents import documents_bp

def register_blueprints(app):
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    app.register_blueprint(bd_bp, url_prefix='/api/bd')
    app.register_blueprint(documents_bp, url_prefix='/api/documents')