"""
Stripe utilities.

Handles Stripe API interactions.
Subscription management, webhook processing, etc.
"""

import stripe

from app.core.config import settings

# Initialize Stripe (only if key is configured)
if settings.STRIPE_SECRET_KEY:
    stripe.api_key = settings.STRIPE_SECRET_KEY


def create_checkout_session(customer_id: str, price_id: str) -> dict:
    """
    Create Stripe checkout session.

    Returns checkout session object.
    """
    # TODO: Implement checkout session creation
    pass


def verify_webhook_signature(payload: bytes, signature: str) -> dict:
    """
    Verify Stripe webhook signature.

    Returns event data if signature is valid.
    Raises error if signature is invalid.
    """
    # TODO: Implement webhook signature verification
    pass
