from fastapi import security
from pydantic import BaseModel

from models.m_user import User2FAMethods

class LoginRequest(BaseModel):
    email: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str

class SecurityTokenResponse(BaseModel):
    security_token: str
    methods: list[User2FAMethods]

class LoginCode2fa(BaseModel):
    code: str
    is_totp: bool = False