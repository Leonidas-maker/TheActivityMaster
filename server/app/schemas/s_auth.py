from pydantic import BaseModel
from typing import List, Optional

from models.m_user import User2FAMethods


class LoginRequest(BaseModel):
    ident: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str

class SecurityTokenResponse(BaseModel):
    security_token: str
    methods: Optional[List[User2FAMethods]]

class LoginCode2fa(BaseModel):
    code: str
    is_totp: bool = False

class ResetPassword(BaseModel):
    password: str