from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Union
import uuid

from .s_generic import Address

# ======================================================== #
# ========================= Roles ======================== #
# ======================================================== #
class GenericRole(BaseModel):
    name: str
    description: str

class Permission(BaseModel):
    name: str
    description: str

class ClubRole(BaseModel):
    name: str
    description: str
    
    permissions: List[Union[Permission, str]]

class Roles(BaseModel):
    generic_roles: List[GenericRole]
    club_roles: Dict[uuid.UUID, ClubRole]

# ======================================================== #
# ========================= User ========================= #
# ======================================================== #
class UserBase(BaseModel):
    username: str = Field(..., max_length=50)
    email: EmailStr = Field(..., max_length=255)
    first_name: str = Field(..., max_length=100)
    last_name: str = Field(..., max_length=100)
    address: Optional[Address] = None


class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=100)


class User(UserBase):
    id: str
    

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