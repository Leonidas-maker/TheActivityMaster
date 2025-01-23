from calendar import c
from pydantic import BaseModel, EmailStr
from typing import Optional


from .s_generic import Address

class UserBase(BaseModel):
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
