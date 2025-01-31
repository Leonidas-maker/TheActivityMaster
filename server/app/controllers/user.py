from fastapi import HTTPException
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import joinedload, undefer
from typing import List, Tuple

import models.m_user as m_user

import schemas.s_user as s_user

import core.security as core_security

from crud.audit import AuditLogger
import crud.user as user_crud
import crud.auth as auth_crud
import crud.generic as generic_crud

from config.security import TOKEN_ISSUER
from config.settings import DEBUG

from core.generic import EndpointContext


async def register_user(ep_context: EndpointContext, user: s_user.UserCreate) -> uuid.UUID:
    """
    Register a new user

    :param ep_context: The endpoint context
    :param username: The username of the new user
    :param password: The password of the new user
    :return: The user ID of the new user
    """
    db = ep_context.db
    audit_logger = ep_context.audit_logger

    # Check if the user already exists
    user_db = await user_crud.get_user_by_ident(db, user.email)
    if user_db:
        raise HTTPException(status_code=400, detail="User already exists")

    # Add audit logs
    audit_logger.sys_info("Registering a new user")

    # Hash the password
    user.password = core_security.hash_password(user.password)

    # Create the user
    user_db = await user_crud.create_user(db, user)
    user_id = user_db.id

    # Add audit logs
    audit_logger.sys_info("User registered", details=f"User ID: {user_id}")
    await db.commit()

    with core_security.email_verify_manager_dependency.get() as evm:
        url_params = evm.generate_verification_params(user_id)
        #TODO: Send email
        if DEBUG:
            print(url_params)

    return user_id

async def verify_email(ep_context: EndpointContext, user_id: str, expire: str, signature: str) -> None:
    """
    Verify the email of a user

    :param ep_context: The endpoint context
    :param code: The verification code
    """
    db = ep_context.db

    with core_security.email_verify_manager_dependency.get() as evm:
        if not evm.verify(user_id, expire, signature):
            raise HTTPException(status_code=400, detail="Invalid email verification code")
       
    # Get the user
    user = await user_crud.get_user_by_id(db, uuid.UUID(user_id))

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Verify the email
    for role in user.generic_roles:
        if role.name == "NotEmailVerified":
            user.generic_roles.remove(role)
            await db.commit()
            break

async def user_delete(
    ep_context: EndpointContext, token_details: core_security.TokenDetails, user_delete: s_user.UserDelete
) -> None:
    """
    Delete a user

    :param ep_context: The endpoint context
    :param token_details: The token details
    :param user_delete: The user deletion information
    """
    db = ep_context.db
    audit_logger = ep_context.audit_logger

    # Get the user ID
    user_id = uuid.UUID(token_details.payload["sub"])

    # Get the user
    user = await user_crud.get_user_by_id(db, user_id)

    # Check if the password is correct
    if not core_security.verify_password(user_delete.password, user.password):
        audit_logger.user_self_deletion_failed(user_id, token_details.payload["aud"], "Invalid password")
        await db.commit()
        raise HTTPException(status_code=400, detail="Invalid password")

    # Delete the user
    await user_crud.delete_user(ep_context, user_id, token_details.payload["aud"])

    # Add audit logs
    audit_logger.user_self_deletion_successful(user_id, token_details.payload["aud"])
    await db.commit()


async def user_information(db: AsyncSession, user_id: uuid.UUID) -> m_user.User:
    """
    Get user information

    :param db: The database session
    :param user_id: The ID of the user
    :return: The user information
    """
    query_params = [joinedload(m_user.User.generic_roles), joinedload(m_user.User.address)]
    res = await db.execute(select(m_user.User).filter(m_user.User.id == user_id).options(*query_params))
    user = res.unique().scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


###########################################################################
############################ Security Settings ############################
###########################################################################


async def totp_register_init(ep_context: EndpointContext, token_details: core_security.TokenDetails) -> Tuple[str, str]:
    """
    Register a TOTP device

    :param ep_context: EndpointContext: The endpoint context
    :param token_details: TokenDetails: Token details
    :param client_ip: str: The client IP address
    :return: The TOTP URI and backup codes if not already generated
    """
    db = ep_context.db
    audit_logger = ep_context.audit_logger

    user = await user_crud.get_user_by_id(db, uuid.UUID(token_details.payload["sub"]))

    with core_security.totp_manager_dependency.get() as totp_m:
        secret, encrypted_secret = totp_m.generate_totp_secret()
        uri = totp_m.get_totp_uri(secret, user.email, TOKEN_ISSUER)

    # Save the TOTP secret
    await user_crud.save_totp_secret(db, user.id, encrypted_secret)

    # Add audit logs
    audit_logger.totp_register_init(user.id, token_details.payload["aud"])

    await db.commit()
    return secret, uri


async def totp_register(
    ep_context: EndpointContext, token_details: core_security.TokenDetails, _2fa_code: str
) -> List[str]:
    """
    Verify a TOTP token

    :param ep_context: EndpointContext: The endpoint context
    :param token: str: The TOTP token
    :param user_id: UUID: The ID of the user
    :return: True if the token is valid, False otherwise
    """
    db = ep_context.db
    audit_logger = ep_context.audit_logger

    # Get the user ID and application ID
    user_id = uuid.UUID(token_details.payload["sub"])
    application_id = token_details.payload["aud"]

    # Get the TOTP secret
    totp_db = await auth_crud.get_2fa_totp(db, user_id)

    # Verify the TOTP code
    with core_security.totp_manager_dependency.get() as totp_m:
        if not totp_m.verify_totp(totp_db.key_handle, _2fa_code):
            audit_logger.totp_register_failed(user_id, application_id, "Invalid TOTP code")
            await db.delete(totp_db)
            await db.commit()
            raise HTTPException(status_code=400, detail="Invalid TOTP code. Please retry the registration process.")
        totp_db.counter = int(_2fa_code)

    # Enable TOTP for the user
    totp_db.fails = 0

    # Generate backup codes if not already generated
    user = await user_crud.get_user_by_id(db, user_id, [undefer(m_user.User.backup_codes_2fa)])
    backup_codes = []
    if not user.backup_codes_2fa:
        audit_logger.backup_codes_generated(user.id)
        backup_codes = core_security.generate_backup_codes()
        user.backup_codes_2fa = ",".join(core_security.bycrypt_hash(code) for code in backup_codes)

    # Add audit logs
    audit_logger.totp_registered(user_id, application_id)
    await db.commit()
    return backup_codes


async def totp_remove(
    ep_context: EndpointContext, token_details: core_security.TokenDetails, remove_totp: s_user.RemoveTOTP
) -> None:
    """
    Remove TOTP from a user

    :param ep_context: The endpoint context
    :param token_details: The token details
    :param remove_totp: The TOTP removal information
    """
    db = ep_context.db
    audit_logger = ep_context.audit_logger

    # Get the user ID
    user_id = uuid.UUID(token_details.payload["sub"])

    # Verify the password
    user = await user_crud.get_user_by_id(db, user_id)

    if not core_security.verify_password(remove_totp.password, user.password):
        audit_logger.totp_removal_failed(user_id, token_details.payload["aud"], "Invalid password")
        await db.commit()
        raise HTTPException(status_code=400, detail="Invalid password")

    # Get the TOTP secret
    totp_db = await auth_crud.get_2fa_totp(db, user_id)

    # Verify the TOTP code
    with core_security.totp_manager_dependency.get() as totp_m:
        if not totp_m.verify_totp(totp_db.key_handle, remove_totp.code):
            audit_logger.totp_removal_failed(user_id, token_details.payload["aud"], "Invalid TOTP code")
            await db.commit()
            raise HTTPException(status_code=400, detail="Invalid TOTP code")

    # Remove the TOTP secret
    await db.delete(totp_db)

    # Add audit logs
    audit_logger.totp_removal(user_id, token_details.payload["aud"])
    await db.commit()


async def change_password(
    ep_context: EndpointContext, token_details: core_security.TokenDetails, password_change: s_user.ChangePassword
) -> None:
    """
    Change the password of a user

    :param ep_context: The endpoint context
    :param token_details: The token details
    :param password_change: The new password
    """
    db = ep_context.db
    audit_logger = ep_context.audit_logger

    # Get the user ID
    user_id = uuid.UUID(token_details.payload["sub"])

    # Get the user
    user = await user_crud.get_user_by_id(db, user_id)

    # Check if the old password is correct
    if not core_security.verify_password(password_change.old_password, user.password):
        raise HTTPException(status_code=400, detail="Invalid old password")

    # Hash the new password
    user.password = core_security.hash_password(password_change.new_password)

    # Add audit logs
    audit_logger.user_password_change(user_id, token_details.payload["aud"])
    await db.commit()


async def update_user_address(
    ep_context: EndpointContext, token_details: core_security.TokenDetails, address: s_user.Address
) -> None:
    """
    Change the address of a user

    :param ep_context: The endpoint context
    :param token_details: The token details
    :param address: The new address
    """
    db = ep_context.db
    audit_logger = ep_context.audit_logger

    # Get the user ID
    user_id = uuid.UUID(token_details.payload["sub"])

    # Get the user
    user = await user_crud.get_user_by_id(db, user_id)

    # Get or create the address
    address = await generic_crud.get_create_address(db, address)

    # Update the address
    user.address = address

    # Add audit logs
    audit_logger.user_address_change(user_id, token_details.payload["aud"])
    await db.commit()
