"""
Heartbeat schemas.

Pydantic models for heartbeat requests and responses.
"""

from datetime import datetime
from typing import Literal

from app.schemas.base import BaseSchema


class HeartbeatRequest(BaseSchema):
    """
    Schema for heartbeat ingestion from server agents.

    MVP contract for agent-to-backend heartbeat reporting.
    Signature is the authentication mechanism (not user JWT).
    """

    server_id: str  # UUID of the server sending heartbeat
    sent_at: datetime  # Agent timestamp (checked for freshness)
    status: Literal["online", "offline"]  # Server status
    nonce: str  # Prevents replay attacks (e.g., UUID)
    signature: str  # Signature over canonical payload
    payload: dict | None = None  # Optional additional data (keep minimal for MVP)


class HeartbeatResponse(BaseSchema):
    """Schema for heartbeat response."""

    received: bool
    server_id: str
