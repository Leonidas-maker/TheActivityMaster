from fastapi import APIRouter, HTTPException, Depends, Request
import uuid

from api.v1.endpoints.club.club_id import base as club_id

from controllers import club as club_controller
from schemas import s_club, s_generic

from core.generic import EndpointContext
import core.security as core_security

from middleware.general import get_endpoint_context
import middleware.auth as auth_middleware

from utils.exceptions import handle_exception

# Router for club endpouuid.UUIDs
router = APIRouter()
router.include_router(club_id.router, prefix="/{club_id}")


###########################################################################
################################### Club ##################################
###########################################################################
@router.get("", tags=["Club"])
async def get_clubs_v1():
    pass


@router.post("", response_model=s_club.Club, tags=["Club"])
async def create_club_v1(
    club_create: s_club.ClubCreate,
    token_details: core_security.TokenDetails = Depends(auth_middleware.AccessTokenChecker()),
    ep_context: EndpointContext = Depends(get_endpoint_context),
):
    try:
        club = await club_controller.create_club(ep_context, token_details, club_create)
        return s_club.Club(
            id=club.id,
            name=club.name,
            description=str(club.description),
            address=s_generic.Address(**club.address.get_as_dict()),
            owner_ids=[token_details.user_id],
        )
    except Exception as e:
        await handle_exception(e, ep_context, "Failed to create club")


@router.get("/{club_id}", tags=["Club"])
async def get_club_v1(club_id: uuid.UUID):
    pass


@router.put("/{club_id}", tags=["Club"])
async def update_club_v1(club_id: uuid.UUID):
    pass


@router.delete("/{club_id}", tags=["Club"])
async def delete_club_v1(club_id: uuid.UUID):
    pass


@router.get("/{club_id}/sessions", tags=["Club - Program - Session"])
async def get_sessions_v1(club_id: uuid.UUID):
    pass


###########################################################################
################################### User ##################################
###########################################################################
@router.get("/me", tags=["User"])
async def get_my_clubs_v1():
    pass


@router.get("/me/memberships", tags=["User"])
async def get_my_memberships_v1():
    pass


@router.get("/me/booked", tags=["User"])
async def get_my_booked_sessions_v1():
    pass


@router.get("/me/attended", tags=["User"])
async def get_my_attended_sessions_v1():
    pass


###########################################################################
########################### Additional Endpoints ##########################
###########################################################################
# ======================================================== #
# ======================== Search ======================== #
# ======================================================== #
@router.get("/search", tags=["Club"])
async def search_clubs_v1(query: str):
    pass


@router.get("/programs/search", tags=["Club - Program"])
async def search_programs_v1(category: str, query: str):
    pass


# ======================================================== #
# ======================= BOOKINGS ======================= #
# ======================================================== #
@router.get("/{club_id}/bookings", tags=["Club - Booking"])
async def get_bookings_v1(club_id: uuid.UUID):
    pass


# ======================================================== #
# ================= Employee & Club Roles ================ #
# ======================================================== #
@router.get("/{club_id}/employees", tags=["Club - Employee"])
async def get_employees_v1(club_id: uuid.UUID):
    pass
