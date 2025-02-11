from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from schemas import s_club

from models import m_club

import crud.generic as generic_crud

async def create_club(db: AsyncSession, user_id, club: s_club.ClubCreate) -> m_club.Club:
    """Create a club

    :param db: The database session
    :param club: The club to create
    :return: The created club
    """
    address = await generic_crud.get_create_address(db, club.address)

    db_club = m_club.Club(
        name=club.name,
        description=club.description,
        address=address
        
    )

    db.add(db_club)

    owner_db = await db.execute(select(m_club.ClubRole).where(m_club.ClubRole.name == "Owner"))
    owner_role = owner_db.unique().scalar_one()

    if not owner_role:
        raise ValueError("Club owner role not found")
    
    db_user_club_role = m_club.UserClubRole(
        user_id=user_id,
        club_role_id=owner_role.id,
        club = db_club
    )

    db.add(db_user_club_role)

    await db.flush()
    return db_club

async def get_club(db: AsyncSession, club_id: int) -> m_club.Club:
    """Get a club by ID

    :param db: The database session
    :param club_id: The ID of the club to get
    :return: The club with the given ID
    """
    res = await db.execute(select(m_club.Club).filter(m_club.Club.id == club_id))
    return res.unique().scalar_one_or_none()


async def delete_club(db: AsyncSession, club_id: int) -> None:
    """Delete a club

    :param db: The database session
    :param club_id: The ID of the club to delete
    """
    await db.execute(delete(m_club.Club).where(m_club.Club.id == club_id))
    await db.flush()
