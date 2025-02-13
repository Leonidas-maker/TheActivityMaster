from fastapi import APIRouter, HTTPException, Depends, Request
import uuid

from api.v1.endpoints.club.club_id import program_offerings
from api.v1.endpoints.club.club_id import club_roles
from api.v1.endpoints.club.club_id import memberships
from api.v1.endpoints.club.club_id import bookings

# Router for club_id endpoints
router = APIRouter()
router.include_router(program_offerings.router, prefix="/programs")
router.include_router(club_roles.router, prefix="/roles")
router.include_router(memberships.router, prefix="/memberships")
router.include_router(bookings.router, prefix="/bookings")