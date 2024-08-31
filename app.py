import os
from flask import Flask, send_from_directory
from flask_migrate import Migrate
from flask_cors import CORS
import logging
from extensions import db
from models import User, Post  # Import User and Post models
from flask_login import LoginManager

logging.basicConfig(level=logging.DEBUG)

# Import the config module
from config import SQLALCHEMY_DATABASE_URI, SECRET_KEY, MAIL_SERVER, MAIL_PORT, MAIL_USE_TLS, MAIL_USERNAME, MAIL_PASSWORD

def create_app():
    app = Flask(__name__, template_folder=os.path.abspath('templates'))
    CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000"}})

    # Apply configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
    app.config['SECRET_KEY'] = SECRET_KEY
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Mail configuration
    app.config['MAIL_SERVER'] = MAIL_SERVER
    app.config['MAIL_PORT'] = MAIL_PORT
    app.config['MAIL_USE_TLS'] = MAIL_USE_TLS
    app.config['MAIL_USERNAME'] = MAIL_USERNAME
    app.config['MAIL_PASSWORD'] = MAIL_PASSWORD

    # Initialize extensions
    db.init_app(app)
    migrate = Migrate(app, db)

    # Initialize Flask-Mail only if it's needed
    if app.config['MAIL_SERVER']:
        from flask_mail import Mail
        mail = Mail(app)

    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max-limit

    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)

    login_manager = LoginManager(app)
    login_manager.login_view = 'auth.login'

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    from routes import bp as main_bp
    app.register_blueprint(main_bp)

    from auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    return app

app = create_app()

# Add this route to serve uploaded files
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True, port=5000)