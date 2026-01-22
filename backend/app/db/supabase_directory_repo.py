"""
Supabase directory repository for Sprint 3+.

Read-only repository that queries from directory_view in Supabase.
Fails fast if Supabase is not configured in non-local environments.
"""

from typing import Sequence

from app.core.config import get_settings
from app.core.errors import NotImplementedError
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

    def __init__(self):
        settings = get_settings()
        
        # Always initialize state explicitly
        self._supabase = None
        self._configured = False
        self._config_error: str | None = None
        
        if not settings.SUPABASE_URL or not settings.SUPABASE_ANON_KEY:
            if settings.ENV not in ("local", "development", "test"):
                raise RuntimeError(
                    "SupabaseDirectoryRepository requires SUPABASE_URL and SUPABASE_ANON_KEY in non-local environments"
                )
            # In local/dev/test, allow unconfigured state (will raise on actual use)
            self._config_error = "Supabase credentials not configured"
        else:
            # Credentials exist - attempt to initialize client
            try:
                from app.core.supabase import get_supabase_anon

                self._supabase = get_supabase_anon()
                if self._supabase is None:
                    raise RuntimeError("get_supabase_anon() returned None")
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
        page: int = 1,
        page_size: int = 50,
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
        maps: list[str] | None = None,  # Multi-select map names (OR)
        mods: list[str] | None = None,
        platforms: list[Platform] | None = None,  # Multi-select platforms (OR)
    ) -> tuple[Sequence[DirectoryServer], int]:
        """
        List servers from Supabase directory_view with filtering, pagination, and ranking.
        """
        if not self._configured:
            error_msg = "SupabaseDirectoryRepository not configured"
            if self._config_error:
                error_msg += f": {self._config_error}"
            raise RuntimeError(error_msg)

        if self._supabase is None:
            raise RuntimeError("Supabase client not initialized")

        # Build query from directory_view
        # Explicitly select columns matching DirectoryServer schema (minus rank fields computed in backend)
        # This prevents failures if view accidentally includes extra columns (extra="forbid" in BaseSchema)
        select_columns = (
            "id,name,description,map_name,join_address,join_instructions_pc,join_instructions_console,"
            "mod_list,rates,wipe_info,effective_status,status_source,last_seen_at,confidence,"
            "created_at,updated_at,cluster_id,cluster_name,cluster_slug,cluster_visibility,"
            "favorite_count,is_verified,is_new,is_stable,ruleset,game_mode,server_type,"
            "platforms,is_official_plus,is_modded,is_crossplay,is_console,is_pc,"
            "players_current,players_capacity,quality_score,uptime_percent"
        )
        query = self._supabase.table("directory_view").select(select_columns, count="exact")

        # Apply search filter (q parameter)
        # Search in name, description, map_name, cluster_name using OR
        # Note: This is the ONLY place we use .or_() - multiple .or_() calls overwrite each other
        if q and (q_trimmed := q.strip()):
            # PostgREST OR syntax: or=(field1.ilike.*value*,field2.ilike.*value*)
            # Format: "field1.ilike.*value*,field2.ilike.*value*"
            or_conditions = ",".join([
                f"name.ilike.%{q_trimmed}%",
                f"description.ilike.%{q_trimmed}%",
                f"map_name.ilike.%{q_trimmed}%",
                f"cluster_name.ilike.%{q_trimmed}%"
            ])
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
            platforms_clean = [str(p).strip().lower() for p in platforms if str(p).strip()]
            if platforms_clean:
                # Use array overlap operator (ov - overlaps)
                # PostgREST: platforms.ov.{platform1,platform2} checks if arrays overlap
                # This gives us OR semantics - server matches if its platforms overlap with any requested platform
                query = query.overlaps("platforms", platforms_clean)

        # SQL ordering (Sprint 3 rule - always ORDER BY updated_at with id tiebreaker)
        # Always use updated_at regardless of requested rank_by (others fallback to updated)
        # Note: id tiebreaker is always ASC regardless of main sort direction
        # NULLS LAST is handled by PostgREST default behavior for DESC, but we document it for clarity
        if order == "asc":
            # ASC: updated_at ASC NULLS LAST, id ASC
            query = query.order("updated_at", desc=False).order("id", desc=False)
        else:
            # DESC: updated_at DESC NULLS LAST, id ASC
            query = query.order("updated_at", desc=True).order("id", desc=False)

        # Handle pagination (LIMIT/OFFSET)
        offset = (page - 1) * page_size
        query = query.range(offset, offset + page_size - 1)

        # Execute query
        try:
            response = query.execute()
        except Exception as e:
            raise RuntimeError(f"Failed to query directory_view: {str(e)}") from e

        # Extract data and count
        data = response.data if hasattr(response, "data") else []
        # Handle count properly - if None, we can't provide accurate total
        total = getattr(response, "count", None)
        if total is None:
            # If count="exact" didn't return a count, we can't provide accurate total
            # DirectoryResponse.total requires int >= 0, so return 0 to indicate "unknown"
            # This is a fallback - count="exact" should normally work
            total = 0  # Indicates count unavailable (unknown total)

        # Convert to DirectoryServer objects
        servers: list[DirectoryServer] = []
        for idx, row in enumerate(data):
            try:
                # Compute rank_position in Python (global rank within sorted/filtered dataset)
                # Formula: (page - 1) * page_size + idx + 1
                rank_position = (page - 1) * page_size + idx + 1

                # Normalize array fields (handle Postgres array string format if needed)
                # DirectoryServer requires list, not Optional or string
                row["mod_list"] = self._normalize_array_field(row.get("mod_list"))
                row["platforms"] = self._normalize_array_field(row.get("platforms"))

                # Create DirectoryServer with rank fields
                server = DirectoryServer(
                    **row,
                    rank_position=rank_position,
                    rank_by=rank_by,
                    rank_delta_24h=None,  # Placeholder for Sprint 4
                )
                servers.append(server)
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
                    raise RuntimeError(f"Failed to parse server row from directory_view: {e}") from e

        return servers, total

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
            select_columns = (
                "id,name,description,map_name,join_address,join_instructions_pc,join_instructions_console,"
                "mod_list,rates,wipe_info,effective_status,status_source,last_seen_at,confidence,"
                "created_at,updated_at,cluster_id,cluster_name,cluster_slug,cluster_visibility,"
                "favorite_count,is_verified,is_new,is_stable,ruleset,game_mode,server_type,"
                "platforms,is_official_plus,is_modded,is_crossplay,is_console,is_pc,"
                "players_current,players_capacity,quality_score,uptime_percent"
            )
            response = (
                self._supabase.table("directory_view")
                .select(select_columns)
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
            # Set rank fields for consistency (rank_position=None for single fetch is fine)
            server = DirectoryServer(
                **row,
                rank_by="updated",  # Consistent with list_servers behavior
                rank_delta_24h=None,  # Placeholder for Sprint 4
            )
            return server

        except Exception as e:
            raise RuntimeError(f"Failed to query directory_view for server {server_id}: {str(e)}") from e

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
                .select("ruleset,game_mode,effective_status,map_name,cluster_slug,cluster_name,players_current,uptime_percent,quality_score")
                .limit(LIMIT_SAFETY)
                .execute()
            )

            all_servers = all_servers_response.data if hasattr(all_servers_response, "data") else []

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
            rank_by_options: list[RankBy] = ["updated", "new", "favorites", "players", "quality", "uptime"]

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

            all_servers = all_servers_response.data if hasattr(all_servers_response, "data") else []

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
            raise RuntimeError(f"Failed to query facets: {str(e)}") from e
