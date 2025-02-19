from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, or_, exists, and_, union, ColumnElement
from sqlalchemy.orm import undefer, joinedload, selectinload
from typing import List, Tuple, Optional
import uuid
from decimal import Decimal

from schemas import s_club

from models import m_club, m_user, m_generic

import crud.generic as generic_crud, crud.role as role_crud

from core.generic import EndpointContext

from config.permissions import ClubPermissions


async def club_exists(db: AsyncSession, club_name: Optional[str] = None, club_id: Optional[uuid.UUID] = None) -> bool:
    """Check if a club with the given name exists

    :param db: The database session
    :param club_name: The name of the club to check
    :param club_id: The ID of the club to check
    :return: True if a club with the given name exists, False otherwise
    """
    if not club_name and not club_id:
        raise ValueError("Club name or ID is required")

    conditions = []
    if club_name:
        conditions.append(m_club.Club.name == club_name)

    if club_id:
        conditions.append(m_club.Club.id == club_id)

    res = await db.execute(select(exists(select(1).select_from(m_club.Club).filter(*conditions))))
    return bool(res.scalar())


async def create_club(db: AsyncSession, user_id: uuid.UUID, club: s_club.ClubCreate) -> m_club.Club:
    """Create a club

    :param db: The database session
    :param club: The club to create
    :return: The created club
    """
    address = await generic_crud.get_create_address(db, club.address)

    db_club = m_club.Club(name=club.name, description=club.description, address=address)

    db.add(db_club)
    await db.flush()
    default_roles = await role_crud.create_default_club_roles(db, db_club.id)

    owner_role = None
    for role in default_roles:
        if role.level == 0:
            owner_role = role
            break

    if not owner_role:
        raise ValueError("Club owner role not found")

    db_user_club_role = m_club.UserClubRole(user_id=user_id, club_role=owner_role)
    db.add(db_user_club_role)

    await db.flush()
    return db_club


async def get_clubs(db: AsyncSession, page: int, page_size: int, city: str) -> List[m_club.Club]:
    """Get all clubs, optionally filtered by city.

    :param db: The database session.
    :param page: The page number.
    :param page_size: The number of clubs per page.
    :param city: The city name to filter by. If None, all clubs are returned.
    :return: A list of clubs.
    """
    query_options = [joinedload(m_club.Club.address), undefer(m_club.Club.description)]

    stmt = select(m_club.Club).options(*query_options)

    if city:
        stmt = (
            stmt.join(m_club.Club.address)
            .join(m_generic.Address.postal_code)
            .join(m_generic.PostalCode.city)
            .filter(m_generic.City.name == city)
            .order_by(m_club.Club.name)
        )

    stmt = stmt.limit(page_size).offset((page - 1) * page_size)

    res = await db.execute(stmt)
    return list(res.scalars().all())


async def get_club(db: AsyncSession, club_id: uuid.UUID, with_details: bool = False) -> m_club.Club:
    """Get a club by ID
    :param db: The database session
    :param club_id: The ID of the club to get
    :param with_details: Whether to load additional details
    :return: The club with the given ID
    """
    query_options = []
    if with_details:
        query_options = [joinedload(m_club.Club.address), undefer(m_club.Club.description)]

    res = await db.execute(select(m_club.Club).filter(m_club.Club.id == club_id).options(*query_options))
    return res.unique().scalar_one_or_none()


async def get_club_with_owners(db: AsyncSession, club_id: uuid.UUID) -> m_club.Club:
    """Get a club by ID with its owners

    :param db: The database session
    :param club_id: The ID of the club to get
    :return: The club with the given ID
    """
    query_options = [
        joinedload(m_club.Club.address),
        joinedload(m_club.Club.club_roles)
        .joinedload(m_club.ClubRole.user_club_roles)
        .joinedload(m_club.UserClubRole.user),
    ]

    res = await db.execute(
        select(m_club.Club)
        .join(m_club.Club.club_roles)
        .join(m_club.ClubRole.user_club_roles)
        .options(*query_options)
        .filter(m_club.Club.id == club_id, m_club.ClubRole.level == 0)
    )
    club = res.unique().scalar_one_or_none()
    return club


async def search_clubs(db: AsyncSession, query: str, page: int = 1, page_size: int = 10) -> List[m_club.Club]:
    """Search for clubs by name, description, address, postal code, city, state, or country.

    :param db: The database session
    :param query: The search query
    :param page: The page number, defaults to 1
    :param page_size: The number of clubs per page, defaults to 10
    :return: A list of clubs matching the search query
    """

    search_pattern = f"%{query}%"
    options = [joinedload(m_club.Club.address), undefer(m_club.Club.description)]
    stmt = (
        select(m_club.Club)
        .options(*options)
        .join(m_generic.Address, m_club.Club.address_id == m_generic.Address.id)
        .join(m_generic.PostalCode, m_generic.Address.postal_code_id == m_generic.PostalCode.id)
        .join(m_generic.City, m_generic.PostalCode.city_id == m_generic.City.id)
        .join(m_generic.State, m_generic.City.state_id == m_generic.State.id)
        .join(m_generic.Country, m_generic.State.country_id == m_generic.Country.id)
        .where(
            or_(
                m_club.Club.name.ilike(search_pattern),
                m_club.Club.description.ilike(search_pattern),
                m_generic.Address.street.ilike(search_pattern),
                m_generic.PostalCode.code.ilike(search_pattern),
                m_generic.City.name.ilike(search_pattern),
                m_generic.State.name.ilike(search_pattern),
                m_generic.Country.name.ilike(search_pattern),
            )
        )
        .limit(page_size)
        .offset((page - 1) * page_size)
        .order_by(m_club.Club.name)
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def update_club(db: AsyncSession, club: m_club.Club, club_update: s_club.ClubUpdate) -> str:
    """Update a club

    :param db: The database session
    :param club_id: The ID of the club to update
    :param club_update: The updated club data
    :return: details of the changes made
    """
    details = ""

    if not club:
        raise ValueError("Club not found")

    if club_update.name and club.name != club_update.name:
        details += f"Name: {club.name} -> {club_update.name}"
        club.name = club_update.name

    if club_update.description and club.description != club_update.description:
        details += f"; Changed description"
        club.description = club_update.description  # type: ignore

    if club_update.address:
        new_address = await generic_crud.get_create_address(db, club_update.address)
        if club.address_id != new_address.id:
            details += f"; Address: {club.address_id} -> {new_address.id}"
            club.address = new_address

    if not details:
        raise ValueError("Provided data does not contain any changes")

    await db.flush()
    return details


# TODO - Implement Delete Club workflow
# async def delete_club(db: AsyncSession, club_id: uuid.UUID) -> None:
#     """Delete a club

#     :param db: The database session
#     :param club_id: The ID of the club to delete
#     """
#     await db.execute(delete(m_club.Club).where(m_club.Club.id == club_id))
#     await db.flush()


###########################################################################
################################# Employee ################################
###########################################################################
async def get_club_employees(db: AsyncSession, club_id: uuid.UUID) -> List[m_club.ClubRole]:
    """Get employees of the club

    :param db: The database session
    :param club_id: The ID of the club to get employees for
    :return: A list of UserClubRole associated with the club
    """
    query_options = [
        joinedload(m_club.ClubRole.user_club_roles).joinedload(m_club.UserClubRole.user),
    ]

    res = await db.execute(
        select(m_club.ClubRole)
        .options(*query_options)
        .filter(m_club.ClubRole.club_id == club_id)
        .order_by(m_club.ClubRole.level)
    )
    club_roles = res.unique().scalars().all()
    return list(club_roles)


async def get_club_employee_by_id(db: AsyncSession, club_id: uuid.UUID, user_id: uuid.UUID) -> m_club.UserClubRole:
    """Get a club employee by ID

    :param db: The database session
    :param club_id: The ID of the club
    :param user_id: The ID of the user
    :return: The user club role
    """
    query_options = [joinedload(m_club.UserClubRole.user), joinedload(m_club.UserClubRole.club_role)]

    res = await db.execute(
        select(m_club.UserClubRole)
        .options(*query_options)
        .join(m_club.ClubRole)
        .filter(m_club.UserClubRole.user_id == user_id, m_club.ClubRole.club_id == club_id)
    )
    return res.unique().scalar_one_or_none()


async def could_user_read_private_program(db, user_id: uuid.UUID, club_id: uuid.UUID, program_id: uuid.UUID) -> bool:
    stmt = (
        select(1)
        .select_from(m_club.UserClubRole)
        .join(m_club.ClubRole, m_club.UserClubRole.club_role_id == m_club.ClubRole.id)
        .join(m_club.ClubRolePermission, m_club.ClubRole.id == m_club.ClubRolePermission.role_id)
        .join(m_club.Permission, m_club.ClubRolePermission.permission_id == m_club.Permission.id)
        .outerjoin(
            m_club.UserTrainer,
            and_(
                m_club.UserTrainer.user_id == m_club.UserClubRole.user_id,
                m_club.UserTrainer.program_id == program_id,
            ),
        )
        .where(
            and_(
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
    )
    result = await db.execute(select(exists(stmt)))
    return bool(result.scalar())


###########################################################################
################################# Session #################################
###########################################################################
async def session_exists(db: AsyncSession, program_id: uuid.UUID, session: s_club.SessionCreate) -> bool:
    """Check if a session already exists

    :param db: The database session
    :param sessions: The session to check
    :return: True if the session already exists, False otherwise
    """
    res = await db.execute(
        select(
            exists(
                select(1)
                .select_from(m_club.Session)
                .filter(
                    m_club.Session.program_id == program_id,
                    or_(
                        and_(
                            m_club.Session.start_datetime == session.start_datetime,
                            m_club.Session.end_datetime == session.end_datetime,
                        ),
                        and_(
                            m_club.Session.start_date == session.start_date,
                            m_club.Session.end_date == session.end_date,
                            m_club.Session.day_of_week == session.day_of_week,
                            m_club.Session.start_time == session.start_time,
                            m_club.Session.end_time == session.end_time,
                        ),
                    ),
                )
            )
        )
    )
    return bool(res.scalar())


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
        membership_required=session.membership_required,
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

    await db.flush()
    return db_session


async def create_sessions_for_program(
    db: AsyncSession,
    sessions: List[s_club.SessionBase],
    program_id: Optional[uuid.UUID] = None,
    program: Optional[m_club.Program] = None,
) -> List[m_club.Session]:
    """Create multiple sessions for a program by providing a list of pydantic "SessionBase" objects

    :param db: The database session
    :param program_id: The ID of the program
    :param sessions: The sessions to create
    :return: The created sessions
    """
    if not program and not program_id:
        raise ValueError("Program or program_id is required")

    if program:
        db_sessions = [m_club.Session(program=program, **session.model_dump()) for session in sessions]
    else:
        db_sessions = [m_club.Session(program_id=program_id, **session.model_dump()) for session in sessions]
    db.add_all(db_sessions)
    await db.flush()
    return db_sessions


async def get_sessions(db: AsyncSession, program_id: uuid.UUID) -> List[m_club.Session]:
    """Get all sessions of a program

    :param db: The database session
    :param program_id: The ID of the program
    :return: A list of sessions
    """
    res = await db.execute(select(m_club.Session).filter(m_club.Session.program_id == program_id))
    return list(res.scalars().all())


###########################################################################
################################# Program #################################
###########################################################################
async def program_exists(db: AsyncSession, club_id: uuid.UUID, program_name: str) -> bool:
    """Check if a program with the given name exists

    :param db: The database session
    :param club_id: The ID of the club
    :param program_name: The name of the program to check
    :return: True if a program with the given name exists, False otherwise
    """
    res = await db.execute(
        select(
            exists(
                select(1)
                .select_from(m_club.Program)
                .where(m_club.Program.club_id == club_id, m_club.Program.name == program_name)
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
    if len(program.sessions) == 0:
        raise ValueError("At least one session is required")

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
        status=program.status,
        categories=categories or [],
    )
    db.add(db_program)

    sessions = await create_sessions_for_program(db, program.sessions, program=db_program)

    await db.flush()
    db_program.sessions = sessions

    return db_program


async def get_authorized_programs(
    db: AsyncSession,
    club_id: uuid.UUID,
    page: int,
    page_size: int,
    user_id: Optional[uuid.UUID] = None,
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

    if user_id:
        query = select(m_club.Program).filter(
            m_club.Program.club_id == club_id,
            or_(
                # Public programs
                m_club.Program.status == m_club.ProgramStatus.ACTIVE,
                # Authorized programs for the user
                m_club.Program.id.in_(
                    select(m_club.Program.id)
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
                ),
            ),
        )
    else:
        query = select(m_club.Program).filter(
            m_club.Program.club_id == club_id, m_club.Program.status == m_club.ProgramStatus.ACTIVE
        )

    res = await db.execute(query.options(*query_options).offset((page - 1) * page_size).limit(page_size))
    return list(res.unique().scalars().all())


async def get_program(
    db: AsyncSession,
    club_id: uuid.UUID,
    program_id: uuid.UUID,
    with_details: bool = False,
    status: Optional[m_club.ProgramStatus] = None,
) -> m_club.Program:
    """Get a program by ID

    :param db: The database session
    :param club_id: The ID of the club
    :param program_id: The ID of the program
    :return: The program with the given ID
    """
    query_options = [joinedload(m_club.Program.categories), undefer(m_club.Program.description)]
    conditions = [m_club.Program.id == program_id, m_club.Program.club_id == club_id]

    if with_details:
        query_options.append(joinedload(m_club.Program.sessions))

    if status:
        conditions.append(m_club.Program.status == status)

    res = await db.execute(select(m_club.Program).options(*query_options).filter(and_(*conditions)))
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

    if program_update.pricing_model and program.pricing_model != program_update.pricing_model:
        details += f"Pricing Model: {program.pricing_model} -> {program_update.pricing_model}"
        program.pricing_model = program_update.pricing_model
        price_model_changed = True

        # Reset all session prices to 0 if the pricing model is PACKAGE
        if program.pricing_model == m_club.PriceType.PACKAGE:
            for session in program.sessions:
                session.price = Decimal(0)

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

    if program_update.status and program.status != program_update.status:
        details += f"Status: {program.status} -> {program_update.status}"
        program.status = program_update.status

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


###########################################################################
################################# Sontiges ################################
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
