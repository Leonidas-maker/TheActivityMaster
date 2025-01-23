from typing import Annotated
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import (
    String,
    Integer,
    ForeignKey,
    UniqueConstraint,
    UUID,
    Boolean,
    DateTime,
    PrimaryKeyConstraint,
    Enum,
    Text,
    DECIMAL,
    Time,
)
import uuid
from datetime import datetime, time
import enum
from typing import List

from config.database import Base
from config.settings import DEFAULT_TIMEZONE

from models.m_generic import *
from models.m_club import *
from models.m_audit import *
from models.m_payment import *

class Club(Base):
    __tablename__ = "clubs"

    id: Mapped[Annotated[uuid.UUID, mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)]]
    name: Mapped[Annotated[str, mapped_column(String(100), nullable=False)]]
    description: Mapped[Annotated[Text, mapped_column(Text(1000), nullable=False)]]
    stripe_account_id: Mapped[Annotated[str, mapped_column(String(255), nullable=True)]]
    address_id: Mapped[
        Annotated[uuid.UUID, mapped_column(UUID(as_uuid=True), ForeignKey("addresses.id"), nullable=False)]
    ]
    created_at: Mapped[
        Annotated[datetime, mapped_column(DateTime, nullable=False, default=lambda: datetime.now(DEFAULT_TIMEZONE))]
    ]

    address: Mapped["Address"] = relationship("Address")
    memberships: Mapped[List["Membership"]] = relationship("Membership", back_populates="club", uselist=True)
    programs: Mapped[List["Program"]] = relationship("Program", back_populates="club", uselist=True)


class Membership(Base):
    __tablename__ = "memberships"

    id: Mapped[Annotated[uuid.UUID, mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)]]
    club_id: Mapped[Annotated[uuid.UUID, mapped_column(UUID(as_uuid=True), ForeignKey("clubs.id"), nullable=False)]]
    name: Mapped[Annotated[str, mapped_column(String(100), nullable=False)]]
    description: Mapped[Annotated[Text, mapped_column(Text(1000), nullable=False)]]
    price: Mapped[Annotated[DECIMAL, mapped_column(DECIMAL(10, 2), nullable=False)]]
    currency: Mapped[Annotated[str, mapped_column(String(3), nullable=False)]]  # ISO 4217
    duration: Mapped[Annotated[int, mapped_column(Integer, nullable=False)]]  # in months
    created_at: Mapped[
        Annotated[datetime, mapped_column(DateTime, nullable=False, default=lambda: datetime.now(DEFAULT_TIMEZONE))]
    ]
    updated_at: Mapped[
        Annotated[
            datetime,
            mapped_column(
                DateTime,
                nullable=False,
                default=lambda: datetime.now(DEFAULT_TIMEZONE),
                onupdate=lambda: datetime.now(DEFAULT_TIMEZONE),
            ),
        ]
    ]

    club: Mapped["Club"] = relationship("Club", back_populates="memberships")
    programs_access: Mapped[List["MembershipAccess"]] = relationship("MembershipAccess", back_populates="membership")
    user_subscriptions: Mapped[List["MembershipSubscription"]] = relationship(
        "MembershipSubscription", back_populates="membership"
    )


class MembershipSubscription(Base):
    __tablename__ = "membership_subscriptions"

    id: Mapped[Annotated[uuid.UUID, mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)]]
    membership_id: Mapped[
        Annotated[uuid.UUID, mapped_column(UUID(as_uuid=True), ForeignKey("memberships.id"), nullable=False)]
    ]
    user_id: Mapped[Annotated[uuid.UUID, mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)]]
    start_time: Mapped[
        Annotated[datetime, mapped_column(DateTime, nullable=False, default=lambda: datetime.now(DEFAULT_TIMEZONE))]
    ]
    end_time: Mapped[Annotated[datetime, mapped_column(DateTime, nullable=True)]]

    user: Mapped["Membership"] = relationship("User", back_populates="membership_subscriptions")
    membership: Mapped["Membership"] = relationship("Membership", back_populates="user_subscriptions")


class MembershipAccess(Base):
    __tablename__ = "membership_access"

    id: Mapped[Annotated[uuid.UUID, mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)]]
    membership_id: Mapped[
        Annotated[uuid.UUID, mapped_column(UUID(as_uuid=True), ForeignKey("memberships.id"), nullable=False)]
    ]
    program_id: Mapped[
        Annotated[uuid.UUID, mapped_column(UUID(as_uuid=True), ForeignKey("programs.id"), nullable=False)]
    ]
    additional_fee: Mapped[Annotated[DECIMAL, mapped_column(DECIMAL(10, 2), nullable=False)]]
    currency: Mapped[Annotated[str, mapped_column(String(3), nullable=False)]]  # ISO 4217

    membership: Mapped["Membership"] = relationship("Membership", back_populates="programs_access")
    program: Mapped["Program"] = relationship("Program", back_populates="memberships")

class MembershipTransaction(Base):
    __tablename__ = "membership_transactions"

    id: Mapped[Annotated[uuid.UUID, mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)]]
    membership_id: Mapped[
        Annotated[uuid.UUID, mapped_column(UUID(as_uuid=True), ForeignKey("memberships.id"), nullable=False)]
    ]
    transaction_id: Mapped[
        Annotated[uuid.UUID, mapped_column(UUID(as_uuid=True), ForeignKey("transactions.id"), nullable=False)]
    ]
    created_at: Mapped[
        Annotated[datetime, mapped_column(DateTime, nullable=False, default=lambda: datetime.now(DEFAULT_TIMEZONE))]
    ]


class ProgramType(Base):
    __tablename__ = "program_types"

    id: Mapped[Annotated[int, mapped_column(Integer, primary_key=True, autoincrement=True)]]
    name: Mapped[Annotated[str, mapped_column(String(50), nullable=False)]]

    programs: Mapped[List["Program"]] = relationship("Program", back_populates="program_types")


class Program(Base):
    __tablename__ = "programs"

    id: Mapped[Annotated[uuid.UUID, mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)]]
    name: Mapped[Annotated[str, mapped_column(String(100), nullable=False)]]
    description: Mapped[Annotated[Text, mapped_column(Text(1000), nullable=False)]]
    program_type_id: Mapped[Annotated[int, mapped_column(Integer, ForeignKey("program_types.id"), nullable=False)]]
    is_event: Mapped[Annotated[bool, mapped_column(Boolean, nullable=False, default=False)]]
    capacity: Mapped[Annotated[int, mapped_column(Integer, nullable=False)]]
    club_id: Mapped[Annotated[uuid.UUID, mapped_column(UUID(as_uuid=True), ForeignKey("clubs.id"), nullable=False)]]
    created_at: Mapped[
        Annotated[datetime, mapped_column(DateTime, nullable=False, default=lambda: datetime.now(DEFAULT_TIMEZONE))]
    ]
    updated_at: Mapped[
        Annotated[
            datetime,
            mapped_column(
                DateTime,
                nullable=False,
                default=lambda: datetime.now(DEFAULT_TIMEZONE),
                onupdate=lambda: datetime.now(DEFAULT_TIMEZONE),
            ),
        ]
    ]

    program_types: Mapped[List["ProgramType"]] = relationship("ProgramType", back_populates="programs")
    memberships: Mapped[List["MembershipAccess"]] = relationship(
        "MembershipAccess", back_populates="program", uselist=True
    )
    club: Mapped["Club"] = relationship("Club", back_populates="programs")

    course: Mapped["Course"] = relationship("Course", back_populates="program")
    event: Mapped["Event"] = relationship("Event", back_populates="program")
    bookings: Mapped[List["Booking"]] = relationship("Booking", back_populates="program")


class Event(Base):
    __tablename__ = "events"

    id: Mapped[Annotated[uuid.UUID, mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)]]
    start_time: Mapped[Annotated[datetime, mapped_column(DateTime, nullable=False)]]
    end_time: Mapped[Annotated[datetime, mapped_column(DateTime, nullable=False)]]
    price: Mapped[Annotated[DECIMAL, mapped_column(DECIMAL(10, 2), nullable=False)]]
    currency: Mapped[Annotated[str, mapped_column(String(3), nullable=False)]]  # ISO 4217
    program_id: Mapped[
        Annotated[uuid.UUID, mapped_column(UUID(as_uuid=True), ForeignKey("programs.id"), nullable=False)]
    ]
    created_at: Mapped[
        Annotated[datetime, mapped_column(DateTime, nullable=False, default=lambda: datetime.now(DEFAULT_TIMEZONE))]
    ]
    updated_at: Mapped[
        Annotated[
            datetime,
            mapped_column(
                DateTime,
                nullable=False,
                default=lambda: datetime.now(DEFAULT_TIMEZONE),
                onupdate=lambda: datetime.now(DEFAULT_TIMEZONE),
            ),
        ]
    ]

    program: Mapped["Program"] = relationship("Program", back_populates="event")


class Course(Base):
    __tablename__ = "courses"

    id: Mapped[Annotated[uuid.UUID, mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)]]
    program_id: Mapped[
        Annotated[uuid.UUID, mapped_column(UUID(as_uuid=True), ForeignKey("programs.id"), nullable=False)]
    ]
    price: Mapped[Annotated[DECIMAL, mapped_column(DECIMAL(10, 2), nullable=False)]]
    currency: Mapped[Annotated[str, mapped_column(String(3), nullable=False)]]  # ISO 4217
    subscription_required: Mapped[Annotated[bool, mapped_column(Boolean, nullable=False)]]
    created_at: Mapped[
        Annotated[datetime, mapped_column(DateTime, nullable=False, default=lambda: datetime.now(DEFAULT_TIMEZONE))]
    ]
    updated_at: Mapped[
        Annotated[
            datetime,
            mapped_column(
                DateTime,
                nullable=False,
                default=lambda: datetime.now(DEFAULT_TIMEZONE),
                onupdate=lambda: datetime.now(DEFAULT_TIMEZONE),
            ),
        ]
    ]

    program: Mapped["Program"] = relationship("Program", back_populates="course")
    sessions: Mapped[List["Session"]] = relationship("Session", back_populates="course", uselist=True)


class Weekday(enum.Enum):
    MONDAY = "Monday"
    TUESDAY = "Tuesday"
    WEDNESDAY = "Wednesday"
    THURSDAY = "Thursday"
    FRIDAY = "Friday"
    SATURDAY = "Saturday"
    SUNDAY = "Sunday"


class Session(Base):
    __tablename__ = "sessions"

    id: Mapped[Annotated[uuid.UUID, mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)]]
    course_id: Mapped[Annotated[uuid.UUID, mapped_column(UUID(as_uuid=True), ForeignKey("courses.id"), nullable=True)]]
    day_of_week: Mapped[Annotated[Weekday, mapped_column(Enum(Weekday), nullable=False)]]
    start_time: Mapped[Annotated[time, mapped_column(Time, nullable=False)]]
    end_time: Mapped[Annotated[time, mapped_column(Time, nullable=False)]]
    start_date: Mapped[Annotated[datetime, mapped_column(DateTime, nullable=True)]]
    end_date: Mapped[Annotated[datetime, mapped_column(DateTime, nullable=True)]]
    address_id: Mapped[
        Annotated[uuid.UUID, mapped_column(UUID(as_uuid=True), ForeignKey("addresses.id"), nullable=True)]
    ]

    course: Mapped["Course"] = relationship("Course", back_populates="sessions")


class BookingStatus(enum.Enum):
    PENDING = "Pending"
    CONFIRMED = "Confirmed"
    CANCELLED = "Cancelled"
    COMPLETED = "Completed"
    CANCELLED_BY_CLUB = "Cancelled by Club"

class Booking(Base):
    __tablename__ = "bookings"

    id: Mapped[Annotated[uuid.UUID, mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)]]
    user_id: Mapped[Annotated[uuid.UUID, mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)]]
    program_id: Mapped[
        Annotated[uuid.UUID, mapped_column(UUID(as_uuid=True), ForeignKey("programs.id"), nullable=False)]
    ]
    booking_type_id: Mapped[Annotated[int, mapped_column(Integer, ForeignKey("booking_types.id"), nullable=False)]]
    status: Mapped[Annotated[BookingStatus, mapped_column(Enum(BookingStatus), nullable=False)]]
    transaction_id: Mapped[
        Annotated[uuid.UUID, mapped_column(UUID(as_uuid=True), ForeignKey("transactions.id"), nullable=True)]
    ]
    created_at: Mapped[
        Annotated[datetime, mapped_column(DateTime, nullable=False, default=lambda: datetime.now(DEFAULT_TIMEZONE))]
    ]
    updated_at: Mapped[
        Annotated[
            datetime,
            mapped_column(
                DateTime,
                nullable=False,
                default=lambda: datetime.now(DEFAULT_TIMEZONE),
                onupdate=lambda: datetime.now(DEFAULT_TIMEZONE),
            ),
        ]
    ]

    user: Mapped["User"] = relationship("User", back_populates="bookings")
    program: Mapped["Program"] = relationship("Program", back_populates="bookings")
    booking_types: Mapped["BookingType"] = relationship("BookingType", back_populates="bookings")


class BookingType(Base):
    __tablename__ = "booking_types"

    id: Mapped[Annotated[int, mapped_column(Integer, primary_key=True, autoincrement=True)]]
    name: Mapped[Annotated[str, mapped_column(String(50), nullable=False, unique=True)]]

    bookings = relationship("Booking", back_populates="booking_types")




###########################################################################
################################### User ##################################
###########################################################################


class ClubRole(Base):
    __tablename__ = "club_roles"

    id: Mapped[Annotated[int, mapped_column(Integer, primary_key=True, autoincrement=True)]]
    name: Mapped[Annotated[str, mapped_column(String(100), nullable=False)]]
    description: Mapped[Annotated[str, mapped_column(String(255), nullable=False)]]

    users: Mapped[List["User"]] = relationship("User", back_populates="club_roles", secondary="user_club_roles", uselist=True)


class UserClubRole(Base):
    __tablename__ = "user_club_roles"

    user_id: Mapped[Annotated[uuid.UUID, mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True)]]
    club_id: Mapped[Annotated[uuid.UUID, mapped_column(UUID(as_uuid=True), ForeignKey("clubs.id"), primary_key=True)]]
    club_role_id: Mapped[Annotated[int, mapped_column(Integer, ForeignKey("club_roles.id"), primary_key=True)]]
    assigned_at: Mapped[
        Annotated[datetime, mapped_column(DateTime, nullable=False, default=lambda: datetime.now(DEFAULT_TIMEZONE))]
    ]

    __table_args__ = (UniqueConstraint("user_id", "club_id", "club_role_id", name="unique_user_club_role"),)