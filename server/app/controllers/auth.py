from fastapi import HTTPException
from typing import Tuple
import uuid
from sqlalchemy import select, delete
import jwt
import datetime
from typing import List, Union
import traceback

from config.settings import DEBUG, DEFAULT_TIMEZONE
from config.security import TOKEN_ISSUER

import models.m_user as m_user
import models.m_audit as m_audit

import schemas.s_auth as s_auth

from utils.time import unix_timestamp

from crud import audit as audit_crud
from crud import auth as auth_crud, user as user_crud

from core import security as core_security
from core.generic import EndpointContext

from data.auth import TokenDetails


###########################################################################
############################## Token Creation #############################
###########################################################################
async def create_security_token(
    ep_context: EndpointContext,
    user_id: uuid.UUID,
    application_id: str,
    amr: List[str],
    ip_address: str,
) -> str:
    """
    Create a 2FA token for a user

    :param ep_context: The endpoint context
    :param user: The user to create the token for
    :param application_id: The application ID to create the token for
    :param amr: The authentication methods used
    :param ip_address: The IP address of the user
    :return: The 2FA token
    """
    db = ep_context.db
    audit_logger = ep_context.audit_logger
    current_timestamp = unix_timestamp()

    # Get the private key
    with core_security.jwt_key_manager_dependency.get() as km:
        security_token_key = km.security_private_key

    # Hash the application ID
    hashed_application_id = core_security.sha256_salt(application_id)

    # Generate the JWT ID and expiration times
    security_token_details = TokenDetails(jti=uuid.uuid4(), exp=unix_timestamp(minutes=5))

    # Generate the 2FA token
    token = jwt.encode(
        {
            "iss": TOKEN_ISSUER,
            "sub": str(user_id),
            "exp": security_token_details.exp,
            "jti": str(security_token_details.jti),
            "aud": hashed_application_id,
            "iat": current_timestamp,
            "amr": amr,
        },
        security_token_key,
        algorithm="ES256",
    )

    # Save the token information to the database
    await auth_crud.save_security_token(db, user_id, hashed_application_id, security_token_details)

    # Log the token creation
    audit_logger.token_creation(
        user_id, ip_address, hashed_application_id, security_token_details.jti, log_creation=True
    )

    return token


async def create_auth_tokens(
    ep_context: EndpointContext, user_id: uuid.UUID, application_id: str, ip_address: str, log_creation: bool = False
) -> Tuple[str, str]:
    """
    Create the access and refresh tokens for a user

    :param ep_context: The endpoint context
    :param user: The user to create the tokens for
    :param application_id: The application ID to create the tokens for
    :param ip_address: The IP address of the user
    :param log_creation: Whether to log the initial token creation or only the refresh token creation (default: False)
    :return: The access and refresh tokens: (access_token, refresh_token)
    """
    db = ep_context.db
    audit_logger = ep_context.audit_logger
    current_timestamp = unix_timestamp()

    # Get the private keys
    with core_security.jwt_key_manager_dependency.get() as km:
        refresh_token_key = km.refresh_private_key
        access_token_key = km.access_private_key

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
    await auth_crud.save_auth_tokens(db, user_id, hashed_application_id, access_token_details, refresh_token_details)

    # Log the token creation
    audit_logger.token_creation(user_id, ip_address, application_id, access_token_details.jti, log_creation)
    audit_logger.token_creation(user_id, ip_address, application_id, refresh_token_details.jti, log_creation)

    await db.flush()
    return access_token, refresh_token


###########################################################################
################################### MAIN ##################################
###########################################################################


async def login(
    ep_context: EndpointContext, login_form: s_auth.LoginRequest, ip_address: str, application_id: str
) -> Tuple[str, list[m_user.User2FAMethods]]:
    """
    Check the user's password and handle 2FA login process.

    :param ep_context: The endpoint context
    :param login_form: The login form containing ident and password
    :param ip_address: The IP address of the user
    :return: A dictionary with a security token and available 2FA methods
    """
    db = ep_context.db
    audit_logger = ep_context.audit_logger

    if not application_id:
        raise HTTPException(status_code=401, detail="Invalid application ID")

    user = await user_crud.get_user_by_ident(db, login_form.ident)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    if user.is_anonymized or user.is_system:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    if not core_security.verify_password(login_form.password, user.password):
        audit_logger.user_login_failed(user.id, ip_address)
        raise HTTPException(status_code=401, detail="Invalid email or password")

    for generic_role in user.generic_roles:
        if generic_role.name == "NotEmailVerified":
            # TODO: Send the email verification email here if the last email was sent more than 30 minutes ago
            raise HTTPException(status_code=401, detail="Email address not verified")

    audit_logger.user_login(user.id, ip_address)

    security_token = await create_security_token(ep_context, user.id, application_id, ["2fa"], ip_address)

    # Get the 2FA methods
    res = await db.execute(select(m_user.User2FA.id, m_user.User2FA.method).filter(m_user.User2FA.user_id == user.id))
    methods_2fa = {method: id for id, method in res.all()}

    # Handle case where EMAIL is the only 2FA method
    if not methods_2fa or (len(methods_2fa) == 1 and m_user.User2FAMethods.EMAIL in methods_2fa):
        if m_user.User2FAMethods.EMAIL in methods_2fa:
            # Delete the existing EMAIL 2FA method
            email_2fa_id = methods_2fa[m_user.User2FAMethods.EMAIL]
            await auth_crud.delete_single_2fa(db, user.id, email_2fa_id)
        else:
            methods_2fa[m_user.User2FAMethods.EMAIL] = None

        # Create a new email code and potentially add a new 2FA entry
        email_code = await auth_crud.create_email_code(db, user)
        # TODO: Send the email with the 2FA code here
        if DEBUG:
            print(f"Email code: {email_code}")

    await db.commit()

    return security_token, list(methods_2fa.keys())


async def verify_code_2fa(
    ep_context: EndpointContext,
    token_details: core_security.TokenDetails,
    metadata: s_auth.LoginCode2fa,
    ip_address: str,
) -> Tuple[str, str]:
    """Verify a 2FA code and return the access and refresh tokens

    :param db: The database session
    :param token_details: The token details
    :param metadata: The metadata for the 2FA code
    :param ip_address: The IP address of the user
    :return: The access and refresh tokens
    """
    db = ep_context.db
    audit_logger = ep_context.audit_logger

    res = await db.execute(
        select(m_user.User2FA).filter(
            m_user.User2FA.user_id == uuid.UUID(token_details.payload["sub"]),
            m_user.User2FA.method == (m_user.User2FAMethods.TOTP if metadata.is_totp else m_user.User2FAMethods.EMAIL),
            m_user.User2FA.fails != -1,
        )
    )
    user_2fa = res.scalar_one_or_none()

    if not user_2fa:
        raise HTTPException(status_code=401, detail="Invalid 2FA method")

    if metadata.is_totp:
        # Check for too many failed attempts
        if user_2fa.fails >= 3:
            if user_2fa.updated_at.replace(tzinfo=DEFAULT_TIMEZONE) > datetime.datetime.now(
                DEFAULT_TIMEZONE
            ) - datetime.timedelta(minutes=5):
                audit_logger.user_2fa_failed(
                    user_2fa.user_id, ip_address, m_audit.AuthMethods.TOTP, "Too many failed attempts."
                )
                await db.commit()
                raise HTTPException(status_code=429, detail="Too many failed attempts. Please try again later.")
            else:
                user_2fa.fails = 0
            # End of if - 5 minutes since last failed attempt
        # End of if - too many failed attempts

        # Handle TOTP verification
        with core_security.totp_manager_dependency.get() as totp_m:
            if user_2fa.counter == int(metadata.code) or not totp_m.verify_totp(user_2fa.key_handle, metadata.code):
                user_2fa.fails += 1

                audit_logger.user_2fa_failed(
                    user_2fa.user_id, ip_address, m_audit.AuthMethods.TOTP, "Invalid TOTP code."
                )
                await db.commit()
                raise HTTPException(status_code=401, detail="Invalid 2FA code")
            else:
                user_2fa.fails = 0
                user_2fa.counter = int(metadata.code)
    else:
        # Check for too many failed attempts
        if user_2fa.fails >= 3:
            await auth_crud.delete_token(db, uuid.UUID(token_details.payload["jti"]))
            await auth_crud.delete_single_2fa(db, user_2fa.user_id, user_2fa.id)
            audit_logger.user_2fa_failed(
                user_2fa.user_id,
                ip_address,
                m_audit.AuthMethods.EMAIL,
                f"Too many failed attempts. 2FA method {user_2fa.id} deleted.",
            )
            await db.commit()
            raise HTTPException(status_code=429, detail="Too many failed attempts. Please try again later.")

        # Handle email code verification
        if not core_security.sha256_salt_verify(metadata.code, user_2fa.public_key):
            user_2fa.fails += 1
            await db.commit()
            raise HTTPException(status_code=401, detail="Invalid 2FA code")
        await db.delete(user_2fa)

    audit_logger.user_2fa_success(user_2fa.user_id, ip_address, m_audit.AuthMethods(user_2fa.method.value))

    # Create the access and refresh tokens
    await auth_crud.delete_token(db, uuid.UUID(token_details.payload["jti"]))
    access_token, refresh_token = await create_auth_tokens(
        ep_context, user_2fa.user_id, token_details.application_id, ip_address, log_creation=True
    )

    await db.commit()
    return access_token, refresh_token


async def refresh_token(
    ep_context: EndpointContext, token_details: core_security.TokenDetails, client_ip: str
) -> Tuple[str, str]:
    """Refresh the access token

    :param ep_context: The endpoint context
    :param access_jti: The access token JWT ID
    :param refresh_jti: The refresh token JWT ID
    :return: The new access and refresh tokens
    """
    db = ep_context.db

    # Get the user ID
    user_id = uuid.UUID(token_details.payload["sub"])

    # Delete the old tokens
    await auth_crud.delete_auth_tokens(db, user_id, token_details.payload["aud"])

    # Create the new tokens
    access_token, refresh_token = await create_auth_tokens(ep_context, user_id, token_details.application_id, client_ip)

    await db.commit()
    return access_token, refresh_token


async def logout(ep_context: EndpointContext, token_details: core_security.TokenDetails, client_ip: str):
    """Logout the user

    :param ep_context: The endpoint context
    :param application_id: The application ID
    :param refresh_token: The refresh token
    """
    db = ep_context.db
    audit_logger = ep_context.audit_logger

    # Get the user ID
    user_id = uuid.UUID(token_details.payload["sub"])

    # Delete the tokens
    await auth_crud.delete_auth_tokens(db, user_id, token_details.payload["aud"])
    audit_logger.user_logout(user_id, client_ip, token_details.payload["aud"])

    await db.commit()


async def forgot_password(ep_context: EndpointContext, ident: str, ip_address: str) -> None:
    """Send a password reset email to the user

    :param ep_context: The endpoint context
    :param email: The email address of the user
    :param ip_address: The IP address of the user
    :param application_id: The application ID
    """
    db = ep_context.db
    audit_logger = ep_context.audit_logger

    user = await user_crud.get_user_by_ident(db, ident)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.is_anonymized or user.is_system:
        raise HTTPException(status_code=404, detail="User not found")

    if not await audit_crud.forgot_password_allowed(db, user.id):
        raise HTTPException(status_code=429, detail="Too many password reset requests. Please try again later.")

    with core_security.email_verify_manager_dependency.get() as emv:
        url_params = emv.generate_verification_params(user.id, 300)
        # TODO send email
        if DEBUG:
            print(url_params)
    audit_logger.user_forgot_password(user.id, ip_address)
    await db.commit()


async def reset_password_init(
    ep_context: EndpointContext, user_id: str, expires: str, signature: str, application_id: str, ip_address: str
) -> str:
    """Reset the user's password

    :param ep_context: The endpoint context
    :param token_details: The token details
    :param new_password: The new password
    """
    db = ep_context.db
    audit_logger = ep_context.audit_logger

    # Verify the signature
    with core_security.email_verify_manager_dependency.get() as emv:
        if not emv.verify(user_id, expires, signature):
            audit_logger.user_reset_password_failed(uuid.UUID(user_id), application_id, "Invalid signature")
            raise HTTPException(status_code=401, detail="Invalid signature")

    audit_logger.user_reset_password_initiated(uuid.UUID(user_id))

    security_token = await create_security_token(
        ep_context, uuid.UUID(user_id), application_id, ["reset_password"], ip_address
    )
    await db.commit()
    return security_token


async def reset_password(
    ep_context: EndpointContext, token_details: core_security.TokenDetails, new_password: str
) -> None:
    """Reset the user's password

    :param ep_context: The endpoint context
    :param token_details: The token details
    :param new_password: The new password
    """
    db = ep_context.db
    audit_logger = ep_context.audit_logger

    # Get the user ID
    user_id = uuid.UUID(token_details.payload["sub"])

    # Update the user's password
    await user_crud.update_user_password(db, user_id, new_password)
    await auth_crud.delete_token(db, uuid.UUID(token_details.payload["jti"]))
    audit_logger.user_reset_password_successful(user_id, token_details.payload["aud"])
    await db.commit()
