"""
Consent schemas.

Pydantic models for consent requests and responses.
"""

from app.schemas.base import BaseSchema


class ConsentGrantRequest(BaseSchema):
    """Schema for granting consent."""

    consent_type: str  # "server_data", "player_data", etc.
    resource_id: str  # Server ID, cluster ID, etc.
    expires_at: str | None = None  # Optional expiration


class ConsentRevokeRequest(BaseSchema):
    """Schema for revoking consent."""

    consent_id: str


class ConsentResponse(BaseSchema):
    """Schema for consent status response."""

    id: str
    consent_type: str
    resource_id: str
    granted_at: str
    expires_at: str | None = None
    revoked_at: str | None = None
