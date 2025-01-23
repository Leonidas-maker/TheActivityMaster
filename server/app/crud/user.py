import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.sql.expression import or_
import datetime
import traceback

import models.m_user as m_user
import models.m_club as m_club

from schemas.s_user import UserCreate

from crud.audit import AuditLogger
from crud.generic import get_create_address

async def create_user(db: AsyncSession, user: UserCreate) -> m_user.User:
    """
    Create a new user

    :param db: AsyncSession: Database session
    :param user: UserCreate: User data to create
    :return: User: The created user
    """
    user_db = m_user.User(
        id=uuid.uuid4(),
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        password=user.password,
    )

    if user.address:
        user_db.address = await get_create_address(db, user.address)

    db.add(user_db)
    
    # await db.flush()
    return user_db

async def get_user_by_email(db: AsyncSession, email: str) -> m_user.User:
    """
    Get a user by their email address

    :param db: AsyncSession: Database session
    :param email: str: Email address to search for
    :return: User: The user
    """
    res = await db.execute(select(m_user.User).filter(m_user.User.email == email))
    return res.scalar_one_or_none()


async def delete_user(db: AsyncSession, user_id: uuid.UUID) -> None:
    """
    Soft delete a user by setting their email to a placeholder and anonymizing their name and password
    This is a soft delete operation is needed to be compliant with GDPR and other regulations

    Note: This function will commit the transaction if successful

    :param db: AsyncSession: Database session
    :param user_id: UUID: ID of the user to delete

    :raises ValueError: If the user is not found
    """
    res = await db.execute(select(m_user.User).filter(m_user.User.id == user_id))
    user = res.scalar_one_or_none()
    if not user:
        raise ValueError("User not found")
    
    audit_logger = AuditLogger(db)
    try:
        # Add audit logs
        init_audit_log = audit_logger.user_self_deletion_initiated(user.id)
        await db.commit()

        # Delete tokens, passkeys, 2FA, tokens and roles
        await db.execute(delete(m_user.UserToken).where(m_user.UserToken.user_id == user.id))
        await db.execute(delete(m_user.UserPasskey).where(m_user.UserPasskey.user_id == user.id))
        await db.execute(delete(m_user.User2FA).where(m_user.User2FA.user_id == user.id))
        await db.execute(delete(m_user.UserRole).where(m_user.UserRole.user_id == user.id))
        await db.execute(delete(m_user.UserClubRole).where(m_user.UserClubRole.user_id == user.id))

        # Cancel all membership subscriptions
        res = await db.execute(
            update(m_club.MembershipSubscription)
            .where(m_club.MembershipSubscription.user_id == user.id, or_(
                m_club.MembershipSubscription.end_time == None,  
                m_club.MembershipSubscription.end_time > datetime.datetime.now()
            ))
            .values(end_time=datetime.datetime.now())
        )

        audit_logger.user_self_deletion_cancelled_memberships(init_audit_log.id, user_id=user.id, count=res.rowcount)

        # Anonymize user data
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
        await db.commit()
    except Exception as e:
        await db.rollback()
        audit_logger.sys_error(
            f"Error deleting user {user.id}",
            traceback=traceback.format_exc(),
            correlation_id=user.id,
        )
        await db.commit()

