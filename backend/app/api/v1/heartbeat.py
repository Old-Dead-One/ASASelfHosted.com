"""
Heartbeat endpoints.

Handles signed heartbeat ingestion from server agents.
Heartbeats prove server is online and operational.

Authentication is via Ed25519 signature verification, not user JWT.
Server agents authenticate using cluster's public/private key pair.
"""

import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request

from app.core.crypto import canonicalize_heartbeat_envelope, verify_ed25519_signature
from app.core.errors import (
    KeyVersionMismatchError,
    NotFoundError,
    SignatureVerificationError,
    UnauthorizedError,
)
from app.core.heartbeat import get_grace_window_seconds
from app.core.supabase import get_supabase_admin
from app.db.heartbeat_jobs_repo import HeartbeatJobsRepository
from app.db.heartbeat_repo import HeartbeatRepository
from app.db.providers import (
    get_heartbeat_jobs_repo,
    get_heartbeat_repo,
)
from app.middleware.rate_limit import heartbeat_rate_limit
from app.schemas.heartbeat import HeartbeatRequest, HeartbeatResponse

router = APIRouter(prefix="/heartbeat", tags=["heartbeat"])
logger = logging.getLogger(__name__)


@router.post("/", response_model=HeartbeatResponse)
async def ingest_heartbeat(
    request: Request,
    heartbeat: HeartbeatRequest,
    heartbeat_repo: HeartbeatRepository = Depends(get_heartbeat_repo),
    jobs_repo: HeartbeatJobsRepository = Depends(get_heartbeat_jobs_repo),
):
    """
    Ingest signed heartbeat from server agent.

    Sprint 4: Ed25519 signature verification, replay protection via heartbeat_id.
    
    Synchronous flow (fast path):
    1. Rate limit check
    2. Load server and cluster by server_id
    3. Validate server exists → 404 if not
    4. Validate cluster has public_key_ed25519 → 401 if missing
    5. Key version check → 409 if mismatch
    6. Verify signature (Ed25519) → 401 if invalid
    7. Timestamp validation (grace window, future check) → 400 if invalid
    8. Insert heartbeat (append-only) → replay detected if duplicate heartbeat_id
    9. Fast path server update (last_seen_at, last_heartbeat_at, status_source='agent')
    10. Enqueue server_id for worker (durable queue)
    11. Return 202 Accepted

    Rate limited: 12 requests per minute per server_id.
    """
    # 1. Rate limit check (12 requests per minute per server)
    heartbeat_rate_limit(request, heartbeat.server_id)
    
    # 2. Load server and cluster by server_id
    supabase_admin = get_supabase_admin()
    if not supabase_admin:
        raise RuntimeError("Supabase admin client not configured")
    
    # Get server with cluster info
    server_response = (
        supabase_admin.table("servers")
        .select("id,cluster_id,clusters!inner(id,key_version,public_key_ed25519,heartbeat_grace_seconds)")
        .eq("id", heartbeat.server_id)
        .limit(1)
        .execute()
    )
    
    server_data = server_response.data if hasattr(server_response, "data") else []
    if not server_data:
        logger.warning(f"Heartbeat rejected: server not found", extra={"server_id": heartbeat.server_id})
        raise NotFoundError("server", heartbeat.server_id)
    
    server = server_data[0]
    cluster = server.get("clusters", {})
    
    # 3. Validate cluster has public_key_ed25519
    public_key_ed25519 = cluster.get("public_key_ed25519")
    if not public_key_ed25519:
        logger.warning(
            f"Heartbeat rejected: cluster missing public_key_ed25519",
            extra={"server_id": heartbeat.server_id, "cluster_id": cluster.get("id")}
        )
        raise UnauthorizedError("Cluster missing public_key_ed25519 for signature verification")
    
    # 4. Key version check
    cluster_key_version = cluster.get("key_version", 1)
    if heartbeat.key_version != cluster_key_version:
        logger.warning(
            f"Heartbeat rejected: key version mismatch",
            extra={
                "server_id": heartbeat.server_id,
                "expected": cluster_key_version,
                "received": heartbeat.key_version
            }
        )
        raise KeyVersionMismatchError(cluster_key_version, heartbeat.key_version)
    
    # 5. Verify signature (Ed25519)
    # Canonicalize envelope (exclude signature, payload)
    envelope = {
        "server_id": heartbeat.server_id,
        "key_version": heartbeat.key_version,
        "timestamp": heartbeat.timestamp,
        "heartbeat_id": heartbeat.heartbeat_id,
        "status": heartbeat.status,
        "map_name": heartbeat.map_name,
        "players_current": heartbeat.players_current,
        "players_capacity": heartbeat.players_capacity,
        "agent_version": heartbeat.agent_version,
    }
    canonical_message = canonicalize_heartbeat_envelope(envelope)
    
    signature_valid = verify_ed25519_signature(
        public_key_ed25519,
        canonical_message,
        heartbeat.signature
    )
    
    if not signature_valid:
        logger.warning(
            f"Heartbeat rejected: invalid signature",
            extra={"server_id": heartbeat.server_id, "cluster_id": cluster.get("id")}
        )
        raise SignatureVerificationError("Invalid Ed25519 signature")
    
    # 6. Timestamp validation
    now = datetime.now(timezone.utc)
    cluster_grace_override = cluster.get("heartbeat_grace_seconds")
    grace_window = get_grace_window_seconds(cluster_grace_override)
    
    # Ensure heartbeat.timestamp is timezone-aware
    if heartbeat.timestamp.tzinfo is None:
        heartbeat_timestamp = heartbeat.timestamp.replace(tzinfo=timezone.utc)
    else:
        heartbeat_timestamp = heartbeat.timestamp
    
    time_delta = (now - heartbeat_timestamp).total_seconds()
    
    # Reject if stale beyond grace window
    if time_delta > grace_window:
        logger.warning(
            f"Heartbeat rejected: timestamp stale",
            extra={
                "server_id": heartbeat.server_id,
                "delta_seconds": time_delta,
                "grace_window": grace_window
            }
        )
        raise HTTPException(
            status_code=400,
            detail=f"Heartbeat timestamp is stale (delta: {time_delta:.0f}s, grace: {grace_window}s)"
        )
    
    # Reject if > 60s in future
    if time_delta < -60:
        logger.warning(
            f"Heartbeat rejected: timestamp too far in future",
            extra={
                "server_id": heartbeat.server_id,
                "delta_seconds": time_delta
            }
        )
        raise HTTPException(
            status_code=400,
            detail=f"Heartbeat timestamp is too far in future (delta: {time_delta:.0f}s)"
        )
    
    # 7. Insert heartbeat (append-only)
    received_at = now
    result = await heartbeat_repo.create_heartbeat(
        heartbeat,
        received_at,
        server_cluster_id=cluster.get("id")
    )
    
    # Handle replay (idempotent - return 202 with replay=True)
    if result.replay:
        logger.info(
            f"Heartbeat replay detected (idempotent)",
            extra={"server_id": heartbeat.server_id, "heartbeat_id": heartbeat.heartbeat_id}
        )
        return HeartbeatResponse(
            received=True,
            server_id=heartbeat.server_id,
            processed=True,
            replay=True
        )
    
    # 8. Fast path server update
    try:
        update_data = {
            "last_seen_at": received_at.isoformat(),
            "last_heartbeat_at": heartbeat_timestamp.isoformat(),
            "status_source": "agent",
        }
        
        # Optionally update players_current, players_capacity for UI convenience
        if heartbeat.players_current is not None:
            update_data["players_current"] = heartbeat.players_current
        if heartbeat.players_capacity is not None:
            update_data["players_capacity"] = heartbeat.players_capacity
        
        # Optionally set effective_status='online' if signature valid (fast UX)
        # Worker will correct this later if needed
        update_data["effective_status"] = "online"
        
        supabase_admin.table("servers").update(update_data).eq("id", heartbeat.server_id).execute()
        
        processed = True
        logger.debug(
            f"Heartbeat fast-path update succeeded",
            extra={"server_id": heartbeat.server_id}
        )
    except Exception as e:
        processed = False
        logger.warning(
            f"Heartbeat fast-path update failed (non-fatal)",
            extra={"server_id": heartbeat.server_id, "error": str(e)}
        )
        # Non-fatal - worker will update later
    
    # 9. Enqueue server_id for worker (durable queue)
    try:
        await jobs_repo.enqueue_server(heartbeat.server_id)
    except Exception as e:
        logger.error(
            f"Failed to enqueue heartbeat job (non-fatal)",
            extra={"server_id": heartbeat.server_id, "error": str(e)}
        )
        # Non-fatal - heartbeat was persisted, worker can catch up
    
    # 10. Return 202 Accepted
    return HeartbeatResponse(
        received=True,
        server_id=heartbeat.server_id,
        processed=processed,
        replay=False
    )
