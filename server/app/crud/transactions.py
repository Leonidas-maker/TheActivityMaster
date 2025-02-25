from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, or_, exists, and_, ColumnElement
from sqlalchemy.orm import undefer, joinedload
from typing import List, Tuple, Optional, Dict
import stripe
import uuid
from rich.console import Console
import traceback

from schemas import s_club, s_payment

from models import m_club, m_user, m_payment

from crud import role as role_crud, generic as generic_crud, audit as audit_crud

from core import transactions as core_transactions


async def create_transaction(
    db: AsyncSession, user_id: uuid.UUID, transaction_data: Dict[uuid.UUID, s_club.TransactionData]
) -> Tuple[m_payment.Transaction, stripe.PaymentIntent]:
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


###########################################################################
############################## Recurring Task #############################
###########################################################################
async def check_pending_transactions(db: AsyncSession, console: Console) -> bool:
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
