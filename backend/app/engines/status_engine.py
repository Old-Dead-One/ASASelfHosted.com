"""
Status engine.

Computes effective_status from heartbeat history and grace window.
Uses received_at (server-trusted clock) for liveness calculation.

Invariants:
- Output is always one of: "online", "offline", "unknown" (never None)
- Stability: Same inputs → same output (deterministic, no randomness)
- Based on received_at (not agent-reported timestamp) for server-trusted clock
- Unknown behavior: Returns "unknown" if no heartbeats (insufficient data)
- Tie-break: Most recent heartbeat wins (deterministic ordering by received_at DESC)
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
    - No heartbeats → "unknown" (does NOT override manual status if set)
    - Latest received_at within grace window → "online"
    - Otherwise → "offline"
    
    Uses received_at (server-trusted clock) for liveness.
    
    Unknown Behavior:
    - Returns "unknown" if no heartbeats (insufficient data)
    - Note: This does not override manual status - worker should only update
      effective_status when status_source='agent' (i.e., when heartbeats exist)
    
    Stability:
    - Deterministic: Same heartbeats + same grace_window → same output
    - Based on received_at (server-trusted clock), not agent timestamp
    - Tie-break: Most recent heartbeat (deterministic ordering)
    
    Args:
        server_id: Server UUID (for logging/debugging)
        heartbeats: List of heartbeats ordered by received_at DESC (most recent first)
        grace_window_seconds: Grace window in seconds
        
    Returns:
        Tuple of (effective_status, last_seen_at datetime or None)
        - effective_status: "online", "offline", or "unknown"
        - last_seen_at: Most recent received_at, or None if no heartbeats
        
    Examples:
        - No heartbeats → ("unknown", None)
        - Latest heartbeat 5 minutes ago, grace=600s → ("online", latest_received_at)
        - Latest heartbeat 15 minutes ago, grace=600s → ("offline", latest_received_at)
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
