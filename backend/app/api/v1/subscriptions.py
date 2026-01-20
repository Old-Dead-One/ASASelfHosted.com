"""
Subscription endpoints.

Handles Stripe subscription management.
Subscriptions unlock premium features (unlimited file size, etc.).
"""

from fastapi import APIRouter

router = APIRouter(prefix="/subscriptions", tags=["subscriptions"])


@router.get("/")
async def get_subscription():
    """
    Get current user's subscription status.

    Requires authentication.
    """
    # TODO: Implement subscription status retrieval
    pass


@router.post("/create-checkout")
async def create_checkout_session():
    """
    Create Stripe checkout session for subscription.

    Returns checkout session URL.
    """
    # TODO: Implement Stripe checkout session creation
    pass


@router.post("/cancel")
async def cancel_subscription():
    """
    Cancel current subscription.

    Requires:
    - Authenticated user
    - Active subscription
    """
    # TODO: Implement subscription cancellation
    pass
