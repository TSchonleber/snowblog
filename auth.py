from flask import Blueprint, request, jsonify, current_app
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash
from models import User
from extensions import db
import secrets
from flask_mail import Message

bp = Blueprint('auth', __name__)

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

    user = User(username=username, email=email)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    return jsonify({'message': 'User registered successfully'}), 201

@bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data.get('username')).first()
    if user and user.check_password(data.get('password')):
        login_user(user)
        return jsonify({'message': 'Logged in successfully'}), 200
    return jsonify({'error': 'Invalid username or password'}), 401

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return jsonify({'message': 'Logged out successfully'}), 200

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
@login_required
def check_auth():
    return jsonify({'authenticated': True, 'user': current_user.username}), 200