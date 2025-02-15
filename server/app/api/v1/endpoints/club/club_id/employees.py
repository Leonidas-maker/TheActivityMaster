from fastapi import APIRouter, HTTPException, Depends, Request, Query
import uuid
from typing import Union, List, Dict


from controllers import club as club_controller
from schemas import s_club, s_generic

from core.generic import EndpointContext
import core.security as core_security

from crud import club as club_crud

from middleware.general import get_endpoint_context
import middleware.auth as auth_middleware

from utils.exceptions import handle_exception

from config.permissions import ClubPermissions

router = APIRouter()

@router.get("", response_model=Dict[str, List[s_club.Employee]]	, tags=["Club - Employee"])
async def get_employees_v1(
    club_id: uuid.UUID,
    ep_context: EndpointContext = Depends(get_endpoint_context),
    token_details: core_security.TokenDetails = Depends(
        auth_middleware.AccessTokenChecker(
            club_permissions=[
                ClubPermissions.READ_EMPLOYEES,
                ClubPermissions.MODIFY_EMPLOYEES,
                ClubPermissions.DELETE_EMPLOYEES,
            ]
        )
    ),
):
    """Get all employees of a club"""
    try:
        club_roles = await club_crud.get_club_employees(ep_context.db, club_id)
        employees = {}
        for role in club_roles:
            employees[role.name] = [s_club.Employee.model_validate(user_club_role.user) for user_club_role in role.user_club_roles]
        
        return employees
    except Exception as e:
        await handle_exception(e, ep_context, "Failed to get employees")


@router.post("", response_model=s_generic.MessageResponse, tags=["Club - Employee"])
async def add_employee_v1(
    club_id: uuid.UUID,
    role_assignment: s_club.UserClubRoleAssignment,
    ep_context: EndpointContext = Depends(get_endpoint_context),
    token_details: core_security.TokenDetails = Depends(
        auth_middleware.AccessTokenChecker(club_permissions=[ClubPermissions.MODIFY_EMPLOYEES])
    ),
):
    """Assign a user to a club role"""
    try:
        await club_controller.add_employee(ep_context, token_details, club_id, role_assignment)
        return s_generic.MessageResponse(message="Role assigned successfully")
    except Exception as e:
        await handle_exception(e, ep_context, "Failed to add employee")


@router.put("", tags=["Club - Employee"])
async def update_employee_v1(
    club_id: uuid.UUID,
    role_change: s_club.UserClubRoleChange,
    ep_context: EndpointContext = Depends(get_endpoint_context),
    token_details: core_security.TokenDetails = Depends(
        auth_middleware.AccessTokenChecker(club_permissions=[ClubPermissions.MODIFY_EMPLOYEES])
    ),
):
    """Update a user's role in a club"""
    try:
        await club_controller.update_employee(ep_context, token_details, club_id, role_change)
        return s_generic.MessageResponse(message="Role updated successfully")
    except Exception as e:
        await handle_exception(e, ep_context, "Failed to update employee")


@router.delete("", response_model=s_generic.MessageResponse, tags=["Club - Employee"])
async def remove_club_role_v1(
    club_id: uuid.UUID,
    user_id: uuid.UUID,
    ep_context: EndpointContext = Depends(get_endpoint_context),
    token_details: core_security.TokenDetails = Depends(
        auth_middleware.AccessTokenChecker(club_permissions=[ClubPermissions.DELETE_EMPLOYEES])
    ),
):
    """Remove a user from a club role"""
    try:
        await club_controller.remove_employee(ep_context, token_details, club_id, user_id)
        return s_generic.MessageResponse(message="Role removed successfully")
    except Exception as e:
        await handle_exception(e, ep_context, "Failed to remove employee")