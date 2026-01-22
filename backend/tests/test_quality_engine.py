"""
Tests for quality engine.

Tests quality score computation.
"""

import pytest

from app.db.servers_derived_repo import Heartbeat
from app.engines.quality_engine import compute_quality_score


def test_compute_quality_score_no_uptime():
    """Test that no uptime data returns None."""
    result = compute_quality_score(
        uptime_percent=None,
        players_current=None,
        players_capacity=None,
        confidence="green",
        heartbeats=[]
    )
    assert result is None


def test_compute_quality_score_high_uptime_green():
    """Test that high uptime with green confidence gives high quality."""
    result = compute_quality_score(
        uptime_percent=95.0,
        players_current=50,
        players_capacity=70,
        confidence="green",
        heartbeats=[]
    )
    
    assert result is not None
    assert result > 80.0  # Should be high with good uptime and activity


def test_compute_quality_score_red_confidence_penalty():
    """Test that red confidence reduces quality score."""
    result_green = compute_quality_score(
        uptime_percent=90.0,
        players_current=50,
        players_capacity=70,
        confidence="green",
        heartbeats=[]
    )
    
    result_red = compute_quality_score(
        uptime_percent=90.0,
        players_current=50,
        players_capacity=70,
        confidence="red",
        heartbeats=[]
    )
    
    assert result_green is not None
    assert result_red is not None
    assert result_green > result_red  # Green should score higher than red


def test_compute_quality_score_player_activity():
    """Test that player activity affects quality score."""
    result_high_activity = compute_quality_score(
        uptime_percent=90.0,
        players_current=65,  # High fill rate
        players_capacity=70,
        confidence="green",
        heartbeats=[]
    )
    
    result_low_activity = compute_quality_score(
        uptime_percent=90.0,
        players_current=5,  # Low fill rate
        players_capacity=70,
        confidence="green",
        heartbeats=[]
    )
    
    assert result_high_activity is not None
    assert result_low_activity is not None
    assert result_high_activity > result_low_activity  # High activity should score higher


def test_compute_quality_score_clamped_0_100():
    """Test that quality score is clamped to 0-100."""
    # Test with extreme values
    result = compute_quality_score(
        uptime_percent=150.0,  # Invalid > 100
        players_current=1000,  # Extreme
        players_capacity=70,
        confidence="green",
        heartbeats=[]
    )
    
    # Should still be clamped
    if result is not None:
        assert 0.0 <= result <= 100.0
