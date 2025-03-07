from typing import Any
from pydantic import BaseModel, Field, ConfigDict, model_validator

class MessageResponse(BaseModel):
    """
    Model for returning a simple message response.

    Fields:
      - message: The message text.
    """
    message: str = Field(..., description="The message text to be returned.")


class PasswordForm(BaseModel):
    """
    Model representing a password submission form.

    Fields:
      - password: The user's password (must be between 8 and 255 characters).
    """
    password: str = Field(
        ..., 
        min_length=8, 
        max_length=255, 
        description="The user's password (must be between 8 and 255 characters)."
    )


class Address(BaseModel):
    """
    Model representing a physical address.

    Fields:
      - street: The street address (3-255 characters).
      - postal_code: The postal or ZIP code (2-20 characters).
      - city: The city name (2-100 characters).
      - state: The state or region (2-100 characters).
      - country: The country name (4-100 characters).

    Validation:
      - The `flatten` validator processes input data that might not be a dictionary.
        If an object with attributes (e.g., nested postal code data) is provided, it extracts and
        flattens the nested structure into a standard dictionary format.
    """
    model_config = ConfigDict(from_attributes=True)
    street: str = Field(
        ..., 
        min_length=3, 
        max_length=255, 
        description="The street address (3-255 characters)."
    )
    postal_code: str = Field(
        ..., 
        min_length=2, 
        max_length=20, 
        description="The postal or ZIP code (2-20 characters)."
    )
    city: str = Field(
        ..., 
        min_length=2, 
        max_length=100, 
        description="The city name (2-100 characters)."
    )
    state: str = Field(
        ..., 
        min_length=2, 
        max_length=100, 
        description="The state or region (2-100 characters)."
    )
    country: str = Field(
        ..., 
        min_length=4, 
        max_length=100, 
        description="The country name (4-100 characters)."
    )

    @model_validator(mode="before")
    def flatten(cls, data: Any) -> Any:
        """
        Flattens nested address data to a dictionary.

        This validator checks if the incoming data is not a dictionary but an object 
        with attributes. If so, it extracts nested address attributes to match the expected format.

        Args:
            data (Any): The input data, potentially a nested object.

        Returns:
            Any: A dictionary with keys 'street', 'postal_code', 'city', 'state', and 'country'.
        """
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
