from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, ForeignKey, UniqueConstraint, UUID
import uuid
from typing import List

from config.database import Base

from models.m_generic import *
from models.m_club import *
from models.m_audit import *
from models.m_payment import *


class Address(Base):
    __tablename__ = "addresses"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    street: Mapped[str] = mapped_column(String(255), nullable=False)  # Explizit VARCHAR(255)
    postal_code_id: Mapped[int] = mapped_column(Integer, ForeignKey("postal_codes.id"), nullable=False)
    
    postal_code: Mapped["PostalCode"] = relationship("PostalCode", back_populates="addresses", lazy="joined")

    __table_args__ = (UniqueConstraint("street", "postal_code_id", name="unique_address_postal_code"),)

    def get_as_dict(self):
        return {
            "id": str(self.id),
            "street": self.street,
            "postal_code": self.postal_code.code,
            "city": self.postal_code.city.name,
            "state": self.postal_code.city.state.name,
            "country": self.postal_code.city.state.country.name,
        }


class PostalCode(Base):
    __tablename__ = "postal_codes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(20), nullable=False)

    city_id: Mapped[int] = mapped_column(Integer, ForeignKey("cities.id"), nullable=False)

    city: Mapped["City"] = relationship("City", back_populates="postal_codes", lazy="joined")
    addresses: Mapped[List["Address"]] = relationship("Address", back_populates="postal_code", uselist=True)

    __table_args__ = (UniqueConstraint("code", "city_id", name="unique_postal_code_city"),)


class City(Base):
    __tablename__ = "cities"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)

    state_id: Mapped[int] = mapped_column(Integer, ForeignKey("states.id"), nullable=False)

    state: Mapped["State"] = relationship("State", back_populates="cities", lazy="joined")
    postal_codes: Mapped[List["PostalCode"]] = relationship("PostalCode", back_populates="city", uselist=True)

    __table_args__ = (UniqueConstraint("name", "state_id", name="unique_city_state"),)


class State(Base):
    __tablename__ = "states"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)

    country_id: Mapped[int] = mapped_column(Integer, ForeignKey("countries.id"), nullable=False)

    country: Mapped["Country"] = relationship("Country", back_populates="states", lazy="joined")
    cities: Mapped[List["City"]] = relationship("City", back_populates="state", uselist=True)

    __table_args__ = (UniqueConstraint("name", "country_id", name="unique_state_country"),)


class Country(Base):
    __tablename__ = "countries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    iso2: Mapped[str] = mapped_column(String(2), nullable=False, unique=True)
    iso3: Mapped[str] = mapped_column(String(3), nullable=False, unique=True)

    states: Mapped[List["State"]] = relationship("State", back_populates="country", uselist=True)
