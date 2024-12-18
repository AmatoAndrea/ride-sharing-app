from flask import Blueprint, request, jsonify, current_app
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from datetime import datetime, timedelta, timezone
from app.models import User
from app import db

user_bp = Blueprint('users', __name__)

@user_bp.route('/users/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')
    role = data.get('role')

    current_app.logger.info(f"Register attempt for username: {username}")

    # Validate input
    if not all([username, password, email, role]):
        current_app.logger.warning("Missing required fields during registration")
        return jsonify({'message': 'Missing required fields'}), 400

    # Check if user exists
    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        current_app.logger.warning(f"User already exists: {username}")
        return jsonify({'message': 'User already exists'}), 409

    # Create new user
    new_user = User(
        username=username,
        password_hash=generate_password_hash(password),
        email=email,
        role=role
    )
    db.session.add(new_user)
    db.session.commit()

    current_app.logger.info(f"User registered successfully: {username}")
    return jsonify({'message': 'User registered successfully'}), 201

@user_bp.route('/users/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    current_app.logger.info(f"Login attempt for username: {username}")

    # Validate input
    if not all([username, password]):
        current_app.logger.warning("Missing username or password during login")
        return jsonify({'message': 'Missing username or password'}), 400

    user = User.query.filter_by(username=username).first()
    if user and check_password_hash(user.password_hash, password):
        # Generate JWT token
        token = jwt.encode({
            'user_id': user.user_id,
            'exp': datetime.now(timezone.utc) + timedelta(hours=1)
        }, current_app.config['SECRET_KEY'], algorithm='HS256')
        current_app.logger.info(f"User logged in successfully: {username}")
        return jsonify({'token': token}), 200
    else:
        current_app.logger.warning(f"Invalid credentials for username: {username}")
        return jsonify({'message': 'Invalid credentials'}), 401

@user_bp.route('/users/id/<user_id>', methods=['GET'])
def get_user(user_id):
    current_app.logger.info(f"Fetching user by ID: {user_id}")
    user = User.query.get(user_id)
    if user:
        user_data = {
            'user_id': user.user_id,
            'username': user.username,
            'email': user.email,
            'role': user.role.value,
            'created_at': user.created_at.isoformat()
        }
        current_app.logger.info(f"User found: {user.username}")
        return jsonify(user_data), 200
    else:
        current_app.logger.warning(f"User not found with ID: {user_id}")
        return jsonify({'message': 'User not found'}), 404

@user_bp.route('/users/username/<username>', methods=['GET'])
def get_user_by_username(username):
    current_app.logger.info(f"Fetching user by username: {username}")
    user = User.query.filter_by(username=username).first()
    if user:
        user_data = {
            'username': user.username,
            'email': user.email,
            'role': user.role.value,
            'created_at': user.created_at.isoformat()
        }
        current_app.logger.info(f"User found: {username}")
        return jsonify(user_data), 200
    else:
        current_app.logger.warning(f"User not found with username: {username}")
        return jsonify({'message': 'User not found'}), 404