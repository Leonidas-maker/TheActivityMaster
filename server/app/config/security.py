from pathlib import Path
from config.settings import ENVIRONMENT

# Token settings
ACCESS_TOKEN_EXPIRE_MINUTES = 15

# CSRF settings
SECRET_KEY = "your_secret"

# Token keyfiles path
TOKEN_KEYFILES_PATH = Path(__file__).parent.absolute() / "jwt_keys" if ENVIRONMENT == "dev" else Path("/run/secrets/")
TOKEN_KEYFILES_PREFIX = "" if ENVIRONMENT == "dev" else "tacm_"
TOKEN_ISSUER = "www.theactivitymaster.de"

# TOTP settings
TOTP_ENCRYPTION_KEY_PATH = Path(__file__).parent.absolute() / "totp_encryption_key.bin" if ENVIRONMENT == "dev" else Path("/run/secrets/totp_encryption_key.bin")