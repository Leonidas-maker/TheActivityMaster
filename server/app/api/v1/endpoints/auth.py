from fastapi import APIRouter, Depends, Request, Header
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordBearer

from core.database import get_db

from controllers import auth as auth_controller

import core.security as core_security
from core.generic import EndpointContext

from utils.exceptions import handle_exception

import schemas.s_auth as s_auth

import middleware.auth as auth_middleware
from middleware.general import get_endpoint_context

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="refresh_token")

# Router for the auth endpoints
router = APIRouter()


@router.post("/login", response_model=s_auth.SecurityTokenResponse, tags=["Authentication-Login"])
async def login_v1(
    login_form: s_auth.LoginRequest,
    request: Request,
    application_id: str = Header(...),
    ep_context: EndpointContext = Depends(get_endpoint_context),
):
    """Login a user and return the security token"""
    try:
        client_ip = request.client.host if request.client else ""

        security_token, methods_2fa = await auth_controller.login(ep_context, login_form, client_ip, application_id)
        return s_auth.SecurityTokenResponse(security_token=security_token, methods=methods_2fa)
    except Exception as e:
        await handle_exception(e, ep_context, "Failed to login")


@router.post("/verify-code-2fa", response_model=s_auth.TokenResponse, tags=["Authentication-Login"])
async def verify_code_2fa_v1(
    metadata: s_auth.LoginCode2fa,
    request: Request,
    token_details: core_security.TokenDetails = Depends(auth_middleware.SecurityTokenChecker("2fa")),
    ep_context: EndpointContext = Depends(get_endpoint_context),
):
    """Verify a 2FA code and return the access and refresh tokens"""
    try:
        client_ip = request.client.host if request.client else ""

        access_token, refresh_token = await auth_controller.verify_code_2fa(
            ep_context, token_details, metadata, client_ip
        )
        return s_auth.TokenResponse(access_token=access_token, refresh_token=refresh_token)
    except Exception as e:
        await handle_exception(e, ep_context, "Failed to verify 2FA code")


@router.post("/refresh-token", response_model=s_auth.TokenResponse, tags=["Authentication-Token"])
async def refresh_token_v1(
    request: Request,
    token_details: core_security.TokenDetails = Depends(auth_middleware.check_refresh_token),
    ep_context: EndpointContext = Depends(get_endpoint_context),
):
    """Refresh the access token"""
    try:
        client_ip = request.client.host if request.client else ""
        access_token, refresh_token = await auth_controller.refresh_token(ep_context, token_details, client_ip)
        return s_auth.TokenResponse(access_token=access_token, refresh_token=refresh_token)
    except Exception as e:
        await handle_exception(e, ep_context, "Failed to refresh token")


@router.delete("/logout", tags=["Authentication-Token"])
async def logout_v1(
    request: Request,
    token_details: core_security.TokenDetails = Depends(auth_middleware.check_access_token),
    ep_context: EndpointContext = Depends(get_endpoint_context),
):
    """Logout a user"""
    try:
        client_ip = request.client.host if request.client else ""
        await auth_controller.logout(ep_context, token_details, client_ip)
        return {"message": "Successfully logged out"}
    except Exception as e:
        await handle_exception(e, ep_context, "Failed to logout")
