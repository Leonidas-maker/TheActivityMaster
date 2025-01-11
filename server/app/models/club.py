from typing import Annotated
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, ForeignKey, UniqueConstraint, UUID, Boolean, DateTime, PrimaryKeyConstraint, Enum, Text, DECIMAL, Time
import uuid
from datetime import datetime, time
import enum

from models.generic import *
from models.user import *
from config.database import Base
from config.settings import DEFAULT_TIMEZONE

class Club(Base):
    __tablename__ = "clubs"

    id: Mapped[Annotated[uuid.UUID, mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)]]
    name: Mapped[Annotated[str, mapped_column(String(100), nullable=False)]]
    description: Mapped[Annotated[Text, mapped_column(Text(1000), nullable=False)]]
    address_id: Mapped[Annotated[uuid.UUID, mapped_column(UUID(as_uuid=True), ForeignKey("addresses.id"), nullable=False)]]
    created_at: Mapped[Annotated[datetime, mapped_column(DateTime, nullable=False, default=datetime.now(DEFAULT_TIMEZONE))]]

    address = relationship("Address", back_populates="clubs")
    memberships = relationship("Membership", back_populates="club")
    programs = relationship("Program", back_populates="club")

class Membership(Base):
    __tablename__ = "memberships"

    id: Mapped[Annotated[uuid.UUID, mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)]]
    club_id: Mapped[Annotated[uuid.UUID, mapped_column(UUID(as_uuid=True), ForeignKey("clubs.id"), nullable=False)]]
    name: Mapped[Annotated[str, mapped_column(String(100), nullable=False)]]
    description: Mapped[Annotated[Text, mapped_column(Text(1000), nullable=False)]]
    price: Mapped[Annotated[DECIMAL, mapped_column(DECIMAL(10, 2), nullable=False)]]
    currency: Mapped[Annotated[str, mapped_column(String(3), nullable=False)]] # ISO 4217
    duration: Mapped[Annotated[int, mapped_column(Integer, nullable=False)]] # in months
    created_at: Mapped[Annotated[datetime, mapped_column(DateTime, nullable=False, default=datetime.now(DEFAULT_TIMEZONE))]]
    updated_at: Mapped[Annotated[datetime, mapped_column(DateTime, nullable=False, default=datetime.now(DEFAULT_TIMEZONE), onupdate=datetime.now(DEFAULT_TIMEZONE))]]

    club = relationship("Club", back_populates="memberships")
    programs_access = relationship("Program", secondary="membership_access", back_populates="membership")
    users = relationship("User", secondary="membership_subscriptions", back_populates="memberships")

class MembershipSubscription(Base):
    __tablename__ = "membership_subscriptions"

    id: Mapped[Annotated[uuid.UUID, mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)]]
    membership_id: Mapped[Annotated[uuid.UUID, mapped_column(UUID(as_uuid=True), ForeignKey("memberships.id"), nullable=False)]]
    user_id: Mapped[Annotated[uuid.UUID, mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)]]
    start_time: Mapped[Annotated[datetime, mapped_column(DateTime, nullable=False, default=datetime.now(DEFAULT_TIMEZONE))]]
    end_time: Mapped[Annotated[datetime, mapped_column(DateTime, nullable=True)]]

    user = relationship("User", back_populates="membership_subscriptions")
    membership = relationship("Membership", back_populates="membership_subscriptions")

class MembershipAccess(Base):
    __tablename__ = "membership_access"

    id: Mapped[Annotated[uuid.UUID, mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)]]
    membership_id: Mapped[Annotated[uuid.UUID, mapped_column(UUID(as_uuid=True), ForeignKey("memberships.id"), nullable=False)]]
    program_id: Mapped[Annotated[uuid.UUID, mapped_column(UUID(as_uuid=True), ForeignKey("programs.id"), nullable=False)]]
    additional_fee: Mapped[Annotated[DECIMAL, mapped_column(DECIMAL(10, 2), nullable=False)]]
    currency: Mapped[Annotated[str, mapped_column(String(3), nullable=False)]] # ISO 4217

    membership = relationship("Membership", back_populates="membership_access")
    program = relationship("Program", back_populates="membership_access")


class ProgramType(Base):
    __tablename__ = "program_types"

    id: Mapped[Annotated[int, mapped_column(Integer, primary_key=True, autoincrement=True)]]
    name: Mapped[Annotated[str, mapped_column(String(50), nullable=False)]]

    programs = relationship("Program", back_populates="program_types")

class Program(Base):
    __tablename__ = "programs"

    id: Mapped[Annotated[uuid.UUID, mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)]]
    name: Mapped[Annotated[str, mapped_column(String(100), nullable=False)]]
    description: Mapped[Annotated[Text, mapped_column(Text(1000), nullable=False)]]
    program_type_id: Mapped[Annotated[int, mapped_column(Integer, ForeignKey("program_types.id"), nullable=False)]]
    is_event: Mapped[Annotated[bool, mapped_column(Boolean, nullable=False, default=False)]]
    capacity: Mapped[Annotated[int, mapped_column(Integer, nullable=False)]]
    club_id: Mapped[Annotated[uuid.UUID, mapped_column(UUID(as_uuid=True), ForeignKey("clubs.id"), nullable=False)]]
    created_at: Mapped[Annotated[datetime, mapped_column(DateTime, nullable=False, default=datetime.now(DEFAULT_TIMEZONE))]]
    updated_at: Mapped[Annotated[datetime, mapped_column(DateTime, nullable=False, default=datetime.now(DEFAULT_TIMEZONE), onupdate=datetime.now(DEFAULT_TIMEZONE))]]

    program_type = relationship("ProgramType", back_populates="programs")
    club = relationship("Club", back_populates="programs")

class Event(Base):
    __tablename__ = "events"

    id: Mapped[Annotated[uuid.UUID, mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)]]
    start_time: Mapped[Annotated[datetime, mapped_column(DateTime, nullable=False)]]
    end_time: Mapped[Annotated[datetime, mapped_column(DateTime, nullable=False)]]
    price: Mapped[Annotated[DECIMAL, mapped_column(DECIMAL(10, 2), nullable=False)]]
    currency: Mapped[Annotated[str, mapped_column(String(3), nullable=False)]] # ISO 4217  
    program_id: Mapped[Annotated[uuid.UUID, mapped_column(UUID(as_uuid=True), ForeignKey("programs.id"), nullable=False)]]
    created_at: Mapped[Annotated[datetime, mapped_column(DateTime, nullable=False, default=datetime.now(DEFAULT_TIMEZONE))]]
    updated_at: Mapped[Annotated[datetime, mapped_column(DateTime, nullable=False, default=datetime.now(DEFAULT_TIMEZONE), onupdate=datetime.now(DEFAULT_TIMEZONE))]]

    club = relationship("Club", back_populates="events")
    program = relationship("Program", back_populates="events")

class Course(Base):
    __tablename__ = "courses"

    id: Mapped[Annotated[uuid.UUID, mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)]]
    program_id: Mapped[Annotated[uuid.UUID, mapped_column(UUID(as_uuid=True), ForeignKey("programs.id"), nullable=False)]]
    price: Mapped[Annotated[DECIMAL, mapped_column(DECIMAL(10, 2), nullable=False)]]
    currency: Mapped[Annotated[str, mapped_column(String(3), nullable=False)]] # ISO 4217    
    subscription_required: Mapped[Annotated[bool, mapped_column(Boolean, nullable=False)]]
    created_at: Mapped[Annotated[datetime, mapped_column(DateTime, nullable=False, default=datetime.now(DEFAULT_TIMEZONE))]]
    updated_at: Mapped[Annotated[datetime, mapped_column(DateTime, nullable=False, default=datetime.now(DEFAULT_TIMEZONE), onupdate=datetime.now(DEFAULT_TIMEZONE))]]

    club = relationship("Club", back_populates="courses")
    program = relationship("Program", back_populates="courses")
    sessions = relationship("Session", back_populates="course", uselist=True)

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
    address_id: Mapped[Annotated[uuid.UUID, mapped_column(UUID(as_uuid=True), ForeignKey("addresses.id"), nullable=True)]]

    course = relationship("Course", back_populates="sessions")

class BookingStatus(enum.Enum):
    PENDING = "Pending"
    CONFIRMED = "Confirmed"
    CANCELLED = "Cancelled"
    COMPLETED = "Completed"

class Booking(Base):
    __tablename__ = "bookings"

    id: Mapped[Annotated[uuid.UUID, mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)]]
    user_id: Mapped[Annotated[uuid.UUID, mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)]]
    program_id: Mapped[Annotated[uuid.UUID, mapped_column(UUID(as_uuid=True), ForeignKey("programs.id"), nullable=False)]]
    booking_type_id: Mapped[Annotated[int, mapped_column(Integer, ForeignKey("booking_types.id"), nullable=False)]]
    status: Mapped[Annotated[BookingStatus, mapped_column(Enum(BookingStatus), nullable=False)]]
    transaction_id: Mapped[Annotated[uuid.UUID, mapped_column(UUID(as_uuid=True), ForeignKey("transactions.id"), nullable=True)]]
    created_at: Mapped[Annotated[datetime, mapped_column(DateTime, nullable=False, default=datetime.now(DEFAULT_TIMEZONE))]]
    updated_at: Mapped[Annotated[datetime, mapped_column(DateTime, nullable=False, default=datetime.now(DEFAULT_TIMEZONE), onupdate=datetime.now(DEFAULT_TIMEZONE))]]

    user = relationship("User", back_populates="bookings")
    program = relationship("Program", back_populates="bookings")
    booking_types = relationship("BookingType", back_populates="bookings")

class BookingType(Base):
    __tablename__ = "booking_types"

    id: Mapped[Annotated[int, mapped_column(Integer, primary_key=True, autoincrement=True)]]
    name: Mapped[Annotated[str, mapped_column(String(50), nullable=False, unique=True)]]

    bookings = relationship("Booking", back_populates="booking_types")

class TransactionStatus(enum.Enum):
    SUCCESS = "Success"
    FAILED = "Failed"
    PENDING = "Pending"

class PaymentMethod(enum.Enum):
    STRIPE = "Stripe"

class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[Annotated[uuid.UUID, mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)]]
    user_id: Mapped[Annotated[uuid.UUID, mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)]]
    amount: Mapped[Annotated[DECIMAL, mapped_column(DECIMAL(10, 2), nullable=False)]]
    currency: Mapped[Annotated[str, mapped_column(String(3), nullable=False)]]
    status: Mapped[Annotated[TransactionStatus, mapped_column(Enum(TransactionStatus), nullable=False)]]
    payment_method: Mapped[Annotated[PaymentMethod, mapped_column(Enum(PaymentMethod), nullable=False, default=PaymentMethod.STRIPE)]]
    created_at: Mapped[Annotated[datetime, mapped_column(DateTime, nullable=False, default=datetime.now(DEFAULT_TIMEZONE))]]
    updated_at: Mapped[Annotated[datetime, mapped_column(DateTime, nullable=False, default=datetime.now(DEFAULT_TIMEZONE), onupdate=datetime.now(DEFAULT_TIMEZONE))]]

    program_id: Mapped[Annotated[uuid.UUID, mapped_column(UUID(as_uuid=True), ForeignKey("programs.id"), nullable=True)]]
    membership_id: Mapped[Annotated[uuid.UUID, mapped_column(UUID(as_uuid=True), ForeignKey("memberships.id"), nullable=True)]]

    user = relationship("User", back_populates="transactions")
    program = relationship("Program", back_populates="transactions")
    membership = relationship("Membership", back_populates="transactions")


###########################################################################
################################### User ##################################
###########################################################################

class ClubRole(Base):
    __tablename__ = "club_roles"

    id: Mapped[Annotated[int, mapped_column(Integer, primary_key=True, autoincrement=True)]]
    name: Mapped[Annotated[str, mapped_column(String(100), nullable=False)]]
    description: Mapped[Annotated[str, mapped_column(String(255), nullable=False)]]

    users = relationship("UserClubRole", back_populates="club_roles")
    

class UserClubRole(Base):
    __tablename__ = "user_club_roles"

    user_id: Mapped[Annotated[uuid.UUID, mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True)]]
    club_id: Mapped[Annotated[uuid.UUID, mapped_column(UUID(as_uuid=True), ForeignKey("clubs.id"), primary_key=True)]]
    club_role_id: Mapped[Annotated[int, mapped_column(Integer, ForeignKey("club_roles.id"), primary_key=True)]]
    assigned_at: Mapped[Annotated[datetime, mapped_column(DateTime, nullable=False, default=datetime.now(DEFAULT_TIMEZONE))]]
    
    __table_args__ = (UniqueConstraint("user_id", "club_id", "club_role_id", name="unique_user_club_role"),)

