from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, or_
from sqlalchemy.orm import undefer, joinedload, selectinload
from typing import List, Tuple, Optional
import uuid

from schemas import s_club

from models import m_club, m_user, m_generic

import crud.generic as generic_crud, crud.role as role_crud

from core.generic import EndpointContext


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
    await role_crud.create_default_club_roles(db, db_club.id)

    res = await db.execute(
        select(m_club.ClubRole.id).filter(m_club.ClubRole.level == 0, m_club.ClubRole.club_id == db_club.id)
    )
    owner_role_id = res.scalar_one_or_none()

    if not owner_role_id:
        raise ValueError("Club owner role not found")

    print("owner_role_id", owner_role_id)

    db_user_club_role = m_club.UserClubRole(user_id=user_id, club_role_id=owner_role_id)
    db.add(db_user_club_role)

    await db.flush()
    return db_club


async def get_clubs(db: AsyncSession, page: int, page_size: int, city: str) -> List[m_club.Club]:
    """Get all clubs, optionally filtered by city.

    :param db: The database session.
    :param page: The page number.
    :param page_size: The number of clubs per page.
    :param city: The city name to filter by. Wenn leer, werden alle Clubs zurückgegeben.
    :return: Eine Liste von Club-Objekten.
    """
    query_options = [joinedload(m_club.Club.address), undefer(m_club.Club.description)]

    stmt = select(m_club.Club).options(*query_options)

    if city:
        stmt = (
            stmt.join(m_club.Club.address)
            .join(m_generic.Address.postal_code)
            .join(m_generic.PostalCode.city)
            .filter(m_generic.City.name == city)
        )

    stmt = stmt.limit(page_size).offset((page - 1) * page_size)

    res = await db.execute(stmt)
    return list(res.scalars().all())


async def get_club(db: AsyncSession, club_id: uuid.UUID) -> m_club.Club:
    """Get a club by ID

    :param db: The database session
    :param club_id: The ID of the club to get
    :return: The club with the given ID
    """
    res = await db.execute(select(m_club.Club).filter(m_club.Club.id == club_id))
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


async def update_club(
    ep_context: EndpointContext, club_id: uuid.UUID, club_update: s_club.ClubUpdate, user_id: uuid.UUID
) -> m_club.Club:
    """Update a club

    :param ep_context: The endpoint context containing database and logger
    :param club_id: The ID of the club to update
    :param club_update: The updated club data
    :param user_id: The ID of the user updating the club (for audit logging)
    :return: The updated club
    """
    db = ep_context.db
    audit_log = ep_context.audit_logger
    details = ""

    query_options = [joinedload(m_club.Club.address)]
    res = await db.execute(select(m_club.Club).filter(m_club.Club.id == club_id).options(*query_options))
    club = res.unique().scalar_one_or_none()

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
        raise ValueError("No changes detected")

    audit_log.club_updated(user_id, club.id, details)

    await db.flush()
    return club


async def get_club_employees(db: AsyncSession, club_id: uuid.UUID) -> List[m_club.ClubRole]:
    """Get employees of the club

    :param db: The database session
    :param club_id: The ID of the club to get employees for
    :return: A list of UserClubRole associated with the club
    """
    query_options = [
        joinedload(m_club.ClubRole.user_club_roles).joinedload(m_club.UserClubRole.user),
    ]

    res = await db.execute(select(m_club.ClubRole).options(*query_options).filter(m_club.ClubRole.club_id == club_id))
    club_roles = res.unique().scalars().all()
    return list(club_roles)


# TODO - Implement Delete Club workflow
# async def delete_club(db: AsyncSession, club_id: uuid.UUID) -> None:
#     """Delete a club

#     :param db: The database session
#     :param club_id: The ID of the club to delete
#     """
#     await db.execute(delete(m_club.Club).where(m_club.Club.id == club_id))
#     await db.flush()


###########################################################################
################################## Search #################################
###########################################################################
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
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())
