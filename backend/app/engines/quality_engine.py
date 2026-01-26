"""
Quality engine.

Computes quality score from uptime, player activity, and confidence.
Simple v1 formula - do not over-engineer.

Invariants:
- Output is always in range [0.0, 100.0] or None (clamped)
- Returns None if uptime_percent is None (insufficient data)
- Monotonic behavior: quality decreases when:
  * uptime_percent decreases (holding other factors constant)
  * confidence degrades (green → yellow → red)
  * player activity decreases (holding other factors constant)
- Unknown behavior: Returns None if uptime_percent is None (cannot compute without uptime)
- Stability: Same inputs → same output (pure function, no randomness)
"""

from typing import Literal

from app.db.servers_derived_repo import Heartbeat


def compute_quality_score(
    uptime_percent: float | None,
    players_current: int | None,
    players_capacity: int | None,
    confidence: Literal["green", "yellow", "red"],
    heartbeats: list[Heartbeat],
) -> float | None:
    """
    Compute quality score (0-100).

    Simple v1 formula:
    quality = (uptime_weight * uptime_percent)
           + (activity_weight * normalized_players)
           + (confidence_multiplier based on RYG)

    Do not over-engineer v1. Flapping penalty = 0 in Sprint 4.

    Invariants:
    - Output range: [0.0, 100.0] or None (clamped, never exceeds bounds)
    - Unknown behavior: Returns None if uptime_percent is None (insufficient data)
    - Monotonic decay: Quality decreases when:
      * uptime_percent decreases (ceteris paribus)
      * confidence degrades: green > yellow > red (ceteris paribus)
      * player activity decreases (ceteris paribus)
    - Stability: Deterministic, same inputs → same output (no randomness)

    Args:
        uptime_percent: Uptime percentage (0-100) or None
        players_current: Current player count or None
        players_capacity: Player capacity or None
        confidence: Confidence level ("green", "yellow", "red")
        heartbeats: List of heartbeats (not used in v1, reserved for future)

    Returns:
        Quality score (0-100) or None if insufficient data (uptime_percent is None)

    Examples:
        - High uptime (95%), high activity (65/70), green confidence → ~90+
        - High uptime (95%), low activity (5/70), green confidence → ~70+
        - High uptime (95%), high activity (65/70), red confidence → ~70+
        - No uptime data → None
    """
    # Weights (v1 simple)
    UPTIME_WEIGHT = 0.6  # 60% weight on uptime
    ACTIVITY_WEIGHT = 0.3  # 30% weight on player activity
    CONFIDENCE_BASE = 0.1  # 10% base from confidence

    # Confidence multipliers (monotonic: green > yellow > red)
    CONFIDENCE_MULTIPLIERS = {
        "green": 1.0,  # Full confidence contribution
        "yellow": 0.7,  # Reduced confidence contribution
        "red": 0.3,  # Minimal confidence contribution
    }

    # Unknown behavior: If no uptime data, cannot compute quality
    # This is the primary data requirement - without uptime, quality is undefined
    if uptime_percent is None:
        return None

    # Clamp uptime_percent to valid range [0, 100] (defensive programming)
    # This ensures output is always in valid range even if caller passes invalid input
    uptime_percent = max(0.0, min(100.0, uptime_percent))

    # Compute uptime component (60% of score)
    uptime_component = UPTIME_WEIGHT * uptime_percent

    # Compute activity component (30% of score, normalized player fill rate)
    # Monotonic: higher fill rate → higher activity component
    activity_component = 0.0
    if (
        players_current is not None
        and players_capacity is not None
        and players_capacity > 0
    ):
        # Normalize to fill rate [0, 1], then scale to [0, 30] (30% weight)
        fill_rate = min(
            1.0, max(0.0, players_current / players_capacity)
        )  # Clamp to 0-1
        activity_component = ACTIVITY_WEIGHT * (
            fill_rate * 100.0
        )  # Scale to 0-100, then apply weight
    elif players_current is not None and players_current > 0:
        # Have players but no capacity - use a default capacity estimate
        # Assume 70 is a reasonable default capacity (common server size)
        # This allows quality computation even when capacity is unknown
        fill_rate = min(1.0, max(0.0, players_current / 70.0))
        activity_component = ACTIVITY_WEIGHT * (fill_rate * 100.0)
    # If players_current is None or 0, activity_component remains 0.0 (no penalty, just no bonus)

    # Compute confidence component (10% base, scaled by confidence multiplier)
    # Monotonic: green > yellow > red (ensures quality decreases as confidence degrades)
    confidence_multiplier = CONFIDENCE_MULTIPLIERS.get(
        confidence, 0.3
    )  # Default to red if unknown
    confidence_component = CONFIDENCE_BASE * (confidence_multiplier * 100.0)

    # Sum components (all components are non-negative, so sum is non-negative)
    quality_score = uptime_component + activity_component + confidence_component

    # Clamp to 0-100 (invariant: output must always be in valid range)
    # This is defensive - theoretically sum should be ≤ 100, but clamp ensures it
    quality_score = max(0.0, min(100.0, quality_score))

    return quality_score
