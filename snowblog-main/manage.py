from flask_migrate import Migrate
from app import create_app, db
from models import User  # Import your models here

app = create_app()
migrate = Migrate(app, db)

if __name__ == '__main__':
    app.run()