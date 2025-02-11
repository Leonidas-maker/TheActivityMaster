from pydantic import BaseModel, Field
from typing import List
import uuid

from schemas import s_generic


class ClubBase(BaseModel):
    name: str = Field(..., max_length=50)
    description: str = Field(..., max_length=100)
    address: s_generic.Address

class ClubCreate(ClubBase):
    pass

class Club(ClubBase):
    id: uuid.UUID
    owner_ids: List[uuid.UUID]

    class Config:
        orm_mode = True