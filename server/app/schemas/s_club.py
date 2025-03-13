from pydantic import BaseModel, Field, EmailStr, ConfigDict, model_validator, conlist, field_validator, RootModel
from typing import List, Optional, Dict, Tuple
import uuid
import datetime

from schemas import s_generic
from models.m_club import SessionType, Weekday, OccurrenceStatus, PriceType, ProgramStatusPublic, ProgramStatus
from models import m_club
from config.settings import DEFAULT_TIMEZONE


# ======================================================== #
# ======================= Employee ======================= #
# ======================================================== #
class EmployeeBase(BaseModel):
    """
    Base model for an employee containing basic personal information.
    
    Fields:
      - first_name: The employee's first name (max 50 characters).
      - last_name: The employee's last name (max 50 characters).
      - email: The employee's email address.
    """
    model_config = ConfigDict(from_attributes=True)
    first_name: str = Field(..., max_length=50, description="The first name of the employee (max 50 characters).")
    last_name: str = Field(..., max_length=50, description="The last name of the employee (max 50 characters).")
    email: EmailStr = Field(..., description="The email address of the employee.")


class Employee(EmployeeBase):
    """
    Employee model including a unique identifier.
    
    Fields:
      - id: The unique ID of the employee.
    """
    id: uuid.UUID = Field(..., description="The unique identifier of the employee.")


class Owner(EmployeeBase):
    """
    Model for a club owner. Inherits from EmployeeBase.
    """
    pass


class EmployeeResponse(Employee):
    """
    Extended employee model for API responses including role details.
    
    Fields:
      - role_name: The name of the employee's role.
      - role_level: The level of the employee's role.
      - program_assignments: A list of program IDs assigned to the employee.
    """
    role_name: str
    role_level: int
    program_assignments: List[uuid.UUID] = Field(
        [], description="List of program IDs assigned to the trainer."
    )


# ======================================================== #
# ========================= Club ========================= #
# ======================================================== #
class ClubBase(BaseModel):
    """
    Base model for a club with basic information.
    
    Fields:
      - name: The club's name (max 50 characters).
      - description: A short description of the club (max 100 characters).
      - address: The club's address details.
    """
    model_config = ConfigDict(from_attributes=True)
    name: str = Field(..., max_length=50, description="The club's name (max 50 characters).")
    description: str = Field(..., max_length=100, description="A brief description of the club (max 100 characters).")
    address: s_generic.Address


class ClubCreate(ClubBase):
    """
    Model used to create a new club.
    """
    pass


class Club(ClubBase):
    """
    Model representing a club including its unique ID and deletion flag.
    
    Fields:
      - id: The unique identifier of the club.
      - is_deleted: Flag indicating whether the club is marked for deletion.
    """
    id: uuid.UUID
    is_deleted: bool = Field(False, description="Indicates if the club is marked as deleted.")


class ClubDetails(Club):
    """
    Detailed club model including its owner information.
    
    Fields:
      - owners: List of club owners.
    """
    owners: List[Owner]


class ClubUpdate(BaseModel):
    """
    Model for updating club information.
    
    At least one of the fields 'name', 'description', or 'address' must be provided.
    """
    name: Optional[str] = Field(None, max_length=50, description="The new club name (max 50 characters).")
    description: Optional[str] = Field(None, max_length=100, description="The new club description (max 100 characters).")
    address: Optional[s_generic.Address] = Field(None, description="The new address of the club.")

    @model_validator(mode="after")
    def check_at_least_one_field(self) -> "ClubUpdate":
        if self.name is None and self.description is None and self.address is None:
            raise ValueError("At least one of the fields 'name', 'description', or 'address' must be provided.")
        return self


class ClubStripeUpdate(BaseModel):
    """
    Model for updating the club's Stripe account information.
    
    Fields:
      - stripe_account_id: The Stripe account ID (max 50 characters).
    """
    stripe_account_id: Optional[str] = Field(None, max_length=50, description="The new Stripe account ID (max 50 characters).")


# ======================================================== #
# ======================= Club Role ====================== #
# ======================================================== #
class UserClubRoleAssignment(BaseModel):
    """
    Model for assigning a role to a user within a club.
    
    Fields:
      - user_ident: The unique identifier of the user (max 50 characters).
      - level: The role level, must be between 1 and 10.
    """
    user_ident: str = Field(..., max_length=50, description="The unique user identifier (max 50 characters).")
    level: int = Field(..., gt=0, le=10, description="The role level (between 1 and 10).")


class UserClubRoleChange(BaseModel):
    """
    Model for changing a user's club role.
    
    Fields:
      - user_id: The unique user ID.
      - level: The new role level, must be between 0 and 10.
    """
    user_id: uuid.UUID
    level: int = Field(..., ge=0, le=10, description="The new role level (between 0 and 10).")


###########################################################################
############################ Program Offerings ############################
###########################################################################
# ======================================================== #
# ================== Session Occurrence ================== #
# ======================================================== #
class SessionOccurrence(BaseModel):
    """
    Model representing an occurrence of a session (for recurring courses).
    
    Fields:
      - id: Unique identifier of the occurrence.
      - session_id: The ID of the session to which this occurrence belongs.
      - status: The current status of the occurrence.
      - occurrence_date: The calendar date of the occurrence.
      - start_datetime: (Optional) New start datetime if the occurrence is rescheduled.
      - end_datetime: (Optional) New end datetime if the occurrence is rescheduled.
      - note: (Optional) A note regarding the occurrence (max 500 characters).
    
    Check conditions:
      - If either 'start_datetime' or 'end_datetime' is provided, both must be given.
      - If both are provided, they are only allowed when the status is 'RESCHEDULED' and start must be before end.
    """
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    session_id: uuid.UUID
    status: OccurrenceStatus = Field(..., description="The status of the occurrence (e.g. scheduled, rescheduled).")
    occurrence_date: datetime.date = Field(..., description="The date of the occurrence.")
    start_datetime: Optional[datetime.datetime] = Field(
        None, description="New start datetime for rescheduled occurrences."
    )
    end_datetime: Optional[datetime.datetime] = Field(
        None, description="New end datetime for rescheduled occurrences."
    )
    note: Optional[str] = Field(None, max_length=500, description="An optional note about the occurrence (max 500 characters).")

    @model_validator(mode="after")
    def validate_occurrence_timing(self) -> "SessionOccurrence":
        if self.start_datetime and not self.end_datetime:
            raise ValueError("End datetime must be provided when start datetime is given.")
        if self.end_datetime and not self.start_datetime:
            raise ValueError("Start datetime must be provided when end datetime is given.")
        if self.start_datetime and self.end_datetime:
            if self.status != OccurrenceStatus.RESCHEDULED:
                raise ValueError("Start and end datetimes are only allowed for rescheduled occurrences.")
            if self.start_datetime >= self.end_datetime:
                raise ValueError("End datetime must be after start datetime.")
        return self


class SessionOccurrenceChange(BaseModel):
    """
    Model for updating a session occurrence's note.
    
    Fields:
      - occurrence_id: The unique identifier of the occurrence.
      - note: (Optional) An updated note.
    """
    occurrence_id: uuid.UUID
    note: Optional[str] = None


class SessionReschedule(SessionOccurrenceChange):
    """
    Model for rescheduling a session occurrence.
    
    Fields:
      - start_datetime: The new start datetime.
      - end_datetime: The new end datetime.
    
    Check conditions:
      - The new start datetime must be before the new end datetime.
      - Microseconds are stripped from both datetimes.
    """
    start_datetime: datetime.datetime = Field(..., description="The new start datetime for the rescheduled occurrence.")
    end_datetime: datetime.datetime = Field(..., description="The new end datetime for the rescheduled occurrence.")

    @model_validator(mode="after")
    def validate_timing(self) -> "SessionReschedule":
        if self.start_datetime >= self.end_datetime:
            raise ValueError("End datetime must be after start datetime.")
        self.start_datetime = self.start_datetime.replace(microsecond=0)
        self.end_datetime = self.end_datetime.replace(microsecond=0)
        return self


class SessionReinstate(SessionOccurrenceChange):
    """
    Model for reinstating a previously changed session occurrence.
    """
    pass


# ======================================================== #
# ======================== Session ======================= #
# ======================================================== #
class SessionBase(BaseModel):
    """
    Base model for a session, supporting either a one-time event or a recurring course.
    
    Fields for one-time events:
      - start_datetime: The event's start datetime.
      - end_datetime: The event's end datetime.
    
    Fields for recurring courses:
      - day_of_week: The day of the week the course occurs.
      - start_time: The start time for the course.
      - end_time: The end time for the course.
      - start_date: The start date for the recurring course.
      - end_date: (Optional) The end date for the recurring course.
    
    Additional fields:
      - session_type: Specifies whether this is an event or a course.
      - capacity: (Optional) Maximum number of participants.
      - price: (Optional) Price of the session.
      - address: (Optional) Address if the session is held at an alternate location.
    
    Check conditions:
      - A session cannot mix one-time event and recurring course fields.
      - For events (SESSION_TYPE.EVENT): both start_datetime and end_datetime must be provided and course fields must not be.
      - For courses (SESSION_TYPE.COURSE): day_of_week, start_time, end_time, and start_date must be provided and one-time event fields must not be.
      - 'price' and 'capacity' must either both be provided or omitted.
      - Start times/dates must precede their corresponding end times/dates.
      - Datetime and time fields have their microseconds removed.
    """
    model_config = ConfigDict(from_attributes=True)

    session_type: SessionType = Field(..., description="The type of the session (event or course).")
    capacity: Optional[int] = Field(None, gt=0, description="Maximum number of participants (must be > 0).")
    price: Optional[int] = Field(None, ge=0, description="Price of the session (must be ≥ 0).")

    # One-time event fields
    start_datetime: Optional[datetime.datetime] = Field(
        None, description="Start datetime for a one-time event."
    )
    end_datetime: Optional[datetime.datetime] = Field(None, description="End datetime for a one-time event.")

    # Recurring course fields
    day_of_week: Optional[Weekday] = Field(None, description="Day of the week for a recurring course.")
    start_time: Optional[datetime.time] = Field(None, description="Start time for a recurring course.")
    end_time: Optional[datetime.time] = Field(None, description="End time for a recurring course.")
    start_date: Optional[datetime.date] = Field(None, description="Start date for a recurring course.")
    end_date: Optional[datetime.date] = Field(None, description="End date for a recurring course (if applicable).")

    address: Optional[s_generic.Address] = Field(
        None, description="Alternate location address if the session is not held at the default venue."
    )

    @model_validator(mode="after")
    def check(self) -> "SessionBase":
        # Ensure session is either a one-time event or a recurring course, not both
        if (self.start_datetime is not None or self.end_datetime is not None) and (
            self.day_of_week is not None
            or self.start_time is not None
            or self.end_time is not None
            or self.start_date is not None
            or self.end_date is not None
        ):
            raise ValueError("Session can be either a one-time event or a recurring course, not both.")

        if self.start_datetime and self.end_datetime and self.start_datetime >= self.end_datetime:
            raise ValueError("End datetime must be after start datetime.")

        # Both price and capacity must be provided together
        if (self.price is not None and self.capacity is None) or (self.capacity is not None and self.price is None):
            raise ValueError("Both price and capacity must be provided together.")

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
                raise ValueError("For event sessions, both start and end datetime must be provided.")
            if course_time_exists:
                raise ValueError(
                    "For event sessions, day of week, start time, end time, and start date should not be provided."
                )
        return self

    @model_validator(mode="after")
    def time_checker(self) -> "SessionBase":
        # Remove microseconds from datetime and time fields
        if self.start_datetime and self.end_datetime:
            self.start_datetime = self.start_datetime.replace(microsecond=0)
            self.end_datetime = self.end_datetime.replace(microsecond=0)

        if self.start_time and self.end_time:
            self.start_time = self.start_time.replace(microsecond=0)
            self.end_time = self.end_time.replace(microsecond=0)

        # Validate ordering of times/dates
        if self.start_datetime and self.end_datetime and self.start_datetime >= self.end_datetime:
            raise ValueError("End datetime must be after start datetime.")

        if self.start_time and self.end_time and self.start_time >= self.end_time:
            raise ValueError("End time must be after start time.")

        if self.start_date and self.end_date and self.start_date >= self.end_date:
            raise ValueError("End date must be after start date.")
        return self


class SessionCreate(SessionBase):
    """
    Model for creating a new session.
    
    Check conditions:
      - Ensures that datetime or time fields without timezone info are assigned the default timezone.
      - Provided datetimes must be in the future.
    """
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
            return value.replace(tzinfo=DEFAULT_TIMEZONE)
        return value


class Session(SessionBase):
    """
    Model representing a session with its unique ID and associated program.
    
    Fields:
      - id: The unique identifier for the session.
      - program_id: The ID of the program to which the session belongs.
      - occurrences: For course sessions, a list of occurrence details. For events, this is set to None.
    
    Check conditions:
      - For event sessions, occurrences are automatically set to None.
    """
    id: uuid.UUID
    program_id: uuid.UUID = Field(..., description="The ID of the program to which the session belongs.")
    occurrences: Optional[List[SessionOccurrence]] = Field(
        None, description="Occurrences for the session (only for course sessions)."
    )

    @model_validator(mode="after")
    def check_occurrences(self) -> "Session":
        if self.session_type == SessionType.EVENT:
            self.occurrences = None
        return self


class SessionUpdate(BaseModel):
    """
    Model for updating session details.
    
    At least one update field must be provided.
    
    Check conditions:
      - For event sessions: 'start_datetime' and 'end_datetime' must be provided and course fields omitted.
      - For course sessions: 'day_of_week', 'start_time', 'end_time', and 'start_date' must be provided and event fields omitted.
      - Time-related fields are adjusted to remove microseconds.
    """
    session_type: Optional[SessionType] = Field(None, description="The new type of the session (event or course).")
    capacity: Optional[int] = Field(None, gt=0, description="New maximum number of participants (must be > 0).")
    price: Optional[int] = Field(None, ge=0, description="New price of the session (must be ≥ 0).")

    start_datetime: Optional[datetime.datetime] = Field(
        None, description="New start datetime for a one-time event."
    )
    end_datetime: Optional[datetime.datetime] = Field(
        None, description="New end datetime for a one-time event."
    )

    day_of_week: Optional[Weekday] = Field(None, description="New day of the week for a recurring course.")
    start_time: Optional[datetime.time] = Field(None, description="New start time for a recurring course.")
    end_time: Optional[datetime.time] = Field(None, description="New end time for a recurring course.")
    start_date: Optional[datetime.date] = Field(None, description="New start date for a recurring course.")
    end_date: Optional[datetime.date] = Field(None, description="New end date for a recurring course.")

    address: Optional[s_generic.Address] = Field(
        None, description="Alternate address if the session is held at a different location."
    )

    null_end_date: bool = Field(False, description="If true, the end date will be set to None.")
    refresh_future_occurrences: bool = Field(
        False,
        description="If true, future occurrences will be deleted and recreated; otherwise, only scheduled occurrences will be updated.",
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
            return value.replace(tzinfo=DEFAULT_TIMEZONE)
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
                "At least one field must be provided for update."
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
    """
    Model representing a program category.
    
    Fields:
      - id: Unique identifier for the category (must be ≥ 0).
      - name: The category name (max 50 characters).
      - description: (Optional) A short description (max 100 characters).
    """
    model_config = ConfigDict(from_attributes=True)
    id: int = Field(..., ge=0, description="The unique identifier of the category (≥ 0).")
    name: str = Field(..., max_length=50, description="The name of the category (max 50 characters).")
    description: Optional[str] = Field(None, max_length=100, description="A brief description of the category (max 100 characters).")


class ProgramBase(BaseModel):
    """
    Base model for a program.
    
    Fields:
      - name: The program name (max 100 characters).
      - description: Detailed program description (between 10 and 500 characters).
      - price: (Optional) The program price.
      - currency: The currency code (max 3 characters).
      - pricing_model: The pricing model (e.g. per_session or package).
      - capacity: (Optional) Maximum number of participants.
      - membership_required: Flag indicating if membership is required.
    
    Check conditions:
      - If pricing_model is 'per_session', then neither price nor capacity should be provided.
      - If pricing_model is 'package', price must be provided (and capacity if applicable).
    """
    model_config = ConfigDict(from_attributes=True)
    name: str = Field(..., max_length=100, description="The name of the program (max 100 characters).")
    description: str = Field(..., min_length=10, max_length=500, description="A detailed description of the program (10-500 characters).")

    price: Optional[int] = Field(
        None,
        ge=0,
        description="The price of the program (must be ≥ 0). For example, 100 represents $1.00 if using cents.",
    )
    currency: str = Field(..., max_length=3, description="The currency code (e.g. USD) for the program (max 3 characters).")
    pricing_model: PriceType = Field(..., description="The pricing model of the program ('per_session' or 'package').")

    capacity: Optional[int] = Field(None, gt=0, description="Maximum number of participants (must be > 0).")
    membership_required: bool = Field(
        False, description="Indicates if a membership is required to participate in the program."
    )

    @model_validator(mode="after")
    def price_and_price_model(self) -> "ProgramBase":
        if self.pricing_model == PriceType.PER_SESSION and self.price is not None and self.capacity is not None:
            raise ValueError("Price should not be provided if the pricing model is 'per_session'.")
        if self.pricing_model == PriceType.PACKAGE and self.price is None and self.capacity is None:
            raise ValueError("Price must be provided if the pricing model is 'package'.")
        return self


class ProgramCreate(ProgramBase):
    """
    Model for creating a new program.
    
    Fields:
      - sessions: A list of session definitions for the program.
      - categories: A list of category IDs (max 5 allowed).
      - status: The initial status of the program (default is 'draft').
    
    Check conditions:
      - For 'package' pricing, sessions should not include price or capacity.
      - For 'per_session' pricing, all sessions must include both price and capacity.
    """
    sessions: List[SessionCreate] = Field([], description="A list of session definitions for the program.")
    categories: List[int] = Field([], max_length=5, description="A list of category IDs (up to 5 allowed).")
    status: ProgramStatusPublic = Field(
        ProgramStatusPublic.DRAFT, description="The program status (default 'draft' upon creation)."
    )

    @model_validator(mode="after")
    def session_check(self) -> "ProgramCreate":
        if self.pricing_model == PriceType.PACKAGE and any([s.price or s.capacity for s in self.sessions]):
            raise ValueError("For 'package' pricing, sessions should not include 'price' or 'capacity'.")
        if self.pricing_model == PriceType.PER_SESSION and any(
            [s.price is None or s.capacity is None for s in self.sessions]
        ):
            raise ValueError("For 'per_session' pricing, each session must include both 'price' and 'capacity'.")
        return self


class Program(ProgramBase):
    """
    Model representing a program.
    
    Fields:
      - club_id: The ID of the club that owns the program.
      - id: The unique identifier for the program.
      - categories: A list of detailed category objects (max 5 allowed).
      - status: The current status of the program.
    """
    club_id: uuid.UUID = Field(..., description="The ID of the club to which the program belongs.")
    id: uuid.UUID = Field(..., description="The unique identifier of the program.")
    categories: List[ProgramCategory] = Field([], max_length=5, description="The list of categories (max 5 allowed).")
    status: ProgramStatus = Field(..., description="The current status of the program.")


class ProgramDetails(Program):
    """
    Detailed program model including associated sessions.
    
    Fields:
      - sessions: A list of session details for the program.
    """
    sessions: List[Session]
    membership_ids: List[uuid.UUID] = Field([], description="List of membership IDs required for the program.")


class ProgramUpdate(BaseModel):
    """
    Model for updating program details.
    
    At least one field must be provided.
    
    Check conditions:
      - For 'package' pricing: both 'price' and 'capacity' must be provided and 'session_data' must not be provided.
      - For 'per_session' pricing: 'session_data' must be provided and 'price'/'capacity' should not be provided.
      - Only one pricing scheme (global price or per-session pricing via session_data) is allowed.
      - The status cannot be updated to 'draft'.
    """
    name: Optional[str] = Field(None, max_length=100, description="New program name (max 100 characters).")
    description: Optional[str] = Field(None, max_length=500, description="New program description (max 500 characters).")
    price: Optional[int] = Field(
        None,
        ge=0,
        description="New global program price in cents (must be ≥ 0)."
    )
    currency: Optional[str] = Field(None, max_length=3, description="New currency code (max 3 characters).")
    pricing_model: Optional[PriceType] = Field(None, description="New pricing model ('per_session' or 'package').")
    capacity: Optional[int] = Field(None, gt=0, description="New maximum number of participants (must be > 0).")
    membership_required: Optional[bool] = Field(
        None, description="Flag indicating if membership is required for the program."
    )
    status: Optional[ProgramStatusPublic] = Field(None, description="New status of the program (cannot be 'draft').")
    categories: Optional[List[int]] = Field(None, max_length=5, description="New list of category IDs (max 5 allowed).")
    session_data: Optional[Dict[uuid.UUID, Tuple[int, int]]] = Field(
        None,
        description="Mapping of session ID to a tuple (price, capacity) for per-session pricing."
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
            raise ValueError("At least one update field must be provided.")

        sessions_exist = self.session_data is not None
        price_correct = self.price is not None and self.capacity is not None

        if self.pricing_model == PriceType.PACKAGE:
            if not price_correct:
                raise ValueError("For 'package' pricing, both 'price' and 'capacity' must be provided.")
            if sessions_exist:
                raise ValueError("For 'package' pricing, session-level pricing should not be provided.")
        if self.pricing_model == PriceType.PER_SESSION:
            if price_correct:
                raise ValueError("For 'per_session' pricing, global 'price' and 'capacity' should not be provided.")
            if not sessions_exist:
                raise ValueError("For 'per_session' pricing, session pricing data must be provided.")

        if self.price is not None and (self.session_data is not None and len(self.session_data) > 0):
            raise ValueError("Only one pricing scheme (global price or session-specific pricing) should be provided.")

        if self.status == ProgramStatusPublic.DRAFT:
            raise ValueError("Status cannot be set to 'draft'; please use 'inactive' instead.")
        return self


###########################################################################
################################ Membership ###############################
###########################################################################
class MembershipProgramAccessBase(BaseModel):
    """
    Base model for program access within a membership.
    
    Fields:
      - program_id: The unique identifier of the program.
      - additional_fee: An additional fee for accessing the program (≥ 0).
    """
    model_config = ConfigDict(from_attributes=True)
    program_id: uuid.UUID
    additional_fee: int = Field(0, ge=0, description="Additional fee for the program (must be ≥ 0).")


class MembershipProgramAccessCreate(MembershipProgramAccessBase):
    """
    Model for creating membership access to a program.
    """
    pass


class MembershipProgramAccess(MembershipProgramAccessBase):
    """
    Model representing program access linked to a membership.
    
    Fields:
      - membership_id: The unique identifier of the membership.
    """
    membership_id: uuid.UUID


class MembershipBase(BaseModel):
    """
    Base model for a membership.
    
    Fields:
      - name: The membership name (max 50 characters).
      - description: A short description (max 100 characters).
      - price: The membership price (≥ 0).
      - currency: The currency code (max 3 characters).
      - duration: The duration in days (must be > 0).
      - duration_unit: The unit for duration (default is MONTH).
    
    Check conditions:
      - If duration_unit is DAY, then duration must be at least 5.
    """
    model_config = ConfigDict(from_attributes=True)
    name: str = Field(..., max_length=50, description="The name of the membership (max 50 characters).")
    description: str = Field(..., max_length=100, description="A short description of the membership (max 100 characters).")
    price: int = Field(..., ge=0, description="The price of the membership (must be ≥ 0).")
    currency: str = Field(..., max_length=3, description="The currency code (e.g. USD) for the membership (max 3 characters).")
    duration: int = Field(..., gt=0, description="The duration of the membership in days (must be > 0).")
    duration_unit: m_club.DurationUnit = Field(
        m_club.DurationUnit.MONTH, description="The unit of the duration (default is 'month')."
    )

    @model_validator(mode="after")
    def check(self) -> "MembershipBase":
        if self.duration_unit == m_club.DurationUnit.DAY and self.duration < 5:
            raise ValueError("For 'day' duration unit, duration must be at least 5 days.")
        return self


class MembershipCreate(MembershipBase):
    """
    Model for creating a new membership.
    
    Fields:
      - status: The initial status of the membership (default is 'draft').
    """
    status: m_club.MembershipStatusPublic = Field(
        m_club.MembershipStatusPublic.DRAFT, description="The status of the membership (default 'draft')."
    )


class Membership(MembershipBase):
    """
    Model representing a membership.
    
    Fields:
      - id: The unique identifier of the membership.
      - club_id: The ID of the club to which the membership belongs.
      - status: The current status of the membership.
    """
    id: uuid.UUID = Field(..., description="The unique identifier of the membership.")
    club_id: uuid.UUID = Field(..., description="The club ID associated with the membership.")
    status: m_club.MembershipStatus = Field(..., description="The current status of the membership.")


class MembershipDetails(Membership):
    """
    Detailed membership model including program access details.
    
    Fields:
      - programs_access: List of programs accessible with the membership.
    """
    programs_access: List[MembershipProgramAccess] = Field(
        ..., description="List of program accesses provided by the membership."
    )


class MembershipUpdate(BaseModel):
    """
    Model for updating membership details.
    
    At least one update field must be provided.
    
    Check conditions:
      - 'status' cannot be set to 'draft'; use 'not_bookable' instead.
    """
    name: Optional[str] = Field(None, max_length=50, description="New membership name (max 50 characters).")
    description: Optional[str] = Field(None, max_length=100, description="New membership description (max 100 characters).")
    price: Optional[int] = Field(None, ge=0, description="New membership price (must be ≥ 0).")
    currency: Optional[str] = Field(None, max_length=3, description="New currency code (max 3 characters).")
    duration: Optional[int] = Field(None, gt=0, description="New duration in days (must be > 0).")
    duration_unit: Optional[m_club.DurationUnit] = Field(None, description="New duration unit.")
    status: Optional[m_club.MembershipStatusPublic] = Field(None, description="New membership status (cannot be 'draft').")

    @model_validator(mode="after")
    def check(self) -> "MembershipUpdate":
        if (
            self.name is None
            and self.description is None
            and self.price is None
            and self.currency is None
            and self.duration is None
            and self.duration_unit is None
        ):
            raise ValueError(
                "At least one field must be provided for updating membership details."
            )
        if self.status == m_club.MembershipStatusPublic.DRAFT:
            raise ValueError("Status cannot be set to 'draft'; please use 'not_bookable' instead.")
        return self

class MembershipSubscription(BaseModel):
    """
    Model for a membership subscription.
    
    Fields:
        - user_id: The unique identifier of the user.
        - price: The subscription price (≥ 0).
        - start_datetime: The start date of the subscription.
        - end_datetime: (Optional) The end date of the subscription.
        - status: The status of the subscription.
        - active_subscription: Flag indicating if the subscription is currently active.
        - membership: The membership details associated with the subscription.
    """
    model_config = ConfigDict(from_attributes=True)
    user_id: uuid.UUID = Field(..., description="The unique identifier of the user.")
    subscription_price: int = Field(..., ge=0, description="The price of the subscription (must be ≥ 0).")
    stripe_subscription_id: str = Field(..., description="The Stripe subscription ID.")
    start_datetime: datetime.datetime = Field(..., description="The start date of the subscription.")
    end_datetime: Optional[datetime.datetime] = Field(None, description="The end date of the subscription.")
    status: m_club.MembershipSubscriptionStatus = Field(
        ..., description="The status of the subscription."
    )

    membership: Membership = Field(
        ..., description="The membership details associated with the subscription."
    )
