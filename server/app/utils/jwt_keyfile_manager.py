from cryptography.hazmat.primitives.serialization import (
    load_pem_private_key,
    load_pem_public_key,
)
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec

from pathlib import Path
from typing import Tuple, Optional, Union
import os

from config.settings import ENVIRONMENT
from config.security import TOKEN_KEYFILES_PATH, TOKEN_KEYFILES_PREFIX

class JWTKeyManager:
    def __init__(
        self,
        keyfiles_path: Path = TOKEN_KEYFILES_PATH,
        keyfiles_prefix: str = TOKEN_KEYFILES_PREFIX,
        environment: str = ENVIRONMENT
    ):
        self.keyfiles_path = keyfiles_path
        self.keyfiles_prefix = keyfiles_prefix
        self.environment = environment
        self._ensure_keys_exist()

    def _ensure_keys_exist(self) -> None:
        """Generate keys if they don't exist (only in dev environment)."""
        if not self._check_keys_exist():
            if self.environment != "dev":
                raise RuntimeError("Key files are missing in non-dev environment.")
            self.generate_keys()

    def _check_keys_exist(self) -> bool:
        """Check if all required key files exist."""
        required_files = [
            "security_private_key.pem", "security_public_key.pem",
            "access_private_key.pem", "access_public_key.pem",
            "refresh_private_key.pem", "refresh_public_key.pem"
        ]
        os.makedirs(self.keyfiles_path, exist_ok=True)
        existing_files = os.listdir(self.keyfiles_path)
        return all(f in existing_files for f in required_files)

    def _save_key(self, key: bytes, name: str) -> None:
        """Save a key to a file with the given name."""
        file_path = self.keyfiles_path / f"{self.keyfiles_prefix}{name}.pem"
        if file_path.exists():
            os.remove(file_path)
        with file_path.open("wb") as f:
            f.write(key)

    def _generate_ecdsa_keypair(self, curve: ec.EllipticCurve) -> Tuple[bytes, bytes]:
        """Generate an ECDSA keypair and return PEM-encoded keys."""
        private_key = ec.generate_private_key(curve)
        public_key = private_key.public_key()

        pem_private = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )
        pem_public = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )
        return pem_private, pem_public

    def generate_keys(self) -> None:
        """Generate all required keys and save them to files."""
        os.makedirs(self.keyfiles_path, exist_ok=True)

        # Security tokens (e.g., for sensitive operations)
        sec_priv, sec_pub = self._generate_ecdsa_keypair(ec.SECP256R1())
        self._save_key(sec_priv, "security_private_key")
        self._save_key(sec_pub, "security_public_key")

        # Access tokens
        acc_priv, acc_pub = self._generate_ecdsa_keypair(ec.SECP256R1())
        self._save_key(acc_priv, "access_private_key")
        self._save_key(acc_pub, "access_public_key")

        # Refresh tokens (using stronger curve)
        ref_priv, ref_pub = self._generate_ecdsa_keypair(ec.SECP521R1())
        self._save_key(ref_priv, "refresh_private_key")
        self._save_key(ref_pub, "refresh_public_key")

    def _load_private_key(self, name: str, password: Optional[bytes] = None) -> ec.EllipticCurvePrivateKey:
        """Internal method to load a private key from file."""
        file_path = self.keyfiles_path / f"{self.keyfiles_prefix}{name}.pem"
        try:
            with file_path.open("rb") as f:
                data = f.read()
                key = load_pem_private_key(
                    data, 
                    password=password, 
                    backend=default_backend()
                )
                if not isinstance(key, ec.EllipticCurvePrivateKey):
                    raise ValueError(f"Invalid private key type: {name}")
                return key
        except FileNotFoundError as e:
            raise RuntimeError(f"Private key file not found: {name}") from e

    def _load_public_key(self, name: str) -> ec.EllipticCurvePublicKey:
        """Internal method to load a public key from file."""
        file_path = self.keyfiles_path / f"{self.keyfiles_prefix}{name}.pem"
        try:
            with file_path.open("rb") as f:
                data = f.read()
                key = load_pem_public_key(
                    data, 
                    backend=default_backend()
                )
                if not isinstance(key, ec.EllipticCurvePublicKey):
                    raise ValueError(f"Invalid public key type: {name}")
                return key
        except FileNotFoundError as e:
            raise RuntimeError(f"Public key file not found: {name}") from e

    # Public properties for key access
    @property
    def security_private_key(self) -> ec.EllipticCurvePrivateKey:
        return self._load_private_key("security_private_key")

    @property
    def security_public_key(self) -> ec.EllipticCurvePublicKey:
        return self._load_public_key("security_public_key")

    @property
    def access_private_key(self) -> ec.EllipticCurvePrivateKey:
        return self._load_private_key("access_private_key")

    @property
    def access_public_key(self) -> ec.EllipticCurvePublicKey:
        return self._load_public_key("access_public_key")

    @property
    def refresh_private_key(self) -> ec.EllipticCurvePrivateKey:
        return self._load_private_key("refresh_private_key")

    @property
    def refresh_public_key(self) -> ec.EllipticCurvePublicKey:
        return self._load_public_key("refresh_public_key")
