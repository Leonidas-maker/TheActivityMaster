from sqlalchemy.orm import Mapped, mapped_column, relationship
import warnings
from sqlalchemy.inspection import inspect
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
    Date,
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
from models.m_verification import *


########################################################################
# Enums
########################################################################


class SessionType(enum.Enum):
    COURSE = "course"  # Wiederkehrender Kurs
    EVENT = "event"  # Einmaliges Event


class Weekday(enum.Enum):
    MONDAY = "Monday"
    TUESDAY = "Tuesday"
    WEDNESDAY = "Wednesday"
    THURSDAY = "Thursday"
    FRIDAY = "Friday"
    SATURDAY = "Saturday"
    SUNDAY = "Sunday"


class OccurrenceStatus(enum.Enum):
    SCHEDULED = "scheduled"
    CANCELLED = "cancelled"
    RESCHEDULED = "rescheduled"


class BookingStatus(enum.Enum):
    PENDING = "Pending"
    CONFIRMED = "Confirmed"
    CANCELLED = "Cancelled"
    COMPLETED = "Completed"
    CANCELLED_BY_CLUB = "Cancelled by Club"


###########################################################################
################################### MAIN ##################################
###########################################################################
class Club(Base):
    __tablename__ = "clubs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    description: Mapped[Text] = mapped_column(Text(1000), nullable=False)
    stripe_account_id: Mapped[str] = mapped_column(String(255), nullable=True, unique=True)
    is_closed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    address_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("addresses.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(DEFAULT_TIMEZONE)
    )

    address: Mapped["Address"] = relationship("Address")
    memberships: Mapped[List["Membership"]] = relationship("Membership", back_populates="club", uselist=True)
    programs: Mapped[List["Program"]] = relationship("Program", back_populates="club", uselist=True)
    club_verifications: Mapped[List["ClubVerification"]] = relationship("ClubVerification", back_populates="club")
    club_roles: Mapped[List["ClubRole"]] = relationship("ClubRole", back_populates="club", uselist=True)

    @property
    def owners(self) -> List["User"]:
        """Get the owners of the club"""
        state = inspect(self)
        
        if "club_roles" in state.unloaded:
            warnings.warn("club_roles not loaded")
            return []
        
        owners = []
        for role in self.club_roles:
            if role.name == "Owner":
                owners.extend([ucr.user for ucr in role.user_club_roles])
        return owners


###########################################################################
############################ Program Offerings ############################
###########################################################################
class ProgramCategory(Base):
    __tablename__ = "program_categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    programs: Mapped[List["Program"]] = relationship(
        "Program", secondary="program_category_association", back_populates="categories"
    )


class ProgramCategoryAssociation(Base):
    __tablename__ = "program_category_association"

    program_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("programs.id"), primary_key=True)
    category_id: Mapped[int] = mapped_column(Integer, ForeignKey("program_categories.id"), primary_key=True)

    __table_args__ = (UniqueConstraint("program_id", "category_id", name="uix_program_category"),)


class Program(Base):
    """A program is a collection of sessions (e.g. a course)"""

    __tablename__ = "programs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    description: Mapped[str] = mapped_column(String(1000), nullable=False)
    club_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("clubs.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(DEFAULT_TIMEZONE)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(DEFAULT_TIMEZONE),
        onupdate=lambda: datetime.now(DEFAULT_TIMEZONE),
    )

    sessions: Mapped[list["Session"]] = relationship("Session", back_populates="program")
    club: Mapped["Club"] = relationship("Club", back_populates="programs")
    memberships: Mapped[List["MembershipAccess"]] = relationship("MembershipAccess", back_populates="program")
    categories: Mapped[List["ProgramCategory"]] = relationship(
        "ProgramCategory", secondary="program_category_association", back_populates="programs"
    )
    trainers: Mapped[List["User"]] = relationship("User", secondary="user_trainers")


class Session(Base):
    """A session is a single event or a recurring course"""

    __tablename__ = "sessions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    program_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("programs.id"), nullable=False)
    session_type: Mapped[SessionType] = mapped_column(Enum(SessionType), nullable=False)
    capacity: Mapped[int] = mapped_column(Integer, nullable=False)
    price: Mapped[DECIMAL] = mapped_column(DECIMAL(10, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False)  # ISO 4217

    # True if the session requires a membership
    membership_required: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    # Fields for one-time events:
    start_datetime: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    end_datetime: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Fields for recurring courses:
    day_of_week: Mapped[Weekday | None] = mapped_column(Enum(Weekday), nullable=True)
    start_time: Mapped[time | None] = mapped_column(Time, nullable=True)
    end_time: Mapped[time | None] = mapped_column(Time, nullable=True)
    # Defines the start and end date of the course
    start_date: Mapped[datetime | None] = mapped_column(Date(), nullable=True)
    end_date: Mapped[datetime | None] = mapped_column(Date(), nullable=True)

    # Optional: Address of the session (if different from the club address)
    address_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("addresses.id"), nullable=True)

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(DEFAULT_TIMEZONE),
        onupdate=lambda: datetime.now(DEFAULT_TIMEZONE),
    )

    program: Mapped["Program"] = relationship("Program", back_populates="sessions")
    occurrences: Mapped[list["SessionOccurrence"]] = relationship("SessionOccurrence", back_populates="session")

    address: Mapped["Address"] = relationship("Address")
    bookings: Mapped[List["Booking"]] = relationship("Booking", back_populates="session")


class SessionOccurrence(Base):
    """A concrete occurrence of a session (e.g. a planned date)"""

    __tablename__ = "session_occurrences"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("sessions.id"), nullable=False)
    # The scheduled date of the occurrence (e.g., the planned appointment)
    occurrence_date: Mapped[datetime] = mapped_column(Date(), nullable=False)
    # Optional: Specific start/end times if these deviate from the regular schedule (e.g., for rescheduling)
    start_datetime: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    end_datetime: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    # Status of the occurrence (scheduled, cancelled, rescheduled)
    status: Mapped[OccurrenceStatus] = mapped_column(
        Enum(OccurrenceStatus), nullable=False, default=OccurrenceStatus.SCHEDULED
    )
    # Optional: Notes for the occurrence (e.g., reason for rescheduling or cancellation)
    note: Mapped[str | None] = mapped_column(String(255), nullable=True)

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(DEFAULT_TIMEZONE),
        onupdate=lambda: datetime.now(DEFAULT_TIMEZONE),
    )

    session: Mapped["Session"] = relationship("Session", back_populates="occurrences")


###########################################################################
################################# BOOKINGS ################################
###########################################################################
class Booking(Base):
    __tablename__ = "bookings"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    session_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("sessions.id"), nullable=False)
    booking_type_id: Mapped[int] = mapped_column(Integer, ForeignKey("booking_types.id"), nullable=False)
    status: Mapped[BookingStatus] = mapped_column(Enum(BookingStatus), nullable=False)
    transaction_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("transactions.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(DEFAULT_TIMEZONE)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(DEFAULT_TIMEZONE),
        onupdate=lambda: datetime.now(DEFAULT_TIMEZONE),
    )

    user: Mapped["User"] = relationship("User", back_populates="bookings")
    session: Mapped["Session"] = relationship("Session", back_populates="bookings")
    booking_type: Mapped["BookingType"] = relationship("BookingType", back_populates="bookings")


class BookingType(Base):
    __tablename__ = "booking_types"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)

    bookings: Mapped[List["Booking"]] = relationship("Booking", back_populates="booking_type")


###########################################################################
############################### Memberships ###############################
###########################################################################
class Membership(Base):
    __tablename__ = "memberships"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    club_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("clubs.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    description: Mapped[Text] = mapped_column(Text(1000), nullable=False)
    price: Mapped[DECIMAL] = mapped_column(DECIMAL(10, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False)  # ISO 4217
    duration: Mapped[int] = mapped_column(Integer, nullable=False)  # Duration in Days
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(DEFAULT_TIMEZONE)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(DEFAULT_TIMEZONE),
        onupdate=lambda: datetime.now(DEFAULT_TIMEZONE),
    )

    club: Mapped["Club"] = relationship("Club", back_populates="memberships")
    programs_access: Mapped[List["MembershipAccess"]] = relationship("MembershipAccess", back_populates="membership")
    user_subscriptions: Mapped[List["MembershipSubscription"]] = relationship(
        "MembershipSubscription", back_populates="membership"
    )


class MembershipAccess(Base):
    __tablename__ = "membership_access"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    membership_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("memberships.id"), nullable=False)
    program_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("programs.id"), nullable=False)
    additional_fee: Mapped[DECIMAL] = mapped_column(DECIMAL(10, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False)  # ISO 4217

    membership: Mapped["Membership"] = relationship("Membership", back_populates="programs_access")
    program: Mapped["Program"] = relationship("Program", back_populates="memberships")

    __table_args__ = (UniqueConstraint("membership_id", "program_id", name="unique_membership_access"),)


class MembershipSubscription(Base):
    __tablename__ = "membership_subscriptions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    membership_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("memberships.id"), nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    start_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(DEFAULT_TIMEZONE)
    )
    end_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)

    user: Mapped["User"] = relationship("User", back_populates="membership_subscriptions")
    membership: Mapped["Membership"] = relationship("Membership", back_populates="user_subscriptions")
    transactions: Mapped[List["MembershipTransaction"]] = relationship(
        "MembershipTransaction", back_populates="membership_subscription"
    )

    __table_args__ = (UniqueConstraint("membership_id", "user_id", name="unique_membership_subscription"),)


class MembershipTransaction(Base):
    __tablename__ = "membership_transactions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    membership_subscription_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("membership_subscriptions.id"), nullable=False
    )
    transaction_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("transactions.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(DEFAULT_TIMEZONE)
    )

    membership_subscription: Mapped["MembershipSubscription"] = relationship(
        "MembershipSubscription", back_populates="transactions"
    )


###########################################################################
################################### User ##################################
###########################################################################
class ClubRolePermission(Base):
    __tablename__ = "club_role_permissions"

    role_id: Mapped[int] = mapped_column(Integer, ForeignKey("club_roles.id"), primary_key=True)
    permission_id: Mapped[int] = mapped_column(Integer, ForeignKey("permissions.id"), primary_key=True)

    __table_args__ = (UniqueConstraint("role_id", "permission_id", name="unique_role_permission"),)


class Permission(Base):
    __tablename__ = "permissions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    description: Mapped[str] = deferred(mapped_column(String(255), nullable=True))

    roles: Mapped[List["ClubRole"]] = relationship(
        "ClubRole", secondary="club_role_permissions", back_populates="permissions"
    )


class ClubRole(Base):
    __tablename__ = "club_roles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    level: Mapped[int] = mapped_column(Integer, nullable=False)  # Lower level means higher permissions
    club_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("clubs.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = deferred(mapped_column(String(255), nullable=False))

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(DEFAULT_TIMEZONE)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(DEFAULT_TIMEZONE),
        onupdate=lambda: datetime.now(DEFAULT_TIMEZONE),
    )

    permissions: Mapped[List["Permission"]] = relationship(
        "Permission", secondary="club_role_permissions", back_populates="roles", lazy="joined"
    )
    club = relationship("Club", back_populates="club_roles")

    user_club_roles: Mapped[List["UserClubRole"]] = relationship("UserClubRole", back_populates="club_role")

    __table_args__ = (
        UniqueConstraint("club_id", "level", name="unique_club_role"),
        UniqueConstraint("club_id", "name", name="unique_club_role_name"),
    )


class UserClubRole(Base):
    __tablename__ = "user_club_roles"

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True)
    club_role_id: Mapped[int] = mapped_column(Integer, ForeignKey("club_roles.id"), primary_key=True)
    assigned_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(DEFAULT_TIMEZONE)
    )

    user: Mapped["User"] = relationship("User", back_populates="club_roles")
    club_role: Mapped["ClubRole"] = relationship("ClubRole", back_populates="user_club_roles", lazy="joined")

    __table_args__ = (UniqueConstraint("user_id", "club_role_id", name="unique_user_club_role"),)


class UserTrainer(Base):
    __tablename__ = "user_trainers"

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True)
    program_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("programs.id"), primary_key=True)
    assigned_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(DEFAULT_TIMEZONE)
    )

    __table_args__ = (UniqueConstraint("user_id", "program_id", name="unique_user_trainer"),)
