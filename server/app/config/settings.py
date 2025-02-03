import pytz
import os
import uuid
from pathlib import Path

DEFAULT_TIMEZONE = pytz.timezone("UTC")
ENVIRONMENT = os.environ.get("ENVIRONMENT", "dev")
DEBUG = True if ENVIRONMENT == "dev" else False #* Set to True for debugging

SYSTEM_USER_ID = uuid.UUID("00000000-0000-0000-0000-000000000001")

# Verification
VERIFICATION_PATH = Path(__file__).parent.absolute() / "verifications"
VERIFICATION_ID_PATH =  VERIFICATION_PATH / "id"
VERIFICATION_CLUB_PATH = VERIFICATION_PATH / "club"
