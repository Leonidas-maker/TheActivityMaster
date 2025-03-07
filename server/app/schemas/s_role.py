from pydantic import BaseModel, Field, ConfigDict, model_validator
from typing import Optional, List, Dict
import uuid

from config.permissions import ClubPermissions


class Permission(BaseModel):
    """
    Represents a single permission.

    Fields:
      - name: The name of the permission.
      - description: A brief description of what the permission allows.
    """
    model_config = ConfigDict(from_attributes=True)
    name: str = Field(..., description="The name of the permission.")
    description: str = Field(..., description="A brief description of the permission.")


class GenericRole(BaseModel):
    """
    Represents a generic role used across the application.

    Fields:
      - name: The name of the role.
      - description: A description of the role.
    """
    model_config = ConfigDict(from_attributes=True)
    name: str = Field(..., description="The name of the role.")
    description: str = Field(..., description="A description of the role.")


class ClubRoleCreate(BaseModel):
    """
    Model used for creating a new club role.

    Fields:
      - level: The role level, must be greater than 0 and less than 10.
      - name: The name of the club role (maximum 50 characters).
      - description: A detailed description of the club role (maximum 255 characters).
      - permissions: A list of permissions assigned to this role.
    """
    model_config = ConfigDict(from_attributes=True)
    level: int = Field(..., gt=0, lt=10, description="The role level (must be > 0 and < 10).")
    name: str = Field(..., max_length=50, description="The name of the club role (max 50 characters).")
    description: str = Field(..., max_length=255, description="A description of the club role (max 255 characters).")
    permissions: List[ClubPermissions] = Field(..., description="List of permissions for the club role.")


class ClubRole(BaseModel):
    """
    Represents an existing club role.

    Fields:
      - id: The unique identifier of the club role.
      - level: The role level.
      - name: The name of the role.
      - description: A detailed description of the role.
      - permissions: A list of permissions associated with this role.
    """
    model_config = ConfigDict(from_attributes=True)
    id: int = Field(..., description="The unique identifier of the club role.")
    level: int = Field(..., description="The level of the club role.")
    name: str = Field(..., description="The name of the club role.")
    description: str = Field(..., description="A detailed description of the club role.")
    permissions: List[Permission] = Field(..., description="List of permissions assigned to the club role.")


class ClubRoleUpdate(BaseModel):
    """
    Model for updating an existing club role.

    At least one field must be provided to update.

    Fields:
      - name: (Optional) New name for the role (max 50 characters).
      - level: (Optional) New role level (must be > 0 and ≤ 10).
      - description: (Optional) New description for the role (max 255 characters).
      - permissions: (Optional) Updated list of permissions for the role.
    """
    name: Optional[str] = Field(None, max_length=50, description="New name for the role (max 50 characters).")
    level: Optional[int] = Field(None, gt=0, le=10, description="New role level (must be > 0 and ≤ 10).")
    description: Optional[str] = Field(None, max_length=255, description="New description for the role (max 255 characters).")
    permissions: Optional[List[ClubPermissions]] = Field(
        None, description="Updated list of permissions for the role."
    )

    @model_validator(mode="after")
    def check_at_least_one_field(self) -> "ClubRoleUpdate":
        """
        Validates that at least one updateable field is provided.

        Raises:
            ValueError: If none of the fields 'name', 'description', 'permissions', or 'level' are provided.
        """
        if (
            self.name is None and
            self.description is None and
            self.permissions is None and
            self.level is None
        ):
            raise ValueError(
                "At least one of the fields 'name', 'description', 'permissions', or 'level' must be provided."
            )
        return self


class Roles(BaseModel):
    """
    Represents a collection of roles in a club context.

    Fields:
      - generic_roles: A list of generic roles available in the system.
      - club_roles: A mapping of club UUIDs to their respective club role details.
    """
    generic_roles: List[GenericRole] = Field(..., description="List of generic roles available in the system.")
    club_roles: Dict[uuid.UUID, ClubRole] = Field(..., description="Mapping of club UUID to its club role details.")
