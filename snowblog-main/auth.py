import os
from flask import Blueprint, request, jsonify, current_app, session
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import User
from extensions import db
from dotenv import load_dotenv
import secrets
from flask_mail import Message
import logging
import traceback
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

load_dotenv()

bp = Blueprint('auth', __name__)

ADMIN_USERNAME = os.getenv('ADMIN_USERNAME')

engine = create_engine(os.getenv('DATABASE_URL'))
Session = sessionmaker(bind=engine)

@bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if User.query.filter_by(username=username).first():
        return jsonify({'error': 'Username already exists'}), 400
    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Email already exists'}), 400

    is_admin = username.lower() == ADMIN_USERNAME.lower()
    is_approved = is_admin  # Auto-approve admin user

    new_user = User(username=username, email=email, is_approved=is_approved, is_admin=is_admin)
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()

    if is_admin:
        return jsonify({'message': 'Admin user registered and approved.'}), 201
    else:
        return jsonify({'message': 'Registration request submitted. Waiting for admin approval.'}), 201

@bp.route('/approve-user/<int:user_id>', methods=['POST'])
@login_required
def approve_user(user_id):
    if not current_user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403

    user = User.query.get_or_404(user_id)
    user.is_approved = True
    db.session.commit()

    return jsonify({'message': 'User approved successfully'}), 200

@bp.route('/pending-users', methods=['GET'])
@login_required
def get_pending_users():
    if not current_user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403

    pending_users = User.query.filter_by(is_approved=False).all()
    return jsonify([user.to_dict() for user in pending_users]), 200

@bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    logging.info(f"Login attempt for username: {username}")

    user = User.query.filter_by(username=username).first()
    if user and check_password_hash(user.password_hash, password):
        login_user(user, remember=True)
        logging.info(f"User {username} logged in successfully. Is admin: {user.is_admin}")
        return jsonify({
            "message": "Logged in successfully", 
            "user": {
                "username": user.username, 
                "is_admin": user.is_admin
            }
        }), 200
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
        logging.info(f"User {current_user.username} is authenticated. Is admin: {current_user.is_admin}")
        return jsonify({
            "authenticated": True, 
            "user": {
                "username": current_user.username, 
                "is_admin": current_user.is_admin
            }
        }), 200
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

@bp.route('/update-profile', methods=['PUT'])
@login_required
def update_profile():
    data = request.get_json()
    current_user.username = data.get('username', current_user.username)
    current_user.email = data.get('email', current_user.email)
    db.session.commit()
    return jsonify({'message': 'Profile updated successfully', 'user': current_user.to_dict()}), 200

@bp.route('/api/users', methods=['GET'])
@login_required
def get_users():
    if not current_user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403
    users = User.query.filter_by(is_approved=True).all()
    return jsonify([user.to_dict() for user in users]), 200

@bp.route('/api/users/<int:user_id>', methods=['PUT'])
@login_required
def update_user(user_id):
    if not current_user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403
    user = User.query.get_or_404(user_id)
    data = request.get_json()
    user.is_admin = data.get('is_admin', user.is_admin)
    db.session.commit()
    return jsonify(user.to_dict()), 200

@bp.route('/api/users/<int:user_id>', methods=['DELETE'])
@login_required
def delete_user(user_id):
    if not current_user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return '', 204