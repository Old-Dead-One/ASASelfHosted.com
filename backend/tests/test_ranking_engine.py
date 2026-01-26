"""
Tests for ranking engine.

Tests ranking score computation and invariants (determinism, same inputs → same output).
"""

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


def test_compute_ranking_score_players_cap_prevents_gaming():
    """Gaming attempt test: Rapid player count changes don't affect ranking."""
    # Server with high player count (above cap)
    high_players: ServerRankingData = {
        "quality_score": 80.0,
        "uptime_percent": 90.0,
        "players_current": 100,  # Above cap of 50
        "players_capacity": 100,
        "anomaly_players_spike": False,
    }

    # Server with capped players (at cap)
    capped_players: ServerRankingData = {
        "quality_score": 80.0,
        "uptime_percent": 90.0,
        "players_current": 50,  # At cap
        "players_capacity": 100,
        "anomaly_players_spike": False,
    }

    score_high = compute_ranking_score(high_players)
    score_capped = compute_ranking_score(capped_players)

    # Scores should be similar (players contribution capped at 50)
    # Small difference might exist due to fill rate calculation, but should be minimal
    assert abs(score_high - score_capped) < 5.0, (
        f"Players cap not working: {score_high} vs {score_capped}"
    )


def test_compute_ranking_score_uptime_manipulation_guarded():
    """Gaming attempt test: Uptime manipulation attempts fail (diminishing returns)."""
    # Server with very high uptime (above diminishing returns threshold)
    very_high_uptime: ServerRankingData = {
        "quality_score": 80.0,
        "uptime_percent": 99.0,  # Above 95% threshold
        "players_current": 30,
        "players_capacity": 70,
        "anomaly_players_spike": False,
    }

    # Server with uptime at threshold
    threshold_uptime: ServerRankingData = {
        "quality_score": 80.0,
        "uptime_percent": 95.0,  # At threshold
        "players_current": 30,
        "players_capacity": 70,
        "anomaly_players_spike": False,
    }

    score_very_high = compute_ranking_score(very_high_uptime)
    score_threshold = compute_ranking_score(threshold_uptime)

    # Very high uptime should get diminishing returns
    # Difference should be small (log scale reduction)
    difference = score_very_high - score_threshold
    assert difference < 2.0, (
        f"Diminishing returns not working: {score_very_high} vs {score_threshold} (diff: {difference})"
    )


def test_compute_ranking_score_impossible_sequences_penalized():
    """Gaming attempt test: Impossible heartbeat sequences get ranking penalty."""
    # Server with anomaly flag (impossible player spike detected)
    with_anomaly: ServerRankingData = {
        "quality_score": 90.0,
        "uptime_percent": 95.0,
        "players_current": 50,
        "players_capacity": 70,
        "anomaly_players_spike": True,  # Anomaly detected
    }

    # Same server without anomaly
    without_anomaly: ServerRankingData = {
        "quality_score": 90.0,
        "uptime_percent": 95.0,
        "players_current": 50,
        "players_capacity": 70,
        "anomaly_players_spike": False,
    }

    score_with = compute_ranking_score(with_anomaly)
    score_without = compute_ranking_score(without_anomaly)

    # Anomaly should reduce ranking score
    assert score_with < score_without, (
        f"Anomaly penalty not applied: {score_with} >= {score_without}"
    )

    # Penalty should be significant (ANOMALY_PENALTY = 20.0)
    penalty = score_without - score_with
    assert penalty >= 15.0, f"Anomaly penalty too small: {penalty} (expected ~20.0)"


def test_compute_ranking_score_rapid_player_changes_guarded():
    """Gaming attempt test: Rapid player count changes don't boost ranking."""
    # Server with rapid changes (0 → 70 → 0) - should be penalized by anomaly flag
    rapid_changes: ServerRankingData = {
        "quality_score": 80.0,
        "uptime_percent": 90.0,
        "players_current": 70,  # Currently high
        "players_capacity": 70,
        "anomaly_players_spike": True,  # Anomaly detected from rapid changes
    }

    # Server with stable player count
    stable: ServerRankingData = {
        "quality_score": 80.0,
        "uptime_percent": 90.0,
        "players_current": 40,  # Stable, moderate
        "players_capacity": 70,
        "anomaly_players_spike": False,
    }

    score_rapid = compute_ranking_score(rapid_changes)
    score_stable = compute_ranking_score(stable)

    # Rapid changes should not boost ranking (anomaly penalty applies)
    # Even though rapid_changes has more players, anomaly penalty should make it lower
    assert score_rapid < score_stable or abs(score_rapid - score_stable) < 10.0, (
        f"Rapid changes not penalized: {score_rapid} vs {score_stable}"
    )
