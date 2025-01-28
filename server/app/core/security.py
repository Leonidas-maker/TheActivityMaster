from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
import hashlib
import secrets
from typing import Tuple, Optional, List
import hmac
from contextlib import contextmanager
from dataclasses import dataclass
import string
import bcrypt

from utils.totp_manager import TOTPManager
from utils.jwt_keyfile_manager import JWTKeyManager

# Global password hasher
ph = PasswordHasher()

def verify_password(password: str, hash: str) -> bool:
    """Verify a password against a hash

    :param password: The password to verify
    :param hash: The hash to verify against
    :raises ValueError: If there is an error verifying the password
    :return: True if the password matches the hash, False otherwise
    """
    try:
        ph.verify(hash, password)
        return True
    except VerifyMismatchError:
        return False
    except Exception as e:
        raise ValueError("Error verifying password") from e


def hash_password(password: str) -> str:
    """Hash a password using Argon2id

    :param password: The password to hash
    :raises ValueError: If there is an error hashing the password
    :return: The hashed password
    """
    try:
        return ph.hash(password)
    except Exception as e:
        raise ValueError("Error hashing password") from e


def sha256_salt(data: str, salt: Optional[str] = None) -> str:
    """Hash data with salt using SHA256 with a random salt

    :param data: The data to hash
    :raises ValueError: If there is an error hashing the data
    :return: The hashed data with salt
    """
    try:
        if not salt:
            salt_bytes = secrets.token_bytes(32)
            return f"{salt_bytes.hex()}.{hashlib.sha256((data).encode() + salt_bytes).hexdigest()}"
        else:
            return f"{salt}.{hashlib.sha256((data).encode() + bytes.fromhex(salt)).hexdigest()}"

    except Exception as e:
        raise ValueError("Error hashing data with salt") from e


def sha256_salt_verify(data: str, data_hash: str) -> bool:
    """Verify data hashed with salt in a cryptographically secure way.

    :param data: The data to verify
    :param data_hash: The salt and hash stored as "<salt>.<hash>"
    :raises ValueError: If there is an error verifying the data
    :return: True if the data matches the hash, False otherwise
    """
    try:
        # Split the stored data_hash into salt and hash
        salt, stored_hash = data_hash.split(".")
        salt_bytes = bytes.fromhex(salt)

        # Recompute the hash
        computed_hash = hashlib.sha256(data.encode() + salt_bytes).hexdigest()

        # Use hmac.compare_digest for secure comparison
        return hmac.compare_digest(computed_hash, stored_hash)
    except Exception as e:
        raise ValueError("Error verifying data hashed with salt") from e

def generate_backup_codes(n: int = 8, code_length: int = 8) -> List[str]:
    """Generate backup codes

    :param n: The number of backup codes to generate
    :param code_length: The length of each backup code
    :return: A list of backup codes
    """
    alphabet = string.ascii_letters + string.digits
    return [''.join(secrets.choice(alphabet) for _ in range(code_length)) for _ in range(n)]

def bycrypt_hash(data: str) -> str:
    """Hash data using bcrypt

    :param data: The data to hash
    :raises ValueError: If there is an error hashing the data
    :return: The hashed data
    """
    try:
        return bcrypt.hashpw(data.encode(), bcrypt.gensalt()).decode()
    except Exception as e:
        raise ValueError("Error hashing data with bcrypt") from e
    
def bcrypt_verify(data: str, hashed_data: str) -> bool:
    """Verify data against a bcrypt hash

    :param data: The data to verify
    :param hashed_data: The bcrypt hash to verify against
    :raises ValueError: If there is an error verifying the data
    :return: True if the data matches the hash, False otherwise
    """
    try:
        return bcrypt.checkpw(data.encode(), hashed_data.encode())
    except Exception as e:
        raise ValueError("Error verifying data hashed with bcrypt") from e

###########################################################################
############################### Dataclasses ###############################
###########################################################################
@dataclass
class TokenDetails():
    application_id: str
    payload: dict

###########################################################################
############################### Dependencies ##############################
###########################################################################
# ======================================================== #
# ==================== JWT-Key Manager =================== #
# ======================================================== #
class JWTKeyManagerDependency:
    def __init__(self):
        self._km: Optional[JWTKeyManager] = None

    def init(self, km_instance: JWTKeyManager):
        self._km = km_instance

    @contextmanager
    def get(self):
        if not self._km:
            raise RuntimeError("KeyManager not initialized")
        yield self._km


jwt_key_manager_dependency = JWTKeyManagerDependency()


# ======================================================== #
# ===================== TOTP Manager ===================== #
# ======================================================== #
class TOTPManagerDependency:
    def __init__(self):
        self._totp_m: Optional[TOTPManager] = None

    def init(self, totp_m_instance: TOTPManager):
        self._totp_m = totp_m_instance

    @contextmanager
    def get(self):
        if not self._totp_m:
            raise RuntimeError("KeyManager not initialized")
        yield self._totp_m


totp_manager_dependency = TOTPManagerDependency()
