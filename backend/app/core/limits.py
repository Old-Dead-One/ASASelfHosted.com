"""
Per-user limit resolution.

Resolves effective servers_limit and clusters_limit for a user:
- If profile has servers_limit_override / clusters_limit_override set, use those.
- Otherwise use MAX_SERVERS_PER_USER / MAX_CLUSTERS_PER_USER from config.

Used by GET /me/limits, create server, and create cluster.
"""

from app.core.config import get_settings
from app.core.supabase import get_supabase_admin


def get_effective_limits(user_id: str) -> tuple[int, int]:
    """
    Return (servers_limit, clusters_limit) for the given user.

    Reads profile overrides; falls back to config defaults.
    """
    settings = get_settings()
    default_servers = settings.MAX_SERVERS_PER_USER
    default_clusters = settings.MAX_CLUSTERS_PER_USER

    admin = get_supabase_admin()
    if not admin:
        return (default_servers, default_clusters)

    try:
        r = (
            admin.table("profiles")
            .select("servers_limit_override, clusters_limit_override")
            .eq("id", user_id)
            .maybe_single()
            .execute()
        )
    except Exception:
        return (default_servers, default_clusters)

    row = r.data if hasattr(r, "data") else None
    if not row:
        return (default_servers, default_clusters)

    so = row.get("servers_limit_override")
    co = row.get("clusters_limit_override")
    servers_limit = int(so) if so is not None else default_servers
    clusters_limit = int(co) if co is not None else default_clusters
    # Clamp to config max so overrides can't exceed system cap
    servers_limit = min(servers_limit, 100)
    clusters_limit = min(clusters_limit, 50)
    if servers_limit <= 0:
        servers_limit = default_servers
    if clusters_limit <= 0:
        clusters_limit = default_clusters
    return (servers_limit, clusters_limit)
