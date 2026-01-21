"""
Supabase directory repository for Sprint 2+.

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
)


class SupabaseDirectoryRepository(DirectoryRepository):
    """
    Supabase-based directory repository.
    
    Queries from directory_view (read-only, public-safe).
    Fails fast if Supabase is not configured.
    """

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
        List servers from Supabase directory_view.
        
        Planned for Sprint 2: Minimum query with updated ranking.
        Full filtering and ranking logic planned for Sprint 3+.
        """
        if not self._configured:
            error_msg = "SupabaseDirectoryRepository not configured"
            if self._config_error:
                error_msg += f": {self._config_error}"
            raise RuntimeError(error_msg)

        # TODO (Sprint 2): Implement basic query with updated ranking
        # TODO (Sprint 3+): Implement full filtering and ranking logic
        raise NotImplementedError("SupabaseDirectoryRepository.list_servers not implemented (Sprint 2+)")

    async def get_server(self, server_id: str) -> DirectoryServer | None:
        """
        Get server by ID from Supabase directory_view.
        
        Planned for Sprint 2: Basic implementation.
        """
        if not self._configured:
            error_msg = "SupabaseDirectoryRepository not configured"
            if self._config_error:
                error_msg += f": {self._config_error}"
            raise RuntimeError(error_msg)

        # TODO (Sprint 2): Implement basic get by ID
        raise NotImplementedError("SupabaseDirectoryRepository.get_server not implemented (Sprint 2+)")

    async def get_filters(self) -> DirectoryFiltersResponse:
        """
        Get filter metadata for UI from Supabase.
        
        Planned for Sprint 2: Query distinct values, ranges, and defaults from directory_view.
        """
        if not self._configured:
            error_msg = "SupabaseDirectoryRepository not configured"
            if self._config_error:
                error_msg += f": {self._config_error}"
            raise RuntimeError(error_msg)

        # TODO (Sprint 2): Query filter metadata from directory_view
        raise NotImplementedError("SupabaseDirectoryRepository.get_filters not implemented (Sprint 2+)")

    async def get_facets(self) -> dict[str, list[str]]:
        """
        Get available filter facets from Supabase directory_view.
        
        Planned for Sprint 2: Query distinct values from directory_view or related tables.
        """
        if not self._configured:
            error_msg = "SupabaseDirectoryRepository not configured"
            if self._config_error:
                error_msg += f": {self._config_error}"
            raise RuntimeError(error_msg)

        # TODO (Sprint 2): Query distinct values from directory_view
        raise NotImplementedError("SupabaseDirectoryRepository.get_facets not implemented (Sprint 2+)")
