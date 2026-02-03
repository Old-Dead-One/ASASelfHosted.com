"""
Supabase servers repository.

CRUD operations for servers using RLS client.
"""

from datetime import datetime, timezone
from typing import Sequence

from postgrest.exceptions import APIError as PostgrestAPIError

from app.core.errors import NotFoundError, UnauthorizedError
from app.core.supabase import get_rls_client
from app.db.servers_repo import ServersRepository
from app.schemas.directory import DirectoryServer
from app.schemas.servers import ServerCreateRequest, ServerUpdateRequest


class SupabaseServersRepository(ServersRepository):
    """
    Supabase-based servers repository.

    Uses RLS client for authenticated operations.
    RLS policies enforce ownership automatically.
    """

    def __init__(self, user_jwt: str):
        """
        Initialize repository with user JWT for RLS.

        Args:
            user_jwt: User's JWT token (from Authorization header)
        """
        self._client = get_rls_client(user_jwt)

    async def create_server(
        self, user_id: str, server_data: ServerCreateRequest
    ) -> DirectoryServer:
        """Create a new server."""
        # Prepare insert data
        insert_data = {
            "owner_user_id": user_id,
            "name": server_data.name.strip(),
            "description": server_data.description.strip() if server_data.description else None,
            "hosting_provider": server_data.hosting_provider,  # Validated by schema
            "cluster_id": server_data.cluster_id,  # Optional cluster association
            "effective_status": server_data.effective_status or "unknown",  # Default to 'unknown' if not provided
            "status_source": None,  # No status source initially
        }
        
        # Basic listing info
        if server_data.map_name:
            insert_data["map_name"] = server_data.map_name.strip()
        if server_data.join_address:
            insert_data["join_address"] = server_data.join_address.strip()
        # join_password: only include if column exists (migration 014 may not be run yet)
        # We'll handle this in a try/except during insert
        join_password_value = None
        if server_data.join_password is not None:
            join_password_value = server_data.join_password.strip() if server_data.join_password else None
        if server_data.join_instructions_pc:
            insert_data["join_instructions_pc"] = server_data.join_instructions_pc.strip()
        if server_data.join_instructions_console:
            insert_data["join_instructions_console"] = server_data.join_instructions_console.strip()
        if server_data.discord_url is not None:
            insert_data["discord_url"] = server_data.discord_url.strip() or None
        if server_data.website_url is not None:
            insert_data["website_url"] = server_data.website_url.strip() or None
        
        # Server configuration
        if server_data.mod_list is not None:
            insert_data["mod_list"] = server_data.mod_list
        if server_data.rates:
            insert_data["rates"] = server_data.rates.strip()
        if server_data.wipe_info:
            insert_data["wipe_info"] = server_data.wipe_info.strip()
        
        # Classification
        if server_data.game_mode:
            insert_data["game_mode"] = server_data.game_mode
        # Database only has ruleset (singular), not rulesets (plural)
        # If rulesets array provided, use first element; otherwise use ruleset directly
        if server_data.rulesets and len(server_data.rulesets) > 0:
            insert_data["ruleset"] = server_data.rulesets[0]  # Primary for legacy/filters
        elif server_data.ruleset:
            insert_data["ruleset"] = server_data.ruleset
        if server_data.is_pc is not None:
            insert_data["is_pc"] = server_data.is_pc
        if server_data.is_console is not None:
            insert_data["is_console"] = server_data.is_console
        if server_data.is_crossplay is not None:
            insert_data["is_crossplay"] = server_data.is_crossplay

        # Insert into servers table (RLS will enforce ownership)
        # Handle join_password separately in case column doesn't exist yet
        if join_password_value is not None:
            insert_data["join_password"] = join_password_value
        
        try:
            result = (
                self._client.table("servers")
                .insert(insert_data)
                .execute()
            )
        except PostgrestAPIError as e:
            err_str = str(e)
            # If insert failed due to missing join_password column, retry without it
            if e.code == "PGRST204" and "join_password" in err_str:
                insert_data.pop("join_password", None)
                result = (
                    self._client.table("servers")
                    .insert(insert_data)
                    .execute()
                )
            # If rulesets or platform columns don't exist yet (migration 015 not run), retry without them
            elif e.code == "42703" and ("rulesets" in err_str or "is_pc" in err_str or "is_console" in err_str or "is_crossplay" in err_str):
                insert_data.pop("rulesets", None)
                insert_data.pop("is_pc", None)
                insert_data.pop("is_console", None)
                insert_data.pop("is_crossplay", None)
                if server_data.rulesets and not insert_data.get("ruleset"):
                    insert_data["ruleset"] = server_data.rulesets[0]
                result = (
                    self._client.table("servers")
                    .insert(insert_data)
                    .execute()
                )
            else:
                raise

        if not result.data or len(result.data) == 0:
            raise RuntimeError("Failed to create server")

        server_id = result.data[0]["id"]

        # Fetch from directory_view to get full DirectoryServer
        # directory_view should update immediately (it's a view, not a materialized view)
        server = await self.get_server(server_id, user_id)
        if server:
            return server
        
        # If directory_view doesn't have it, this is unexpected
        # Possible causes:
        # 1. View refresh delay (shouldn't happen for regular views)
        # 2. hosting_provider filter excluded it (shouldn't happen due to validation)
        # 3. Database transaction isolation
        # For now, raise an error - in production, we might want to retry or construct manually
        raise RuntimeError(
            f"Server created (id: {server_id}) but not found in directory_view. "
            "This may indicate a view refresh issue or hosting_provider mismatch."
        )

    async def get_server(
        self, server_id: str, user_id: str | None = None
    ) -> DirectoryServer | None:
        """Get server by ID from directory_view."""
        # Use directory_view - it has all the computed fields we need
        # If join_password column doesn't exist yet, handle gracefully
        try:
            result = (
                self._client.table("directory_view")
                .select("*")
                .eq("id", server_id)
                .limit(1)
                .execute()
            )

            if not result.data or len(result.data) == 0:
                return None

            row = result.data[0]
            # Ensure join_password exists (set to None if column doesn't exist in view)
            if "join_password" not in row:
                row["join_password"] = None
            
            # Convert to DirectoryServer
            return self._map_to_directory_server(row)
        except PostgrestAPIError as e:
            # If directory_view query fails due to missing join_password column, retry without it
            if e.code == "42703" and "join_password" in str(e):
                # Try selecting all columns except join_password
                try:
                    result = (
                        self._client.table("directory_view")
                        .select("id,name,description,map_name,join_address,join_instructions_pc,join_instructions_console,mod_list,rates,wipe_info,effective_status,status_source,last_seen_at,confidence,created_at,updated_at,cluster_id,cluster_name,cluster_slug,cluster_visibility,favorite_count,is_verified,is_new,is_stable,ruleset,game_mode,server_type,platforms,is_official_plus,is_modded,is_crossplay,is_console,is_pc,players_current,players_capacity,quality_score,uptime_percent")
                        .eq("id", server_id)
                        .limit(1)
                        .execute()
                    )
                    
                    if not result.data or len(result.data) == 0:
                        return None
                    
                    row = result.data[0]
                    row["join_password"] = None  # Column doesn't exist yet
                    return self._map_to_directory_server(row)
                except Exception:
                    # If that also fails, fall through to servers table fallback
                    pass
            
            # If directory_view query fails for other reasons,
            # try querying servers table directly as fallback
            import logging
            logging.warning(f"directory_view query failed for server {server_id}, trying servers table: {e}")
            
            # Fallback: query servers table directly
            result = (
                self._client.table("servers")
                .select("*")
                .eq("id", server_id)
                .limit(1)
                .execute()
            )
            
            if not result.data or len(result.data) == 0:
                return None
            
            row = result.data[0]
            # Add join_password if it exists, otherwise None
            if "join_password" not in row:
                row["join_password"] = None
            
            # Get cluster and favorite count (minimal fields needed)
            cluster_id = row.get("cluster_id")
            if cluster_id:
                try:
                    cluster_result = (
                        self._client.table("clusters")
                        .select("name,slug,visibility")
                        .eq("id", cluster_id)
                        .limit(1)
                        .execute()
                    )
                    if cluster_result.data:
                        row["cluster_name"] = cluster_result.data[0].get("name")
                        row["cluster_slug"] = cluster_result.data[0].get("slug")
                        row["cluster_visibility"] = cluster_result.data[0].get("visibility")
                except Exception:
                    pass
            
            # Get favorite count
            try:
                fav_result = (
                    self._client.table("favorites")
                    .select("id")
                    .eq("server_id", server_id)
                    .execute()
                )
                row["favorite_count"] = len(fav_result.data) if fav_result.data else 0
            except Exception:
                row["favorite_count"] = 0
            
            # Set defaults for computed fields
            row.setdefault("is_new", False)
            row.setdefault("is_stable", False)
            row.setdefault("server_type", None)
            
            return self._map_to_directory_server(row)


    async def list_owner_servers(
        self, user_id: str
    ) -> Sequence[DirectoryServer]:
        """List all servers owned by user."""
        # Query directory_view filtered by owner_user_id
        # Note: directory_view doesn't include owner_user_id, so we need to query servers table
        # and then fetch from directory_view
        
        # Get server IDs owned by user
        servers_result = (
            self._client.table("servers")
            .select("id")
            .eq("owner_user_id", user_id)
            .order("created_at", desc=True)
            .execute()
        )

        if not servers_result.data:
            return []

        server_ids = [row["id"] for row in servers_result.data]

        # Query directory_view with all server IDs at once (more efficient than looping)
        # Use 'in' filter to get all servers in one query
        directory_result = (
            self._client.table("directory_view")
            .select("*")
            .in_("id", server_ids)
            .execute()
        )

        if not directory_result.data:
            return []

        # Map all results to DirectoryServer
        servers = []
        for row in directory_result.data:
            try:
                server = self._map_to_directory_server(row)
                servers.append(server)
            except Exception as e:
                # Log error but continue processing other servers
                import logging
                logging.warning(f"Failed to map server {row.get('id')} to DirectoryServer: {e}")
                continue

        # Sort by created_at descending to match original order
        servers.sort(key=lambda s: s.created_at, reverse=True)

        return servers

    async def update_server(
        self, server_id: str, user_id: str, server_data: ServerUpdateRequest
    ) -> DirectoryServer | None:
        """Update server."""
        # First verify server exists and user owns it
        existing = await self.get_server(server_id, user_id)
        if not existing:
            raise NotFoundError("server", server_id)

        # Prepare update data (only include fields that are provided)
        update_data: dict = {}
        if server_data.name is not None:
            update_data["name"] = server_data.name.strip()
        if server_data.description is not None:
            update_data["description"] = (
                server_data.description.strip() if server_data.description else None
            )
        if server_data.hosting_provider is not None:
            # Already validated by schema to be 'self_hosted'
            update_data["hosting_provider"] = server_data.hosting_provider
        if server_data.cluster_id is not None:
            # Allow setting cluster_id or removing it (empty string = remove)
            update_data["cluster_id"] = server_data.cluster_id if server_data.cluster_id else None
        
        # Basic listing info
        if server_data.map_name is not None:
            update_data["map_name"] = server_data.map_name.strip() if server_data.map_name else None
        if server_data.join_address is not None:
            update_data["join_address"] = server_data.join_address.strip() if server_data.join_address else None
        # join_password: handle separately in case column doesn't exist yet
        join_password_value = None
        if server_data.join_password is not None:
            join_password_value = server_data.join_password.strip() if server_data.join_password else None
        if server_data.join_instructions_pc is not None:
            update_data["join_instructions_pc"] = server_data.join_instructions_pc.strip() if server_data.join_instructions_pc else None
        if server_data.join_instructions_console is not None:
            update_data["join_instructions_console"] = server_data.join_instructions_console.strip() if server_data.join_instructions_console else None
        if server_data.discord_url is not None:
            update_data["discord_url"] = server_data.discord_url.strip() or None
        if server_data.website_url is not None:
            update_data["website_url"] = server_data.website_url.strip() or None
        
        # Server configuration
        if server_data.mod_list is not None:
            update_data["mod_list"] = server_data.mod_list
        if server_data.rates is not None:
            update_data["rates"] = server_data.rates.strip() if server_data.rates else None
        if server_data.wipe_info is not None:
            update_data["wipe_info"] = server_data.wipe_info.strip() if server_data.wipe_info else None
        
        # Classification
        if server_data.game_mode is not None:
            update_data["game_mode"] = server_data.game_mode
        # Database only has ruleset (singular), not rulesets (plural)
        # If rulesets array provided, use first element; otherwise use ruleset directly
        if server_data.rulesets is not None:
            if len(server_data.rulesets) > 0:
                update_data["ruleset"] = server_data.rulesets[0]
            else:
                update_data["ruleset"] = None
        elif server_data.ruleset is not None:
            update_data["ruleset"] = server_data.ruleset
        if server_data.effective_status is not None:
            update_data["effective_status"] = server_data.effective_status
        if server_data.is_pc is not None:
            update_data["is_pc"] = server_data.is_pc
        if server_data.is_console is not None:
            update_data["is_console"] = server_data.is_console
        if server_data.is_crossplay is not None:
            update_data["is_crossplay"] = server_data.is_crossplay

        # Add join_password to update_data if provided (will fail gracefully if column doesn't exist)
        if join_password_value is not None:
            update_data["join_password"] = join_password_value

        if not update_data:
            # No fields to update
            return existing

        # Update servers table (RLS will enforce ownership)
        try:
            result = (
                self._client.table("servers")
                .update(update_data)
                .eq("id", server_id)
                .eq("owner_user_id", user_id)  # Extra ownership check
                .execute()
            )

            if not result.data or len(result.data) == 0:
                # Update failed - either server not found or user doesn't own it
                raise UnauthorizedError("Server not found or you don't have permission to update it")
        except PostgrestAPIError as e:
            err_str = str(e)
            # If update failed due to missing column, retry without it
            if e.code == "PGRST204" and "join_password" in err_str:
                # Column doesn't exist yet - remove join_password and retry
                update_data_retry = {k: v for k, v in update_data.items() if k != "join_password"}
                if update_data_retry:
                    result = (
                        self._client.table("servers")
                        .update(update_data_retry)
                        .eq("id", server_id)
                        .eq("owner_user_id", user_id)
                        .execute()
                    )
                    if not result.data or len(result.data) == 0:
                        raise UnauthorizedError("Server not found or you don't have permission to update it")
            elif e.code == "PGRST204" and "rulesets" in err_str:
                # rulesets column doesn't exist yet (migration 015 not run) - retry without it; ruleset (singular) is kept
                update_data_retry = {k: v for k, v in update_data.items() if k != "rulesets"}
                if update_data_retry:
                    result = (
                        self._client.table("servers")
                        .update(update_data_retry)
                        .eq("id", server_id)
                        .eq("owner_user_id", user_id)
                        .execute()
                    )
                    if not result.data or len(result.data) == 0:
                        raise UnauthorizedError("Server not found or you don't have permission to update it")
            else:
                raise

        # Fetch updated server from directory_view
        return await self.get_server(server_id, user_id)

    async def delete_server(
        self, server_id: str, user_id: str
    ) -> bool:
        """Delete server."""
        # Verify server exists and user owns it
        existing = await self.get_server(server_id, user_id)
        if not existing:
            return False

        # Delete from servers table (RLS will enforce ownership)
        # CASCADE will handle related records (heartbeats, favorites, etc.)
        result = (
            self._client.table("servers")
            .delete()
            .eq("id", server_id)
            .eq("owner_user_id", user_id)  # Extra ownership check
            .execute()
        )

        # Check if deletion was successful
        # Supabase delete returns empty data on success
        return True

    @staticmethod
    def _map_to_directory_server(row: dict) -> DirectoryServer:
        """
        Map database row to DirectoryServer schema.
        
        Handles type conversions and field normalization.
        """
        # Normalize array fields (similar to directory_repo)
        mod_list = SupabaseServersRepository._normalize_array_field(row.get("mod_list"))
        platforms = SupabaseServersRepository._normalize_array_field(row.get("platforms"))
        rulesets = SupabaseServersRepository._normalize_array_field(row.get("rulesets"))
        if not rulesets and row.get("ruleset"):
            rulesets = [row["ruleset"]]
        
        # Convert datetime strings to datetime objects if needed
        def parse_datetime(value: str | datetime | None) -> datetime | None:
            if value is None:
                return None
            if isinstance(value, datetime):
                return value
            if isinstance(value, str):
                return datetime.fromisoformat(value.replace("Z", "+00:00"))
            return None
        
        # Build DirectoryServer with normalized fields
        return DirectoryServer(
            id=str(row["id"]),
            name=row["name"],
            description=row.get("description"),
            map_name=row.get("map_name"),
            join_address=row.get("join_address"),
            join_password=row.get("join_password"),
            join_instructions_pc=row.get("join_instructions_pc"),
            join_instructions_console=row.get("join_instructions_console"),
            discord_url=row.get("discord_url"),
            website_url=row.get("website_url"),
            mod_list=mod_list,
            rates=row.get("rates"),
            wipe_info=row.get("wipe_info"),
            effective_status=row.get("effective_status", "unknown"),
            status_source=row.get("status_source"),
            last_seen_at=parse_datetime(row.get("last_seen_at")),
            seconds_since_seen=row.get("seconds_since_seen"),
            confidence=row.get("confidence"),
            created_at=parse_datetime(row.get("created_at")) or datetime.now(),
            updated_at=parse_datetime(row.get("updated_at")) or datetime.now(),
            cluster_id=row.get("cluster_id"),
            cluster_name=row.get("cluster_name"),
            cluster_slug=row.get("cluster_slug"),
            cluster_visibility=row.get("cluster_visibility"),
            favorite_count=row.get("favorite_count", 0),
            players_current=row.get("players_current"),
            players_capacity=row.get("players_capacity"),
            players_max=row.get("players_max"),
            quality_score=row.get("quality_score"),
            uptime_percent=row.get("uptime_percent"),
            uptime_24h=row.get("uptime_24h"),
            rank_position=row.get("rank_position"),
            rank=row.get("rank"),
            rank_by=row.get("rank_by"),
            rank_delta_24h=row.get("rank_delta_24h"),
            is_verified=row.get("is_verified", False),
            is_new=row.get("is_new", False),
            is_stable=row.get("is_stable", False),
            ruleset=row.get("ruleset"),
            rulesets=rulesets,
            server_type=row.get("server_type"),
            game_mode=row.get("game_mode"),
            platforms=platforms,
            is_official_plus=row.get("is_official_plus"),
            is_modded=row.get("is_modded"),
            is_crossplay=row.get("is_crossplay"),
            is_console=row.get("is_console"),
            is_pc=row.get("is_pc"),
            is_PC=row.get("is_PC"),
        )
    
    @staticmethod
    def _normalize_array_field(value: str | list | None) -> list:
        """
        Normalize Postgres array fields to Python lists.
        
        Handles cases where Supabase/PostgREST returns arrays as:
        - JSON arrays (list): return as-is
        - Postgres array strings ("{value1,value2}"): parse to list
        - None: return empty list
        """
        if value is None:
            return []
        
        if isinstance(value, list):
            return value
        
        if isinstance(value, str):
            # Handle Postgres array string format: "{value1,value2}"
            if value.startswith("{") and value.endswith("}"):
                # Remove braces and split by comma
                inner = value.strip("{}")
                if not inner:
                    return []
                # Split and clean up values
                return [v.strip().strip('"') for v in inner.split(",") if v.strip()]
            # If it's a plain string, wrap it in a list
            return [value] if value else []
        
        # Fallback: try to convert to list
        return list(value) if value else []
