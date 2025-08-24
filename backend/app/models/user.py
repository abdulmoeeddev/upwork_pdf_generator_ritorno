from . import db
from werkzeug.security import generate_password_hash, check_password_hash
from enum import Enum

class UserRole(Enum):
    ADMIN = 'admin'
    BUSINESS_DEVELOPER = 'business_developer'

class User(db.Document):
    username = db.StringField(required=True, unique=True)
    email = db.EmailField(required=True, unique=True)
    password_hash = db.StringField(required=True)
    role = db.StringField(required=True, choices=[role.value for role in UserRole])
    is_active = db.BooleanField(default=True)
    created_at = db.DateTimeField(default=db.datetime.utcnow)
    updated_at = db.DateTimeField(default=db.datetime.utcnow)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    meta = {
        'collection': 'users',
        'indexes': [
            'username',
            'email',
            'role'
        ]
    }