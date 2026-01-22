"""
Uptime engine.

Computes uptime percentage over rolling window.
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
    window_hours: int = 24
) -> float | None:
    """
    Compute uptime percentage over rolling window.
    
    Algorithm:
    - Treat each heartbeat as online coverage for grace_window_seconds
    - Merge overlapping intervals
    - Compute: (minutes_online / total_minutes_in_window) * 100
    
    Start with 24h window only (Sprint 4).
    
    Args:
        server_id: Server UUID (for logging/debugging)
        heartbeats: List of heartbeats ordered by received_at DESC
        grace_window_seconds: Grace window in seconds (coverage per heartbeat)
        window_hours: Rolling window size in hours (default 24)
        
    Returns:
        Uptime percentage (0-100) or None if no heartbeats
    """
    if not heartbeats:
        return None
    
    # Calculate window boundaries
    now = datetime.now(timezone.utc)
    window_start = now - timedelta(hours=window_hours)
    
    # Filter heartbeats within window
    window_heartbeats = [
        hb for hb in heartbeats
        if hb["received_at"] >= window_start
    ]
    
    if not window_heartbeats:
        return None
    
    # Create intervals: each heartbeat covers grace_window_seconds
    intervals: list[TimeInterval] = []
    for hb in window_heartbeats:
        received_at = hb["received_at"]
        interval_start = received_at
        interval_end = received_at + timedelta(seconds=grace_window_seconds)
        
        # Clamp to window boundaries
        interval_start = max(interval_start, window_start)
        interval_end = min(interval_end, now)
        
        if interval_start < interval_end:
            intervals.append(TimeInterval(interval_start, interval_end))
    
    if not intervals:
        return None
    
    # Sort intervals by start time
    intervals.sort(key=lambda x: x.start)
    
    # Merge overlapping intervals
    merged: list[TimeInterval] = []
    current = intervals[0]
    
    for interval in intervals[1:]:
        if interval.start <= current.end:
            # Overlapping - merge
            current = TimeInterval(current.start, max(current.end, interval.end))
        else:
            # Non-overlapping - save current and start new
            merged.append(current)
            current = interval
    
    merged.append(current)
    
    # Calculate total online minutes
    total_online_seconds = sum(
        (interval.end - interval.start).total_seconds()
        for interval in merged
    )
    total_online_minutes = total_online_seconds / 60.0
    
    # Calculate total window minutes
    total_window_minutes = (now - window_start).total_seconds() / 60.0
    
    if total_window_minutes == 0:
        return None
    
    # Compute uptime percentage
    uptime_percent = (total_online_minutes / total_window_minutes) * 100.0
    
    # Clamp to 0-100
    uptime_percent = max(0.0, min(100.0, uptime_percent))
    
    return uptime_percent
