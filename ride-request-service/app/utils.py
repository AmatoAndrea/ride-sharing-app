from flask import request, jsonify, current_app, g
import jwt
from functools import wraps

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        # Get token from the Authorization header
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header[len('Bearer '):]

        if not token:
            current_app.logger.warning("Token is missing")
            return jsonify({'message': 'Token is missing'}), 401
        
        try:
            #Decode token
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
            # Add user_id to kwargs
            g.user_id = data['user_id']
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token is expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Invalid token'}), 401
        
        return f(*args, **kwargs)
    return decorated
