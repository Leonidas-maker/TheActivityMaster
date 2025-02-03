from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from pathlib import Path
import secrets
from typing import Optional, cast
import base64

from config.security import EC_ENCRYPTION_KEY_PATH

class AsymmetricECEncryptor:
    def __init__(self, public_key_path: Path = EC_ENCRYPTION_KEY_PATH, private_key_path: Optional[Path] = None):
        """Initialize the EC encryptor with paths for public and private keys.

        :param public_key_path: Path to store/load the public key
        :param private_key_path: Path to store/load the private key (defaults to 'private_key.pem' in same directory)
        """
        self.public_key_path = public_key_path
        self.private_key_path = private_key_path or public_key_path.parent / "private_key.pem"

        # Generate new key pair if public key doesn't exist
        if not self.public_key_path.exists():
            self._generate_key_pair()

        # Load existing public key
        self.public_key = self._load_public_key()

        # Load private key if available
        self.private_key = self._load_private_key() if self.private_key_path.exists() else None

    def _generate_key_pair(self):
        """Generate and store new EC key pair (SECP384R1 curve)."""
        private_key = ec.generate_private_key(ec.SECP384R1(), default_backend())
        public_key = private_key.public_key()

        # Save public key
        pub_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        self.public_key_path.write_bytes(pub_pem)

        # Save private key
        priv_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        self.private_key_path.write_bytes(priv_pem)

    def _load_public_key(self) -> ec.EllipticCurvePublicKey:
        """Load and validate EC public key from specified path."""
        public_key = serialization.load_pem_public_key(
            self.public_key_path.read_bytes(),
            backend=default_backend()
        )
        
        if not isinstance(public_key, ec.EllipticCurvePublicKey):
            raise ValueError("Loaded key is not an EC public key")
            
        return cast(ec.EllipticCurvePublicKey, public_key)

    def _load_private_key(self) -> Optional[ec.EllipticCurvePrivateKey]:
        """Load and validate EC private key from specified path."""
        private_key = serialization.load_pem_private_key(
            self.private_key_path.read_bytes(),
            password=None,
            backend=default_backend()
        )
        
        if not isinstance(private_key, ec.EllipticCurvePrivateKey):
            raise ValueError("Loaded key is not an EC private key")
            
        return cast(ec.EllipticCurvePrivateKey, private_key)

    def encrypt(self, plaintext: str) -> str:
        """Encrypt data using ECIES with proper salt handling."""
        # Generate ephemeral key pair
        ephemeral_key = ec.generate_private_key(ec.SECP384R1(), default_backend())
        ephemeral_pubkey = ephemeral_key.public_key()

        # Generate fresh random salt (16 bytes recommended)
        salt = secrets.token_bytes(16)
        
        # Key exchange and derivation
        shared_secret = ephemeral_key.exchange(ec.ECDH(), self.public_key)
        
        aes_key = HKDF(
            algorithm=hashes.SHA512(),
            length=32,
            salt=salt,
            info=b'ecies-encryption',
            backend=default_backend()
        ).derive(shared_secret)

        # Encrypt with AES-GCM
        iv = secrets.token_bytes(12)
        cipher = Cipher(algorithms.AES(aes_key), modes.GCM(iv), backend=default_backend())
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(plaintext.encode()) + encryptor.finalize()

        # Format: ephemeral_pubkey (97) + salt (16) + iv (12) + tag (16) + ciphertext
        res =(
            ephemeral_pubkey.public_bytes(
                encoding=serialization.Encoding.X962,
                format=serialization.PublicFormat.UncompressedPoint
            )
            + salt
            + iv
            + encryptor.tag
            + ciphertext
        )
        return base64.b64encode(res).decode()

    def decrypt(self, encrypted_data_str: str) -> str:
        """Decrypt data using stored private key."""
        if not self.private_key:
            raise ValueError("Decryption requires private key")

        encrypted_data = base64.b64decode(encrypted_data_str)

        # Parse components (adjust indices based on new format)
        if len(encrypted_data) < 97 + 16 + 12 + 16:
            raise ValueError("Invalid encrypted data format")

        ephemeral_pubkey_bytes = encrypted_data[:97]
        salt = encrypted_data[97:113]    # 16 bytes
        iv = encrypted_data[113:125]     # 12 bytes
        tag = encrypted_data[125:141]    # 16 bytes
        ciphertext = encrypted_data[141:] 

        ephemeral_pubkey = ec.EllipticCurvePublicKey.from_encoded_point(
            ec.SECP384R1(),
            ephemeral_pubkey_bytes
        )

        # Key exchange and derivation
        shared_secret = self.private_key.exchange(ec.ECDH(), ephemeral_pubkey)
        
        aes_key = HKDF(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            info=b'ecies-encryption',
            backend=default_backend()
        ).derive(shared_secret)

        # Decrypt with AES-GCM
        cipher = Cipher(algorithms.AES(aes_key), modes.GCM(iv, tag), backend=default_backend())
        decryptor = cipher.decryptor()
        
        return (decryptor.update(ciphertext) + decryptor.finalize()).decode()