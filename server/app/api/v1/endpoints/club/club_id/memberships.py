from fastapi import APIRouter, HTTPException, Depends, Request, Query, Path, Body
import uuid
from typing import Union, List, Dict


from controllers import club as club_controller
from schemas import s_club, s_generic, s_payment

from core.generic import EndpointContext
import core.security as core_security

from crud import club as club_crud, role as role_crud

from middleware.general import get_endpoint_context
import middleware.auth as auth_middleware

from utils.exceptions import handle_exception

from config.permissions import ClubPermissions


# Router for club membership endpoints
router = APIRouter()


###########################################################################
################################### Main ##################################
###########################################################################
@router.get("", response_model=List[s_club.Membership], tags=["Club - Membership"])
async def get_memberships_v1(
    club_id: uuid.UUID,
    ep_context: EndpointContext = Depends(get_endpoint_context),
    token_details: core_security.TokenDetails = Depends(auth_middleware.AccessTokenCheckerHybrid()),
):
    try:
        user_id = token_details.user_id if token_details else None
        if user_id and await role_crud.has_user_any_club_permission(
            ep_context.db, user_id, club_id, {ClubPermissions.READ_MEMBERSHIPS}
        ):
            memberships = await club_crud.get_club_memberships(ep_context.db, club_id, only_bookable=False)
        else:
            memberships = await club_crud.get_club_memberships(ep_context.db, club_id, only_bookable=True)
        return [s_club.Membership.model_validate(membership) for membership in memberships]
    except Exception as e:
        await handle_exception(e, ep_context, "Failed to get memberships")


@router.post("", response_model=s_club.Membership, tags=["Club - Membership"])
async def create_membership_v1(
    club_id: uuid.UUID = Path(..., description="The ID of the club to which the membership is to be added"),
    membership: s_club.MembershipCreate = Body(...),
    ep_context: EndpointContext = Depends(get_endpoint_context),
    token_details: core_security.TokenDetails = Depends(
        auth_middleware.AccessTokenChecker(club_permissions=[ClubPermissions.CREATE_MEMBERSHIPS])
    ),
):
    try:
        return await club_controller.create_membership(ep_context, token_details, club_id, membership)
    except Exception as e:
        await handle_exception(e, ep_context, "Failed to create membership")


@router.get("/{membership_id}", response_model=s_club.MembershipDetails, tags=["Club - Membership"])
async def get_membership_v1(
    club_id: uuid.UUID,
    membership_id: uuid.UUID,
    token_details: core_security.TokenDetails = Depends(auth_middleware.AccessTokenCheckerHybrid()),
    ep_context: EndpointContext = Depends(get_endpoint_context),
):
    try:
        user_id = token_details.user_id if token_details else None
        membership = await club_crud.get_user_viewable_membership_by_id(ep_context.db, club_id, membership_id, user_id)
        if not membership:
            raise HTTPException(status_code=404, detail="Membership not found")

        return s_club.MembershipDetails.model_validate(membership)
    except Exception as e:
        await handle_exception(e, ep_context, "Failed to get membership")


@router.put("/{membership_id}", response_model=s_club.Membership, tags=["Club - Membership"])
async def update_membership_v1(
    club_id: uuid.UUID = Path(..., description="The ID of the club to which the membership belongs"),
    membership_id: uuid.UUID = Path(..., description="The ID of the membership to be updated"),
    membership_update: s_club.MembershipUpdate = Body(...),
    ep_context: EndpointContext = Depends(get_endpoint_context),
    token_details: core_security.TokenDetails = Depends(
        auth_middleware.AccessTokenChecker(club_permissions=[ClubPermissions.UPDATE_MEMBERSHIPS])
    ),
):
    try:
        return await club_controller.update_membership(
            ep_context, token_details, club_id, membership_id, membership_update
        )
    except Exception as e:
        await handle_exception(e, ep_context, "Failed to update membership")


@router.delete("/{membership_id}", response_model=s_generic.MessageResponse, tags=["Club - Membership"])
async def delete_membership_v1(
    club_id: uuid.UUID,
    membership_id: uuid.UUID,
    password_form: s_generic.PasswordForm = Body(...),
    ep_context: EndpointContext = Depends(get_endpoint_context),
    token_details: core_security.TokenDetails = Depends(
        auth_middleware.AccessTokenChecker(club_permissions=[ClubPermissions.DELETE_MEMBERSHIPS])
    ),
):
    try:
        await club_controller.delete_membership(
            ep_context, token_details, club_id, membership_id, password_form.password
        )
        return s_generic.MessageResponse(message="Membership deleted")
    except Exception as e:
        await handle_exception(e, ep_context, "Failed to delete membership")


# ======================================================== #
# =================== Membership Access ================== #
# ======================================================== #
@router.post(
    "/{membership_id}/access", response_model=List[s_club.MembershipProgramAccess], tags=["Club - Membership Access"]
)
async def create_membership_access_v1(
    club_id: uuid.UUID = Path(..., description="The ID of the club to which the membership belongs"),
    membership_id: uuid.UUID = Path(..., description="The ID of the membership to be updated"),
    membership_access: List[s_club.MembershipProgramAccessCreate] = Body(
        ..., description="The details of the new membership access"
    ),
    ep_context: EndpointContext = Depends(get_endpoint_context),
    token_details: core_security.TokenDetails = Depends(
        auth_middleware.AccessTokenChecker(club_permissions=[ClubPermissions.UPDATE_MEMBERSHIPS])
    ),
):
    try:
        return await club_controller.create_membership_access(
            ep_context, token_details, club_id, membership_id, membership_access
        )
    except Exception as e:
        await handle_exception(e, ep_context, "Failed to create membership access")


@router.put("/{membership_id}/access", response_model=s_club.MembershipProgramAccess, tags=["Club - Membership Access"])
async def update_membership_access_v1(
    club_id: uuid.UUID = Path(..., description="The ID of the club to which the membership belongs"),
    membership_id: uuid.UUID = Path(..., description="The ID of the membership to be updated"),
    program_id: uuid.UUID = Query(..., description="The ID of the program to be updated"),
    new_additional_fee: int = Query(..., description="The new additional fee for the program"),
    ep_context: EndpointContext = Depends(get_endpoint_context),
    token_details: core_security.TokenDetails = Depends(
        auth_middleware.AccessTokenChecker(club_permissions=[ClubPermissions.UPDATE_MEMBERSHIPS])
    ),
):
    try:
        return await club_controller.update_membership_access(
            ep_context, token_details, club_id, membership_id, program_id, new_additional_fee
        )
    except Exception as e:
        await handle_exception(e, ep_context, "Failed to update membership access")


@router.delete("/{membership_id}/access", response_model=s_generic.MessageResponse, tags=["Club - Membership Access"])
async def delete_membership_access_v1(
    club_id: uuid.UUID = Path(..., description="The ID of the club to which the membership belongs"),
    membership_id: uuid.UUID = Path(..., description="The ID of the membership to be updated"),
    program_id: List[uuid.UUID] = Body(...),
    ep_context: EndpointContext = Depends(get_endpoint_context),
    token_details: core_security.TokenDetails = Depends(
        auth_middleware.AccessTokenChecker(club_permissions=[ClubPermissions.UPDATE_MEMBERSHIPS])
    ),
):
    try:
        await club_controller.delete_membership_access(ep_context, token_details, club_id, membership_id, program_id)
        return s_generic.MessageResponse(message="Membership access deleted")
    except Exception as e:
        await handle_exception(e, ep_context, "Failed to delete membership access")


# ###########################################################################
# ############################## Subscriptions ##############################
# ###########################################################################
@router.post("/{membership_id}/buy", response_model=s_payment.MemberShipsubscriptionResponse, tags=["Club - Membership"])
async def buy_membership_v1(
    club_id: uuid.UUID = Path(..., description="The ID of the club to which the membership belongs"),
    membership_id: uuid.UUID = Path(..., description="The ID of the membership to be updated"),
    ep_context: EndpointContext = Depends(get_endpoint_context),
    token_details: core_security.TokenDetails = Depends(auth_middleware.AccessTokenChecker()),
):
    try:
        return await club_controller.buy_membership(ep_context, token_details, club_id, membership_id)
    except Exception as e:
        await handle_exception(e, ep_context, "Failed to buy membership")


@router.delete("/{membership_id}/cancel", response_model=s_generic.MessageResponse, tags=["Club - Membership"])
async def cancel_membership_v1(
    club_id: uuid.UUID = Path(..., description="The ID of the club to which the membership belongs"),
    membership_id: uuid.UUID = Path(..., description="The ID of the membership to be updated"),
    ep_context: EndpointContext = Depends(get_endpoint_context),
    token_details: core_security.TokenDetails = Depends(auth_middleware.AccessTokenChecker()),
):
    try:
        await club_controller.cancel_membership(ep_context, token_details, club_id, membership_id)
        return s_generic.MessageResponse(message="Membership cancelled")
    except Exception as e:
        await handle_exception(e, ep_context, "Failed to cancel membership")