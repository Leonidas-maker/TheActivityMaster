from fastapi import APIRouter, Depends, Request, Header, File, UploadFile, HTTPException
from fastapi.responses import FileResponse
import uuid
from typing import List, Optional

from controllers import verification as verification_controller

from schemas import s_verification, s_generic

import core.security as core_security
from core.generic import EndpointContext

from middleware.general import get_endpoint_context
import middleware.auth as auth_middleware

from utils.exceptions import handle_exception

from config import settings
from api.v1.endpoints.verification import identity


# Router for the verification endpoints
router = APIRouter()

# Include the identity router
router.include_router(identity.router, prefix="/identity")


@router.post("/verify_email", response_model=s_generic.MessageResponse, tags=["Verification"])
async def verify_email_v1(
    user_id: str, expires: str, signature: str, ep_context: EndpointContext = Depends(get_endpoint_context)
):
    """Verify the user's email"""
    try:
        await verification_controller.verify_email(ep_context, user_id, expires, signature)
        return {"message": "Email verified"}
    except Exception as e:
        await handle_exception(e, ep_context, "Failed to verify email")