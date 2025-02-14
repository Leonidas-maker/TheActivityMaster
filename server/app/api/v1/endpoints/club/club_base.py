from fastapi import APIRouter, HTTPException, Depends, Request, Query
import uuid
from typing import Union, List

from api.v1.endpoints.club.club_id import base as club_id

from controllers import club as club_controller
from schemas import s_club, s_generic

from core.generic import EndpointContext
import core.security as core_security

from crud import club as club_crud

from middleware.general import get_endpoint_context
import middleware.auth as auth_middleware

from utils.exceptions import handle_exception


router = APIRouter()
router.include_router(club_id.router, prefix="/{club_id}")

###########################################################################
########################### Additional Endpoints ##########################
###########################################################################
# ======================================================== #
# ======================== Search ======================== #
# ======================================================== #
@router.get("/search", response_model=List[s_club.Club], tags=["Club"])
async def search_clubs_v1(
    query: str = Query(..., min_length=1),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50),
    ep_context: EndpointContext = Depends(get_endpoint_context),
):
    try:
        clubs = await club_crud.search_clubs(ep_context.db, query, page, page_size)
        return [
            s_club.Club(
                id=club.id,
                name=club.name,
                description=str(club.description),
                address=s_generic.Address(**club.address.get_as_dict()),
            )
            for club in clubs
        ]
    except Exception as e:
        await handle_exception(e, ep_context, "Failed to search clubs")


@router.get("/programs/search", tags=["Club - Program"])
async def search_programs_v1(category: str, query: str):
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
################################### Club ##################################
###########################################################################
@router.get("", response_model=List[s_club.Club], tags=["Club", "Public"])
async def get_clubs_v1(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50),
    city: str = Query(default="", min_length=0, max_length=20),
    ep_context: EndpointContext = Depends(get_endpoint_context),
):
    try:
        clubs = await club_crud.get_clubs(ep_context.db, page, page_size, city)
        return [
            s_club.Club(
                id=club.id,
                name=club.name,
                description=str(club.description),
                address=s_generic.Address(**club.address.get_as_dict()),
            )
            for club in clubs
        ]
    except Exception as e:
        await handle_exception(e, ep_context, "Failed to get clubs")


@router.post("", response_model=s_club.Club, tags=["Club"])
async def create_club_v1(
    club_create: s_club.ClubCreate,
    token_details: core_security.TokenDetails = Depends(auth_middleware.AccessTokenChecker()),
    ep_context: EndpointContext = Depends(get_endpoint_context),
):
    try:
        return await club_controller.create_club(ep_context, token_details, club_create)
    except Exception as e:
        await handle_exception(e, ep_context, "Failed to create club")


@router.get("/{club_id}", response_model=Union[s_club.ClubDetails, s_club.ClubDetails], tags=["Club", "Public"])
async def get_club_v1(
    club_id: uuid.UUID,
    ep_context: EndpointContext = Depends(get_endpoint_context),
):
    try:
        club = await club_controller.get_club(ep_context, club_id)
        return s_club.ClubDetails(
            id=club.id,
            name=club.name,
            description=str(club.description),
            address=s_generic.Address(**club.address.get_as_dict()),
            owner_ids=[
                s_club.Employee(
                    id=user_club_role.user.id,
                    first_name=user_club_role.user.first_name,
                    last_name=user_club_role.user.last_name,
                    email=user_club_role.user.email,
                )
                for user_club_role in club.user_club_roles
            ],
        )

    except Exception as e:
        await handle_exception(e, ep_context, "Failed to get club")


@router.put("/{club_id}", tags=["Club"])
async def update_club_v1(club_id: uuid.UUID):
    pass


@router.delete("/{club_id}", response_model=s_generic.MessageResponse, tags=["Club"])
async def delete_club_v1(club_id: uuid.UUID):
    return {"message": "Not available yet. Please contact support."}


@router.get("/{club_id}/sessions", tags=["Club - Program - Session"])
async def get_sessions_v1(club_id: uuid.UUID):
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