from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from config import Config
from app.models import initialize_db
from app.routes import register_blueprints

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize extensions
    CORS(app, origins="*", allow_headers=["Content-Type", "Authorization"])
    jwt = JWTManager(app)
    
    # Initialize database
    try:
        initialize_db(app)
    except Exception as e:
        print(f"Database initialization error: {e}")
    
    # Register blueprints
    register_blueprints(app)
    
    # Health check endpoint
    @app.route('/health')
    def health_check():
        return {'status': 'healthy', 'message': 'Upwork Proposal Generator API is running'}
    
    return app