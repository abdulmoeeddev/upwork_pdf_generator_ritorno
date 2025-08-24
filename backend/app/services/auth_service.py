from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt_identity
from ..models.user import User

def require_roles(roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                user_id = get_jwt_identity()
                user = User.objects(id=user_id).first()
                
                if not user or user.role not in [role.value for role in roles]:
                    return jsonify({'error': 'Insufficient permissions'}), 403
                
                return f(*args, **kwargs)
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        return decorated_function
    return decorator