import os
import sys
import logging
from urllib.parse import quote_plus

print(f"Current working directory: {os.getcwd()}")

try:
    with open('config_debug.log', 'w') as f:
        f.write('Test log file creation\n')
    print("Successfully created config_debug.log")
except Exception as e:
    print(f"Error creating config_debug.log: {e}")

# Set up logging to both file and console
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('config_debug.log', mode='w'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Disable buffering for FileHandler
for handler in logger.handlers:
    if isinstance(handler, logging.FileHandler):
        handler.flush()

logger.debug("Starting config.py execution")

# Print all environment variables
logger.debug("Raw environment variables:")
for key, value in os.environ.items():
    if 'PASS' not in key.upper():
        logger.debug(f"{key}: {value}")
    else:
        logger.debug(f"{key}: ********")

def load_env_file(file_path):
    env_vars = {}
    logger.debug(f"Attempting to load .env file from: {file_path}")
    try:
        with open(file_path, 'r') as file:
            for line in file:
                if line.strip() and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    env_vars[key] = value.strip("'").strip('"')
                    if key != 'DB_PASS':
                        logger.debug(f"Loaded from .env: {key}={value}")
                    else:
                        logger.debug(f"Loaded from .env: {key}=********")
    except Exception as e:
        logger.debug(f"Error loading .env file: {e}")
    return env_vars

# Load environment variables from .env file
current_dir = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(current_dir, '.env')
logger.debug(f"Current directory: {current_dir}")
logger.debug(f".env file path: {env_path}")
logger.debug(f".env file exists: {os.path.exists(env_path)}")

env_vars = load_env_file(env_path)

logger.debug("\nDatabase connection details:")
DB_USER = env_vars.get('DB_USER') or os.getenv('DB_USER')
DB_PASS = env_vars.get('DB_PASS') or os.getenv('DB_PASS')
DB_NAME = env_vars.get('DB_NAME') or os.getenv('DB_NAME')
DB_HOST = env_vars.get('DB_HOST') or os.getenv('DB_HOST')
DB_PORT = env_vars.get('DB_PORT') or os.getenv('DB_PORT')
CLOUD_SQL_CONNECTION_NAME = env_vars.get('CLOUD_SQL_CONNECTION_NAME') or os.getenv('CLOUD_SQL_CONNECTION_NAME')

# Properly encode the password
encoded_pass = quote_plus(DB_PASS) if DB_PASS else ''

# Determine if we're running locally or on Google Cloud
IS_LOCAL = True  # Force local development mode

# Add debug logging for IS_LOCAL
logger.debug(f"IS_LOCAL: {IS_LOCAL}")

# Construct the Database URI
if IS_LOCAL:
    # Local development - use standard PostgreSQL connection
    SQLALCHEMY_DATABASE_URI = f"postgresql://{DB_USER}:{encoded_pass}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
else:
    # Google Cloud - use Unix domain socket
    SQLALCHEMY_DATABASE_URI = f"postgresql://{DB_USER}:{encoded_pass}@/{DB_NAME}?host=/cloudsql/{CLOUD_SQL_CONNECTION_NAME}"

logger.debug(f"\nConstructed Database URI: {SQLALCHEMY_DATABASE_URI.replace(encoded_pass, '********')}")

# Add other configuration variables
SECRET_KEY = env_vars.get('SECRET_KEY') or os.getenv('SECRET_KEY')
MAIL_SERVER = env_vars.get('MAIL_SERVER') or os.getenv('MAIL_SERVER')
MAIL_PORT = int(env_vars.get('MAIL_PORT') or os.getenv('MAIL_PORT', 587))
MAIL_USE_TLS = (env_vars.get('MAIL_USE_TLS') or os.getenv('MAIL_USE_TLS', 'True')).lower() == 'true'
MAIL_USERNAME = env_vars.get('MAIL_USERNAME') or os.getenv('MAIL_USERNAME')
MAIL_PASSWORD = env_vars.get('MAIL_PASSWORD') or os.getenv('MAIL_PASSWORD')

logger.debug("Finished config.py execution")
logger.debug("If you see this message, logging is working correctly.")

# Force flush all handlers
for handler in logger.handlers:
    handler.flush()

logger.debug(f"DB_HOST from env: {DB_HOST}")
logger.debug(f"DB_PORT from env: {DB_PORT}")

# Additional debug logging as per instructions
logger.debug(f"Raw DB_HOST from env_vars: {env_vars.get('DB_HOST')}")
logger.debug(f"Raw DB_HOST from os.getenv: {os.getenv('DB_HOST')}")
logger.debug(f"Final DB_HOST: {DB_HOST}")
logger.debug(f"Raw DB_PORT from env_vars: {env_vars.get('DB_PORT')}")
logger.debug(f"Raw DB_PORT from os.getenv: {os.getenv('DB_PORT')}")
logger.debug(f"Final DB_PORT: {DB_PORT}")