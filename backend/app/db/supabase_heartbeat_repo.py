"""
Supabase heartbeat repository for Sprint 4+.

Append-only heartbeat persistence with replay detection.
Uses service_role key to bypass RLS for writes.
"""

from datetime import datetime

from app.core.config import get_settings
from app.core.supabase import get_supabase_admin
from app.db.heartbeat_repo import HeartbeatCreateResult, HeartbeatRepository
from app.schemas.heartbeat import HeartbeatRequest


class SupabaseHeartbeatRepository(HeartbeatRepository):
    """
    Supabase-based heartbeat repository.

    Inserts heartbeats append-only with replay detection.
    Uses service_role key (bypasses RLS for writes).
    """

    def __init__(self):
        settings = get_settings()

        self._supabase = None
        self._configured = False
        self._config_error: str | None = None

        if not settings.SUPABASE_URL or not settings.SUPABASE_SERVICE_ROLE_KEY:
            if settings.ENV not in ("local", "development", "test"):
                raise RuntimeError(
                    "SupabaseHeartbeatRepository requires SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY in non-local environments"
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
                self._config_error = (
                    f"Supabase admin client initialization failed: {str(e)}"
                )

    async def create_heartbeat(
        self,
        req: HeartbeatRequest,
        received_at: datetime,
        server_cluster_id: str | None = None,
    ) -> HeartbeatCreateResult:
        """
        Insert heartbeat append-only with replay detection.

        Replay detection via UNIQUE(server_id, heartbeat_id) constraint:
        - Same heartbeat_id, same server → idempotent (returns replay=True)
        - Same heartbeat_id, different server → rejected (DB constraint violation)

        Normalizes players fields: canonical fields (players_current, players_capacity)
        are the source of truth. Legacy fields (player_count, max_players) are set
        for compatibility but should not be read by engines.
        """
        if not self._configured:
            error_msg = "SupabaseHeartbeatRepository not configured"
            if self._config_error:
                error_msg += f": {self._config_error}"
            raise RuntimeError(error_msg)

        if self._supabase is None:
            raise RuntimeError("Supabase admin client not initialized")

        # Prepare heartbeat data
        # Normalize players fields: set both canonical and legacy fields
        heartbeat_data = {
            "server_id": req.server_id,
            "source": "agent",  # status_source enum value
            "received_at": received_at.isoformat(),
            "status": req.status,
            "key_version": req.key_version,
            "heartbeat_id": req.heartbeat_id,
            "signature": req.signature,
            "agent_version": req.agent_version,
            "map_name": req.map_name,
            # Canonical fields
            "players_current": req.players_current,
            "players_capacity": req.players_capacity,
            # Legacy fields (for compatibility during deprecation window)
            "player_count": req.players_current,  # Normalize to legacy field
            "max_players": req.players_capacity,  # Normalize to legacy field
            # Optional payload (JSONB)
            "payload": req.payload if req.payload else None,
        }

        try:
            # Insert heartbeat (append-only)
            response = (
                self._supabase.table("heartbeats").insert(heartbeat_data).execute()
            )

            # If insert succeeded, it's a new heartbeat
            if response.data:
                return HeartbeatCreateResult(inserted=True, replay=False)
            else:
                # No data returned (shouldn't happen, but handle gracefully)
                return HeartbeatCreateResult(inserted=False, replay=False)

        except Exception as e:
            error_str = str(e).lower()

            # Check for unique constraint violation (replay)
            # UNIQUE(server_id, heartbeat_id) ensures:
            # - Same server_id + same heartbeat_id → replay (idempotent)
            # - Different server_id + same heartbeat_id → rejected (should never happen, but DB enforces)
            if (
                "unique" in error_str
                or "duplicate" in error_str
                or "uq_heartbeats_server_heartbeat_id" in error_str
            ):
                # Replay detected - heartbeat_id already exists for this server
                # This is idempotent: same heartbeat_id for same server is safe to ignore
                return HeartbeatCreateResult(inserted=False, replay=True)

            # Other error - re-raise
            raise RuntimeError(f"Failed to insert heartbeat: {str(e)}") from e
