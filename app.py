import os
import logging
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

load_dotenv()

def create_app():
    load_dotenv()
    
    app = Flask(__name__)
    CORS(app, supports_credentials=True)
    
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY') or 'a-very-secret-key'
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SESSION_COOKIE_SECURE'] = True
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'None'
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)

    from extensions import db
    db.init_app(app)
    migrate = Migrate(app, db)

    login_manager = LoginManager(app)
    login_manager.login_view = None  # Disable default redirect

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    @app.before_request
    def make_session_permanent():
        session.permanent = True

    from routes import bp as main_bp
    app.register_blueprint(main_bp)

    from auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    logging.basicConfig(level=logging.INFO)
    
    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    
    @app.route('/api/ai/text', methods=['POST'])
    def generate_text():
        prompt = request.json['prompt']
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=150
            )
            return jsonify({'text': response.choices[0].message.content.strip()})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)