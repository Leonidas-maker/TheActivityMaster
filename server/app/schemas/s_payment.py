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
    program: s_club.Program
    session: s_club.Session


class UserClubBooking(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID = Field(..., description="The ID of the user who made the booking.")
    first_name: str = Field(..., max_length=50, description="The first name of the user who made the booking.")
    last_name: str = Field(..., max_length=50, description="The last name of the user who made the booking.")


class ClubBooking(BookingBase):
    program_id: uuid.UUID = Field(..., description="The ID of the program for which the booking was made.")
    price: int = Field(..., description="The price of the booking.")
    user: UserClubBooking = Field(..., description="The user who made the booking.")


class BookingCreateRequest(BaseModel):
    club_id: uuid.UUID = Field(..., description="The ID of the club for which the booking was made.")
    program_ids: List[uuid.UUID] = Field(
        ..., max_length=5, description="The IDs of the programs for which the booking was made."
    )
    session_ids: List[uuid.UUID] = Field(
        ..., max_length=10, description="The IDs of the sessions for which the booking was made."
    )

class BookingsCreateResponse(BaseModel):
    bookings: List[Booking] = Field(..., description="The IDs of the bookings.")
    client_secret: Optional[str] = Field(None, description="The client secret of the payment intent. None if no payment is required.")

###########################################################################
############################### Transactions ##############################
###########################################################################
class SplitTransaction(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID = Field(..., description="The ID of the split transaction.")
    transaction_id: uuid.UUID = Field(..., description="The ID of the transaction.")

    club_id: uuid.UUID = Field(..., description="The ID of the club.")
    amount: int = Field(..., description="The amount of the split transaction.")
    amount_refunded: int = Field(..., description="The amount refunded for the split transaction.")


class Transaction(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID = Field(..., description="The ID of the transaction.")
    user_id: uuid.UUID = Field(..., description="The ID of the user who made the transaction.")

    amount: int = Field(..., description="The total amount of the transaction.")
    amount_refunded: int = Field(..., description="The total amount refunded for the transaction.")
    currency: str = Field(..., description="The currency of the transaction.")
    status: TransactionStatus = Field(..., description="The status of the transaction.")
    payment_method: PaymentMethod = Field(..., description="The payment method of the transaction.")
    created_at: datetime.datetime = Field(..., description="The creation date of the transaction.")
    updated_at: datetime.datetime = Field(..., description="The last update date of the transaction.")

    split_details: List[SplitTransaction] = Field([], description="The split details of the transaction.")


class MemberShipsubscription(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID = Field(..., description="The ID of the membership.")
    membership_id: uuid.UUID = Field(..., description="The ID of the membership.")
    user_id: uuid.UUID = Field(..., description="The ID of the user who made the transaction.")

    stripe_subscription_id: str = Field(..., description="The ID of the stripe subscription.")
    start_datetime: datetime.datetime = Field(..., description="The start date of the subscription.")

    status: MembershipSubscriptionStatus = Field(..., description="The status of the subscription.")
    modiefied_at: datetime.datetime = Field(..., description="The last update date of the subscription.")

class MemberShipsubscriptionResponse(BaseModel):
    subscriptionId: str = Field(..., description="The ID of the subscription.", examples=["sub_XXXXXXX"])
    subscriptionStatus: str = Field(..., description="The status of the subscription.", examples=["active"])
    paymentIntentClientSecret: str = Field(..., description="The client secret of the payment intent.", examples=["pi_XXXX_secret_XXXX"])