from fastapi import HTTPException
from typing import Tuple
import uuid
from sqlalchemy import select, delete
import jwt
import datetime
from typing import List, Union
import traceback

from config.settings import DEBUG, DEFAULT_TIMEZONE

from models import m_audit, m_user, m_club
from schemas import s_club

from crud import audit as audit_crud, verification as verification_crud, club as club_crud

from core.generic import EndpointContext
import core.security as core_security

async def create_club(
    ep_context: EndpointContext,
    token_details: core_security.TokenDetails,
    club_create: s_club.ClubCreate
) -> m_club.Club:
    db = ep_context.db
    audit_log = ep_context.audit_logger
    user_id = token_details.user_id

    if not verification_crud.is_user_identity_verified(db, user_id):
        raise HTTPException(status_code=403, detail="User identity not verified")
    
    club = await club_crud.create_club(db, user_id, club_create)

    audit_log.club_created(user_id, club.id)
    await db.commit()
    return club