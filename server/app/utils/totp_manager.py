import pyotp
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from pathlib import Path
import secrets
import base64
from typing import Optional

from config.security import TOTP_ENCRYPTION_KEY_PATH
from config.settings import ENVIRONMENT

class TOTPManager:
    def __init__(self, key_path: Path = TOTP_ENCRYPTION_KEY_PATH):
        """Initialize the TOTP manager

        :param key_path: The path to the encryption key file, defaults to TOTP_ENCRYPTION_KEY_PATH
        :raises ValueError: If the key length is invalid
        """
        self.key_path = key_path
        self._load_key()
        self.new_key = None

    def _load_key(self):
        """Load and validate encryption key"""
        if not self.key_path.exists():
            if ENVIRONMENT == "dev":
                with self.key_path.open("wb") as key_file:
                    key_file.write(secrets.token_bytes(32))
            else:
                raise FileNotFoundError("TOTP encryption key file not found")

        with self.key_path.open("rb") as key_file:
            self.encryption_key = key_file.read()
        
        if len(self.encryption_key) != 32:
            raise ValueError("Invalid key length (must be 32 bytes)")

    def encrypt(self, plaintext: str, key_override: Optional[bytes] = None) -> bytes:
        """Encrypt a secret using AES-GCM

        :param plaintext: The plaintext secret to encrypt
        :return: The encrypted secret
        """

        iv = secrets.token_bytes(12)  # 96-bit IV for AES-GCM
        if key_override:
            cipher = Cipher(algorithms.AES(key_override), modes.GCM(iv), backend=default_backend())
        else:
            cipher = Cipher(algorithms.AES(self.encryption_key), modes.GCM(iv), backend=default_backend())
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(plaintext.encode()) + encryptor.finalize()
        return iv + ciphertext + encryptor.tag 

    def decrypt(self, encrypted_secret: bytes) -> str:
        """Decrypt an encrypted secret

        :param encrypted_secret: The encrypted secret to decrypt
        :raises ValueError: If the encrypted secret is invalid
        :return: The decrypted secret
        """
        if len(encrypted_secret) < 28:  # 12B IV + 16B tag
                raise ValueError("Invalid encrypted secret")
        iv = encrypted_secret[:12]
        tag = encrypted_secret[-16:]
        ciphertext = encrypted_secret[12:-16]

        cipher = Cipher(algorithms.AES(self.encryption_key), modes.GCM(iv, tag), backend=default_backend())
        decryptor = cipher.decryptor()
        decrypted = decryptor.update(ciphertext) + decryptor.finalize()
        return decrypted.decode()

    def generate_totp_secret(self) -> tuple[str, str]:
        """Generate a TOTP secret and encrypt it

        :return: A tuple containing the secret and the encrypted secret
        """
        secret = pyotp.random_base32()
        encrypted_secret = base64.b64encode(self.encrypt(secret)).decode()
        return secret, encrypted_secret

    def get_totp_uri(self, secret: str, username: str, issuer_name: str) -> str:
        """Get the provisioning URI for a TOTP secret

        :param secret: The TOTP secret
        :param username: The username
        :param issuer_name: The issuer name
        :return: The provisioning URI
        """
        return pyotp.totp.TOTP(secret).provisioning_uri(name=username, issuer_name=issuer_name)

    def verify_totp(self, encrypted_secret: str, code: str) -> bool:
        """Verify a TOTP code

        :param encrypted_secret: The encrypted TOTP secret
        :param code: The TOTP code to verify
        :return: True if the code is valid, False otherwise
        """
        encrypted_secret_bytes = base64.b64decode(encrypted_secret)
        secret = self.decrypt(encrypted_secret_bytes)
        return pyotp.TOTP(secret).verify(code)
    
    # ======================================================== #
    # ===================== Key Rotation ===================== #
    # ======================================================== #
    def generate_new_key(self) -> bytes:
        """Generate a new encryption key"""
        if not self.new_key:
            self.new_key = secrets.token_bytes(32)
            return self.new_key
        else:
            raise ValueError("New key already generated")
    
    
    def save_new_key(self):
        """Save the encryption key to a file

        :param key: The encryption key to save
        """
        if not self.new_key:
            raise ValueError("No new key generated")
        
        with self.key_path.open("wb") as key_file:
            key_file.write(self.new_key)
        self.encryption_key = self.new_key
        self.new_key = None

    def rotate_key(self, new_key: bytes, encrypted_secret: str) -> str:
        """Rotate the encryption key of an encrypted secret

        :param new_key: The new encryption key
        :param encrypted_secret: The encrypted TOTP secret
        :return: The re-encrypted secret
        """
        secret = self.decrypt(base64.b64decode(encrypted_secret))
        reencrypted_secret = self.encrypt(secret, new_key)
        return base64.b64encode(reencrypted_secret).decode()
        