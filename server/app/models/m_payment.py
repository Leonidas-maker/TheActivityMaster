from typing import List, Tuple, Optional, Dict
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey, UUID, Boolean, DateTime, Enum, Integer, UniqueConstraint, CheckConstraint
from sqlalchemy.inspection import inspect
import uuid
import enum
import datetime
import warnings


from config.database import Base
from config.settings import DEFAULT_TIMEZONE


from models.m_club import PriceType

###########################################################################
################################## Enums ##################################
###########################################################################

class BookingStatus(enum.Enum):
    PENDING = "Pending"
    CONFIRMED = "Confirmed"
    CANCELLED = "Cancelled"
    COMPLETED = "Completed"
    CANCELLED_BY_CLUB = "Cancelled by Club"


class BookingType(enum.Enum):
    PAID = "Paid"  # Requires payment
    FREE = "Free"  # Does not require payment

    MEMBERSHIP = "Membership"  # Means additional fee for members
    MEMBERSHIP_ACCESS = "Membership Access"  # Means no additional fee for members


#! On change also update the check constraint in the booking table
FREE_BOOKING_TYPES = {BookingType.FREE, BookingType.MEMBERSHIP_ACCESS}


class TransactionStatus(enum.Enum):
    SUCCESS = "Success"
    FAILED = "Failed"
    PENDING = "Pending"


class PaymentMethod(enum.Enum):
    STRIPE = "Stripe"


class RefundType(enum.Enum):
    USER_REQUESTED = "User Requested"
    CANCELLED_BY_CLUB = "Cancelled by Club"


###########################################################################
############################# Database Models #############################
###########################################################################
from models.m_generic import *
from models.m_audit import *
from models.m_payment import *
from models.m_club import *
class Booking(Base):
    __tablename__ = "bookings"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    session_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("sessions.id"), nullable=False)
    booking_type: Mapped[BookingType] = mapped_column(Enum(BookingType), nullable=False)
    price_snapshot: Mapped[int] = mapped_column(Integer, nullable=False)
    pricing_model_snapshot: Mapped[PriceType] = mapped_column(Enum(PriceType), nullable=False)
    
    status: Mapped[BookingStatus] = mapped_column(Enum(BookingStatus), nullable=False)
    transaction_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("transactions.id"), nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.datetime.now(DEFAULT_TIMEZONE)
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.datetime.now(DEFAULT_TIMEZONE),
        onupdate=lambda: datetime.datetime.now(DEFAULT_TIMEZONE),
    )

    user: Mapped["User"] = relationship("User", back_populates="bookings")  # type: ignore
    session: Mapped["Session"] = relationship("Session", back_populates="bookings") # type: ignore
    transaction: Mapped["Transaction"] = relationship("Transaction", back_populates="bookings")

    @property
    def program(self) -> Optional["Program"]: # type: ignore
        state = inspect(self)
        if "session" in state.unloaded:
            warnings.warn("session not loaded returning None")
            return None
        else:
            return self.session.program

    @property
    def club_id(self) -> Optional[uuid.UUID]:
        state = inspect(self)
        if "session" in state.unloaded:
            warnings.warn("session not loaded returning None")
            return None
        else:
            state = inspect(self.session)
            if "program" in state.unloaded:
                warnings.warn("program not loaded returning None")
                return None
            else:
                return self.session.program.club_id
            
    @property
    def program_id(self) -> Optional[uuid.UUID]:
        state = inspect(self)
        if "session" in state.unloaded:
            warnings.warn("session not loaded returning None")
            return None
        else:
            return self.session.program_id
            
    @property
    def price(self) -> int:
        return self.price_snapshot
    
    @property
    def pricing_model(self) -> PriceType:
        return self.pricing_model_snapshot

    __table_args__ = (
        CheckConstraint(
            "booking_type NOT IN ('Free', 'Membership Access') OR transaction_id IS NULL", name="chk_free_booking"
        ),
        CheckConstraint(
            "booking_type NOT IN ('Paid', 'Membership') OR transaction_id IS NOT NULL", name="chk_paid_booking"
        ),
        UniqueConstraint("user_id", "session_id", name="unique_booking"),
    )


class MembershipTransaction(Base):
    __tablename__ = "membership_transactions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    membership_subscription_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("membership_subscriptions.id"), nullable=False
    )
    transaction_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("transactions.id"), nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.datetime.now(DEFAULT_TIMEZONE)
    )


class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    external_charge_id: Mapped[str] = mapped_column(String(255), nullable=False)  # e.g. Stripe charge ID
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    amount: Mapped[int] = mapped_column(Integer, nullable=False)
    amount_refunded: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    currency: Mapped[str] = mapped_column(String(3), nullable=False)
    is_split_payment: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    status: Mapped[TransactionStatus] = mapped_column(
        Enum(TransactionStatus), nullable=False, default=TransactionStatus.PENDING
    )
    payment_method: Mapped[PaymentMethod] = mapped_column(
        Enum(PaymentMethod), nullable=False, default=PaymentMethod.STRIPE
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

    user: Mapped["User"] = relationship("User", back_populates="transactions")  # type: ignore
    bookings: Mapped[List["Booking"]] = relationship("Booking", back_populates="transaction")
    membership_subscription: Mapped[List["MembershipSubscription"]] = relationship( # type: ignore
        "MembershipSubscription", secondary="membership_transactions", back_populates="transactions"
    )

    split_details: Mapped[List["SplitTransaction"]] = relationship("SplitTransaction", back_populates="transaction", lazy="joined")


class SplitTransaction(Base):
    __tablename__ = "split_transactions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    transaction_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("transactions.id"))
    external_transfer_id: Mapped[str] = mapped_column(String(255), nullable=True)  # z.B. Stripe transfer ID
    club_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("clubs.id"))

    amount: Mapped[int] = mapped_column(Integer, nullable=False)
    amount_refunded: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    status: Mapped[TransactionStatus] = mapped_column(
        Enum(TransactionStatus), nullable=False, default=TransactionStatus.PENDING
    )

    transaction: Mapped["Transaction"] = relationship("Transaction", back_populates="split_details")
    club: Mapped["Club"] = relationship("Club")  # type: ignore

    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.datetime.now(DEFAULT_TIMEZONE)
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.datetime.now(DEFAULT_TIMEZONE),
        onupdate=lambda: datetime.datetime.now(DEFAULT_TIMEZONE),
    )

    __table_args__ = (
        UniqueConstraint("transaction_id", "club_id"),
        CheckConstraint("amount >= 0"),
        CheckConstraint("amount_refunded >= 0"),
        CheckConstraint("status = 'Success' AND external_transfer_id IS NOT NULL"),
    )


class Refund(Base):
    __tablename__ = "refunds"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    transaction_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("transactions.id"))
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    club_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("clubs.id"), nullable=True)

    refund_type: Mapped[RefundType] = mapped_column(Enum(RefundType), nullable=False)
    amount: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[TransactionStatus] = mapped_column(Enum(TransactionStatus), nullable=False)
    reason: Mapped[str] = mapped_column(String(500), nullable=True)
    external_refund_id: Mapped[str] = mapped_column(String(255), nullable=True)

    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.datetime.now(DEFAULT_TIMEZONE)
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.datetime.now(DEFAULT_TIMEZONE),
        onupdate=lambda: datetime.datetime.now(DEFAULT_TIMEZONE),
    )

    transaction: Mapped["Transaction"] = relationship("Transaction")
    user: Mapped["User"] = relationship("User")  # type: ignore
    club: Mapped["Club"] = relationship("Club")  # type: ignore
