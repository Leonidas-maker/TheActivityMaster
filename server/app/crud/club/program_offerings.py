from sqlalchemy.orm import joinedload
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, or_, exists, and_, ColumnElement, func, update
from sqlalchemy.inspection import inspect
from sqlalchemy.orm import undefer, joinedload
from typing import List, Tuple, Optional, Dict
import uuid
import datetime
from rich.console import Console
from dateutil.rrule import rrule, WEEKLY
import traceback

from schemas import s_club

from models import m_club, m_payment

from crud import audit as audit_crud, generic as generic_crud

from config.permissions import ClubPermissions


###########################################################################
################################# Helpers #################################
###########################################################################
def authorized_read_program_db_condition(user_id: uuid.UUID, club_id: uuid.UUID) -> ColumnElement[bool]:
    subquery = (
        select(1)
        .select_from(m_club.Program)
        .join(m_club.ClubRole, m_club.Program.club_id == m_club.ClubRole.club_id)
        .join(m_club.UserClubRole, m_club.ClubRole.id == m_club.UserClubRole.club_role_id)
        .join(m_club.ClubRolePermission, m_club.ClubRole.id == m_club.ClubRolePermission.role_id)
        .join(m_club.Permission, m_club.ClubRolePermission.permission_id == m_club.Permission.id)
        .outerjoin(
            m_club.UserTrainer,
            and_(
                m_club.UserTrainer.user_id == m_club.UserClubRole.user_id,
                m_club.UserTrainer.program_id == m_club.Program.id,
            ),
        )
        .filter(
            m_club.UserClubRole.user_id == user_id,
            m_club.ClubRole.club_id == club_id,
            m_club.Permission.name == ClubPermissions.READ_PROGRAMS.value,
            or_(
                m_club.ClubRole.level != 10,
                and_(
                    m_club.ClubRole.level == 10,
                    m_club.UserTrainer.user_id.isnot(None),
                ),
            ),
        )
    )
    return exists(subquery).correlate(m_club.Program)


def active_sessions_db_condition() -> ColumnElement[bool]:
    return and_(
        or_(
            m_club.Session.end_date >= datetime.datetime.now(tz=datetime.timezone.utc),
            m_club.Session.end_date == None,
        ),
        or_(
            m_club.Session.end_datetime >= datetime.datetime.now(tz=datetime.timezone.utc),
            m_club.Session.end_datetime == None,
        ),
    )


###########################################################################
########################### Session Occurrences ###########################
###########################################################################
def refresh_occurrences_for_session(session: m_club.Session) -> Tuple[List[m_club.SessionOccurrence], int]:
    if session.session_type != m_club.SessionType.COURSE:
        raise ValueError("Only COURSE sessions can have occurrences")

    weekday_mapping = {
        m_club.Weekday.MONDAY.value: 0,
        m_club.Weekday.TUESDAY.value: 1,
        m_club.Weekday.WEDNESDAY.value: 2,
        m_club.Weekday.THURSDAY.value: 3,
        m_club.Weekday.FRIDAY.value: 4,
        m_club.Weekday.SATURDAY.value: 5,
        m_club.Weekday.SUNDAY.value: 6,
    }

    existing_weeks = {
        (occurrence.occurrence_date.isocalendar()[0], occurrence.occurrence_date.isocalendar()[1]): occurrence
        for occurrence in session.occurrences
    }

    byweekday = weekday_mapping.get(session.day_of_week.value)  # type: ignore
    if byweekday is None:
        return [], 0

    occurrences = []
    occurrences_updated = 0

    end_date = session.end_date if session.end_date else datetime.date.today() + datetime.timedelta(days=90)

    for dt in rrule(
        freq=WEEKLY,
        dtstart=datetime.datetime.combine(session.start_date, session.start_time),  # type: ignore
        until=datetime.datetime.combine(end_date, session.end_time),  # type: ignore
        byweekday=byweekday,
    ):
        occ_date = dt.date()
        current_week = (occ_date.isocalendar()[0], occ_date.isocalendar()[1])

        if not existing_weeks.get(current_week):
            occurrence = m_club.SessionOccurrence(
                session=session,
                occurrence_date=occ_date,
            )
            occurrences.append(occurrence)
            existing_weeks[current_week] = occurrence
        else:
            existing_weeks[current_week].occurrence_date = occ_date
            occurrences_updated += 1

    return occurrences, occurrences_updated


async def clear_future_occurrences_for_session(
    db: AsyncSession, session_id: uuid.UUID, only_scheduled: bool = False
) -> int:
    """Clear future occurrences for a session

    :param db: The database session
    :param session_id: The ID of the session
    :param only_scheduled: Whether to clear only scheduled occurrences
    :return: The number of deleted occurrences
    """
    conditions = [
        m_club.SessionOccurrence.session_id == session_id,
        m_club.SessionOccurrence.occurrence_date >= datetime.date.today(),
    ]

    if only_scheduled:
        conditions.append(m_club.SessionOccurrence.status == m_club.OccurrenceStatus.SCHEDULED)

    res = await db.execute(
        delete(m_club.SessionOccurrence).filter(
            and_(*conditions),
        )
    )
    await db.flush()
    return res.rowcount


async def get_session_occurrences_dict(
    db: AsyncSession,
    program_id: uuid.UUID,
    session_id: uuid.UUID,
    with_email_details: bool = False,
) -> Dict[uuid.UUID, m_club.SessionOccurrence]:
    """Get occurrences for a session

    :param db: The database session
    :param program_id: The ID of the program, used for cross validation
    :param session_id: The ID of the session
    :return:
    """
    query_options = [joinedload(m_club.SessionOccurrence.session)]

    if with_email_details:
        query_options.extend(
            [
                joinedload(m_club.SessionOccurrence.session)
                .joinedload(m_club.Session.program)
                .load_only(m_club.Program.name),
                joinedload(m_club.SessionOccurrence.session)
                .joinedload(m_club.Session.program)
                .joinedload(m_club.Program.club)
                .load_only(m_club.Club.name),
            ]
        )

    res = await db.execute(
        select(m_club.SessionOccurrence)
        .join(m_club.Session)
        .options(*query_options)
        .filter(
            m_club.SessionOccurrence.session_id == session_id,
            m_club.Session.program_id == program_id,
            m_club.Session.session_type == m_club.SessionType.COURSE,
        )
    )
    return {occurrence.id: occurrence for occurrence in res.unique().scalars().all()}


async def get_session_occurrences(
    db: AsyncSession,
    program_id: uuid.UUID,
    session_id: uuid.UUID,
    start_date: Optional[datetime.date] = None,
    end_date: Optional[datetime.date] = None,
) -> List[m_club.SessionOccurrence]:
    """Get occurrences for a session

    :param db: The database session
    :param program_id: The ID of the program, used for cross validation
    :param session_id: The ID of the session
    :param start_date: The start date
    :param end_date: The end date
    :return: A list of occurrences
    """
    conditions = [m_club.SessionOccurrence.session_id == session_id, m_club.Session.program_id == program_id]

    if start_date:
        conditions.append(m_club.SessionOccurrence.occurrence_date >= start_date)

    if end_date:
        conditions.append(m_club.SessionOccurrence.occurrence_date <= end_date)

    res = await db.execute(
        select(m_club.SessionOccurrence)
        .join(m_club.Session)
        .filter(
            and_(*conditions),
        )
    )
    return list(res.unique().scalars().all())


async def get_occurrences_for_program(
    db: AsyncSession, club_id: uuid.UUID, program_id: uuid.UUID, start_date: datetime.date, end_date: datetime.date
) -> List[m_club.SessionOccurrence]:
    """Get occurrences for a program

    :param db: The database session
    :param club_id: The ID of the club, used for cross validation
    :param program_id: The ID of the program
    :param start_date: The start date
    :param end_date: The end date
    :return: A list of occurrences
    """
    res = await db.execute(
        select(m_club.SessionOccurrence)
        .join(m_club.Session)
        .join(m_club.Program)
        .filter(
            m_club.Session.program_id == program_id,
            m_club.Program.club_id == club_id,
            m_club.SessionOccurrence.occurrence_date >= start_date,
            m_club.SessionOccurrence.occurrence_date <= end_date,
        )
    )
    return list(res.unique().scalars().all())


async def get_session_occurrence(
    db: AsyncSession,
    program_id: uuid.UUID,
    session_id: uuid.UUID,
    occurrence_id: uuid.UUID,
    with_email_details: bool = False,
) -> m_club.SessionOccurrence:
    """Get an occurrence by ID

    :param db: The database session
    :param program_id: The ID of the program
    :param session_id: The ID of the session
    :param occurrence_id: The ID of the occurrence
    :return: The occurrence with the given ID
    """
    query_options = []
    if with_email_details:
        query_options.extend(
            [
                joinedload(m_club.SessionOccurrence.session),
                joinedload(m_club.SessionOccurrence.session)
                .joinedload(m_club.Session.program)
                .load_only(m_club.Program.name),
                joinedload(m_club.SessionOccurrence.session)
                .joinedload(m_club.Session.program)
                .joinedload(m_club.Program.club)
                .load_only(m_club.Club.name),
            ]
        )

    res = await db.execute(
        select(m_club.SessionOccurrence)
        .options(*query_options)
        .join(m_club.Session)
        .filter(
            m_club.SessionOccurrence.id == occurrence_id,
            m_club.Session.id == session_id,
            m_club.Session.program_id == program_id,
        )
    )
    return res.unique().scalar_one_or_none()


async def session_occurrence_reschedule(
    db: AsyncSession, occurrence: m_club.SessionOccurrence, occurrence_update: s_club.SessionReschedule
):
    """Update an occurrence

    :param db: The database session
    :param occurrence: The occurrence to update
    :param occurrence_update: The updated occurrence data
    :return: details of the changes made
    """
    occurrence.status = m_club.OccurrenceStatus.RESCHEDULED

    occurrence.start_datetime = occurrence_update.start_datetime
    occurrence.end_datetime = occurrence_update.end_datetime
    occurrence.note = occurrence_update.note


async def session_occurrence_cancel(db: AsyncSession, occurrence: m_club.SessionOccurrence, note: Optional[str] = None):
    """Cancel an occurrence

    :param db: The database session
    :param occurrence: The occurrence to cancel
    """
    occurrence.status = m_club.OccurrenceStatus.CANCELLED
    occurrence.start_datetime = None
    occurrence.end_datetime = None
    occurrence.note = note


async def session_occurrence_reinstate(
    db: AsyncSession, occurrence: m_club.SessionOccurrence, note: Optional[str] = None
):
    """Reinstate a cancelled or rescheduled occurrence

    :param db: The database session
    :param occurrence: The occurrence to reinstate
    """
    occurrence.status = m_club.OccurrenceStatus.SCHEDULED

    occurrence.start_datetime = None
    occurrence.end_datetime = None
    occurrence.note = note


async def clear_occurrences_for_session(db: AsyncSession, session_id: uuid.UUID) -> None:
    """Clear occurrences for a session

    :param db: The database session
    :param session_id: The ID of the session
    """
    await db.execute(delete(m_club.SessionOccurrence).where(m_club.SessionOccurrence.session_id == session_id))


###########################################################################
################################# Session #################################
###########################################################################
async def session_exists_event(
    db: AsyncSession, program_id: uuid.UUID, start_datetime: datetime.datetime, end_datetime: datetime.datetime
) -> bool:
    """Check if a session already exists

    :param db: The database session
    :param sessions: The session to check
    :return: True if the session already exists, False otherwise
    """
    conditions = [m_club.Session.program_id == program_id]
    conditions.extend(
        [
            m_club.Session.start_datetime == start_datetime,
            m_club.Session.end_datetime == end_datetime,
        ]
    )
    res = await db.execute(
        select(
            exists(
                select(1)
                .select_from(m_club.Session)
                .where(
                    and_(*conditions),
                )
            )
        )
    )
    return bool(res.scalar())


async def session_exists_course(
    db: AsyncSession,
    program_id: uuid.UUID,
    day_of_week: int,
    start_time: datetime.time,
    end_time: datetime.time,
) -> bool:
    """Check if a session already exists

    :param db: The database session
    :param sessions: The session to check
    :return: True if the session already exists, False otherwise
    """
    conditions = [m_club.Session.program_id == program_id]
    conditions.extend(
        [
            m_club.Session.day_of_week == day_of_week,
            m_club.Session.start_time == start_time,
            m_club.Session.end_time == end_time,
        ]
    )
    res = await db.execute(
        select(
            exists(
                select(1)
                .select_from(m_club.Session)
                .where(
                    and_(*conditions),
                )
            )
        )
    )
    return bool(res.scalar())


async def get_session(
    db: AsyncSession, program_id: uuid.UUID, session_id: uuid.UUID, query_options: list = []
) -> m_club.Session:
    """Get a session by ID

    :param db: The database session
    :param program_id: The ID of the program
    :param session_id: The ID of the session
    :return: The session with the given ID
    """
    res = await db.execute(
        select(m_club.Session)
        .filter(m_club.Session.program_id == program_id, m_club.Session.id == session_id)
        .options(*query_options)
    )
    return res.unique().scalar_one_or_none()


async def get_active_session(
    db: AsyncSession, program_id: uuid.UUID, session_id: uuid.UUID, query_options: list = []
) -> m_club.Session:
    """Get a session by ID which is active and not past

    :param db: The database session
    :param program_id: The ID of the program
    :param session_id: The ID of the session
    :return: The session with the given ID
    """
    res = await db.execute(
        select(m_club.Session)
        .filter(
            m_club.Session.program_id == program_id,
            m_club.Session.id == session_id,
            active_sessions_db_condition(),
        )
        .options(*query_options)
    )
    return res.unique().scalar_one_or_none()


async def get_bookable_sessions(db: AsyncSession, session_ids: List[uuid.UUID]) -> List[m_club.Session]:
    """Get bookable sessions which are active, not past and not requiring membership

    :param db: The database session
    :param session_ids: The IDs of the sessions
    :return: A list of sessions
    """
    bookings_count_subquery = (
        select(func.count(m_payment.Booking.id))
        .where(m_payment.Booking.session_id == m_club.Session.id)
        .scalar_subquery()
    )

    res = await db.execute(
        select(m_club.Session)
        .join(m_club.Program)
        .filter(
            m_club.Program.status == m_club.ProgramStatus.ACTIVE,
            m_club.Program.pricing_model == m_club.PriceType.PER_SESSION,
            m_club.Session.deleted_at.is_(None),
            m_club.Session.id.in_(session_ids),
            active_sessions_db_condition(),
            m_club.Session.capacity > bookings_count_subquery,
        )
        .options(
            joinedload(m_club.Session.program).joinedload(m_club.Program.memberships_access),
            joinedload(m_club.Session.program).joinedload(m_club.Program.club),
        )
    )
    return list(res.unique().scalars().all())


async def get_authorized_sessions(
    db: AsyncSession, club_id: uuid.UUID, page: int, page_size: int, user_id: Optional[uuid.UUID] = None
) -> List[m_club.Session]:
    """Get sessions that the user is authorized to view

    :param db: The database session
    :param club_id: The ID of the club
    :param page: The page number
    :param page_size: The number of sessions per page
    :param user_id: The ID of the user
    :return: A list of sessions
    """
    query_options = [
        joinedload(m_club.Session.address),
        joinedload(m_club.Session.occurrences),
    ]

    if user_id:
        query = (
            select(m_club.Session)
            .join(m_club.Program, m_club.Program.id == m_club.Session.program_id)
            .filter(
                m_club.Program.club_id == club_id,
                or_(
                    # Public sessions
                    m_club.Program.status == m_club.ProgramStatus.ACTIVE,
                    # Authorized sessions for the user
                    authorized_read_program_db_condition(user_id, club_id),
                ),
                or_(
                    m_club.Session.end_date >= datetime.datetime.now(tz=datetime.timezone.utc),
                    m_club.Session.end_date == None,
                ),
                or_(
                    m_club.Session.end_datetime >= datetime.datetime.now(tz=datetime.timezone.utc),
                    m_club.Session.end_datetime == None,
                ),
            )
        )
    else:
        query = (
            select(m_club.Session)
            .join(m_club.Program, m_club.Program.id == m_club.Session.program_id)
            .filter(m_club.Program.club_id == club_id, m_club.Program.status == m_club.ProgramStatus.ACTIVE)
        )

    res = await db.execute(query.options(*query_options).offset((page - 1) * page_size).limit(page_size))
    return list(res.unique().scalars().all())

async def get_session_users(
    db: AsyncSession, session_id: uuid.UUID) -> List[uuid.UUID]:
    """Get users for a session"""
    res = await db.execute(
        select(m_payment.Booking.user_id)
        .filter(m_payment.Booking.session_id == session_id, m_payment.Booking.status == m_payment.BookingStatus.CONFIRMED)
    )
    return list(res.unique().scalars().all())

async def get_program_sessions(
    db: AsyncSession, program_id: uuid.UUID, session_ids: Optional[List[uuid.UUID]] = None
) -> List[m_club.Session]:
    """Get all sessions of a program

    :param db: The database session
    :param program_id: The ID of the program
    :return: A list of sessions
    """
    conditions = [m_club.Session.program_id == program_id]
    if session_ids:
        conditions.append(m_club.Session.id.in_(session_ids))
    res = await db.execute(select(m_club.Session).filter(and_(*conditions)))
    return list(res.unique().scalars().all())


async def create_session(db: AsyncSession, program_id: uuid.UUID, session: s_club.SessionCreate) -> m_club.Session:
    """Create a session

    :param db: The database session
    :param session: The session to create
    :return: The created session
    """
    # * This could be done without consistency checks, because of the own pydantic model validation
    # * which ensure that the session is either a one-time event or a recurring event, not both.

    address = None
    if session.address:
        address = await generic_crud.get_create_address(db, session.address)

    db_session = m_club.Session(
        program_id=program_id,
        session_type=session.session_type,
        capacity=session.capacity,
        price=session.price,
        start_datetime=session.start_datetime,
        end_datetime=session.end_datetime,
        day_of_week=session.day_of_week,
        start_time=session.start_time,
        end_time=session.end_time,
        start_date=session.start_date,
        end_date=session.end_date,
        address=address,
    )

    db.add(db_session)
    if session.session_type == m_club.SessionType.COURSE:
        occurrences, _ = refresh_occurrences_for_session(db_session)
        db.add_all(occurrences)

    await db.flush()
    await db.refresh(db_session, ["occurrences"])
    return db_session


async def create_sessions_for_program(
    db: AsyncSession,
    sessions: List[s_club.SessionCreate],
    program_id: Optional[uuid.UUID] = None,
    program: Optional[m_club.Program] = None,
) -> List[m_club.Session]:
    """Create multiple sessions for a program by providing a list of pydantic "SessionBase" objects

    :param db: The database session
    :param program_id: The ID of the program
    :param sessions: The sessions to create
    :return: The created sessions
    """
    if len(sessions) == 0:
        raise ValueError("No sessions provided")

    if not program and not program_id:
        raise ValueError("Program or program_id is required")

    if program:
        db_sessions = [m_club.Session(program=program, **session.model_dump()) for session in sessions]
    else:
        db_sessions = [m_club.Session(program_id=program_id, **session.model_dump()) for session in sessions]
    db.add_all(db_sessions)
    await db.flush()
    return db_sessions


async def update_session(db: AsyncSession, session: m_club.Session, session_update: s_club.SessionUpdate) -> str:
    """Update a session

    :param db: The database session
    :param session: The session to update
    :param session_update: The updated session data
    :return: details of the changes made
    """
    details = ""
    course_time_changed = False

    if not session:
        raise ValueError("Session not found")

    if not session_update.session_type:
        if session.session_type == m_club.SessionType.COURSE and any(
            [session_update.start_datetime, session_update.end_datetime]
        ):
            raise ValueError("Start and end datetime are not allowed for COURSE sessions")

        if session.session_type == m_club.SessionType.EVENT and any(
            [
                session_update.day_of_week,
                session_update.start_time,
                session_update.end_time,
                session_update.start_date,
                session_update.end_date,
            ]
        ):
            raise ValueError("Day of week, start time, end time and start date are not allowed for EVENT sessions")

    if session_update.capacity and session.capacity != session_update.capacity:
        details += f"Capacity: {session.capacity} -> {session_update.capacity}"
        session.capacity = session_update.capacity

    if session_update.price and session.price != session_update.price:
        details += f"Price: {session.price} -> {session_update.price}"
        session.price = session_update.price

    if session_update.address:
        new_address = await generic_crud.get_create_address(db, session_update.address)
        if session.address_id != new_address.id:
            details += f"Address: {session.address_id} -> {new_address.id}"
            session.address = new_address

    session_type_changed = False
    if session_update.session_type and session.session_type != session_update.session_type:
        details += f"Session Type: {session.session_type} -> {session_update.session_type}"
        session.session_type = session_update.session_type
        session_type_changed = True

        if session_update.session_type == m_club.SessionType.EVENT:
            if not session_update.start_datetime or not session_update.end_datetime:
                raise ValueError("Start and end datetime are required for EVENT sessions")

            session.day_of_week = None
            session.start_time = None
            session.end_time = None
            session.start_date = None
            session.end_date = None

            session.start_datetime = session_update.start_datetime
            session.end_datetime = session_update.end_datetime

            await clear_occurrences_for_session(db, session.id)
            session.occurrences = []

        if session_update.session_type == m_club.SessionType.COURSE:
            if (
                not session_update.day_of_week
                or not session_update.start_time
                or not session_update.end_time
                and not session.start_date
            ):
                raise ValueError("Day of week, start time, end time and start date are required for COURSE sessions")

            session.start_datetime = None
            session.end_datetime = None

            session.day_of_week = session_update.day_of_week
            session.start_time = session_update.start_time
            session.end_time = session_update.end_time
            session.start_date = session_update.start_date
            session.end_date = session_update.end_date

            occurrences, _ = refresh_occurrences_for_session(session)
            db.add_all(occurrences)

    if session_type_changed:
        if not details:
            raise ValueError("Provided data does not contain any changes")
        await db.flush()
        return details

    # ~~~~~~~~~~~~~~~~~~ Time ~~~~~~~~~~~~~~~~~ #
    if session_update.start_datetime and session.start_datetime != session_update.start_datetime:
        if (
            not session_update.end_datetime
            and session.end_datetime
            and session_update.start_datetime > session.end_datetime
        ):
            raise ValueError("Start datetime cannot be after end datetime")

        details += f"Start Datetime: {session.start_datetime} -> {session_update.start_datetime}"
        session.start_datetime = session_update.start_datetime

    if session_update.end_datetime and session.end_datetime != session_update.end_datetime:
        if (
            session_update.start_datetime
            and session.start_datetime
            and session_update.end_datetime < session.start_datetime
        ):
            raise ValueError("End datetime cannot be before start datetime")

        details += f"End Datetime: {session.end_datetime} -> {session_update.end_datetime}"
        session.end_datetime = session_update.end_datetime

    if session_update.day_of_week and session.day_of_week != session_update.day_of_week:
        details += f"Day of Week: {session.day_of_week} -> {session_update.day_of_week}"
        session.day_of_week = session_update.day_of_week
        course_time_changed = True

    if session_update.start_time and session.start_time != session_update.start_time:
        if not session_update.end_time and session.end_time and session_update.start_time > session.end_time:
            raise ValueError("Start time cannot be after end time")

        details += f"Start Time: {session.start_time} -> {session_update.start_time}"
        session.start_time = session_update.start_time
        course_time_changed = True

    if session_update.end_time and session.end_time != session_update.end_time:
        if not session_update.start_time and session.start_time and session_update.end_time < session.start_time:
            raise ValueError("End time cannot be before start time")

        details += f"End Time: {session.end_time} -> {session_update.end_time}"
        session.end_time = session_update.end_time
        course_time_changed = True

    if session_update.start_date and session.start_date != session_update.start_date:
        if not session_update.end_date and session.end_date and session_update.start_date > session.end_date:
            raise ValueError("Start date cannot be after end date")

        details += f"Start Date: {session.start_date} -> {session_update.start_date}"
        session.start_date = session_update.start_date
        course_time_changed = True

    if (session_update.end_date and session.end_date != session_update.end_date) or session_update.null_end_date:
        if (
            not session_update.start_date
            and session_update.end_date
            and session.start_date
            and session_update.end_date < session.start_date
        ):
            raise ValueError("End date cannot be before start date")

        details += f"End Date: {session.end_date} -> {session_update.end_date}"
        session.end_date = session_update.end_date
        course_time_changed = True

    if course_time_changed:
        if session_update.refresh_future_occurrences:
            await clear_future_occurrences_for_session(db, session.id)
            occurrences, _ = refresh_occurrences_for_session(session)
            db.add_all(occurrences)
        else:
            await clear_future_occurrences_for_session(db, session.id, only_scheduled=True)
            await db.refresh(session, ["occurrences"])
            occurrences, _ = refresh_occurrences_for_session(session)
            db.add_all(occurrences)

    if not details:
        raise ValueError("Provided data does not contain any changes")

    await db.flush()
    return details


async def delete_session(db: AsyncSession, session: m_club.Session) -> None:
    """Delete a session

    :param db: The database session
    :param session: The session to delete
    """
    session.deleted_at = datetime.datetime.now(tz=datetime.timezone.utc)
    if session.session_type == m_club.SessionType.COURSE:
        await clear_occurrences_for_session(db, session.id)
    await db.flush()


###########################################################################
################################# Program #################################
###########################################################################
async def program_exists(
    db: AsyncSession, club_id: uuid.UUID, program_name: Optional[str] = None, program_id: Optional[uuid.UUID] = None
) -> bool:
    """Check if a program with the given name exists

    :param db: The database session
    :param club_id: The ID of the club
    :param program_name: The name of the program to check
    :param program_id: The ID of the program to check
    :return: True if a program with the given name exists, False otherwise
    """
    conditions = [m_club.Program.club_id == club_id, m_club.Program.deleted_at.is_(None)]
    if program_name:
        conditions.append(m_club.Program.name == program_name)

    if program_id:
        conditions.append(m_club.Program.id == program_id)

    res = await db.execute(
        select(
            exists(
                select(1)
                .select_from(m_club.Program)
                .filter(
                    and_(*conditions),
                )
            )
        )
    )
    return bool(res.scalar())


async def create_program(db: AsyncSession, club_id: uuid.UUID, program: s_club.ProgramCreate) -> m_club.Program:
    """Create a program

    :param db: The database session
    :param club_id: The ID of the club
    :param program: The program to create
    :return: The created program
    """
    categories = None
    if program.categories:
        categories = await get_program_categories(db, program.categories)
        if len(categories) != len(program.categories):
            raise ValueError("Invalid program categories")

    db_program = m_club.Program(
        club_id=club_id,
        name=program.name,
        description=program.description,
        price=program.price,
        currency=program.currency,
        pricing_model=program.pricing_model,
        capacity=program.capacity,
        membership_required=program.membership_required,
        status=program.status.to_internal(),
        categories=categories or [],
    )
    db.add(db_program)

    if program.sessions:
        await create_sessions_for_program(db, program.sessions, program=db_program)
    await db.flush()
    await db.refresh(db_program, ["sessions"])

    return db_program


async def get_authorized_programs(
    db: AsyncSession,
    club_id: uuid.UUID,
    page: int,
    page_size: int,
    user_id: Optional[uuid.UUID] = None,
    search: Optional[str] = None,
    with_details: bool = False,
) -> List[m_club.Program]:
    """Get programs that the user is authorized to view

    :param db: The database session
    :param club_id: The ID of the club
    :param page: The page number
    :param page_size: The number of programs per page
    :param user_id: The ID of the user
    :return: A list of programs
    """
    query_options = [
        joinedload(m_club.Program.categories),
        undefer(m_club.Program.description),
    ]
    conditions = [m_club.Program.club_id == club_id]

    if with_details:
        query_options.append(joinedload(m_club.Program.sessions))
        query_options.append(joinedload(m_club.Program.sessions).joinedload(m_club.Session.address))
        query_options.append(joinedload(m_club.Program.sessions).joinedload(m_club.Session.occurrences))
        query_options.append(joinedload(m_club.Program.memberships_access).load_only(m_club.MembershipAccess.membership_id))

    if user_id:
        conditions.append(
            or_(
                # Public programs
                m_club.Program.status == m_club.ProgramStatus.ACTIVE,
                # Authorized programs for the user
                authorized_read_program_db_condition(user_id, club_id),
            )
        )

    else:
        conditions.append(m_club.Program.status == m_club.ProgramStatus.ACTIVE)

    if search:
        conditions.append(m_club.Program.name.ilike(f"%{search}%"))

    res = await db.execute(
        select(m_club.Program)
        .options(*query_options)
        .filter(and_(*conditions))
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    return list(res.unique().scalars().all())


async def get_program(
    db: AsyncSession,
    club_id: uuid.UUID,
    program_id: uuid.UUID,
    with_details: bool = False,
    with_club: bool = False,
    status: Optional[m_club.ProgramStatus] = None,
) -> m_club.Program:
    """Get a program by ID

    :param db: The database session
    :param club_id: The ID of the club
    :param program_id: The ID of the program
    :param with_details: Whether to load additional details
    :param status: The status of the program
    :return: The program with the given ID
    """
    query_options = [joinedload(m_club.Program.categories), undefer(m_club.Program.description)]
    conditions = [m_club.Program.id == program_id, m_club.Program.club_id == club_id]

    if with_details:
        query_options.append(joinedload(m_club.Program.sessions))
        query_options.append(joinedload(m_club.Program.sessions, m_club.Session.address))
        query_options.append(joinedload(m_club.Program.sessions, m_club.Session.occurrences))
        query_options.append(joinedload(m_club.Program.memberships_access).load_only(m_club.MembershipAccess.membership_id))

    if with_club:
        query_options.append(joinedload(m_club.Program.club))

    if status:
        conditions.append(m_club.Program.status == status)

    res = await db.execute(select(m_club.Program).options(*query_options).filter(and_(*conditions)))
    return res.unique().scalar_one_or_none()


async def get_bookable_programs(db: AsyncSession, program_ids: List[uuid.UUID]) -> List[m_club.Program]:
    """Get bookable programs

    :param db: The database session
    :param program_ids: The IDs of the programs
    :return: A list of programs
    """
    bookings_count_subquery = (
        select(func.count(m_payment.Booking.id))
        .where(m_payment.Booking.session_id == m_club.Session.id)
        .scalar_subquery()
    )

    res = await db.execute(
        select(m_club.Program)
        .join(m_club.Session)
        .filter(
            m_club.Program.status == m_club.ProgramStatus.ACTIVE,
            m_club.Program.pricing_model == m_club.PriceType.PACKAGE,
            m_club.Program.id.in_(program_ids),
            active_sessions_db_condition(),
            m_club.Program.capacity > bookings_count_subquery,
        )
        .options(
            joinedload(m_club.Program.sessions),
            joinedload(m_club.Program.memberships_access),
            joinedload(m_club.Program.club),
            joinedload(m_club.Program.sessions).joinedload(m_club.Session.program),
        )
    )
    return list(res.unique().scalars().all())


async def get_authorized_program(
    db: AsyncSession,
    club_id: uuid.UUID,
    program_id: uuid.UUID,
    user_id: Optional[uuid.UUID] = None,
    with_details: bool = False,
) -> m_club.Program:
    """Get a program that the user is authorized to view

    :param db: The database session
    :param club_id: The ID of the club
    :param program_id: The ID of the program
    :param user_id: The ID of the user
    :param with_details: Whether to load additional details
    :return: The program with the given ID if the user is authorized to view it
    """
    query_options = [
        joinedload(m_club.Program.categories),
        undefer(m_club.Program.description),
    ]

    if with_details:
        query_options.append(joinedload(m_club.Program.sessions))
        query_options.append(joinedload(m_club.Program.sessions, m_club.Session.address))
        query_options.append(joinedload(m_club.Program.sessions, m_club.Session.occurrences))
        query_options.append(joinedload(m_club.Program.memberships_access).load_only(m_club.MembershipAccess.membership_id))

    if user_id:
        query = select(m_club.Program).filter(
            m_club.Program.id == program_id,
            m_club.Program.club_id == club_id,
            or_(
                # Public programs
                m_club.Program.status == m_club.ProgramStatus.ACTIVE,
                # Authorized programs for the user
                authorized_read_program_db_condition(user_id, club_id),
            ),
        )
    else:
        query = select(m_club.Program).filter(
            m_club.Program.id == program_id,
            m_club.Program.club_id == club_id,
            m_club.Program.status == m_club.ProgramStatus.ACTIVE,
        )

    res = await db.execute(query.options(*query_options))
    return res.unique().scalar_one_or_none()


async def search_programs(
    db: AsyncSession, filters: List[ColumnElement], page: int, page_size: int
) -> List[m_club.Program]:
    """Search for programs

    :param db: The database session
    :param filters: The filter criteria for searching programs
    :param page: The page number
    :param page_size: The number of programs per page
    :return: A list of programs that match the filters
    """
    query_options = [joinedload(m_club.Program.categories), undefer(m_club.Program.description)]

    query = select(m_club.Program).filter(*filters)
    res = await db.execute(query.offset((page - 1) * page_size).limit(page_size).options(*query_options))
    return list(res.unique().scalars().all())


async def is_price_model_package(
    db: AsyncSession, program_id: Optional[uuid.UUID] = None, session_id: Optional[uuid.UUID] = None
) -> bool:
    """Check if the price model of a program or session is PACKAGE

    :param db: The database session
    :param program_id: The ID of the program
    :param session_id: The ID of the session
    :return: True if the price model is PACKAGE, False otherwise
    """
    conditions = []
    if program_id:
        conditions.append(m_club.Program.id == program_id)
    if session_id:
        conditions.append(m_club.Session.id == session_id)

    res = await db.execute(
        select(
            exists(
                select(1)
                .select_from(m_club.Program)
                .filter(
                    and_(*conditions),
                    m_club.Program.pricing_model == m_club.PriceType.PACKAGE,
                )
            )
        )
    )
    return bool(res.scalar())


async def get_club_program_ids(db: AsyncSession, club_id: uuid.UUID) -> set[uuid.UUID]:
    """Get all program IDs of a club

    :param db: The database session
    :param club_id: The ID of the club
    :return: A list of program IDs
    """
    res = await db.execute(select(m_club.Program.id).filter(m_club.Program.club_id == club_id))
    return {row[0] for row in res.all()}


async def update_program(
    db: AsyncSession,
    program: m_club.Program,
    program_update: s_club.ProgramUpdate,
) -> str:
    """Update a program

    :param db: The database session
    :param program: The program to update
    :param program_update: The updated program data
    :return: details of the changes made
    """
    details = ""
    price_model_changed = False

    if program_update.name and program.name != program_update.name:
        if await program_exists(db, program.club_id, program_update.name):
            raise ValueError("Program with the same name already exists")

        details += f"Name: {program.name} -> {program_update.name}"
        program.name = program_update.name

    if program_update.description and program.description != program_update.description:
        details += f"Description: {program.description} -> {program_update.description}"
        program.description = program_update.description

    if program_update.price and program.price != program_update.price:
        details += f"Price: {program.price} -> {program_update.price}"
        program.price = program_update.price

    if program_update.currency and program.currency != program_update.currency:
        details += f"Currency: {program.currency} -> {program_update.currency}"
        program.currency = program_update.currency

    if program_update.capacity and program.capacity != program_update.capacity:
        details += f"Capacity: {program.capacity} -> {program_update.capacity}"
        program.capacity = program_update.capacity

    if (
        program_update.membership_required is not None
        and program.membership_required != program_update.membership_required
    ):
        details += f"Membership Required: {program.membership_required} -> {program_update.membership_required}"
        program.membership_required = program_update.membership_required

    if program_update.pricing_model and program.pricing_model != program_update.pricing_model:
        details += f"Pricing Model: {program.pricing_model} -> {program_update.pricing_model}"
        program.pricing_model = program_update.pricing_model
        price_model_changed = True

        # Reset all session prices to 0 if the pricing model is PACKAGE
        if program.pricing_model == m_club.PriceType.PACKAGE:
            for session in program.sessions:
                session.price = None
                session.capacity = None

        # Reset program price and capacity if the pricing model is PER_SESSION
        if program_update.pricing_model == m_club.PriceType.PER_SESSION:
            program.price = None
            program.capacity = None

    if program_update.session_data:
        if program.pricing_model == m_club.PriceType.PACKAGE:
            raise ValueError("Session prices are not allowed for PACKAGE pricing model")

        if price_model_changed and len(program.sessions) != len(program_update.session_data):
            raise ValueError("Length of session prices does not match the number of sessions.")

        program.price = None
        sessions_details = []

        # Update session prices
        for session in program.sessions:
            new_price, new_capacity = program_update.session_data.get(session.id, (None, None))

            session_details = []

            # Check if the session has a price
            if session.price != new_price:
                session_details.append(f"Price: {session.price} -> {new_price}")
                session.price = new_price
            elif price_model_changed:
                raise ValueError(f"Missing price for session {session.id}")

            # Check if the session has a capacity
            if session.capacity != new_capacity:
                session_details.append(f"Capacity: {session.capacity} -> {new_capacity}")
                session.capacity = new_capacity

            elif price_model_changed:
                raise ValueError(f"Missing capacity for session {session.id}")

            if session_details:
                sessions_details.append(f"{session.id} ~ {', '.join(session_details)}")

        if sessions_details:
            details += f"Session Prices: {';'.join(sessions_details)}"

    if program_update.status and program.status != program_update.status.to_internal():
        details += f"Status: {program.status} -> {program_update.status}"
        program.status = program_update.status.to_internal()

    if program_update.categories:
        new_categories = await get_program_categories(db, program_update.categories)
        if len(new_categories) != len(program_update.categories):
            raise ValueError("Invalid program categories")

        program.categories = new_categories
        details += f"Categories: {', '.join([str(category.id) for category in new_categories])}"

    if not details:
        raise ValueError("Provided data does not contain any changes")

    await db.flush()
    return details


async def delete_program(db: AsyncSession, program: m_club.Program) -> None:
    """Delete a program

    :param db: The database session
    :param program: The program to delete
    """
    program.status = m_club.ProgramStatus.DELETED
    program.deleted_at = datetime.datetime.now(tz=datetime.timezone.utc)
    db.add(program)
    await db.flush()


###########################################################################
################################# Sonstiges ###############################
###########################################################################
async def get_program_categories(db: AsyncSession, ids: Optional[List[int]] = None) -> List[m_club.ProgramCategory]:
    """Get all program categories

    :param db: The database session
    :param ids: A list of category ids to filter by
    :return: A list of program categories
    """
    stmt = select(m_club.ProgramCategory).options(joinedload(m_club.ProgramCategory.translations))

    if ids:
        stmt = stmt.filter(m_club.ProgramCategory.id.in_(ids))

    res = await db.execute(stmt)
    return list(res.unique().scalars().all())


###########################################################################
############################## Recurring Task #############################
###########################################################################
async def update_session_occurrences(db: AsyncSession, console: Console) -> bool:
    """Create session occurrences for all programs with recurring sessions"""
    audit_logger = audit_crud.AuditLogger(db)
    audit_logger.sys_info("Updating session occurrences")

    try:
        # Get all sessions with recurring sessions
        res = await db.execute(
            select(m_club.Session)
            .options(joinedload(m_club.Session.occurrences))
            .filter(
                m_club.Session.session_type == m_club.SessionType.COURSE,
                m_club.Session.start_date.isnot(None),
                m_club.Session.end_date.isnot(None),
                m_club.Session.deleted_at.is_(None),
            )
        )

        sessions = res.unique().scalars().all()

        # Generate occurrences for each session 90 days in advance
        today = datetime.date.today()
        new_occurrences = []
        updated_occurrences = 0
        for session in sessions:
            occurrences, updated = refresh_occurrences_for_session(session)
            new_occurrences.extend(occurrences)
            updated_occurrences += updated

        db.add_all(new_occurrences)
        audit_logger.sys_info(f"Added {len(new_occurrences)} new occurrences and updated {updated_occurrences}")
        await db.flush()

        # Remove occurrences that are older than 90 and not changed
        res = await db.execute(
            delete(m_club.SessionOccurrence).filter(
                m_club.SessionOccurrence.occurrence_date < today - datetime.timedelta(days=90),
                m_club.SessionOccurrence.status == m_club.OccurrenceStatus.SCHEDULED,
            )
        )
        num_deleted = res.rowcount
        audit_logger.sys_info(f"Removed {num_deleted} old occurrences")
        await db.commit()

        console.log(
            f"[blue][INFO][/blue]\t\tAdded {len(new_occurrences)} new occurrences and removed {num_deleted} old occurrences"
        )
        return True
    except Exception as e:
        await db.rollback()
        audit_logger.sys_error("Error updating session occurrences", traceback=traceback.format_exc())
        await db.commit()
        console.log("[red][ERROR][/red]\t\tError updating session occurrences")
        console.print_exception()
        return False


async def set_programs_inactive(db: AsyncSession, console: Console) -> bool:
    """Set all programs to inactive if all sessions are in the past"""
    audit_logger = audit_crud.AuditLogger(db)
    audit_logger.sys_info("Setting programs inactive")

    try:
        now = datetime.datetime.now(tz=datetime.timezone.utc)

        # Subquery: Check if there are any sessions that have not yet ended
        session_active = exists().where(
            (m_club.Session.program_id == m_club.Program.id)
            & or_(
                m_club.Session.end_date >= now,
                m_club.Session.end_datetime >= now,
            )
        )

        # UPDATE statement: Set the status to INACTIVE when:
        # - the program is currently active and
        # - there are no future sessions
        stmt = (
            update(m_club.Program)
            .where(m_club.Program.status == m_club.ProgramStatus.ACTIVE, ~session_active)
            .values(status=m_club.ProgramStatus.INACTIVE)
        )

        res = await db.execute(stmt)

        num_updated = res.rowcount
        audit_logger.sys_info(f"Set {num_updated} programs to inactive")
        await db.commit()

        console.log(f"[blue][INFO][/blue]\t\tSet {num_updated} programs to inactive")
        return True
    except Exception as e:
        await db.rollback()
        audit_logger.sys_error("Error setting programs inactive", traceback=traceback.format_exc())
        await db.commit()
        console.log("[red][ERROR][/red]\t\tError setting programs inactive")
        console.print_exception()
        return False
