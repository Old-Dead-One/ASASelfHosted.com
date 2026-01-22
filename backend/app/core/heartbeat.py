"""
Heartbeat utility functions.

Grace window resolution and heartbeat processing helpers.
"""

import logging

from app.core.config import get_settings

logger = logging.getLogger(__name__)


def get_grace_window_seconds(cluster_override: int | None) -> int:
    """
    Get grace window for heartbeat freshness.
    
    Priority:
    1. Cluster override (if set)
    2. Environment variable default
    3. Clamp to min/max bounds
    
    Args:
        cluster_override: Per-cluster grace window override (from clusters.heartbeat_grace_seconds)
        
    Returns:
        Grace window in seconds (clamped to min/max)
    """
    settings = get_settings()
    
    # Use cluster override if provided, otherwise use env default
    grace_seconds = cluster_override if cluster_override is not None else settings.HEARTBEAT_GRACE_SECONDS
    
    # Clamp to min/max bounds
    grace_seconds = max(settings.HEARTBEAT_GRACE_MIN, grace_seconds)
    grace_seconds = min(settings.HEARTBEAT_GRACE_MAX, grace_seconds)
    
    return grace_seconds
