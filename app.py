import os
from flask import Flask, session, request, jsonify, render_template, redirect, url_for, flash
from flask_cors import CORS
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from models import User
from dotenv import load_dotenv
from extensions import db
from datetime import timedelta
from sqlalchemy.orm import Session
from openai import OpenAI
from flask_migrate import Migrate
import logging
from sqlalchemy import create_engine, text
from werkzeug.security import generate_password_hash, check_password_hash

load_dotenv()

def create_app():
    load_dotenv()
    
    app = Flask(__name__)
    CORS(app, supports_credentials=True)
    
    # Print the database URL for debugging
    db_user = os.getenv('DB_USER')
    db_pass = os.getenv('DB_PASS')
    db_name = os.getenv('DB_NAME')
    db_host = os.getenv('DB_HOST')
    db_port = os.getenv('DB_PORT')

    # Construct DATABASE_URL from individual components
    DATABASE_URL = f"postgresql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"
    print("Constructed DATABASE_URL:", DATABASE_URL)

    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY') or 'a-very-secret-key'
    app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SESSION_COOKIE_SECURE'] = True
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'None'
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)

    # Set the UPLOAD_FOLDER configuration
    app.config['UPLOAD_FOLDER'] = 'path/to/your/upload/folder'

    # Ensure the upload folder exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    from extensions import db
    db.init_app(app)
    migrate = Migrate(app, db)

    login_manager = LoginManager(app)
    login_manager.login_view = None  # Disable default redirect

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    # Admin panel routes
    @app.route('/admin')
    @login_required
    def admin_panel():
        if not current_user.is_admin:
            flash('You do not have permission to access the admin panel.', 'error')
            return redirect(url_for('home'))
        
        # Fetch users for the user management section
        with engine.connect() as conn:
            result = conn.execute(text("SELECT * FROM users"))
            users = result.fetchall()
        
        return render_template('admin/index.html', users=users)

    @app.route('/admin/user/<int:user_id>', methods=['GET', 'POST'])
    @login_required
    def edit_user(user_id):
        if not current_user.is_admin:
            flash('You do not have permission to edit users.', 'error')
            return redirect(url_for('home'))
        
        with engine.connect() as conn:
            if request.method == 'POST':
                username = request.form['username']
                email = request.form['email']
                is_admin = 'is_admin' in request.form
                conn.execute(text("UPDATE users SET username = :username, email = :email, is_admin = :is_admin WHERE id = :id"),
                             {"username": username, "email": email, "is_admin": is_admin, "id": user_id})
                flash('User updated successfully.', 'success')
                return redirect(url_for('admin_panel'))
            else:
                result = conn.execute(text("SELECT * FROM users WHERE id = :id"), {"id": user_id})
                user = result.fetchone()
                if user:
                    return render_template('admin/edit_user.html', user=user)
                else:
                    flash('User not found.', 'error')
                    return redirect(url_for('admin_panel'))

    @app.route('/admin/user/<int:user_id>/delete', methods=['POST'])
    @login_required
    def delete_user(user_id):
        if not current_user.is_admin:
            flash('You do not have permission to delete users.', 'error')
            return redirect(url_for('home'))
        
        with engine.connect() as conn:
            conn.execute(text("DELETE FROM users WHERE id = :id"), {"id": user_id})
            flash('User deleted successfully.', 'success')
        return redirect(url_for('admin_panel'))

    @app.route('/admin/users')
    @login_required
    def admin_users():
        if not current_user.is_admin:
            flash('You do not have permission to access this page.', 'error')
            return redirect(url_for('home'))
        
        with engine.connect() as conn:
            result = conn.execute(text("SELECT * FROM users"))
            users = result.fetchall()
            print(f"Found {len(users)} users")  # Debug print
            for user in users:
                print(f"User: {user.username}, Email: {user.email}, Admin: {user.is_admin}")  # Debug print
        return render_template('admin_users.html', users=users)

    @app.before_request
    def make_session_permanent():
        session.permanent = True

    from routes import bp as main_bp
    app.register_blueprint(main_bp)

    from auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    logging.basicConfig(level=logging.INFO)
    
    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    
    # API endpoints for user management
    @app.route('/api/admin/users', methods=['GET'])
    @login_required
    def get_users():
        if not current_user.is_admin:
            return jsonify({"error": "Unauthorized"}), 403
        
        users = User.query.all()
        return jsonify([
            {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'is_admin': user.is_admin
            } for user in users
        ])

    @app.route('/api/admin/users/<int:user_id>', methods=['GET', 'PUT', 'DELETE'])
    @login_required
    def manage_user(user_id):
        if not current_user.is_admin:
            return jsonify({"error": "Unauthorized"}), 403

        user = User.query.get(user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404

        if request.method == 'GET':
            return jsonify({
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'is_admin': user.is_admin
            })

        elif request.method == 'PUT':
            data = request.json
            user.username = data.get('username', user.username)
            user.email = data.get('email', user.email)
            user.is_admin = data.get('is_admin', user.is_admin)
            db.session.commit()
            return jsonify({"message": "User updated successfully"})

        elif request.method == 'DELETE':
            db.session.delete(user)
            db.session.commit()
            return jsonify({"message": "User deleted successfully"})

    @app.route('/api/admin/users/<int:user_id>/change-password', methods=['PUT'])
    @login_required
    def change_user_password(user_id):
        if not current_user.is_admin:
            return jsonify({"error": "Unauthorized"}), 403

        user = User.query.get(user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404

        data = request.json
        new_password = data.get('new_password')
        if not new_password:
            return jsonify({"error": "New password is required"}), 400

        user.set_password(new_password)
        db.session.commit()
        return jsonify({"message": "Password updated successfully"})

    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)