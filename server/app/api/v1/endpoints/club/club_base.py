from fastapi import APIRouter, HTTPException, Depends, Request, Query, Path, Body, Header
from sqlalchemy import or_, ColumnElement
import uuid
from typing import Union, List, Dict, Optional
from decimal import Decimal

from api.v1.endpoints.club.club_id import base as club_id_router

from controllers import club as club_controller
from schemas import s_club, s_generic, s_user, s_role
from models import m_club, m_payment

from core.generic import EndpointContext
import core.security as core_security
from core.context import current_language_var

from crud import club as club_crud, role as role_crud

from middleware.general import get_endpoint_context
import middleware.auth as auth_middleware

from utils.exceptions import handle_exception

from config.permissions import ClubPermissions

router = APIRouter()
router.include_router(club_id_router.router, prefix="/{club_id}")


###########################################################################
########################### Additional Endpoints ##########################
###########################################################################
# ======================================================== #
# ======================== Search ======================== #
# ======================================================== #
@router.get("/search", response_model=List[s_club.Club], tags=["Club"])
async def search_clubs_v1(
    query: str = Query(..., min_length=1, max_length=50, description="The search query"),
    page: int = Query(1, ge=1, description="The page number"),
    page_size: int = Query(10, ge=1, le=50, description="The number of clubs per page"),
    ep_context: EndpointContext = Depends(get_endpoint_context),
):
    try:
        clubs = await club_crud.search_clubs(ep_context.db, query, page, page_size)
        return [s_club.Club.model_validate(club) for club in clubs]
    except Exception as e:
        await handle_exception(e, ep_context, "Failed to search clubs")


@router.get(
    "/programs/search", response_model=List[s_club.Program], tags=["Club - Program"], response_model_exclude_none=True
)
async def search_programs_v1(
    query: Optional[str] = Query(None, min_length=1, max_length=50, description="Free text search (Name, Description)"),
    category_id: Optional[int] = Query(None, description="Category ID"),
    min_price: Optional[Decimal] = Query(None, description="Minimum price"),
    max_price: Optional[Decimal] = Query(None, description="Maximum price"),
    session_type: Optional[m_club.SessionType] = Query(None, description="Filter by session type"),
    page: int = Query(1, ge=1, description="The page number"),
    page_size: int = Query(10, ge=1, le=50, description="The number of clubs per page"),
    ep_context: EndpointContext = Depends(get_endpoint_context),
):
    try:
        filters: List[ColumnElement] = []

        if query:
            filters.append(
                or_(
                    m_club.Program.name.ilike(f"%{query}%"),
                    m_club.Program.description.ilike(f"%{query}%"),
                )
            )
        if category_id:
            filters.append(m_club.Program.categories.any(m_club.ProgramCategory.id == category_id))
        if min_price is not None:
            filters.append(m_club.Program.price >= min_price)
        if max_price is not None:
            filters.append(m_club.Program.price <= max_price)
        if session_type:
            filters.append(m_club.Program.sessions.any(m_club.Session.session_type == session_type))

        if not filters:
            raise HTTPException(status_code=400, detail="At least one filter is required")

        filters.append(m_club.Program.status == m_club.ProgramStatus.ACTIVE)

        programs = await club_crud.search_programs(ep_context.db, filters, page, page_size)
        return [s_club.Program.model_validate(program) for program in programs]
    except Exception as e:
        await handle_exception(e, ep_context, "Failed to search programs")


# ======================================================== #
# ========================= Other ======================== #
# ======================================================== #
@router.get("/permissions", response_model=List[s_role.Permission], tags=["Club - Role"])
async def get_club_permissions_v1(ep_context: EndpointContext = Depends(get_endpoint_context)):
    try:
        permissions = await role_crud.get_permissions(ep_context.db, "club")
        return [s_role.Permission.model_validate(permission) for permission in permissions]
    except Exception as e:
        await handle_exception(e, ep_context, "Failed to get club permissions")


@router.get(
    "/program-categories", response_model=List[s_club.ProgramCategory], tags=["Club - Program", "Access: Public"]
)
async def get_program_categories_v1(
    ep_context: EndpointContext = Depends(get_endpoint_context),
    current_language: str = Header(default="en", alias="Accept-Language"),
):
    try:
        current_language_var.set(current_language)
        program_categories = await club_crud.get_program_categories(ep_context.db)
        return [s_club.ProgramCategory.model_validate(category) for category in program_categories]
    except Exception as e:
        await handle_exception(e, ep_context, "Failed to get program categories")


###########################################################################
################################### User ##################################
###########################################################################
@router.get("/me", tags=["User"], response_model=s_club.Club, response_model_exclude_none=True)
async def get_my_clubs_v1(
    ep_context: EndpointContext = Depends(get_endpoint_context),
    token_details: core_security.TokenDetails = Depends(auth_middleware.AccessTokenChecker()),
):
    try:
        user_id = token_details.user_id
        clubs = await club_crud.get_user_clubs(ep_context.db, user_id)
        return [s_club.Club.model_validate(club) for club in clubs]
    except Exception as e:
        await handle_exception(e, ep_context, "Failed to get user clubs")


@router.get("/me/memberships", tags=["User"])
async def get_my_memberships_v1():
    pass


@router.get("/me/booked", tags=["User"], response_model=List[s_club.Booking], response_model_exclude_none=True)
async def get_my_booked_sessions_v1(
    ep_context: EndpointContext = Depends(get_endpoint_context),
    token_details: core_security.TokenDetails = Depends(auth_middleware.AccessTokenChecker()),
):
    try:
        user_id = token_details.user_id
        sessions = await club_crud.get_bookings_by_user_id(
            ep_context.db,
            user_id,
            stats=[
                m_payment.BookingStatus.PENDING,
                m_payment.BookingStatus.CONFIRMED,
                m_payment.BookingStatus.CANCELLED,
                m_payment.BookingStatus.CANCELLED_BY_CLUB,
            ],
        )
        return [s_club.Booking.model_validate(session) for session in sessions]
    except Exception as e:
        await handle_exception(e, ep_context, "Failed to get user booked sessions")


@router.get("/me/attended", tags=["User"], response_model=List[s_club.Booking], response_model_exclude_none=True)
async def get_my_attended_sessions_v1(
    ep_context: EndpointContext = Depends(get_endpoint_context),
    token_details: core_security.TokenDetails = Depends(auth_middleware.AccessTokenChecker()),
):
    try:
        user_id = token_details.user_id
        sessions = await club_crud.get_bookings_by_user_id(
            ep_context.db,
            user_id,
            stats=[
                m_payment.BookingStatus.COMPLETED,
            ],
        )
        return [s_club.Booking.model_validate(session) for session in sessions]
    except Exception as e:
        await handle_exception(e, ep_context, "Failed to get user attended sessions")


###########################################################################
################################### Club ##################################
###########################################################################
@router.get("", response_model=List[s_club.Club], tags=["Club", "Access: Public"])
async def get_clubs_v1(
    page: int = Query(1, ge=1, description="The page number"),
    page_size: int = Query(10, ge=1, le=50, description="The number of clubs per page"),
    city: str = Query(default="", min_length=0, max_length=20, description="The city name to filter by"),
    ep_context: EndpointContext = Depends(get_endpoint_context),
):
    try:
        clubs = await club_crud.get_clubs(ep_context.db, page, page_size, city)
        return [s_club.Club.model_validate(club) for club in clubs]
    except Exception as e:
        await handle_exception(e, ep_context, "Failed to get clubs")


@router.post("", response_model=s_club.Club, tags=["Club"])
async def create_club_v1(
    club_create: s_club.ClubCreate = Body(..., description="The club data to create"),
    token_details: core_security.TokenDetails = Depends(auth_middleware.AccessTokenChecker()),
    ep_context: EndpointContext = Depends(get_endpoint_context),
):
    try:
        return await club_controller.create_club(ep_context, token_details, club_create)
    except Exception as e:
        await handle_exception(e, ep_context, "Failed to create club")


@router.get("/{club_id}", response_model=Union[s_club.ClubDetails, s_club.ClubDetails], tags=["Club", "Access: Public"])
async def get_club_v1(
    club_id: uuid.UUID = Path(..., description="The ID of the club"),
    ep_context: EndpointContext = Depends(get_endpoint_context),
):
    try:
        club = await club_controller.get_club(ep_context, club_id)
        return s_club.ClubDetails.model_validate(club)

    except Exception as e:
        await handle_exception(e, ep_context, "Failed to get club")


@router.put("/{club_id}", response_model=s_club.Club, tags=["Club"])
async def update_club_v1(
    club_id: uuid.UUID = Path(..., description="The ID of the club"),
    club_update: s_club.ClubUpdate = Body(..., description="The updated club data"),
    ep_context: EndpointContext = Depends(get_endpoint_context),
    token_details: core_security.TokenDetails = Depends(
        auth_middleware.AccessTokenChecker(club_permissions=[ClubPermissions.UPDATE_CLUB_DATA])
    ),
):
    try:
        return await club_controller.update_club(ep_context, token_details, club_id, club_update)
    except Exception as e:
        await handle_exception(e, ep_context, "Failed to update club")


@router.delete("/{club_id}", response_model=s_generic.MessageResponse, tags=["Club"])
async def delete_club_v1(club_id: uuid.UUID = Path(..., description="The ID of the club")):
    return {"message": "Not available yet. Please contact support."}


@router.get(
    "/{club_id}/sessions",
    response_model=List[s_club.Session],
    tags=["Club - Program - Session", "Access: Hybrid"],
    response_model_exclude_none=True,
)
async def get_program_sessions_v1(
    club_id: uuid.UUID = Path(..., description="The ID of the club"),
    page: int = Query(1, ge=1, description="The page number"),
    page_size: int = Query(10, ge=1, le=50, description="The number of sessions per page"),
    ep_context: EndpointContext = Depends(get_endpoint_context),
    token_details: core_security.TokenDetails = Depends(auth_middleware.AccessTokenCheckerHybrid()),
):
    """Get sessions of a club

    **Note: If the user has the permission to read programs or is a trainee of the program,
    provide the authentication details to view the sessions of a program with any status.**
    """
    try:
        user_id = token_details.user_id if token_details else None
        programs = await club_crud.get_authorized_sessions(ep_context.db, club_id, page, page_size, user_id)
        return [s_club.Session.model_validate(program) for program in programs]
    except Exception as e:
        await handle_exception(e, ep_context, "Failed to get program sessions")


# ======================================================== #
# ======================= BOOKINGS ======================= #
# ======================================================== #
@router.get("/{club_id}/bookings", tags=["Club - Booking"])
async def get_bookings_v1(club_id: uuid.UUID = Path(..., description="The ID of the club")):
    pass


@router.post("/book", tags=["Club - Booking"])
async def create_booking_v1(
    booking_create: List[s_club.BookingCreateRequest],
    ep_context: EndpointContext = Depends(get_endpoint_context),
    token_details: core_security.TokenDetails = Depends(auth_middleware.AccessTokenChecker()),
):
    try:
        bookings, intent = await club_controller.create_booking(ep_context, token_details, booking_create)
        return {"bookings": bookings, "client_secret": intent.client_secret}
    except Exception as e:
        await handle_exception(e, ep_context, "Failed to create booking")


@router.get(
    "/bookings/{booking_id}",
    response_model=s_club.BookingDetails,
    response_model_exclude_none=True,
    tags=["Club - Booking"],
)
async def get_booking_v1(
    booking_id: uuid.UUID,
    ep_context: EndpointContext = Depends(get_endpoint_context),
    token_details: core_security.TokenDetails = Depends(auth_middleware.AccessTokenChecker()),
):
    try:
        booking = await club_crud.get_bookings_by_user_id_and_id(ep_context.db, booking_id, token_details.user_id)
        return s_club.BookingDetails.model_validate(booking)
    except Exception as e:
        await handle_exception(e, ep_context, "Failed to get booking")


@router.delete("/bookings/{booking_id}", tags=["Club - Booking"])
async def delete_booking_v1(
    booking_id: uuid.UUID,
    ep_context: EndpointContext = Depends(get_endpoint_context),
    token_details: core_security.TokenDetails = Depends(auth_middleware.AccessTokenChecker()),
):
    try:
        # TODO: Implement cancel booking
        return {"message": "Not available yet. Please contact support."}
    except Exception as e:
        await handle_exception(e, ep_context, "Failed to cancel booking")
