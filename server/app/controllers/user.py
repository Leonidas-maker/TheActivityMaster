from fastapi import HTTPException
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import joinedload, undefer
from typing import List, Tuple
import datetime

import models.m_user as m_user

from schemas import s_user, s_role

import core.security as core_security

from crud.audit import AuditLogger
from crud import (
    user as user_crud,
    auth as auth_crud,
    generic as generic_crud,
    verification as verification_crud,
    role as role_crud,
)


from config.security import TOKEN_ISSUER
from config.settings import DEBUG, DEFAULT_TIMEZONE, ENVIRONMENT

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
        # TODO: Send email
        if DEBUG:
            print(url_params)

    return user_id


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
    user_id = token_details.user_id

    # Get the user
    user = await user_crud.get_user_by_id(db, user_id)

    # Check if the password is correct
    if not core_security.verify_password(user_delete.password, user.password):
        audit_logger.user_self_deletion_failed(user_id, token_details.payload["aud"], "Invalid password")
        await db.commit()
        raise HTTPException(status_code=400, detail="Invalid password")

    # Delete the user
    await user_crud.delete_user(ep_context, user_id, token_details.payload["aud"])

    # Delete the user's identity verification
    verification = await verification_crud.get_identity_verification_by_id(db, user_id)
    if verification:
        await verification_crud.delete_identity_verification(db, verification.id)
        audit_logger.id_verification_rejected(user_id, user_id, "User self-deletion")
        audit_logger.id_verification_soft_deleted(user_id, user_id)

    # Add audit logs
    audit_logger.user_self_deletion_successful(user_id, token_details.payload["aud"])
    await db.commit()


async def get_user_roles(ep_context: EndpointContext, token_details: core_security.TokenDetails) -> s_role.Roles:
    """
    Get the roles of a user

    :param ep_context: The endpoint context
    :param token_details: The token details
    :return: The generic and club roles of the user
    """
    db = ep_context.db
    user_id = token_details.user_id

    # Get the user with roles
    user = await role_crud.get_user_with_roles(db, user_id)

    return s_role.Roles(
        generic_roles=[s_role.GenericRole.model_validate(role) for role in user.generic_roles],
        club_roles={
            club_id: s_role.ClubRole.model_validate(club_role) for club_id, club_role in user.clubs_with_roles.items()
        },
    )


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

    user = await user_crud.get_user_by_id(db, token_details.user_id)

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
    user_id = token_details.user_id

    # Get the hashed application ID
    application_id_hash = token_details.payload["aud"]

    # Get the TOTP secret
    totp_db = await auth_crud.get_2fa_totp(db, user_id)

    # Verify the TOTP code
    with core_security.totp_manager_dependency.get() as totp_m:
        if not totp_m.verify_totp(totp_db.key_handle, _2fa_code):
            audit_logger.totp_register_failed(user_id, application_id_hash, "Invalid TOTP code")
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
    audit_logger.totp_registered(user_id, application_id_hash)
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
    user_id = token_details.user_id

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


###########################################################################
################################# Changes #################################
###########################################################################
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
    user_id = token_details.user_id

    # Get the user
    user = await user_crud.get_user_by_id(db, user_id)

    if not DEBUG and user.updated_at.replace(tzinfo=DEFAULT_TIMEZONE) + datetime.timedelta(
        minutes=30
    ) > datetime.datetime.now(DEFAULT_TIMEZONE):
        raise HTTPException(status_code=400, detail="Please try again later")

    # Check if the old password is correct
    if not core_security.verify_password(password_change.old_password, user.password):
        raise HTTPException(status_code=400, detail="Invalid old password")

    # Hash the new password
    user.password = core_security.hash_password(password_change.new_password)

    # TODO Send Email to inform user of password change

    # Add audit logs
    audit_logger.user_password_change(user_id, token_details.payload["aud"])
    await db.commit()


async def update_user_email(
    ep_context: EndpointContext, token_details: core_security.TokenDetails, email: str, password: str
) -> None:
    """
    Change the email of a user

    :param ep_context: The endpoint context
    :param token_details: The token details
    :param email: The new email
    """
    db = ep_context.db
    audit_logger = ep_context.audit_logger
    user_id = token_details.user_id

    # Get the user
    user = await user_crud.get_user_by_id(db, user_id, query_options=[joinedload(m_user.User.generic_roles)])

    # Check if the password is correct
    if not core_security.verify_password(password, user.password):
        raise HTTPException(status_code=400, detail="Invalid password")

    # Delay to prevent email enumeration
    if not DEBUG and user.updated_at.replace(tzinfo=DEFAULT_TIMEZONE) + datetime.timedelta(
        minutes=30
    ) > datetime.datetime.now(DEFAULT_TIMEZONE):
        raise HTTPException(status_code=400, detail="Please try again later")

    # Check if the email is already in use
    if await user_crud.get_user_by_ident(db, email):
        raise HTTPException(status_code=400, detail="Email already in use")

    # Update the email
    old_email_hash = core_security.sha256_salt(user.email)
    user.email = email

    if not any([role.name == "NotEmailVerified" for role in user.generic_roles]):
        user.generic_roles.append(await role_crud.get_generic_role_by_name(db, "NotEmailVerified"))

    # TODO Send Email to old email and verify new email
    with core_security.email_verify_manager_dependency.get() as evm:
        url_params = evm.generate_verification_params(user_id)
        if DEBUG:
            print(url_params)

    # Add audit logs
    audit_logger.user_email_change(user_id, token_details.payload["aud"], old_email_hash)
    await db.commit()


async def update_user_username(
    ep_context: EndpointContext, token_details: core_security.TokenDetails, username: str, password: str
) -> None:
    """
    Change the username of a user

    :param ep_context: The endpoint context
    :param token_details: The token details
    :param username: The new username
    """
    db = ep_context.db
    audit_logger = ep_context.audit_logger
    user_id = token_details.user_id

    # Get the user
    user = await user_crud.get_user_by_id(db, user_id)

    # Check if the password is correct
    if not core_security.verify_password(password, user.password):
        raise HTTPException(status_code=400, detail="Invalid password")

    # Delay to prevent username enumeration
    if not DEBUG and user.updated_at.replace(tzinfo=DEFAULT_TIMEZONE) + datetime.timedelta(
        minutes=30
    ) > datetime.datetime.now(DEFAULT_TIMEZONE):
        raise HTTPException(status_code=400, detail="Please try again later")

    # Check if the username is already in use
    if await user_crud.get_user_by_ident(db, username):
        raise HTTPException(status_code=400, detail="Username already in use")

    # Update the username
    user.username = username

    # TODO Send Email to inform user of username change

    # Add audit logs
    audit_logger.user_username_change(user_id, token_details.payload["aud"])
    await db.commit()


async def update_user_basic(
    ep_context: EndpointContext, token_details: core_security.TokenDetails, user_update: s_user.UserUpdate
) -> None:
    """
    Change the address of a user

    :param ep_context: The endpoint context
    :param token_details: The token details
    :param address: The new address
    """
    db = ep_context.db
    audit_logger = ep_context.audit_logger
    user_id = token_details.user_id
    audit_details = ""

    # Get the user
    user = await user_crud.get_user_by_id(db, user_id)

    if (user_update.first_name or user_update.last_name) and await verification_crud.is_user_identity_verified(
        db, user_id
    ):
        raise HTTPException(status_code=400, detail="Cannot change name after identity verification")

    if user_update.first_name:
        user.first_name = user_update.first_name
        audit_details += "First name updated"

    if user_update.last_name:
        user.last_name = user_update.last_name
        audit_details += "; Last name updated"

    if user_update.address:
        # Get or create the address and update the user
        user.address = await generic_crud.get_create_address(db, user_update.address)
        audit_details += "; Address updated"

    # Add audit logs
    audit_logger.user_profile_update(user_id, token_details.payload["aud"], audit_details)

    await db.commit()
