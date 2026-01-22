"""
Status engine.

Computes effective_status from heartbeat history and grace window.
"""

from datetime import datetime, timezone

from app.db.servers_derived_repo import Heartbeat
from app.schemas.directory import ServerStatus


def compute_effective_status(
    server_id: str,
    heartbeats: list[Heartbeat],
    grace_window_seconds: int
) -> tuple[ServerStatus, datetime | None]:
    """
    Compute effective_status from heartbeat history.
    
    Rules:
    - No heartbeats → unknown (does NOT override manual status if set)
    - Latest received_at within grace window → online
    - Otherwise → offline
    
    Uses received_at (server-trusted clock) for liveness.
    
    Note: If no agent heartbeats exist, this returns "unknown" but does not
    override a manually-set effective_status. The worker should only update
    effective_status if agent heartbeats exist (status_source='agent').
    
    Args:
        server_id: Server UUID (for logging/debugging)
        heartbeats: List of heartbeats ordered by received_at DESC (most recent first)
        grace_window_seconds: Grace window in seconds
        
    Returns:
        Tuple of (effective_status, last_seen_at datetime or None)
    """
    if not heartbeats:
        # Never seen by agent → unknown
        # Note: This does not override manual status - worker should only update
        # effective_status when status_source='agent' (i.e., when heartbeats exist)
        return "unknown", None
    
    # Get most recent heartbeat
    latest_heartbeat = heartbeats[0]
    latest_received_at = latest_heartbeat["received_at"]
    
    # Check if latest heartbeat is within grace window
    now = datetime.now(timezone.utc)
    time_since_latest = (now - latest_received_at).total_seconds()
    
    if time_since_latest <= grace_window_seconds:
        # Recent heartbeat within grace window → online
        return "online", latest_received_at
    else:
        # Missed grace window but had heartbeats before → offline
        return "offline", latest_received_at
