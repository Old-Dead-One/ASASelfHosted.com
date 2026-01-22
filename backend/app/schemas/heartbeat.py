"""
Heartbeat schemas.

Pydantic models for heartbeat requests and responses.
Sprint 4: Ed25519 signature verification, replay protection via heartbeat_id.
"""

from datetime import datetime
from typing import Literal

from app.schemas.base import BaseSchema


class HeartbeatRequest(BaseSchema):
    """
    Schema for heartbeat ingestion from server agents.
    
    Sprint 4 contract: Ed25519 signature verification, heartbeat_id for replay protection.
    Signature is the authentication mechanism (not user JWT).
    """

    server_id: str  # UUID of the server sending heartbeat
    key_version: int  # Key version (must match cluster's key_version)
    timestamp: datetime  # Agent-reported time (UTC, checked for freshness)
    heartbeat_id: str  # UUID string for replay protection (unique per server_id)
    status: Literal["online", "offline"]  # Server status
    map_name: str | None = None  # Map name (optional)
    players_current: int | None = None  # Current player count (optional)
    players_capacity: int | None = None  # Player capacity (optional)
    agent_version: str | None = None  # Agent version string (optional)
    payload: dict | None = None  # Optional diagnostic data (not signed, debug only)
    signature: str  # Base64 Ed25519 signature over canonical envelope


class HeartbeatResponse(BaseSchema):
    """
    Schema for heartbeat response.
    
    Indicates whether heartbeat was received, processed, and if it was a replay.
    """

    received: bool  # True if heartbeat was accepted
    server_id: str  # Server ID that sent the heartbeat
    processed: bool = False  # True if fast-path update succeeded
    replay: bool = False  # True if heartbeat_id was duplicate (replay detected)
