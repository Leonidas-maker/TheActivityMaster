from pydantic import BaseModel, Field

class MessageResponse(BaseModel):
    message: str

class Address(BaseModel):
    street: str = Field(..., max_length=255)
    postal_code: str = Field(..., max_length=20)
    city: str = Field(..., max_length=100)
    state: str = Field(..., max_length=100)
    country: str = Field(..., max_length=100)