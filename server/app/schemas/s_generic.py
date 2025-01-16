from pydantic import BaseModel

class Address(BaseModel):
    street: str
    postal_code: str
    city: str
    state: str
    country: str
