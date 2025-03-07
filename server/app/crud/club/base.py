from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, or_, exists, and_, ColumnElement, update
from sqlalchemy.orm import undefer, joinedload
from typing import List, Tuple, Optional, Dict
import uuid
import traceback
from rich.console import Console
import datetime
import os

from schemas import s_club

from models import m_club, m_generic, m_user

from crud import role as role_crud, generic as generic_crud, audit as audit_crud

from config.permissions import ClubPermissions
from config.settings import DEFAULT_TIMEZONE, DEBUG, TESTING


###########################################################################
################################### Club ##################################
###########################################################################
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


async def has_club_stripe_account(db: AsyncSession, club_id: uuid.UUID) -> bool:
    """Check if a club has a stripe account

    :param db: The database session
    :param club_id: The ID of the club
    :return: True if the club has a stripe account, False otherwise
    """
    res = await db.execute(
        select(
            exists(
                select(1)
                .select_from(m_club.Club)
                .filter(m_club.Club.id == club_id, m_club.Club.stripe_account_id != None)
            )
        )
    )
    return bool(res.scalar())


async def create_club(db: AsyncSession, user_id: uuid.UUID, club: s_club.ClubCreate) -> m_club.Club:
    """Create a club

    :param db: The database session
    :param club: The club to create
    :return: The created club
    """
    address = await generic_crud.get_create_address(db, club.address)

    db_club = m_club.Club(name=club.name, description=club.description, address=address)
    
    if DEBUG and not TESTING:
        db_club.stripe_account_id = f"acct_{os.urandom(16).hex()}"

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
            .filter(m_generic.City.name == city, m_club.Club.is_deleted == False)
            .order_by(m_club.Club.name)
        )

    stmt = stmt.limit(page_size).offset((page - 1) * page_size)

    res = await db.execute(stmt)
    return list(res.scalars().all())


async def get_user_clubs(db: AsyncSession, user_id: uuid.UUID) -> List[m_club.Club]:
    """Get all clubs for a user

    :param db: The database session
    :param user_id: The ID of the user
    :return: A list of clubs
    """
    query_options = [joinedload(m_club.Club.address), undefer(m_club.Club.description)]

    res = await db.execute(
        select(m_club.Club)
        .join(m_club.Club.club_roles)
        .join(m_club.ClubRole.user_club_roles)
        .filter(m_club.UserClubRole.user_id == user_id)
        .options(*query_options)
    )
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
        .filter(
            or_(
                m_club.Club.name.ilike(search_pattern),
                m_club.Club.description.ilike(search_pattern),
                m_generic.Address.street.ilike(search_pattern),
                m_generic.PostalCode.code.ilike(search_pattern),
                m_generic.City.name.ilike(search_pattern),
                m_generic.State.name.ilike(search_pattern),
                m_generic.Country.name.ilike(search_pattern),
            ),
            m_club.Club.is_deleted == False,
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


async def is_club_deletable(db: AsyncSession, club_id: uuid.UUID) -> bool:
    """Check if a club is deletable

    :param db: The database session
    :param club_id: The ID of the club
    :return: True if the club is deletable, False otherwise
    """
    res = await db.execute(
        select(
            exists(
                select(1)
                .select_from(m_club.Program)
                .filter(m_club.Program.club_id == club_id, m_club.Program.status == m_club.ProgramStatus.ACTIVE)
            )
        )
    )
    return not bool(res.scalar())


async def delete_club(db: AsyncSession, club_id: uuid.UUID) -> None:
    """Mark a club as deleted

    Note: This does not delete the club, but marks it as deleted. After X days, the club will be deleted.

    :param db: The database session
    :param club_id: The ID of the club to close
    """
    await db.execute(update(m_club.Club).where(m_club.Club.id == club_id).values(is_deleted=True))
    await db.flush()


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


async def get_club_employee_by_id(
    db: AsyncSession, club_id: uuid.UUID, user_id: uuid.UUID, with_details: bool = False
) -> m_club.UserClubRole:
    """Get a club employee by ID

    :param db: The database session
    :param club_id: The ID of the club
    :param user_id: The ID of the user
    :return: The user club role
    """
    query_options = [joinedload(m_club.UserClubRole.user), joinedload(m_club.UserClubRole.club_role)]

    if with_details:
        query_options.extend(
            [
                joinedload(m_club.UserClubRole.club_role).undefer(m_club.ClubRole.description),
                joinedload(m_club.UserClubRole.club_role).joinedload(m_club.ClubRole.permissions),
                joinedload(m_club.UserClubRole.club_role).joinedload(m_club.ClubRole.permissions).undefer(
                    m_club.Permission.description
                ),
            ]
        )

    res = await db.execute(
        select(m_club.UserClubRole)
        .options(*query_options)
        .join(m_club.ClubRole)
        .filter(m_club.UserClubRole.user_id == user_id, m_club.ClubRole.club_id == club_id)
    )
    return res.unique().scalar_one_or_none()


# ======================================================== #
# ======================== Trainer ======================= #
# ======================================================== #
async def get_program_assignments(db: AsyncSession, club_id: uuid.UUID, user_id: uuid.UUID) -> List[uuid.UUID]:
    """Get the uuid of the programs assigned to a user

    :param db: The database session
    :param club_id: The ID of the club
    :param user_id: The ID of the user
    :return: A list of program IDs
    """
    res = await db.execute(
        select(m_club.UserTrainer.program_id)
        .join(m_club.Program)
        .filter(m_club.UserTrainer.user_id == user_id, m_club.Program.club_id == club_id)
    )
    return [row[0] for row in res.all()]


async def add_trainer(db: AsyncSession, program_id: uuid.UUID, user_id: uuid.UUID) -> m_club.UserTrainer:
    """Add a trainer to a program

    :param db: The database session
    :param program_id: The ID of the program
    :param user_id: The ID of the user
    :return: The created UserTrainer
    """
    db_user_trainer = m_club.UserTrainer(program_id=program_id, user_id=user_id)
    db.add(db_user_trainer)
    await db.flush()
    return db_user_trainer


async def get_trainers(db: AsyncSession, program_id: uuid.UUID) -> List[m_user.User]:
    """Get trainers of a program

    :param db: The database session
    :param program_id: The ID of the program
    :return: A list of UserTrainer associated with the program
    """
    res = await db.execute(
        select(m_user.User).join(m_club.UserTrainer).filter(m_club.UserTrainer.program_id == program_id)
    )
    return list(res.scalars().all())


async def remove_trainer(db: AsyncSession, program_id: uuid.UUID, user_id: uuid.UUID) -> None:
    """Remove a trainer from a program

    :param db: The database session
    :param program_id: The ID of the program
    :param user_id: The ID of the user
    """
    await db.execute(
        delete(m_club.UserTrainer).filter(
            m_club.UserTrainer.program_id == program_id, m_club.UserTrainer.user_id == user_id
        )
    )
    await db.flush()


###########################################################################
############################## Recurring Task #############################
###########################################################################
async def delete_marked_clubs(db: AsyncSession, console: Console) -> bool:
    """Delete clubs that have been marked as deleted"""
    audit_logger = audit_crud.AuditLogger(db)
    audit_logger.sys_info("Removing old clubs")
    try:
        res = await db.execute(
            delete(m_club.Club).filter(
                m_club.Club.is_deleted == True,
                m_club.Club.updated_at < datetime.datetime.now(tz=DEFAULT_TIMEZONE) - datetime.timedelta(days=1095),
            )
        )

        num_deleted = res.rowcount
        audit_logger.sys_info(f"Removed {num_deleted} old clubs")
        await db.commit()

        console.log(f"[blue][INFO][/blue]\t\tRemoved {num_deleted} old clubs")
        return True
    except Exception as e:
        await db.rollback()
        audit_logger.sys_error("Error removing old clubs", traceback=traceback.format_exc())
        await db.commit()
        console.log("[red][ERROR][/red]\t\tError removing old clubs")
        console.print_exception()
        return False
