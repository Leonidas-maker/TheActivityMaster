from pydantic import BaseModel, Field
from typing import List, Optional

from models.m_user import User2FAMethods


class LoginRequest(BaseModel):
    ident: str = Field(..., max_length=255)
    password: str = Field(..., min_length=8, max_length=100)

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str

class SecurityTokenResponse(BaseModel):
    security_token: str
    methods: Optional[List[User2FAMethods]]

class LoginCode2fa(BaseModel):
    code: str = Field(..., max_length=6)
    is_totp: bool = False

class ResetPassword(BaseModel):
    password: str = Field(..., min_length=8, max_length=100)