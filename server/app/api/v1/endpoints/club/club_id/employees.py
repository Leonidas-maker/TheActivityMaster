from fastapi import APIRouter, HTTPException, Depends, Request, Query, Path, Body
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

@router.get("/all", response_model=Dict[str, List[s_club.Employee]]	, tags=["Club - Employee"])
async def get_employees_v1(
    club_id: uuid.UUID = Path(..., description="The ID of the club"),
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

@router.get(f"", response_model=s_club.EmployeeResponse, tags=["Club - Employee"])
async def get_employee_v1(
    club_id: uuid.UUID = Path(..., description="The ID of the club"),
    user_id: uuid.UUID = Query(..., description="The User ID of the employee"),
    ep_context: EndpointContext = Depends(get_endpoint_context),
    token_details: core_security.TokenDetails = Depends(
        auth_middleware.AccessTokenChecker(
            club_permissions=[
                ClubPermissions.READ_EMPLOYEES
            ]
        )
    ),
):
    """Get all employees of a club"""
    try:
        user_club_roles = await club_crud.get_club_employee_by_id(ep_context.db, club_id, user_id)

        if not user_club_roles:
            raise HTTPException(status_code=404, detail="This user is not an employee of this club")

        return s_club.EmployeeResponse(
            role_name=user_club_roles.club_role.name,
            role_level=user_club_roles.club_role.level,
            id=user_club_roles.user.id,
            first_name=user_club_roles.user.first_name,
            last_name=user_club_roles.user.last_name,
            email=user_club_roles.user.email,
        )
    except Exception as e:
        await handle_exception(e, ep_context, "Failed to get employees")

@router.post("", response_model=s_generic.MessageResponse, tags=["Club - Employee"])
async def add_employee_v1(
    club_id: uuid.UUID = Path(..., description="The ID of the club"),
    role_assignment: s_club.UserClubRoleAssignment = Body(..., description="The role assignment data"),
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
    club_id: uuid.UUID = Path(..., description="The ID of the club"),
    role_change: s_club.UserClubRoleChange = Body(..., description="The role change data"),
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
    club_id: uuid.UUID = Path(..., description="The ID of the club"),
    user_id: uuid.UUID = Query(..., description="The ID of the user to remove from the role"),
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