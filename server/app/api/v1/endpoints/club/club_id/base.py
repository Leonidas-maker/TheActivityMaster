from fastapi import APIRouter, HTTPException, Depends, Request
import uuid

from api.v1.endpoints.club.club_id import program_offerings, club_roles, memberships, employees


# Router for club_id endpoints
router = APIRouter()
router.include_router(program_offerings.router, prefix="/programs")
router.include_router(club_roles.router, prefix="/roles")
router.include_router(memberships.router, prefix="/memberships")
router.include_router(employees.router, prefix="/employees")