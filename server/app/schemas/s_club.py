from pydantic import BaseModel, Field, EmailStr, ConfigDict, model_validator, conlist
from typing import List, Optional, Dict, Tuple
import uuid
import datetime
from decimal import Decimal

from schemas import s_generic
from models.m_club import SessionType, Weekday, OccurrenceStatus, BookingStatus, PriceType, ProgramStatus


# ======================================================== #
# ======================= Employee ======================= #
# ======================================================== #
class Employee(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    first_name: str
    last_name: str
    email: EmailStr


class EmployeeResponse(Employee):
    role_name: str
    role_level: int


# ======================================================== #
# ========================= Club ========================= #
# ======================================================== #
class ClubBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    name: str = Field(..., max_length=50)
    description: str = Field(..., max_length=100)
    address: s_generic.Address


class ClubCreate(ClubBase):
    pass


class Club(ClubBase):
    id: uuid.UUID


class ClubDetails(Club):
    owners: List[Employee]


class ClubUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=50)
    description: Optional[str] = Field(None, max_length=100)
    address: Optional[s_generic.Address] = None

    @model_validator(mode="after")
    def check_at_least_one_field(self) -> "ClubUpdate":
        if self.name is None and self.description is None and self.address is None:
            raise ValueError("At least one of the fields 'name', 'description', or 'address' must be provided.")
        return self


# ======================================================== #
# ======================= Club Role ====================== #
# ======================================================== #
class UserClubRoleAssignment(BaseModel):
    user_ident: str = Field(..., max_length=50)
    level: int = Field(..., gt=0, le=10)


class UserClubRoleChange(BaseModel):
    user_id: uuid.UUID
    level: int = Field(..., ge=0, le=10)


###########################################################################
############################ Program Offerings ############################
###########################################################################


# ======================================================== #
# ======================== Session ======================= #
# ======================================================== #
class SessionBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    session_type: SessionType = Field(..., description="The type of the session.")
    capacity: Optional[int] = Field(None, gt=0, description="The maximum number of participants for the session.")
    price: Optional[Decimal] = Field(None, ge=0, decimal_places=2, description="The price of the session.")

    membership_required: bool

    # one time event
    start_datetime: Optional[datetime.datetime] = Field(
        None, description="The start date and time for a one-time event."
    )
    end_datetime: Optional[datetime.datetime] = Field(None, description="The end date and time for a one-time event.")

    # recurring event
    day_of_week: Optional[Weekday] = Field(None, description="The day of the week for a recurring event.")
    start_time: Optional[datetime.time] = Field(None, description="The start time for a recurring event.")
    end_time: Optional[datetime.time] = Field(None, description="The end time for a recurring event.")
    start_date: Optional[datetime.date] = Field(None, description="The start date for a recurring event.")
    end_date: Optional[datetime.date] = Field(None, description="The end date for a recurring event.")

    address: Optional[s_generic.Address] = Field(
        None, description="Provide an address if the session is held at a different location."
    )

    @model_validator(mode="after")
    def check(self) -> "SessionBase":
        if (self.start_datetime is not None or self.end_datetime is not None) and (
            self.day_of_week is not None
            or self.start_time is not None
            or self.end_time is not None
            or self.start_date is not None
            or self.end_date is not None
        ):
            raise ValueError("Session can be either a one-time event or a recurring event, not both.")

        if self.start_datetime and self.end_datetime and self.start_datetime >= self.end_datetime:
            raise ValueError("End datetime must be after start datetime.")

        if self.price is not None and self.capacity is None or self.capacity is not None and self.price is None:
            raise ValueError("Both price and capacity must be provided.")

        event_time_exists = self.start_datetime is not None and self.end_datetime is not None
        course_time_exists = (
            self.day_of_week is not None
            and self.start_time is not None
            and self.end_time is not None
            and self.start_date is not None
        )

        if self.session_type == SessionType.COURSE:
            if not course_time_exists:
                raise ValueError(
                    "For course sessions, day of week, start time, end time, and start date must be provided."
                )
            if event_time_exists:
                raise ValueError("For course sessions, start and end datetime should not be provided.")
        elif self.session_type == SessionType.EVENT:
            if not event_time_exists:
                raise ValueError("For event sessions, start and end datetime must be provided.")
            if course_time_exists:
                raise ValueError(
                    "For event sessions, day of week, start time, end time, and start date should not be provided."
                )

        return self


class SessionCreate(SessionBase):
    pass

class Session(SessionBase):
    id: uuid.UUID
    program_id: uuid.UUID = Field(..., description="The ID of the program to which the session belongs.")


# ======================================================== #
# ======================== Program ======================= #
# ======================================================== #
class ProgramCategory(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int = Field(..., ge=0, description="The ID of the category.")
    name: str = Field(..., max_length=50, description="The name of the category.")
    description: Optional[str] = Field(None, max_length=100, description="The description of the category.")


class ProgramBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    name: str = Field(..., max_length=100, description="The name of the program.")
    description: str = Field(..., min_length=10, max_length=500, description="The description of the program.")

    price: Optional[Decimal] = Field(None, ge=0, decimal_places=2, description="The price of the program.")
    currency: str = Field(..., max_length=3, description="The currency of the program.")
    pricing_model: PriceType = Field(..., description="The pricing model of the program.")

    capacity: Optional[int] = Field(None, gt=0, description="The maximum number of participants for the program.")

    @model_validator(mode="after")
    def price_and_price_model(self) -> "ProgramBase":
        if self.pricing_model == PriceType.PER_SESSION and self.price is not None and self.capacity is not None:
            raise ValueError("Price should not be provided if the pricing model is 'per_session'.")

        if self.pricing_model == PriceType.PACKAGE and self.price is None and self.capacity is None:
            raise ValueError("Price must be provided if the pricing model is 'package'.")

        return self


class ProgramCreate(ProgramBase):
    sessions: List[SessionBase] = Field(..., min_length=1)
    categories: List[int] = Field([], max_length=5)
    status: ProgramStatus = Field(
        ProgramStatus.DRAFT, description="The status of the program. Default for creation is 'draft'."
    )

    @model_validator(mode="after")
    def session_check(self) -> "ProgramCreate":
        if self.pricing_model == PriceType.PACKAGE and any([s.price or s.capacity for s in self.sessions]):
            raise ValueError(
                "Price and capacity should not be provided for sessions if the pricing model is 'package'."
            )

        if self.pricing_model == PriceType.PER_SESSION and any(
            [s.price is None or s.capacity is None for s in self.sessions]
        ):
            raise ValueError(
                "Price and capacity must be provided for all sessions if the pricing model is 'per_session'."
            )

        return self


class Program(ProgramBase):
    club_id: uuid.UUID = Field(..., description="The ID of the club to which the program belongs.")
    id: uuid.UUID = Field(..., description="The ID of the program.")
    categories: List[ProgramCategory] = Field([], max_length=5, description="The categories of the program.")
    status: ProgramStatus = Field(..., description="The status of the program.")


class ProgramDetails(Program):
    sessions: List[Session]


class ProgramUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100, description="The new name of the program.")
    description: Optional[str] = Field(None, max_length=500, description="The new description of the program.")

    price: Optional[Decimal] = Field(None, ge=0, decimal_places=2, description="The new price of the program.")
    currency: Optional[str] = Field(None, max_length=3, description="The new currency of the program.")
    pricing_model: Optional[PriceType] = Field(None, description="The new pricing model of the program.")

    capacity: Optional[int] = Field(None, gt=0, description="The new maximum number of participants for the program.")

    status: Optional[ProgramStatus] = Field(None, description="The new status of the program.")

    categories: Optional[List[int]] = Field(None, max_length=5, description="The new categories of the program.")
    session_data: Optional[Dict[uuid.UUID, Tuple[Decimal, int]]] = None

    @model_validator(mode="after")
    def check(self) -> "ProgramUpdate":
        if (
            self.name is None
            and self.description is None
            and self.price is None
            and self.currency is None
            and self.pricing_model is None
            and self.categories is None
            and self.session_data is None
        ):
            raise ValueError(
                "At least one of the fields 'name', 'description', 'price', 'currency', 'pricing_model', 'categories', or 'session_prices' must be provided."
            )

        sessions_exist = self.session_data is not None and len(self.session_data) > 0
        price_correct = self.price is not None and self.capacity is not None

        if self.pricing_model == PriceType.PACKAGE:
            if not price_correct:
                raise ValueError("Price and capacity must be provided if the pricing model is 'package'.")
            if sessions_exist:
                raise ValueError("Session prices should not be provided if the pricing model is 'package'.")

        if self.pricing_model == PriceType.PER_SESSION:
            if price_correct:
                raise ValueError("Price and capacity should not be provided if the pricing model is 'per_session'.")
            if not sessions_exist:
                raise ValueError("Session prices must be provided if the pricing model is 'per_session'.")

        if self.price is not None and (self.session_data is not None and len(self.session_data) > 0):
            raise ValueError("Only one price should be provided.")

        if self.status == ProgramStatus.DRAFT:
            raise ValueError("Status cannot be set to 'draft'. Please use 'inactive' instead.")

        return self


# ======================================================== #
# ================== Session Occurrence ================== #
# ======================================================== #
class SessionOccurrence(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID

    session_id: uuid.UUID

    status: OccurrenceStatus = Field(..., description="The status of the occurrence.")

    occurrence_datetime: datetime.date = Field(..., description="The date of the occurrence.")
    start_datetime: Optional[datetime.datetime] = Field(
        None, description="If the occurrence is rescheduled, this is the new start datetime."
    )
    end_datetime: Optional[datetime.datetime] = Field(
        None, description="If the occurrence is rescheduled, this is the new end datetime."
    )

    note: Optional[str] = Field(None, max_length=500, description="A note about the occurrence.")

    @model_validator(mode="after")
    def validate_occurrence_timing(self) -> "SessionOccurrence":
        if self.start_datetime and not self.end_datetime:
            raise ValueError("End datetime must be provided.")
        if self.end_datetime and not self.start_datetime:
            raise ValueError("Start datetime must be provided.")
        if self.start_datetime and self.end_datetime:
            if self.status != OccurrenceStatus.RESCHEDULED:
                raise ValueError("Start and end datetime must be provided only for rescheduled occurrences.")
            if self.start_datetime >= self.end_datetime:
                raise ValueError("End datetime must be after start datetime.")
        return self


class SessionOccurrenceChange(BaseModel):
    occurrence_id: uuid.UUID
    start_datetime: datetime.datetime
    end_datetime: datetime.datetime
    note: Optional[str] = None

    @model_validator(mode="after")
    def validate_timing(self) -> "SessionOccurrenceChange":
        if self.start_datetime >= self.end_datetime:
            raise ValueError("End datetime must be after start datetime.")
        return self
