from fastapi import APIRouter, HTTPException, Depends, Request, Query, Path, Body
from sqlalchemy import or_, ColumnElement
import uuid
from typing import Union, List, Dict, Optional
from decimal import Decimal
from fastapi_cache.decorator import cache


from controllers import club as club_controller
from schemas import s_club, s_generic
from models import m_club

from core.generic import EndpointContext
import core.security as core_security

from crud import club as club_crud

from middleware.general import get_endpoint_context
import middleware.auth as auth_middleware

from utils.exceptions import handle_exception
from utils.cache_keybuilder import request_key_builder

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
    page_size: int = Query(10, ge=1, le=50, description="The number of items per page"),
    search_query: Optional[str] = Query(None, description="Search query"),
    ep_context: EndpointContext = Depends(get_endpoint_context),
    token_details: core_security.TokenDetails = Depends(auth_middleware.AccessTokenCheckerHybrid()),
):
    """Get programs of a club

    **Note: If the user has the permission to read programs or is a trainee of the program,
    provide the authentication details to view a program with any status.**
    """
    try:
        user_id = token_details.user_id if token_details else None
        programs = await club_crud.get_authorized_programs(
            ep_context.db, club_id, page, page_size, user_id, search_query
        )
        return [s_club.Program.model_validate(program) for program in programs]
    except Exception as e:
        await handle_exception(e, ep_context, "Failed to get programs")

@router.get(
    "/details",
    response_model=List[s_club.ProgramDetails],
    tags=["Club - Program", "Access: Hybrid"],
    response_model_exclude_none=True,
)
async def get_programs_details_v1(
    club_id: uuid.UUID = Path(..., description="The ID of the club"),
    page: int = Query(1, ge=1, description="The page number"),
    page_size: int = Query(10, ge=1, le=50, description="The number of items per page"),
    search_query: Optional[str] = Query(None, description="Search query"),
    ep_context: EndpointContext = Depends(get_endpoint_context),
    token_details: core_security.TokenDetails = Depends(auth_middleware.AccessTokenCheckerHybrid()),
):
    """Get programs of a club with details

    **Note: If the user has the permission to read programs or is a trainee of the program,
    provide the authentication details to view a program with any status.**
    """
    try:
        user_id = token_details.user_id if token_details else None
        programs = await club_crud.get_authorized_programs(
            ep_context.db, club_id, page, page_size, user_id, search_query, with_details=True
        )
        return [s_club.ProgramDetails.model_validate(program) for program in programs]
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
        user_id = token_details.user_id if token_details else None
        program = await club_crud.get_authorized_program(ep_context.db, club_id, program_id, user_id, with_details=True)

        if not program:
            raise HTTPException(status_code=404, detail="Program not found")

        return s_club.ProgramDetails.model_validate(program)
    except Exception as e:
        await handle_exception(e, ep_context, "Failed to get program")


# ======================================================== #
# ======================== Private ======================= #
# ======================================================== #
@router.post("", response_model=s_club.Program, tags=["Club - Program"], response_model_exclude_none=True)
async def create_program_v1(
    club_id: uuid.UUID = Path(..., description="The ID of the club"),
    new_program: s_club.ProgramCreate = Body(...),
    ep_context: EndpointContext = Depends(get_endpoint_context),
    token_details: core_security.TokenDetails = Depends(
        auth_middleware.AccessTokenChecker(club_permissions=[ClubPermissions.CREATE_PROGRAMS])
    ),
):
    try:
        return await club_controller.create_program(ep_context, token_details, club_id, new_program)
    except Exception as e:
        await handle_exception(e, ep_context, "Failed to create program")


@router.put(
    "/{program_id}", response_model=s_club.ProgramDetails, tags=["Club - Program"], response_model_exclude_none=True
)
async def update_program_v1(
    club_id: uuid.UUID = Path(..., description="The ID of the club"),
    program_id: uuid.UUID = Path(..., description="The ID of the program"),
    program_update: s_club.ProgramUpdate = Body(...),
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
async def delete_program_v1(
    club_id: uuid.UUID = Path(..., description="The ID of the club"),
    program_id: uuid.UUID = Path(..., description="The ID of the program"),
    force: Optional[bool] = Query(False, description="Force delete the program"),
    ep_context: EndpointContext = Depends(get_endpoint_context),
    token_details: core_security.TokenDetails = Depends(
        auth_middleware.AccessTokenChecker(club_permissions=[ClubPermissions.DELETE_PROGRAMS])
    ),
):
    try:
        await club_controller.delete_program(ep_context, token_details, club_id, program_id, force)
        return {"message": "Program deleted successfully."}
    except Exception as e:
        await handle_exception(e, ep_context, "Failed to delete program")


###########################################################################
################################# Sessions ################################
###########################################################################
# ======================================================== #
# ======================== Hybrid ======================== #
# ======================================================== #
@router.get(
    "/{program_id}/sessions",
    response_model=List[s_club.Session],
    tags=["Club - Program - Session", "Access: Hybrid"],
    response_model_exclude_none=True,
)
async def get_sessions_v1(
    club_id: uuid.UUID = Path(..., description="The ID of the club"),
    program_id: uuid.UUID = Path(..., description="The ID of the program"),
    ep_context: EndpointContext = Depends(get_endpoint_context),
    token_details: core_security.TokenDetails = Depends(auth_middleware.AccessTokenCheckerHybrid()),
):
    """Get sessions of a program

    **Note: If the user has the permission to read programs or is a trainee of the program,
    provide the authentication details to view the sessions of a program with any status.**
    """
    try:
        user_id = token_details.user_id if token_details else None
        program = await club_crud.get_authorized_program(ep_context.db, club_id, program_id, user_id, with_details=True)
        if not program:
            raise HTTPException(status_code=404, detail="Program not found")

        return [s_club.Session.model_validate(session) for session in program.sessions]
    except Exception as e:
        await handle_exception(e, ep_context, "Failed to get sessions")


# ======================================================== #
# ======================== Private ======================= #
# ======================================================== #
@router.post(
    "/{program_id}/sessions",
    response_model=s_club.Session,
    tags=["Club - Program - Session"],
    response_model_exclude_none=True,
)
async def create_session_v1(
    club_id: uuid.UUID = Path(..., description="The ID of the club"),
    program_id: uuid.UUID = Path(..., description="The ID of the program"),
    new_session: s_club.SessionCreate = Body(...),
    ep_context: EndpointContext = Depends(get_endpoint_context),
    token_details: core_security.TokenDetails = Depends(
        auth_middleware.AccessTokenChecker(club_permissions=[ClubPermissions.UPDATE_PROGRAMS])
    ),
):
    try:
        return await club_controller.create_session(ep_context, token_details, club_id, program_id, new_session)
    except Exception as e:
        await handle_exception(e, ep_context, "Failed to create session")


@router.put(
    "/{program_id}/sessions/{session_id}",
    response_model=s_club.Session,
    tags=["Club - Program - Session"],
    response_model_exclude_none=True,
)
async def update_session_v1(
    club_id: uuid.UUID = Path(..., description="The ID of the club"),
    program_id: uuid.UUID = Path(..., description="The ID of the program"),
    session_id: uuid.UUID = Path(..., description="The ID of the session"),
    session_update: s_club.SessionUpdate = Body(...),
    ep_context: EndpointContext = Depends(get_endpoint_context),
    token_details: core_security.TokenDetails = Depends(
        auth_middleware.AccessTokenChecker(club_permissions=[ClubPermissions.UPDATE_PROGRAMS])
    ),
):
    """Update a session"""
    try:
        return await club_controller.update_session(
            ep_context, token_details, club_id, program_id, session_id, session_update
        )
    except Exception as e:
        await handle_exception(e, ep_context, "Failed to update session")


@router.delete(
    "/{program_id}/sessions/{session_id}", response_model=s_generic.MessageResponse, tags=["Club - Program - Session"]
)
async def delete_session_v1(
    club_id: uuid.UUID = Path(..., description="The ID of the club"),
    program_id: uuid.UUID = Path(..., description="The ID of the program"),
    session_id: uuid.UUID = Path(..., description="The ID of the session"),
    ep_context: EndpointContext = Depends(get_endpoint_context),
    token_details: core_security.TokenDetails = Depends(
        auth_middleware.AccessTokenChecker(club_permissions=[ClubPermissions.UPDATE_PROGRAMS])
    ),
):
    try:
        await club_controller.delete_session(ep_context, token_details, club_id, program_id, session_id)
        return {"message": "Session deleted successfully."}
    except Exception as e:
        await handle_exception(e, ep_context, "Failed to delete session")


# ======================================================== #
# =================== SessionOccurrence ================== #
# ======================================================== #
@router.put(
    "/{program_id}/sessions/{session_id}/occurrences/reschedule",
    response_model=s_generic.MessageResponse,
    tags=["Club - Program - Session Occurrence"],
)
async def reschedule_occurrences_v1(
    club_id: uuid.UUID = Path(..., description="The ID of the club"),
    program_id: uuid.UUID = Path(..., description="The ID of the program"),
    session_id: uuid.UUID = Path(..., description="The ID of the session"),
    reschedule_data: List[s_club.SessionReschedule] = Body(...),
    ep_context: EndpointContext = Depends(get_endpoint_context),
    token_details: core_security.TokenDetails = Depends(
        auth_middleware.AccessTokenChecker(club_permissions=[ClubPermissions.UPDATE_PROGRAMS])
    ),
):
    try:
        await club_controller.reschedule_session_occurrences(
            ep_context, token_details, club_id, program_id, session_id, reschedule_data
        )
        return {"message": "Occurrence rescheduled successfully."}
    except Exception as e:
        await handle_exception(e, ep_context, "Failed to get occurrences")


@router.put(
    "/{program_id}/sessions/{session_id}/occurrences/reinstate",
    tags=["Club - Program - Session Occurrence"],
)
async def reinstate_occurrences_v1(
    club_id: uuid.UUID = Path(..., description="The ID of the club"),
    program_id: uuid.UUID = Path(..., description="The ID of the program"),
    session_id: uuid.UUID = Path(..., description="The ID of the session"),
    occurrences_reinstate: List[s_club.SessionReinstate] = Body(...),
    ep_context: EndpointContext = Depends(get_endpoint_context),
    token_details: core_security.TokenDetails = Depends(
        auth_middleware.AccessTokenChecker(club_permissions=[ClubPermissions.UPDATE_PROGRAMS])
    ),
):
    try:
        await club_controller.reinstate_session_occurrences(
            ep_context, token_details, club_id, program_id, session_id, occurrences_reinstate
        )
        return {"message": "Occurrences reinstated successfully."}
    except Exception as e:
        await handle_exception(e, ep_context, "Failed to reinstate occurrences")


@router.delete(
    "/{program_id}/sessions/{session_id}/occurrences/{occurrence_id}",
    tags=["Club - Program - Session Occurrence"],
)
async def cancel_occurrence_v1(
    club_id: uuid.UUID = Path(..., description="The ID of the club"),
    program_id: uuid.UUID = Path(..., description="The ID of the program"),
    session_id: uuid.UUID = Path(..., description="The ID of the session"),
    occurrence_id: uuid.UUID = Path(..., description="The ID of the occurrence"),
    note: Optional[str] = Body(None, description="The reason for deletion"),
    ep_context: EndpointContext = Depends(get_endpoint_context),
    token_details: core_security.TokenDetails = Depends(
        auth_middleware.AccessTokenChecker(club_permissions=[ClubPermissions.UPDATE_PROGRAMS])
    ),
):
    try:
        await club_controller.cancel_session_occurrences(
            ep_context, token_details, club_id, program_id, session_id, occurrence_id, note
        )
        return {"message": "Occurrence cancelled successfully."}
    except Exception as e:
        await handle_exception(e, ep_context, "Failed to cancel occurrence")


###########################################################################
################################# Trainers ################################
###########################################################################
@router.get(
    "/{program_id}/trainers",
    response_model=List[s_club.Employee],
    tags=["Club - Program - Trainer"],
    response_model_exclude_none=True,
)
async def get_trainers_v1(
    club_id: uuid.UUID = Path(..., description="The ID of the club"),
    program_id: uuid.UUID = Path(..., description="The ID of the program"),
    ep_context: EndpointContext = Depends(get_endpoint_context),
    token_details: core_security.TokenDetails = Depends(
        auth_middleware.AccessTokenChecker(club_permissions=[ClubPermissions.READ_PROGRAMS])
    ),
):
    try:
        trainers = await club_crud.get_trainers(ep_context.db, program_id)
        return [s_club.Employee.model_validate(trainer) for trainer in trainers]
    except Exception as e:
        await handle_exception(e, ep_context, "Failed to get trainers")


@router.post(
    "/{program_id}/trainers",
    response_model=s_generic.MessageResponse,
    tags=["Club - Program - Trainer"],
    response_model_exclude_none=True,
)
async def add_trainer_v1(
    club_id: uuid.UUID = Path(..., description="The ID of the club"),
    program_id: uuid.UUID = Path(..., description="The ID of the program"),
    user_id: uuid.UUID = Query(..., description="The ID of the user to add as a trainer"),
    ep_context: EndpointContext = Depends(get_endpoint_context),
    token_details: core_security.TokenDetails = Depends(
        auth_middleware.AccessTokenChecker(club_permissions=[ClubPermissions.UPDATE_PROGRAMS])
    ),
):
    try:
        await club_controller.add_trainer(ep_context, token_details, club_id, program_id, user_id)
        return {"message": "Trainer added successfully."}
    except Exception as e:
        await handle_exception(e, ep_context, "Failed to add trainer")


@router.delete(
    "/{program_id}/trainers/{trainer_id}",
    response_model=s_generic.MessageResponse,
    tags=["Club - Program - Trainer"],
)
async def remove_trainer_v1(
    club_id: uuid.UUID = Path(..., description="The ID of the club"),
    program_id: uuid.UUID = Path(..., description="The ID of the program"),
    trainer_id: uuid.UUID = Path(..., description="The ID of the trainer"),
    ep_context: EndpointContext = Depends(get_endpoint_context),
    token_details: core_security.TokenDetails = Depends(
        auth_middleware.AccessTokenChecker(club_permissions=[ClubPermissions.UPDATE_PROGRAMS])
    ),
):
    try:
        await club_controller.remove_trainer(ep_context, token_details, club_id, program_id, trainer_id)
        return {"message": "Trainer removed successfully."}
    except Exception as e:
        await handle_exception(e, ep_context, "Failed to remove trainer")
