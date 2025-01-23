from typing import Annotated
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import (
    String,
    ForeignKey,
    UUID,
    Boolean,
    DateTime,
    Enum,
    DECIMAL,
)
import uuid
from datetime import datetime
import enum
from typing import List

from config.database import Base
from config.settings import DEFAULT_TIMEZONE

from models.m_generic import *
from models.m_club import *
from models.m_audit import *
from models.m_payment import *

###########################################################################
################################## Enums ##################################
###########################################################################
class TransactionStatus(enum.Enum):
    SUCCESS = "Success"
    FAILED = "Failed"
    PENDING = "Pending"


class PaymentMethod(enum.Enum):
    STRIPE = "Stripe"


class RefundType(enum.Enum):
    FULL = "Full Refund"
    PARTIAL = "Partial Refund"
    CANCELLED_BY_CLUB = "Cancelled by Club"


###########################################################################
############################# Database Models #############################
###########################################################################
class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[Annotated[uuid.UUID, mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)]]
    external_charge_id = Mapped[Annotated[str, mapped_column(String(255), nullable=False)]]  # e.g. Stripe charge ID
    user_id: Mapped[Annotated[uuid.UUID, mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)]]

    amount: Mapped[Annotated[DECIMAL, mapped_column(DECIMAL(10, 2), nullable=False)]]
    amount_refunded: Mapped[
        Annotated[DECIMAL, mapped_column(DECIMAL(10, 2), nullable=False, default=0)]
    ]  # Max amount that can be refunded: amount - amount * service_fee = amount_refunded
    currency: Mapped[Annotated[str, mapped_column(String(3), nullable=False)]]
    is_split_payment: Mapped[Annotated[bool, mapped_column(Boolean, nullable=False, default=False)]]
    status: Mapped[Annotated[TransactionStatus, mapped_column(Enum(TransactionStatus), nullable=False)]]
    payment_method: Mapped[
        Annotated[PaymentMethod, mapped_column(Enum(PaymentMethod), nullable=False, default=PaymentMethod.STRIPE)]
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

    program_id: Mapped[
        Annotated[uuid.UUID, mapped_column(UUID(as_uuid=True), ForeignKey("programs.id"), nullable=True)]
    ]
    membership_id: Mapped[
        Annotated[uuid.UUID, mapped_column(UUID(as_uuid=True), ForeignKey("memberships.id"), nullable=True)]
    ]

    user: Mapped["User"] = relationship("User", back_populates="transactions")
    programs: Mapped["Program"] = relationship("Program", uselist=True)
    memberships: Mapped["Membership"] = relationship("Membership", uselist=True)
    split_details: Mapped[List["SplitTransaction"]] = relationship("SplitTransaction", back_populates="transaction")


class SplitTransaction(Base):
    __tablename__ = "split_transactions"

    id: Mapped[Annotated[uuid.UUID, mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)]]
    transaction_id: Mapped[Annotated[uuid.UUID, mapped_column(UUID(as_uuid=True), ForeignKey("transactions.id"))]]
    external_transfer_id: Mapped[Annotated[str, mapped_column(String(255), nullable=False)]]  # e.g. Stripe transfer ID
    club_id: Mapped[Annotated[uuid.UUID, mapped_column(UUID(as_uuid=True), ForeignKey("clubs.id"))]]

    amount: Mapped[Annotated[DECIMAL, mapped_column(DECIMAL(10, 2), nullable=False)]]
    amount_refunded: Mapped[Annotated[DECIMAL, mapped_column(DECIMAL(10, 2), nullable=False, default=0)]]
    status: Mapped[Annotated[TransactionStatus, mapped_column(Enum(TransactionStatus), nullable=False)]]

    transaction: Mapped["Transaction"] = relationship("Transaction", back_populates="split_details")
    club: Mapped["Club"] = relationship("Club")

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


class Refund(Base):
    __tablename__ = "refunds"

    id: Mapped[Annotated[uuid.UUID, mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)]]
    transaction_id: Mapped[Annotated[uuid.UUID, mapped_column(UUID(as_uuid=True), ForeignKey("transactions.id"))]]
    user_id: Mapped[Annotated[uuid.UUID, mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))]]
    club_id: Mapped[Annotated[uuid.UUID, mapped_column(UUID(as_uuid=True), ForeignKey("clubs.id"), nullable=True)]]

    refund_type: Mapped[Annotated[RefundType, mapped_column(Enum(RefundType), nullable=False)]]
    amount: Mapped[Annotated[DECIMAL, mapped_column(DECIMAL(10, 2), nullable=False)]]
    status: Mapped[Annotated[TransactionStatus, mapped_column(Enum(TransactionStatus), nullable=False)]]
    reason: Mapped[Annotated[str, mapped_column(String(500), nullable=True)]]
    external_refund_id: Mapped[Annotated[str, mapped_column(String(255), nullable=True)]]

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

    transaction: Mapped["Transaction"] = relationship("Transaction")
    user: Mapped["User"] = relationship("User")
    club: Mapped["Club"] = relationship("Club")
