from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, or_, exists, and_, ColumnElement
from sqlalchemy.orm import undefer, joinedload
from typing import List, Tuple, Optional, Dict
import stripe
import uuid
from rich.console import Console
import traceback

from schemas import s_payment

from models import m_club, m_payment

from crud import audit as audit_crud, club as club_crud

from core import transactions as core_transactions


###########################################################################
##################### Transaction for Program Booking #####################
###########################################################################
async def create_transaction(
    db: AsyncSession, user_id: uuid.UUID, transaction_data: Dict[uuid.UUID, s_payment.TransactionData]
) -> Tuple[m_payment.Transaction, stripe.PaymentIntent]:
    """Create a transaction

    :param db: The database session
    :param user_id: The ID of the user
    :param transaction_data: The transaction data
    :return: The transaction and the payment intent
    """

    if not transaction_data or len(transaction_data) == 0:
        raise ValueError("No transactions to process")

    # Calculate total amount and check if all transactions have the same currency
    total_amount = 0
    currency = None
    for club_id, transaction_details in transaction_data.items():
        total_amount += transaction_details.total_amount
        if currency is None:
            currency = transaction_details.currency
        elif currency != transaction_details.currency:
            raise ValueError("All transactions must have the same currency")

    if total_amount == 0:
        raise ValueError("Total amount of transaction is 0")

    # * Should not happen but just in case
    if currency is None:
        raise ValueError("No currency found for transaction data")

    if len(transaction_data) > 1:
        transaction_id = uuid.uuid4()

        payment_intent = core_transactions.create_single_payment(
            total_amount=total_amount,
            currency=currency,
            transfer_group=f"ORDER_{transaction_id}",
        )
        try:
            transaction = m_payment.Transaction(
                id=transaction_id,
                external_charge_id=payment_intent.id,
                user_id=user_id,
                currency=currency,
                amount=total_amount,
                payment_method=m_payment.PaymentMethod.STRIPE,
                is_split_payment=True,
                status=m_payment.TransactionStatus.PENDING,
            )
            db.add(transaction)
            await db.flush()

            split_transactions_db = []
            for club_id, split_transaction_data in transaction_data.items():
                split_transactions_db.append(
                    m_payment.SplitTransaction(
                        club_id=club_id,
                        stripe_club_account_id=split_transaction_data["stripe_account_id"],
                        amount=split_transaction_data["total_amount"],
                        currency=split_transaction_data["currency"],
                        transaction=transaction,
                        status=m_payment.TransactionStatus.PENDING,
                    )
                )
            db.add_all(split_transactions_db)
            await db.flush()
        except Exception as e:
            stripe.PaymentIntent.cancel(payment_intent.id)
            raise e
    else:
        club_id = list(transaction_data.keys())[0]
        payment_intent = core_transactions.create_single_payment(
            stripe_club_account_id=str(club_id),
            total_amount=total_amount,
            currency=currency,
        )
        try:
            transaction = m_payment.Transaction(
                user_id=user_id,
                currency=currency,
                amount=total_amount,
                payment_method=m_payment.PaymentMethod.STRIPE,
                external_charge_id=payment_intent.id,
                status=m_payment.TransactionStatus.PENDING,
            )
            db.add(transaction)
            await db.flush()
        except Exception as e:
            stripe.PaymentIntent.cancel(payment_intent.id)
            raise e
    return transaction, payment_intent


async def add_transfer_id_to_split_transactions(
    db: AsyncSession, transaction_id: uuid.UUID
) -> List[m_payment.SplitTransaction]:
    """Add transfer ID to split transactions

    :param db: The database session
    :param transaction_id: The ID of the transaction
    :return: The split transactions
    """

    split_transactions = await db.execute(
        select(m_payment.SplitTransaction)
        .join(m_payment.Transaction)
        .options(joinedload(m_payment.SplitTransaction.club))
        .filter(
            m_payment.Transaction.is_split_payment == True,
            m_payment.SplitTransaction.transaction_id == transaction_id,
        )
    )
    split_transactions_db = split_transactions.unique().scalars().all()
    transfer_group = f"ORDER_{transaction_id}"

    if any(split_transaction.external_transfer_id is not None for split_transaction in split_transactions_db):
        raise ValueError("Some split transactions already have an external transfer")

    for split_transaction in split_transactions_db:
        transfer = core_transactions.create_split_payment_transfer(
            transfer_group=transfer_group,
            total_amount=split_transaction.amount,
            currency=split_transaction.currency,
            stripe_club_account_id=split_transaction.stripe_club_account_id,
        )
        split_transaction.external_transfer_id = transfer.id
        split_transaction.status = m_payment.TransactionStatus.PENDING

    await db.flush()
    return list(split_transactions_db)


async def get_transaction_by_id(
    db: AsyncSession, transaction_id: uuid.UUID, with_details: bool = False
) -> m_payment.Transaction:
    """Get a transaction by ID

    :param db: The database session
    :param transaction_id: The ID of the transaction
    :return: The transaction
    """
    options = []
    if with_details:
        options.extend(
            [
                joinedload(m_payment.Transaction.bookings),
                joinedload(m_payment.Transaction.bookings)
                .joinedload(m_payment.Booking.session)
                .load_only(m_club.Session.program_id),
                joinedload(m_payment.Transaction.bookings)
                .joinedload(m_payment.Booking.session)
                .joinedload(m_club.Session.program)
                .load_only(m_club.Program.club_id),
            ]
        )

    transaction = await db.execute(select(m_payment.Transaction).filter(m_payment.Transaction.id == transaction_id))
    return transaction.unique().scalar()

###########################################################################
################################## Refund #################################
###########################################################################
async def create_refund(
    db: AsyncSession,
    bookings: List[m_payment.Booking],
    reason: str,
    is_user_refund: bool = True,
    check_pricing_model: bool = True,
) -> List[m_payment.Refund]:
    """Create a refund

    :param db: The database session
    :param bookings: List of bookings to refund
    :param reason: Reason for the refund
    :param is_user_refund: Indicates if this is a user-initiated refund, defaults to True
    :return: A tuple containing the refund object and the Stripe refund object
    """
    # Fetch transaction with all details
    transaction = await get_transaction_by_id(db, bookings[0].transaction_id, with_details=True)

    if transaction.status in [m_payment.TransactionStatus.FAILED, m_payment.TransactionStatus.FAILED]:
        raise ValueError("Transaction is not successful")

    refund_amount_per_club: Dict[str, int] = {}

    for booking in bookings:
        if transaction.id != booking.transaction_id:
            raise ValueError("Bookings do not belong to the same transaction")
        if booking.status != m_payment.BookingStatus.CONFIRMED:
            raise ValueError("Booking is not confirmed")
        if check_pricing_model and club_crud.is_price_model_package(db, session_id=booking.session_id):
            raise ValueError("Cannot refund bookings with package pricing model")

        refund_amount_per_club[str(booking.club_id)] = (
            refund_amount_per_club.get(str(booking.club_id), 0) + booking.price_snapshot
        )

    stripe_fee = core_transactions.get_payment_fee(transaction.external_charge_id)

    club_ids = [booking.club_id for booking in bookings]

    refunds_db: List[m_payment.Refund] = []
    if len(club_ids) > 1:
        sum_refund_amount = sum(refund_amount_per_club.values())
        if (
            sum_refund_amount > transaction.amount
            or transaction.amount_refunded + sum_refund_amount > transaction.amount
        ):
            raise ValueError("Refund amount exceeds transaction amount")

        fee_per_club: Dict[str, int] = {}
        amount_per_club: Dict[str, int] = {}
        split_transactions: Dict[str, m_payment.SplitTransaction] = {}
        for split_transaction in transaction.split_details:
            fee_per_club[str(split_transaction.club_id)] = int(
                (split_transaction.amount / transaction.amount) * stripe_fee
            )
            amount_per_club[str(split_transaction.club_id)] = split_transaction.amount
            split_transactions[str(split_transaction.club_id)] = split_transaction

        if is_user_refund:
            for club_id in club_ids:
                refund_amount_per_club[str(club_id)] -= round(
                    (refund_amount_per_club[str(club_id)] / amount_per_club[str(club_id)]) * fee_per_club[str(club_id)]
                )

        club_reversals = {}

        # TODO - Implement recurring task to check if the transfer reversal is successful and initiate refund
        for refund_club_id, refund_amount in refund_amount_per_club.items():
            split_transaction = split_transactions[refund_club_id]
            if split_transaction.amount_refunded + refund_amount > split_transaction.amount:
                raise ValueError("Refund amount exceeds split transaction amount")

            club_reversals[refund_club_id] = core_transactions.create_reversal(
                transfer_id=split_transaction.external_transfer_id,
                amount=refund_amount,
            )
            refund = m_payment.Refund(
                transaction_id=transaction.id,
                user_id=transaction.user_id,
                club_id=uuid.UUID(refund_club_id),
                refund_type=(
                    m_payment.RefundType.USER_REQUESTED if is_user_refund else m_payment.RefundType.CANCELLED_BY_CLUB
                ),
                amount=refund_amount,
                reason=reason,
                status=m_payment.TransactionStatus.PENDING,
            )
            refunds_db.append(refund)

            split_transaction.amount_refunded += refund_amount
            transaction.amount_refunded += refund_amount
    else:
        refund_amount = sum(refund_amount_per_club.values())
        if refund_amount > transaction.amount or transaction.amount_refunded + refund_amount > transaction.amount:
            raise ValueError("Refund amount exceeds transaction amount")

        if is_user_refund:
            refund_amount -= int((refund_amount / transaction.amount) * stripe_fee)
        refund = core_transactions.create_refund(transaction.external_charge_id, refund_amount)
        refunds_db.append(
            m_payment.Refund(
                transaction_id=transaction.id,
                user_id=transaction.user_id,
                club_id=club_ids[0],
                refund_type=(
                    m_payment.RefundType.USER_REQUESTED if is_user_refund else m_payment.RefundType.CANCELLED_BY_CLUB
                ),
                amount=refund_amount,
                reason=reason,
                status=m_payment.TransactionStatus.PENDING,
            )
        )
        transaction.amount_refunded += refund_amount

    db.add_all(refunds_db)
    await db.flush()
    return refunds_db


###########################################################################
############################## Recurring Task #############################
###########################################################################
async def check_pending_transactions(db: AsyncSession, console: Console) -> bool:
    """Check pending transactions

    :param db: The database session
    :param console: The console
    :return: True if successful, False otherwise
    """

    audit_logger = audit_crud.AuditLogger(db)
    audit_logger.sys_info("Checking pending transactions")

    try:
        pending_transactions = await db.execute(
            select(m_payment.Transaction)
            .filter(m_payment.Transaction.status == m_payment.TransactionStatus.PENDING)
            .options(joinedload(m_payment.Transaction.split_details), joinedload(m_payment.Transaction.bookings))
        )
        pending_transactions_db = pending_transactions.unique().scalars().all()

        transactions_succeeded = 0
        transactions_cancelled = 0

        for transaction in pending_transactions_db:
            intent_status = core_transactions.get_transaction_status(transaction.external_charge_id)
            transaction_id = transaction.id

            if intent_status == "succeeded":
                transaction.status = m_payment.TransactionStatus.SUCCESS
                transactions_succeeded += 1
                if transaction.is_split_payment:
                    await add_transfer_id_to_split_transactions(db, transaction_id)
                for booking in transaction.bookings:
                    booking.status = m_payment.BookingStatus.CONFIRMED
            elif intent_status == "canceled":
                transaction.status = m_payment.TransactionStatus.FAILED
                transactions_cancelled += 1
                if transaction.is_split_payment:
                    split_transactions = transaction.split_details
                    for split_transaction in split_transactions:
                        split_transaction.status = m_payment.TransactionStatus.FAILED

        audit_logger.sys_info(f"Transactions: succeeded: {transactions_succeeded}, cancelled: {transactions_cancelled}")
        await db.commit()
        console.log(
            f"[blue][INFO][/blue]\t\tTransactions: succeeded: {transactions_succeeded}, cancelled: {transactions_cancelled}"
        )
        return True
    except Exception as e:
        await db.rollback()
        audit_logger.sys_error("Error checking pending transactions", traceback=traceback.format_exc())
        await db.commit()
        console.log("[red][ERROR][/red]\t\tError checking pending transactions")
        console.print_exception()
        return False
