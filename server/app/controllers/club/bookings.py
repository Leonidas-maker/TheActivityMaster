from fastapi import HTTPException
import uuid
from typing import List, Union, Optional, Tuple, Dict
import stripe
from sqlalchemy.orm import joinedload

from models import m_user, m_club, m_payment
from schemas import s_club, s_role, s_payment

from crud import (
    club as club_crud,
    user as user_crud,
    transactions as transactions_crud,
)

from core.generic import EndpointContext
from core import security as core_security


###########################################################################
################################# Helpers #################################
###########################################################################
def add_to_transaction_data(
    transaction_data: dict,
    session: Optional[m_club.Session] = None,
    program: Optional[m_club.Program] = None,
    membership_fee: Optional[int] = None,
) -> None:
    """Add session or program to transaction data

    :param transaction_data: Transaction data dictionary to add to
    :param session: Session object, defaults to None
    :param program: Program object, defaults to None
    :raises ValueError: If session has no price or program has no price
    """

    if session:
        if session.price is None:
            raise ValueError(f"Session {session.id} has no price")

        if session.program.club_id not in transaction_data:
            transaction_data[session.program.club_id] = s_payment.TransactionData(
                stripe_account_id=session.program.club.stripe_account_id, # type: ignore
                total_amount=session.price if membership_fee is None else membership_fee,
                currency=session.program.currency,
            )
        else:
            if transaction_data[session.program.club_id]["currency"] != session.program.currency:
                raise ValueError(f"Currency mismatch for session {session.id}")

            transaction_data[session.program.club_id]["total_amount"] += (
                session.price if membership_fee is None else membership_fee
            )
    elif program:
        if program.price is None:
            raise ValueError(f"Program {program.id} has no price")

        if program.club_id not in transaction_data:
            transaction_data[program.club_id] = s_payment.TransactionData(
                stripe_account_id=program.club.stripe_account_id, # type: ignore
                total_amount=program.price if membership_fee is None else membership_fee,
                currency=program.currency,
            )
        else:
            if transaction_data[program.club_id]["currency"] != program.currency:
                raise ValueError(f"Currency mismatch for program {program.id}")

            transaction_data[program.club_id]["total_amount"] += (
                program.price if membership_fee is None else membership_fee
            )


###########################################################################
################################### Main ##################################
###########################################################################
async def create_bookings(
    ep_context: EndpointContext,
    token_details: core_security.TokenDetails,
    booking_create: s_payment.BookingCreateRequest,
) -> Tuple[List[s_payment.Booking], Optional[stripe.PaymentIntent]]:
    audit_log = ep_context.audit_logger
    db = ep_context.db
    user_id = token_details.user_id

    # Step 1: Get all sessions and programs to book
    sessions_to_book: List[m_club.Session] = []
    programs_to_book: List[m_club.Program] = []
    all_session_ids: List[uuid.UUID] = []

   
    if booking_create.session_ids:
        sessions = await club_crud.get_bookable_sessions(db, booking_create.session_ids)

        if len(sessions) != len(booking_create.session_ids):
            raise HTTPException(status_code=400, detail="Invalid session_ids")

        sessions_to_book.extend(sessions)
        all_session_ids.extend(booking_create.session_ids)

    if booking_create.program_ids:
        programs = await club_crud.get_bookable_programs(db, booking_create.program_ids)

        if len(programs) != len(booking_create.program_ids):
            raise HTTPException(status_code=400, detail="Invalid program_ids")

        programs_to_book.extend(programs)
        for program in programs:
            all_session_ids.extend([session.id for session in program.sessions])

    if await club_crud.has_user_booked(db, user_id, all_session_ids):
        raise HTTPException(status_code=400, detail="User has already booked some of the sessions")

    # Step 2: Check which is bookable or free for the user
    user_memberships = await club_crud.get_user_membership_subscriptions(db, user_id, only_active=True)
    user_memberships_dict = {membership.membership_id: membership for membership in user_memberships}

    transaction_data: Dict[uuid.UUID, s_payment.TransactionData] = {}
    bookings: List[Tuple[m_club.Session, int, m_payment.BookingType]] = []

    # Step 2.1: Check which sessions are bookable or free for the user
    for session in sessions_to_book:
        program = session.program

        has_membership = False
        for membership_access in program.memberships_access:
            # Check if user has membership
            if user_memberships_dict.get(membership_access.membership_id):
                # Check if user has to pay additional fee
                if membership_access.additional_fee != 0:
                    add_to_transaction_data(transaction_data, session=session)
                    bookings.append((session, membership_access.additional_fee, m_payment.BookingType.MEMBERSHIP))  # type: ignore
                else:
                    bookings.append((session, 0, m_payment.BookingType.MEMBERSHIP_ACCESS))
                has_membership = True
                break

        # If user has no membership
        if not has_membership:
            if program.membership_required:
                raise HTTPException(status_code=400, detail=f"Membership required for session {session.id}")
            elif session.price != 0:
                add_to_transaction_data(transaction_data, session=session)
                bookings.append((session, session.price, m_payment.BookingType.PAID))  # type: ignore
            else:
                bookings.append((session, 0, m_payment.BookingType.FREE))

    # Step 2.2: Check which programs are bookable or free for the user
    for program in programs_to_book:
        has_membership = False
        for membership_access in program.memberships_access:
            # Check if user has membership
            if user_memberships_dict.get(membership_access.membership_id):
                # Check if user has to pay additional fee
                if membership_access.additional_fee != 0:
                    add_to_transaction_data(transaction_data, program=program)
                    for session in program.sessions:
                        bookings.append((session, membership_access.additional_fee, m_payment.BookingType.MEMBERSHIP))  # type: ignore
                else:
                    for session in program.sessions:
                        bookings.append((session, 0, m_payment.BookingType.MEMBERSHIP_ACCESS))

                has_membership = True
                break

        # If user has no membership
        if not has_membership:
            if program.membership_required:
                raise HTTPException(status_code=400, detail=f"Membership required for program {program.id}")
            elif program.price != 0:
                add_to_transaction_data(transaction_data, program=program)
                for session in program.sessions:
                    bookings.append((session, program.price, m_payment.BookingType.PAID))  # type: ignore
            else:
                for session in program.sessions:
                    bookings.append((session, 0, m_payment.BookingType.FREE))

    # Step 3: Create transaction
    transaction_id = None
    payment_intent = None
    if transaction_data:
        transaction, payment_intent = await transactions_crud.create_transaction(db, user_id, transaction_data)
        transaction_id = transaction.id
        audit_log.transaction_created(user_id, transaction.id, payment_intent)

    # Step 4: Create bookings
    bookings_db, details = await club_crud.create_bookings(db, user_id, bookings, transaction_id)

    # Step 5: Audit log
    audit_log.bookings_created(user_id, details)

    bookings_res: List[s_payment.Booking] = [s_payment.Booking.model_validate(booking) for booking in bookings_db]

    await db.commit()
    return bookings_res, payment_intent


async def user_cancel_bookings(
    ep_context: EndpointContext,
    token_details: core_security.TokenDetails,
    booking_ids: List[uuid.UUID],
) -> m_payment.Transaction:
    audit_log = ep_context.audit_logger
    db = ep_context.db
    user_id = token_details.user_id

    bookings = await club_crud.get_bookings_by_ids(
        db,
        booking_ids,
        additional_query_options=[
            joinedload(m_payment.Booking.session),
            joinedload(m_payment.Booking.session).joinedload(m_club.Session.program),
            joinedload(m_payment.Booking.session)
            .joinedload(m_club.Session.program)
            .joinedload(m_club.Program.sessions)
            .load_only(m_club.Session.id),
        ],
    )

    if not bookings:
        raise HTTPException(status_code=400, detail="Invalid booking_ids")

    for booking in bookings:
        if booking.user_id != user_id:
            raise HTTPException(status_code=400, detail="Booking not found")
        if booking.status in {m_payment.BookingStatus.CANCELLED, m_payment.BookingStatus.CANCELLED_BY_CLUB}:
            raise HTTPException(status_code=400, detail="Booking already cancelled")
        elif booking.status == m_payment.BookingStatus.COMPLETED:
            raise HTTPException(status_code=400, detail="Booking already completed")
        elif booking.status == m_payment.BookingStatus.PENDING:
            raise HTTPException(
                status_code=400,
                detail="Booking not yet confirmed and payment not yet processed. Please wait a few minutes and try again",
            )


        if booking.session.program.pricing_model == m_club.PriceType.PACKAGE:
            booked_sessions_ids = {session.id for session in booking.session.program.sessions}
            for session in booking.session.program.sessions:
                if session.id not in booked_sessions_ids:
                    raise HTTPException(
                        status_code=400,
                        detail=f"For package booking, all sessions must be cancelled. Missing {session.id}",
                    )

    bookings_to_refund = [booking for booking in bookings if booking.booking_type not in m_payment.FREE_BOOKING_TYPES]

    if bookings_to_refund:
        try:
            refunds = await transactions_crud.create_refund(
                db, bookings_to_refund, "User requested refund", check_pricing_model=False
            )
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

        audit_log.refunds_created(
            user_id=user_id,
            transaction_id=bookings_to_refund[0].transaction_id,
            refund_ids=[refund.id for refund in refunds],
            details=f"User initiated refund for {', '.join([str(booking.id) for booking in bookings_to_refund])}",
            is_initiated_by_user=True,
        )

    await club_crud.change_booking_stats(db, booking_ids, m_payment.BookingStatus.CANCELLED)
    details = f"User requested refund for {', '.join([str(booking.id) for booking in bookings])}"
    audit_log.bookings_cancelled(user_id, details)

    transaction_id = bookings[0].transaction_id
    await db.commit()
    transaction = await transactions_crud.get_transaction_by_id(db, transaction_id)
    return transaction
