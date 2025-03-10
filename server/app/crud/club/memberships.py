from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, or_, exists, and_, ColumnElement
from sqlalchemy.inspection import inspect
from sqlalchemy.orm import undefer, joinedload
from typing import List, Tuple, Optional, Dict, Literal
import stripe
import uuid
import datetime
import traceback
from rich.console import Console

from schemas import s_club, s_email

from models import m_club, m_user, m_payment

from crud import audit as audit_crud, generic as generic_crud, transactions as transactions_crud, club as club_crud

from core import transactions as transactions_core, email as email_core

from config.permissions import ClubPermissions  #

from .program_offerings import active_sessions_db_condition, program_exists


###########################################################################
################################# Helpers #################################
###########################################################################
def membership_duration_to_timedelta(duration: int, duration_unit: m_club.DurationUnit) -> datetime.timedelta:
    """
    Convert a membership duration to a timedelta.

    :param duration: The duration of the membership
    :param duration_unit: The unit of the duration
    :return: The duration as a timedelta
    """
    if duration_unit == m_club.DurationUnit.DAY:
        return datetime.timedelta(days=duration)
    elif duration_unit == m_club.DurationUnit.MONTH:
        return datetime.timedelta(days=duration * 30)
    else:
        raise ValueError("Invalid duration unit")


def membership_duration_to_stripe_duration(
    duration: int, duration_unit: m_club.DurationUnit
) -> Literal["day", "month", "week", "year"]:
    """
    Convert a membership duration to a timedelta.

    :param duration: The duration of the membership
    :param duration_unit: The unit of the duration
    :return: The duration as a timedelta
    """
    if duration_unit == m_club.DurationUnit.DAY:
        return "day"
    elif duration_unit == m_club.DurationUnit.MONTH:
        return "month"
    else:
        raise ValueError("Invalid duration unit")


###########################################################################
################################ Membership ###############################
###########################################################################
async def create_membership(
    db: AsyncSession, club_id: uuid.UUID, new_membership: s_club.MembershipCreate
) -> m_club.Membership:
    """
    Create a new membership.

    :param db: The database session
    :param new_membership: The details of the new membership
    :return: The created membership
    """
    club = await club_crud.get_club(db, club_id)

    stripe_product, stripe_price = transactions_core.create_membership(
        club.stripe_account_id, # type: ignore
        new_membership.name,
        new_membership.description,
        new_membership.price,
        new_membership.currency,
        membership_duration_to_stripe_duration(new_membership.duration, new_membership.duration_unit),
        new_membership.duration,
    )

    membership = m_club.Membership(
        name=new_membership.name,
        description=new_membership.description,
        club_id=club_id,
        stripe_product_id=stripe_product.id,
        stripe_price_id=stripe_price.id,
        status=new_membership.status.to_internal(),
        price=new_membership.price,
        currency=new_membership.currency,
        duration=new_membership.duration,
        duration_unit=new_membership.duration_unit,
    )
    db.add(membership)
    await db.flush()
    return membership


async def get_club_memberships(
    db: AsyncSession, club_id: uuid.UUID, only_bookable: bool = True
) -> List[m_club.Membership]:
    """
    Retrieve the memberships associated with a specific club.

    :param db: The database session
    :param club_id: The ID of the club whose memberships are to be retrieved
    :param only_bookable: Whether to only retrieve bookable memberships
    :return: A list of memberships for the club
    """
    conditions = [m_club.Membership.club_id == club_id]
    if only_bookable:
        conditions.append(m_club.Membership.status == m_club.MembershipStatus.BOOKABLE)
    else:
        conditions.append(m_club.Membership.status != m_club.MembershipStatus.DELETED)

    memberships = await db.execute(
        select(m_club.Membership).options(undefer(m_club.Membership.description)).filter(and_(*conditions))
    )
    return list(memberships.unique().scalars().all())


async def get_membership_by_id(
    db: AsyncSession, club_id: uuid.UUID, membership_id: uuid.UUID, with_details: bool = False, query_options: list = []
) -> Optional[m_club.Membership]:
    """
    Retrieve a membership by its ID.

    :param db: The database session
    :param membership_id: The ID of the membership to retrieve
    :return: The membership, if found
    """
    query_options.extend([undefer(m_club.Membership.description), joinedload(m_club.Membership.programs_access)])
    if with_details:
        query_options.append(joinedload(m_club.Membership.programs_access).joinedload(m_club.MembershipAccess.program))

    membership = await db.execute(
        select(m_club.Membership)
        .options(*query_options)
        .filter(m_club.Membership.id == membership_id, m_club.Membership.club_id == club_id)
    )
    return membership.unique().scalar_one_or_none()


async def get_user_viewable_membership_by_id(
    db: AsyncSession, club_id: uuid.UUID, membership_id: uuid.UUID, user_id: Optional[uuid.UUID]
) -> Optional[m_club.Membership]:
    """
    Retrieve a membership by its ID and user ID.

    Note: Also memberships access is loaded for the user.

    :param db: The database session
    :param membership_id: The ID of the membership to retrieve
    :param user_id: The ID of the user
    :return: The membership, if found
    """
    query_options = [undefer(m_club.Membership.description), joinedload(m_club.Membership.programs_access)]
    if user_id is None:
        res = await db.execute(
            select(m_club.Membership)
            .options(*query_options)
            .filter(
                m_club.Membership.id == membership_id,
                m_club.Membership.club_id == club_id,
                m_club.Membership.status == m_club.MembershipStatus.BOOKABLE,
            )
        )

    else:
        permission_exists = exists(
            select(1)
            .select_from(m_club.UserClubRole)
            .join(m_club.ClubRole, m_club.UserClubRole.club_role_id == m_club.ClubRole.id)
            .join(m_club.ClubRolePermission, m_club.ClubRole.id == m_club.ClubRolePermission.role_id)
            .join(m_club.Permission, m_club.ClubRolePermission.permission_id == m_club.Permission.id)
            .filter(
                m_club.UserClubRole.user_id == user_id,
                m_club.ClubRole.club_id == club_id,
                m_club.Permission.name == ClubPermissions.READ_MEMBERSHIPS.value,
            )
        )

        subscription_exists = exists(
            select(1)
            .select_from(m_payment.MembershipSubscription)
            .filter(
                m_payment.MembershipSubscription.user_id == user_id,
                m_payment.MembershipSubscription.membership_id == m_club.Membership.id,
            )
        )

        res = await db.execute(
            select(m_club.Membership)
            .options(*query_options)
            .filter(
                m_club.Membership.id == membership_id,
                m_club.Membership.club_id == club_id,
                or_(
                    m_club.Membership.status == m_club.MembershipStatus.BOOKABLE,
                    permission_exists,
                    subscription_exists,
                ),
            )
        )

    return res.unique().scalar_one_or_none()


async def membership_exists(
    db: AsyncSession,
    club_id: uuid.UUID,
    membership_name: Optional[str] = None,
    membership_id: Optional[uuid.UUID] = None,
    only_active: bool = True,
) -> bool:
    """
    Check if a membership with the given name exists for a club.

    :param db: The database session
    :param club_id: The ID of the club
    :param membership_name: The name of the membership
    :return: Whether a membership with the given name exists
    """
    conditions = [m_club.Membership.club_id == club_id]
    if membership_name:
        conditions.append(m_club.Membership.name == membership_name)

    if membership_id:
        conditions.append(m_club.Membership.id == membership_id)

    if only_active:
        conditions.append(m_club.Membership.status != m_club.MembershipStatus.DELETED)

    res = await db.execute(select(exists(select(1).select_from(m_club.Membership).filter(and_(*conditions)))))
    return bool(res.scalar())


async def update_membership(
    db: AsyncSession, membership: m_club.Membership, updated_membership: s_club.MembershipUpdate
) -> Tuple[str, bool]:
    """
    Update a membership.

    :param db: The database session
    :param membership: The membership to update
    :param updated_membership: The updated membership details
    :return: The updated membership
    """
    details = ""
    cancel_subscriptions = False
    name_description_updated = False

    if updated_membership.status and updated_membership.status == m_club.MembershipStatusPublic.DRAFT:
        raise ValueError("Cannot update membership to draft status")

    if updated_membership.name and membership.name != updated_membership.name:
        if await membership_exists(db, membership.club_id, updated_membership.name):
            raise ValueError("Membership already exists")

        details += f"Name: {membership.name}\n"
        membership.name = updated_membership.name
        name_description_updated = True

    if updated_membership.description and membership.description != updated_membership.description:
        details += f"Description: {membership.description}\n"
        membership.description = updated_membership.description
        name_description_updated = True

    if updated_membership.status and membership.status != updated_membership.status.to_internal():
        details += f"Status: {membership.status}\n"
        membership.status = updated_membership.status.to_internal()

    if updated_membership.price and membership.price != updated_membership.price:
        details += f"Price: {membership.price}\n"
        membership.price = updated_membership.price
        cancel_subscriptions = True

    if updated_membership.currency and membership.currency != updated_membership.currency:
        details += f"Currency: {membership.currency}\n"
        membership.currency = updated_membership.currency
        cancel_subscriptions = True

    if updated_membership.duration and membership.duration != updated_membership.duration:
        details += f"Duration: {membership.duration}\n"
        membership.duration = updated_membership.duration
        cancel_subscriptions = True

    if updated_membership.duration_unit and membership.duration_unit != updated_membership.duration_unit:
        details += f"Duration Unit: {membership.duration_unit}\n"
        membership.duration_unit = updated_membership.duration_unit
        cancel_subscriptions = True

    if not details:
        raise ValueError("No changes detected")

    if name_description_updated:
        transactions_core.modify_membership_name_description(
            membership.club.stripe_account_id, membership.stripe_product_id, membership.name, membership.description # type: ignore
        )

    if cancel_subscriptions:
        new_stripe_price = transactions_core.modify_membership_price_duration(
            membership.club.stripe_account_id, # type: ignore
            membership.price,
            membership.currency,
            membership_duration_to_stripe_duration(membership.duration, membership.duration_unit),
            membership.duration,
        )
        membership.stripe_price_id = new_stripe_price.id

    await db.flush()
    return details, cancel_subscriptions


async def delete_membership(db: AsyncSession, membership: m_club.Membership) -> None:
    """
    Delete a membership.

    :param db: The database session
    :param club_id: The ID of the club to which the membership belongs
    :param membership_id: The ID of the membership to be deleted
    """
    if membership.status == m_club.MembershipStatus.DELETED:
        raise ValueError("Membership already deleted")

    membership.status = m_club.MembershipStatus.DELETED
    membership.deleted_at = datetime.datetime.now()
    await db.flush()


###########################################################################
############################ Membership Access ############################
###########################################################################
async def create_membership_access(
    db: AsyncSession,
    membership_id: uuid.UUID,
    membership_access: List[s_club.MembershipProgramAccessCreate],
) -> List[m_club.MembershipAccess]:
    """
    Create access to programs for a membership.

    :param db: The database session
    :param membership_id: The ID of the membership
    :param membership_access: The details of the membership access
    :return: The created membership access
    """
    accesses = []
    for access in membership_access:
        program_access = m_club.MembershipAccess(
            membership_id=membership_id,
            program_id=access.program_id,
            additional_fee=access.additional_fee,
        )
        accesses.append(program_access)

    db.add_all(accesses)
    await db.flush()
    return accesses


async def any_membership_access_exists(
    db: AsyncSession,
    membership_id: uuid.UUID,
    program_ids: List[uuid.UUID],
) -> bool:
    """
    Check if any membership access exists for a membership and a list of programs.

    :param db: The database session
    :param club_id: The ID of the club
    :param membership_id: The ID of the membership
    :param program_ids: The IDs of the programs
    :return: Whether any membership access exists
    """
    res = await db.execute(
        select(
            exists(
                select(1)
                .select_from(m_club.MembershipAccess)
                .filter(
                    m_club.MembershipAccess.membership_id == membership_id,
                    m_club.MembershipAccess.program_id.in_(program_ids),
                )
            )
        )
    )
    return bool(res.scalar())


async def get_membership_access(
    db: AsyncSession, club_id: uuid.UUID, membership_id: uuid.UUID, program_id: uuid.UUID
) -> Optional[m_club.MembershipAccess]:
    """
    Retrieve access to a program for a membership.

    :param db: The database session
    :param membership_id: The ID of the membership
    :param program_id: The ID of the program
    :return: The membership access, if found
    """
    access = await db.execute(
        select(m_club.MembershipAccess)
        .join(m_club.Membership)
        .filter(
            m_club.Membership.club_id == club_id,
            m_club.MembershipAccess.membership_id == membership_id,
            m_club.MembershipAccess.program_id == program_id,
        )
    )
    return access.scalar_one_or_none()


async def update_membership_access(
    db: AsyncSession,
    membership_access: m_club.MembershipAccess,
    additional_fee: int,
) -> m_club.MembershipAccess:
    """
    Update access to a program for a membership.

    :param db: The database session
    :param membership_id: The ID of the membership
    :param program_id: The ID of the program
    :param additional_fee: The additional fee for the program
    :return: The updated membership access
    """
    membership_access.additional_fee = additional_fee
    await db.flush()
    return membership_access


async def delete_membership_access(db: AsyncSession, membership_id: uuid.UUID, program_ids: List[uuid.UUID]) -> None:
    """
    Delete access to programs for a membership.

    :param db: The database session
    :param club_id: The ID of the club
    :param membership_id: The ID of the membership
    :param program_ids: The IDs of the programs to remove access to
    """
    await db.execute(
        delete(m_club.MembershipAccess).where(
            m_club.MembershipAccess.membership_id == membership_id,
            m_club.MembershipAccess.program_id.in_(program_ids),
        )
    )
    await db.flush()


###########################################################################
############################## Subscriptions ##############################
###########################################################################
async def create_membership_subscription(
    db: AsyncSession, user: m_user.User, membership: m_club.Membership
) -> Tuple[m_payment.MembershipSubscription, stripe.Subscription]:
    """
    Create a new membership subscription.

    :param db: The database session
    :param user: The user who is subscribing to the membership
    :param membership: The membership to subscribe to
    :return: The created membership subscription
    """
    if membership.status in [m_club.MembershipStatus.DELETED, m_club.MembershipStatus.DRAFT]:
        raise ValueError("Cannot create subscription for deleted or draft memberships")

    state = inspect(membership)
    if "club" in state.unloaded:
        await db.refresh(membership, ["club"])

    timedelta = membership_duration_to_timedelta(membership.duration, membership.duration_unit)

    # TODO Create a stripe customer if user does not have one and then create a subscription
    if not user.stripe_customer_id:
        stripe_user = transactions_core.create_customer(user.email, f"{user.first_name} {user.last_name}")
        user.stripe_customer_id = stripe_user.id
        await db.flush()

    stripe_subscription = transactions_core.create_subscription(
        membership.club.stripe_account_id, user.stripe_customer_id, membership.stripe_price_id # type: ignore
    )

    subscription = m_payment.MembershipSubscription(
        membership_id=membership.id,
        user_id=user.id,
        stripe_subscription_id=stripe_subscription.id,
        price_snapshot=membership.price,
        start_datetime=datetime.datetime.now(),
        end_datetime=datetime.datetime.now() + timedelta,
        status=m_payment.MembershipSubscriptionStatus.ACTIVE,
    )
    db.add(subscription)
    await db.flush()
    return subscription, stripe_subscription


async def get_membership_subscription_by_user(
    db: AsyncSession, user_id: uuid.UUID, membership_id: uuid.UUID, query_options: list = []
) -> Optional[m_payment.MembershipSubscription]:
    """
    Retrieve a membership subscription by user ID and subscription ID.

    :param db: The database session
    :param user_id: The ID of the user whose memberships are to be retrieved
    :param membership_id: The ID of the membership
    :param query_options: The query options to apply
    :return: The membership subscription, if found
    """
    subscription = await db.execute(
        select(m_payment.MembershipSubscription)
        .options(*query_options)
        .filter(
            m_payment.MembershipSubscription.user_id == user_id,
            m_payment.MembershipSubscription.membership_id == membership_id,
        )
    )
    return subscription.scalar_one_or_none()


async def get_user_membership_subscriptions(
    db: AsyncSession, user_id: uuid.UUID
) -> List[m_payment.MembershipSubscription]:
    """
    Retrieve the memberships associated with a specific user.

    :param db: The database session
    :param user_id: The ID of the user whose memberships are to be retrieved
    :return: A list of memberships for the user
    """
    memberships = await db.execute(
        select(m_payment.MembershipSubscription).filter(m_payment.MembershipSubscription.user_id == user_id)
    )
    return list(memberships.unique().scalars().all())


async def get_user_active_membership_subscriptions(
    db: AsyncSession, user_id: uuid.UUID
) -> List[m_payment.MembershipSubscription]:
    """
    Retrieve the active memberships associated with a specific user.

    :param db: The database session
    :param user_id: The ID of the user whose memberships are to be retrieved
    :return: A list of active memberships for the user
    """
    memberships = await db.execute(
        select(m_payment.MembershipSubscription).filter(
            m_payment.MembershipSubscription.user_id == user_id,
            m_payment.MembershipSubscription.end_datetime > datetime.datetime.now(),
        )
    )
    return list(memberships.unique().scalars().all())


async def get_user_active_membership_subscription_by_club(
    db: AsyncSession, user_id: uuid.UUID, club_id: uuid.UUID
) -> Optional[m_payment.MembershipSubscription]:
    """
    Retrieve a membership subscription by user ID and club ID.

    :param db: The database session
    :param user_id: The ID of the user
    :param club_id: The ID of the club
    :return: The membership subscription, if found
    """
    subscription = await db.execute(
        select(m_payment.MembershipSubscription).filter(
            m_payment.MembershipSubscription.user_id == user_id,
            m_payment.MembershipSubscription.club_id == club_id,
            m_payment.MembershipSubscription.status == m_payment.MembershipSubscriptionStatus.ACTIVE,
            m_payment.MembershipSubscription.end_datetime > datetime.datetime.now(),
        )
    )
    return subscription.scalar_one_or_none()


async def cancel_membership_subscription(db: AsyncSession, subscription: m_payment.MembershipSubscription) -> None:
    """
    Cancel a specific membership subscription.

    :param db: The database session
    :param subscription: The subscription to cancel
    """
    if subscription.status == m_payment.MembershipSubscriptionStatus.CANCELLED:
        raise ValueError("Membership subscription already cancelled")

    # Stripe cancellation
    transactions_core.cancel_subscription(
        subscription.membership.club.stripe_account_id, subscription.stripe_subscription_id
    )

    # Update subscription status
    subscription.status = m_payment.MembershipSubscriptionStatus.CANCELLED
    await db.flush()


async def cancel_all_membership_subscriptions_by_user(
    db: AsyncSession, user_id: uuid.UUID
) -> List[m_payment.MembershipSubscription]:
    """
    Cancel all active memberships associated with a specific user.

    :param db: The database session
    :param user_id: The ID of the user whose memberships are to be cancelled
    :return: A list of memberships that were cancelled
    """
    memberships = await get_user_active_membership_subscriptions(db, user_id)
    for membership in memberships:
        membership.status = m_payment.MembershipSubscriptionStatus.CANCELLED
    return memberships


async def cancel_membership_subscriptions(
    db: AsyncSession, club_id: uuid.UUID, membership_id: uuid.UUID
) -> List[m_payment.MembershipSubscription]:
    """
    Cancel all active subscriptions for a specific membership issued by the club.

    Note: This function is called when a membership is updated and the price, currency, duration, or duration unit is changed.

    :param db: The database session
    :param club_id: The ID of the club
    :param membership_id: The ID of the membership
    """
    res = await db.execute(
        select(m_payment.MembershipSubscription)
        .join(m_club.Membership)
        .options(joinedload(m_payment.MembershipSubscription.user))
        .filter(
            m_club.Membership.club_id == club_id,
            m_payment.MembershipSubscription.membership_id == membership_id,
            or_(
                m_payment.MembershipSubscription.end_datetime == None,
                m_payment.MembershipSubscription.end_datetime > datetime.datetime.now(),
            ),
        )
    )
    subscriptions = list(res.unique().scalars().all())

    for subscription in subscriptions:
        subscription.status = m_payment.MembershipSubscriptionStatus.CANCELLED_BY_CLUB
    await db.flush()
    return subscriptions


###########################################################################
############################## Recurring Task #############################
###########################################################################
async def cancel_bookings_for_cancelled_membership_subscriptions(db: AsyncSession, console: Console) -> bool:
    """
    Cancel all bookings associated with memberships that have been cancelled.

    :param db: The database session
    """
    audit_logger = audit_crud.AuditLogger(db)
    audit_logger.sys_info("Cancelling bookings for cancelled membership subscriptions")

    try:
        res = await db.execute(
            select(m_payment.MembershipSubscription).filter(
                or_(
                    m_payment.MembershipSubscription.status == m_payment.MembershipSubscriptionStatus.CANCELLED,
                    and_(
                        m_payment.MembershipSubscription.status
                        == m_payment.MembershipSubscriptionStatus.CANCELLED_BY_CLUB,
                        m_payment.MembershipSubscription.modified_at
                        < datetime.datetime.now() - datetime.timedelta(days=7),
                    ),
                ),
                m_payment.MembershipSubscription.end_datetime > datetime.datetime.now(),
            )
        )
        subscriptions = res.unique().scalars().all()

        total_cancelled = 0
        for subscription in subscriptions:
            if subscription.status == m_payment.MembershipSubscriptionStatus.CANCELLED_BY_CLUB:
                active_subscription = await get_user_active_membership_subscription_by_club(
                    db, subscription.user_id, subscription.club_id
                )
                if active_subscription and active_subscription.membership_id == subscription.membership_id:
                    continue

            is_user_initiator = (
                False if subscription.status == m_payment.MembershipSubscriptionStatus.CANCELLED_BY_CLUB else True
            )

            res = await db.execute(
                select(m_payment.Booking)
                .join(m_club.Session)
                .join(m_club.Program)
                .filter(
                    m_payment.Booking.user_id == subscription.user_id,
                    m_payment.Booking.status == m_payment.BookingStatus.CONFIRMED,
                    m_payment.Booking.booking_type.in_(
                        [m_payment.BookingType.MEMBERSHIP, m_payment.BookingType.MEMBERSHIP_ACCESS]
                    ),
                    m_club.Program.club_id == subscription.club_id,
                    active_sessions_db_condition(),
                )
            )

            user_bookings = res.unique().scalars().all()
            bookings_to_refund_by_transaction = {}

            for booking in user_bookings:
                if booking.transaction_id not in bookings_to_refund_by_transaction:
                    bookings_to_refund_by_transaction[booking.transaction_id] = []
                bookings_to_refund_by_transaction[booking.transaction_id].append(booking)

            refunds = []
            for transaction_id, bookings in bookings_to_refund_by_transaction.items():
                refunds = await transactions_crud.create_refund(
                    db, transaction_id, bookings, is_user_refund=is_user_initiator
                )
                audit_logger.refunds_created(
                    subscription.user_id,
                    transaction_id,
                    refund_ids=[refund.id for refund in refunds],
                    details=f"Refunds created due to cancellation of membership subscription {subscription.id}",
                    is_initiated_by_user=is_user_initiator,
                )

            await db.flush()

            booking_ids = []
            for booking in user_bookings:
                booking.status = m_payment.BookingStatus.CANCELLED
                booking_ids.append(booking.id)

            audit_logger.bookings_cancelled(
                subscription.user_id,
                details=f"Bookings cancelled for cancelled membership subscription {subscription.id}: {', '.join(booking_ids)}",
            )
            await db.flush()
            if refunds:
                pass
                # TODO - Inform the user of the cancellation and the refund

            total_cancelled += len(user_bookings)

        # End of for loop
        audit_logger.sys_info(f"{total_cancelled} bookings cancelled for cancelled membership subscriptions")
        await db.commit()
        console.log(
            f"[blue][INFO][/blue]\t\t{total_cancelled} bookings cancelled for cancelled membership subscriptions"
        )
        return True

    except Exception as e:
        await db.rollback()
        audit_logger.sys_error(
            "Error cancelling bookings for cancelled membership subscriptions", traceback=traceback.format_exc()
        )
        await db.commit()
        console.log("[red][ERROR][/red]\t\tError cancelling bookings for cancelled membership subscriptions")
        console.print_exception()
        return False
