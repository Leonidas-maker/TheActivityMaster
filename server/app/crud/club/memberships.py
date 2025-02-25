from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, or_, exists, and_, ColumnElement
from sqlalchemy.inspection import inspect
from sqlalchemy.orm import undefer, joinedload
from typing import List, Tuple, Optional, Dict
import uuid
import datetime
import traceback

from schemas import s_club

from models import m_club

from crud import audit as audit_crud, generic as generic_crud

from config.permissions import ClubPermissions


async def get_user_memberships(db: AsyncSession, user_id: uuid.UUID) -> List[m_club.MembershipSubscription]:
    """
    Retrieve the memberships associated with a specific user.

    :param db: The database session
    :param user_id: The ID of the user whose memberships are to be retrieved
    :return: A list of memberships for the user
    """
    memberships = await db.execute(select(m_club.MembershipSubscription).filter(m_club.MembershipSubscription.user_id == user_id))
    return list(memberships.unique().scalars().all())
