"""
Observed status endpoints.

Owner opt-in observation provides best-effort status via probes (not verified).
This router supports:
- enqueueing on-demand refresh work (used by ServerForm "Test Observation")
- fetching latest observed result + config (used for polling)
"""

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Request

from app.core.deps import extract_bearer_token, require_user
from app.core.errors import DomainValidationError, NotFoundError, UnauthorizedError
from app.core.security import UserIdentity
from app.core.supabase import get_rls_client
from app.db.observed_repo import ObservedRepository
from app.db.providers import get_observed_repo
from app.middleware.rate_limit import auth_user_rate_limit
from app.schemas.observed import (
    ObservedRefreshRequest,
    ObservedRefreshResponse,
    ServerObservationConfig,
    ServerObservedLatestResponse,
)

router = APIRouter(prefix="/observed", tags=["observed"])


@router.post(
    "/refresh",
    response_model=ObservedRefreshResponse,
    status_code=202,
    dependencies=[Depends(auth_user_rate_limit)],
)
async def refresh_observed(
    body: ObservedRefreshRequest,
    request: Request,
    user: UserIdentity = Depends(require_user),
    repo: ObservedRepository = Depends(get_observed_repo),
):
    """
    Enqueue on-demand observed refresh for the given server IDs (owner-only).

    This is used by the server edit form "Test Observation" and owner login refresh.
    """
    token = extract_bearer_token(request)
    if not token:
        raise UnauthorizedError("Authentication required")

    # Guardrails
    server_ids = list(dict.fromkeys([sid.strip() for sid in body.server_ids if sid.strip()]))
    if len(server_ids) == 0:
        raise DomainValidationError("server_ids must not be empty")
    if len(server_ids) > 96:
        raise DomainValidationError("server_ids must be <= 96")

    client = get_rls_client(token)
    # Cooldown prevents UI spam. For the explicit ServerForm "Test Observation" button,
    # allow immediate re-tests (owner-only + rate-limited).
    cooldown_seconds = 0 if body.reason == "test_button" else 300
    now = datetime.now(timezone.utc)

    to_enqueue: list[str] = []
    skipped_fresh = 0
    skipped_not_owned = 0

    for sid in server_ids:
        row = (
            client.table("servers")
            .select("id,owner_user_id,observed_checked_at")
            .eq("id", sid)
            .limit(1)
            .execute()
        )
        if not row.data:
            raise NotFoundError("server", sid)

        s = row.data[0]
        if str(s.get("owner_user_id")) != user.user_id:
            skipped_not_owned += 1
            continue

        checked_at_raw = s.get("observed_checked_at")
        if isinstance(checked_at_raw, str) and checked_at_raw:
            try:
                checked_at = datetime.fromisoformat(checked_at_raw.replace("Z", "+00:00"))
                if checked_at.tzinfo is None:
                    checked_at = checked_at.replace(tzinfo=timezone.utc)
                if (now - checked_at).total_seconds() < cooldown_seconds:
                    skipped_fresh += 1
                    continue
            except Exception:
                # If parse fails, treat as not fresh
                pass

        to_enqueue.append(sid)

    if skipped_not_owned:
        # Owner-only endpoint; don't leak other users' server existence
        raise UnauthorizedError("One or more servers are not owned by the current user")

    queued, skipped_dupe = await repo.enqueue_refresh(
        to_enqueue,
        requested_by_user_id=user.user_id,
        reason=body.reason,
    )
    return ObservedRefreshResponse(
        queued=queued,
        skipped_fresh=skipped_fresh,
        skipped_dupe=skipped_dupe,
    )


@router.get(
    "/latest/{server_id}",
    response_model=ServerObservedLatestResponse,
    dependencies=[Depends(auth_user_rate_limit)],
)
async def get_observed_latest(
    server_id: str,
    request: Request,
    user: UserIdentity = Depends(require_user),
    repo: ObservedRepository = Depends(get_observed_repo),
):
    """
    Get latest observed status + owner-only observation config (owner-only).

    Used by the ServerForm after "Test Observation" to poll until observed_checked_at changes.
    """
    token = extract_bearer_token(request)
    if not token:
        raise UnauthorizedError("Authentication required")

    client = get_rls_client(token)
    row = (
        client.table("servers")
        .select("id,owner_user_id,observed_status,observed_checked_at,observed_latency_ms,observed_error")
        .eq("id", server_id)
        .limit(1)
        .execute()
    )
    if not row.data:
        raise NotFoundError("server", server_id)
    s = row.data[0]
    if str(s.get("owner_user_id")) != user.user_id:
        raise UnauthorizedError("Server not found or you don't have permission to view it")

    cfg_row = await repo.get_server_observation_config(server_id)
    cfg = ServerObservationConfig(
        observation_enabled=bool(cfg_row.get("observation_enabled")) if cfg_row else False,
        observed_host=str(cfg_row.get("observed_host")) if cfg_row and cfg_row.get("observed_host") else None,
        observed_port=int(cfg_row.get("observed_port")) if cfg_row and cfg_row.get("observed_port") is not None else None,
        observed_probe=str(cfg_row.get("observed_probe")) if cfg_row and cfg_row.get("observed_probe") else "eos",
    )

    return ServerObservedLatestResponse(
        server_id=server_id,
        config=cfg,
        observed_status=s.get("observed_status"),
        observed_checked_at=s.get("observed_checked_at"),
        observed_latency_ms=s.get("observed_latency_ms"),
        observed_error=s.get("observed_error"),
    )