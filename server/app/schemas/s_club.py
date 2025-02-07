from pydantic import BaseModel, Field

from schemas import s_generic

class ClubBase(BaseModel):
    name: str = Field(..., max_length=50)
    description: str = Field(..., max_length=100)
    address: s_generic.Address

class ClubCreate(ClubBase):
    pass

class Club(ClubBase):
    id: int
    owner_id: int

    class Config:
        orm_mode = True