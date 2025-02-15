from typing import Any
from pydantic import BaseModel, Field, ConfigDict, model_validator


class MessageResponse(BaseModel):
    message: str


class Address(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    street: str = Field(..., min_length=3, max_length=255)
    postal_code: str = Field(..., min_length=2, max_length=20)
    city: str = Field(..., min_length=2, max_length=100)
    state: str = Field(..., min_length=2, max_length=100)
    country: str = Field(..., min_length=4, max_length=100)

    @model_validator(mode="before")
    def flatten(cls, data):
        if isinstance(data, dict):
            return data

        if hasattr(data, "postal_code"):
            return {
                "street": data.street,
                "postal_code": data.postal_code.code,
                "city": data.postal_code.city.name,
                "state": data.postal_code.city.state.name,
                "country": data.postal_code.city.state.country.name,
            }
        return data