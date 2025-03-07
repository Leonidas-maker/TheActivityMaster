from pydantic import BaseModel, Field
from typing import List, Optional

from models.m_user import User2FAMethods


class LoginRequest(BaseModel):
    """
    Model for a login request.

    Fields:
      - ident: The user identifier (e.g., username or email), with a maximum length of 255 characters.
      - password: The user's password (8-100 characters).
    """
    ident: str = Field(..., max_length=255, description="User identifier (username or email, max 255 characters).")
    password: str = Field(..., min_length=8, max_length=100, description="User password (8-100 characters).")


class TokenResponse(BaseModel):
    """
    Response model for login that returns access and refresh tokens.

    Fields:
      - access_token: The access token for API authentication.
      - refresh_token: The refresh token used to obtain a new access token.
    """
    access_token: str = Field(..., description="Access token for authentication.")
    refresh_token: str = Field(..., description="Refresh token to obtain a new access token.")


class SecurityTokenResponse(BaseModel):
    """
    Response model for providing a security token along with available 2FA methods.

    Fields:
      - security_token: The security token string.
      - methods: An optional list of two-factor authentication methods available for the user.
    """
    security_token: str = Field(..., description="Security token string.")
    methods: Optional[List[User2FAMethods]] = Field(
        None, description="Optional list of 2FA methods available for the user."
    )


class LoginCode2fa(BaseModel):
    """
    Model for two-factor authentication code submission during login.

    Fields:
      - code: The 2FA code (max 6 characters).
      - is_totp: Boolean indicating if the code is TOTP-based; defaults to False.
    """
    code: str = Field(..., max_length=6, description="Two-factor authentication code (max 6 characters).")
    is_totp: bool = Field(False, description="Indicates if the 2FA code is TOTP-based (default False).")


class ResetPassword(BaseModel):
    """
    Model for resetting a user's password.

    Fields:
      - password: The new password (8-100 characters).
    """
    password: str = Field(..., min_length=8, max_length=100, description="The new password (8-100 characters).")