from fastapi import HTTPException, UploadFile
import uuid
from typing import List, Tuple
import datetime

from schemas import s_verification
from models import m_verification

from crud import verification as verification_crud
from crud import user as user_crud

from core.generic import EndpointContext
import core.security as core_security
import core.verification as core_verification

from config import settings


async def verify_email(ep_context: EndpointContext, user_id: str, expire: str, signature: str) -> None:
    """
    Verify the email of a user

    :param ep_context: The endpoint context
    :param code: The verification code
    """
    db = ep_context.db

    with core_security.email_verify_manager_dependency.get() as evm:
        if not evm.verify(user_id, expire, signature):
            raise HTTPException(status_code=400, detail="Invalid email verification code")

    # Get the user
    user = await user_crud.get_user_by_id(db, uuid.UUID(user_id))

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Verify the email
    for role in user.generic_roles:
        if role.name == "NotEmailVerified":
            user.generic_roles.remove(role)
            await db.commit()
            break


###########################################################################
################################# Identity ################################
###########################################################################
async def submit_identity_verification(
    ep_context: EndpointContext,
    verification_data: s_verification.IdentityVerificationRequest,
    image_files: List[UploadFile],
    user_id: uuid.UUID,
):
    db = ep_context.db
    audit_logger = ep_context.audit_logger

    # Check the images
    if len(image_files) > 3:
        raise HTTPException(status_code=400, detail="Too many files uploaded")

    for file in image_files:
        if not file.filename:
            raise HTTPException(status_code=400, detail="Image file name is required")
        if file.filename.split(".")[-1] != "png":
            raise HTTPException(status_code=400, detail="Invalid image type (only PNG allowed)")
        if file.filename.split(".")[0] not in ["front", "rear", "selfie"]:
            raise HTTPException(status_code=400, detail="Invalid image name")

    # Check if a verification is already pending or approved
    existing = await verification_crud.get_identity_verification_by_user(db, user_id, only_active=True)
    if existing:
        raise HTTPException(
            status_code=400, detail="An identity verification is already pending or approved for this user"
        )

    # Save the images
    image_path = core_verification.write_identification_verification(user_id, image_files)

    # Save details
    with core_security.ec_encryptor_dependency.get() as ec_encryptor:
        verification_data.id_card_mrz = ec_encryptor.encrypt(verification_data.id_card_mrz)

    new_verification = await verification_crud.create_identity_verification(db, user_id, verification_data, image_path)

    # Log the submission
    audit_logger.id_verification_submitted(user_id, new_verification.id)

    await db.commit()
    return new_verification


async def get_self_identity_verification_status(
    ep_context: EndpointContext, token_details: core_security.TokenDetails
) -> Tuple[uuid.UUID, str, datetime.datetime, datetime.datetime, datetime.datetime]:
    db = ep_context.db
    audit_logger = ep_context.audit_logger

    # Get the verification
    verification = await verification_crud.get_identity_verification_by_user(db, token_details.user_id, False)

    if not verification:
        raise HTTPException(status_code=404, detail="Identity verification not found")

    verification_status = (
        verification.id,
        verification.status.value,
        verification.created_at,
        verification.updated_at,
        verification.expires_at,
    )

    # Log self retrieval
    audit_logger.id_verification_retrieved(token_details.user_id, token_details.user_id)
    await db.commit()

    return verification_status


###########################################################################
################################# Approval ################################
###########################################################################
async def approve_identity_verification(
    ep_context: EndpointContext, token_details: core_security.TokenDetails, verification_id: uuid.UUID
):
    db = ep_context.db
    audit_logger = ep_context.audit_logger

    # Approve the verification
    verification = await verification_crud.purge_sensitive_fields(db, verification_id, approved=True)

    # Clear the images
    core_verification.clear_identification_verification(verification.user_id, throw_error=True)

    # Log the approval
    audit_logger.id_verification_approved(token_details.user_id, verification.user_id)

    await db.commit()


async def reject_identity_verification(
    ep_context: EndpointContext,
    token_details: core_security.TokenDetails,
    reject_details: s_verification.IdentityVerificationRejectRequest,
):
    db = ep_context.db
    audit_logger = ep_context.audit_logger

    # Reject the verification
    verification = await verification_crud.purge_sensitive_fields(
        db, reject_details.identity_verification_id, approved=False
    )

    # Clear the images
    core_verification.clear_identification_verification(verification.user_id, throw_error=True)

    # Log the rejection
    audit_logger.id_verification_rejected(token_details.user_id, verification.user_id, reject_details.reason)

    await db.commit()


async def get_pending_identity_verifications(
    ep_context: EndpointContext, token_details: core_security.TokenDetails
) -> List[Tuple[uuid.UUID, uuid.UUID]]:
    db = ep_context.db
    audit_logger = ep_context.audit_logger

    # Get the pending verifications
    pending_verifications = await verification_crud.get_pending_identity_verifications(db)

    # Log the retrieval
    audit_logger.id_verification_pending_retrieved(token_details.user_id)
    await db.commit()

    return pending_verifications


async def get_identity_verification_details(
    ep_context: EndpointContext, token_details: core_security.TokenDetails, verification_id: uuid.UUID
) -> s_verification.IdentityVerificationDetailsResponse:
    db = ep_context.db
    audit_logger = ep_context.audit_logger

    # Get the verification details
    identity_verification = await verification_crud.get_identity_verification_by_id(db, verification_id)

    if not identity_verification:
        raise HTTPException(status_code=404, detail="Identity verification not found")

    response = s_verification.IdentityVerificationDetailsResponse.model_validate(identity_verification)

    # Log the retrieval
    audit_logger.id_verification_retrieved(token_details.user_id, identity_verification.user_id)
    await db.commit()

    return response


async def get_identity_verification_image(ep_context: EndpointContext, verification_id: uuid.UUID, index: int) -> str:
    db = ep_context.db
    audit_logger = ep_context.audit_logger

    # Get the image name
    match index:
        case 0:
            image = "front.png"
        case 1:
            image = "rear.png"
        case 2:
            image = "selfie.png"
        case _:
            raise HTTPException(status_code=400, detail="Invalid image index")

    # Get the verification
    verification = await verification_crud.get_identity_verification_by_id(db, verification_id)

    if not verification:
        raise HTTPException(status_code=404, detail="Identity verification not found")

    image_path = f"{verification.image_url}/{image}"

    # Log the retrieval
    audit_logger.id_verification_image_retrieved(verification.user_id, verification_id, image)
    await db.commit()

    return image_path


async def delete_self_identity_verification(ep_context: EndpointContext, token_details: core_security.TokenDetails):
    """Delete the user's identity verification record (soft delete)

    :param ep_context: The endpoint context
    :param token_details: The token details
    :raises HTTPException: If the identity verification is not found, or if it has expired
    """
    db = ep_context.db
    audit_logger = ep_context.audit_logger

    # Get the verification
    verification = await verification_crud.get_identity_verification_by_user(
        db, token_details.user_id, only_active=False
    )

    if not verification:
        raise HTTPException(status_code=404, detail="Identity verification not found")

    if verification.expires_at.replace(tzinfo=settings.DEFAULT_TIMEZONE) < datetime.datetime.now(
        settings.DEFAULT_TIMEZONE
    ):
        raise HTTPException(status_code=400, detail="Identity verification has expired and will be deleted soon")

    # Delete the verification
    await verification_crud.delete_identity_verification(db, verification.id, soft_delete=True)

    # Delete the images
    core_verification.clear_identification_verification(verification.user_id, throw_error=False)

    # Log the deletion
    audit_logger.id_verification_rejected(token_details.user_id, verification.user_id, "User deleted the verification")
    audit_logger.id_verification_soft_deleted(token_details.user_id, verification.id)
    await db.commit()
