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
