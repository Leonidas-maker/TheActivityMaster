from fastapi import APIRouter
import uuid

# Router for club membership endpoints
router = APIRouter()

###########################################################################
################################### Main ##################################
###########################################################################
@router.get("", tags=["Club - Membership"])
async def get_memberships_v1(club_id: uuid.UUID):
    pass


@router.post("", tags=["Club - Membership"])
async def create_membership_v1(club_id: uuid.UUID):
    pass


@router.get("/{membership_id}", tags=["Club - Membership"])
async def get_membership_v1(club_id: uuid.UUID, membership_id: uuid.UUID):
    pass


@router.put("/{membership_id}", tags=["Club - Membership"])
async def update_membership_v1(club_id: uuid.UUID, membership_id: uuid.UUID):
    pass


@router.delete("/{membership_id}", tags=["Club - Membership"])
async def delete_membership_v1(club_id: uuid.UUID, membership_id: uuid.UUID):
    pass

###########################################################################
############################## Subscriptions ##############################
###########################################################################
@router.get("/subscriptions", tags=["Club - Membership Subscription"])
async def get_subscriptions_v1(club_id: uuid.UUID):
    pass


@router.get(
    "/{membership_id}/subscriptions/{subscription_id}", tags=["Club - Membership Subscription"]
)
async def get_subscription_v1(club_id: uuid.UUID, membership_id: uuid.UUID, subscription_id: uuid.UUID):
    pass


@router.delete(
    "/{membership_id}/subscriptions/{subscription_id}", tags=["Club - Membership Subscription"]
)
async def delete_subscription_v1(club_id: uuid.UUID, membership_id: uuid.UUID, subscription_id: uuid.UUID):
    pass
