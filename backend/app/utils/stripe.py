"""
Stripe utilities.

Handles Stripe API interactions.
Subscription management, webhook processing, etc.
"""

import stripe

from app.core.config import get_settings

# Initialize Stripe (lazy initialization to avoid import-time side effects)
_stripe_initialized = False


def _init_stripe_if_needed():
    """Initialize Stripe API key if configured (lazy initialization)."""
    global _stripe_initialized
    if not _stripe_initialized:
        settings = get_settings()
        if settings.STRIPE_SECRET_KEY:
            stripe.api_key = settings.STRIPE_SECRET_KEY
        _stripe_initialized = True


def create_checkout_session(customer_id: str, price_id: str) -> dict:
    """
    Create Stripe checkout session.

    Returns checkout session object.
    """
    _init_stripe_if_needed()
    # TODO: Implement checkout session creation
    pass


def verify_webhook_signature(payload: bytes, signature: str) -> dict:
    """
    Verify Stripe webhook signature.

    Returns event data if signature is valid.
    Raises error if signature is invalid.
    """
    _init_stripe_if_needed()
    # TODO: Implement webhook signature verification
    pass
