from fastapi import APIRouter
from api.v1.endpoints import auth
from api.v1.endpoints import user

# Haupt-Router für die API-Version
router = APIRouter()

# Registrieren der Endpunkte
router.include_router(auth.router, prefix="/auth", tags=["auth"])
router.include_router(user.router, prefix="/user", tags=["user"])