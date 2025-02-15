from fastapi import APIRouter, HTTPException, Depends, Request
import uuid
from typing import List

from controllers import club as club_controller
from schemas import s_club, s_generic, s_user

from core.generic import EndpointContext
import core.security as core_security

from crud import club as club_crud, role as role_crud

from middleware.general import get_endpoint_context
import middleware.auth as auth_middleware

from utils.exceptions import handle_exception

from config.permissions import ClubPermissions

from schemas import s_role


# Router for club role endpoints
router = APIRouter()


@router.post("", response_model=s_role.ClubRole, tags=["Club - Role"])
async def create_club_role_v1(
    club_id: uuid.UUID,
    club_role_create: s_role.ClubRoleCreate,
    ep_context: EndpointContext = Depends(get_endpoint_context),
    token_details: core_security.TokenDetails = Depends(
        auth_middleware.AccessTokenChecker(club_permissions=[ClubPermissions.MODIFY_ROLES])
    ),
):
    try:
        return await club_controller.create_club_role(ep_context, token_details, club_id, club_role_create)
    except Exception as e:
        await handle_exception(e, ep_context, "Failed to create club role")


@router.get("", response_model=List[s_role.ClubRole], tags=["Club - Role"])
async def get_club_roles_v1(
    club_id: uuid.UUID,
    ep_context: EndpointContext = Depends(get_endpoint_context),
    token_details: core_security.TokenDetails = Depends(
        auth_middleware.AccessTokenChecker(
            club_permissions=[ClubPermissions.READ_ROLES, ClubPermissions.MODIFY_ROLES, ClubPermissions.DELETE_ROLES]
        )
    ),
):
    try:
        roles = await role_crud.get_club_roles(ep_context.db, club_id)
        return [s_role.ClubRole.model_validate(role) for role in roles]
    except Exception as e:
        await handle_exception(e, ep_context, "Failed to get club roles")


@router.get("/{role_id}", response_model=s_role.ClubRole, tags=["Club - Role"])
async def get_club_role_v1(
    club_id: uuid.UUID, role_id: int, ep_context: EndpointContext = Depends(get_endpoint_context)
):
    try:
        club_role = await role_crud.get_club_role(ep_context.db, club_id, role_id=role_id, with_details=True)
        if not club_role:
            raise HTTPException(status_code=404, detail="Club role not found")
        return s_role.ClubRole.model_validate(club_role)
    except Exception as e:
        await handle_exception(e, ep_context, "Failed to get club role")


@router.put("/{role_id}", response_model=s_role.ClubRole, tags=["Club - Role"])
async def update_club_role_v1(
    club_id: uuid.UUID,
    role_id: int,
    club_role_update: s_role.ClubRoleUpdate,
    ep_context: EndpointContext = Depends(get_endpoint_context),
    token_details: core_security.TokenDetails = Depends(
        auth_middleware.AccessTokenChecker(club_permissions=[ClubPermissions.MODIFY_ROLES])
    ),
):
    try:
        return await club_controller.update_club_role(ep_context, token_details, club_id, role_id, club_role_update)
    except Exception as e:
        await handle_exception(e, ep_context, "Failed to update club role")


@router.delete("/{role_id}", response_model=s_generic.MessageResponse, tags=["Club - Role"])
async def delete_club_role_v1(
    club_id: uuid.UUID,
    role_id: int,
    ep_context: EndpointContext = Depends(get_endpoint_context),
    token_details: core_security.TokenDetails = Depends(
        auth_middleware.AccessTokenChecker(club_permissions=[ClubPermissions.DELETE_ROLES])
    ),
):
    try:
        await club_controller.delete_club_role(ep_context, token_details, club_id, role_id)
        return {"message": "Club role deleted successfully."}
    except Exception as e:
        await handle_exception(e, ep_context, "Failed to delete club role")


@router.get("/{role_id}/members", tags=["Club - Role"])
async def get_club_role_members_v1(
    club_id: uuid.UUID,
    role_id: int,
    ep_context: EndpointContext = Depends(get_endpoint_context),
    token_details: core_security.TokenDetails = Depends(
        auth_middleware.AccessTokenChecker(club_permissions=[ClubPermissions.READ_ROLES])
    ),
):
    try:
        members = await role_crud.get_club_role_members(ep_context.db, club_id, role_id)
        return [s_club.Employee.model_validate(member) for member in members]

    except Exception as e:
        await handle_exception(e, ep_context, "Failed to get club role members")
