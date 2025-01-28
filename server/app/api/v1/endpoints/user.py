from fastapi import APIRouter, HTTPException, Depends,Request
from sqlalchemy.ext.asyncio import AsyncSession
import uuid
import traceback

from core.database import get_db

import schemas.s_user as s_user
import schemas.s_generic as s_generic

import core.security as core_security
from utils.exceptions import handle_exception

import middleware.auth as auth_middleware
from middleware.general import get_endpoint_context

import controllers.user as user_controller

from core.generic import EndpointContext

# Router for user endpoints
router = APIRouter()

@router.post("/register")
async def register_user_v1(user: s_user.UserCreate, ep_context: EndpointContext = Depends(get_endpoint_context)):
    """Register a new user
    """
    try:
        user_id = await user_controller.register_user(ep_context, user)
        return {"message": "User registered", "user_id": user_id}
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=f"Invalid user data: {ve}")
    except Exception as e:
        await handle_exception(e, ep_context, "Failed to register user")

@router.get("/user/me", response_model=s_user.User)
async def get_user_information(token_details: core_security.TokenDetails = Depends(auth_middleware.check_access_token), ep_context: EndpointContext = Depends(get_endpoint_context)):
    """Get user information
    """
    try:
        user = await user_controller.user_information(ep_context.db, uuid.UUID(token_details.payload["sub"]))
        return s_user.User(
            id=str(user.id),
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            address=s_generic.Address(**user.address.get_as_dict()) if user.address else None,
        )
    except Exception as e:
        await handle_exception(e, ep_context, "Failed to get user information")

    
@router.post("/totp_register_init", response_model=s_user.RegisterInitTOTP, tags=["TOTP"])
async def totp_register_init_v1(
    token_details: core_security.TokenDetails = Depends(auth_middleware.check_access_token),
    ep_context: EndpointContext = Depends(get_endpoint_context),
):
    """Start registering a TOTP device
    """
    try:
        secret, uri = await user_controller.totp_register_init(ep_context, token_details)
        return s_user.RegisterInitTOTP(secret=secret, uri=uri)
    except Exception as e:
        await handle_exception(e, ep_context, "Failed to start TOTP registration")

@router.post("/totp_register", response_model=s_user.RegisterTOTP, tags=["TOTP"])
async def totp_register_v1(
    _2fa_code: str,
    token_details: core_security.TokenDetails = Depends(auth_middleware.check_access_token),
    ep_context: EndpointContext = Depends(get_endpoint_context),
):
    """Verify a TOTP token
    """
    try:
        backup_codes = await user_controller.totp_register(ep_context, token_details, _2fa_code)
        return s_user.RegisterTOTP(success=True, backup_codes=backup_codes)
    except Exception as e:
        await handle_exception(e, ep_context, "Failed to register TOTP")