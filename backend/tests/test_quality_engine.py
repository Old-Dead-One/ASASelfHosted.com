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


def test_compute_quality_score_monotonic_uptime():
    """Test that quality decreases when uptime decreases (monotonic behavior)."""
    result_high = compute_quality_score(
        uptime_percent=95.0,
        players_current=50,
        players_capacity=70,
        confidence="green",
        heartbeats=[]
    )
    
    result_low = compute_quality_score(
        uptime_percent=50.0,  # Lower uptime
        players_current=50,   # Same activity
        players_capacity=70,
        confidence="green",   # Same confidence
        heartbeats=[]
    )
    
    assert result_high is not None
    assert result_low is not None
    assert result_high > result_low  # Higher uptime → higher quality


def test_compute_quality_score_monotonic_confidence():
    """Test that quality decreases when confidence degrades (monotonic behavior)."""
    result_green = compute_quality_score(
        uptime_percent=90.0,
        players_current=50,
        players_capacity=70,
        confidence="green",
        heartbeats=[]
    )
    
    result_yellow = compute_quality_score(
        uptime_percent=90.0,  # Same uptime
        players_current=50,    # Same activity
        players_capacity=70,
        confidence="yellow",   # Lower confidence
        heartbeats=[]
    )
    
    result_red = compute_quality_score(
        uptime_percent=90.0,  # Same uptime
        players_current=50,   # Same activity
        players_capacity=70,
        confidence="red",      # Lowest confidence
        heartbeats=[]
    )
    
    assert result_green is not None
    assert result_yellow is not None
    assert result_red is not None
    assert result_green > result_yellow > result_red  # Monotonic: green > yellow > red


def test_compute_quality_score_monotonic_activity():
    """Test that quality decreases when player activity decreases (monotonic behavior)."""
    result_high_activity = compute_quality_score(
        uptime_percent=90.0,
        players_current=65,  # High fill rate
        players_capacity=70,
        confidence="green",
        heartbeats=[]
    )
    
    result_low_activity = compute_quality_score(
        uptime_percent=90.0,  # Same uptime
        players_current=5,    # Low fill rate
        players_capacity=70,
        confidence="green",    # Same confidence
        heartbeats=[]
    )
    
    assert result_high_activity is not None
    assert result_low_activity is not None
    assert result_high_activity > result_low_activity  # Higher activity → higher quality


def test_compute_quality_score_unknown_behavior():
    """Test that None is returned when uptime_percent is None (unknown behavior)."""
    # Test various combinations - all should return None if uptime is None
    result1 = compute_quality_score(
        uptime_percent=None,
        players_current=50,
        players_capacity=70,
        confidence="green",
        heartbeats=[]
    )
    assert result1 is None
    
    result2 = compute_quality_score(
        uptime_percent=None,
        players_current=None,
        players_capacity=None,
        confidence="green",
        heartbeats=[]
    )
    assert result2 is None


def test_compute_quality_score_bounded_outputs():
    """Test that all outputs are bounded to [0, 100] or None (property test)."""
    # Test various input combinations
    test_cases = [
        (0.0, 0, 70, "red"),
        (100.0, 70, 70, "green"),
        (50.0, 35, 70, "yellow"),
        (25.0, 10, 70, "red"),
        (75.0, 50, 70, "green"),
    ]
    
    for uptime, players, capacity, confidence in test_cases:
        result = compute_quality_score(
            uptime_percent=uptime,
            players_current=players,
            players_capacity=capacity,
            confidence=confidence,
            heartbeats=[]
        )
        # Property: output is either None or in [0, 100]
        assert result is None or (0.0 <= result <= 100.0)
