from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
from app.models.user import User, UserRole

def require_roles(roles):
    """Decorator to require specific roles for access"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                # Verify JWT token exists
                verify_jwt_in_request()
                
                user_id = get_jwt_identity()
                if not user_id:
                    return jsonify({'error': 'Invalid token'}), 401
                
                user = User.objects(id=user_id, is_active=True).first()
                if not user:
                    return jsonify({'error': 'User not found or inactive'}), 401
                
                # Check if user has required role
                if user.role not in [role.value for role in roles]:
                    return jsonify({'error': 'Insufficient permissions'}), 403
                
                return f(*args, **kwargs)
            except Exception as e:
                return jsonify({'error': f'Authentication error: {str(e)}'}), 401
        return decorated_function
    return decorator

def get_current_user():
    """Get current authenticated user"""
    try:
        user_id = get_jwt_identity()
        if not user_id:
            return None
        return User.objects(id=user_id, is_active=True).first()
    except Exception:
        return None

class AuthService:
    @staticmethod
    def authenticate_user(username, password):
        """Authenticate user with username and password"""
        try:
            user = User.objects(username=username, is_active=True).first()
            if user and user.check_password(password):
                return user
            return None
        except Exception:
            return None
    
    @staticmethod
    def create_user(username, email, password, role=UserRole.BUSINESS_DEVELOPER):
        """Create a new user"""
        try:
            # Check if user already exists
            if User.objects(username=username).first():
                raise ValueError("Username already exists")
            if User.objects(email=email).first():
                raise ValueError("Email already exists")
            
            user = User(
                username=username,
                email=email,
                role=role.value
            )
            user.set_password(password)
            user.save()
            return user
        except Exception as e:
            raise e