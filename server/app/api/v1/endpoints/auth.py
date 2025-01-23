from fastapi import APIRouter, HTTPException, Depends, Request, security
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordBearer

from core.database import get_db

from controllers import auth as auth_controller

import schemas.s_auth as s_auth

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="refresh_token")


# Router for the auth endpoints
router = APIRouter()

@router.post("/login", response_model=s_auth.SecurityTokenResponse, tags=["Authentication"])
async def login_v1(login_form: s_auth.LoginRequest, request: Request, db: AsyncSession = Depends(get_db)):
    """Login a user and return the security token"""
    client_ip = request.client.host if request.client else ""

    security_token, methods_2fa = await auth_controller.login(db, login_form, client_ip)
    return s_auth.SecurityTokenResponse(security_token=security_token, methods=methods_2fa)

@router.post("/verify-2fa", response_model=s_auth.TokenResponse, tags=["Authentication"])
async def verify_2fa_v1(metadata: s_auth.LoginCode2fa, request: Request, security_token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    """Verify a 2FA code and return the access and refresh tokens"""
    client_ip = request.client.host if request.client else ""

    access_token, refresh_token = await auth_controller.verify_2fa(db, security_token, metadata, client_ip)
    return s_auth.TokenResponse(access_token=access_token, refresh_token=refresh_token)