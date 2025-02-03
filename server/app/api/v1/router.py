from fastapi import APIRouter
from api.v1.endpoints import auth
from api.v1.endpoints import user
from api.v1.endpoints.verification import base

# Main-Router
router = APIRouter()

# Registering the sub-routers
router.include_router(auth.router, prefix="/auth")
router.include_router(user.router, prefix="/user")
router.include_router(base.router, prefix="/verification")