from pydantic import BaseModel, EmailStr
from typing import Optional, List


from .s_generic import Address


class UserBase(BaseModel):
    username: str
    email: EmailStr
    first_name: str
    last_name: str
    address: Optional[Address] = None


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: str

    class Config:
        from_attributes = True

class UserDelete(BaseModel):
    password: str

class RegisterInitTOTP(BaseModel):
    secret: str
    uri: str


class RegisterTOTP(BaseModel):
    success: bool
    backup_codes: List[str]


class RemoveTOTP(BaseModel):
    code: str
    password: str


class ChangePassword(BaseModel):
    new_password: str
    old_password: str
