from app import app, db
from models import User, Post  # Import your models here

with app.app_context():
    db.create_all()
    print("Database tables created.")