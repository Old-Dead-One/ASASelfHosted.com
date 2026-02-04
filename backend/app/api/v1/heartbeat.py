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
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError as PydanticValidationError

from app.core.crypto import canonicalize_heartbeat_envelope, verify_ed25519_signature
from app.core.errors import (
    KeyVersionMismatchError,
    NotFoundError,
    SignatureVerificationError,
    UnauthorizedError,
)
from app.core.config import get_settings
from app.core.heartbeat import get_grace_window_seconds
from app.core.version import is_version_at_least
from app.db.heartbeat_jobs_repo import HeartbeatJobsRepository
from app.db.heartbeat_repo import HeartbeatRepository
from app.db.ingest_rejections_repo import IngestRejectionsRepository
from app.db.providers import (
    get_heartbeat_jobs_repo,
    get_heartbeat_repo,
    get_ingest_rejections_repo,
    get_servers_derived_repo,
)
from app.db.servers_derived_repo import ServersDerivedRepository
from app.middleware.consent import DATA_TYPE_HEARTBEAT, is_data_allowed_now
from app.middleware.rate_limit import heartbeat_rate_limit
from app.schemas.heartbeat import HeartbeatRequest, HeartbeatResponse
from app.schemas.ingest import validate_heartbeat_v1_body

router = APIRouter(prefix="/heartbeat", tags=["heartbeat"])
logger = logging.getLogger(__name__)


@router.post("/", response_model=HeartbeatResponse, status_code=202)
async def ingest_heartbeat(
    request: Request,
    heartbeat_repo: HeartbeatRepository = Depends(get_heartbeat_repo),
    jobs_repo: HeartbeatJobsRepository = Depends(get_heartbeat_jobs_repo),
    derived_repo: ServersDerivedRepository = Depends(get_servers_derived_repo),
    rejections_repo: IngestRejectionsRepository = Depends(get_ingest_rejections_repo),
):
    """
    Ingest signed heartbeat from server agent.

    Sprint 4: Ed25519 signature verification, replay protection via heartbeat_id.
    Sprint 8: Body parsed here so unknown_field and malformed_payload can be audited to ingest_rejections.

    Synchronous flow (fast path):
    0. Parse body; audit unknown_field / malformed_payload to ingest_rejections.
    1. Rate limit check
    2. Load server and cluster by server_id
    3. Validate server exists → 404 if not
    4. Validate cluster has public_key_ed25519 → 401 if missing
    5. Key version check → 409 if mismatch
    6. Verify signature (Ed25519) → 401 if invalid
    7. Timestamp validation (grace window, future check) → 400 if invalid
    8. Consent gate → 403 if not allowed (e.g. not self_hosted)
    9. Insert heartbeat (append-only) → replay detected if duplicate heartbeat_id
    10. Fast path server update (last_seen_at, last_heartbeat_at, status_source='agent')
    11. Enqueue server_id for worker (durable queue)
    12. Return 202 Accepted

    Rate limited: 12 requests per minute per server_id.
    """
    # 0. Parse body and audit contract violations (DROP_ON_VIOLATION: unknown_field, malformed_payload)
    try:
        body = await request.json()
    except Exception:
        await rejections_repo.record_rejection(
            None,
            "malformed_payload",
            metadata={"note": "invalid_json"},
        )
        raise RequestValidationError([{"loc": ("body",), "msg": "Invalid JSON", "type": "value_error"}])


    valid, unknown_fields = validate_heartbeat_v1_body(body)
    if not valid and unknown_fields:
        server_id_from_body = body.get("server_id") if isinstance(body, dict) else None
        server_id_str = server_id_from_body if isinstance(server_id_from_body, str) else None
        await rejections_repo.record_rejection(
            server_id_str,
            "unknown_field",
            metadata={"unknown_fields": list(unknown_fields)},
        )
        logger.warning(
            "Heartbeat body had unknown fields (audited)",
            extra={"server_id": server_id_str, "unknown_fields": list(unknown_fields)},
        )

    try:
        heartbeat = HeartbeatRequest.model_validate(body)
    except PydanticValidationError as e:
        server_id_from_body = body.get("server_id") if isinstance(body, dict) else None
        server_id_str = server_id_from_body if isinstance(server_id_from_body, str) else None
        await rejections_repo.record_rejection(
            server_id_str,
            "malformed_payload",
            metadata={"validation_errors": [err.get("type") for err in e.errors()]},
        )
        raise RequestValidationError(e.errors()) from e

    # 1. Rate limit check (12 requests per minute per server)
    heartbeat_rate_limit(request, heartbeat.server_id)

    # 2. Load server and cluster by server_id
    server_cluster = await derived_repo.get_server_cluster_and_grace(
        heartbeat.server_id
    )
    if not server_cluster:
        await rejections_repo.record_rejection(
            heartbeat.server_id,
            "server_not_found",
            agent_version=heartbeat.agent_version,
        )
        logger.warning(
            "Heartbeat rejected: server not found",
            extra={
                "server_id": heartbeat.server_id,
                "rejection_reason": "server_not_found",
                "heartbeat_id": heartbeat.heartbeat_id,
            },
        )
        raise NotFoundError("server", heartbeat.server_id)

    public_key_ed25519 = server_cluster.get("public_key_ed25519")
    if not public_key_ed25519:
        await rejections_repo.record_rejection(
            heartbeat.server_id,
            "cluster_missing_public_key",
            agent_version=heartbeat.agent_version,
        )
        logger.warning(
            "Heartbeat rejected: cluster missing public_key_ed25519",
            extra={
                "server_id": heartbeat.server_id,
                "cluster_id": server_cluster.get("cluster_id"),
                "rejection_reason": "cluster_missing_public_key",
                "heartbeat_id": heartbeat.heartbeat_id,
            },
        )
        raise UnauthorizedError(
            "Server/cluster missing public_key_ed25519 for signature verification"
        )

    cluster_key_version = server_cluster.get("key_version", 1)
    if heartbeat.key_version != cluster_key_version:
        await rejections_repo.record_rejection(
            heartbeat.server_id,
            "key_version_mismatch",
            agent_version=heartbeat.agent_version,
            metadata={"expected": cluster_key_version, "got": heartbeat.key_version},
        )
        raise KeyVersionMismatchError(
            expected=cluster_key_version,
            got=heartbeat.key_version,
        )

    cluster_grace_seconds = server_cluster.get("heartbeat_grace_seconds")
    grace_window = get_grace_window_seconds(cluster_grace_seconds)

    # 3. Verify signature (Ed25519)
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
        public_key_ed25519, canonical_message, heartbeat.signature
    )

    if not signature_valid:
        await rejections_repo.record_rejection(
            heartbeat.server_id,
            "invalid_signature",
            agent_version=heartbeat.agent_version,
        )
        logger.warning(
            "Heartbeat rejected: invalid signature",
            extra={
                "server_id": heartbeat.server_id,
                "cluster_id": server_cluster.get("cluster_id"),
                "rejection_reason": "invalid_signature",
                "heartbeat_id": heartbeat.heartbeat_id,
                "key_version": heartbeat.key_version,
            },
        )
        raise SignatureVerificationError("Invalid Ed25519 signature")

    # 4. Timestamp validation
    now = datetime.now(timezone.utc)

    # Ensure heartbeat.timestamp is timezone-aware
    if heartbeat.timestamp.tzinfo is None:
        heartbeat_timestamp = heartbeat.timestamp.replace(tzinfo=timezone.utc)
    else:
        heartbeat_timestamp = heartbeat.timestamp

    time_delta = (now - heartbeat_timestamp).total_seconds()

    # Reject if stale beyond grace window
    if time_delta > grace_window:
        await rejections_repo.record_rejection(
            heartbeat.server_id,
            "stale_timestamp",
            agent_version=heartbeat.agent_version,
            metadata={"grace_window_seconds": grace_window, "time_delta_seconds": time_delta},
        )
        logger.warning(
            "Heartbeat rejected: timestamp stale",
            extra={
                "server_id": heartbeat.server_id,
                "rejection_reason": "timestamp_stale",
                "heartbeat_id": heartbeat.heartbeat_id,
                "timestamp": heartbeat.timestamp.isoformat()
                if heartbeat.timestamp
                else None,
                "grace_window_seconds": grace_window,
                "time_since_timestamp": time_delta,
            },
        )
        raise HTTPException(
            status_code=400,
            detail=f"Heartbeat timestamp is stale (delta: {time_delta:.0f}s, grace: {grace_window}s)",
        )

    # Reject if > 60s in future (clock skew violation)
    if time_delta < -60:
        await rejections_repo.record_rejection(
            heartbeat.server_id,
            "clock_skew_violation",
            agent_version=heartbeat.agent_version,
            metadata={"time_delta_seconds": time_delta},
        )
        logger.warning(
            "Heartbeat rejected: clock skew violation (timestamp too far in future)",
            extra={
                "server_id": heartbeat.server_id,
                "rejection_reason": "clock_skew_violation",
                "heartbeat_id": heartbeat.heartbeat_id,
                "timestamp": heartbeat.timestamp.isoformat()
                if heartbeat.timestamp
                else None,
                "time_ahead": abs(time_delta),
                "delta_seconds": time_delta,
                "agent_timestamp": heartbeat_timestamp.isoformat(),
                "server_timestamp": now.isoformat(),
                "agent_version": heartbeat.agent_version,
            },
        )
        raise HTTPException(
            status_code=400,
            detail=f"Heartbeat timestamp is too far in future (clock skew: {time_delta:.0f}s). Agent clock may be incorrect.",
        )

    # 5b. Agent version enforcement (optional) → 426 Upgrade Required
    min_agent = get_settings().MIN_AGENT_VERSION
    if min_agent and heartbeat.agent_version is not None:
        if not is_version_at_least(heartbeat.agent_version, min_agent):
            await rejections_repo.record_rejection(
                heartbeat.server_id,
                "agent_version_too_old",
                agent_version=heartbeat.agent_version,
                metadata={"min_required": min_agent},
            )
            logger.warning(
                "Heartbeat rejected: agent version below minimum",
                extra={
                    "server_id": heartbeat.server_id,
                    "rejection_reason": "agent_version_too_old",
                    "agent_version": heartbeat.agent_version,
                    "min_required": min_agent,
                },
            )
            raise HTTPException(
                status_code=426,
                detail="Upgrade required. Your agent version is below the minimum. Please update the agent.",
            )

    # 6. Consent gate: do not persist without consent
    if not is_data_allowed_now(
        heartbeat.server_id,
        DATA_TYPE_HEARTBEAT,
        context={"server_cluster": server_cluster},
    ):
        await rejections_repo.record_rejection(
            heartbeat.server_id,
            "consent_denied",
            agent_version=heartbeat.agent_version,
        )
        logger.warning(
            "Heartbeat rejected: consent denied (e.g. not self_hosted)",
            extra={
                "server_id": heartbeat.server_id,
                "rejection_reason": "consent_denied",
                "heartbeat_id": heartbeat.heartbeat_id,
            },
        )
        raise HTTPException(
            status_code=403,
            detail="Data collection not allowed for this server (e.g. not self-hosted).",
        )

    # 7. Insert heartbeat (append-only)
    received_at = now
    create_result = await heartbeat_repo.create_heartbeat(
        heartbeat, received_at, server_cluster_id=server_cluster.get("cluster_id")
    )

    # Handle replay (idempotent - return 202 with result=duplicate)
    if create_result.replay:
        logger.info(
            "Heartbeat replay detected (idempotent)",
            extra={
                "server_id": heartbeat.server_id,
                "heartbeat_id": heartbeat.heartbeat_id,
            },
        )
        return HeartbeatResponse(
            received=True,
            server_id=heartbeat.server_id,
            processed=True,
            replay=True,
            result="duplicate",
        )

    # 8. Fast path server update (effective_status from agent: online/offline/unknown)
    try:
        await derived_repo.fast_path_update_from_heartbeat(
            server_id=heartbeat.server_id,
            received_at=received_at,
            heartbeat_timestamp=heartbeat_timestamp,
            status=heartbeat.status,
            players_current=heartbeat.players_current,
            players_capacity=heartbeat.players_capacity,
        )
        processed = True
        logger.debug(
            "Heartbeat fast-path update succeeded",
            extra={"server_id": heartbeat.server_id},
        )
    except Exception as e:
        processed = False
        logger.warning(
            "Heartbeat fast-path update failed (non-fatal)",
            extra={"server_id": heartbeat.server_id, "error": str(e)},
        )
        # Non-fatal - worker will update later

    # 7. Enqueue server_id for worker (durable queue)
    try:
        await jobs_repo.enqueue_server(heartbeat.server_id)
    except Exception as e:
        logger.error(
            "Failed to enqueue heartbeat job (non-fatal)",
            extra={"server_id": heartbeat.server_id, "error": str(e)},
        )
        # Non-fatal - heartbeat was persisted, worker can catch up

    # 9. Return 202 Accepted
    return HeartbeatResponse(
        received=True,
        server_id=heartbeat.server_id,
        processed=processed,
        replay=False,
        result="accepted",
    )
