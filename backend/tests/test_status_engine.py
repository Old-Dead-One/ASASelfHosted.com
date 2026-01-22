"""
Tests for status engine.

Tests effective_status computation from heartbeat history.
"""

from datetime import datetime, timedelta, timezone

import pytest

from app.db.servers_derived_repo import Heartbeat
from app.engines.status_engine import compute_effective_status


def test_compute_effective_status_no_heartbeats():
    """Test that no heartbeats returns unknown."""
    status, last_seen = compute_effective_status("server-1", [], grace_window_seconds=600)
    
    assert status == "unknown"
    assert last_seen is None


def test_compute_effective_status_recent_heartbeat():
    """Test that recent heartbeat within grace window returns online."""
    now = datetime.now(timezone.utc)
    recent_time = now - timedelta(seconds=300)  # 5 minutes ago (within 10 min grace)
    
    heartbeats: list[Heartbeat] = [
        {
            "id": "hb-1",
            "server_id": "server-1",
            "received_at": recent_time,
            "status": "online",
            "map_name": None,
            "players_current": None,
            "players_capacity": None,
            "agent_version": None,
            "key_version": None,
        }
    ]
    
    status, last_seen = compute_effective_status("server-1", heartbeats, grace_window_seconds=600)
    
    assert status == "online"
    assert last_seen == recent_time


def test_compute_effective_status_stale_heartbeat():
    """Test that stale heartbeat beyond grace window returns offline."""
    now = datetime.now(timezone.utc)
    stale_time = now - timedelta(seconds=1200)  # 20 minutes ago (beyond 10 min grace)
    
    heartbeats: list[Heartbeat] = [
        {
            "id": "hb-1",
            "server_id": "server-1",
            "received_at": stale_time,
            "status": "online",
            "map_name": None,
            "players_current": None,
            "players_capacity": None,
            "agent_version": None,
            "key_version": None,
        }
    ]
    
    status, last_seen = compute_effective_status("server-1", heartbeats, grace_window_seconds=600)
    
    assert status == "offline"
    assert last_seen == stale_time


def test_compute_effective_status_uses_most_recent():
    """Test that status uses the most recent heartbeat."""
    now = datetime.now(timezone.utc)
    recent_time = now - timedelta(seconds=300)  # 5 minutes ago
    old_time = now - timedelta(seconds=1200)  # 20 minutes ago
    
    heartbeats: list[Heartbeat] = [
        {
            "id": "hb-1",
            "server_id": "server-1",
            "received_at": recent_time,  # Most recent first
            "status": "online",
            "map_name": None,
            "players_current": None,
            "players_capacity": None,
            "agent_version": None,
            "key_version": None,
        },
        {
            "id": "hb-2",
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
    
    status, last_seen = compute_effective_status("server-1", heartbeats, grace_window_seconds=600)
    
    # Should use most recent (recent_time, within grace)
    assert status == "online"
    assert last_seen == recent_time
