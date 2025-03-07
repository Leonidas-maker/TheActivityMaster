from pydantic import BaseModel, Field, ConfigDict
from fastapi import Form
import uuid
import datetime

class IdentityVerificationRequest(BaseModel):
    """
    Request model for submitting identity verification data.

    Fields:
      - id_card_mrz: The Machine Readable Zone (MRZ) data from the ID card (max 255 characters).
      - first_name: The user's first name (max 50 characters).
      - last_name: The user's last name (max 50 characters).
      - date_of_birth: The user's date of birth as a string (max 10 characters).
    """
    id_card_mrz: str = Field(..., max_length=255, description="MRZ data from the ID card (max 255 characters).")
    first_name: str = Field(..., max_length=50, description="The user's first name (max 50 characters).")
    last_name: str = Field(..., max_length=50, description="The user's last name (max 50 characters).")
    date_of_birth: str = Field(..., max_length=10, description="The user's date of birth (max 10 characters).")

    @classmethod
    def as_form(
        cls,
        id_card_mrz: str = Form(...),
        first_name: str = Form(...),
        last_name: str = Form(...),
        date_of_birth: str = Form(...),
    ):
        """
        Allows the model to be used with form data in FastAPI endpoints.
        
        Parameters:
          - id_card_mrz: MRZ data from the ID card.
          - first_name: User's first name.
          - last_name: User's last name.
          - date_of_birth: User's date of birth.
        
        Returns:
          An instance of IdentityVerificationRequest.
        """
        return cls(
            id_card_mrz=id_card_mrz,
            first_name=first_name,
            last_name=last_name,
            date_of_birth=date_of_birth,
        )


class IdentityVerificationRejectRequest(BaseModel):
    """
    Request model for rejecting an identity verification request.

    Fields:
      - identity_verification_id: The UUID of the verification request to be rejected.
      - reason: The reason for rejecting the verification (max 255 characters).
    """
    identity_verification_id: uuid.UUID = Field(..., description="The ID of the verification request.")
    reason: str = Field(..., max_length=255, description="The reason for rejection (max 255 characters).")


class PendingIdentityVerificationResponse(BaseModel):
    """
    Response model for a pending identity verification request.

    Fields:
      - id: The UUID of the pending identity verification request.
      - user_id: The UUID of the user associated with the pending verification.
    """
    id: uuid.UUID = Field(..., description="The ID of the pending identity verification request.")
    user_id: uuid.UUID = Field(..., description="The user ID associated with the pending verification.")


class IdentityVerificationDetailsResponse(BaseModel):
    """
    Detailed response model for an identity verification request.

    Fields:
      - id: The UUID of the identity verification request.
      - user_id: The UUID of the user who submitted the verification.
      - first_name: The user's first name.
      - last_name: The user's last name.
      - date_of_birth: The user's date of birth.
      - image_url: URL to the uploaded identity document image.
      - status: The current status of the verification request.
      - created_at: Timestamp when the verification was created.
      - updated_at: Timestamp when the verification was last updated.
      - expires_at: Timestamp when the verification request expires.
    """
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID = Field(..., description="The unique identifier of the verification request.")
    user_id: uuid.UUID = Field(..., description="The user ID associated with the verification request.")
    first_name: str = Field(..., description="The user's first name.")
    last_name: str = Field(..., description="The user's last name.")
    date_of_birth: str = Field(..., description="The user's date of birth.")
    image_url: str = Field(..., description="URL of the uploaded identity document image.")
    status: str = Field(..., description="The current status of the verification request.")
    created_at: datetime.datetime = Field(..., description="Timestamp when the verification request was created.")
    updated_at: datetime.datetime = Field(..., description="Timestamp when the verification request was last updated.")
    expires_at: datetime.datetime = Field(..., description="Timestamp when the verification request expires.")


class IdentityVerificationStatusResponse(BaseModel):
    """
    Response model for checking the status of an identity verification request.

    Fields:
      - id: The UUID of the identity verification request.
      - status: The current status of the verification.
      - created_at: Timestamp when the verification was created.
      - updated_at: Timestamp when the verification was last updated.
      - expires_at: Timestamp when the verification request expires.
    """
    id: uuid.UUID = Field(..., description="The unique identifier of the verification request.")
    status: str = Field(..., description="The current status of the verification request.")
    created_at: datetime.datetime = Field(..., description="Timestamp when the verification request was created.")
    updated_at: datetime.datetime = Field(..., description="Timestamp when the verification request was last updated.")
    expires_at: datetime.datetime = Field(..., description="Timestamp when the verification request expires.")
