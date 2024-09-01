import os
from flask import Flask, session, request, jsonify
from flask_cors import CORS
from flask_login import LoginManager
from models import User
from dotenv import load_dotenv
from extensions import db
from datetime import timedelta
from sqlalchemy.orm import Session
from openai import OpenAI
from flask_migrate import Migrate
import logging

load_dotenv()

def create_app():
    load_dotenv()
    
    app = Flask(__name__)
    CORS(app, supports_credentials=True)
    
    # Print the database URL for debugging
    db_url = os.getenv('DATABASE_URL')
    print(f"Database URL: {db_url}")

    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY') or 'a-very-secret-key'
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SESSION_COOKIE_SECURE'] = True
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'None'
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)

    # Set the UPLOAD_FOLDER configuration
    app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'uploads')

    # Ensure the upload folder exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    from extensions import db
    db.init_app(app)
    migrate = Migrate(app, db)

    login_manager = LoginManager(app)
    login_manager.login_view = None  # Disable default redirect

    @login_manager.user_loader
    def load_user(user_id):
        from models import User  # Import here to avoid circular imports
        return User.query.get(int(user_id))

    @app.before_request
    def make_session_permanent():
        session.permanent = True

    from routes import bp as main_bp
    app.register_blueprint(main_bp)

    from auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    logging.basicConfig(level=logging.INFO)
    
    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    
    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)