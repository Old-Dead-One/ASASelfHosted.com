"""
Supabase directory repository for Sprint 3+.

Read-only repository that queries from directory_view in Supabase.
Fails fast if Supabase is not configured in non-local environments.
"""

from datetime import datetime, timezone
from typing import Sequence

from app.core.config import get_settings
from app.core.errors import DomainValidationError
from app.db.directory_repo import DirectoryRepository
from app.schemas.directory import (
    DirectoryServer,
    DirectoryFiltersResponse,
    RankBy,
    ServerStatus,
    SortOrder,
    DirectoryView,
    TriState,
    GameMode,
    Ruleset,
    ServerType,
    ClusterVisibility,
    VerificationMode,
    Platform,
    ClusterInfo,
    NumericRange,
)
from app.utils.cursor import Cursor, create_cursor, parse_cursor


class SupabaseDirectoryRepository(DirectoryRepository):
    """
    Supabase-based directory repository.

    Queries from directory_view (read-only, public-safe).
    Fails fast if Supabase is not configured.
    """

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

    @staticmethod
    def _format_cursor_value_for_postgrest(value: object) -> str:
        """Format cursor last_value for PostgREST or_ filter (no reserved chars in value)."""
        if hasattr(value, "isoformat"):
            s = value.isoformat()
        elif value is None:
            s = "null"
        else:
            s = str(value)
        if any(c in s for c in ",:()"):
            return f'"{s}"'
        return s

    @staticmethod
    def _map_rank_by_to_column(rank_by: RankBy) -> str:
        """
        Map rank_by parameter to database column name.

        Args:
            rank_by: Sort key parameter

        Returns:
            Database column name for sorting
        """
        mapping = {
            "updated": "updated_at",
            "new": "created_at",
            "favorites": "favorite_count",
            "players": "players_current",
            "quality": "quality_score",
            "uptime": "uptime_percent",
        }
        return mapping.get(rank_by, "updated_at")  # Default to updated_at

    @staticmethod
    def _is_nullable_column(column: str) -> bool:
        """
        Check if a column can be NULL.

        Args:
            column: Database column name

        Returns:
            True if column can be NULL, False otherwise
        """
        nullable_columns = {
            "players_current",
            "quality_score",
            "uptime_percent",
            "favorite_count",  # Can be 0 but not NULL in practice, but check anyway
        }
        return column in nullable_columns

    def __init__(self):
        settings = get_settings()

        # Always initialize state explicitly
        self._supabase = None
        self._configured = False
        self._config_error: str | None = None

        if not settings.SUPABASE_URL or not settings.SUPABASE_SERVICE_ROLE_KEY:
            if settings.ENV not in ("local", "development", "test"):
                raise RuntimeError(
                    "SupabaseDirectoryRepository requires SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY in non-local environments"
                )
            # In local/dev/test, allow unconfigured state (will raise on actual use)
            self._config_error = "Supabase credentials not configured"
        else:
            # Credentials exist - attempt to initialize client (service_role so we can use SECURITY INVOKER views without granting anon SELECT on base tables)
            try:
                from app.core.supabase import get_supabase_admin

                self._supabase = get_supabase_admin()
                if self._supabase is None:
                    raise RuntimeError("get_supabase_admin() returned None")
                self._configured = True
            except Exception as e:
                # In non-local, client init failure is a hard error
                if settings.ENV not in ("local", "development", "test"):
                    raise RuntimeError(
                        f"Failed to initialize Supabase client: {str(e)}"
                    ) from e
                # In local/dev/test, allow failure but record it
                self._config_error = f"Supabase client initialization failed: {str(e)}"

    async def list_servers(
        self,
        limit: int = 25,
        cursor: str | None = None,
        q: str | None = None,
        status: ServerStatus | None = None,
        mode: VerificationMode | None = None,
        rank_by: RankBy = "updated",
        order: SortOrder = "desc",
        view: DirectoryView = "card",  # UI hint only; repo must not branch logic on view
        ruleset: Ruleset | None = None,
        game_mode: GameMode | None = None,
        # TODO (Sprint 3+): Remove server_type filter - use ruleset instead
        # Note: If both ruleset and server_type are provided, ruleset takes precedence.
        server_type: ServerType | None = None,  # Deprecated: use ruleset instead
        map_name: str | None = None,  # Single map filter (string match)
        cluster: str | None = None,  # Filter by cluster slug or name (string match)
        cluster_visibility: ClusterVisibility | None = None,
        cluster_id: str | None = None,
        players_current_min: int | None = None,
        players_current_max: int | None = None,
        uptime_min: float | None = None,  # Minimum uptime percent (0-100)
        quality_min: float | None = None,  # Minimum quality score (0-100)
        official_plus: TriState = "any",
        modded: TriState = "any",
        crossplay: TriState = "any",
        console: TriState = "any",
        pc: TriState = "any",  # PC support filter (canonical name)
        is_cluster: TriState = "any",  # Filter by cluster association (true = has cluster, false = no cluster)
        maps: list[str] | None = None,  # Multi-select map names (OR)
        mods: list[str] | None = None,
        platforms: list[Platform] | None = None,  # Multi-select platforms (OR)
        now_utc: datetime | None = None,  # Request handling time for seconds_since_seen
    ) -> tuple[Sequence[DirectoryServer], str | None]:
        """
        List servers from Supabase directory_view with cursor pagination.

        Returns:
            Tuple of (server list, next_cursor). next_cursor is None if no more results.
        """
        if not self._configured:
            error_msg = "SupabaseDirectoryRepository not configured"
            if self._config_error:
                error_msg += f": {self._config_error}"
            raise RuntimeError(error_msg)

        if self._supabase is None:
            raise RuntimeError("Supabase client not initialized")

        # Enforce max limit (400 error if > 100)
        if limit > 100:
            raise DomainValidationError(f"limit must be <= 100, got {limit}")

        # Parse and validate cursor
        parsed_cursor: Cursor | None = None
        if cursor:
            parsed_cursor = parse_cursor(cursor)
            # Validate cursor matches request parameters
            parsed_cursor.validate_match(rank_by, order)

        # Get request handling time (consistent across response)
        if now_utc is None:
            now_utc = datetime.now(timezone.utc)

        # Map rank_by to database column
        sort_column = self._map_rank_by_to_column(rank_by)
        # Note: directory_view COALESCEs nullable sort columns, so no special NULL handling needed

        # Build query from directory_view
        # Explicitly select columns matching DirectoryServer schema (minus rank fields computed in backend)
        # This prevents failures if view accidentally includes extra columns (extra="forbid" in BaseSchema)
        # Select ruleset only; directory_view may not have rulesets (migration 015). We derive rulesets from ruleset below.
        select_columns = (
            "id,name,description,map_name,join_address,join_instructions_pc,join_instructions_console,"
            "mod_list,rates,wipe_info,effective_status,status_source,last_seen_at,confidence,"
            "created_at,updated_at,cluster_id,cluster_name,cluster_slug,cluster_visibility,"
            "favorite_count,is_verified,is_new,is_stable,ruleset,game_mode,server_type,"
            "platforms,is_official_plus,is_modded,is_crossplay,is_console,is_pc,"
            "players_current,players_capacity,quality_score,uptime_percent"
        )
        # No count needed for cursor pagination
        query = self._supabase.table("directory_view").select(select_columns)

        # Apply search filter (q parameter)
        # Search in name, description, map_name, cluster_name using OR
        # Note: This is the ONLY place we use .or_() - multiple .or_() calls overwrite each other
        if q and (q_trimmed := q.strip()):
            # PostgREST OR syntax: or=(field1.ilike.*value*,field2.ilike.*value*)
            # Format: "field1.ilike.*value*,field2.ilike.*value*"
            or_conditions = ",".join(
                [
                    f"name.ilike.%{q_trimmed}%",
                    f"description.ilike.%{q_trimmed}%",
                    f"map_name.ilike.%{q_trimmed}%",
                    f"cluster_name.ilike.%{q_trimmed}%",
                ]
            )
            query = query.or_(or_conditions)

        # Apply status filter
        if status:
            query = query.eq("effective_status", status)

        # Apply VerificationMode filter (mode parameter)
        # VerificationMode is listing trust (is_verified), not status provenance (status_source)
        if mode == "verified":
            query = query.eq("is_verified", True)
        elif mode == "manual":
            query = query.eq("is_verified", False)

        # Apply core server trait filters
        # Note: If both ruleset and server_type are provided, ruleset takes precedence
        if ruleset:
            query = query.eq("ruleset", ruleset)
        elif server_type:  # Only apply server_type if ruleset not provided
            query = query.eq("server_type", server_type)

        if game_mode:
            query = query.eq("game_mode", game_mode)

        if map_name:
            map_trimmed = map_name.strip()
            if map_trimmed:
                query = query.ilike("map_name", f"%{map_trimmed}%")

        if cluster and (cluster_trimmed := cluster.strip()):
            # Sprint 3: Use slug as canonical filter to avoid needing another OR group
            # (Multiple .or_() calls overwrite each other in PostgREST)
            # Note: Original plan allowed "cluster slug OR name" - reduced to slug-only for Sprint 3
            # To restore name search later, use RPC function or include in main q search
            query = query.ilike("cluster_slug", f"%{cluster_trimmed}%")

        if cluster_visibility:
            query = query.eq("cluster_visibility", cluster_visibility)

        if cluster_id:
            query = query.eq("cluster_id", cluster_id)

        # Apply player filters
        if players_current_min is not None:
            query = query.gte("players_current", players_current_min)
        if players_current_max is not None:
            query = query.lte("players_current", players_current_max)

        # Apply numeric range filters
        if uptime_min is not None:
            query = query.gte("uptime_percent", uptime_min)
        if quality_min is not None:
            query = query.gte("quality_score", quality_min)

        # Apply is_cluster filter (tri-state: any/true/false)
        # true = has cluster_id, false = no cluster_id
        if is_cluster == "true":
            # Has cluster: cluster_id IS NOT NULL
            query = query.not_.is_("cluster_id", "null")
        elif is_cluster == "false":
            # No cluster: cluster_id IS NULL
            query = query.is_("cluster_id", "null")
        
        # Apply tri-state filters (critical: unknown/NULL does NOT match false)
        # Helper to normalize tri-state
        def _normalize_tristate(ts: TriState) -> bool | None:
            if ts == "any":
                return None
            return ts == "true"

        official_plus_val = _normalize_tristate(official_plus)
        if official_plus_val is not None:
            # true = include only matching (IS TRUE), false = exclude matching (IS FALSE)
            if official_plus_val:
                query = query.eq("is_official_plus", True)
            else:
                query = query.eq("is_official_plus", False)

        modded_val = _normalize_tristate(modded)
        if modded_val is not None:
            # modded filter checks "has mods installed" (is_modded), not ruleset classification
            if modded_val:
                query = query.eq("is_modded", True)
            else:
                query = query.eq("is_modded", False)

        crossplay_val = _normalize_tristate(crossplay)
        if crossplay_val is not None:
            if crossplay_val:
                query = query.eq("is_crossplay", True)
            else:
                query = query.eq("is_crossplay", False)

        console_val = _normalize_tristate(console)
        if console_val is not None:
            if console_val:
                query = query.eq("is_console", True)
            else:
                query = query.eq("is_console", False)

        pc_val = _normalize_tristate(pc)
        if pc_val is not None:
            if pc_val:
                query = query.eq("is_pc", True)
            else:
                query = query.eq("is_pc", False)

        # Apply multi-select filters (OR semantics)
        if maps:
            # Filter by map names (exact match, OR semantics)
            # Use .in_() for exact match list - avoids needing OR groups
            maps_clean = [m.strip() for m in maps if m.strip()]
            if maps_clean:
                query = query.in_("map_name", maps_clean)

        if mods:
            # Filter by mod names in mod_list array (OR semantics)
            # Use array overlap operator - gives "server has ANY of these mods"
            mods_clean = [m.strip() for m in mods if m.strip()]
            if mods_clean:
                query = query.overlaps("mod_list", mods_clean)

        if platforms:
            # Filter by platforms array (OR semantics)
            platforms_clean = [
                str(p).strip().lower() for p in platforms if str(p).strip()
            ]
            if platforms_clean:
                # Use array overlap operator (ov - overlaps)
                # PostgREST: platforms.ov.{platform1,platform2} checks if arrays overlap
                # This gives us OR semantics - server matches if its platforms overlap with any requested platform
                query = query.overlaps("platforms", platforms_clean)

        # Apply cursor seek predicate if cursor provided (route rejects cursor+q)
        # Seek: (sort_col < last_value) OR (sort_col = last_value AND id > last_id) for DESC;
        #       (sort_col > last_value) OR (sort_col = last_value AND id > last_id) for ASC.
        # Use PostgREST or_() with nested and(); then limit(limit+1). No OFFSET, no Python filter.
        if parsed_cursor:
            v = self._format_cursor_value_for_postgrest(parsed_cursor.last_value)
            lid = str(parsed_cursor.last_id)
            if any(c in lid for c in ",:()"):
                lid = f'"{lid}"'
            if order == "desc":
                seek = f"{sort_column}.lt.{v},and({sort_column}.eq.{v},id.gt.{lid})"
            else:
                seek = f"{sort_column}.gt.{v},and({sort_column}.eq.{v},id.gt.{lid})"
            query = query.or_(seek)

        # ORDER BY sort_column, id (tie-break)
        if order == "asc":
            query = query.order(sort_column, desc=False).order("id", desc=False)
        else:
            query = query.order(sort_column, desc=True).order("id", desc=False)

        query = query.limit(limit + 1)

        # Execute query
        try:
            response = query.execute()
        except Exception as e:
            import logging

            logger = logging.getLogger(__name__)
            logger.error(
                "Directory read error: failed to query directory_view",
                extra={
                    "error": str(e),
                    "error_type": type(e).__name__,
                    "read_operation": "list_servers",
                    "rank_by": rank_by,
                    "order": order,
                    "limit": limit,
                },
                exc_info=True,
            )
            raise RuntimeError(f"Failed to query directory_view: {str(e)}") from e

        data = response.data if hasattr(response, "data") else []

        # Check if there's a next page (we have limit + 1 rows)
        has_next = len(data) > limit
        if has_next:
            data = data[:limit]  # Keep only limit items

        # Convert to DirectoryServer objects
        servers: list[DirectoryServer] = []
        last_row = None
        for row in data:
            try:
                # Normalize array fields (handle Postgres array string format if needed)
                # DirectoryServer requires list, not Optional or string
                row["mod_list"] = self._normalize_array_field(row.get("mod_list"))
                row["platforms"] = self._normalize_array_field(row.get("platforms"))
                # directory_view may only have ruleset; DirectoryServer expects rulesets list
                if "rulesets" not in row or row.get("rulesets") is None:
                    row["rulesets"] = [row["ruleset"]] if row.get("ruleset") else []

                # Compute seconds_since_seen
                last_seen_at = row.get("last_seen_at")
                seconds_since_seen = None
                if last_seen_at:
                    # Parse last_seen_at if it's a string
                    if isinstance(last_seen_at, str):
                        last_seen_dt = datetime.fromisoformat(
                            last_seen_at.replace("Z", "+00:00")
                        )
                    else:
                        last_seen_dt = last_seen_at

                    # Ensure timezone-aware
                    if last_seen_dt.tzinfo is None:
                        last_seen_dt = last_seen_dt.replace(tzinfo=timezone.utc)

                    # Compute seconds_since_seen = now_utc - last_seen_at
                    delta = (now_utc - last_seen_dt).total_seconds()
                    seconds_since_seen = max(0.0, delta)  # Clamp negatives to 0

                # Create DirectoryServer with rank fields and seconds_since_seen
                server = DirectoryServer(
                    **row,
                    seconds_since_seen=seconds_since_seen,
                    rank_position=None,  # Not needed for cursor pagination
                    rank_by=rank_by,
                    rank_delta_24h=None,  # Placeholder for Sprint 5
                )
                servers.append(server)
                last_row = row  # Keep track of last row for cursor generation
            except Exception as e:
                # Handle parse errors based on environment
                import logging
                from app.core.config import get_settings

                logger = logging.getLogger(__name__)
                settings = get_settings()

                error_msg = f"Failed to parse server row: {e}"

                # In local/dev/test: log and skip (allows development with incomplete data)
                # In non-local: fail fast (silently dropping rows is dangerous in production)
                if settings.ENV in ("local", "development", "test"):
                    logger.warning(error_msg)
                    continue
                else:
                    # Production: fail fast - silently dropping rows is dangerous
                    logger.error(error_msg)
                    raise RuntimeError(
                        f"Failed to parse server row from directory_view: {e}"
                    ) from e

        # Generate next_cursor if there are more results
        next_cursor = None
        if has_next and last_row:
            # Get sort value and id from last row
            last_sort_value = last_row.get(sort_column)
            last_id = last_row.get("id")

            if last_id:
                next_cursor = create_cursor(rank_by, order, last_sort_value, last_id)

        return servers, next_cursor

    async def count_servers(
        self,
        q: str | None = None,
        status: ServerStatus | None = None,
        mode: VerificationMode | None = None,
        ruleset: Ruleset | None = None,
        game_mode: GameMode | None = None,
        server_type: ServerType | None = None,
        map_name: str | None = None,
        cluster: str | None = None,
        cluster_visibility: ClusterVisibility | None = None,
        cluster_id: str | None = None,
        players_current_min: int | None = None,
        players_current_max: int | None = None,
        uptime_min: float | None = None,
        quality_min: float | None = None,
        official_plus: TriState = "any",
        modded: TriState = "any",
        crossplay: TriState = "any",
        console: TriState = "any",
        pc: TriState = "any",
        is_cluster: TriState = "any",
        maps: list[str] | None = None,
        mods: list[str] | None = None,
        platforms: list[Platform] | None = None,
    ) -> int:
        """Return total number of servers matching the given filters."""
        if not self._configured or self._supabase is None:
            return 0

        def _norm(ts: TriState) -> bool | None:
            if ts == "any":
                return None
            return ts == "true"

        try:
            query = self._supabase.table("directory_view").select("id", count="exact")
            if q and (q_trimmed := q.strip()):
                or_conditions = ",".join(
                    [
                        f"name.ilike.%{q_trimmed}%",
                        f"description.ilike.%{q_trimmed}%",
                        f"map_name.ilike.%{q_trimmed}%",
                        f"cluster_name.ilike.%{q_trimmed}%",
                    ]
                )
                query = query.or_(or_conditions)
            if status:
                query = query.eq("effective_status", status)
            if mode == "verified":
                query = query.eq("is_verified", True)
            elif mode == "manual":
                query = query.eq("is_verified", False)
            if ruleset:
                query = query.eq("ruleset", ruleset)
            elif server_type:
                query = query.eq("server_type", server_type)
            if game_mode:
                query = query.eq("game_mode", game_mode)
            if map_name and (map_trimmed := map_name.strip()):
                query = query.ilike("map_name", f"%{map_trimmed}%")
            if cluster and (cluster_trimmed := cluster.strip()):
                query = query.ilike("cluster_slug", f"%{cluster_trimmed}%")
            if cluster_visibility:
                query = query.eq("cluster_visibility", cluster_visibility)
            if cluster_id:
                query = query.eq("cluster_id", cluster_id)
            if players_current_min is not None:
                query = query.gte("players_current", players_current_min)
            if players_current_max is not None:
                query = query.lte("players_current", players_current_max)
            if uptime_min is not None:
                query = query.gte("uptime_percent", uptime_min)
            if quality_min is not None:
                query = query.gte("quality_score", quality_min)
            if is_cluster == "true":
                query = query.not_.is_("cluster_id", "null")
            elif is_cluster == "false":
                query = query.is_("cluster_id", "null")
            ov = _norm(official_plus)
            if ov is not None:
                query = query.eq("is_official_plus", ov)
            md = _norm(modded)
            if md is not None:
                query = query.eq("is_modded", md)
            cp = _norm(crossplay)
            if cp is not None:
                query = query.eq("is_crossplay", cp)
            co = _norm(console)
            if co is not None:
                query = query.eq("is_console", co)
            pv = _norm(pc)
            if pv is not None:
                query = query.eq("is_pc", pv)
            if maps:
                maps_clean = [m.strip() for m in maps if m.strip()]
                if maps_clean:
                    query = query.in_("map_name", maps_clean)
            if mods:
                mods_clean = [m.strip() for m in mods if m.strip()]
                if mods_clean:
                    query = query.overlaps("mod_list", mods_clean)
            if platforms:
                platforms_clean = [str(p).strip().lower() for p in platforms if str(p).strip()]
                if platforms_clean:
                    query = query.overlaps("platforms", platforms_clean)

            response = query.limit(0).execute()
            # supabase-py / postgrest returns count when count="exact" is used
            count = getattr(response, "count", None)
            if count is not None:
                return int(count)
            # Fallback: some clients expose it in headers or elsewhere
            return 0
        except Exception:
            return 0

    async def get_server(self, server_id: str) -> DirectoryServer | None:
        """
        Get server by ID from Supabase directory_view.
        """
        if not self._configured:
            error_msg = "SupabaseDirectoryRepository not configured"
            if self._config_error:
                error_msg += f": {self._config_error}"
            raise RuntimeError(error_msg)

        if self._supabase is None:
            raise RuntimeError("Supabase client not initialized")

        try:
            # Explicitly select columns matching DirectoryServer schema (minus rank fields)
            # This prevents failures if view accidentally includes extra columns (extra="forbid" in BaseSchema)
            # Try with join_password first (if migration 014 has been run)
            select_columns_with_password = (
                "id,name,description,map_name,join_address,join_password,join_instructions_pc,join_instructions_console,"
                "mod_list,rates,wipe_info,effective_status,status_source,last_seen_at,confidence,"
                "created_at,updated_at,cluster_id,cluster_name,cluster_slug,cluster_visibility,"
                "favorite_count,is_verified,is_new,is_stable,ruleset,game_mode,server_type,"
                "platforms,is_official_plus,is_modded,is_crossplay,is_console,is_pc,"
                "players_current,players_capacity,quality_score,uptime_percent"
            )
            response = (
                self._supabase.table("directory_view")
                .select(select_columns_with_password)
                .eq("id", server_id)
                .limit(1)
                .execute()
            )

            data = response.data if hasattr(response, "data") else []
            if not data:
                return None

            # Convert to DirectoryServer
            row = data[0]
            # Normalize array fields (handle Postgres array string format if needed)
            # DirectoryServer requires list, not Optional or string
            row["mod_list"] = self._normalize_array_field(row.get("mod_list"))
            row["platforms"] = self._normalize_array_field(row.get("platforms"))

            # Compute seconds_since_seen (request handling time)
            now_utc = datetime.now(timezone.utc)
            last_seen_at = row.get("last_seen_at")
            seconds_since_seen = None
            if last_seen_at:
                # Parse last_seen_at if it's a string
                if isinstance(last_seen_at, str):
                    last_seen_dt = datetime.fromisoformat(
                        last_seen_at.replace("Z", "+00:00")
                    )
                else:
                    last_seen_dt = last_seen_at

                # Ensure timezone-aware
                if last_seen_dt.tzinfo is None:
                    last_seen_dt = last_seen_dt.replace(tzinfo=timezone.utc)

                # Compute seconds_since_seen = now_utc - last_seen_at
                delta = (now_utc - last_seen_dt).total_seconds()
                seconds_since_seen = max(0.0, delta)  # Clamp negatives to 0

            # Set rank fields for consistency (rank_position=None for single fetch is fine)
            server = DirectoryServer(
                **row,
                seconds_since_seen=seconds_since_seen,
                rank_by="updated",  # Consistent with list_servers behavior
                rank_delta_24h=None,  # Placeholder for Sprint 5
            )
            return server

        except Exception as e:
            from postgrest.exceptions import APIError as PostgrestAPIError

            # If join_password or rulesets column doesn't exist (migration 014/015 not run), retry without them
            if isinstance(e, PostgrestAPIError) and (
                e.code == "42703" and ("join_password" in str(e) or "rulesets" in str(e))
            ):
                # Retry without join_password and without rulesets
                select_columns_without_password = (
                    "id,name,description,map_name,join_address,join_instructions_pc,join_instructions_console,"
                    "mod_list,rates,wipe_info,effective_status,status_source,last_seen_at,confidence,"
                    "created_at,updated_at,cluster_id,cluster_name,cluster_slug,cluster_visibility,"
                    "favorite_count,is_verified,is_new,is_stable,ruleset,game_mode,server_type,"
                    "platforms,is_official_plus,is_modded,is_crossplay,is_console,is_pc,"
                    "players_current,players_capacity,quality_score,uptime_percent"
                )
                response = (
                    self._supabase.table("directory_view")
                    .select(select_columns_without_password)
                    .eq("id", server_id)
                    .limit(1)
                    .execute()
                )
                
                data = response.data if hasattr(response, "data") else []
                if not data:
                    return None
                
                row = data[0]
                # Add join_password as None since column doesn't exist
                row["join_password"] = None
                # rulesets may not exist in view; derive from ruleset
                if "rulesets" not in row and row.get("ruleset"):
                    row["rulesets"] = [row["ruleset"]]
                
                # Normalize array fields
                row["mod_list"] = self._normalize_array_field(row.get("mod_list"))
                row["platforms"] = self._normalize_array_field(row.get("platforms"))
                
                # Compute seconds_since_seen
                now_utc = datetime.now(timezone.utc)
                last_seen_at = row.get("last_seen_at")
                seconds_since_seen = None
                if last_seen_at:
                    if isinstance(last_seen_at, str):
                        last_seen_dt = datetime.fromisoformat(
                            last_seen_at.replace("Z", "+00:00")
                        )
                    else:
                        last_seen_dt = last_seen_at
                    if last_seen_dt.tzinfo is None:
                        last_seen_dt = last_seen_dt.replace(tzinfo=timezone.utc)
                    delta = (now_utc - last_seen_dt).total_seconds()
                    seconds_since_seen = max(0.0, delta)
                
                server = DirectoryServer(
                    **row,
                    seconds_since_seen=seconds_since_seen,
                    rank_by="updated",
                    rank_delta_24h=None,
                )
                return server
            
            if isinstance(e, PostgrestAPIError) and e.code == "22P02":
                # Invalid UUID / invalid text representation → treat as not found
                return None
            import logging

            logger = logging.getLogger(__name__)
            logger.error(
                "Directory read error: failed to query directory_view for server",
                extra={
                    "error": str(e),
                    "error_type": type(e).__name__,
                    "read_operation": "get_server",
                    "server_id": server_id,
                },
                exc_info=True,
            )
            raise RuntimeError(
                f"Failed to query directory_view for server {server_id}: {str(e)}"
            ) from e

    async def get_filters(self) -> DirectoryFiltersResponse:
        """
        Get filter metadata for UI from Supabase.

        Returns available filter options, ranges, and defaults from directory_view.
        """
        if not self._configured:
            error_msg = "SupabaseDirectoryRepository not configured"
            if self._config_error:
                error_msg += f": {self._config_error}"
            raise RuntimeError(error_msg)

        if self._supabase is None:
            raise RuntimeError("Supabase client not initialized")

        try:
            # Query distinct values for filter options
            # Note: PostgREST doesn't support DISTINCT directly in select,
            # so we'll query all rows and extract distinct values in Python
            # For large datasets, this could be optimized with RPC functions or helper views later
            # Sprint 3: Add LIMIT safety to prevent loading entire table
            LIMIT_SAFETY = 10000  # Reasonable limit for Sprint 3

            # Get all servers to extract distinct values (with safety limit)
            all_servers_response = (
                self._supabase.table("directory_view")
                .select(
                    "ruleset,game_mode,effective_status,map_name,cluster_slug,cluster_name,players_current,uptime_percent,quality_score"
                )
                .limit(LIMIT_SAFETY)
                .execute()
            )

            all_servers = (
                all_servers_response.data
                if hasattr(all_servers_response, "data")
                else []
            )

            # Extract distinct values
            rulesets_set: set[str] = set()
            game_modes_set: set[str] = set()
            statuses_set: set[str] = set()
            maps_set: set[str] = set()
            clusters_dict: dict[str, str] = {}  # slug -> name

            players_values: list[int] = []
            uptime_values: list[float] = []
            quality_values: list[float] = []

            for row in all_servers:
                if row.get("ruleset"):
                    rulesets_set.add(row["ruleset"])
                if row.get("game_mode"):
                    game_modes_set.add(row["game_mode"])
                if row.get("effective_status"):
                    statuses_set.add(row["effective_status"])
                if row.get("map_name"):
                    maps_set.add(row["map_name"])
                if row.get("cluster_slug") and row.get("cluster_name"):
                    clusters_dict[row["cluster_slug"]] = row["cluster_name"]

                # Collect numeric values for ranges
                if row.get("players_current") is not None:
                    players_values.append(row["players_current"])
                if row.get("uptime_percent") is not None:
                    uptime_values.append(row["uptime_percent"])
                if row.get("quality_score") is not None:
                    quality_values.append(row["quality_score"])

            # Build response
            clusters_list = [
                ClusterInfo(slug=slug, name=name)
                for slug, name in clusters_dict.items()
            ]

            # Compute numeric ranges
            ranges = {
                "players": NumericRange(
                    min=min(players_values) if players_values else None,
                    max=max(players_values) if players_values else None,
                ),
                "uptime": NumericRange(
                    min=min(uptime_values) if uptime_values else None,
                    max=max(uptime_values) if uptime_values else None,
                ),
                "quality": NumericRange(
                    min=min(quality_values) if quality_values else None,
                    max=max(quality_values) if quality_values else None,
                ),
            }

            # Available rank_by options (from schema)
            rank_by_options: list[RankBy] = [
                "updated",
                "new",
                "favorites",
                "players",
                "quality",
                "uptime",
            ]

            return DirectoryFiltersResponse(
                rank_by=rank_by_options,
                rulesets=sorted(list(rulesets_set)),
                game_modes=sorted(list(game_modes_set)),
                statuses=sorted(list(statuses_set)),
                maps=sorted(list(maps_set)),
                clusters=clusters_list,
                ranges=ranges,
                defaults={},  # Can be populated later with UI defaults
            )

        except Exception as e:
            import logging

            logger = logging.getLogger(__name__)
            logger.error(
                "Directory read error: failed to query filter metadata",
                extra={
                    "error": str(e),
                    "error_type": type(e).__name__,
                    "read_operation": "get_filters",
                },
                exc_info=True,
            )
            raise RuntimeError(f"Failed to query filter metadata: {str(e)}") from e

    async def get_facets(self) -> dict[str, list[str]]:
        """
        Get available filter facets from Supabase directory_view.

        Returns distinct values for maps, mods, platforms, clusters.
        In Sprint 3, facets are "global distincts" (not filter-aware).
        """
        if not self._configured:
            error_msg = "SupabaseDirectoryRepository not configured"
            if self._config_error:
                error_msg += f": {self._config_error}"
            raise RuntimeError(error_msg)

        if self._supabase is None:
            raise RuntimeError("Supabase client not initialized")

        try:
            # Query all servers to extract distinct facet values
            # Note: For large datasets, this should be optimized with helper views or RPC functions
            # Sprint 3: Add LIMIT safety to prevent loading entire table
            LIMIT_SAFETY = 10000  # Reasonable limit for Sprint 3

            # Explicitly select only needed columns to avoid extra="forbid" issues
            select_columns = "map_name,mod_list,platforms,cluster_slug,cluster_name"
            all_servers_response = (
                self._supabase.table("directory_view")
                .select(select_columns)
                .limit(LIMIT_SAFETY)
                .execute()
            )

            all_servers = (
                all_servers_response.data
                if hasattr(all_servers_response, "data")
                else []
            )

            # Extract distinct values
            maps_set: set[str] = set()
            mods_set: set[str] = set()
            platforms_set: set[str] = set()
            clusters_set: set[str] = set()

            for row in all_servers:
                if row.get("map_name"):
                    maps_set.add(row["map_name"])

                # Extract mods from mod_list array
                if row.get("mod_list"):
                    mod_list = row["mod_list"]
                    if isinstance(mod_list, list):
                        for mod in mod_list:
                            if mod:
                                mods_set.add(str(mod))

                # Extract platforms from platforms array
                if row.get("platforms"):
                    platforms = row["platforms"]
                    if isinstance(platforms, list):
                        for platform in platforms:
                            if platform:
                                platforms_set.add(str(platform))

                if row.get("cluster_slug"):
                    clusters_set.add(row["cluster_slug"])

            return {
                "maps": sorted(list(maps_set)),
                "mods": sorted(list(mods_set)),
                "platforms": sorted(list(platforms_set)),
                "clusters": sorted(list(clusters_set)),
            }

        except Exception as e:
            import logging

            logger = logging.getLogger(__name__)
            logger.error(
                "Directory read error: failed to query facets",
                extra={
                    "error": str(e),
                    "error_type": type(e).__name__,
                    "read_operation": "get_facets",
                },
                exc_info=True,
            )
            raise RuntimeError(f"Failed to query facets: {str(e)}") from e
