"""
Verification schemas.

Pydantic models for verification requests and responses.
"""

from app.schemas.base import BaseSchema


class VerificationInitiateRequest(BaseSchema):
    """Schema for initiating verification."""

    server_id: str
    public_key: str


class VerificationVerifyRequest(BaseSchema):
    """Schema for submitting verification signature."""

    server_id: str
    challenge: str
    signature: str


class VerificationResponse(BaseSchema):
    """Schema for verification status response."""

    server_id: str
    status: str
    verified_at: str | None = None
