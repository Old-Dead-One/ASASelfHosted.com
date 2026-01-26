"""
Tests for confidence engine.

Tests RYG confidence computation.
"""

from datetime import datetime, timedelta, timezone

from app.db.servers_derived_repo import Heartbeat
from app.engines.confidence_engine import compute_confidence


def test_compute_confidence_no_heartbeats():
    """Test that no heartbeats returns red."""
    confidence = compute_confidence(
        "server-1", [], grace_window_seconds=600, agent_version=None
    )
    assert confidence == "red"


def test_compute_confidence_stale_beyond_2x_grace():
    """Test that stale beyond 2*grace returns red."""
    now = datetime.now(timezone.utc)
    stale_time = now - timedelta(seconds=1500)  # 25 minutes ago (beyond 2*600=1200s)

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

    confidence = compute_confidence(
        "server-1", heartbeats, grace_window_seconds=600, agent_version=None
    )
    assert confidence == "red"


def test_compute_confidence_insufficient_samples():
    """Test that insufficient samples (< 3) returns yellow."""
    now = datetime.now(timezone.utc)
    recent_time = now - timedelta(seconds=300)  # 5 minutes ago (within grace)

    heartbeats: list[Heartbeat] = [
        {
            "id": f"hb-{i}",
            "server_id": "server-1",
            "received_at": recent_time,
            "status": "online",
            "map_name": None,
            "players_current": None,
            "players_capacity": None,
            "agent_version": None,
            "key_version": None,
        }
        for i in range(2)  # Only 2 heartbeats (< 3)
    ]

    confidence = compute_confidence(
        "server-1", heartbeats, grace_window_seconds=600, agent_version=None
    )
    assert confidence == "yellow"


def test_compute_confidence_green():
    """Test that within grace + enough samples returns green."""
    now = datetime.now(timezone.utc)
    recent_time = now - timedelta(seconds=300)  # 5 minutes ago (within grace)

    heartbeats: list[Heartbeat] = [
        {
            "id": f"hb-{i}",
            "server_id": "server-1",
            "received_at": recent_time,
            "status": "online",
            "map_name": None,
            "players_current": None,
            "players_capacity": None,
            "agent_version": None,
            "key_version": None,
        }
        for i in range(5)  # 5 heartbeats (>= 3)
    ]

    confidence = compute_confidence(
        "server-1", heartbeats, grace_window_seconds=600, agent_version=None
    )
    assert confidence == "green"


def test_compute_confidence_yellow_within_2x_grace():
    """Test that within 2*grace but beyond grace returns yellow."""
    now = datetime.now(timezone.utc)
    intermediate_time = now - timedelta(
        seconds=900
    )  # 15 minutes ago (within 2*600=1200s, beyond 600s)

    heartbeats: list[Heartbeat] = [
        {
            "id": f"hb-{i}",
            "server_id": "server-1",
            "received_at": intermediate_time,
            "status": "online",
            "map_name": None,
            "players_current": None,
            "players_capacity": None,
            "agent_version": None,
            "key_version": None,
        }
        for i in range(5)  # Enough samples
    ]

    confidence = compute_confidence(
        "server-1", heartbeats, grace_window_seconds=600, agent_version=None
    )
    assert confidence == "yellow"
