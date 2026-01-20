"""
Webhook endpoints.

Handles Stripe webhook events.
Webhooks update subscription status, license keys, etc.
"""

from fastapi import APIRouter, Request

router = APIRouter(prefix="/webhooks", tags=["webhooks"])


@router.post("/stripe")
async def stripe_webhook(request: Request):
    """
    Handle Stripe webhook events.

    Verifies webhook signature before processing.
    Processes subscription events, payment events, etc.

    Note: Uses idempotency (event ID) instead of rate limiting.
    Stripe retries webhooks, so we must handle duplicates gracefully.
    """
    # TODO: Implement Stripe webhook handler
    # TODO: Verify webhook signature using STRIPE_WEBHOOK_SECRET
    # TODO: Check idempotency (event ID) to prevent duplicate processing
    # TODO: Process webhook events (subscription.created, subscription.updated, etc.)
    # TODO: Update subscriptions table
    pass
