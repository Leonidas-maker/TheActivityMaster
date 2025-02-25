from pydantic import BaseModel, Field, EmailStr, ConfigDict, model_validator, conlist, field_validator, RootModel
from typing import List, Optional, Dict, Tuple
import uuid
import datetime

from schemas import s_generic
from models.m_club import SessionType, Weekday, OccurrenceStatus, PriceType, ProgramStatus
from models.m_payment import BookingStatus, BookingType

from models import m_club

from config.settings import DEFAULT_TIMEZONE


# ======================================================== #
# ======================= Employee ======================= #
# ======================================================== #
class EmployeeBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    first_name: str = Field(..., max_length=50, description="The first name of the employee.")
    last_name: str = Field(..., max_length=50, description="The last name of the employee.")
    email: EmailStr = Field(..., description="The email of the employee.")


class Employee(EmployeeBase):
    id: uuid.UUID = Field(..., description="The ID of the employee.")


class Owner(EmployeeBase):
    pass


class EmployeeResponse(Employee):
    role_name: str
    role_level: int
    program_assignments: List[uuid.UUID] = Field([], description="The IDs of the programs assigned to the trainer.")


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
    owners: List[Owner]


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
# ================== Session Occurrence ================== #
# ======================================================== #
class SessionOccurrence(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID

    session_id: uuid.UUID

    status: OccurrenceStatus = Field(..., description="The status of the occurrence.")

    occurrence_date: datetime.date = Field(..., description="The date of the occurrence.")
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
    note: Optional[str] = None


class SessionReschedule(SessionOccurrenceChange):
    start_datetime: datetime.datetime = Field(..., description="The new start datetime.")
    end_datetime: datetime.datetime = Field(..., description="The new end datetime.")

    @model_validator(mode="after")
    def validate_timing(self) -> "SessionReschedule":
        if self.start_datetime >= self.end_datetime:
            raise ValueError("End datetime must be after start datetime.")

        self.start_datetime = self.start_datetime.replace(microsecond=0)
        self.end_datetime = self.end_datetime.replace(microsecond=0)

        return self


class SessionReinstate(SessionOccurrenceChange):
    pass


# ======================================================== #
# ======================== Session ======================= #
# ======================================================== #
class SessionBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    session_type: SessionType = Field(..., description="The type of the session.")
    capacity: Optional[int] = Field(None, gt=0, description="The maximum number of participants for the session.")
    price: Optional[int] = Field(None, ge=0, description="The price of the session.")

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

    @model_validator(mode="after")
    def time_checker(self) -> "SessionBase":
        if self.start_datetime and self.end_datetime:
            self.start_datetime = self.start_datetime.replace(microsecond=0)
            self.end_datetime = self.end_datetime.replace(microsecond=0)

        if self.start_time and self.end_time:
            self.start_time = self.start_time.replace(microsecond=0)
            self.end_time = self.end_time.replace(microsecond=0)

        if self.start_datetime and self.end_datetime and self.start_datetime >= self.end_datetime:
            raise ValueError("End datetime must be after start datetime.")

        if self.start_time and self.end_time and self.start_time >= self.end_time:
            raise ValueError("End time must be after start time.")

        if self.start_date and self.end_date and self.start_date >= self.end_date:
            raise ValueError("End date must be after start date.")
        return self


class SessionCreate(SessionBase):
    @field_validator("start_datetime", "end_datetime", "start_time", "end_time", "start_date", "end_date")
    @classmethod
    def ensure_timezone(cls, value):
        today = datetime.datetime.now(tz=DEFAULT_TIMEZONE)
        if isinstance(value, datetime.datetime) and value.tzinfo is None:
            new_value = value.replace(tzinfo=DEFAULT_TIMEZONE)
            if new_value < today:
                raise ValueError("Time must be in the future.")
            return new_value
        elif isinstance(value, datetime.time) and value.tzinfo is None:
            new_value = value.replace(tzinfo=DEFAULT_TIMEZONE)
            if new_value < today.time():
                raise ValueError("Time must be in the future.")
            return new_value
        return value


class Session(SessionBase):
    id: uuid.UUID
    program_id: uuid.UUID = Field(..., description="The ID of the program to which the session belongs.")

    occurrences: Optional[List[SessionOccurrence]] = Field(
        None, description="The occurrences of the session if type is 'course'."
    )

    @model_validator(mode="after")
    def check_occurrences(self) -> "Session":
        if self.session_type == SessionType.EVENT:
            self.occurrences = None
        return self
    


class SessionUpdate(BaseModel):
    session_type: Optional[SessionType] = Field(None, description="The new type of the session.")
    capacity: Optional[int] = Field(None, gt=0, description="The new maximum number of participants for the session.")
    price: Optional[int] = Field(None, ge=0, description="The new price of the session.")

    start_datetime: Optional[datetime.datetime] = Field(
        None, description="The new start date and time for a one-time event."
    )
    end_datetime: Optional[datetime.datetime] = Field(
        None, description="The new end date and time for a one-time event."
    )

    day_of_week: Optional[Weekday] = Field(None, description="The new day of the week for a recurring event.")
    start_time: Optional[datetime.time] = Field(None, description="The new start time for a recurring event.")
    end_time: Optional[datetime.time] = Field(None, description="The new end time for a recurring event.")
    start_date: Optional[datetime.date] = Field(None, description="The new start date for a recurring event.")
    end_date: Optional[datetime.date] = Field(None, description="The new end date for a recurring event.")

    address: Optional[s_generic.Address] = Field(
        None, description="Provide an address if the session is held at a different location."
    )

    null_end_date: bool = Field(False, description="If true, the end date will be set to None.")
    refresh_future_occurrences: bool = Field(
        False,
        description="If true, future occurrences will be deleted and recreated. If false only scheduled occurrences will be recreated.",
    )

    @field_validator("start_datetime", "end_datetime", "start_time", "end_time", "start_date", "end_date")
    @classmethod
    def ensure_timezone(cls, value):
        today = datetime.datetime.now(tz=DEFAULT_TIMEZONE)
        if isinstance(value, datetime.datetime) and value.tzinfo is None:
            new_value = value.replace(tzinfo=DEFAULT_TIMEZONE)
            if new_value < today:
                raise ValueError("Time must be in the future.")
            return new_value
        elif isinstance(value, datetime.time) and value.tzinfo is None:
            new_value = value.replace(tzinfo=DEFAULT_TIMEZONE)
            if new_value < today.time():
                raise ValueError("Time must be in the future.")
            return new_value
        return value

    @model_validator(mode="after")
    def time_checker(self) -> "SessionUpdate":
        if self.start_datetime and self.end_datetime:
            self.start_datetime = self.start_datetime.replace(microsecond=0)
            self.end_datetime = self.end_datetime.replace(microsecond=0)

        if self.start_time and self.end_time:
            self.start_time = self.start_time.replace(microsecond=0)
            self.end_time = self.end_time.replace(microsecond=0)

        if self.start_datetime and self.end_datetime and self.start_datetime >= self.end_datetime:
            raise ValueError("End datetime must be after start datetime.")

        if self.start_time and self.end_time and self.start_time >= self.end_time:
            raise ValueError("End time must be after start time.")

        if self.start_date and self.end_date and self.start_date >= self.end_date:
            raise ValueError("End date must be after start date.")

        return self

    @model_validator(mode="after")
    def check(self) -> "SessionUpdate":
        if (
            self.session_type is None
            and self.capacity is None
            and self.price is None
            and self.start_datetime is None
            and self.end_datetime is None
            and self.day_of_week is None
            and self.start_time is None
            and self.end_time is None
            and self.start_date is None
            and self.end_date is None
            and self.address is None
            and not self.null_end_date
            and not self.refresh_future_occurrences
        ):
            raise ValueError(
                "At least one of the fields 'session_type', 'capacity', 'price', 'membership_required', "
                "'start_datetime', 'end_datetime', 'day_of_week', 'start_time', 'end_time', 'start_date', 'end_date', "
                "'address', 'null_end_date', or 'refresh_future_occurrences' must be provided."
            )

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

    price: Optional[int] = Field(
        None,
        ge=0,
        description="The price of the program (e.g. 100 cents to charge $1.00 or 100 to charge ¥100, a zero-decimal currency).",
    )
    currency: str = Field(..., max_length=3, description="The currency of the program.")
    pricing_model: PriceType = Field(..., description="The pricing model of the program.")

    capacity: Optional[int] = Field(None, gt=0, description="The maximum number of participants for the program.")

    membership_required: bool = Field(
        False, description="Whether a membership is required to participate in the program."
    )

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

    price: Optional[int] = Field(
        None,
        ge=0,
        description="The new price of the program in cents (e.g. 100 cents to charge $1.00 or 100 to charge ¥100, a zero-decimal currency)",
    )
    currency: Optional[str] = Field(None, max_length=3, description="The new currency of the program.")
    pricing_model: Optional[PriceType] = Field(None, description="The new pricing model of the program.")

    capacity: Optional[int] = Field(None, gt=0, description="The new maximum number of participants for the program.")

    membership_required: Optional[bool] = Field(
        None, description="Whether a membership is required to participate in the program."
    )

    status: Optional[ProgramStatus] = Field(None, description="The new status of the program.")

    categories: Optional[List[int]] = Field(None, max_length=5, description="The new categories of the program.")
    session_data: Optional[Dict[uuid.UUID, Tuple[int, int]]] = Field(
        None,
        description="The new session data for the program. Key is the session ID and value is a tuple of price "
        "(e.g. 100 cents to charge $1.00 or 100 to charge ¥100, a zero-decimal currency) and capacity.",
    )

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
            and self.status is None
        ):
            raise ValueError(
                "At least one of the fields 'name', 'description', 'price', "
                " 'currency', 'pricing_model', 'categories', 'session_data', or 'status' must be provided."
            )

        sessions_exist = self.session_data is not None and len(self.session_data) > 0
        price_correct = self.price is not None and self.capacity is not None

        if self.pricing_model == PriceType.PACKAGE:  #
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


###########################################################################
################################# Booking #################################
###########################################################################


class TransactionData(BaseModel):
    stripe_account_id: str
    total_amount: int
    currency: str

    def __getitem__(self, key):
        if hasattr(self, key):
            return getattr(self, key)
        else:
            raise AttributeError(f"{key} is not a valid attribute.")

    def __setitem__(self, key, value):
        if hasattr(self, key):
            setattr(self, key, value)
        else:
            raise AttributeError(f"{key} is not a valid attribute.")


class BookingBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    session_id: uuid.UUID = Field(..., description="The ID of the session for which the booking was made.")
    booking_type: BookingType = Field(..., description="The type of the booking.")


class Booking(BookingBase):
    id: uuid.UUID = Field(..., description="The ID of the booking.")
    club_id: uuid.UUID = Field(..., description="The ID of the club for which the booking was made.")
    program_id: uuid.UUID = Field(..., description="The ID of the program for which the booking was made.")

    user_id: uuid.UUID = Field(..., description="The ID of the user who made the booking.")
    status: BookingStatus = Field(..., description="The status of the booking.")
    transaction_id: Optional[uuid.UUID] = Field(None, description="The ID of the transaction for the booking.")
    price: int = Field(..., description="The price of the booking.")
    pricing_model: PriceType = Field(..., description="The pricing model of the booking.")

    @model_validator(mode="after")
    def check_booking_type(self) -> "Booking":
        if self.booking_type == BookingType.MEMBERSHIP_ACCESS and self.transaction_id:
            raise ValueError("Transaction ID should not be provided for membership access bookings.")

        if self.booking_type in [BookingType.PAID, BookingType.MEMBERSHIP] and not self.transaction_id:
            raise ValueError("Transaction ID must be provided for paid bookings.")

        return self


class BookingDetails(Booking):
    program: Program
    session: Session

class ClubBooking(Booking):
    user_id: uuid.UUID = Field(..., description="The ID of the user who made the booking.")


class BookingCreateRequest(BaseModel):
    club_id: uuid.UUID = Field(..., description="The ID of the club for which the booking was made.")
    program_ids: List[uuid.UUID] = Field(
        ..., max_length=5, description="The IDs of the programs for which the booking was made."
    )
    session_ids: List[uuid.UUID] = Field(
        ..., max_length=10, description="The IDs of the sessions for which the booking was made."
    )
