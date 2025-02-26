from typing import List, Tuple, Optional
import os
import stripe
import random

from config.settings import ENVIRONMENT

if ENVIRONMENT == "dev":
    stripe.api_key = "sk_test_..."
    stripe.api_base = f"http://{os.environ.get('STRIPE_MOCK_HOST', 'localhost')}:12111"


#! Stripe API will be used in the future now we will use a stripe mock
def create_single_payment(
    total_amount: int, currency: str, stripe_club_account_id: Optional[str] = None, transfer_group: Optional[str] = None
) -> stripe.PaymentIntent:
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
            payment_method_types=["card"],  # TODO: Change
            transfer_group=transfer_group,
        )
    elif stripe_club_account_id:
        payment_intent = stripe.PaymentIntent.create(
            amount=total_amount,  # in cents
            currency=currency,
            payment_method_types=["card"],  # TODO: Change
            transfer_data={"destination": stripe_club_account_id},
        )
    else:
        raise ValueError("Must specify either transfer_group or stripe_club_account_id")
    return payment_intent


def create_split_payment_transfer(
    transfer_group: str, total_amount: int, currency: str, stripe_club_account_id: str
) -> stripe.Transfer:
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


# TODO Dummy function - Implement properly
def get_transaction_status(payment_intent_id: str) -> str:
    """Get the status of a transaction

    :param payment_intent_id: The ID of the transaction
    :return: The status of the transaction
    """
    # payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)
    # return payment_intent.status
    types = [
        "succeeded",
        "processing",
        "requires_payment_method",
        "requires_confirmation",
        "requires_action",
        "canceled",
    ]
    weights = [0.7, 0.1, 0.05, 0.05, 0.05, 0.05]
    return random.choices(types, weights=weights)[0]


# TODO Dummy function - Implement properly
def get_payment_fee(payment_intent_id: str) -> int:
    """Get the fee of a payment

    :param payment_intent_id: The ID of the transaction
    :return: The fee of the payment
    """
    payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)
    charge = None

    if payment_intent.latest_charge:
        if isinstance(payment_intent.latest_charge, str):
            charge_id = payment_intent.latest_charge
        else:
            charge_id = payment_intent.latest_charge.id
        charge = stripe.Charge.retrieve(charge_id)

    if charge and charge.balance_transaction:

        if isinstance(charge.balance_transaction, str):
            balance_transaction_id = charge.balance_transaction
        else:
            balance_transaction_id = charge.balance_transaction.id

        balance_tx = stripe.BalanceTransaction.retrieve(balance_transaction_id)
        return balance_tx.fee

    # raise ValueError("No charge found for payment intent")
    return round(payment_intent.amount * 0.027)


def create_refund(payment_intent_id: str, amount: int) -> stripe.Refund:
    """Create a refund

    :param payment_intent_id: The ID of the transaction
    :param amount: The amount to refund in cents
    :return: The refund
    """
    refund = stripe.Refund.create(
        payment_intent=payment_intent_id,
        amount=amount,
    )
    return refund


def create_reversal(transfer_id: str, amount: int) -> stripe.Reversal:
    """Create a reversal

    :param transfer_id: The ID of the transfer
    :return: The reversal
    """
    reversal = stripe.Transfer.create_reversal(transfer_id, amount=amount)
    return reversal
