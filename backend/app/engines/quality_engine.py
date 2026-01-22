"""
Quality engine.

Computes quality score from uptime, player activity, and confidence.
Simple v1 formula - do not over-engineer.
"""

from typing import Literal

from app.db.servers_derived_repo import Heartbeat


def compute_quality_score(
    uptime_percent: float | None,
    players_current: int | None,
    players_capacity: int | None,
    confidence: Literal["green", "yellow", "red"],
    heartbeats: list[Heartbeat]
) -> float | None:
    """
    Compute quality score (0-100).
    
    Simple v1 formula:
    quality = (uptime_weight * uptime_percent)
           + (activity_weight * normalized_players)
           + (confidence_multiplier based on RYG)
    
    Do not over-engineer v1. Flapping penalty = 0 in Sprint 4.
    
    Args:
        uptime_percent: Uptime percentage (0-100) or None
        players_current: Current player count or None
        players_capacity: Player capacity or None
        confidence: Confidence level ("green", "yellow", "red")
        heartbeats: List of heartbeats (not used in v1, reserved for future)
        
    Returns:
        Quality score (0-100) or None if insufficient data
    """
    # Weights (v1 simple)
    UPTIME_WEIGHT = 0.6  # 60% weight on uptime
    ACTIVITY_WEIGHT = 0.3  # 30% weight on player activity
    CONFIDENCE_BASE = 0.1  # 10% base from confidence
    
    # Confidence multipliers
    CONFIDENCE_MULTIPLIERS = {
        "green": 1.0,
        "yellow": 0.7,
        "red": 0.3,
    }
    
    # If no uptime data, cannot compute quality
    if uptime_percent is None:
        return None
    
    # Compute uptime component
    uptime_component = UPTIME_WEIGHT * uptime_percent
    
    # Compute activity component (normalized player fill rate)
    activity_component = 0.0
    if players_current is not None and players_capacity is not None and players_capacity > 0:
        fill_rate = min(1.0, players_current / players_capacity)  # Clamp to 0-1
        activity_component = ACTIVITY_WEIGHT * (fill_rate * 100.0)  # Scale to 0-100
    elif players_current is not None and players_current > 0:
        # Have players but no capacity - use a default capacity estimate
        # Assume 70 is a reasonable default capacity
        fill_rate = min(1.0, players_current / 70.0)
        activity_component = ACTIVITY_WEIGHT * (fill_rate * 100.0)
    
    # Compute confidence component
    confidence_multiplier = CONFIDENCE_MULTIPLIERS.get(confidence, 0.3)
    confidence_component = CONFIDENCE_BASE * (confidence_multiplier * 100.0)
    
    # Sum components
    quality_score = uptime_component + activity_component + confidence_component
    
    # Clamp to 0-100
    quality_score = max(0.0, min(100.0, quality_score))
    
    return quality_score
