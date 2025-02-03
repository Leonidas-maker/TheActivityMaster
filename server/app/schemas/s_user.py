from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List


from .s_generic import Address


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

    class Config:
        from_attributes = True

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

