from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, or_, exists, and_, ColumnElement, update, func
from sqlalchemy.orm import undefer, joinedload, with_loader_criteria
from typing import List, Tuple, Optional, Dict
import uuid
from rich.console import Console
import traceback
import datetime

from schemas import s_club

from models import m_club, m_generic, m_user, m_payment

from crud import role as role_crud, generic as generic_crud, audit as audit_crud


async def create_bookings(
    db: AsyncSession,
    user_id: uuid.UUID,
    booking_creates: List[Tuple[m_club.Session, int, m_payment.BookingType]],
    transaction_id: Optional[uuid.UUID] = None,
) -> Tuple[List[m_payment.Booking], str]:
    """Create bookings for a user

    :param db: The database session
    :param user_id: The ID of the user
    :param transaction_id: The ID of the transaction
    :param booking_creates: A list of tuples containing the session and booking type
    :return: A list of bookings created
    """
    details_list = []
    bookings: List[m_payment.Booking] = []
    for booking_create in booking_creates:
        booking_id = uuid.uuid4()
        booking = m_payment.Booking(
            id=booking_id,
            user_id=user_id,
            session=booking_create[0],
            price_snapshot=booking_create[1],
            pricing_model_snapshot=booking_create[0].program.pricing_model,
            booking_type=booking_create[2],
            transaction_id=(
                transaction_id
                if booking_create[2] not in m_payment.FREE_BOOKING_TYPES
                else None  # Membership access and free sessions/programs do not require transaction_id
            ),
            status=(
                m_payment.BookingStatus.PENDING
                if booking_create[2] not in m_payment.FREE_BOOKING_TYPES
                else m_payment.BookingStatus.CONFIRMED  # Membership access and free sessions/programs do not require waiting for payment
            ),
        )
        bookings.append(booking)
        details_list.append(f"{booking_id}:{booking_create[0].id}:{booking_create[2].value}")

    db.add_all(bookings)
    await db.flush()
    details = "Bookings: " + ", ".join(details_list)
    return bookings, details


async def get_booking_by_id(db: AsyncSession, booking_id: uuid.UUID) -> m_payment.Booking:
    """Get a booking by its ID

    :param db: The database session
    :param booking_id: The ID of the booking
    :return: The booking
    """
    booking = await db.execute(select(m_payment.Booking).filter(m_payment.Booking.id == booking_id))
    return booking.unique().scalar()


async def get_bookings_by_ids(
    db: AsyncSession, booking_ids: List[uuid.UUID], with_ids: bool = False, additional_query_options=[]
) -> List[m_payment.Booking]:
    """Get bookings by their IDs

    :param db: The database session
    :param booking_ids: The IDs of the bookings
    :return: The bookings
    """
    query_options = []
    if with_ids:
        query_options.extend(
            [
                joinedload(m_payment.Booking.session).load_only(m_club.Session.program_id),
                joinedload(m_payment.Booking.session)
                .joinedload(m_club.Session.program)
                .load_only(m_club.Program.club_id),
            ]
        )
    if additional_query_options:
        query_options.extend(additional_query_options)

    bookings = await db.execute(
        select(m_payment.Booking).options(*query_options).filter(m_payment.Booking.id.in_(booking_ids))
    )
    return list(bookings.unique().scalars().all())


async def get_bookings_by_session_id(
    db: AsyncSession, session_id: uuid.UUID, with_user=False
) -> List[m_payment.Booking]:
    """Get bookings by session ID

    :param db: The database session
    :param session_id: The ID of the session
    :return: The bookings
    """
    query_options = []
    if with_user:
        query_options.append(joinedload(m_payment.Booking.user))
    bookings = await db.execute(
        select(m_payment.Booking).options(*query_options).filter(m_payment.Booking.session_id == session_id)
    )
    return list(bookings.unique().scalars().all())


async def get_bookings_by_club_id(
    db: AsyncSession,
    club_id: uuid.UUID,
    status: m_payment.BookingStatus = m_payment.BookingStatus.CONFIRMED,
    additional_filters=[],
) -> List[m_payment.Booking]:
    """Get bookings by club ID

    :param db: The database session
    :param club_id: The ID of the club
    :param stats: List of booking statuses to filter
    :return: The bookings associated with the club
    """
    bookings = await db.execute(
        select(m_payment.Booking)
        .options(
            joinedload(m_payment.Booking.session).load_only(m_club.Session.program_id),
            joinedload(m_payment.Booking.session).joinedload(m_club.Session.program).load_only(m_club.Program.club_id),
            joinedload(m_payment.Booking.user).load_only(m_user.User.id, m_user.User.first_name, m_user.User.last_name),
        )
        .options(
            joinedload(m_payment.Booking.session).load_only(m_club.Session.program_id),
            joinedload(m_payment.Booking.session).joinedload(m_club.Session.program).load_only(m_club.Program.club_id),
        )
        .filter(
            m_club.Session.program.has(m_club.Program.club_id == club_id),
            m_payment.Booking.status == status,
            and_(*additional_filters),
        )
    )
    return list(bookings.unique().scalars().all())


async def get_bookings_by_user_id(
    db: AsyncSession, user_id: uuid.UUID, stats: List[m_payment.BookingStatus] = []
) -> List[m_payment.Booking]:
    """Get bookings by user ID

    :param db: The database session
    :param user_id: The ID of the user
    :param stats: List of booking statuses to filter
    :return: The bookings associated with the user
    """
    bookings = await db.execute(
        select(m_payment.Booking)
        .options(
            joinedload(m_payment.Booking.session).load_only(m_club.Session.program_id),
            joinedload(m_payment.Booking.session).joinedload(m_club.Session.program).load_only(m_club.Program.club_id),
        )
        .filter(m_payment.Booking.user_id == user_id, m_payment.Booking.status.in_(stats))
    )
    return list(bookings.unique().scalars().all())


async def get_bookings_by_user_id_and_id(
    db: AsyncSession, booking_id: uuid.UUID, user_id: uuid.UUID
) -> m_payment.Booking:
    """Get a booking by its ID and user ID

    :param db: The database session
    :param booking_id: The ID of the booking
    :param user_id: The ID of the user
    :return: The booking
    """

    booking = await db.execute(
        select(m_payment.Booking)
        .options(
            joinedload(m_payment.Booking.session),
            joinedload(m_payment.Booking.session).joinedload(m_club.Session.occurrences),
            joinedload(m_payment.Booking.session).joinedload(m_club.Session.program),
            joinedload(m_payment.Booking.session)
            .joinedload(m_club.Session.program)
            .undefer(m_club.Program.description),
            joinedload(m_payment.Booking.session)
            .joinedload(m_club.Session.program)
            .joinedload(m_club.Program.categories),
        )
        .filter(m_payment.Booking.id == booking_id, m_payment.Booking.user_id == user_id)
    )
    return booking.unique().scalar()


async def get_user_booked_sessions(db: AsyncSession, user_id: uuid.UUID):
    query_options = [
        joinedload(m_club.Program.categories),
        undefer(m_club.Program.description),
        joinedload(m_club.Program.sessions),
        joinedload(m_club.Program.sessions).joinedload(m_club.Session.occurrences),
        joinedload(m_club.Program.sessions).joinedload(m_club.Session.address),
        joinedload(m_club.Program.memberships_access).load_only(m_club.MembershipAccess.membership_id),
        with_loader_criteria(
            m_club.Session,
            lambda s: s.bookings.any(
                and_(
                    m_payment.Booking.user_id == user_id, m_payment.Booking.status == m_payment.BookingStatus.CONFIRMED
                )
            ),
            include_aliases=True,
        ),
    ]

    session_count_filter = (
        select(func.count(m_club.Session.id)).where(m_club.Session.program_id == m_club.Program.id).scalar_subquery()
        > 0
    )

    res = await db.execute(select(m_club.Program).options(*query_options).filter(session_count_filter))
    return list(res.unique().scalars().all())


async def get_users_by_session_id(db: AsyncSession, session_id: uuid.UUID) -> List[m_user.User]:
    """Get users by session ID

    :param db: The database session
    """
    users = await db.execute(
        select(m_user.User)
        .options(
            joinedload(m_user.User.address),
        )
        .join(m_payment.Booking)
        .filter(m_payment.Booking.session_id == session_id)
    )
    return list(users.unique().scalars().all())


async def has_user_booked(db: AsyncSession, user_id: uuid.UUID, session_ids: List[uuid.UUID]) -> bool:
    """Check if user has already booked the sessions or programs

    :param db: The database session
    :param user_id: The ID of the user
    :param session_ids: The IDs of the sessions
    :return: True if user has already booked the sessions, False otherwise
    """
    res = await db.execute(
        select(
            exists(
                select(1)
                .select_from(m_payment.Booking)
                .filter(
                    and_(
                        m_payment.Booking.user_id == user_id,
                        or_(
                            m_payment.Booking.session_id.in_(session_ids),
                        ),
                    )
                )
            )
        )
    )
    return bool(res.scalar())


async def change_booking_stats(db: AsyncSession, booking_ids: List[uuid.UUID], status: m_payment.BookingStatus) -> bool:
    """Change the status of the bookings

    :param db: The database session
    :param booking_ids: The IDs of the bookings
    :param status: The new status of the bookings
    :return: True if the status was changed, False otherwise
    """
    res = await db.execute(
        update(m_payment.Booking).values(status=status).filter(m_payment.Booking.id.in_(booking_ids))
    )
    return res.rowcount == len(booking_ids)


###########################################################################
############################## Recurring Task #############################
###########################################################################
async def refresh_bookings_status(db: AsyncSession, console: Console) -> bool:
    """Refresh the status of the bookings"""
    audit_logger = audit_crud.AuditLogger(db)
    audit_logger.sys_info("Refreshing bookings status")

    try:
        res = await db.execute(
            update(m_payment.Booking)
            .values(status=m_payment.BookingStatus.COMPLETED)
            .filter(
                m_payment.Booking.status == m_payment.BookingStatus.CONFIRMED,
                m_payment.Booking.session_id == m_club.Session.id,
                or_(
                    m_club.Session.end_date < datetime.datetime.now(tz=datetime.timezone.utc),
                    m_club.Session.end_date == None,
                ),
                or_(
                    m_club.Session.end_datetime < datetime.datetime.now(tz=datetime.timezone.utc),
                    m_club.Session.end_datetime == None,
                ),
            )
        )

        audit_logger.sys_info(f"Updated {res.rowcount} bookings to COMPLETED")
        await db.commit()

        console.log(f"[blue][INFO][/blue]\t\tUpdated {res.rowcount} bookings to COMPLETED")
        return True
    except Exception as e:
        await db.rollback()
        audit_logger.sys_error("Error checking refreshing booking stats", traceback=traceback.format_exc())
        await db.commit()
        console.log("[red][ERROR][/red]\t\tError checking refreshing booking stats")
        console.print_exception()
        return False
