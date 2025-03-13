from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import Mapped, mapped_column, relationship
import warnings
from sqlalchemy.inspection import inspect
from sqlalchemy import (
    event,
    DDL,
    String,
    Integer,
    ForeignKey,
    UniqueConstraint,
    UUID,
    Boolean,
    DateTime,
    PrimaryKeyConstraint,
    CheckConstraint,
    Enum,
    Text,
    DECIMAL,
    Time,
    Date,
    Computed,
)
from decimal import Decimal
import uuid
import enum
from typing import List, Optional


from config.database import Base
from config.settings import DEFAULT_TIMEZONE

from core.context import current_language_var


###########################################################################
################################## Enums ##################################
###########################################################################
class PriceType(enum.Enum):
    PACKAGE = "package"
    PER_SESSION = "per_session"


class SessionType(enum.Enum):
    COURSE = "course"  # Recurring Course
    EVENT = "event"  # One-time Event


class ProgramStatus(enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    DRAFT = "draft"
    DELETED = "deleted"
    FORCE_DELETED = "force_deleted"


class ProgramStatusPublic(enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    DRAFT = "draft"

    def to_internal(self) -> ProgramStatus:
        if self == ProgramStatusPublic.ACTIVE:
            return ProgramStatus.ACTIVE
        if self == ProgramStatusPublic.INACTIVE:
            return ProgramStatus.INACTIVE
        if self == ProgramStatusPublic.DRAFT:
            return ProgramStatus.DRAFT
        raise ValueError(f"Invalid ProgramStatusPublic value: {self}")


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


class DurationUnit(enum.Enum):
    DAY = "day"
    MONTH = "month"


class MembershipStatus(enum.Enum):
    DRAFT = "draft"
    BOOKABLE = "bookable"
    NOT_BOOKABLE = "not_bookable"
    DELETED = "deleted"


class MembershipStatusPublic(enum.Enum):
    DRAFT = "draft"
    BOOKABLE = "bookable"
    NOT_BOOKABLE = "not_bookable"

    def to_internal(self) -> MembershipStatus:
        if self == MembershipStatusPublic.DRAFT:
            return MembershipStatus.DRAFT
        if self == MembershipStatusPublic.BOOKABLE:
            return MembershipStatus.BOOKABLE
        if self == MembershipStatusPublic.NOT_BOOKABLE:
            return MembershipStatus.NOT_BOOKABLE
        raise ValueError(f"Invalid MembershipStatusPublic value: {self}")


###########################################################################
############################# Database Models #############################
###########################################################################
from models.m_generic import *
from models.m_audit import *
from models.m_verification import *
from models.m_payment import *
import datetime


class Club(Base):
    __tablename__ = "clubs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    description: Mapped[Text] = mapped_column(Text(1000), nullable=False)
    stripe_account_id: Mapped[str | None] = mapped_column(String(255), nullable=True, unique=True)
    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    address_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("addresses.id"), nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.datetime.now(DEFAULT_TIMEZONE)
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.datetime.now(DEFAULT_TIMEZONE),
        onupdate=lambda: datetime.datetime.now(DEFAULT_TIMEZONE),
    )

    address: Mapped["Address"] = relationship("Address")  # type: ignore
    memberships: Mapped[List["Membership"]] = relationship("Membership", back_populates="club", uselist=True)
    programs: Mapped[List["Program"]] = relationship("Program", back_populates="club", uselist=True)
    club_verifications: Mapped[List["ClubVerification"]] = relationship("ClubVerification", back_populates="club")
    club_roles: Mapped[List["ClubRole"]] = relationship("ClubRole", back_populates="club", uselist=True)

    @property
    def owners(self) -> List["User"]:  # type: ignore
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
class ProgramCategoryTranslation(Base):
    __tablename__ = "program_category_translations"

    category_id: Mapped[int] = mapped_column(Integer, ForeignKey("program_categories.id"), primary_key=True)
    language: Mapped[str] = mapped_column(String(2), primary_key=True)  # ISO 639-1
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)

    category: Mapped["ProgramCategory"] = relationship("ProgramCategory", back_populates="translations")


class ProgramCategory(Base):
    __tablename__ = "program_categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    translations: Mapped[List["ProgramCategoryTranslation"]] = relationship(
        "ProgramCategoryTranslation", back_populates="category", cascade="all, delete-orphan", lazy="joined"
    )

    programs: Mapped[List["Program"]] = relationship(
        "Program", secondary="program_category_association", back_populates="categories"
    )

    def get_translation(self, lang: str) -> "ProgramCategoryTranslation":
        for translation in self.translations:
            if translation.language == lang:
                return translation
        for translation in self.translations:
            if translation.language == "en":
                return translation
        raise ValueError(f"No default translation found for category {self.id}")

    @property
    def name(self) -> str:
        lang = current_language_var.get()
        translation = self.get_translation(lang)
        return translation.name

    @property
    def description(self) -> str:
        lang = current_language_var.get()
        translation = self.get_translation(lang)
        return translation.description


class ProgramCategoryAssociation(Base):
    __tablename__ = "program_category_association"

    program_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("programs.id"), primary_key=True)
    category_id: Mapped[int] = mapped_column(Integer, ForeignKey("program_categories.id"), primary_key=True)

    __table_args__ = (UniqueConstraint("program_id", "category_id", name="uix_program_category"),)


class Program(Base):
    """A program is a collection of sessions (e.g. a course)"""

    __tablename__ = "programs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    club_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("clubs.id"), nullable=False)

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = deferred(mapped_column(String(500), nullable=False))

    price: Mapped[int | None] = mapped_column(Integer, nullable=True)
    currency: Mapped[str] = mapped_column(String(3), nullable=False)  # ISO 4217
    pricing_model: Mapped[PriceType] = mapped_column(Enum(PriceType), nullable=False, default=PriceType.PACKAGE)

    capacity: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Membership required to access the program
    membership_required: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    status: Mapped[ProgramStatus] = mapped_column(Enum(ProgramStatus), nullable=False, default=ProgramStatus.DRAFT)

    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.datetime.now(DEFAULT_TIMEZONE)
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.datetime.now(DEFAULT_TIMEZONE),
        onupdate=lambda: datetime.datetime.now(DEFAULT_TIMEZONE),
    )
    deleted_at: Mapped[datetime.datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    active_program: Mapped[bool | None] = mapped_column(
        Boolean, Computed("CASE WHEN status NOT IN ('deleted', 'force_deleted') THEN TRUE ELSE NULL END")
    )

    @property
    def membership_ids(self) -> List[uuid.UUID]:
        return [ma.membership_id for ma in self.memberships_access]

    sessions: Mapped[list["Session"]] = relationship("Session", back_populates="program")
    club: Mapped["Club"] = relationship("Club", back_populates="programs")
    memberships_access: Mapped[List["MembershipAccess"]] = relationship("MembershipAccess", back_populates="program")
    categories: Mapped[List["ProgramCategory"]] = relationship(
        "ProgramCategory", secondary="program_category_association", back_populates="programs"
    )
    trainers: Mapped[List["User"]] = relationship("User", secondary="user_trainers")  # type: ignore

    __table_args__ = (
        UniqueConstraint("club_id", "name", "active_program", name="unique_program"),
        CheckConstraint("price >= 0", name="chk_price_non_negative"),
        CheckConstraint("capacity >= 0", name="chk_capacity_non_negative"),
        CheckConstraint(
            "status NOT IN ('deleted', 'force_deleted') AND deleted_at IS NULL OR status IN ('deleted', 'force_deleted') AND deleted_at IS NOT NULL",
            name="chk_status_deleted",
        ),
        # Pricingmodell-Logic: Package-Pricing requires price and capacity, per_session requires none
        CheckConstraint(
            "((pricing_model = 'package' AND price IS NOT NULL AND capacity IS NOT NULL) OR "
            "(pricing_model = 'per_session' AND price IS NULL AND capacity IS NULL))",
            name="chk_pricing_model_consistency",
        ),
    )


class Session(Base):
    """A session is a single event or a recurring course"""

    __tablename__ = "sessions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    program_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("programs.id"), nullable=False)
    session_type: Mapped[SessionType] = mapped_column(Enum(SessionType), nullable=False)
    capacity: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Individual price for the session
    price: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Fields for one-time events:
    start_datetime: Mapped[datetime.datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    end_datetime: Mapped[datetime.datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Fields for recurring courses:
    day_of_week: Mapped[Weekday | None] = mapped_column(Enum(Weekday), nullable=True)
    start_time: Mapped[datetime.time | None] = mapped_column(Time, nullable=True)
    end_time: Mapped[datetime.time | None] = mapped_column(Time, nullable=True)
    # Defines the start and end date of the course
    start_date: Mapped[datetime.date | None] = mapped_column(Date(), nullable=True)
    end_date: Mapped[datetime.date | None] = mapped_column(Date(), nullable=True)

    # Optional: Address of the session (if different from the club address)
    address_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("addresses.id"), nullable=True)

    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.datetime.now(DEFAULT_TIMEZONE),
        onupdate=lambda: datetime.datetime.now(DEFAULT_TIMEZONE),
    )
    deleted_at: Mapped[datetime.datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    program: Mapped["Program"] = relationship("Program", back_populates="sessions")
    occurrences: Mapped[list["SessionOccurrence"]] = relationship(
        "SessionOccurrence",
        back_populates="session",
        cascade="all, delete-orphan",
        uselist=True,
        order_by="SessionOccurrence.occurrence_date",
    )
    address: Mapped["Address"] = relationship("Address")  # type: ignore
    bookings: Mapped[List["Booking"]] = relationship("Booking", back_populates="session")  # type: ignore

    __table_args__ = (
        CheckConstraint("price >= 0", name="chk_price_non_negative"),
        CheckConstraint("capacity >= 0", name="chk_capacity_non_negative"),
        CheckConstraint("start_datetime < end_datetime", name="chk_start_end_datetime"),
        CheckConstraint("start_date < end_date", name="chk_start_end_date"),
        CheckConstraint("start_time < end_time", name="chk_start_end_time"),
        # Logic based on session_type:
        # EVENT: start_datetime and end_datetime must be set, and all course-specific fields must be NULL.
        # COURSE: start_datetime and end_datetime must be NULL, and course-specific fields (except end_date) must be set.
        CheckConstraint(
            "("
            "  (session_type = 'event' AND start_datetime IS NOT NULL AND end_datetime IS NOT NULL "
            "   AND day_of_week IS NULL AND start_time IS NULL AND end_time IS NULL AND start_date IS NULL AND end_date IS NULL) "
            " OR "
            "  (session_type = 'course' AND start_datetime IS NULL AND end_datetime IS NULL "
            "   AND day_of_week IS NOT NULL AND start_time IS NOT NULL AND end_time IS NOT NULL AND start_date IS NOT NULL)"
            ")",
            name="chk_session_type_fields",
        ),
    )


class SessionOccurrence(Base):
    """A concrete occurrence of a session (e.g. a planned date)"""

    __tablename__ = "session_occurrences"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False
    )
    # The scheduled date of the occurrence (e.g., the planned appointment)
    occurrence_date: Mapped[datetime.date] = mapped_column(Date(), nullable=False)
    # Optional: Specific start/end times if these deviate from the regular schedule (e.g., for rescheduling)
    start_datetime: Mapped[datetime.datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    end_datetime: Mapped[datetime.datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    # Status of the occurrence (scheduled, cancelled, rescheduled)
    status: Mapped[OccurrenceStatus] = mapped_column(
        Enum(OccurrenceStatus), nullable=False, default=OccurrenceStatus.SCHEDULED
    )
    # Optional: Notes for the occurrence (e.g., reason for rescheduling or cancellation)
    note: Mapped[str | None] = mapped_column(String(255), nullable=True)

    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.datetime.now(DEFAULT_TIMEZONE),
        onupdate=lambda: datetime.datetime.now(DEFAULT_TIMEZONE),
    )

    session: Mapped["Session"] = relationship("Session", back_populates="occurrences")


###########################################################################
############################### Memberships ###############################
###########################################################################
class Membership(Base):
    __tablename__ = "memberships"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    club_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("clubs.id"), nullable=False)

    stripe_product_id: Mapped[str] = mapped_column(String(255), nullable=True, unique=True)
    stripe_price_id: Mapped[str] = mapped_column(String(255), nullable=True, unique=True)

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = deferred(mapped_column(String(500), nullable=False))
    price: Mapped[int] = mapped_column(Integer, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False)  # ISO 4217
    duration: Mapped[int] = mapped_column(Integer, nullable=False)
    duration_unit: Mapped[DurationUnit] = mapped_column(Enum(DurationUnit), nullable=False, default=DurationUnit.MONTH)

    status: Mapped[MembershipStatus] = mapped_column(
        Enum(MembershipStatus), nullable=False, default=MembershipStatus.DRAFT
    )

    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.datetime.now(DEFAULT_TIMEZONE)
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.datetime.now(DEFAULT_TIMEZONE),
        onupdate=lambda: datetime.datetime.now(DEFAULT_TIMEZONE),
    )
    deleted_at: Mapped[datetime.datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    active_membership: Mapped[bool | None] = mapped_column(
        Boolean, Computed("CASE WHEN status NOT IN ('deleted') THEN TRUE ELSE NULL END")
    )

    club: Mapped["Club"] = relationship("Club", back_populates="memberships", viewonly=True)
    programs_access: Mapped[List["MembershipAccess"]] = relationship("MembershipAccess", back_populates="membership")
    user_subscriptions: Mapped[List["MembershipSubscription"]] = relationship(  # type: ignore
        "MembershipSubscription", back_populates="membership"
    )

    __table_args__ = (
        UniqueConstraint("club_id", "name", "active_membership", name="unique_membership"),
        CheckConstraint("price >= 0", name="chk_price_non_negative"),
        CheckConstraint("duration > 0", name="chk_duration_positive"),
        CheckConstraint(
            "status NOT IN ('deleted') AND deleted_at IS NULL OR status IN ('deleted') AND deleted_at IS NOT NULL",
            name="chk_status_deleted",
        ),
    )


class MembershipAccess(Base):
    __tablename__ = "membership_access"

    membership_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("memberships.id"), nullable=False, primary_key=True
    )
    program_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("programs.id"), nullable=False, primary_key=True
    )
    additional_fee: Mapped[int | None] = mapped_column(Integer, nullable=True)

    membership: Mapped["Membership"] = relationship("Membership", back_populates="programs_access")
    program: Mapped["Program"] = relationship("Program", back_populates="memberships_access")

    __table_args__ = (
        UniqueConstraint("membership_id", "program_id", name="unique_membership_access"),
        UniqueConstraint("program_id", "membership_id", name="unique_program_membership_access"),
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

    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.datetime.now(DEFAULT_TIMEZONE)
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.datetime.now(DEFAULT_TIMEZONE),
        onupdate=lambda: datetime.datetime.now(DEFAULT_TIMEZONE),
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
    assigned_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.datetime.now(DEFAULT_TIMEZONE)
    )

    user: Mapped["User"] = relationship("User", back_populates="club_roles")  # type: ignore
    club_role: Mapped["ClubRole"] = relationship("ClubRole", back_populates="user_club_roles", lazy="joined")

    __table_args__ = (UniqueConstraint("user_id", "club_role_id", name="unique_user_club_role"),)


class UserTrainer(Base):
    __tablename__ = "user_trainers"

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True)
    program_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("programs.id", ondelete="CASCADE"), primary_key=True
    )
    assigned_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.datetime.now(DEFAULT_TIMEZONE)
    )

    __table_args__ = (UniqueConstraint("user_id", "program_id", name="unique_user_trainer"),)


###########################################################################
################################# Triggers ################################
###########################################################################
trigger_session_pricing_before_insert = DDL(
    """
CREATE TRIGGER check_session_pricing_before_insert
BEFORE INSERT ON sessions
FOR EACH ROW
BEGIN
    DECLARE p_model VARCHAR(20);
    SELECT pricing_model INTO p_model FROM programs WHERE id = NEW.program_id;
    IF p_model = 'package' THEN
        IF NEW.price IS NOT NULL OR NEW.capacity IS NOT NULL THEN
            SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'For programs with PACKAGE pricing, session price and capacity must be NULL';
        END IF;
    ELSEIF p_model = 'per_session' THEN
        IF NEW.price IS NULL OR NEW.capacity IS NULL THEN
            SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'For programs with PER_SESSION pricing, session price and capacity must be set';
        END IF;
    END IF;
END;
"""
)

trigger_session_pricing_before_update = DDL(
    """
CREATE TRIGGER check_session_pricing_before_update
BEFORE UPDATE ON sessions
FOR EACH ROW
BEGIN
    DECLARE p_model VARCHAR(20);
    SELECT pricing_model INTO p_model FROM programs WHERE id = NEW.program_id;
    IF p_model = 'package' THEN
        IF NEW.price IS NOT NULL OR NEW.capacity IS NOT NULL THEN
            SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'For programs with PACKAGE pricing, session price and capacity must be NULL';
        END IF;
    ELSEIF p_model = 'per_session' THEN
        IF NEW.price IS NULL OR NEW.capacity IS NULL THEN
            SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'For programs with PER_SESSION pricing, session price and capacity must be set';
        END IF;
    END IF;
END;
"""
)

# Add triggers to check session pricing consistency
event.listen(Session.__table__, "after_create", trigger_session_pricing_before_insert)
event.listen(Session.__table__, "after_create", trigger_session_pricing_before_update)
