from re import U
from sys import audit
import trace
from annotated_types import T
from anyio import current_time
from fastapi import HTTPException, security
from typing import Tuple
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
import jwt
import hashlib
import traceback
import datetime
import pyotp
import time

from config.settings import DEBUG, DEFAULT_TIMEZONE
from config.security import TOKEN_ISSUER

import models.m_user as m_user
import models.m_audit as m_audit

import schemas.s_auth as s_auth

from utils import jwt_keyfiles
from utils.time import unix_timestamp

from crud import audit as audit_crud
from crud import auth as auth_crud, user as user_crud

from core import security as core_security

from data.auth import TokenDetails


###########################################################################
############################## Token Creation #############################
###########################################################################
async def create_2fa_token(
    db: AsyncSession, user: m_user.User, application_id: str, ip_address: str, audit_logger: audit_crud.AuditLogger
) -> str:
    """
    Create a 2FA token for a user

    :param db: The database session
    :param user: The user to create the token for
    :return: The 2FA token
    """
    if not audit_logger:
        audit_logger = audit_crud.AuditLogger(db)
    current_timestamp = unix_timestamp()

    try:
        # Get the private key
        security_token_key = jwt_keyfiles.get_security_token_private()

        # Hash the application ID
        hashed_application_id = core_security.sha256_salt(application_id)

        # Generate the JWT ID and expiration times
        security_token_details = TokenDetails(jti=uuid.uuid4(), exp=unix_timestamp(minutes=5))

        # Generate the 2FA token
        token = jwt.encode(
            {
                "iss": TOKEN_ISSUER,
                "sub": str(user.id),
                "exp": security_token_details.exp,
                "jti": str(security_token_details.jti),
                "aud": hashed_application_id,
                "iat": current_timestamp,
            },
            security_token_key,
            algorithm="ES256",
        )

        # Save the token information to the database
        await auth_crud.save_security_token(db, user.id, hashed_application_id, security_token_details)

        # Log the token creation
        audit_logger.token_creation(
            user.id, ip_address, hashed_application_id, security_token_details.jti, log_creation=True
        )

        return token
    except Exception as e:
        await db.rollback()
        audit_logger.sys_critical("Failed to create 2FA token", traceback=traceback.format_exc())
        await db.commit()
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Failed to create 2FA token. Please try again later.")


async def create_auth_tokens(db: AsyncSession, user_id: uuid.UUID, application_id: str, ip_address: str) -> Tuple[str, str]:
    """
    Create the access and refresh tokens for a user

    :param db: The database session
    :param user: The user to create the tokens for
    :param application_id: The application ID to create the tokens for
    :return: The access and refresh tokens: (access_token, refresh_token)
    """
    audit_logger = audit_crud.AuditLogger(db)
    current_timestamp = unix_timestamp()

    try:
        # Get the private keys
        refresh_token_key, access_token_key = jwt_keyfiles.get_auth_keys_private()

        # Get the user ID
        user_id_str = str(user_id)

        # Hash the application ID
        hashed_application_id = core_security.sha256_salt(application_id)

        # Generate the JWT ID and expiration times
        access_token_details = TokenDetails(jti=uuid.uuid4(), exp=unix_timestamp(minutes=12))
        refresh_token_details = TokenDetails(jti=uuid.uuid4(), exp=unix_timestamp(days=7))

        # Generate the access token
        access_token = jwt.encode(
            {
                "iss": TOKEN_ISSUER,
                "sub": user_id_str,
                "exp": access_token_details.exp,
                "jti": str(access_token_details.jti),
                "aud": hashed_application_id,
                "iat": current_timestamp,
            },
            access_token_key,
            algorithm="ES256",
        )

        # Generate the refresh token
        refresh_token = jwt.encode(
            {
                "iss": TOKEN_ISSUER,
                "sub": user_id_str,
                "exp": refresh_token_details.exp,
                "jti": str(refresh_token_details.jti),
                "aud": hashed_application_id,
                "iat": current_timestamp,
                "nbf": unix_timestamp(minutes=8),
            },
            refresh_token_key,
            algorithm="ES512",
        )

        # Save the token information to the database
        await auth_crud.save_auth_tokens(
            db, user_id, hashed_application_id, access_token_details, refresh_token_details
        )

        # Log the token creation
        audit_logger.token_creation(user_id, ip_address, application_id, access_token_details.jti)

        await db.flush()
        return access_token, refresh_token
    except Exception as e:
        await db.rollback()
        audit_logger.sys_critical("Failed to create tokens", traceback=traceback.format_exc())
        await db.commit()
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Failed to create tokens. Please try again later.")


###########################################################################
################################### MAIN ##################################
###########################################################################


async def login(db: AsyncSession, login_form: s_auth.LoginRequest, ip_address: str) -> Tuple[str, list[m_user.User2FAMethods]]:
    """
    Check the user's password and handle 2FA login process.

    :param db: The database session
    :param login_form: The login form containing email and password
    :param ip_address: The IP address of the user
    :return: A dictionary with a security token and available 2FA methods
    """
    user = await user_crud.get_user_by_email(db, login_form.email)
    if not user:
        raise HTTPException(status_code=400, detail="Invalid email or password")

    audit_logger = audit_crud.AuditLogger(db)
    try:
        if not core_security.verify_password(login_form.password, user.password):
            audit_logger.user_login_failed(user.id, ip_address)
            raise HTTPException(status_code=400, detail="Invalid email or password")

        audit_logger.user_login(user.id, ip_address)

        security_token = await create_2fa_token(db, user, login_form.application_id, ip_address, audit_logger)

        # Get the 2FA methods
        res = await db.execute(select(m_user.User2FA.id, m_user.User2FA.method).filter(m_user.User2FA.user_id == user.id))
        methods_2fa = {method: id for id, method in res.all()}

        # Handle case where EMAIL is the only 2FA method
        if not methods_2fa or (len(methods_2fa) == 1 and m_user.User2FAMethods.EMAIL in methods_2fa):
            if m_user.User2FAMethods.EMAIL in methods_2fa:
                # Delete the existing EMAIL 2FA method
                email_2fa_id = methods_2fa[m_user.User2FAMethods.EMAIL]
                await db.execute(delete(m_user.User2FA).where(m_user.User2FA.id == email_2fa_id))
            else:
                methods_2fa[m_user.User2FAMethods.EMAIL] = None

            # Create a new email code and potentially add a new 2FA entry
            email_code = await auth_crud.create_email_code(db, user)
            # TODO: Send the email with the 2FA code here
            if DEBUG:
                print(f"Email code: {email_code}")

        await db.commit()

        return security_token, list(methods_2fa.keys())
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        audit_logger.sys_critical(f"Failed to login user {user.id}", traceback=str(e))
        await db.commit()
        raise HTTPException(status_code=500, detail="Failed to login. Please try again later.")


async def verify_2fa(db: AsyncSession, security_token: str, metadata: s_auth.LoginCode2fa, ip_address: str) -> Tuple[str, str]:
    """Verify a 2FA code and return the access and refresh tokens

    :param AsyncSession: The database session
    :param str: The security token
    :param str: The 2FA code
    :return: The access and refresh tokens
    """
    audit_logger = audit_crud.AuditLogger(db)

    token_payload = await auth_crud.verify_token(db, security_token, m_user.TokenTypes.SECURITY, metadata.application_id)

    if not token_payload:
        raise HTTPException(status_code=401, detail="Invalid security token")

    res = await db.execute(
        select(m_user.User2FA).filter(
            m_user.User2FA.user_id == uuid.UUID(token_payload["sub"]),
            m_user.User2FA.method == (m_user.User2FAMethods.TOTP if metadata.is_totp else m_user.User2FAMethods.EMAIL),
        )
    )
    user_2fa = res.scalar_one_or_none()

    if not user_2fa:
        raise HTTPException(status_code=401, detail="Invalid 2FA method")

    if metadata.is_totp:
        # Check for too many failed attempts
        if user_2fa.fails >= 3 and user_2fa.updated_at > datetime.datetime.now(DEFAULT_TIMEZONE) - datetime.timedelta(minutes=5):
            audit_logger.user_2fa_failed(user_2fa.user_id, ip_address, m_audit.AuthMethods.TOTP, "Too many failed attempts.")
            await db.commit()
            raise HTTPException(status_code=429, detail="Too many failed attempts. Please try again later.")
        else:
            user_2fa.fails = 0

        # Handle TOTP verification
        totp = pyotp.TOTP(user_2fa.key_handle)
        if not totp.verify(metadata.code):
            user_2fa.fails += 1
            await db.commit()
            raise HTTPException(status_code=401, detail="Invalid 2FA code")
    else:
        # Check for too many failed attempts
        if user_2fa.fails >= 3:
            await auth_crud.delete_token(db, uuid.UUID(token_payload["jti"]))
            await auth_crud.delete_single_2fa(db, user_2fa.user_id, user_2fa.id)
            audit_logger.user_2fa_failed(user_2fa.user_id, ip_address, m_audit.AuthMethods.EMAIL, f"Too many failed attempts. 2FA method {user_2fa.id} deleted.")
            await db.commit()
            raise HTTPException(status_code=429, detail="Too many failed attempts. Please try again later.")

        # Handle email code verification
        if not core_security.sha256_salt_verify(metadata.code, user_2fa.public_key):
            user_2fa.fails += 1
            await db.commit()
            raise HTTPException(status_code=401, detail="Invalid 2FA code")

    # Create the access and refresh tokens
    await auth_crud.delete_token(db, uuid.UUID(token_payload["jti"]))
    access_token, refresh_token = await create_auth_tokens(db, user_2fa.user_id, metadata.application_id, ip_address)

    await db.commit()
    return access_token, refresh_token