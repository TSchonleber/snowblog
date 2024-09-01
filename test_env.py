import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# Load environment variables from .env file
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if not os.path.exists(dotenv_path):
    print(f"Error: .env file not found at {dotenv_path}")
else:
    load_dotenv(dotenv_path)
    print(f".env file loaded from {dotenv_path}")

# Print environment variables to verify
db_user = os.getenv('DB_USER')
db_pass = os.getenv('DB_PASS')
db_name = os.getenv('DB_NAME')
db_host = os.getenv('DB_HOST')
db_port = os.getenv('DB_PORT')

# Construct DATABASE_URL from individual components
database_url = f"postgresql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"

print("DB_USER:", db_user)
print("DB_PASS:", db_pass)
print("DB_NAME:", db_name)
print("DB_HOST:", db_host)
print("DB_PORT:", db_port)
print("Constructed DATABASE_URL:", database_url)

# Check if DATABASE_URL is set correctly
if not database_url:
    print("Error: DATABASE_URL is not set")
else:
    print("Connecting to:", database_url)
    engine = create_engine(database_url)

    # Test the connection
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            print("Connection successful:", result.fetchone())
    except Exception as e:
        print("Connection failed:", e)