from mongoengine import Document, StringField, EmailField, BooleanField, DateTimeField
from werkzeug.security import generate_password_hash, check_password_hash
from enum import Enum
from datetime import datetime

class UserRole(Enum):
    ADMIN = 'admin'
    BUSINESS_DEVELOPER = 'business_developer'

class User(Document):
    username = StringField(required=True, unique=True, max_length=50)
    email = EmailField(required=True, unique=True)
    password_hash = StringField(required=True)
    role = StringField(
        required=True, 
        choices=[role.value for role in UserRole],
        default=UserRole.BUSINESS_DEVELOPER.value
    )
    is_active = BooleanField(default=True)
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)

    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Check if provided password matches hash"""
        return check_password_hash(self.password_hash, password)

    def save(self, *args, **kwargs):
        """Override save to update timestamp"""
        if not self.created_at:
            self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        return super(User, self).save(*args, **kwargs)

    def to_dict(self):
        """Convert user to dictionary representation"""
        return {
            'id': str(self.id),
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    meta = {
        'collection': 'users',
        'indexes': [
            'username',
            'email',
            'role',
            'created_at'
        ]
    }