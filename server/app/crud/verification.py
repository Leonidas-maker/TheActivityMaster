# crud/verification.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from sqlalchemy.sql.expression import and_, or_
import uuid
import datetime
from typing import List, Tuple
import traceback
from rich.console import Console

from models.m_verification import IdentityVerification, VerificationStatus
from schemas.s_verification import IdentityVerificationRequest

from config.settings import DEFAULT_TIMEZONE

import crud.audit as audit_crud


async def create_identity_verification(
    db: AsyncSession, user_id: uuid.UUID, verification_data: IdentityVerificationRequest, image_url: str
) -> IdentityVerification:
    new_verification = IdentityVerification(
        user_id=user_id,
        encrypted_id_card_mrz=verification_data.id_card_mrz,
        first_name=verification_data.first_name,
        last_name=verification_data.last_name,
        date_of_birth=verification_data.date_of_birth,
        image_url=image_url,
        status=VerificationStatus.PENDING,
        expires_at=datetime.datetime.now(DEFAULT_TIMEZONE) + datetime.timedelta(days=30),
    )
    db.add(new_verification)
    await db.flush()
    return new_verification


async def purge_sensitive_fields(
    db: AsyncSession, verification_id: uuid.UUID, approved: bool = False
) -> IdentityVerification:
    result = await db.execute(select(IdentityVerification).where(IdentityVerification.id == verification_id))
    verification = result.scalars().first()

    if verification:
        verification.first_name = ""
        verification.last_name = ""
        verification.date_of_birth = ""
        verification.image_url = ""
        verification.status = VerificationStatus.APPROVED if approved else VerificationStatus.REJECTED
        if approved:
            expire_date = datetime.datetime.now(DEFAULT_TIMEZONE) + datetime.timedelta(days=730)
        await db.flush()
    return verification


async def get_identity_verification_by_user(
    db: AsyncSession, user_id: uuid.UUID, only_active: bool = True
) -> IdentityVerification:
    """Get the latest identity verification for a user.

    :param db: The database session
    :param user_id: The user ID
    :param only_active: True to only get active verifications, False to get all verifications, defaults to True
    :return: The identity verification
    """
    if only_active:
        result = await db.execute(
            select(IdentityVerification)
            .where(
                and_(
                    IdentityVerification.user_id == user_id,
                    or_(
                        IdentityVerification.status == VerificationStatus.PENDING,
                        IdentityVerification.status == VerificationStatus.APPROVED,
                    ),
                    IdentityVerification.expires_at > datetime.datetime.now(DEFAULT_TIMEZONE),
                )
            )
            .order_by(IdentityVerification.created_at.desc())
        )
    else:
        result = await db.execute(
            select(IdentityVerification)
            .where(IdentityVerification.user_id == user_id)
            .order_by(IdentityVerification.created_at.desc())
        )
    return result.scalars().first()


async def get_identity_verification_by_id(db: AsyncSession, verification_id: uuid.UUID) -> IdentityVerification:
    result = await db.execute(select(IdentityVerification).where(IdentityVerification.id == verification_id))
    return result.scalars().first()


async def get_pending_identity_verifications(db: AsyncSession) -> List[Tuple[uuid.UUID, uuid.UUID]]:
    """Get all pending identity verifications. This is used by the admin panel to show all pending verifications.

    Note: This function only returns the ID and user ID of the pending verifications.

    :param db: The database session
    :return: The pending verifications
    """
    result = await db.execute(
        select(IdentityVerification.id, IdentityVerification.user_id).where(
            IdentityVerification.status == VerificationStatus.PENDING
        )
    )
    return [(row[0], row[1]) for row in result.all()]


async def get_identity_verification_details(db: AsyncSession, verification_id: uuid.UUID) -> IdentityVerification:
    """Get the details of an identity verification.

    :param db: The database session
    :param verification_id: The verification ID
    :return: The identity verification
    """
    result = await db.execute(select(IdentityVerification).where(IdentityVerification.id == verification_id))
    return result.scalars().first()


async def is_user_identity_verified(db: AsyncSession, user_id: uuid.UUID) -> bool:
    """Check if a user has an approved identity verification.

    :param db: The database session
    :param user_id: The user ID
    :return: True if the user has an approved identity verification, False otherwise
    """
    result = await db.execute(
        select(IdentityVerification)
        .where(
            and_(
                IdentityVerification.user_id == user_id,
                IdentityVerification.status == VerificationStatus.APPROVED,
                IdentityVerification.expires_at > datetime.datetime.now(DEFAULT_TIMEZONE),
            )
        )
    )
    return result.scalars().first() is not None


async def delete_identity_verification(db: AsyncSession, verification_id: uuid.UUID, soft_delete: bool = True):
    result = await db.execute(select(IdentityVerification).where(IdentityVerification.id == verification_id))
    verification = result.scalars().first()
    if verification:
        if soft_delete:
            verification.expires_at = datetime.datetime.now(DEFAULT_TIMEZONE)
            if verification.status == VerificationStatus.PENDING or verification.status == VerificationStatus.APPROVED:
                verification.status = VerificationStatus.REJECTED
        else:
            await db.delete(verification)
        await db.flush()


###########################################################################
############################## Recurring Task #############################
###########################################################################
async def delete_expired_identity_verifications(db: AsyncSession, console: Console, since_days: int = 14) -> bool:
    """Delete expired identity verifications.

    :param db: The database session
    :param since_days: The number of days since the verification expired, defaults to 14
    """
    audit_log = audit_crud.AuditLogger(db)

    try:
        audit_log.sys_info("delete_expired_identity_verifications", f"Deleting expired identity verifications since {since_days} days")
        result = await db.execute(
            delete(IdentityVerification).where(
                IdentityVerification.expires_at
                < datetime.datetime.now(DEFAULT_TIMEZONE) - datetime.timedelta(days=since_days)
            )
        )

        audit_log.id_verification_expired_deleted(since_days, result.rowcount)
        await db.commit()
        console.log(f"[blue][INFO][/blue]\t\tDeleted {result.rowcount} expired identity verifications.")

        return True
    except Exception as e:
        await db.rollback()
        audit_log.sys_error("delete_expired_identity_verifications", traceback=traceback.format_exc())
        await db.commit()
        console.log("[red][ERROR][/red]\t\tFailed to delete expired identity verifications.")
        console.print_exception()
        return False