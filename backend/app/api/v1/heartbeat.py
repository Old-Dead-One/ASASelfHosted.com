"""
Heartbeat endpoints.

Handles signed heartbeat ingestion from server agents.
Heartbeats prove server is online and operational.

Authentication is via signature verification, not user JWT.
Server agents authenticate using their registered public/private key pair.
"""

from fastapi import APIRouter, Request

from app.middleware.rate_limit import heartbeat_rate_limit
from app.schemas.heartbeat import HeartbeatRequest, HeartbeatResponse

router = APIRouter(prefix="/heartbeat", tags=["heartbeat"])


@router.post("/", response_model=HeartbeatResponse)
async def ingest_heartbeat(
    request: Request,
    heartbeat: HeartbeatRequest,
):
    """
    Ingest signed heartbeat from server agent.

    Heartbeat must be:
    - Signed with server's private key
    - Include server status information
    - Timestamped (sent_at checked for freshness window, e.g., 5 minutes)
    - Include nonce to prevent replay attacks

    Rate limited: 12 requests per minute per server_id.

    Authentication: Signature verification (not user JWT).
    Requires server to be registered and heartbeat signature valid.

    Processing steps (MVP):
    1. Rate limit by server_id
    2. Load server public key by server_id
    3. Verify signature and freshness window (sent_at within 5 minutes)
    4. Insert row into heartbeats table
    5. Update servers.effective_status, last_seen_at, status_source='agent'
    """
    # Rate limit check (12 requests per minute per server)
    heartbeat_rate_limit(request, heartbeat.server_id)

    # TODO: Load server public key by server_id
    # TODO: Verify signature over canonical payload
    # TODO: Check freshness window (sent_at within 5 minutes of now)
    # TODO: Verify nonce hasn't been used (optional: store nonces with TTL)
    # TODO: Insert row into heartbeats table
    # TODO: Update servers.effective_status, last_seen_at, status_source='agent'

    return HeartbeatResponse(
        received=True,
        server_id=heartbeat.server_id,
    )
