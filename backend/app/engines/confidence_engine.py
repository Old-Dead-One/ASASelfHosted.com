"""
Confidence engine.

Computes RYG confidence from heartbeat consistency and agent signals.
"""

from datetime import datetime, timezone
from typing import Literal

from app.db.servers_derived_repo import Heartbeat


def compute_confidence(
    server_id: str,
    heartbeats: list[Heartbeat],
    grace_window_seconds: int,
    agent_version: str | None = None
) -> Literal["green", "yellow", "red"]:
    """
    Compute RYG confidence (v1, simple, deterministic).
    
    green: within grace + enough samples (consistent)
    yellow: within 2*grace or insufficient samples (intermittent/new)
    red: stale beyond 2*grace (stale/spoof attempts)
    
    Args:
        server_id: Server UUID (for logging/debugging)
        heartbeats: List of heartbeats ordered by received_at DESC
        grace_window_seconds: Grace window in seconds
        agent_version: Optional agent version string (not used in v1, reserved for future)
        
    Returns:
        Confidence level: "green", "yellow", or "red"
    """
    if not heartbeats:
        # No heartbeats → red (stale/never seen)
        return "red"
    
    # Get most recent heartbeat
    latest_heartbeat = heartbeats[0]
    latest_received_at = latest_heartbeat["received_at"]
    
    # Check time since latest heartbeat
    now = datetime.now(timezone.utc)
    time_since_latest = (now - latest_received_at).total_seconds()
    
    # Red: stale beyond 2*grace
    if time_since_latest > (2 * grace_window_seconds):
        return "red"
    
    # Check sample count (need at least 3 heartbeats for green)
    sample_count = len(heartbeats)
    if sample_count < 3:
        # Insufficient samples → yellow (new/intermittent)
        return "yellow"
    
    # Check if within grace window
    if time_since_latest <= grace_window_seconds:
        # Within grace + enough samples → green (consistent)
        return "green"
    else:
        # Within 2*grace but beyond grace → yellow (intermittent)
        return "yellow"
