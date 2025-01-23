from tkinter import E
from annotated_types import T
from cryptography.hazmat.primitives.serialization import (
    load_pem_private_key,
    load_pem_public_key,
)
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.asymmetric.types import PrivateKeyTypes, PublicKeyTypes 

from pathlib import Path
from typing import Tuple, Union, Optional
import os

from config.settings import ENVIRONMENT
from config.security import TOKEN_KEYFILES_PATH, TOKEN_KEYFILES_PREFIX

###########################################################################
################################## Helper #################################
###########################################################################
# ======================================================== #
# ================== Key File Operations ================= #
# ======================================================== #
def load_private_key(
    file_name: str,
    key_password: Optional[bytes] = None,
    folder_path: Path = TOKEN_KEYFILES_PATH,
) -> ec.EllipticCurvePrivateKey:
    """
    Load the private key from a file

    :param file_name: The name of the file to load the key from
    :param key_password: The password for the key
    :param folder_path: The path to the folder to load the key from
    :return: The private key loaded from the file

    :raises RuntimeError: If the file is not found
    """
    key = None
    try:
        file = folder_path / f"{TOKEN_KEYFILES_PREFIX}{file_name}.pem"
        with file.open("rb") as key_file:
            key = load_pem_private_key(key_file.read(), password=key_password, backend=default_backend())

    except FileNotFoundError as e:
        raise RuntimeError(f"Private key: {file_name} not found") from e

    if isinstance(key, ec.EllipticCurvePrivateKey):
        return key
    else:
        raise RuntimeError(f"Private key is not an ECDSA key: {file_name}")

def load_public_key(
    file_name: str,
    folder_path: Path = TOKEN_KEYFILES_PATH,
) -> ec.EllipticCurvePublicKey:
    """
    Load the public key from a file

    :param file_name: The name of the file to load the key from
    :param folder_path: The path to the folder to load the key from
    :return: The public key loaded from the file
    
    :raises RuntimeError: If the file is not found
    """
    key = None
    try:
        file = folder_path / f"{TOKEN_KEYFILES_PREFIX}{file_name}.pem"
        with file.open("rb") as key_file:
            key = load_pem_public_key(key_file.read(), backend=default_backend())
    except FileNotFoundError as e:
        raise RuntimeError(f"Public key: {file_name} not found") from e

    if isinstance(key, ec.EllipticCurvePublicKey):
        return key
    else:
        raise RuntimeError(f"Public key is not an ECDSA key: {file_name}")

def save_key(key: bytes, file_name: str, folder_path: Path):
    """
    Save the key to a file

    :param key: The key to save
    :param file_name: The name of the file to save the key to
    """
    file = folder_path / f"{TOKEN_KEYFILES_PREFIX}{file_name}.pem"
    if file.exists():
        os.remove(file)
    with file.open("wb") as key_file:
        key_file.write(key)

###########################################################################
################################# Gen Keys ################################
###########################################################################
def generate_ecdsa_keys(curve: ec.EllipticCurve):
    """
    Generate the ECDSA keys

    :param curve: The curve to use for the keys
    :return: The private and public keys in PEM format
    """

    # Generate the private key
    private_key = ec.generate_private_key(curve)

    # Get the public key from the private key
    public_key = private_key.public_key()

    # Convert the keys to PEM format
    pem_private_key = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )
    pem_public_key = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )

    return pem_private_key, pem_public_key

def check_keys_exist(folder_path: Path = TOKEN_KEYFILES_PATH) -> bool:
    """
    Check if the keys exist

    :param folder_path: The path to the folder to save the keys
    :return: True if the keys exist, False otherwise
    """
    files = os.listdir(folder_path)
    needed_files = ["security_private_key.pem", "security_public_key.pem", "access_private_key.pem", "access_public_key.pem", "refresh_private_key.pem", "refresh_public_key.pem"]
    return all([file in files for file in needed_files])

def generate_keys(folder_path: Path = TOKEN_KEYFILES_PATH):
    """
    Generate the keys for the tokens

    :param folder_path: The path to the folder to save the keys
    """
    os.makedirs(folder_path, exist_ok=True)

    if check_keys_exist(folder_path):
        return
    elif ENVIRONMENT != "dev":
        raise RuntimeError("Key files are missing")
    
    security_private_key, security_public_key = generate_ecdsa_keys(ec.SECP256R1())
    access_private_key, access_public_key = generate_ecdsa_keys(ec.SECP256R1())
    refresh_private_key, refresh_public_key = generate_ecdsa_keys(ec.SECP521R1())

    # Save the keys to files
    save_key(security_private_key, "security_private_key", folder_path)
    save_key(security_public_key, "security_public_key", folder_path)
    save_key(access_private_key, "access_private_key", folder_path)
    save_key(access_public_key, "access_public_key", folder_path)
    save_key(refresh_private_key, "refresh_private_key", folder_path)
    save_key(refresh_public_key, "refresh_public_key", folder_path)


###########################################################################
################################## Getter #################################
###########################################################################
#* ======================================================== #
#* ====================== Private Keys ==================== #
#* ======================================================== #
def get_auth_keys_private(
) -> Tuple[ec.EllipticCurvePrivateKey, ec.EllipticCurvePrivateKey]:
    """
    Get the private keys for the tokens, generate if not exist
    
    :param folder_path: The path to the folder to save the keys
    :return: The private keys for the tokens [refresh, access]
    """
    refresh_private_key = load_private_key("refresh_private_key")
    access_private_key = load_private_key("access_private_key")

    return refresh_private_key, access_private_key

def get_security_token_private(
) -> ec.EllipticCurvePrivateKey:
    """
    Get the private key for security tokens, generate if not exist

    :param folder_path: The path to the folder to save the keys
    :return: The private key for security tokens    
    """
    security_private_key = load_private_key("security_private_key")
    return security_private_key


#* ======================================================== #
#* ====================== Public Keys ===================== #
#* ======================================================== #
def get_refresh_token_public(
) -> ec.EllipticCurvePublicKey:
    """
    Get the public key for refresh tokens, generate if not exist

    :param folder_path: The path to the folder to save the keys
    :return: The public key for refresh tokens
    """
    public_key = load_public_key("refresh_public_key")
    return public_key

def get_access_token_public(
) -> ec.EllipticCurvePublicKey:
    """
    Get the public key for access tokens, generate if not exist

    :param folder_path: The path to the folder to save the keys
    :return: The public key for access tokens
    """
    public_key = load_public_key("access_public_key")
    return public_key


def get_security_token_public(
) -> ec.EllipticCurvePublicKey:
    """
    Get the public key for security tokens, generate if not exist

    :param folder_path: The path to the folder to save the keys
    :return: The public key for security tokens
    """
    public_key = load_public_key("security_public_key")
    return public_key