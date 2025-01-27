import re
from turtle import st
import pyotp
import secrets
import bcrypt
import jwt
from datetime import datetime, timezone, timedelta
import uuid
from typing import Tuple, Union, Optional
from sqlalchemy.ext.asyncio import AsyncSession
import hashlib
from sqlalchemy import delete, select
import time

from config.settings import ENVIRONMENT, DEFAULT_TIMEZONE
from config.security import TOKEN_ISSUER
from models.m_user import User, UserToken, TokenTypes, User2FA, User2FAMethods
from core import security as core_security
from utils import jwt_keyfiles
from crud import audit as audit_crud
from data.auth import TokenDetails


###########################################################################
################################### MAIN ##################################
###########################################################################
async def save_auth_tokens(
    db: AsyncSession,
    user_id: uuid.UUID,
    hashed_application_id: str,
    access_token_details: TokenDetails,
    refresh_token_details: TokenDetails,
):
    """Save the authentication tokens to the database.

    :param db: The database session
    :param user_id: The user ID to save the tokens for
    :param hashed_application_id: The hashed application ID to apply the tokens for
    :param access_token_details: The access token details
    :param refresh_token_details: The refresh token details
    """
    # Access token
    db.add(
        UserToken(
            id=access_token_details.jti,
            user_id=user_id,
            application_id_hash=hashed_application_id,
            token_type=TokenTypes.ACCESS,
            expires_at=datetime.fromtimestamp(access_token_details.exp, tz=DEFAULT_TIMEZONE),
        )
    )

    # Refresh token
    db.add(
        UserToken(
            id=refresh_token_details.jti,
            user_id=user_id,
            application_id_hash=hashed_application_id,
            token_type=TokenTypes.REFRESH,
            expires_at=datetime.fromtimestamp(refresh_token_details.exp, tz=DEFAULT_TIMEZONE),
        )
    )

    await db.flush()


async def save_security_token(
    db: AsyncSession, user_id: uuid.UUID, hashed_application_id: str, token_details: TokenDetails
):
    """Save the security token information to the database

    :param db: The database session
    :param user_id: The user ID to save the token for
    :param hashed_application_id: The hashed application ID to apply the token for
    :param token_details: Details of the security token
    """
    db.add(
        UserToken(
            id=token_details.jti,
            user_id=user_id,
            application_id_hash=hashed_application_id,
            token_type=TokenTypes.SECURITY,
            expires_at=datetime.fromtimestamp(token_details.exp, tz=DEFAULT_TIMEZONE),
        )
    )

    await db.flush()


async def verify_token(db: AsyncSession, token: str, token_type: TokenTypes, application_id: str) -> dict:
    """Verify the token

    :param db: The database session
    :param token: The token to verify
    :param token_type: The type of token
    :param application_id: The application ID
    :raises ValueError: If the token type is invalid
    :return: True if the token is valid, False otherwise
    """
    if not token or len(token.split(".")) != 3:
        return {}

    # Get the public key
    match token_type:
        case TokenTypes.ACCESS:
            jwt_key = jwt_keyfiles.get_access_token_public()
            algorithm = "ES256"
        case TokenTypes.REFRESH:
            jwt_key = jwt_keyfiles.get_refresh_token_public()
            algorithm = "ES512"
        case TokenTypes.SECURITY:
            jwt_key = jwt_keyfiles.get_security_token_public()
            algorithm = "ES256"
        case _:
            raise ValueError("Invalid token type")

    payload = jwt.decode(token, algorithms=algorithm, options={"verify_signature": False})
    salt, _ = payload["aud"].split(".")

    hashed_application_id = core_security.sha256_salt(application_id, salt)

    # Verify the token
    try:
        payload = jwt.decode(token, jwt_key, algorithms=algorithm, audience=hashed_application_id, issuer=TOKEN_ISSUER)
    except jwt.ExpiredSignatureError:
        return {}
    except jwt.InvalidTokenError:
        return {}

    # Check if the token and corresponding information exists in the database
    res = await db.execute(select(UserToken).filter(UserToken.id == uuid.UUID(payload["jti"])))
    token_db = res.scalar_one_or_none()
    if not token_db:
        return {}
    if (
        not core_security.sha256_salt_verify(application_id, token_db.application_id_hash)
        and token_db.token_type != token_type
        and token_db.user_id != payload["sub"]
    ):
        return {}
    return payload

async def delete_token(db: AsyncSession, jti: uuid.UUID) -> int:
    """Delete a token from the database

    :param db: The database session
    :param jti: The JTI of the token to delete
    :return: The number of tokens deleted
    """
    res = await db.execute(delete(UserToken).filter(UserToken.id == jti))
    return res.rowcount


async def delete_auth_tokens(db: AsyncSession, user_id: uuid.UUID, hashed_application_id: str) -> int:
    """Delete the authentication tokens for a user

    :param db: The database session
    :param user: The user to delete the tokens for
    :param application_id: The application ID to delete the tokens for
    :return: The number of tokens deleted
    """
    res = await db.execute(
        delete(UserToken).filter(UserToken.user_id == user_id, UserToken.application_id_hash == hashed_application_id)
    )
    return res.rowcount


###########################################################################
################################### 2FA ###################################
###########################################################################
async def create_email_code(db: AsyncSession, user: User) -> str:
    """Create an email code for 2FA

    :param db: The database session
    :param user: The user to create the email code for
    :return: The email code
    """
    # Generate the email code
    email_code = str(secrets.randbelow(1000000)).zfill(6)
    email_code_hash = core_security.sha256_salt(email_code)

    email_2fa = User2FA(user_id=user.id, method=User2FAMethods.EMAIL, public_key=email_code_hash)
    db.add(email_2fa)

    return email_code

async def delete_single_2fa(db: AsyncSession, user_id: uuid.UUID, id_2fa: uuid.UUID) -> int:
    """Delete a single 2FA method

    :param db: The database session
    :param user: The user to delete the 2FA method for
    :param id: The ID of the 2FA method to delete
    :return: The number of 2FA methods deleted
    """
    res = await db.execute(delete(User2FA).filter(User2FA.user_id == user_id, User2FA.id == id_2fa))
    return res.rowcount

###########################################################################
############################## Recurring Task #############################
###########################################################################
async def clean_tokens(db: AsyncSession) -> int:
    """Clean up expired tokens

    :param db: The database session
    :return: The number of tokens deleted
    """
    # Add audit logs
    audit_log = audit_crud.AuditLogger(db)
    audit_log.sys_info("Cleaning up expired tokens")

    # Delete expired tokens
    res = await db.execute(delete(UserToken).where(UserToken.expires_at < datetime.now(tz=timezone.utc)))

    # Add audit logs
    audit_log.sys_info("Cleaned up expired tokens completed.", details="Deleted {res.rowcount} expired tokens")
    await db.commit()
    return res.rowcount
