import os
from flask import Blueprint, request, jsonify, current_app, session
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import User
from extensions import db
import secrets
from flask_mail import Message
import logging
import traceback
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

bp = Blueprint('auth', __name__)

engine = create_engine(os.getenv('DATABASE_URL'))
Session = sessionmaker(bind=engine)

@bp.route('/register', methods=['POST'])
def register():
    current_app.logger.info('Received registration request')
    try:
        data = request.get_json()
        current_app.logger.info(f'Registration data: {data}')
        
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')

        current_app.logger.info(f'Extracted data - Username: {username}, Email: {email}')

        if not username or not email or not password:
            current_app.logger.warning('Missing required fields')
            return jsonify({'error': 'Missing required fields'}), 400

        existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
        if existing_user:
            if existing_user.username == username:
                current_app.logger.warning(f'Username already exists: {username}')
                return jsonify({'error': 'Username already exists'}), 400
            else:
                current_app.logger.warning(f'Email already exists: {email}')
                return jsonify({'error': 'Email already exists'}), 400

        new_user = User(username=username, email=email)
        new_user.set_password(password)
        current_app.logger.info(f'Created new user object: {new_user}')

        db.session.add(new_user)
        current_app.logger.info('Added new user to session')

        db.session.commit()
        current_app.logger.info(f'User registered successfully: {username}')

        return jsonify({'message': 'User registered successfully'}), 201
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error during registration: {str(e)}")
        current_app.logger.error(f"Traceback: {traceback.format_exc()}")
        return jsonify({'error': 'An error occurred during registration'}), 500

@bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    logging.info(f"Login attempt for username: {username}")

    user = User.query.filter_by(username=username).first()
    if user and check_password_hash(user.password_hash, password):
        login_user(user, remember=True)
        logging.info(f"User {username} logged in successfully")
        return jsonify({"message": "Logged in successfully", "user": {"username": user.username}}), 200
    else:
        logging.warning(f"Failed login attempt for username: {username}")
        return jsonify({"error": "Invalid username or password"}), 401

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return jsonify({"message": "Logged out successfully"}), 200

@bp.route('/user')
@login_required
def get_user():
    return jsonify({
        'id': current_user.id,
        'username': current_user.username,
        'email': current_user.email
    })

@bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    data = request.get_json()
    email = data.get('email')
    user = User.query.filter_by(email=email).first()
    if user:
        token = secrets.token_urlsafe(20)
        user.reset_token = token
        db.session.commit()
        
        # Send reset email
        msg = Message('Password Reset Request',
                      sender='noreply@yourdomain.com',
                      recipients=[user.email])
        msg.body = f'''To reset your password, visit the following link:
{request.host_url}reset-password/{token}

If you did not make this request then simply ignore this email and no changes will be made.
'''
        current_app.extensions['mail'].send(msg)
        
        return jsonify({'message': 'Password reset email sent'}), 200
    return jsonify({'error': 'Email not found'}), 404

@bp.route('/reset-password/<token>', methods=['POST'])
def reset_password(token):
    data = request.get_json()
    new_password = data.get('password')
    user = User.query.filter_by(reset_token=token).first()
    if user:
        user.set_password(new_password)
        user.reset_token = None
        db.session.commit()
        return jsonify({'message': 'Password reset successfully'}), 200
    return jsonify({'error': 'Invalid or expired token'}), 400

@bp.route('/check-auth')
def check_auth():
    if current_user.is_authenticated:
        return jsonify({"authenticated": True, "user": {"username": current_user.username}}), 200
    else:
        return jsonify({"authenticated": False}), 200

@bp.route('/check_user/<username>', methods=['GET'])
def check_user(username):
    current_app.logger.info(f'Checking if user exists: {username}')
    user = User.query.filter_by(username=username).first()
    if user:
        current_app.logger.info(f'User found: {username}')
        return jsonify({'exists': True, 'username': user.username, 'email': user.email}), 200
    else:
        current_app.logger.info(f'User not found: {username}')
        return jsonify({'exists': False}), 404

@bp.route('/change-password', methods=['POST'])
@login_required
def change_password():
    data = request.get_json()
    old_password = data.get('oldPassword')
    new_password = data.get('newPassword')

    if not check_password_hash(current_user.password_hash, old_password):
        return jsonify({"error": "Incorrect old password"}), 400

    current_user.password_hash = generate_password_hash(new_password)
    db.session.commit()

    return jsonify({"message": "Password changed successfully"}), 200