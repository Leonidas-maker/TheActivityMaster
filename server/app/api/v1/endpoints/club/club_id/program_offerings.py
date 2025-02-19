from fastapi import APIRouter, HTTPException, Depends, Request, Query, Path, Body
from sqlalchemy import or_, ColumnElement
import uuid
from typing import Union, List, Dict, Optional
from decimal import Decimal


from controllers import club as club_controller
from schemas import s_club, s_generic
from models import m_club

from core.generic import EndpointContext
import core.security as core_security

from crud import club as club_crud

from middleware.general import get_endpoint_context
import middleware.auth as auth_middleware

from utils.exceptions import handle_exception

from config.permissions import ClubPermissions

# Router for club sessions endpoints
router = APIRouter()


###########################################################################
################################# Programs ################################
###########################################################################
# ======================================================== #
# ======================== Hybrid ======================== #
# ======================================================== #


@router.get(
    "", response_model=List[s_club.Program], tags=["Club - Program", "Access: Hybrid"], response_model_exclude_none=True
)
async def get_programs_v1(
    club_id: uuid.UUID = Path(..., description="The ID of the club"),
    page: int = Query(1, ge=1, description="The page number"),
    page_size: int = Query(10, ge=1, le=50, description="The number of clubs per page"),
    ep_context: EndpointContext = Depends(get_endpoint_context),
    token_details: core_security.TokenDetails = Depends(auth_middleware.AccessTokenCheckerHybrid()),
):
    try:
        user_id = token_details.user_id if token_details else None
        programs = await club_crud.get_authorized_programs(ep_context.db, club_id, page, page_size, user_id)
        return [s_club.Program.model_validate(program) for program in programs]
    except Exception as e:
        await handle_exception(e, ep_context, "Failed to get programs")


@router.get(
    "/{program_id}",
    response_model=s_club.ProgramDetails,
    tags=["Club - Program", "Access: Hybrid"],
    response_model_exclude_none=True,
)
async def get_program_v1(
    club_id: uuid.UUID = Path(..., description="The ID of the club"),
    program_id: uuid.UUID = Path(..., description="The ID of the program"),
    ep_context: EndpointContext = Depends(get_endpoint_context),
    token_details: core_security.TokenDetails = Depends(auth_middleware.AccessTokenCheckerHybrid()),
):
    """Get a program

    **Note: If the user has the permission to read programs or is a trainee of the program,
    provide the authentication details to view a program with any status.**
    """
    try:
        club_program = await club_controller.get_program(ep_context, token_details, club_id, program_id)
        return s_club.ProgramDetails.model_validate(club_program)
    except Exception as e:
        await handle_exception(e, ep_context, "Failed to get program")


# ======================================================== #
# ======================== Private ======================= #
# ======================================================== #
@router.post("", response_model=s_club.Program, tags=["Club - Program"], response_model_exclude_none=True)
async def create_program_v1(
    club_id: uuid.UUID = Path(..., description="The ID of the club"),
    new_program: s_club.ProgramCreate = Body(..., description="The program values for creation"),
    ep_context: EndpointContext = Depends(get_endpoint_context),
    token_details: core_security.TokenDetails = Depends(
        auth_middleware.AccessTokenChecker(club_permissions=[ClubPermissions.CREATE_PROGRAMS])
    ),
):
    try:
        return await club_controller.create_program(ep_context, token_details, club_id, new_program)
    except Exception as e:
        await handle_exception(e, ep_context, "Failed to create program")


@router.put("/{program_id}", tags=["Club - Program"], response_model_exclude_none=True)
async def update_program_v1(
    club_id: uuid.UUID = Path(..., description="The ID of the club"),
    program_id: uuid.UUID = Path(..., description="The ID of the program"),
    program_update: s_club.ProgramUpdate = Body(..., description="The update values"),
    ep_context: EndpointContext = Depends(get_endpoint_context),
    token_details: core_security.TokenDetails = Depends(
        auth_middleware.AccessTokenChecker(club_permissions=[ClubPermissions.UPDATE_PROGRAMS])
    ),
):
    try:
        return await club_controller.update_program(ep_context, token_details, club_id, program_id, program_update)
    except Exception as e:
        await handle_exception(e, ep_context, "Failed to update program")


@router.delete("/{program_id}", tags=["Club - Program"])
async def delete_program_v1(club_id: uuid.UUID, program_id: uuid.UUID):
    pass


###########################################################################
################################# Sessions ################################
###########################################################################
@router.get("/{program_id}/sessions", tags=["Club - Program - Session"])
async def get_program_sessions_v1(club_id: uuid.UUID, program_id: uuid.UUID):
    pass


@router.post("/{program_id}/sessions", tags=["Club - Program - Session"])
async def create_session_v1(club_id: uuid.UUID, program_id: uuid.UUID):
    pass


@router.get("/{program_id}/sessions/{session_id}", tags=["Club - Program - Session"])
async def get_session_v1(club_id: uuid.UUID, program_id: uuid.UUID, session_id: uuid.UUID):
    pass


@router.put("/{program_id}/sessions/{session_id}", tags=["Club - Program - Session"])
async def update_session_v1(club_id: uuid.UUID, program_id: uuid.UUID, session_id: uuid.UUID):
    pass


@router.delete("/{program_id}/sessions/{session_id}", tags=["Club - Program - Session"])
async def delete_session_v1(club_id: uuid.UUID, program_id: uuid.UUID, session_id: uuid.UUID):
    pass


# ======================================================== #
# =================== SessionOccurrence ================== #
# ======================================================== #
@router.get("/{program_id}/sessions/{session_id}/occurrences", tags=["Club - Program - Session Occurrence"])
async def get_occurrences_v1(club_id: uuid.UUID, session_id: uuid.UUID):
    pass


@router.put(
    "/{program_id}/sessions/{session_id}/occurrences/{occurrence_id}", tags=["Club - Program - Session Occurrence"]
)
async def update_occurrence_v1(club_id: uuid.UUID, session_id: uuid.UUID, occurrence_id: uuid.UUID):
    pass
