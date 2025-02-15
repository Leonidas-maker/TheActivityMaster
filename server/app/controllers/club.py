from fastapi import HTTPException
from typing import Tuple
import uuid
from sqlalchemy import select, delete
from typing import List, Union, Optional

from config.settings import DEBUG, DEFAULT_TIMEZONE
from config.permissions import ClubPermissions

from models import m_user, m_club
from schemas import s_club, s_generic, s_role

from crud import (
    verification as verification_crud,
    club as club_crud,
    user as user_crud,
    role as role_crud,
)

from core.generic import EndpointContext
import core.security as core_security


async def create_club(
    ep_context: EndpointContext, token_details: core_security.TokenDetails, club_create: s_club.ClubCreate
) -> s_club.Club:
    """Create a club

    :param ep_context: The endpoint context containing database and logger
    :param token_details: The token details of the authenticated user
    :param club_create: The data to create a new club
    :raises HTTPException: If the user identity is not verified
    :return: The created club object
    """
    db = ep_context.db
    audit_log = ep_context.audit_logger
    user_id = token_details.user_id

    if not await verification_crud.is_user_identity_verified(db, user_id) and not await role_crud.is_user_elevated(
        db, user_id
    ):
        raise HTTPException(status_code=403, detail="User identity not verified")

    club = await club_crud.create_club(db, user_id, club_create)

    audit_log.club_created(user_id, club.id)

    response = s_club.Club.model_validate(club)
    await db.commit()
    return response


async def get_club(
    ep_context: EndpointContext,
    club_id: uuid.UUID,
) -> m_user.Club:
    """Get a club by ID

    :param ep_context: The endpoint context containing database and logger
    :param token_details: The token details of the authenticated user
    :param club_id: The ID of the club to get
    :raises HTTPException: If the user is not a member of the club
    :return: The club with the given ID
    """
    db = ep_context.db
    club = await club_crud.get_club_with_owners(db, club_id)

    if not club:
        raise HTTPException(status_code=404, detail="Club not found")

    return club


async def update_club(
    ep_context: EndpointContext,
    token_details: core_security.TokenDetails,
    club_id: uuid.UUID,
    club_update: s_club.ClubUpdate,
) -> s_club.Club:
    """Update a club

    :param ep_context: The endpoint context containing database and logger
    :param club_id: The ID of the club to update
    :param club_update: The data to update a club
    :return: The updated club object
    """
    db = ep_context.db
    user_id = token_details.user_id
    try:
        club = await club_crud.update_club(ep_context, club_id, club_update, user_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    response = s_club.Club.model_validate(club)
    await db.commit()
    return response


###########################################################################
################################ Club Role ################################
###########################################################################
async def create_club_role(
    ep_context: EndpointContext,
    token_details: core_security.TokenDetails,
    club_id: uuid.UUID,
    club_role_create: s_role.ClubRoleCreate,
) -> s_role.ClubRole:
    """Add a role to a club

    :param ep_context: The endpoint context containing database and logger
    :param club_id: The ID of the club
    :param club_role: The role to add to the club
    :return: The added club role
    """
    db = ep_context.db
    audit_log = ep_context.audit_logger
    issuer_id = token_details.user_id

    if len(club_role_create.permissions) == 0:
        raise HTTPException(status_code=400, detail="Please provide permissions")

    if await role_crud.club_role_exists(db, club_id, club_role_create.name, club_role_create.level):
        raise HTTPException(status_code=400, detail="Role name or level already exists")

    if not await role_crud.has_user_higher_club_level(db, issuer_id, club_id, level=club_role_create.level):
        raise HTTPException(status_code=403, detail="User has higher or equal level than role")

    permissions = await role_crud.get_permissions(db, names=club_role_create.permissions)
    if len(permissions) != len(club_role_create.permissions):
        raise HTTPException(status_code=400, detail="Invalid permissions")

    new_role = await role_crud.add_club_role(
        db, club_id, club_role_create.name, club_role_create.description, club_role_create.level, permissions
    )

    audit_log.club_role_added(issuer_id, club_id, new_role.id)

    response = s_role.ClubRole.model_validate(new_role)

    await db.commit()
    return response


async def update_club_role(
    ep_context: EndpointContext,
    token_details: core_security.TokenDetails,
    club_id: uuid.UUID,
    role_id: int,
    club_role_update: s_role.ClubRoleUpdate,
) -> s_role.ClubRole:
    """Update a role in a club

    :param ep_context: The endpoint context containing database and logger
    :param club_id: The ID of the club
    :param role_id: The ID of the role to update
    :param club_role: The updated role data
    :return: The updated club role
    """
    db = ep_context.db
    audit_log = ep_context.audit_logger
    issuer_id = token_details.user_id

    club_role = await role_crud.get_club_role(db, club_id, role_id=role_id, with_details=True)

    if not club_role:
        raise HTTPException(status_code=404, detail="Role not found")

    if not await role_crud.has_user_higher_club_level(db, issuer_id, club_id, level=club_role.level):
        raise HTTPException(status_code=403, detail="User has higher or equal level than role")

    details = ""
    if club_role_update.name and club_role.name != club_role_update.name:
        details += f"Name: {club_role.name} -> {club_role_update.name}"
        club_role.name = club_role_update.name

    if club_role_update.description and club_role.description != club_role_update.description:
        details += f"Description: {club_role.description} -> {club_role_update.description}"
        club_role.description = club_role_update.description

    if club_role_update.permissions and club_role.permissions != club_role_update.permissions:
        permission_details = ""
        permissions_db = await role_crud.get_permissions(db, "club")
        available_permissions = dict([(permission.name, permission) for permission in permissions_db])

        old_permissions = set([permission.name for permission in club_role.permissions])

        for permission in club_role_update.permissions:
            if permission.value not in available_permissions.keys():
                raise HTTPException(status_code=400, detail=f"Invalid permission: {permission.value }")

            if permission.value not in old_permissions:
                club_role.permissions.append(available_permissions[permission.value])
                permission_details += f"+{permission.value}"
            else:
                old_permissions.remove(permission.value)

        for permission in old_permissions:
            club_role.permissions.remove(available_permissions[permission])
            permission_details += f"-{permission}"

        if permission_details:
            details += f"; Permissions: {permission_details}"

    audit_log.club_role_updated(issuer_id, club_id, role_id, details)

    result = s_role.ClubRole.model_validate(club_role)
    await db.commit()
    return result


async def delete_club_role(
    ep_context: EndpointContext,
    token_details: core_security.TokenDetails,
    club_id: uuid.UUID,
    role_id: int,
) -> None:
    """Delete a role from a club

    :param ep_context: The endpoint context containing database and logger
    :param club_id: The ID of the club
    :param role_id: The ID of the role to delete
    :return: None
    """
    db = ep_context.db
    audit_log = ep_context.audit_logger
    issuer_id = token_details.user_id

    if not await role_crud.has_user_higher_club_level(db, issuer_id, club_id):
        raise HTTPException(status_code=403, detail="User has higher or equal level than role")

    user_club_roles = await role_crud.get_user_club_roles(db, club_id, role_id)

    if user_club_roles:
        raise HTTPException(status_code=403, detail="Role is assigned to users")

    await role_crud.delete_club_role(db, club_id, role_id)
    audit_log.club_role_deleted(issuer_id, club_id, role_id)

    await db.commit()


###########################################################################
################################# Employee ################################
###########################################################################
async def add_employee(
    ep_context: EndpointContext,
    token_details: core_security.TokenDetails,
    club_id: uuid.UUID,
    role_assignment: s_club.UserClubRoleAssignment,
) -> None:
    """Assign a user to a club role

    :param ep_context: The endpoint context containing database and logger
    :param club_id: The ID of the club
    :param level: The level of the role
    :param user_id: The ID of the user to assign the role to
    :return: The assigned user club role
    """
    db = ep_context.db
    audit_log = ep_context.audit_logger
    issuer_id = token_details.user_id

    club_role = await role_crud.get_club_role(db, club_id, level=role_assignment.level)

    if not club_role:
        raise HTTPException(status_code=404, detail="Role not found")

    user = await user_crud.get_user_by_ident(db, role_assignment.user_ident)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if issuer_id == user.id:
        raise HTTPException(status_code=400, detail="Cannot assign role to self")

    if await role_crud.is_user_employee_of_club(db, user.id, club_id):
        raise HTTPException(
            status_code=403,
            detail="User is already an employee of the club. Please use the put method to update the role",
        )

    if not await role_crud.has_user_higher_club_level(db, issuer_id, club_id, level=club_role.level):
        raise HTTPException(status_code=403, detail="User or Role has higher or equal level than issuer")

    await role_crud.add_employee(db, club_id, club_role.id, user.id)
    audit_log.club_employee_added(token_details.user_id, club_id, user.id, club_role.id)

    await db.commit()


async def update_employee(
    ep_context: EndpointContext,
    token_details: core_security.TokenDetails,
    club_id: uuid.UUID,
    role_assignment: s_club.UserClubRoleChange,
) -> None:
    """Update a user's role in a club

    :param ep_context: The endpoint context containing database and logger
    :param club_id: The ID of the club
    :param level: The level of the role
    :param user_id: The ID of the user to update the role for
    :return: None
    """
    db = ep_context.db
    audit_log = ep_context.audit_logger
    issuer_id = token_details.user_id

    if not await role_crud.is_user_employee_of_club(db, role_assignment.user_id, club_id):
        raise HTTPException(status_code=403, detail="User is not an employee of the club")

    club_role_id = await role_crud.get_club_role_id(db, club_id, level=role_assignment.level)

    if not club_role_id:
        raise HTTPException(status_code=404, detail="Role not found")

    if not await role_crud.has_user_higher_club_level(
        db, issuer_id, club_id, to_user_id=role_assignment.user_id, level=role_assignment.level
    ):
        raise HTTPException(status_code=403, detail="User or Role has higher or equal level than issuer")

    old_club_role_id = await role_crud.update_employee(db, club_id, role_assignment.user_id, club_role_id)
    audit_log.club_employee_updated(issuer_id, club_id, role_assignment.user_id, old_club_role_id, club_role_id)

    await db.commit()


async def remove_employee(
    ep_context: EndpointContext,
    token_details: core_security.TokenDetails,
    club_id: uuid.UUID,
    user_id: uuid.UUID,
) -> None:
    """Remove a user from a club role

    :param ep_context: The endpoint context containing database and logger
    :param club_id: The ID of the club
    :param level: The level of the role
    :param user_id: The ID of the user to remove the role from
    :return: None
    """
    db = ep_context.db
    audit_log = ep_context.audit_logger
    issuer_id = token_details.user_id

    if issuer_id == user_id:
        raise HTTPException(status_code=400, detail="Cannot remove role from self")

    if not await role_crud.is_user_employee_of_club(db, issuer_id, club_id):
        raise HTTPException(status_code=403, detail="User is not an employee of the club")

    if not await role_crud.has_user_higher_club_level(db, issuer_id, club_id, user_id):
        raise HTTPException(status_code=403, detail="Cannot remove role from user with higher level")

    await role_crud.remove_employee(db, club_id, user_id)
    audit_log.club_employee_removed(issuer_id, club_id, user_id, 0)
    await db.commit()
