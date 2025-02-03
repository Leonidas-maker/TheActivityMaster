from pydantic import BaseModel, Field, ConfigDict
from fastapi import Form
import uuid
import datetime

class IdentityVerificationRequest(BaseModel):
    id_card_mrz: str = Field(..., max_length=255)
    first_name: str = Field(..., max_length=50)
    last_name: str = Field(..., max_length=50)
    date_of_birth: str = Field(..., max_length=10)

    @classmethod
    def as_form(
        cls,
        id_card_mrz: str = Form(...),
        first_name: str = Form(...),
        last_name: str = Form(...),
        date_of_birth: str = Form(...),
    ):
        return cls(
            id_card_mrz=id_card_mrz,
            first_name=first_name,
            last_name=last_name,
            date_of_birth=date_of_birth,
        )

class IdentityVerificationRejectRequest(BaseModel):
    identity_verification_id: uuid.UUID
    reason: str = Field(..., max_length=255)

class PendingIdentityVerificationResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    
class IdentityVerificationDetailsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    first_name: str
    last_name: str
    date_of_birth: str
    image_url: str
    status: str
    created_at: datetime.datetime
    updated_at: datetime.datetime
    expires_at: datetime.datetime


class IdentityVerificationStatusResponse(BaseModel):
    id: uuid.UUID
    status: str
    created_at: datetime.datetime
    updated_at: datetime.datetime
    expires_at: datetime.datetime