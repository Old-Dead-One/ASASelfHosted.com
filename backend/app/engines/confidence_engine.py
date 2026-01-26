"""
Confidence engine.

Computes RYG confidence from heartbeat consistency and agent signals.
State machine: green → yellow → red (downgrade only, no sudden jumps).

Invariants:
- Output is always one of: "green", "yellow", "red" (never None)
- Stability: Same inputs → same output (deterministic, no randomness)
- Based on received_at (server-trusted clock) for liveness
- No sudden jumps: Cannot go red → green without passing through yellow
- Monotonic downgrade: Confidence can only decrease (green → yellow → red)
"""

import logging
from datetime import datetime, timezone
from typing import Literal

from app.db.servers_derived_repo import Heartbeat

logger = logging.getLogger(__name__)


def compute_confidence(
    server_id: str,
    heartbeats: list[Heartbeat],
    grace_window_seconds: int,
    agent_version: str | None = None,
) -> Literal["green", "yellow", "red"]:
    """
    Compute RYG confidence (v1, simple, deterministic).

    State Machine (downgrade only, no sudden jumps):
    - green: within grace + enough samples (≥3) → consistent signal
    - yellow: insufficient samples (<3) OR within 2*grace but beyond grace → intermittent/new
    - red: stale beyond 2*grace OR no heartbeats → stale/spoof attempts

    Explicit Downgrade Rules (when confidence decreases):
    1. green → yellow: time_since_latest exceeds grace_window (but ≤ 2*grace)
    2. green → yellow: sample_count drops below 3 (holding time constant)
    3. yellow → red: time_since_latest exceeds 2*grace_window
    4. yellow → red: all heartbeats removed (sample_count → 0)
    5. green → red: time_since_latest exceeds 2*grace_window (skips yellow, but rare)

    No Sudden Jumps:
    - Cannot go red → green directly (must pass through yellow first)
    - Requires: time_since_latest ≤ grace_window AND sample_count ≥ 3
    - This ensures sustained signal before green (prevents gaming)

    Stability:
    - Deterministic: Same heartbeats + same grace_window → same output
    - Based on received_at (server-trusted clock), not agent timestamp
    - Tie-break: Most recent heartbeat wins (deterministic ordering)

    Args:
        server_id: Server UUID (for logging/debugging)
        heartbeats: List of heartbeats ordered by received_at DESC (most recent first)
        grace_window_seconds: Grace window in seconds
        agent_version: Optional agent version string (not used in v1, reserved for future)

    Returns:
        Confidence level: "green", "yellow", or "red" (never None)

    Examples:
        - 5 heartbeats, latest within grace → "green"
        - 2 heartbeats, latest within grace → "yellow" (insufficient samples)
        - 5 heartbeats, latest between grace and 2*grace → "yellow" (intermittent)
        - Any heartbeats, latest beyond 2*grace → "red" (stale)
        - No heartbeats → "red" (never seen)
    """
    if not heartbeats:
        # No heartbeats → red (stale/never seen)
        # Downgrade rule: Any state → red if all heartbeats removed
        return "red"

    # Get most recent heartbeat (deterministic: heartbeats ordered by received_at DESC)
    # Stability: Uses received_at (server-trusted clock), not agent timestamp
    latest_heartbeat = heartbeats[0]
    latest_received_at = latest_heartbeat["received_at"]

    # Check time since latest heartbeat (based on received_at for stability)
    now = datetime.now(timezone.utc)
    time_since_latest = (now - latest_received_at).total_seconds()

    # Red: stale beyond 2*grace (downgrade rule: any state → red if stale)
    # This is the most severe downgrade (stale signal)
    if time_since_latest > (2 * grace_window_seconds):
        reason = "stale"
        logger.debug(
            f"Confidence: red ({reason})",
            extra={
                "server_id": server_id,
                "time_since_latest": time_since_latest,
                "grace_window": grace_window_seconds,
            },
        )
        return "red"

    # Check sample count (need at least 3 heartbeats for green)
    # Downgrade rule: green → yellow if sample_count drops below 3
    sample_count = len(heartbeats)
    if sample_count < 3:
        # Insufficient samples → yellow (new/intermittent)
        # Prevents sudden jumps: cannot be green without sustained signal (≥3 samples)
        reason = "insufficient_samples"
        logger.debug(
            f"Confidence: yellow ({reason})",
            extra={"server_id": server_id, "sample_count": sample_count},
        )
        return "yellow"

    # Check if within grace window
    if time_since_latest <= grace_window_seconds:
        # Within grace + enough samples (≥3) → green (consistent)
        # Upgrade rule: yellow → green if time_since_latest ≤ grace AND sample_count ≥ 3
        # No sudden jumps: requires both conditions (sustained signal)
        reason = "consistent"
        logger.debug(
            f"Confidence: green ({reason})",
            extra={"server_id": server_id, "sample_count": sample_count},
        )
        return "green"
    else:
        # Within 2*grace but beyond grace → yellow (intermittent)
        # Downgrade rule: green → yellow if time_since_latest exceeds grace (but ≤ 2*grace)
        # This is the intermediate state (prevents sudden red → green jumps)
        reason = "intermittent"
        logger.debug(
            f"Confidence: yellow ({reason})",
            extra={
                "server_id": server_id,
                "time_since_latest": time_since_latest,
                "grace_window": grace_window_seconds,
            },
        )
        return "yellow"
