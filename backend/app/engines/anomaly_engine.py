"""
Anomaly detection engine.

Detects impossible or suspicious player count changes that indicate gaming/abuse.
Computed as derived metrics (stored alongside other derived fields).
"""

from datetime import datetime, timedelta, timezone

from app.db.servers_derived_repo import Heartbeat


def detect_player_spike_anomaly(
    server_id: str,
    heartbeats: list[Heartbeat],
    current_anomaly_flag: bool | None,
    last_anomaly_at: datetime | None,
    anomaly_decay_minutes: int = 30,
) -> tuple[bool, datetime | None]:
    """
    Detect impossible or suspicious player count spikes.
    
    Anomaly Detection Rules:
    1. Impossible spikes: 0 → high (e.g., 70) → 0 in < 60 seconds
       - Indicates fake player counts (can't fill/empty server that fast)
    2. Suspicious spikes: Sudden large increases (> 50% capacity jump in < 60 seconds)
       - May indicate gaming (artificially inflating player counts)
    
    Decay Strategy (Sprint 5):
    - Clear anomaly flag after T minutes (default 30) without new spikes
    - Based on `received_at` timestamps (doesn't depend on heartbeat frequency)
    - Prevents permanent scars on servers
    
    Args:
        server_id: Server UUID (for logging/debugging)
        heartbeats: List of heartbeats ordered by received_at DESC (most recent first)
        current_anomaly_flag: Current anomaly flag state (from previous computation)
        last_anomaly_at: Timestamp of last detected anomaly (for decay)
        anomaly_decay_minutes: Minutes without spikes before clearing flag (default 30)
        
    Returns:
        Tuple of (anomaly_players_spike: bool, last_anomaly_at: datetime | None)
        - anomaly_players_spike: True if anomaly detected, False otherwise
        - last_anomaly_at: Timestamp of most recent anomaly, or None if no anomaly
    """
    if not heartbeats or len(heartbeats) < 2:
        # Need at least 2 heartbeats to detect spikes
        # If no anomaly detected and enough time has passed, clear flag
        if current_anomaly_flag and last_anomaly_at:
            now = datetime.now(timezone.utc)
            decay_threshold = last_anomaly_at + timedelta(minutes=anomaly_decay_minutes)
            if now >= decay_threshold:
                return False, None
        return current_anomaly_flag or False, last_anomaly_at
    
    # Check for impossible spikes: 0 → high → 0 in < 60 seconds
    # Heartbeats are ordered DESC (most recent first), so:
    # hb[0] = most recent (newest timestamp), hb[1] = previous (older), hb[2] = oldest
    # Chronologically: hb[2] (oldest) → hb[1] (middle) → hb[0] (newest)
    now = datetime.now(timezone.utc)
    anomaly_detected = False
    latest_anomaly_time = last_anomaly_at
    
    # Check for rapid 0 → high → 0 pattern
    # Chronological pattern: oldest (0) → middle (high) → newest (0) in < 60 seconds
    for i in range(len(heartbeats) - 2):
        hb_newest = heartbeats[i]  # Most recent (newest timestamp)
        hb_middle = heartbeats[i + 1]  # Middle (older)
        hb_oldest = heartbeats[i + 2]  # Oldest
        
        players_newest = hb_newest.get("players_current")
        players_middle = hb_middle.get("players_current")
        players_oldest = hb_oldest.get("players_current")
        
        # Skip if any players_current is None
        if players_newest is None or players_middle is None or players_oldest is None:
            continue
        
        received_newest = hb_newest["received_at"]
        received_middle = hb_middle["received_at"]
        received_oldest = hb_oldest["received_at"]
        
        # Calculate time deltas (chronologically: oldest → middle → newest)
        time_delta_oldest_to_middle = (received_middle - received_oldest).total_seconds()
        time_delta_middle_to_newest = (received_newest - received_middle).total_seconds()
        total_time = time_delta_oldest_to_middle + time_delta_middle_to_newest
        
        # Rule 1: Impossible spike - 0 → high → 0 in < 60 seconds
        # Chronological: oldest (0) → middle (high) → newest (0)
        if players_oldest == 0 and players_middle >= 50 and players_newest == 0 and total_time < 60:
            anomaly_detected = True
            latest_anomaly_time = received_newest
            break
        
        # Rule 2: Suspicious spike - sudden large increase (> 50% capacity jump in < 60 seconds)
        # Check if middle → newest is a large jump (chronologically: middle is older, newest is newer)
        if players_middle > 0 and players_newest > players_middle:
            # Calculate percentage increase
            increase = players_newest - players_middle
            capacity = hb_newest.get("players_capacity") or 70  # Default capacity if unknown
            percent_increase = (increase / capacity) * 100
            
            # If > 50% capacity jump in < 60 seconds, flag as suspicious
            if percent_increase > 50 and time_delta_middle_to_newest < 60:
                anomaly_detected = True
                latest_anomaly_time = received_newest
                break
        
        # Rule 3: Impossible drop - high → 0 in < 10 seconds (too fast for real server)
        # Chronological: middle (high) → newest (0)
        if players_middle >= 30 and players_newest == 0 and time_delta_middle_to_newest < 10:
            anomaly_detected = True
            latest_anomaly_time = received_newest
            break
    
    # Apply decay: if anomaly was detected before but enough time has passed, clear it
    if not anomaly_detected and current_anomaly_flag and last_anomaly_at:
        decay_threshold = last_anomaly_at + timedelta(minutes=anomaly_decay_minutes)
        if now >= decay_threshold:
            return False, None
    
    # Return anomaly state
    if anomaly_detected:
        return True, latest_anomaly_time
    elif current_anomaly_flag:
        # Keep existing flag until decay threshold
        return True, last_anomaly_at
    else:
        return False, None
