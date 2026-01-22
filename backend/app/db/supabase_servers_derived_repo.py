"""
Supabase servers derived state repository for Sprint 4+.

Fetches server/cluster info and heartbeats, updates derived state.
Uses service_role key for writes (bypasses RLS).
"""

from datetime import datetime, timezone

from app.core.config import get_settings
from app.core.supabase import get_supabase_admin
from app.db.servers_derived_repo import (
    DerivedServerState,
    Heartbeat,
    ServerClusterInfo,
    ServersDerivedRepository,
)


class SupabaseServersDerivedRepository(ServersDerivedRepository):
    """
    Supabase-based servers derived state repository.
    
    Fetches server/cluster info and heartbeats, updates derived state.
    Uses service_role key for writes (bypasses RLS).
    """

    def __init__(self):
        settings = get_settings()
        
        self._supabase = None
        self._configured = False
        self._config_error: str | None = None
        
        if not settings.SUPABASE_URL or not settings.SUPABASE_SERVICE_ROLE_KEY:
            if settings.ENV not in ("local", "development", "test"):
                raise RuntimeError(
                    "SupabaseServersDerivedRepository requires SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY in non-local environments"
                )
            self._config_error = "Supabase service_role credentials not configured"
        else:
            try:
                self._supabase = get_supabase_admin()
                if self._supabase is None:
                    raise RuntimeError("get_supabase_admin() returned None")
                self._configured = True
            except Exception as e:
                if settings.ENV not in ("local", "development", "test"):
                    raise RuntimeError(
                        f"Failed to initialize Supabase admin client: {str(e)}"
                    ) from e
                self._config_error = f"Supabase admin client initialization failed: {str(e)}"

    async def get_server_cluster_and_grace(self, server_id: str) -> ServerClusterInfo | None:
        """Get server cluster information and grace window."""
        if not self._configured or self._supabase is None:
            raise RuntimeError("SupabaseServersDerivedRepository not configured")

        try:
            # Get server first
            server_response = (
                self._supabase.table("servers")
                .select("cluster_id")
                .eq("id", server_id)
                .limit(1)
                .execute()
            )
            
            server_data = server_response.data if hasattr(server_response, "data") else []
            if not server_data:
                return None
            
            cluster_id = server_data[0].get("cluster_id")
            if not cluster_id:
                # Server has no cluster
                return {
                    "cluster_id": None,
                    "key_version": 1,
                    "heartbeat_grace_seconds": None,
                    "public_key_ed25519": None,
                }
            
            # Get cluster info
            cluster_response = (
                self._supabase.table("clusters")
                .select("id,key_version,heartbeat_grace_seconds,public_key_ed25519")
                .eq("id", cluster_id)
                .limit(1)
                .execute()
            )
            
            cluster_data = cluster_response.data if hasattr(cluster_response, "data") else []
            if not cluster_data:
                # Cluster not found
                return {
                    "cluster_id": cluster_id,
                    "key_version": 1,
                    "heartbeat_grace_seconds": None,
                    "public_key_ed25519": None,
                }
            
            cluster = cluster_data[0]
            
            return {
                "cluster_id": cluster.get("id"),
                "key_version": cluster.get("key_version", 1),
                "heartbeat_grace_seconds": cluster.get("heartbeat_grace_seconds"),
                "public_key_ed25519": cluster.get("public_key_ed25519"),
            }
            
        except Exception as e:
            raise RuntimeError(f"Failed to get server cluster info for {server_id}: {str(e)}") from e

    async def get_recent_heartbeats(self, server_id: str, limit: int) -> list[Heartbeat]:
        """Get recent heartbeats for a server, ordered by received_at DESC."""
        if not self._configured or self._supabase is None:
            raise RuntimeError("SupabaseServersDerivedRepository not configured")

        try:
            response = (
                self._supabase.table("heartbeats")
                .select("id,server_id,received_at,status,map_name,players_current,players_capacity,agent_version,key_version")
                .eq("server_id", server_id)
                .eq("source", "agent")  # Only agent heartbeats
                .order("received_at", desc=True)
                .limit(limit)
                .execute()
            )
            
            data = response.data if hasattr(response, "data") else []
            
            heartbeats: list[Heartbeat] = []
            for row in data:
                # Parse received_at
                received_at_str = row.get("received_at")
                if received_at_str:
                    received_at = datetime.fromisoformat(received_at_str.replace("Z", "+00:00"))
                else:
                    continue  # Skip if no timestamp
                
                heartbeats.append({
                    "id": row.get("id", ""),
                    "server_id": row.get("server_id", ""),
                    "received_at": received_at,
                    "status": row.get("status", "unknown"),
                    "map_name": row.get("map_name"),
                    "players_current": row.get("players_current"),
                    "players_capacity": row.get("players_capacity"),
                    "agent_version": row.get("agent_version"),
                    "key_version": row.get("key_version"),
                })
            
            return heartbeats
            
        except Exception as e:
            raise RuntimeError(f"Failed to get recent heartbeats for {server_id}: {str(e)}") from e

    async def update_derived_state(
        self,
        server_id: str,
        state: DerivedServerState
    ) -> None:
        """Update server derived state (does NOT update is_verified)."""
        if not self._configured or self._supabase is None:
            raise RuntimeError("SupabaseServersDerivedRepository not configured")

        try:
            # Prepare update data
            update_data = {
                "effective_status": state["effective_status"],
                "confidence": state["confidence"],
                "uptime_percent": state.get("uptime_percent"),
                "quality_score": state.get("quality_score"),
                "players_current": state.get("players_current"),
                "players_capacity": state.get("players_capacity"),
                "last_heartbeat_at": state.get("last_heartbeat_at").isoformat() if state.get("last_heartbeat_at") else None,
                "status_source": "agent",  # Set status_source to 'agent' when updating from heartbeats
            }
            
            # Update servers table
            self._supabase.table("servers").update(update_data).eq("id", server_id).execute()
            
        except Exception as e:
            raise RuntimeError(f"Failed to update derived state for {server_id}: {str(e)}") from e
