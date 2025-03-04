from fastapi import HTTPException
import uuid
from typing import List, Union, Optional, Tuple, Dict
from sqlalchemy.orm import joinedload

from models import m_user, m_club, m_payment
from schemas import s_club, s_role, s_payment


from crud import (
    club as club_crud,
    user as user_crud,
    transactions as transactions_crud,
)

from core.generic import EndpointContext
from core import security as core_security, transactions as transactions_core


async def create_membership(
    ep_context: EndpointContext,
    token_details: core_security.TokenDetails,
    club_id: uuid.UUID,
    new_membership: s_club.MembershipCreate,
) -> s_club.Membership:
    """
    Create a new membership.

    :param ep_context: The endpoint context
    :param token_details: The token details
    :param club_id: The ID of the club to which the membership is to be added
    :param new_membership: The details of the new membership
    :return: The created membership
    """
    audit_log = ep_context.audit_logger
    db = ep_context.db
    user_id = token_details.user_id

    # Check if membership already exists
    if await club_crud.membership_exists(db, club_id, new_membership.name):
        raise HTTPException(status_code=409, detail="Membership already exists")

    if new_membership.status == m_club.MembershipStatusPublic.BOOKABLE and not club_crud.has_club_stripe_account(
        db, club_id
    ):
        raise HTTPException(status_code=400, detail="Club does not have a Stripe account")

    # Create the membership
    try:
        membership = await club_crud.create_membership(db, club_id, new_membership)
    except Exception as e:
        raise HTTPException(status_code=400, detail=e)

    # Log the creation of the membership
    audit_log.membership_created(user_id, club_id, membership.id)

    result = s_club.Membership.model_validate(membership)
    await db.commit()
    return result


async def update_membership(
    ep_context: EndpointContext,
    token_details: core_security.TokenDetails,
    club_id: uuid.UUID,
    membership_id: uuid.UUID,
    membership_update: s_club.MembershipUpdate,
) -> s_club.Membership:
    """
    Update a membership.

    :param ep_context: The endpoint context
    :param token_details: The token details
    :param club_id: The ID of the club to which the membership belongs
    :param membership_id: The ID of the membership to be updated
    :param membership_update: The details of the membership update
    :return: The updated membership
    """
    audit_log = ep_context.audit_logger
    db = ep_context.db
    user_id = token_details.user_id

    # Retrieve the membership
    membership = await club_crud.get_membership_by_id(
        db, club_id, membership_id, query_options=[joinedload(m_club.Membership.club)]
    )

    if membership is None:
        raise HTTPException(status_code=404, detail="Membership not found")

    if (
        membership_update.status
        and membership_update.status == m_club.MembershipStatusPublic.BOOKABLE
        and not club_crud.has_club_stripe_account(db, club_id)
    ):
        raise HTTPException(status_code=400, detail="Club does not have a Stripe account")

    # Update the membership
    try:
        details, cancel_subscriptions = await club_crud.update_membership(db, membership, membership_update)
    except Exception as e:
        raise HTTPException(status_code=400, detail=e)

    # Log the update of the membership
    audit_log.membership_updated(user_id, club_id, membership_id, details)

    # Cancel subscriptions if necessary
    if cancel_subscriptions:
        canceled_subscriptions = await club_crud.cancel_membership_subscriptions(db, club_id, membership_id)
        # TODO - Notify users of subscription cancellation and if their want to "renew" their subscription to the new conditions

        canceled_subscriptions_ids = [subscription.id for subscription in canceled_subscriptions]
        audit_log.membership_subscriptions_cancelled(
            user_id, club_id, canceled_subscriptions_ids, reason="Membership Update"
        )

    result = s_club.Membership.model_validate(membership)

    await db.commit()
    return result


async def delete_membership(
    ep_context: EndpointContext,
    token_details: core_security.TokenDetails,
    club_id: uuid.UUID,
    membership_id: uuid.UUID,
    user_password: str,
) -> None:
    """
    Delete a membership.

    :param ep_context: The endpoint context
    :param token_details: The token details
    :param club_id: The ID of the club to which the membership belongs
    :param membership_id: The ID of the membership to be deleted
    """
    audit_log = ep_context.audit_logger
    db = ep_context.db
    user_id = token_details.user_id

    user = await user_crud.get_user_by_id(db, user_id)
    if not user or not core_security.verify_password(user_password, user.password):
        raise HTTPException(status_code=401, detail="Invalid password")

    # Retrieve the membership
    membership = await club_crud.get_membership_by_id(db, club_id, membership_id)

    if membership is None:
        raise HTTPException(status_code=404, detail="Membership not found")

    # Delete the membership
    await club_crud.delete_membership(db, membership)

    # Cancel subscriptions
    canceled_subscriptions = await club_crud.cancel_membership_subscriptions(db, club_id, membership_id)
    # TODO - Notify users of subscription cancellation

    canceled_subscriptions_ids = [subscription.id for subscription in canceled_subscriptions]

    # Log the deletion of the membership
    audit_log.membership_deleted(
        user_id,
        club_id,
        membership_id,
        f"Canceled {len(canceled_subscriptions)} subscriptions. See canceled subscriptions audit log for details.",
    )
    audit_log.membership_subscriptions_cancelled(
        user_id, club_id, canceled_subscriptions_ids, reason="Membership Deletion"
    )

    await db.commit()


async def create_membership_access(
    ep_context: EndpointContext,
    token_details: core_security.TokenDetails,
    club_id: uuid.UUID,
    membership_id: uuid.UUID,
    new_membership_access: List[s_club.MembershipProgramAccessCreate],
) -> List[s_club.MembershipProgramAccess]:
    """
    Create a new membership access.

    :param ep_context: The endpoint context
    :param token_details: The token details
    :param club_id: The ID of the club to which the membership belongs
    :param membership_id: The ID of the membership to which the access is to be added
    :param new_membership_access: The details of the new membership access
    :return: The created membership access
    """
    audit_log = ep_context.audit_logger
    db = ep_context.db
    user_id = token_details.user_id

    # Check if membership access already exists
    if not await club_crud.membership_exists(db, club_id, membership_id=membership_id, only_active=False):
        raise HTTPException(status_code=404, detail="Membership not found")

    club_program_ids = await club_crud.get_club_program_ids(db, club_id)
    if not all(access.program_id in club_program_ids for access in new_membership_access):
        raise HTTPException(status_code=400, detail="Invalid program ID")

    if await club_crud.any_membership_access_exists(
        db, membership_id, [access.program_id for access in new_membership_access]
    ):
        raise HTTPException(status_code=409, detail="Membership access already exists")

    # Create the membership access
    try:
        access = await club_crud.create_membership_access(db, membership_id, new_membership_access)
    except Exception as e:
        raise HTTPException(status_code=400, detail=e)

    # Log the creation of the membership access
    audit_log.membership_access_created(user_id, club_id, membership_id, [access.program_id for access in access])

    result = [s_club.MembershipProgramAccess.model_validate(access) for access in access]
    await db.commit()
    return result


async def update_membership_access(
    ep_context: EndpointContext,
    token_details: core_security.TokenDetails,
    club_id: uuid.UUID,
    membership_id: uuid.UUID,
    program_id: uuid.UUID,
    new_additional_fee: int,
) -> s_club.MembershipProgramAccess:
    """
    Update a membership access.

    :param ep_context: The endpoint context
    :param token_details: The token details
    :param club_id: The ID of the club to which the membership belongs
    :param membership_id: The ID of the membership to which the access belongs
    :param program_id: The ID of the program to which the access belongs
    :param access_update: The details of the access update
    :return: The updated membership access
    """
    audit_log = ep_context.audit_logger
    db = ep_context.db
    user_id = token_details.user_id

    # Retrieve the membership access
    access = await club_crud.get_membership_access(db, club_id, membership_id, program_id)

    if not access:
        raise HTTPException(status_code=404, detail="Membership access not found")

    # Update the membership access
    try:
        access = await club_crud.update_membership_access(db, access, new_additional_fee)
    except Exception as e:
        raise HTTPException(status_code=400, detail=e)

    # Log the update of the membership access
    audit_log.membership_access_updated(user_id, club_id, membership_id, access.program_id, new_additional_fee)

    result = s_club.MembershipProgramAccess.model_validate(access)
    await db.commit()
    return result


async def delete_membership_access(
    ep_context: EndpointContext,
    token_details: core_security.TokenDetails,
    club_id: uuid.UUID,
    membership_id: uuid.UUID,
    program_ids: List[uuid.UUID],
) -> None:
    """
    Delete a membership access.

    :param ep_context: The endpoint context
    :param token_details: The token details
    :param club_id: The ID of the club to which the membership belongs
    :param membership_id: The ID of the membership to which the access belongs
    :param program_id: The ID of the program to which the access belongs
    """
    audit_log = ep_context.audit_logger
    db = ep_context.db
    user_id = token_details.user_id

    if not await club_crud.membership_exists(db, club_id, membership_id=membership_id, only_active=False):
        raise HTTPException(status_code=409, detail="Membership not found")

    if not await club_crud.any_membership_access_exists(db, membership_id, program_ids):
        raise HTTPException(status_code=409, detail="Membership access not found")

    # Delete the membership access
    await club_crud.delete_membership_access(db, membership_id, program_ids)

    # Log the deletion of the membership access
    audit_log.membership_access_deleted(user_id, club_id, membership_id, program_ids)

    await db.commit()


async def buy_membership(
    ep_context: EndpointContext,
    token_details: core_security.TokenDetails,
    club_id: uuid.UUID,
    membership_id: uuid.UUID,
) -> s_payment.MemberShipsubscriptionResponse:
    audit_log = ep_context.audit_logger
    db = ep_context.db
    membership = await club_crud.get_membership_by_id(
        db, club_id, membership_id, query_options=[joinedload(m_club.Membership.club)]
    )

    if not membership:
        raise HTTPException(status_code=404, detail="Membership not found")
    
    if membership.status != m_club.MembershipStatusPublic.BOOKABLE:
        raise HTTPException(status_code=404, detail="Membership not found")

    user = await user_crud.get_user_by_id(db, token_details.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    try:
        membership_subscription, stripe_subscription = await club_crud.create_membership_subscription(
            db, user, membership
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=e)

    # Log the creation of the membership subscription
    audit_log.membership_supscription_created(user.id, club_id, membership_subscription.id)

    #TODO Change to correct stripe implementation
    client_secret = None
    if not hasattr(membership_subscription, "latest_invoice"):
        client_secret = "dummy_client_secret" 
    elif hasattr(membership_subscription, "latest_invoice"):
        client_secret = membership_subscription.latest_invoice.payment_intent.client_secret 
    
    if not client_secret:
        transactions_core.cancel_subscription(membership.club.stripe_account_id, stripe_subscription.id)
        raise HTTPException(status_code=500, detail="Payment intent client secret not found. Please try again.")

    await db.commit()

    result = s_payment.MemberShipsubscriptionResponse(
        subscriptionId=stripe_subscription.id,
        subscriptionStatus=stripe_subscription.status,
        paymentIntentClientSecret=client_secret,
    )
    return result


async def cancel_membership(
    ep_context: EndpointContext,
    token_details: core_security.TokenDetails,
    club_id: uuid.UUID,
    membership_id: uuid.UUID,
) -> None:
    audit_log = ep_context.audit_logger
    db = ep_context.db
    user_id = token_details.user_id

    membership = await club_crud.get_membership_by_id(
        db, club_id, membership_id, query_options=[joinedload(m_club.Membership.club)]
    )

    if membership is None:
        raise HTTPException(status_code=404, detail="Membership not found")

    user = await user_crud.get_user_by_id(db, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    membership_subscription = await club_crud.get_membership_subscription_by_user(db, user_id, membership_id)
    if membership_subscription is None:
        raise HTTPException(status_code=404, detail="Membership subscription not found")

    try:
        await club_crud.cancel_membership_subscription(db, membership_subscription)
    except Exception as e:
        raise HTTPException(status_code=400, detail=e)

    # Log the cancellation of the membership subscription
    audit_log.membership_subscription_cancelled(user_id, club_id, membership_subscription.id)

    await db.commit()
