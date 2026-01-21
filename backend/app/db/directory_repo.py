"""
Directory repository interface.

Abstract interface for directory read operations.
This is the seam where mock data (Sprint 1) plugs into real Supabase (Sprint 2+).
"""

from abc import ABC, abstractmethod
from typing import Sequence

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


class DirectoryRepository(ABC):
    """
    Abstract repository for directory read operations.
    
    Implementations:
    - MockDirectoryRepository: Mock data for Sprint 1
    - SupabaseDirectoryRepository: Real Supabase queries (Sprint 2+)
    """

    @abstractmethod
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
        # Core server trait filters
        ruleset: Ruleset | None = None,
        game_mode: GameMode | None = None,
        # TODO (Sprint 3+): Remove server_type filter - use ruleset instead
        # Note: If both ruleset and server_type are provided, ruleset takes precedence.
        server_type: ServerType | None = None,  # Deprecated: use ruleset instead
        map_name: str | None = None,  # Single map filter (string match)
        cluster: str | None = None,  # Filter by cluster slug or name (string match)
        cluster_visibility: ClusterVisibility | None = None,
        cluster_id: str | None = None,
        # Player filters
        players_current_min: int | None = None,
        players_current_max: int | None = None,
        # Numeric range filters
        uptime_min: float | None = None,  # Minimum uptime percent (0-100)
        quality_min: float | None = None,  # Minimum quality score (0-100)
        # Tri-state filters (any = no filter, true = include only, false = exclude)
        official_plus: TriState = "any",
        modded: TriState = "any",
        crossplay: TriState = "any",
        console: TriState = "any",
        pc: TriState = "any",  # PC support filter (canonical name)
        # Multi-select filters (OR semantics)
        maps: list[str] | None = None,  # Multi-select map names (OR)
        mods: list[str] | None = None,
        platforms: list[Platform] | None = None,  # Multi-select platforms (OR)
    ) -> tuple[Sequence[DirectoryServer], int]:
        """
        List servers from directory view.
        
        Args:
            page: Page number (1-indexed)
            page_size: Items per page
            q: Optional search query (server name, description, map name, cluster name)
            status: Optional status filter (online, offline, unknown)
            mode: Optional verification mode filter (manual, verified)
            rank_by: Which metric to rank/sort by
            order: Sort order for rank_by
            view: UI view hint (card/compact). Repository must not branch logic on this parameter.
            ruleset: Filter by ruleset (vanilla, vanilla_qol, boosted, modded)
            game_mode: Filter by game mode (pve, pvp, pvpve)
            server_type: Filter by server type (vanilla, boosted) - Deprecated: use ruleset instead.
                If both ruleset and server_type are provided, ruleset takes precedence.
            map_name: Single map filter (string match)
            maps: Multi-select filter for map names (OR semantics)
            cluster: Filter by cluster slug or name (string match)
            cluster_visibility: Filter by cluster visibility (public, unlisted)
            cluster_id: Filter by specific cluster ID
            players_current_min: Minimum current player count
            players_current_max: Maximum current player count
            uptime_min: Minimum uptime percent (0-100)
            quality_min: Minimum quality score (0-100)
            official_plus: Tri-state filter for official+ servers (any/true/false)
            modded: Tri-state filter for "has mods installed" (any/true/false).
                Note: This checks for installed mods, not ruleset classification.
                Use ruleset='modded' for gameplay classification.
            crossplay: Tri-state filter for crossplay support (any/true/false)
            console: Tri-state filter for console support (any/true/false)
            pc: Tri-state filter for PC support (any/true/false)
            mods: Multi-select filter for mod names (OR semantics)
            platforms: Multi-select filter for platforms (OR semantics)
            
        Returns:
            Tuple of (server list, total count)
        """
        ...

    @abstractmethod
    async def get_facets(self) -> dict[str, list[str]]:
        """
        Get available filter facets from directory data.
        
        Returns:
            Dictionary mapping facet names to lists of available values.
            Expected keys (may include additional keys):
                - "maps": List of available map names
                - "mods": List of available mod names
                - "platforms": List of available platform values
                - "clusters": List of available cluster names/slugs
                - "server_types": List of available server types (deprecated, may be removed)
                - "game_modes": List of available game modes
                - "statuses": List of available server statuses
            
            Example: {
                "maps": ["The Island", "Ragnarok"],
                "mods": ["S+ Structures"],
                "platforms": ["steam", "xbox"],
                "clusters": ["sun-bros-cluster"],
                "game_modes": ["pvp", "pve", "pvpve"],
                "statuses": ["online", "offline", "unknown"]
            }
        """
        ...

    @abstractmethod
    async def get_filters(self) -> DirectoryFiltersResponse:
        """
        Get filter metadata for UI.
        
        Returns:
            DirectoryFiltersResponse with available filter options, ranges, and defaults.
        """
        ...

    @abstractmethod
    async def get_server(self, server_id: str) -> DirectoryServer | None:
        """
        Get server by ID.
        
        Args:
            server_id: Server UUID
            
        Returns:
            DirectoryServer if found, None otherwise
        """
        ...
