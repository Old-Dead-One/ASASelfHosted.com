"""
Heartbeat schemas.

Pydantic models for heartbeat requests and responses.
"""

from app.schemas.base import BaseSchema


class HeartbeatRequest(BaseSchema):
    """Schema for heartbeat ingestion."""

    server_id: str
    timestamp: str
    signature: str
    status: dict  # Server status information
    # TODO: Add all heartbeat fields


class HeartbeatResponse(BaseSchema):
    """Schema for heartbeat response."""

    received: bool
    server_id: str
