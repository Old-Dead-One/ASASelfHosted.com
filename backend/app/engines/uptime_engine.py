"""
Uptime engine.

Computes uptime percentage over rolling window.
Uses received_at (server-trusted clock) for liveness calculation.

Invariants:
- Output is always in range [0.0, 100.0] or None (clamped)
- Returns None if no heartbeats in window (insufficient data)
- Stability: Same inputs → same output (deterministic, no randomness)
- Based on received_at (not agent-reported timestamp) for server-trusted clock
- Tie-break ordering: Deterministic interval merging (sorted by start time)
"""

from datetime import datetime, timedelta, timezone
from typing import NamedTuple

from app.db.servers_derived_repo import Heartbeat


class TimeInterval(NamedTuple):
    """Time interval for uptime calculation."""

    start: datetime
    end: datetime


def compute_uptime_percent(
    server_id: str,
    heartbeats: list[Heartbeat],
    grace_window_seconds: int,
    window_hours: int = 24,
) -> float | None:
    """
    Compute uptime percentage over rolling window.

    Algorithm:
    - Treat each heartbeat as online coverage for grace_window_seconds
    - Merge overlapping intervals (deterministic: sorted by start time)
    - Compute: (minutes_online / total_minutes_in_window) * 100

    Known limitation: Gaps between heartbeats (beyond grace_window_seconds) are
    assumed to be offline. This is conservative and may underestimate uptime for
    servers with irregular heartbeat intervals.

    Window Boundaries:
    - Window start: now - window_hours (rolling window)
    - Window end: now (current time)
    - Intervals are clamped to window boundaries (no extrapolation)

    Edge Cases:
    - No heartbeats in window → None (insufficient data)
    - All intervals outside window → None
    - Overlapping intervals → merged (deterministic)
    - Intervals extending beyond window → clamped to window boundaries

    Stability:
    - Deterministic: Same heartbeats + same window → same output
    - Stable across restarts: Uses received_at (server-trusted), not agent timestamp
    - Tie-break: Intervals sorted by start time (deterministic ordering)

    Start with 24h window only (Sprint 4).

    Args:
        server_id: Server UUID (for logging/debugging)
        heartbeats: List of heartbeats ordered by received_at DESC (most recent first)
        grace_window_seconds: Grace window in seconds (coverage per heartbeat)
        window_hours: Rolling window size in hours (default 24)

    Returns:
        Uptime percentage (0-100) or None if no heartbeats in window

    Examples:
        - 24 heartbeats (1 per hour) with 600s grace → ~100% uptime
        - 12 heartbeats (1 per 2 hours) with 600s grace → ~50% uptime
        - No heartbeats in last 24h → None
    """
    if not heartbeats:
        return None

    # Calculate window boundaries (rolling window: now - window_hours to now)
    # Stability: Uses current time (now) for window end, ensuring deterministic calculation
    now = datetime.now(timezone.utc)
    window_start = now - timedelta(hours=window_hours)

    # Filter heartbeats within window (based on received_at, server-trusted clock)
    # Stability: received_at is deterministic (not agent-reported timestamp which may vary)
    window_heartbeats = [hb for hb in heartbeats if hb["received_at"] >= window_start]

    if not window_heartbeats:
        return None

    # Create intervals: each heartbeat covers grace_window_seconds
    # Each heartbeat represents "online" status for grace_window_seconds after received_at
    intervals: list[TimeInterval] = []
    for hb in window_heartbeats:
        received_at = hb["received_at"]  # Server-trusted clock (stability guarantee)
        interval_start = received_at
        interval_end = received_at + timedelta(seconds=grace_window_seconds)

        # Clamp to window boundaries (no extrapolation beyond window)
        interval_start = max(interval_start, window_start)
        interval_end = min(interval_end, now)

        # Only add valid intervals (start < end)
        if interval_start < interval_end:
            intervals.append(TimeInterval(interval_start, interval_end))

    if not intervals:
        return None

    # Sort intervals by start time (tie-break: deterministic ordering)
    # Stability: Same intervals → same sorted order → same merged result
    intervals.sort(key=lambda x: x.start)

    # Merge overlapping intervals (deterministic: sorted order ensures consistent merging)
    merged: list[TimeInterval] = []
    current = intervals[0]

    for interval in intervals[1:]:
        if interval.start <= current.end:
            # Overlapping - merge (extend current interval to cover both)
            current = TimeInterval(current.start, max(current.end, interval.end))
        else:
            # Non-overlapping - save current and start new
            merged.append(current)
            current = interval

    merged.append(current)

    # Calculate total online seconds (sum of all merged intervals)
    total_online_seconds = sum(
        (interval.end - interval.start).total_seconds() for interval in merged
    )
    total_online_minutes = total_online_seconds / 60.0

    # Calculate total window minutes (window size)
    total_window_minutes = (now - window_start).total_seconds() / 60.0

    if total_window_minutes == 0:
        return None

    # Compute uptime percentage: (online_time / total_time) * 100
    uptime_percent = (total_online_minutes / total_window_minutes) * 100.0

    # Clamp to 0-100 (invariant: output must always be in valid range)
    # Defensive programming: theoretically should be ≤ 100, but clamp ensures it
    uptime_percent = max(0.0, min(100.0, uptime_percent))

    return uptime_percent
