from fastapi import APIRouter, Depends, Request, Header
from fastapi.security import OAuth2PasswordBearer


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


@router.post("/login", response_model=s_auth.SecurityTokenResponse, tags=["Authentication - Login"])
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


@router.post("/verify-code-2fa", response_model=s_auth.TokenResponse, tags=["Authentication - Login"])
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


@router.post("/refresh-token", response_model=s_auth.TokenResponse, tags=["Authentication - Token"])
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


@router.delete("/logout", tags=["Authentication - Token"])
async def logout_v1(
    request: Request,
    token_details: core_security.TokenDetails = Depends(auth_middleware.AccessTokenChecker()),
    ep_context: EndpointContext = Depends(get_endpoint_context),
):
    """Logout a user"""
    try:
        client_ip = request.client.host if request.client else ""
        await auth_controller.logout(ep_context, token_details, client_ip)
        return {"message": "Successfully logged out"}
    except Exception as e:
        await handle_exception(e, ep_context, "Failed to logout")


@router.post("/forgot-password", tags=["Authentication - Forgot-Password"])
async def forgot_password_v1(
    ident: str,
    request: Request,
    ep_context: EndpointContext = Depends(get_endpoint_context),
):
    """Send a forgot password email"""
    try:
        client_ip = request.client.host if request.client else ""
        await auth_controller.forgot_password(ep_context, ident, client_ip)
        return {"message": "Successfully sent forgot password email"}
    except Exception as e:
        await handle_exception(e, ep_context, "Failed to send forgot password email")

@router.post("/reset-password/init", response_model=s_auth.SecurityTokenResponse, tags=["Authentication - Forgot-Password"])
async def reset_password_init_v1(
    user_id: str,
    expires: str,
    signature: str,
    request: Request,
    application_id: str = Header(...),
    ep_context: EndpointContext = Depends(get_endpoint_context),
):
    """Reset a user's password"""
    try:
        client_ip = request.client.host if request.client else ""
        security_token = await auth_controller.reset_password_init(ep_context, user_id, expires, signature, application_id, client_ip)
        return s_auth.SecurityTokenResponse(security_token=security_token, methods=None)
    except Exception as e:
        await handle_exception(e, ep_context, "Failed to reset password")

@router.post("/reset-password", tags=["Authentication - Forgot-Password"])
async def reset_password_v1(
    reset_form: s_auth.ResetPassword,
    ep_context: EndpointContext = Depends(get_endpoint_context),
    token_details: core_security.TokenDetails = Depends(auth_middleware.SecurityTokenChecker("reset_password")),
):
    """Reset a user's password"""
    try:
         await auth_controller.reset_password(ep_context, token_details, reset_form.password)
    except Exception as e:
        await handle_exception(e, ep_context, "Failed to reset password")