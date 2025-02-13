from fastapi import HTTPException
from typing import Tuple
import uuid
from sqlalchemy import select, delete
import jwt
import datetime
from typing import List, Union, Optional
import traceback
import time

from config.settings import DEBUG, DEFAULT_TIMEZONE
from config.club import ClubPermissions

from models import m_audit, m_user, m_club
from schemas import s_club, s_generic

from crud import audit as audit_crud, verification as verification_crud, club as club_crud, user as user_crud

from core.generic import EndpointContext
import core.security as core_security

async def create_club(
    ep_context: EndpointContext, token_details: core_security.TokenDetails, club_create: s_club.ClubCreate
) -> s_club.Club:
    """Create a club

    :param ep_context: The endpoint context containing database and logger
    :param token_details: The token details of the authenticated user
    :param club_create: The data to create a new club
    :raises HTTPException: If the user identity is not verified
    :return: The created club object
    """
    db = ep_context.db
    audit_log = ep_context.audit_logger
    user_id = token_details.user_id

    if not await verification_crud.is_user_identity_verified(db, user_id) and not await user_crud.is_user_elevated(
        db, user_id
    ):
        raise HTTPException(status_code=403, detail="User identity not verified")

    club = await club_crud.create_club(db, user_id, club_create)

    audit_log.club_created(user_id, club.id)

    response = s_club.Club(
        id=club.id,
        name=club.name,
        description=str(club.description),
        address=s_generic.Address(**club.address.get_as_dict()),
    )

    await db.commit()
    return response


async def get_club(
    ep_context: EndpointContext, club_id: uuid.UUID, 
) -> m_user.Club:
    """Get a club by ID

    :param ep_context: The endpoint context containing database and logger
    :param token_details: The token details of the authenticated user
    :param club_id: The ID of the club to get
    :raises HTTPException: If the user is not a member of the club
    :return: The club with the given ID
    """
    db = ep_context.db  
    club = await club_crud.get_club_with_owners(db, club_id)

    if not club:
        raise HTTPException(status_code=404, detail="Club not found")

    return club

