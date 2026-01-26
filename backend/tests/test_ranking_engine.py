"""
Tests for ranking engine.

Tests ranking score computation and invariants (determinism, same inputs → same output).
"""

import pytest

from app.engines.ranking import ServerRankingData, compute_ranking_score


def test_compute_ranking_score_same_inputs_same_output():
    """Same inputs → same output (pure function, no oscillation)."""
    data: ServerRankingData = {
        "quality_score": 85.0,
        "uptime_percent": 92.0,
        "players_current": 40,
        "players_capacity": 70,
        "anomaly_players_spike": False,
    }
    a = compute_ranking_score(data)
    b = compute_ranking_score(data)
    assert a == b
    assert isinstance(a, float)
    assert a >= 0.0


def test_compute_ranking_score_anomaly_penalty():
    """Anomaly flag reduces score."""
    base: ServerRankingData = {
        "quality_score": 80.0,
        "uptime_percent": 90.0,
        "players_current": 30,
        "players_capacity": 70,
        "anomaly_players_spike": False,
    }
    without = compute_ranking_score(base)
    base["anomaly_players_spike"] = True
    with_anom = compute_ranking_score(base)
    assert with_anom < without
    assert with_anom >= 0.0


def test_compute_ranking_score_bounded():
    """Output is non-negative and bounded reasonably."""
    data: ServerRankingData = {
        "quality_score": 100.0,
        "uptime_percent": 100.0,
        "players_current": 70,
        "players_capacity": 70,
        "anomaly_players_spike": False,
    }
    score = compute_ranking_score(data)
    assert score >= 0.0
    assert score <= 200.0  # Sanity upper bound
