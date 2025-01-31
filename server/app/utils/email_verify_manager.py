import os
import hmac
import hashlib
import base64
import time
from urllib.parse import urlencode
from typing import Optional
from pathlib import Path
import uuid

from config.security import EMAIL_VERIFY_EXPIRE_MINUTES, EMAIL_VERIFY_KEY_PATH

class EmailVerifyManager:
    def __init__(self, key_file_path: Path = EMAIL_VERIFY_KEY_PATH):
        """
        Initializes the EmailVerifier with a secret key from a file.
        
        :param key_file_path: Path to the file containing the secret key
        """
        self.key_file_path = key_file_path
        self.secret_key = self._load_key()

    def _load_key(self) -> bytes:
        """Loads the secret key from the file."""
        if not os.path.exists(self.key_file_path):
            key = os.urandom(32)
            with open(self.key_file_path, "wb") as key_file:
                key_file.write(key)
                
        with open(self.key_file_path, "rb") as key_file:
            return key_file.read()

    def generate_verification_params(self, user_id: uuid.UUID, expires_seconds: int = 60 * EMAIL_VERIFY_EXPIRE_MINUTES) -> str:
        """
        Generates a verified link with HMAC signature.
        
        :param user_id: User ID to verify
        :param expires_seconds: Validity period in seconds
        :return: Verification link
        """
        user_id_str = str(user_id)
        timestamp = int(time.time()) + expires_seconds
        data = f"{user_id_str}:{timestamp}".encode("utf-8")
        
        # Create HMAC signature
        signature = hmac.new(self.secret_key, data, hashlib.sha256).digest()
        encoded_sig = base64.urlsafe_b64encode(signature).decode().rstrip("=")
        
        # Create query parameters
        params = {
            "user_id": user_id_str,
            "expires": timestamp,
            "signature": encoded_sig
        }
        
        return urlencode(params)

    def verify(self, user_id: str, expires: str, signature: str) -> bool:
        """
        Verifies the HMAC signature and link validity.
        
        :param user_id: User ID from the link
        :param expires: Timestamp from the link
        :param signature: Signature from the link
        :return: True if valid, False if invalid
        """
        try:
            # Convert expires to integer and check expiration
            expires_int = int(expires)
            if expires_int < time.time():
                return False

            # Reconstruct original data
            data = f"{user_id}:{expires_int}".encode("utf-8")
            
            # Calculate expected signature
            expected_sig = hmac.new(self.secret_key, data, hashlib.sha256).digest()
            encoded_expected_sig = base64.urlsafe_b64encode(expected_sig).decode().rstrip("=")
            
            # Compare signatures (constant-time comparison)
            return hmac.compare_digest(encoded_expected_sig, signature)
            
        except (ValueError, TypeError):
            return False