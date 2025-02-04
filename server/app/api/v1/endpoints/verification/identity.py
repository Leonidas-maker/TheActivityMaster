from fastapi import APIRouter, Depends, Request, Header, File, UploadFile, HTTPException
from fastapi.responses import FileResponse
import uuid
from typing import List, Optional
import os

from controllers import verification as verification_controller

from schemas import s_verification, s_generic

import core.security as core_security
from core.generic import EndpointContext

from middleware.general import get_endpoint_context
import middleware.auth as auth_middleware

from utils.exceptions import handle_exception

from config import settings

router = APIRouter()

@router.post(
    "/submit_identity_verification", response_model=s_generic.MessageResponse, tags=["Verification - Identity"]
)
async def submit_identity_verification_v1(
    verification_data: s_verification.IdentityVerificationRequest = Depends(
        s_verification.IdentityVerificationRequest.as_form
    ),
    image_files: List[UploadFile] = File(max_length=3 * 1024 * 1024),
    token_details: core_security.TokenDetails = Depends(auth_middleware.AccessTokenChecker()),
    ep_context: EndpointContext = Depends(get_endpoint_context),
):
    """Submit an identity verification"""
    try:
        await verification_controller.submit_identity_verification(
            ep_context, verification_data, image_files, token_details.user_id
        )
        return {"message": "Identity verification submitted"}
    except Exception as e:
        await handle_exception(e, ep_context, "Failed to submit identity verification")


@router.post(
    "/approve",
    response_model=s_generic.MessageResponse,
    tags=["Verification - Identity [Elevated]"],
)
async def approve_identity_verification_v1(
    verification_id: uuid.UUID,
    token_details: core_security.TokenDetails = Depends(auth_middleware.AccessTokenChecker(["admin"])),
    ep_context: EndpointContext = Depends(get_endpoint_context),
):
    """Approve an identity verification"""
    try:
        await verification_controller.approve_identity_verification(ep_context, token_details, verification_id)
        return {"message": "Identity verification approved"}
    except Exception as e:
        await handle_exception(e, ep_context, "Failed to approve identity verification")


@router.post(
    "/reject",
    response_model=s_generic.MessageResponse,
    tags=["Verification - Identity [Elevated]"],
)
async def reject_identity_verification_v1(
    reject_details: s_verification.IdentityVerificationRejectRequest,
    token_details: core_security.TokenDetails = Depends(auth_middleware.AccessTokenChecker(["admin"])),
    ep_context: EndpointContext = Depends(get_endpoint_context),
):
    """Reject an identity verification"""
    try:
        await verification_controller.reject_identity_verification(ep_context, token_details, reject_details)
        return {"message": "Identity verification rejected"}
    except Exception as e:
        await handle_exception(e, ep_context, "Failed to reject identity verification")


@router.get(
    "/pending",
    response_model=List[s_verification.PendingIdentityVerificationResponse],
    tags=["Verification - Identity [Elevated]"],
)
async def get_pending_verifications_v1(
    ep_context: EndpointContext = Depends(get_endpoint_context),
    token_details: core_security.TokenDetails = Depends(auth_middleware.AccessTokenChecker(["admin"])),
):
    """Get all pending identity verifications"""
    try:
        pending_identity_verifications = await verification_controller.get_pending_identity_verifications(
            ep_context, token_details
        )

        response = []
        for verification in pending_identity_verifications:
            response.append(
                s_verification.PendingIdentityVerificationResponse(id=verification[0], user_id=verification[1])
            )
        return response

    except Exception as e:
        await handle_exception(e, ep_context, "Failed to get pending identity verifications")


@router.get(
    "/get/{verification_id}",
    response_model=s_verification.IdentityVerificationDetailsResponse,
    tags=["Verification - Identity [Elevated]"],
)
async def get_identity_verification_details_v1(
    verification_id: uuid.UUID,
    ep_context: EndpointContext = Depends(get_endpoint_context),
    token_details: core_security.TokenDetails = Depends(auth_middleware.AccessTokenChecker(["admin"])),
):
    """Get the details of an identity verification"""
    try:
        verification = await verification_controller.get_identity_verification_details(
            ep_context, token_details, verification_id
        ) 
        return verification

    except Exception as e:
        await handle_exception(e, ep_context, "Failed to get identity verification details")


@router.get("/get/{verification_id}/image", tags=["Verification - Identity [Elevated]"])
async def get_identity_verification_image_v1(
    verification_id: uuid.UUID,
    index: int = 0,
    ep_context: EndpointContext = Depends(get_endpoint_context),
    token_details: core_security.TokenDetails = Depends(auth_middleware.AccessTokenChecker(["admin"])),
):
    """Get the image of an identity verification

    Note:
        index: 0 for front image, 1 for back image, 2 for selfie image, defaults to 0
    """
    try:
        file_name = await verification_controller.get_identity_verification_image(ep_context, verification_id, index)
        if not os.path.exists(file_name):
            raise HTTPException(status_code=404, detail="Image not found")
        return FileResponse(file_name)
    except Exception as e:
        await handle_exception(e, ep_context, "Failed to get identity verification image")


@router.get(
    "/self", response_model=s_verification.IdentityVerificationStatusResponse, tags=["Verification - Identity"]
)
async def get_self_identity_verification_status_v1(
    ep_context: EndpointContext = Depends(get_endpoint_context),
    token_details: core_security.TokenDetails = Depends(auth_middleware.AccessTokenChecker()),
):
    """Get the status of the user's identity verification"""
    try:
        verification_status = await verification_controller.get_self_identity_verification_status(
            ep_context, token_details
        )
        return s_verification.IdentityVerificationStatusResponse(
            id=verification_status[0],
            status=verification_status[1],
            created_at=verification_status[2],
            updated_at=verification_status[3],
            expires_at=verification_status[4],
        )
    except Exception as e:
        await handle_exception(e, ep_context, "Failed to get self identity verification status")


@router.delete("/self", response_model=s_generic.MessageResponse, tags=["Verification - Identity"])
async def delete_self_identity_verification_v1(
    ep_context: EndpointContext = Depends(get_endpoint_context),
    token_details: core_security.TokenDetails = Depends(auth_middleware.AccessTokenChecker()),
):
    """Soft delete the user's identity verification"""
    try:
        await verification_controller.delete_self_identity_verification(ep_context, token_details)
        return {"message": "Identity will be deleted soon"}
    except Exception as e:
        await handle_exception(e, ep_context, "Failed to delete self identity verification")
