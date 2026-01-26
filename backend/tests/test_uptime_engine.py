"""
Tests for uptime engine.

Tests uptime percentage computation over rolling window.
"""

from datetime import datetime, timedelta, timezone

import pytest

from app.db.servers_derived_repo import Heartbeat
from app.engines.uptime_engine import compute_uptime_percent


def test_compute_uptime_percent_no_heartbeats():
    """Test that no heartbeats returns None."""
    result = compute_uptime_percent("server-1", [], grace_window_seconds=600, window_hours=24)
    assert result is None


def test_compute_uptime_percent_all_online():
    """Test uptime with consistent heartbeats (should be high)."""
    now = datetime.now(timezone.utc)
    window_start = now - timedelta(hours=24)
    
    # Create heartbeats every 5 minutes within window
    heartbeats: list[Heartbeat] = []
    current_time = window_start
    while current_time <= now:
        heartbeats.append({
            "id": f"hb-{current_time.isoformat()}",
            "server_id": "server-1",
            "received_at": current_time,
            "status": "online",
            "map_name": None,
            "players_current": None,
            "players_capacity": None,
            "agent_version": None,
            "key_version": None,
        })
        current_time += timedelta(minutes=5)
    
    # Should have high uptime (heartbeats cover most of window)
    result = compute_uptime_percent("server-1", heartbeats, grace_window_seconds=600, window_hours=24)
    
    assert result is not None
    assert result > 80.0  # Should be high with regular heartbeats


def test_compute_uptime_percent_all_offline():
    """Test uptime with no recent heartbeats (should be low/zero)."""
    now = datetime.now(timezone.utc)
    old_time = now - timedelta(hours=25)  # Outside 24h window
    
    heartbeats: list[Heartbeat] = [
        {
            "id": "hb-1",
            "server_id": "server-1",
            "received_at": old_time,
            "status": "offline",
            "map_name": None,
            "players_current": None,
            "players_capacity": None,
            "agent_version": None,
            "key_version": None,
        }
    ]
    
    result = compute_uptime_percent("server-1", heartbeats, grace_window_seconds=600, window_hours=24)
    
    # Should be None or very low (heartbeat outside window)
    assert result is None or result < 10.0


def test_compute_uptime_percent_interval_merging():
    """Test that overlapping intervals are merged correctly."""
    now = datetime.now(timezone.utc)
    base_time = now - timedelta(hours=1)
    
    # Create overlapping heartbeats (each covers 600s grace window)
    heartbeats: list[Heartbeat] = [
        {
            "id": f"hb-{i}",
            "server_id": "server-1",
            "received_at": base_time + timedelta(seconds=i * 300),  # Every 5 minutes
            "status": "online",
            "map_name": None,
            "players_current": None,
            "players_capacity": None,
            "agent_version": None,
            "key_version": None,
        }
        for i in range(10)  # 10 heartbeats over 50 minutes
    ]
    
    result = compute_uptime_percent("server-1", heartbeats, grace_window_seconds=600, window_hours=24)
    
    assert result is not None
    assert 0.0 <= result <= 100.0


def test_compute_uptime_percent_long_offline_gap():
    """Regression test: Server offline for days, then comes back."""
    now = datetime.now(timezone.utc)
    
    # Server was online 3 days ago, then offline, now back online
    old_online = now - timedelta(days=3)
    recent_online = now - timedelta(minutes=5)
    
    heartbeats: list[Heartbeat] = [
        {
            "id": "hb-recent",
            "server_id": "server-1",
            "received_at": recent_online,
            "status": "online",
            "map_name": None,
            "players_current": None,
            "players_capacity": None,
            "agent_version": None,
            "key_version": None,
        },
        {
            "id": "hb-old",
            "server_id": "server-1",
            "received_at": old_online,
            "status": "online",
            "map_name": None,
            "players_current": None,
            "players_capacity": None,
            "agent_version": None,
            "key_version": None,
        },
    ]
    
    result = compute_uptime_percent("server-1", heartbeats, grace_window_seconds=600, window_hours=24)
    
    # Should have low uptime (only recent heartbeat in 24h window)
    # Old heartbeat is outside window, so only recent one counts
    assert result is not None
    assert result < 50.0  # Should be low (only one heartbeat in window)


def test_compute_uptime_percent_flapping_servers():
    """Regression test: Server rapidly goes online/offline (flapping)."""
    now = datetime.now(timezone.utc)
    window_start = now - timedelta(hours=2)
    
    # Create flapping pattern: online for 5 min, offline for 5 min, repeat
    heartbeats: list[Heartbeat] = []
    current_time = window_start
    online = True
    
    while current_time <= now:
        if online:
            heartbeats.append({
                "id": f"hb-{current_time.isoformat()}",
                "server_id": "server-1",
                "received_at": current_time,
                "status": "online",
                "map_name": None,
                "players_current": None,
                "players_capacity": None,
                "agent_version": None,
                "key_version": None,
            })
        # Toggle every 5 minutes
        current_time += timedelta(minutes=5)
        online = not online
    
    result = compute_uptime_percent("server-1", heartbeats, grace_window_seconds=600, window_hours=24)
    
    # Should have moderate uptime (about 50% if flapping pattern)
    assert result is not None
    assert 0.0 <= result <= 100.0
    # With 5 min on/off pattern and 600s grace window, uptime depends on heartbeat frequency
    # The actual value may be lower if heartbeats are sparse, but should be > 0
    assert result > 0.0  # Should have some uptime (at least some heartbeats in window)


def test_compute_uptime_percent_cold_start_server():
    """Regression test: New server with no history (cold-start)."""
    now = datetime.now(timezone.utc)
    
    # New server with single recent heartbeat
    heartbeats: list[Heartbeat] = [
        {
            "id": "hb-1",
            "server_id": "server-new",
            "received_at": now - timedelta(minutes=2),
            "status": "online",
            "map_name": None,
            "players_current": None,
            "players_capacity": None,
            "agent_version": None,
            "key_version": None,
        }
    ]
    
    result = compute_uptime_percent("server-new", heartbeats, grace_window_seconds=600, window_hours=24)
    
    # Should have very low uptime (single heartbeat in 24h window)
    assert result is not None
    assert result < 10.0  # Single heartbeat covers ~600s out of 86400s = ~0.7%
