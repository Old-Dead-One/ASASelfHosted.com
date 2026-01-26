"""
Ranking engine.

Computes ranking scores for servers based on derived metrics.
Applies anti-gaming guards to prevent manipulation.

Ranking is computed in Python (not SQL) for:
- Testability (hermetic tests)
- Fast iteration (easy to adjust formula)
- Centralized logic (single source of truth)

Placement: Called from repository layer (not routes).
This preserves "no business logic in routes" principle.

Invariants:
- Output is always a float (ranking score, higher = better rank)
- Stability: Same inputs → same output (deterministic, no randomness)
- Reads derived fields only (quality_score, uptime_percent, players_current, anomaly flags)
- Does NOT read raw heartbeat history (uses pre-computed derived metrics)
- Anti-gaming: Guards prevent manipulation (capped players, diminishing returns, anomaly penalties)
"""

from typing import TypedDict


class ServerRankingData(TypedDict):
    """Server data for ranking computation (derived fields only)."""

    quality_score: float | None
    uptime_percent: float | None
    players_current: int | None
    players_capacity: int | None
    anomaly_players_spike: bool | None
    # Future: can add more fields (favorite_count, etc.)


def compute_ranking_score(server_data: ServerRankingData) -> float:
    """
    Compute ranking score for a server.

    Ranking Formula (v1, simple):
    ranking_score = (quality_weight * quality_score)
                  + (uptime_weight * normalized_uptime)
                  + (activity_weight * normalized_players)
                  - (anomaly_penalty if anomaly detected)

    Anti-Gaming Guards:
    1. Players cap: players_current contribution capped at threshold (e.g., 50)
    2. Uptime diminishing returns: Uptime > threshold gets diminishing returns
    3. Anomaly penalty: Servers with anomaly flags get ranking penalty

    Args:
        server_data: ServerRankingData with derived fields

    Returns:
        Ranking score (float, higher = better rank)
        Defaults to 0.0 if insufficient data

    Examples:
        - High quality (90), high uptime (95%), high players (60/70), no anomaly → high score
        - High quality (90), high uptime (95%), high players (60/70), anomaly → reduced score
        - Low quality (50), low uptime (60%), low players (10/70), no anomaly → low score
    """
    # Weights (v1 simple)
    QUALITY_WEIGHT = 0.5  # 50% weight on quality score
    UPTIME_WEIGHT = 0.3  # 30% weight on uptime
    ACTIVITY_WEIGHT = 0.2  # 20% weight on player activity

    # Anti-gaming thresholds
    PLAYERS_CAP = 50  # Cap players_current contribution at 50 (prevents gaming)
    UPTIME_DIMINISHING_THRESHOLD = 95.0  # Uptime > 95% gets diminishing returns

    # Anomaly penalty
    ANOMALY_PENALTY = 20.0  # Fixed penalty for anomaly flag

    # Initialize components
    quality_component = 0.0
    uptime_component = 0.0
    activity_component = 0.0
    anomaly_penalty = 0.0

    # Quality component (50% of score)
    quality_score = server_data.get("quality_score")
    if quality_score is not None:
        # Clamp quality_score to valid range [0, 100]
        quality_score = max(0.0, min(100.0, quality_score))
        quality_component = QUALITY_WEIGHT * quality_score

    # Uptime component (30% of score, with diminishing returns)
    uptime_percent = server_data.get("uptime_percent")
    if uptime_percent is not None:
        # Clamp uptime_percent to valid range [0, 100]
        uptime_percent = max(0.0, min(100.0, uptime_percent))

        # Diminishing returns: Uptime > threshold gets log-scale reduction
        if uptime_percent > UPTIME_DIMINISHING_THRESHOLD:
            # Apply diminishing returns: log scale above threshold
            # Formula: threshold + log(1 + (uptime - threshold)) * scaling_factor
            import math

            excess = uptime_percent - UPTIME_DIMINISHING_THRESHOLD
            # Scale excess through log to reduce impact
            # Max excess is 5% (100 - 95), so log(1 + 5) ≈ 1.79
            # Normalize to keep result in [0, 5] range, then scale
            normalized_excess = (
                math.log(1 + excess) / math.log(6) * 5.0
            )  # Normalize to [0, 5]
            effective_uptime = UPTIME_DIMINISHING_THRESHOLD + normalized_excess
        else:
            effective_uptime = uptime_percent

        uptime_component = UPTIME_WEIGHT * effective_uptime

    # Activity component (20% of score, with players cap)
    players_current = server_data.get("players_current")
    players_capacity = server_data.get("players_capacity")

    if players_current is not None and players_current > 0:
        # Anti-gaming guard: Cap players_current contribution
        capped_players = min(players_current, PLAYERS_CAP)

        # Normalize to fill rate [0, 1]
        if players_capacity is not None and players_capacity > 0:
            fill_rate = min(1.0, max(0.0, capped_players / players_capacity))
        else:
            # No capacity - use default capacity estimate (70)
            fill_rate = min(1.0, max(0.0, capped_players / 70.0))

        # Scale to [0, 100] then apply weight
        activity_component = ACTIVITY_WEIGHT * (fill_rate * 100.0)

    # Anomaly penalty (subtract from score if anomaly detected)
    anomaly_flag = server_data.get("anomaly_players_spike")
    if anomaly_flag is True:
        anomaly_penalty = ANOMALY_PENALTY

    # Sum components and subtract penalty
    ranking_score = (
        quality_component + uptime_component + activity_component - anomaly_penalty
    )

    # Ensure non-negative (penalty can't make score negative)
    ranking_score = max(0.0, ranking_score)

    return ranking_score
