from fastapi import APIRouter, HTTPException, Depends, Request
import uuid

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


@router.post("/register", response_model=s_generic.MessageResponse, tags=["User"])
async def register_user_v1(user: s_user.UserCreate, ep_context: EndpointContext = Depends(get_endpoint_context)):
    """Register a new user"""
    try:
        user_id = await user_controller.register_user(ep_context, user)
        return s_generic.MessageResponse(message=str(user_id))
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=f"Invalid user data: {ve}")
    except Exception as e:
        await handle_exception(e, ep_context, "Failed to register user")

###########################################################################
################################### /Me ###################################
###########################################################################
@router.get("/me", response_model=s_user.User, tags=["User"])
async def get_user_information(
    token_details: core_security.TokenDetails = Depends(auth_middleware.AccessTokenChecker()),
    ep_context: EndpointContext = Depends(get_endpoint_context),
):
    """Get user information"""
    try:
        user = await user_controller.user_information(ep_context.db, uuid.UUID(token_details.payload["sub"]))
        _2fa_methods = [ method.method.value for method in user._2fa ]
        if not _2fa_methods:
            _2fa_methods = ["email"]
        return s_user.User(
            id=str(user.id),
            username=user.username,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            address=s_generic.Address(**user.address.get_as_dict()) if user.address else None,
            methods_2fa=_2fa_methods
        )
    except Exception as e:
        await handle_exception(e, ep_context, "Failed to get user information")


@router.patch("/me", tags=["User"])
async def delete_user_v1(
    user_delete: s_user.UserDelete,
    token_details: core_security.TokenDetails = Depends(auth_middleware.AccessTokenChecker()),
    ep_context: EndpointContext = Depends(get_endpoint_context),
):
    """Delete the user"""
    try:
        await user_controller.user_delete(ep_context, token_details, user_delete)
        return {"message": "User deleted"}
    except Exception as e:
        await handle_exception(e, ep_context, "Failed to delete user")


@router.post("/me/totp_register_init", response_model=s_user.RegisterInitTOTP, tags=["User - TOTP"])
async def totp_register_init_v1(
    token_details: core_security.TokenDetails = Depends(auth_middleware.AccessTokenChecker()),
    ep_context: EndpointContext = Depends(get_endpoint_context),
):
    """Start registering a TOTP device"""
    try:
        secret, uri = await user_controller.totp_register_init(ep_context, token_details)
        return s_user.RegisterInitTOTP(secret=secret, uri=uri)
    except Exception as e:
        await handle_exception(e, ep_context, "Failed to start TOTP registration")


@router.post("/me/totp_register", response_model=s_user.RegisterTOTP, tags=["User - TOTP"])
async def totp_register_v1(
    _2fa_code: str,
    token_details: core_security.TokenDetails = Depends(auth_middleware.AccessTokenChecker()),
    ep_context: EndpointContext = Depends(get_endpoint_context),
):
    """Verify a TOTP token"""
    try:
        backup_codes = await user_controller.totp_register(ep_context, token_details, _2fa_code)
        return s_user.RegisterTOTP(success=True, backup_codes=backup_codes)
    except Exception as e:
        await handle_exception(e, ep_context, "Failed to register TOTP")


@router.post("/me/totp_remove", tags=["User - TOTP"])
async def totp_remove_v1(
    remove_totp: s_user.RemoveTOTP,
    token_details: core_security.TokenDetails = Depends(auth_middleware.AccessTokenChecker()),
    ep_context: EndpointContext = Depends(get_endpoint_context),
):
    """Remove the TOTP device"""
    try:
        await user_controller.totp_remove(ep_context, token_details, remove_totp)
        return {"message": "TOTP device removed"}
    except Exception as e:
        await handle_exception(e, ep_context, "Failed to remove TOTP")


@router.post("/me/change_password", tags=["User"])
async def change_password_v1(
    password_change: s_user.ChangePassword,
    token_details: core_security.TokenDetails = Depends(auth_middleware.AccessTokenChecker()),
    ep_context: EndpointContext = Depends(get_endpoint_context),
):
    """Change the user's password"""
    try:
        await user_controller.change_password(ep_context, token_details, password_change)
        return {"message": "Password changed"}
    except Exception as e:
        await handle_exception(e, ep_context, "Failed to change password")


@router.put("/me/address", tags=["User"])
async def update_user_address_v1(
    address: s_generic.Address,
    token_details: core_security.TokenDetails = Depends(auth_middleware.AccessTokenChecker()),
    ep_context: EndpointContext = Depends(get_endpoint_context),
):
    """Update the user's address"""
    try:
        await user_controller.update_user_address(ep_context, token_details, address)
        return {"message": "Address updated"}
    except Exception as e:
        await handle_exception(e, ep_context, "Failed to update address")


###########################################################################
################################## Admin ##################################
###########################################################################
