from pickle import TRUE
from tkinter import E
import pytz
import os
import uuid

DEFAULT_TIMEZONE = pytz.timezone("UTC")
ENVIRONMENT = os.environ.get("ENVIRONMENT", "dev")
DEBUG = TRUE if ENVIRONMENT == "dev" else False #* Set to True for debugging

SYSTEM_USER_ID = uuid.UUID("00000000-0000-0000-0000-000000000001")
