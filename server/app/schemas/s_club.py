from pydantic import BaseModel, Field, EmailStr, ConfigDict, model_validator
from typing import List, Optional
import uuid

from schemas import s_generic
class Employee(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    first_name: str
    last_name: str
    email: EmailStr


class ClubBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    name: str = Field(..., max_length=50)
    description: str = Field(..., max_length=100)
    address: s_generic.Address

class ClubCreate(ClubBase):
    pass

class Club(ClubBase):
    id: uuid.UUID
class ClubDetails(Club):
    owners: List[Employee]

class ClubUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=50)
    description: Optional[str] = Field(None, max_length=100)
    address: Optional[s_generic.Address] = None

    @model_validator(mode="after")
    def check_at_least_one_field(self) -> "ClubUpdate":
        if (
            self.name is None and
            self.description is None and
            self.address is None
        ):
            raise ValueError(
                "At least one of the fields 'name', 'description', or 'address' must be provided."
            )
        return self
class UserClubRoleAssignment(BaseModel):
    user_ident: str = Field(..., max_length=50)
    level: int = Field(..., gt=0, le=10)

class UserClubRoleChange(BaseModel):
    user_id: uuid.UUID
    level: int = Field(..., ge=0, le=10)

