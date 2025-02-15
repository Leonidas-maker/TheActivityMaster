from pydantic import BaseModel, EmailStr, Field, ConfigDict, model_validator
from typing import Optional, List, Dict, Union
import uuid

from .s_generic import Address



# ======================================================== #
# ========================= User ========================= #
# ======================================================== #
class UserBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    username: str = Field(..., max_length=50)
    email: EmailStr = Field(..., max_length=255)
    first_name: str = Field(..., max_length=100)
    last_name: str = Field(..., max_length=100)
    address: Optional[Address] = None


class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=100)


class User(UserBase):
    id: uuid.UUID
    

class UserDetails(User):
    methods_2fa: List[str] = []
    identity_verified: bool = False


class UserDelete(BaseModel):
    password: str = Field(..., min_length=8, max_length=100)


class RegisterInitTOTP(BaseModel):
    secret: str
    uri: str


class RegisterTOTP(BaseModel):
    success: bool
    backup_codes: List[str]


class RemoveTOTP(BaseModel):
    code: str = Field(..., max_length=6)
    password: str = Field(..., min_length=8, max_length=100)


class ChangePassword(BaseModel):
    new_password: str = Field(..., min_length=8, max_length=100)
    old_password: str = Field(..., min_length=8, max_length=100)

class ChangeEmail(BaseModel):
    new_email: EmailStr = Field(..., max_length=255)
    password: str = Field(..., min_length=8, max_length=100)

class ChangeUsername(BaseModel):
    new_username: str = Field(..., max_length=50)
    password: str = Field(..., min_length=8, max_length=100)

class UserUpdate(BaseModel):
    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    address: Optional[Address] = None

    @model_validator(mode="after")
    def check_at_least_one_field(self) -> "UserUpdate":
        if (
            self.first_name is None and
            self.last_name is None and
            self.address is None
        ):
            raise ValueError(
                "At least one of the fields 'first_name', 'last_name', or 'address' must be provided."
            )
        return self