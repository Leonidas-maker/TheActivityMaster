from pydantic import BaseModel, EmailStr, Field, ConfigDict, model_validator
from typing import Optional, List, Dict, Union
import uuid

from .s_generic import Address


# ======================================================== #
# ========================= User ========================= #
# ======================================================== #
class UserBase(BaseModel):
    """
    Base model representing a user with common attributes.

    Fields:
      - username: The unique username (3-50 characters).
      - email: The user's email address (3-255 characters).
      - first_name: The user's first name (1-100 characters).
      - last_name: The user's last name (1-100 characters).
      - address: (Optional) The user's address.
    """
    model_config = ConfigDict(from_attributes=True)
    username: str = Field(..., min_length=3, max_length=50, description="The unique username (3-50 characters).")
    email: EmailStr = Field(..., min_length=3, max_length=255, description="The user's email address (3-255 characters).")
    first_name: str = Field(..., min_length=1, max_length=100, description="The user's first name (1-100 characters).")
    last_name: str = Field(..., min_length=1, max_length=100, description="The user's last name (1-100 characters).")
    address: Optional[Address] = Field(None, description="The user's address.")


class UserCreate(UserBase):
    """
    Model for creating a new user.

    Inherits from UserBase and adds:
      - password: The user's password (8-100 characters).
      - newsletter_subscribed: Flag indicating newsletter subscription (default False).
    """
    password: str = Field(..., min_length=8, max_length=100, description="The user's password (8-100 characters).")
    newsletter_subscribed: bool = Field(False, description="True if the user is subscribed to the newsletter (default False).")


class User(UserBase):
    """
    Model representing an existing user.

    Inherits from UserBase and adds:
      - id: The unique UUID of the user.
      - is_newsletter_subscribed: Indicates if the user is subscribed to the newsletter.
    """
    id: uuid.UUID = Field(..., description="The unique identifier of the user.")
    is_newsletter_subscribed: bool = Field(
        ..., description="True if the user is subscribed to the newsletter."
    )


class UserDetails(User):
    """
    Detailed model representing a user with additional security and verification attributes.

    Inherits from User and adds:
      - methods_2fa: A list of enabled two-factor authentication methods.
      - identity_verified: Flag indicating if the user's identity has been verified.
    """
    methods_2fa: List[str] = Field([], description="List of two-factor authentication methods enabled for the user.")
    identity_verified: bool = Field(False, description="True if the user's identity is verified.")


class UserDelete(BaseModel):
    """
    Model for user deletion requests.

    Fields:
      - password: The user's password to confirm deletion (8-100 characters).
    """
    password: str = Field(..., min_length=8, max_length=100, description="Password to confirm account deletion (8-100 characters).")


class RegisterInitTOTP(BaseModel):
    """
    Model for initiating Time-based One-Time Password (TOTP) registration.

    Fields:
      - secret: The secret key used for TOTP.
      - uri: The TOTP URI for QR code generation.
    """
    secret: str = Field(..., description="The secret key for TOTP registration.")
    uri: str = Field(..., description="The TOTP URI to generate the QR code.")


class RegisterTOTP(BaseModel):
    """
    Model for completing TOTP registration.

    Fields:
      - success: Indicates whether TOTP registration was successful.
      - backup_codes: A list of backup codes for account recovery.
    """
    success: bool = Field(..., description="True if TOTP registration was successful.")
    backup_codes: List[str] = Field(..., description="List of backup codes for account recovery.")


class RemoveTOTP(BaseModel):
    """
    Model for removing TOTP authentication from a user's account.

    Fields:
      - code: A verification code (up to 6 characters).
      - password: The user's password for confirmation (8-100 characters).
    """
    code: str = Field(..., max_length=6, description="Verification code (up to 6 characters) for removing TOTP.")
    password: str = Field(..., min_length=8, max_length=100, description="Password to confirm TOTP removal (8-100 characters).")


class ChangePassword(BaseModel):
    """
    Model for changing a user's password.

    Fields:
      - new_password: The new password (8-100 characters).
      - old_password: The current password (8-100 characters).
    """
    new_password: str = Field(..., min_length=8, max_length=100, description="The new password (8-100 characters).")
    old_password: str = Field(..., min_length=8, max_length=100, description="The current password (8-100 characters).")


class ChangeEmail(BaseModel):
    """
    Model for changing a user's email address.

    Fields:
      - new_email: The new email address (max 255 characters).
      - password: The user's password to confirm the change (8-100 characters).
    """
    new_email: EmailStr = Field(..., max_length=255, description="The new email address (max 255 characters).")
    password: str = Field(..., min_length=8, max_length=100, description="Password to confirm email change (8-100 characters).")


class ChangeUsername(BaseModel):
    """
    Model for changing a user's username.

    Fields:
      - new_username: The new username (max 50 characters).
      - password: The user's password to confirm the change (8-100 characters).
    """
    new_username: str = Field(..., max_length=50, description="The new username (max 50 characters).")
    password: str = Field(..., min_length=8, max_length=100, description="Password to confirm username change (8-100 characters).")


class UserUpdate(BaseModel):
    """
    Model for updating a user's details.

    At least one of the following fields must be provided:
      - first_name: The user's updated first name (max 100 characters).
      - last_name: The user's updated last name (max 100 characters).
      - address: The user's updated address.
    """
    first_name: Optional[str] = Field(None, max_length=100, description="Updated first name (max 100 characters).")
    last_name: Optional[str] = Field(None, max_length=100, description="Updated last name (max 100 characters).")
    address: Optional[Address] = Field(None, description="Updated address.")

    @model_validator(mode="after")
    def check_at_least_one_field(self) -> "UserUpdate":
        """
        Validates that at least one updateable field is provided.

        Raises:
            ValueError: If none of the fields 'first_name', 'last_name', or 'address' are provided.
        """
        if (
            self.first_name is None and
            self.last_name is None and
            self.address is None
        ):
            raise ValueError(
                "At least one of the fields 'first_name', 'last_name', or 'address' must be provided."
            )
        return self
