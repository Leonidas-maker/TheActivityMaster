from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, or_
from sqlalchemy.orm import undefer, joinedload, selectinload
from typing import List, Tuple, Optional

import uuid

from schemas import s_club

from models import m_club, m_user, m_generic

import crud.generic as generic_crud


async def create_club(db: AsyncSession, user_id: uuid.UUID, club: s_club.ClubCreate) -> m_club.Club:
    """Create a club

    :param db: The database session
    :param club: The club to create
    :return: The created club
    """
    address = await generic_crud.get_create_address(db, club.address)

    db_club = m_club.Club(name=club.name, description=club.description, address=address)

    db.add(db_club)

    owner_db = await db.execute(select(m_club.ClubRole).where(m_club.ClubRole.name == "Owner"))
    owner_role = owner_db.unique().scalar_one()

    if not owner_role:
        raise ValueError("Club owner role not found")

    db_user_club_role = m_club.UserClubRole(user_id=user_id, club_role_id=owner_role.id, club=db_club)

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
    query_options = [
        joinedload(m_club.Club.address),
        joinedload(m_club.Club.user_club_roles).joinedload(m_club.UserClubRole.user),
        joinedload(m_club.Club.user_club_roles).joinedload(m_club.UserClubRole.club_role),
    ]

    res = await db.execute(
        select(m_club.Club)
        .join(m_club.Club.user_club_roles)
        .join(m_club.UserClubRole.club_role)
        .options(*query_options)
        .filter(m_club.Club.id == club_id, m_club.UserClubRole.club_role.has(name="Owner"))
    )
    club = res.unique().scalar_one_or_none()
    return club


async def get_club_employees(db: AsyncSession, club_id: uuid.UUID) -> Optional[List[m_club.UserClubRole]]:
    query_options = [
        joinedload(m_club.Club.address),
        joinedload(m_club.Club.user_club_roles).joinedload(m_club.UserClubRole.user),
        joinedload(m_club.Club.user_club_roles).joinedload(m_club.UserClubRole.club_role),
    ]

    res = await db.execute(
        select(m_club.Club)
        .join(m_club.Club.user_club_roles)
        .join(m_club.UserClubRole.club_role)
        .options(*query_options)
        .filter(m_club.Club.id == club_id)
    )
    club = res.unique().scalar_one_or_none()
    return club.user_club_roles if club else []


# TODO - Implement Delete Club workflow
# async def delete_club(db: AsyncSession, club_id: uuid.UUID) -> None:
#     """Delete a club

#     :param db: The database session
#     :param club_id: The ID of the club to delete
#     """
#     await db.execute(delete(m_club.Club).where(m_club.Club.id == club_id))
#     await db.flush()


###########################################################################
################################## Roles ##################################
###########################################################################


###########################################################################
################################## Search #################################
###########################################################################
async def search_clubs(
    db: AsyncSession, query: str, page: int = 1, page_size: int = 10
) -> List[m_club.Club]:
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