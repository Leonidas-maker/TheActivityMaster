from fastapi import HTTPException
import uuid
from sqlalchemy.orm import joinedload
from typing import List, Union, Optional, Tuple

from config.settings import DEBUG, DEFAULT_TIMEZONE
from config.permissions import ClubPermissions

from models import m_user, m_club, m_payment
from schemas import s_club, s_generic, s_role

from crud import (
    club as club_crud,
    user as user_crud,
    role as role_crud,
    transactions as transactions_crud,
)

from core.generic import EndpointContext
import core.security as core_security


###########################################################################
################################# Program #################################
###########################################################################
async def create_program(
    ep_context: EndpointContext,
    token_details: core_security.TokenDetails,
    club_id: uuid.UUID,
    new_program: s_club.ProgramCreate,
) -> s_club.Program:
    """Create a program

    :param ep_context: The endpoint context containing database and logger
    :param token_details: The token details of the authenticated user
    :param club_id: The ID of the club
    :param program: The details of the program to create
    :return: The created program
    """
    db = ep_context.db
    audit_log = ep_context.audit_logger
    issuer_id = token_details.user_id

    if new_program.pricing_model == m_club.PriceType.PACKAGE and any(
        [session.price for session in new_program.sessions]
    ):
        raise HTTPException(status_code=400, detail="No session should have a price if the pricing model is 'package'.")

    if new_program.pricing_model == m_club.PriceType.PER_SESSION and not all(
        [session.price for session in new_program.sessions]
    ):
        raise HTTPException(
            status_code=400, detail="Each session must have a price if the pricing model is 'per_session'."
        )

    if await club_crud.program_exists(db, club_id, new_program.name):
        raise HTTPException(status_code=400, detail="Program name already exists")

    if (
        new_program.status == m_club.ProgramStatusPublic.ACTIVE
        and await club_crud.has_club_stripe_account(db, club_id) is False
    ):
        raise HTTPException(status_code=400, detail="Cannot activate a program without a stripe account")

    try:
        program = await club_crud.create_program(db, club_id, new_program)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    details = f"Sessions: {', '.join([str(session.id) for session in program.sessions])}"
    audit_log.program_created(issuer_id, club_id, program.id, details)

    s_program = s_club.Program.model_validate(program)

    await db.commit()
    return s_program


async def update_program(
    ep_context: EndpointContext,
    token_details: core_security.TokenDetails,
    club_id: uuid.UUID,
    program_id: uuid.UUID,
    program_update: s_club.ProgramUpdate,
) -> s_club.Program:
    """Update a program

    :param ep_context: The endpoint context containing database and logger
    :param token_details: The token details of the authenticated user
    :param club_id: The ID of the club
    :param program_id: The ID of the program to update
    :param program_update: The data to update the program with
    :return: The updated program
    """
    db = ep_context.db
    audit_log = ep_context.audit_logger
    issuer_id = token_details.user_id

    program = await club_crud.get_program(db, club_id, program_id, with_details=True, with_club=True)

    if not program:
        raise HTTPException(status_code=404, detail="Program not found")

    if program_update.pricing_model and program.status == m_club.ProgramStatusPublic.ACTIVE:
        raise HTTPException(status_code=400, detail="Cannot change pricing model of an active program")

    if (
        program_update.status
        and program_update.status == m_club.ProgramStatusPublic.ACTIVE
        and program.club.stripe_account_id is None
    ):
        raise HTTPException(status_code=400, detail="Cannot activate a program without a stripe account")

    try:
        details = await club_crud.update_program(db, program, program_update)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    audit_log.program_updated(issuer_id, program.club_id, program.id, details)

    s_program = s_club.Program.model_validate(program)

    await db.commit()
    return s_program


async def delete_program(
    ep_context: EndpointContext,
    token_details: core_security.TokenDetails,
    club_id: uuid.UUID,
    program_id: uuid.UUID,
) -> None:
    """Delete a program

    :param ep_context: The endpoint context containing database and logger
    :param token_details: The token details of the authenticated user
    :param club_id: The ID of the club
    :param program_id: The ID of the program to delete
    :return: None
    """
    db = ep_context.db
    audit_log = ep_context.audit_logger
    issuer_id = token_details.user_id

    program = await club_crud.get_program(db, club_id, program_id)

    if not program:
        raise HTTPException(status_code=404, detail="Program not found")

    # TODO: Check if program sessions are booked
    # * We need a param to force delete the program and cancel all bookings -> init refund process
    # * If not force delete, set the last session date of each session to the last booked date
    # await club_crud.delete_program(db, program_id)
    # audit_log.program_deleted(issuer_id, club_id, program_id)

    # await db.commit()


###########################################################################
################################# Session #################################
###########################################################################
async def create_session(
    ep_context: EndpointContext,
    token_details: core_security.TokenDetails,
    club_id: uuid.UUID,
    program_id: uuid.UUID,
    new_session: s_club.SessionCreate,
) -> s_club.Session:
    """Create a session

    :param ep_context: The endpoint context containing database and logger
    :param token_details: The token details of the authenticated user
    :param club_id: The ID of the club
    :param program_id: The ID of the program
    :param session: The details of the session to create
    :return: The created session
    """
    db = ep_context.db
    audit_log = ep_context.audit_logger
    issuer_id = token_details.user_id

    program = await club_crud.get_program(db, club_id, program_id, with_details=True)

    if not program:
        raise HTTPException(status_code=404, detail="Program not found")
    if program.pricing_model == m_club.PriceType.PACKAGE and program.status == m_club.ProgramStatus.ACTIVE:
        raise HTTPException(
            status_code=400, detail="Cannot create a session for an active program with pricing model 'package'"
        )

    if (
        program.pricing_model == m_club.PriceType.PER_SESSION
        and new_session.price is None
        or new_session.capacity is None
    ):
        raise HTTPException(
            status_code=400, detail="Each session must have a price and capacity if the pricing model is 'per_session'."
        )

    if new_session.session_type == m_club.SessionType.EVENT and await club_crud.session_exists_event(
        db, program_id, new_session.start_datetime, new_session.end_datetime  # type: ignore
    ):
        raise HTTPException(status_code=400, detail="Event session with the same start and end times already exists")

    if new_session.session_type == m_club.SessionType.COURSE and await club_crud.session_exists_course(
        db, program_id, new_session.day_of_week, new_session.start_time, new_session.end_time  # type: ignore
    ):
        raise HTTPException(
            status_code=400, detail="Course session with the same start and end times and day of week already"
        )

    try:
        session = await club_crud.create_session(db, program_id, new_session)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    details = f"Program: {program_id}"
    audit_log.session_created(issuer_id, club_id, session.id, details)

    s_session = s_club.Session.model_validate(session)

    await db.commit()
    return s_session


async def update_session(
    ep_context: EndpointContext,
    token_details: core_security.TokenDetails,
    club_id: uuid.UUID,
    program_id: uuid.UUID,
    session_id: uuid.UUID,
    session_update: s_club.SessionUpdate,
) -> s_club.Session:
    """Update a session

    :param ep_context: The endpoint context containing database and logger
    :param token_details: The token details of the authenticated user
    :param program_id: The ID of the program
    :param session_id: The ID of the session to update
    :param session_update: The data to update the session with
    :return: The updated session
    """
    db = ep_context.db
    audit_log = ep_context.audit_logger
    issuer_id = token_details.user_id

    session = await club_crud.get_active_session(
        db,
        program_id,
        session_id,
        query_options=[
            joinedload(m_club.Session.bookings),
            joinedload(m_club.Session.program),
            joinedload(m_club.Session.occurrences),
        ],
    )

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    if (
        session.program.pricing_model == m_club.PriceType.PACKAGE
        and session.program.status == m_club.ProgramStatus.ACTIVE
    ):
        raise HTTPException(
            status_code=400, detail="Cannot update a session for an active program with pricing model 'package'"
        )

    try:
        details = await club_crud.update_session(db, session, session_update)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    audit_log.session_updated(issuer_id, club_id, session_id, details)

    s_session = s_club.Session.model_validate(session)

    await db.commit()
    return s_session


async def delete_session(
    ep_context: EndpointContext,
    token_details: core_security.TokenDetails,
    club_id: uuid.UUID,
    program_id: uuid.UUID,
    session_id: uuid.UUID,
) -> None:
    """Delete a session

    :param ep_context: The endpoint context containing database and logger
    :param token_details: The token details of the authenticated user
    :param program_id: The ID of the program
    :param session_id: The ID of the session to delete
    :return: None
    """
    db = ep_context.db
    audit_log = ep_context.audit_logger
    issuer_id = token_details.user_id

    session_to_delete = await club_crud.get_active_session(
        db,
        program_id,
        session_id,
        query_options=[
            joinedload(m_club.Session.program).joinedload(m_club.Program.sessions),
            joinedload(m_club.Session.bookings),
        ],
    )

    if not session_to_delete:
        raise HTTPException(status_code=404, detail="Session not found")

    if len(session_to_delete.bookings) > 0 and session_to_delete.membership_required == False:
        if session_to_delete.program.pricing_model == m_club.PriceType.PACKAGE:
            raise HTTPException(
                status_code=400,
                detail="Cannot delete a session that is not membership required and pricing model is package. Please delete the program instead",
            )
        elif session_to_delete.program.pricing_model == m_club.PriceType.PER_SESSION:
            bookings = await club_crud.get_bookings_by_session_id(db, session_id)

            # * This only works for per session pricing model
            for booking in bookings:
                refunds = await transactions_crud.create_refund(
                    db, [booking], f"Club {club_id} cancelled session", is_user_refund=False, check_pricing_model=False
                )
                refund_details = f"Club {club_id} cancelled session refund for booking: {booking.id}"
                audit_log.refunds_created(
                    issuer_id,
                    booking.transaction_id,
                    [refund.id for refund in refunds],
                    refund_details,
                    is_initiated_by_user=False,
                )

                booking.status = m_payment.BookingStatus.CANCELLED_BY_CLUB

            details = f"Club {club_id} cancelled session with bookings: {', '.join([str(booking.id) for booking in bookings])}"
            audit_log.bookings_cancelled(issuer_id, details)

        else:
            raise HTTPException(status_code=400, detail="The handling of this program pricing model is not supported")

    # TODO EMAIL - Notify users that have booked the session
    await db.delete(session_to_delete)
    audit_log.session_deleted(issuer_id, club_id, session_id)
    await db.commit()


###########################################################################
########################### Session Occurrences ###########################
###########################################################################
async def reschedule_session_occurrences(
    ep_context: EndpointContext,
    token_details: core_security.TokenDetails,
    club_id: uuid.UUID,
    program_id: uuid.UUID,
    session_id: uuid.UUID,
    reschedules: List[s_club.SessionReschedule],
) -> None:
    """Reschedule session occurrences

    :param ep_context: The endpoint context containing database and logger
    :param token_details: The token details of the authenticated user
    :param program_id: The ID of the program
    :param session_id: The ID of the session to reschedule
    :param reschedule: The data to reschedule the session with
    :return: None
    """
    db = ep_context.db
    audit_log = ep_context.audit_logger
    issuer_id = token_details.user_id

    occurrences = await club_crud.get_session_occurrences_dict(db, program_id, session_id)

    if not occurrences:
        raise HTTPException(status_code=404, detail="No occurrences found")

    for reschedule in reschedules:
        occurrence = occurrences.get(reschedule.occurrence_id)
        if not occurrence:
            raise HTTPException(status_code=404, detail="Occurrence not found")

        await club_crud.session_occurrence_reschedule(db, occurrence, reschedule)

        if occurrence.status != m_club.OccurrenceStatus.RESCHEDULED:
            # TODO EMAIL - Notify users that have booked the session
            pass

        details = f"Rescheduled to {reschedule.start_datetime} - {reschedule.end_datetime}"
        audit_log.occurrence_rescheduled(issuer_id, club_id, session_id, occurrence.id, details)

    await db.commit()


async def cancel_session_occurrences(
    ep_context: EndpointContext,
    token_details: core_security.TokenDetails,
    club_id: uuid.UUID,
    program_id: uuid.UUID,
    session_id: uuid.UUID,
    occurrence_id: uuid.UUID,
    note: Optional[str] = None,
) -> None:
    """Cancel session occurrences

    :param ep_context: The endpoint context containing database and logger
    :param token_details: The token details of the authenticated user
    :param program_id: The ID of the program
    :param session_id: The ID of the session to cancel
    :param occurrence_id: The ID of the occurrence to cancel
    :param note: The note to add to the cancellation
    :return: None
    """
    db = ep_context.db
    audit_log = ep_context.audit_logger
    issuer_id = token_details.user_id

    occurrence = await club_crud.get_session_occurrence(db, program_id, session_id, occurrence_id)

    if not occurrence:
        raise HTTPException(status_code=404, detail="Occurrence not found")

    if occurrence.status == m_club.OccurrenceStatus.CANCELLED:
        raise HTTPException(status_code=400, detail="Occurrence already cancelled")

    await club_crud.session_occurrence_cancel(db, occurrence, note)
    audit_log.occurrence_cancelled(issuer_id, club_id, session_id, occurrence.id, details=f"{note}")

    # TODO EMAIL - Notify users that have booked the session

    await db.commit()


async def reinstate_session_occurrences(
    ep_context: EndpointContext,
    token_details: core_security.TokenDetails,
    club_id: uuid.UUID,
    program_id: uuid.UUID,
    session_id: uuid.UUID,
    occurrences_reinstate: List[s_club.SessionReinstate],
) -> None:
    """Reinstate session occurrences

    :param ep_context: The endpoint context containing database and logger
    :param token_details: The token details of the authenticated user
    :param program_id: The ID of the program
    :param session_id: The ID of the session to reinstate
    :param occurrences_reinstate: The data to reinstate the session with
    :return: None
    """
    db = ep_context.db
    audit_log = ep_context.audit_logger
    issuer_id = token_details.user_id

    occurrences = await club_crud.get_session_occurrences_dict(db, program_id, session_id)

    if not occurrences:
        raise HTTPException(status_code=404, detail="No occurrences found")

    for occurrence_reinstate in occurrences_reinstate:
        occurrence = occurrences.get(occurrence_reinstate.occurrence_id)

        if not occurrence:
            raise HTTPException(status_code=404, detail="Occurrence not found")

        if occurrence.status == m_club.OccurrenceStatus.SCHEDULED:
            raise HTTPException(status_code=400, detail="Cannot reinstate a scheduled occurrence")

        await club_crud.session_occurrence_reinstate(db, occurrence)

        details = f"Reinstated from {occurrence.status}"
        audit_log.occurrence_rescheduled(issuer_id, club_id, session_id, occurrence.id, details)

        # TODO EMAIL - Notify users that have booked the session

    await db.commit()


###########################################################################
################################# Trainer #################################
###########################################################################
async def add_trainer(
    ep_context: EndpointContext,
    token_details: core_security.TokenDetails,
    club_id: uuid.UUID,
    program_id: uuid.UUID,
    user_id: uuid.UUID,
) -> None:
    """Add a trainer to a program

    :param ep_context: The endpoint context containing database and logger
    :param token_details: The token details of the authenticated user
    :param club_id: The ID of the club
    :param program_id: The ID of the program
    :param user_id: The ID of the user to add as a trainer
    :return: None
    """
    db = ep_context.db
    audit_log = ep_context.audit_logger
    issuer_id = token_details.user_id

    if not await club_crud.program_exists(db, club_id, program_id=program_id):
        raise HTTPException(status_code=404, detail="Program not found")

    if await role_crud.is_user_trainee(db, user_id, program_id):
        raise HTTPException(status_code=400, detail="Employee is already a trainer for this program")

    user_club_role = await club_crud.get_club_employee_by_id(db, club_id, user_id)

    if not user_club_role:
        raise HTTPException(status_code=404, detail="Employee not found")

    await club_crud.add_trainer(db, program_id, user_id)

    audit_log.trainer_added(issuer_id, club_id, program_id, user_id)
    await db.commit()


async def remove_trainer(
    ep_context: EndpointContext,
    token_details: core_security.TokenDetails,
    club_id: uuid.UUID,
    program_id: uuid.UUID,
    user_id: uuid.UUID,
) -> None:
    """Remove a trainer from a program

    :param ep_context: The endpoint context containing database and logger
    :param token_details: The token details of the authenticated user
    :param club_id: The ID of the club
    :param program_id: The ID of the program
    :param user_id: The ID of the user to remove as a trainer
    :return: None
    """
    db = ep_context.db
    audit_log = ep_context.audit_logger
    issuer_id = token_details.user_id

    if not await club_crud.program_exists(db, club_id, program_id=program_id):
        raise HTTPException(status_code=404, detail="Program not found")

    if not await role_crud.is_user_trainee(db, user_id, program_id):
        raise HTTPException(status_code=400, detail="Employee is not a trainer for this program")

    await club_crud.remove_trainer(db, program_id, user_id)

    audit_log.trainer_removed(issuer_id, club_id, program_id, user_id)
    await db.commit()
