"""
Directory endpoints.

Read-only endpoints for public server directory.
Uses directory_view read model (mock in Sprint 1, real Supabase in Sprint 2+).
"""

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Query

from app.core.deps import get_optional_user
from app.core.errors import DomainValidationError, NotFoundError
from app.core.security import UserIdentity
from app.db.directory_clusters_repo import DirectoryClustersRepository
from app.db.directory_repo import DirectoryRepository
from app.db.providers import get_directory_clusters_repo, get_directory_repo
from app.schemas.directory import (
    DirectoryCluster,
    DirectoryClustersResponse,
    DirectoryResponse,
    DirectoryFiltersResponse,
    DirectoryServer,
    ServerStatus,
    RankBy,
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

router = APIRouter(prefix="/directory", tags=["directory"])


@router.get("/servers", response_model=DirectoryResponse)
async def list_directory_servers(
    limit: int = Query(default=25, ge=1, le=100, description="Maximum items to return (max 100)"),
    cursor: str | None = Query(default=None, description="Opaque cursor for pagination (from previous response)"),
    q: str | None = Query(default=None, description="Search query (searches name, description, map name, cluster name)"),
    status: ServerStatus | None = Query(default=None, description="Filter by server status"),
    mode: VerificationMode | None = Query(
        default=None, description="Filter by verification mode (manual, verified)"
    ),
    rank_by: RankBy = Query(default="updated", description="Rank/sort servers by"),
    order: SortOrder = Query(default="desc", description="Sort order for rank_by"),
    view: DirectoryView = Query(default="card", description="UI view hint (card/compact)"),
    # Core server trait filters
    ruleset: Ruleset | None = Query(
        default=None, description="Filter by ruleset (vanilla, vanilla_qol, boosted, modded)"
    ),
    game_mode: GameMode | None = Query(
        default=None, description="Filter by game mode (pve, pvp, pvpve)"
    ),
    # TODO (Sprint 3+): Remove server_type filter - use ruleset instead
    # Note: If both ruleset and server_type are provided, ruleset takes precedence.
    server_type: ServerType | None = Query(
        default=None, description="Filter by server type (vanilla, boosted) - Deprecated: use ruleset"
    ),
    map_name: str | None = Query(default=None, description="Filter by map name (string match)"),
    cluster: str | None = Query(
        default=None, description="Filter by cluster slug or name (string match)"
    ),
    cluster_visibility: ClusterVisibility | None = Query(
        default=None, description="Filter by cluster visibility (public, unlisted)"
    ),
    cluster_id: str | None = Query(default=None, description="Filter by specific cluster ID"),
    # Player filters
    # Canonical parameters (use these)
    players_current_min: int | None = Query(
        default=None, ge=0, description="Minimum current player count"
    ),
    players_current_max: int | None = Query(
        default=None, ge=0, description="Maximum current player count"
    ),
    # Deprecated aliases (use players_current_min/max instead)
    players_min: int | None = Query(
        default=None, ge=0, description="Deprecated: use players_current_min instead"
    ),
    players_max: int | None = Query(
        default=None, ge=0, description="Deprecated: use players_current_max instead"
    ),
    # Numeric range filters
    uptime_min: float | None = Query(
        default=None, ge=0, le=100, description="Minimum uptime percent (0-100)"
    ),
    quality_min: float | None = Query(
        default=None, ge=0, le=100, description="Minimum quality score (0-100)"
    ),
    # Tri-state filters (any = no filter, true = include only, false = exclude)
    official_plus: TriState = Query(
        default="any", description="Filter official+ servers (any/true/false)"
    ),
    modded: TriState = Query(
        default="any",
        description="Filter servers that have mods installed (any/true/false). Note: This checks for installed mods, not ruleset classification. Use ruleset='modded' for gameplay classification."
    ),
    crossplay: TriState = Query(
        default="any", description="Filter crossplay support (any/true/false)"
    ),
    console: TriState = Query(default="any", description="Filter console support (any/true/false)"),
    pc: TriState = Query(default="any", description="Filter PC support (any/true/false)"),
    # Multi-select filters (OR semantics)
    maps: list[str] | None = Query(default=None, description="Filter by map names (OR)"),
    mods: list[str] | None = Query(default=None, description="Filter by mod names (OR)"),
    platforms: list[Platform] | None = Query(default=None, description="Filter by platforms (OR)"),
    repo: DirectoryRepository = Depends(get_directory_repo),
    _user: UserIdentity | None = Depends(get_optional_user),
):
    """
    List public servers from directory view with cursor pagination.

    Public endpoint - no authentication required.
    Returns servers from directory_view (public read model).
    
    Cursor pagination provides deterministic results under concurrent updates.
    Use `cursor` from previous response to get next page.
    
    User context is available for personalized data (favorites, etc.) in future.
    """
    # Enforce max limit (400 error if > 100)
    if limit > 100:
        raise DomainValidationError(f"limit must be <= 100, got {limit}")
    
    # Normalize players_min/max to players_current_min/max for repository
    # Use explicit None check (0 is valid and falsy)
    effective_players_min = players_current_min if players_current_min is not None else players_min
    effective_players_max = players_current_max if players_current_max is not None else players_max

    # Enforce precedence: if both ruleset and server_type are provided, ruleset takes precedence
    effective_server_type = None if ruleset else server_type

    # Get request handling time (consistent across all items in response)
    now_utc = datetime.now(timezone.utc)

    servers, next_cursor = await repo.list_servers(
        limit=limit,
        cursor=cursor,
        q=q,
        status=status,
        mode=mode,
        rank_by=rank_by,
        order=order,
        view=view,
        ruleset=ruleset,
        game_mode=game_mode,
        server_type=effective_server_type,
        map_name=map_name,
        cluster=cluster,
        cluster_visibility=cluster_visibility,
        cluster_id=cluster_id,
        players_current_min=effective_players_min,
        players_current_max=effective_players_max,
        uptime_min=uptime_min,
        quality_min=quality_min,
        official_plus=official_plus,
        modded=modded,
        crossplay=crossplay,
        console=console,
        pc=pc,
        maps=maps,
        mods=mods,
        platforms=platforms,
        now_utc=now_utc,
    )

    return DirectoryResponse(
        data=list(servers),
        limit=limit,
        cursor=cursor,
        next_cursor=next_cursor,
        rank_by=rank_by,
        order=order,
        view=view,
    )


@router.get("/servers/{server_id}", response_model=DirectoryServer)
async def get_directory_server(
    server_id: str,
    repo: DirectoryRepository = Depends(get_directory_repo),
    _user: UserIdentity | None = Depends(get_optional_user),
):
    """
    Get server details by ID from directory view.

    Public endpoint - returns server if it's in the public directory.
    User context is available for personalized data in future.
    """
    server = await repo.get_server(server_id)
    if not server:
        raise NotFoundError("server", server_id)

    return server


@router.get("/filters", response_model=DirectoryFiltersResponse)
async def get_directory_filters(
    repo: DirectoryRepository = Depends(get_directory_repo),
):
    """
    Get filter metadata for UI.

    Returns available filter options, ranges, and defaults.
    Frontend uses this to populate filter dropdowns/toggles without hardcoding options.
    
    Repository implementation determines availability:
    - MockDirectoryRepository: Returns mock data derived from available servers
    - SupabaseDirectoryRepository: Returns real data from Supabase (Sprint 2+)
    """
    # Let the repository implementation handle capability checks
    # If not implemented, repo will raise app.core.errors.NotImplementedError (HTTP 501)
    filters = await repo.get_filters()
    return filters


@router.get("/clusters", response_model=DirectoryClustersResponse)
async def list_directory_clusters(
    limit: int = Query(default=25, ge=1, le=100, description="Maximum items to return (max 100)"),
    cursor: str | None = Query(default=None, description="Opaque cursor for pagination (from previous response)"),
    visibility: ClusterVisibility | None = Query(
        default=None, description="Filter by visibility (public/unlisted). If None, returns public only."
    ),
    sort_by: str = Query(default="updated", description="Sort clusters by (updated or name)"),
    order: SortOrder = Query(default="desc", description="Sort order for sort_by"),
    repo: DirectoryClustersRepository = Depends(get_directory_clusters_repo),
    _user: UserIdentity | None = Depends(get_optional_user),
):
    """
    List public clusters from directory with cursor pagination.

    Public endpoint - no authentication required.
    Returns clusters from clusters table.
    
    Cursor pagination provides deterministic results under concurrent updates.
    Use `cursor` from previous response to get next page.
    
    Visibility Rules:
        - If visibility is None: returns only public clusters (default)
        - If visibility is "public": returns only public clusters
        - If visibility is "unlisted": returns only unlisted clusters (requires explicit filter)
    """
    # Enforce max limit (400 error if > 100)
    if limit > 100:
        raise DomainValidationError(f"limit must be <= 100, got {limit}")
    
    # Validate sort_by
    if sort_by not in ("updated", "name"):
        raise DomainValidationError(f"sort_by must be 'updated' or 'name', got {sort_by}")
    
    # Get request handling time (consistent across all items in response)
    now_utc = datetime.now(timezone.utc)

    clusters, next_cursor = await repo.list_clusters(
        limit=limit,
        cursor=cursor,
        visibility=visibility,
        sort_by=sort_by,
        order=order,
        now_utc=now_utc,
    )

    return DirectoryClustersResponse(
        data=list(clusters),
        limit=limit,
        cursor=cursor,
        next_cursor=next_cursor,
        sort_by=sort_by,
        order=order,
    )


@router.get("/clusters/{cluster_id}", response_model=DirectoryCluster)
async def get_directory_cluster(
    cluster_id: str,
    repo: DirectoryClustersRepository = Depends(get_directory_clusters_repo),
    _user: UserIdentity | None = Depends(get_optional_user),
):
    """
    Get cluster details by ID from directory.

    Public endpoint - returns cluster if it's accessible.
    
    Visibility Rules:
        - public: returns cluster (readable by everyone)
        - unlisted: returns cluster if found (may require owner authentication due to RLS)
        - private: does not exist in DB enum, so not applicable
    
    Note: Unlisted clusters may not be accessible via this endpoint if RLS policies
    restrict access to owners only. This is a known limitation that may require
    RLS policy adjustments for full unlisted cluster support.
    """
    # Get request handling time
    now_utc = datetime.now(timezone.utc)
    
    cluster = await repo.get_cluster(cluster_id, now_utc=now_utc)
    if not cluster:
        raise NotFoundError("cluster", cluster_id)

    return cluster


@router.post("/servers/search", include_in_schema=False)
async def advanced_search(
    _user: UserIdentity | None = Depends(get_optional_user),
):
    """
    Advanced boolean search endpoint (not implemented, hidden from schema).

    This endpoint is reserved for future advanced search with AND/OR/NOT logic.
    Returns 501 Not Implemented until Sprint 3+.
    
    Hidden from OpenAPI schema until implemented to avoid advertising unsupported features.
    """
    from app.core.errors import NotImplementedError

    raise NotImplementedError("Advanced boolean filtering coming soon")
