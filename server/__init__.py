from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_mail import Mail
import os

db = SQLAlchemy()
login_manager = LoginManager()
mail = Mail()

def create_app():
    app = Flask(__name__)
    basedir = os.path.abspath(os.path.dirname(__file__))
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL') or \
        'postgresql+psycopg2://postgres:{password}@/{database}?host=/cloudsql/{project}:{region}:{instance}'.format(
            password=os.environ.get('DB_PASSWORD'),
            database=os.environ.get('DB_NAME'),
            project=os.environ.get('GOOGLE_CLOUD_PROJECT'),
            region='your-region',  # e.g., 'us-central1'
            instance=os.environ.get('CLOUD_SQL_INSTANCE')
        )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'your-secret-key'  # Change this to a random secret key

    # Mail settings
    app.config['MAIL_SERVER'] = 'smtp.mailtrap.io'
    app.config['MAIL_PORT'] = 2525
    app.config['MAIL_USERNAME'] = 'your_mailtrap_username'
    app.config['MAIL_PASSWORD'] = 'your_mailtrap_password'
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USE_SSL'] = False
    
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