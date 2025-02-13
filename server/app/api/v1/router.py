from fastapi import APIRouter
from api.v1.endpoints import auth, user
from api.v1.endpoints.verification import verification_base as verification
from api.v1.endpoints.club import club_base as club
    

# Main-Router
router = APIRouter()

# Registering the sub-routers
router.include_router(auth.router, prefix="/auth")
router.include_router(user.router, prefix="/user")
router.include_router(verification.router, prefix="/verification")
router.include_router(club.router, prefix="/clubs")
