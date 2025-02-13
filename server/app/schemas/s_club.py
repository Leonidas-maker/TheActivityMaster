from pydantic import BaseModel, Field, EmailStr
from typing import List
import uuid

from schemas import s_generic

class Employee(BaseModel):
    id: uuid.UUID
    first_name: str
    last_name: str
    email: EmailStr


class ClubBase(BaseModel):
    name: str = Field(..., max_length=50)
    description: str = Field(..., max_length=100)
    address: s_generic.Address

class ClubCreate(ClubBase):
    pass

class Club(ClubBase):
    id: uuid.UUID
class ClubDetails(Club):
    owner_ids: List[Employee]
