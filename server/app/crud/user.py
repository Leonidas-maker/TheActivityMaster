import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, exists
from sqlalchemy.sql.expression import or_
from sqlalchemy.orm import joinedload, undefer
import datetime
import traceback
from typing import Optional, List, Tuple, Dict

from models import m_user, m_club, m_verification

from schemas.s_user import UserCreate

from crud.audit import AuditLogger
from crud.generic import get_create_address

from core.generic import EndpointContext
import core.security as core_security

from config.club import ClubPermissions


async def create_user(db: AsyncSession, user: UserCreate) -> m_user.User:
    """
    Create a new user

    :param db: AsyncSession: Database session
    :param user: UserCreate: User data to create
    :return: User: The created user
    """
    user_db = m_user.User(
        id=uuid.uuid4(),
        username=user.username,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        password=user.password,
    )

    if user.address:
        user_db.address = await get_create_address(db, user.address)

    res = await db.execute(select(m_user.GenericRole).where(m_user.GenericRole.name == "NotEmailVerified"))
    role = res.unique().scalar_one()
    user_db.generic_roles.append(role)

    db.add(user_db)
    await db.flush()
    return user_db


async def get_user_by_ident(db: AsyncSession, ident: str) -> m_user.User:
    """
    Get a user by their email address

    :param db: AsyncSession: Database session
    :param email: str: Email address to search for
    :return: User: The user
    """
    res = await db.execute(select(m_user.User).filter(or_(m_user.User.email == ident, m_user.User.username == ident)))
    return res.unique().scalar_one_or_none()


async def get_user_by_id(
    db: AsyncSession, user_id: uuid.UUID, query_options: list = [], only_real_users: bool = True
) -> m_user.User:
    """
    Get a user by their ID

    :param db: AsyncSession: Database session
    :param user_id: UUID: ID of the user to search for
    :return: User: The user
    """
    res = await db.execute(select(m_user.User).filter(m_user.User.id == user_id).options(*query_options))
    user = res.unique().scalar_one_or_none()
    if not user:
        raise ValueError("User not found")
    if only_real_users and (user.is_anonymized or user.is_system):
        raise ValueError("User is not a real user")
    return user


async def get_user_details_by_id(db: AsyncSession, user_id: uuid.UUID) -> m_user.User:
    """
    Get a user by their ID

    :param db: AsyncSession: Database session
    :param user_id: UUID: ID of the user to search for
    :return: User: The user
    """
    query_options = [
        joinedload(m_user.User.address),
        joinedload(m_user.User.identity_verifications),
        joinedload(m_user.User._2fa),
    ]
    res = await db.execute(select(m_user.User).filter(m_user.User.id == user_id).options(*query_options))
    return res.unique().scalar_one_or_none()


###########################################################################
################################## Roles ##################################
###########################################################################
async def get_generic_role_by_name(db: AsyncSession, role_name: str) -> m_user.GenericRole:
    """
    Get a generic role by its name

    :param db: AsyncSession: Database session
    :param role_name: str: Name of the role to search for
    :return: GenericRole: The role
    """
    res = await db.execute(select(m_user.GenericRole).filter(m_user.GenericRole.name == role_name))
    return res.unique().scalar_one_or_none()


async def get_user_generic_roles(
    db: AsyncSession, user_id: uuid.UUID, query_options: list = []
) -> List[m_user.GenericRole]:
    """
    Get the generic roles for a user

    :param db: AsyncSession: Database session
    :param user_id: UUID: ID of the user to search for
    :return: list[GenericRole]: The generic roles
    """
    res = await db.execute(
        select(m_user.GenericRole)
        .join(m_user.UserRole)
        .filter(m_user.UserRole.user_id == user_id)
        .options(*query_options)
    )
    return list(res.scalars().all())


async def get_user_club_roles(
    db: AsyncSession, user_id: uuid.UUID, club_id: uuid.UUID, query_options: list = []
) -> List[m_user.ClubRole]:
    """
    Get the club roles for a user

    :param db: AsyncSession: Database session
    :param user_id: UUID: ID of the user to search for
    :return: list[ClubRole]: The club roles
    """
    res = await db.execute(
        select(m_user.ClubRole)
        .join(m_user.UserClubRole)
        .filter(m_user.ClubRole.user_id == user_id, m_user.ClubRole.club_id == club_id)
        .options(*query_options)
    )
    return list(res.scalars().all())


async def get_user_roles(
    db: AsyncSession, user_id: uuid.UUID
) -> Tuple[List[m_user.GenericRole], Dict[uuid.UUID, m_user.ClubRole]]:
    """
    Get the roles for a user with each description.

    :param db: AsyncSession: Database session
    :param user_id: UUID: ID of the user to search for
    :return: tuple: (generic_roles, club_roles)
    """
    query_options = [
        joinedload(m_user.User.generic_roles).options(undefer(m_user.GenericRole.description)),
        joinedload(m_user.User.club_roles)
        .joinedload(m_club.UserClubRole.club_role)
        .options(undefer(m_club.ClubRole.description)),
    ]

    res = await db.execute(select(m_user.User).filter(m_user.User.id == user_id).options(*query_options))
    user = res.unique().scalar_one_or_none()
    if not user:
        raise ValueError("User not found")

    return user.generic_roles, user.clubs_with_roles


async def is_user_elevated(db: AsyncSession, user_id: uuid.UUID) -> bool:
    """
    Check if a user has elevated permissions

    :param db: AsyncSession: Database session
    :param user_id: UUID: ID of the user to search for
    :return: bool: If the user has elevated permissions
    """
    res = await db.execute(
        select(m_user.GenericRole)
        .join(m_user.UserRole)
        .filter(m_user.UserRole.user_id == user_id, m_user.GenericRole.name == "Admin")
    )
    return res.scalar_one_or_none() is not None


async def has_user_club_permission(
    db: AsyncSession, user_id: uuid.UUID, club_id: uuid.UUID, permission: ClubPermissions
) -> bool:
    res = await db.execute(
        select(
            exists(
                select(1)
                .select_from(m_club.UserClubRole)
                .join(m_club.UserClubRole.club_role)
                .join(m_club.ClubRole.permissions)
                .filter(
                    m_club.UserClubRole.user_id == user_id,
                    m_club.UserClubRole.club_id == club_id,
                    m_club.Permission.name == permission.value,
                )
            )
        )
    )
    return res.scalar_one_or_none() is not None


###########################################################################
################################## Delete #################################
###########################################################################
async def delete_user(ep_context: EndpointContext, user_id: uuid.UUID, application_id_hash: str) -> None:
    """
    Soft delete a user by setting their email to a placeholder and anonymizing their name and password
    This is a soft delete operation is needed to be compliant with GDPR and other regulations

    Note: This function will commit the transaction if successful

    :param db: AsyncSession: Database session
    :param user_id: UUID: ID of the user to delete

    :raises ValueError: If the user is not found
    """
    db = ep_context.db
    audit_logger = ep_context.audit_logger

    res = await db.execute(select(m_user.User).filter(m_user.User.id == user_id))
    user = res.unique().scalar_one_or_none()
    if not user:
        raise ValueError("User not found")

    try:
        # Add audit logs
        init_audit_log = audit_logger.user_self_deletion_initiated(user.id, application_id_hash)

        # Delete tokens, passkeys, 2FA, tokens and roles
        await db.execute(delete(m_user.UserToken).where(m_user.UserToken.user_id == user.id))
        await db.execute(delete(m_user.UserPasskey).where(m_user.UserPasskey.user_id == user.id))
        await db.execute(delete(m_user.User2FA).where(m_user.User2FA.user_id == user.id))
        await db.execute(delete(m_user.UserRole).where(m_user.UserRole.user_id == user.id))
        await db.execute(delete(m_user.UserClubRole).where(m_user.UserClubRole.user_id == user.id))

        # Cancel all membership subscriptions
        res = await db.execute(
            update(m_club.MembershipSubscription)
            .where(
                m_club.MembershipSubscription.user_id == user.id,
                or_(
                    m_club.MembershipSubscription.end_time == None,
                    m_club.MembershipSubscription.end_time > datetime.datetime.now(),
                ),
            )
            .values(end_time=datetime.datetime.now())
        )

        audit_logger.user_self_deletion_cancelled_memberships(init_audit_log.id, user_id=user.id, count=res.rowcount)

        # Anonymize user data
        user.username = f"deleted_user_{user.id}"
        user.email = f"deleted_user_{user.id}@example.com"
        user.first_name = "Anonymized"
        user.last_name = "User"
        user.password = "REMOVED"
        user.is_2fa_enabled = False
        user.is_passkey_enabled = False
        user.is_anonymized = True

        # Add audit logs
        audit_logger.user_self_deletion_anonymized(init_audit_log.id, user_id=user.id)
        audit_logger.user_self_deletion_completed(init_audit_log.id, user_id=user.id)
        await db.flush()
    except Exception as e:
        await db.rollback()
        audit_logger.sys_error(
            f"Error deleting user {user.id}",
            traceback=traceback.format_exc(),
            correlation_id=user.id,
        )
        await db.commit()


###########################################################################
############################ Security Settings ############################
###########################################################################
async def save_totp_secret(
    db: AsyncSession, user_id: uuid.UUID, encrypted_secret: str, device_name: Optional[str] = None
) -> m_user.User2FA:
    """
    Save the TOTP secret for a user

    :param db: AsyncSession: Database session
    :param user_id: UUID: ID of the user
    :param secret: str: The secret to save
    """
    totp_2fa = m_user.User2FA(
        user_id=user_id, key_handle=encrypted_secret, method=m_user.User2FAMethods.TOTP, device_name=device_name
    )
    db.add(totp_2fa)
    await db.flush()
    return totp_2fa


async def update_user_password(db: AsyncSession, user_id: uuid.UUID, new_password: str) -> None:
    """
    Update a user's password

    :param db: AsyncSession: Database session
    :param user_id: UUID: ID of the user to update
    :param password: str: The new password
    """
    res = await db.execute(select(m_user.User).filter(m_user.User.id == user_id))
    user = res.unique().scalar_one_or_none()
    if not user:
        raise ValueError("User not found")

    user.password = core_security.hash_password(new_password)
    await db.flush()
