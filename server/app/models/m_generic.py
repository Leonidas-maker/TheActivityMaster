from typing import Annotated
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, ForeignKey, UniqueConstraint, UUID
import uuid
from typing import List

from config.database import Base


class Address(Base):
    __tablename__ = "addresses"

    id: Mapped[Annotated[uuid.UUID, mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)]]
    street: Mapped[Annotated[str, mapped_column(String(255), nullable=False)]]  # Explizit VARCHAR(255)
    postal_code_id: Mapped[Annotated[int, mapped_column(Integer, ForeignKey("postal_codes.id"), nullable=False)]]
    
    postal_code: Mapped["PostalCode"] = relationship("PostalCode", back_populates="addresses")

    __table_args__ = (UniqueConstraint("street", "postal_code_id", name="unique_address_postal_code"),)


class PostalCode(Base):
    __tablename__ = "postal_codes"

    id: Mapped[Annotated[int, mapped_column(Integer, primary_key=True, autoincrement=True)]]
    code: Mapped[Annotated[str, mapped_column(String(20), nullable=False)]]

    city_id: Mapped[Annotated[int, mapped_column(Integer, ForeignKey("cities.id"), nullable=False)]]

    city: Mapped["City"] = relationship("City", back_populates="postal_codes")
    addresses: Mapped[List["Address"]] = relationship("Address", back_populates="postal_code", uselist=True)

    __table_args__ = (UniqueConstraint("code", "city_id", name="unique_postal_code_city"),)


class City(Base):
    __tablename__ = "cities"

    id: Mapped[Annotated[int, mapped_column(Integer, primary_key=True, autoincrement=True)]]
    name: Mapped[Annotated[str, mapped_column(String(100), nullable=False)]]

    state_id: Mapped[Annotated[int, mapped_column(Integer, ForeignKey("states.id"), nullable=False)]]

    state: Mapped["State"] = relationship("State", back_populates="cities")
    postal_codes: Mapped[List["PostalCode"]] = relationship("PostalCode", back_populates="city", uselist=True)

    __table_args__ = (UniqueConstraint("name", "state_id", name="unique_city_state"),)


class State(Base):
    __tablename__ = "states"

    id: Mapped[Annotated[int, mapped_column(Integer, primary_key=True, autoincrement=True)]]
    name: Mapped[Annotated[str, mapped_column(String(100), nullable=False)]]

    country_id: Mapped[Annotated[int, mapped_column(Integer, ForeignKey("countries.id"), nullable=False)]]

    country: Mapped["Country"] = relationship("Country", back_populates="states")
    cities: Mapped[List["City"]] = relationship("City", back_populates="state", uselist=True)

    __table_args__ = (UniqueConstraint("name", "country_id", name="unique_state_country"),)


class Country(Base):
    __tablename__ = "countries"

    id: Mapped[Annotated[int, mapped_column(Integer, primary_key=True, autoincrement=True)]]
    name: Mapped[Annotated[str, mapped_column(String(100), nullable=False, unique=True)]]
    iso2: Mapped[Annotated[str, mapped_column(String(2), nullable=False, unique=True)]]
    iso3: Mapped[Annotated[str, mapped_column(String(3), nullable=False, unique=True)]]

    states:  Mapped[List["State"]] = relationship("State", back_populates="country", uselist=True)