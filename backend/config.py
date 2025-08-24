import os
from datetime import timedelta
from dotenv import load_dotenv

class Config:
    # Flask
    load_dotenv()
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'Shusnain@123'
    
    # MongoDB
    MONGODB_URI = os.environ.get('MONGODB_URI') or 'mongodb://localhost:27017/upwork_proposal_generator'
    
    # JWT
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-key-change-in-production'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
    JWT_ALGORITHM = 'HS256'
    
    # GROQ API
    GROQ_API_KEY = os.environ.get('GROQ_API_KEY') or 'your-groq-api-key'
    
    # File upload
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER') or '/tmp/uploads'