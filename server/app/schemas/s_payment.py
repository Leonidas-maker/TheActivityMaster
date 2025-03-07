from pydantic import BaseModel, Field, EmailStr, ConfigDict, model_validator
from typing import List, Optional, Dict, Tuple
import uuid
import datetime

from . import s_club

from models.m_club import PriceType
from models.m_payment import BookingStatus, BookingType, PaymentMethod, TransactionStatus, MembershipSubscriptionStatus

from config.settings import DEFAULT_TIMEZONE


###########################################################################
################################# Booking #################################
###########################################################################
class TransactionData(BaseModel):
    """
    Model representing transaction data details.

    Fields:
      - stripe_account_id: The Stripe account identifier.
      - total_amount: The total amount for the transaction.
      - currency: The currency code (e.g., USD).
    
    Note:
      Supports dictionary-like access for getting and setting attributes.
      Raises an AttributeError if an invalid attribute key is used.
    """
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
    """
    Base model for a booking request.

    Fields:
      - session_id: The UUID of the session for which the booking is made.
      - booking_type: The type of booking (e.g., paid, membership, membership access).
    """
    model_config = ConfigDict(from_attributes=True)
    session_id: uuid.UUID = Field(..., description="The ID of the session for which the booking was made.")
    booking_type: BookingType = Field(..., description="The type of the booking.")


class Booking(BookingBase):
    """
    Model representing a booking.

    Fields:
      - id: The unique identifier of the booking.
      - club_id: The UUID of the club for which the booking is made.
      - program_id: The UUID of the program for which the booking is made.
      - user_id: The UUID of the user who made the booking.
      - status: The status of the booking.
      - transaction_id: (Optional) The UUID of the transaction (must be provided for paid bookings).
      - price: The price charged for the booking.
      - pricing_model: The pricing model applied for the booking.
    
    Validation rules:
      - For membership access bookings, a transaction_id must NOT be provided.
      - For paid bookings (BookingType.PAID or BookingType.MEMBERSHIP), a transaction_id is required.
    """
    id: uuid.UUID = Field(..., description="The unique identifier of the booking.")
    club_id: uuid.UUID = Field(..., description="The ID of the club for which the booking was made.")
    program_id: uuid.UUID = Field(..., description="The ID of the program for which the booking was made.")
    user_id: uuid.UUID = Field(..., description="The ID of the user who made the booking.")
    status: BookingStatus = Field(..., description="The status of the booking.")
    transaction_id: Optional[uuid.UUID] = Field(None, description="The ID of the transaction for the booking.")
    price: int = Field(..., description="The price of the booking.")
    pricing_model: PriceType = Field(..., description="The pricing model of the booking.")

    @model_validator(mode="after")
    def check_booking_type(self) -> "Booking":
        """
        Validate booking type rules:
          - If booking_type is MEMBERSHIP_ACCESS, no transaction_id should be provided.
          - If booking_type is PAID or MEMBERSHIP, a transaction_id must be provided.
        """
        if self.booking_type == BookingType.MEMBERSHIP_ACCESS and self.transaction_id:
            raise ValueError("Transaction ID should not be provided for membership access bookings.")
        if self.booking_type in [BookingType.PAID, BookingType.MEMBERSHIP] and not self.transaction_id:
            raise ValueError("Transaction ID must be provided for paid bookings.")
        return self


class BookingDetails(Booking):
    """
    Extended booking model including detailed program and session information.

    Fields:
      - program: The program details (from s_club).
      - session: The session details (from s_club).
    """
    program: s_club.Program
    session: s_club.Session


class UserClubBooking(BaseModel):
    """
    Model representing a user who made a booking for a club.

    Fields:
      - id: The UUID of the user.
      - first_name: The first name of the user (max 50 characters).
      - last_name: The last name of the user (max 50 characters).
    """
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID = Field(..., description="The ID of the user who made the booking.")
    first_name: str = Field(..., max_length=50, description="The first name of the user who made the booking.")
    last_name: str = Field(..., max_length=50, description="The last name of the user who made the booking.")


class ClubBooking(BookingBase):
    """
    Model representing a booking made at a club level.

    Fields:
      - program_id: The UUID of the program associated with the booking.
      - price: The price charged for the booking.
      - user: The user details who made the booking.
    """
    program_id: uuid.UUID = Field(..., description="The ID of the program for which the booking was made.")
    price: int = Field(..., description="The price of the booking.")
    user: UserClubBooking = Field(..., description="The user who made the booking.")


class BookingCreateRequest(BaseModel):
    """
    Request model for creating bookings.

    Fields:
      - club_id: The UUID of the club for which the booking is made.
      - program_ids: A list of program UUIDs (max 5 allowed) for which bookings are being made.
      - session_ids: A list of session UUIDs (max 10 allowed) for which bookings are being made.
    """
    club_id: uuid.UUID = Field(..., description="The ID of the club for which the booking was made.")
    program_ids: List[uuid.UUID] = Field(
        ..., max_length=5, description="The IDs of the programs for which the booking was made."
    )
    session_ids: List[uuid.UUID] = Field(
        ..., max_length=10, description="The IDs of the sessions for which the booking was made."
    )


class BookingsCreateResponse(BaseModel):
    """
    Response model for a bookings creation request.

    Fields:
      - bookings: A list of booking objects that were created.
      - client_secret: (Optional) The client secret from the payment intent (None if no payment is required).
    """
    bookings: List[Booking] = Field(..., description="The list of bookings created.")
    client_secret: Optional[str] = Field(None, description="The client secret of the payment intent; None if no payment is required.")


###########################################################################
############################### Transactions ##############################
###########################################################################
class SplitTransaction(BaseModel):
    """
    Model representing a split transaction detail.

    Fields:
      - id: The unique identifier of the split transaction.
      - transaction_id: The UUID of the related transaction.
      - club_id: The UUID of the club.
      - amount: The amount for this split transaction.
      - amount_refunded: The amount refunded for this split transaction.
    """
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID = Field(..., description="The ID of the split transaction.")
    transaction_id: uuid.UUID = Field(..., description="The ID of the transaction.")
    club_id: uuid.UUID = Field(..., description="The ID of the club.")
    amount: int = Field(..., description="The amount of the split transaction.")
    amount_refunded: int = Field(..., description="The amount refunded for the split transaction.")


class Transaction(BaseModel):
    """
    Model representing a payment transaction.

    Fields:
      - id: The unique identifier of the transaction.
      - user_id: The UUID of the user who made the transaction.
      - amount: The total amount charged.
      - amount_refunded: The total amount refunded.
      - currency: The currency code of the transaction.
      - status: The current status of the transaction.
      - payment_method: The payment method used.
      - created_at: Timestamp when the transaction was created.
      - updated_at: Timestamp when the transaction was last updated.
      - split_details: A list of associated split transactions.
    """
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID = Field(..., description="The ID of the transaction.")
    user_id: uuid.UUID = Field(..., description="The ID of the user who made the transaction.")
    amount: int = Field(..., description="The total amount of the transaction.")
    amount_refunded: int = Field(..., description="The total amount refunded for the transaction.")
    currency: str = Field(..., description="The currency of the transaction.")
    status: TransactionStatus = Field(..., description="The status of the transaction.")
    payment_method: PaymentMethod = Field(..., description="The payment method used for the transaction.")
    created_at: datetime.datetime = Field(..., description="The creation timestamp of the transaction.")
    updated_at: datetime.datetime = Field(..., description="The last update timestamp of the transaction.")
    split_details: List[SplitTransaction] = Field([], description="List of split transactions associated with this transaction.")


class MemberShipsubscription(BaseModel):
    """
    Model representing a membership subscription.

    Fields:
      - id: The unique identifier of the membership subscription.
      - membership_id: The UUID of the membership.
      - user_id: The UUID of the user who subscribed.
      - stripe_subscription_id: The Stripe subscription identifier.
      - start_datetime: The start datetime of the subscription.
      - status: The current status of the subscription.
      - modiefied_at: The timestamp when the subscription was last modified.
    """
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID = Field(..., description="The ID of the membership subscription.")
    membership_id: uuid.UUID = Field(..., description="The ID of the membership.")
    user_id: uuid.UUID = Field(..., description="The ID of the user who subscribed to the membership.")
    stripe_subscription_id: str = Field(..., description="The Stripe subscription ID.")
    start_datetime: datetime.datetime = Field(..., description="The start datetime of the subscription.")
    status: MembershipSubscriptionStatus = Field(..., description="The current status of the membership subscription.")
    modiefied_at: datetime.datetime = Field(..., description="The last modification timestamp of the subscription.")


class MemberShipsubscriptionResponse(BaseModel):
    """
    Response model for membership subscription details.

    Fields:
      - subscriptionId: The subscription identifier (e.g., "sub_XXXXXXX").
      - subscriptionStatus: The current status of the subscription (e.g., "active").
      - paymentIntentClientSecret: The client secret from the payment intent.
    """
    subscriptionId: str = Field(..., description="The ID of the subscription.", examples=["sub_XXXXXXX"])
    subscriptionStatus: str = Field(..., description="The status of the subscription.", examples=["active"])
    paymentIntentClientSecret: str = Field(..., description="The client secret of the payment intent.", examples=["pi_XXXX_secret_XXXX"])
