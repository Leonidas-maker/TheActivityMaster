from pydantic import BaseModel, Field, ConfigDict, model_validator
from typing import Optional, List, Dict, Union
import uuid

from config.permissions import ClubPermissions

class Permission(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    name: str
    description: str

class GenericRole(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    name: str
    description: str


class ClubRoleCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    level: int = Field(..., gt=0, lt=10)
    name: str = Field(..., max_length=50)
    description: str = Field(..., max_length=255)
    permissions: List[ClubPermissions]


class ClubRole(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    level: int
    name: str
    description: str
    permissions: List[Permission]


class ClubRoleUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=50)
    level: int = Field(..., gt=0, le=10)
    description: Optional[str] = Field(None, max_length=255)
    permissions: Optional[List[ClubPermissions]] = None

    @model_validator(mode="after")
    def check_at_least_one_field(self) -> "ClubRoleUpdate":
        if (
            self.name is None and
            self.description is None and
            self.permissions is None
        ):
            raise ValueError(
                "At least one of the fields 'name', 'description', or 'permissions' must be provided."
            )
        return self


class Roles(BaseModel):
    generic_roles: List[GenericRole]
    club_roles: Dict[uuid.UUID, ClubRole]
