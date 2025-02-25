from typing import List, Tuple, Optional
import os
import stripe

from config.settings import ENVIRONMENT

if ENVIRONMENT == "dev":
    stripe.api_key = "sk_test_..."
    stripe.api_base = f"http://{os.environ.get('STRIPE_MOCK_HOST', 'localhost')}:12111"


#! Stripe API will be used in the future now we will use a stripe mock
def create_single_payment(total_amount: int, currency: str, stripe_club_account_id: Optional[str] = None, transfer_group: Optional[str] = None) -> stripe.PaymentIntent:
    """Create a single payment intent

    :param stripe_club_account_id: The stripe account id of the club
    :param total_amount: The total amount of the payment in cents
    :param currency: The currency of the payment
    :return: The payment intent
    """
    if transfer_group and stripe_club_account_id:
        raise ValueError("Cannot specify both transfer_group and stripe_club_account_id")

    if transfer_group:
        payment_intent = stripe.PaymentIntent.create(
            amount=total_amount,  # in cents
            currency=currency,
            payment_method_types=["card"], #TODO: Change
            transfer_group=transfer_group,
        )
    elif stripe_club_account_id:
        payment_intent = stripe.PaymentIntent.create(
            amount=total_amount,  # in cents
            currency=currency,
            payment_method_types=["card"], #TODO: Change
            transfer_data={"destination": stripe_club_account_id},
        )
    else:
        raise ValueError("Must specify either transfer_group or stripe_club_account_id")
    return payment_intent


def create_split_payment_transfer(transfer_group:str, total_amount: int, currency: str, stripe_club_account_id: str) -> stripe.Transfer:
    """Create a split payment transfer

    :param transfer_group: The transfer group
    :param total_amount: The total amount of the transfer in cents
    :param currency: The currency of the transfer
    :param stripe_club_account_id: The stripe account id of the club
    :return The transfer
    """
    if total_amount <= 0:
        raise ValueError("Total amount must be greater than 0")
    
    transfer = stripe.Transfer.create(
        amount=total_amount,
        currency=currency,
        destination=stripe_club_account_id,
        transfer_group=transfer_group,
    )
    return transfer

def get_transaction_status(transaction_id: str) -> str:
    """Get the status of a transaction

    :param transaction_id: The ID of the transaction
    :return: The status of the transaction
    """
    payment_intent = stripe.PaymentIntent.retrieve(transaction_id)
    return payment_intent.status