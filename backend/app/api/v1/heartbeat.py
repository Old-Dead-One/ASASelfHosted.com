"""
Heartbeat endpoints.

Handles signed heartbeat ingestion from server agents.
Heartbeats prove server is online and operational.
"""

from fastapi import APIRouter, Depends, Request

from app.core.deps import get_optional_user
from app.core.security import UserIdentity
from app.middleware.rate_limit import heartbeat_rate_limit

router = APIRouter(prefix="/heartbeat", tags=["heartbeat"])


@router.post("/")
async def ingest_heartbeat(
    request: Request,
    server_id: str,  # Will come from request body in implementation
    user: UserIdentity | None = Depends(get_optional_user),
):
    """
    Ingest signed heartbeat from server agent.

    Heartbeat must be:
    - Signed with server's private key
    - Include server status information
    - Timestamped

    Rate limited: 12 requests per minute per server_id.

    Consent: Server owner must have granted consent for heartbeat collection.
    """
    # Rate limit check (12 requests per minute per server)
    heartbeat_rate_limit(request, server_id)

    # TODO: Implement heartbeat ingestion with signature verification
    # TODO: Validate server_id belongs to authenticated user (if user provided)
    # TODO: Verify signature
    # TODO: Write to heartbeats table
    # TODO: Update servers.effective_status
    pass
