import pytz
import os
import uuid
from pydantic import SecretStr
from pathlib import Path


DEFAULT_TIMEZONE = pytz.timezone("UTC")
ENVIRONMENT = os.environ.get("ENVIRONMENT", "dev")
DEBUG = True if ENVIRONMENT == "dev" else False #* Set to True for debugging
TESTING = os.environ.get("TESTING", "False") == "True" and ENVIRONMENT == "dev"

SYSTEM_USER_ID = uuid.UUID("00000000-0000-0000-0000-000000000001")

# Verification
VERIFICATION_PATH = Path(__file__).parent.absolute() / "verifications"
VERIFICATION_ID_PATH =  VERIFICATION_PATH / "id"
VERIFICATION_CLUB_PATH = VERIFICATION_PATH / "club"


# Redis
REDIS_URL = os.getenv("REDIS_HOST", "127.0.0.1")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", "root")

# Email
EMAIL_HOST = os.getenv("EMAIL_HOST", "localhost")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", "1025"))
EMAIL_USERNAME = os.getenv("EMAIL_USERNAME", "")
EMAIL_PASSWORD = SecretStr(os.getenv("EMAIL_PASSWORD", ""))
SERVER_DOMAIN = os.getenv("SERVER_DOMAIN", "localhost:8000")