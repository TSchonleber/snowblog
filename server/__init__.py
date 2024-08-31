import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_mail import Mail

db = SQLAlchemy()
login_manager = LoginManager()
mail = Mail()

def create_app():
    app = Flask(__name__)
    
    # Print current working directory and .env file path
    print(f"Current working directory: {os.getcwd()}")
    print(f".env file path: {os.path.join(os.getcwd(), '.env')}")
    print(f".env file exists: {os.path.exists(os.path.join(os.getcwd(), '.env'))}")
    
    # Database configuration
    db_user = os.getenv('DB_USER')
    db_pass = os.getenv('DB_PASS')
    db_name = os.getenv('DB_NAME')
    db_host = os.getenv('DB_HOST')
    db_port = os.getenv('DB_PORT', '5432')

    # Print out the environment variables for debugging
    print(f"DB_USER: {db_user}")
    print(f"DB_PASS: {'*' * len(db_pass) if db_pass else 'Not set'}")
    print(f"DB_NAME: {db_name}")
    print(f"DB_HOST: {db_host}")
    print(f"DB_PORT: {db_port}")

    # Check if all necessary variables are set
    if not all([db_user, db_pass, db_name, db_host]):
        raise ValueError("Missing database configuration. Please check your .env file.")

    # Construct the database URI
    db_uri = f"postgresql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"
    print(f"Database URI: {db_uri}")  # For debugging, remove in production

    app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY') or 'you-will-never-guess'

    # Mail settings
    app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER', 'smtp.googlemail.com')
    app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', 587))
    app.config['MAIL_USE_TLS'] = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
    
    db.init_app(app)
    CORS(app)
    login_manager.init_app(app)
    login_manager.login_view = 'login'
    mail.init_app(app)

    with app.app_context():
        from . import routes
        routes.init_routes(app)

    @login_manager.user_loader
    def load_user(user_id):
        from .models import User
        return User.query.get(int(user_id))

    return app