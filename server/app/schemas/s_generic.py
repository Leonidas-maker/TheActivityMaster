from pydantic import BaseModel, Field


class MessageResponse(BaseModel):
    message: str


class Address(BaseModel):
    street: str = Field(..., min_length=3, max_length=255)
    postal_code: str = Field(..., min_length=2, max_length=20)
    city: str = Field(..., min_length=2, max_length=100)
    state: str = Field(..., min_length=2, max_length=100)
    country: str = Field(..., min_length=4, max_length=100)