"""
Subscription schemas.

Pydantic models for subscription requests and responses.
"""

from app.schemas.base import BaseSchema


class SubscriptionResponse(BaseSchema):
    """Schema for subscription status response."""

    active: bool
    plan: str | None = None
    expires_at: str | None = None


class CheckoutSessionResponse(BaseSchema):
    """Schema for checkout session response."""

    session_id: str
    url: str
