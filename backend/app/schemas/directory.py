"""
Directory schemas.

Pydantic models for directory_view responses.
This is the single source of truth for directory data contracts.
All API responses should use these schemas.
"""

from datetime import datetime
from typing import Literal

from pydantic import Field, model_validator

from app.schemas.base import BaseSchema


# Type aliases matching database enums
ServerStatus = Literal["online", "offline", "unknown"]
StatusSource = Literal["manual", "agent"]
VerificationMode = Literal["manual", "verified"]  # Server verification/listing mode
GameMode = Literal["pvp", "pve", "pvpve"]
Ruleset = Literal["vanilla", "vanilla_qol", "boosted", "modded"]
# TODO (Sprint 3+): Remove ServerType - replaced by Ruleset for clearer classification
ServerType = Literal["vanilla", "boosted"]  # Deprecated: use ruleset instead
ClusterVisibility = Literal["public", "unlisted"]
Confidence = Literal["red", "yellow", "green"]

# Directory rank/sort contract (extensible)
RankBy = Literal["updated", "new", "favorites", "players", "quality", "uptime"]
SortOrder = Literal["asc", "desc"]
DirectoryView = Literal["card", "compact"]

# Tri-state filter type (any = no filter, true = include only, false = exclude)
TriState = Literal["any", "true", "false"]

# Platform types (known universe for type safety)
Platform = Literal["steam", "xbox", "playstation", "windows_store", "epic"]

# Hosting provider (internal validation only; not exposed in directory/UI)
HostingProvider = Literal["self_hosted", "nitrado", "official", "other_managed"]


class DirectoryServer(BaseSchema):
    """
    Directory server response schema.

    The directory_view provides the persisted fields from the database.
    The backend adds computed rank fields (rank_position, rank_delta_24h, rank_by)
    and legacy field aliases (players_max, uptime_24h, rank, is_PC).

    All directory endpoints should return this schema.
    Frontend TypeScript type must match this structure.
    """

    # Core identity
    id: str
    name: str
    description: str | None = None
    map_name: str | None = None

    # Join information
    join_address: str | None = None
    join_password: str | None = None  # Server password (public, visible to all players)
    join_instructions_pc: str | None = None
    join_instructions_console: str | None = None

    # Server configuration
    mod_list: list[str] = Field(default_factory=list)  # Always a list, never None
    rates: str | None = None
    wipe_info: str | None = None
    # Removed pvp_enabled and vanilla - use game_mode and server_type instead

    # Status (effective status from servers table)
    effective_status: ServerStatus
    status_source: StatusSource | None = None  # None is valid (unknown source)
    # Note: status_source and is_verified are independent:
    # - status_source: Where the status came from (manual entry vs agent detection)
    # - is_verified: Listing trust flag (curated/verified listing, regardless of status source)
    # Examples:
    #   - status_source="manual" + is_verified=True = Manually entered status, but listing is verified/curated
    #   - status_source="agent" + is_verified=True = Agent-detected status, listing is verified/curated
    #   - status_source="manual" + is_verified=False = Manually entered status, listing not verified
    last_seen_at: datetime | None = None
    seconds_since_seen: float | None = (
        None  # Seconds since last_seen_at (computed server-side, null if last_seen_at is null)
    )
    confidence: Confidence | None = None  # RYG logic in Sprint 2

    # Timestamps
    created_at: datetime
    updated_at: datetime

    # Cluster info (if associated)
    cluster_id: str | None = None
    cluster_name: str | None = None
    cluster_slug: str | None = None
    cluster_visibility: ClusterVisibility | None = None

    # Owner info removed from public directory for privacy
    # Add back later with explicit user visibility controls if needed

    # Aggregates
    favorite_count: int = 0

    # Player stats (optional; real values will come from agents/heartbeats later)
    players_current: int | None = None
    players_capacity: int | None = None  # Maximum player capacity (canonical)
    # TODO (Sprint 3+): Remove players_max alias - use players_capacity only
    players_max: int | None = (
        None  # Deprecated alias (auto-populated from players_capacity)
    )

    # Scoring (optional; real values arrive Sprint 2+)
    quality_score: float | None = None  # e.g. 0-100
    uptime_percent: float | None = None  # e.g. 0.0-100.0 (canonical field)
    # TODO (Sprint 3+): Remove uptime_24h alias - use uptime_percent only
    uptime_24h: float | None = (
        None  # Deprecated alias (auto-populated from uptime_percent)
    )

    # Ranking (computed by backend for the chosen rank_by)
    # rank is global within the sorted dataset (not page-local)
    rank_position: int | None = None  # Canonical field
    # TODO (Sprint 3+): Remove rank alias - use rank_position only
    rank: int | None = None  # Deprecated alias (auto-populated from rank_position)
    rank_by: RankBy | None = None
    # Trending indicator (NOT a filter). Positive = moved up (better rank).
    # rank_delta_24h = prev_rank - current_rank
    rank_delta_24h: int | None = None

    # Badge flags (computed in directory_view)
    is_verified: bool = False
    is_new: bool = False
    is_stable: bool = False

    # Classification
    ruleset: Ruleset | None = None  # Legacy/primary; use rulesets for multi-value
    rulesets: list[str] = Field(default_factory=list)  # Multi-value: at most one of vanilla/vanilla_qol/modded; boosted optional
    # TODO (Sprint 3+): Remove server_type - fully replaced by ruleset
    server_type: ServerType | None = None  # Deprecated: use ruleset instead

    # Game mode (mutually exclusive: pvp, pve, or pvpve)
    game_mode: GameMode | None = None

    # Platform and feature flags (computed in directory_view)
    platforms: list[Platform] = Field(default_factory=list)
    is_official_plus: bool | None = (
        None  # Vanilla-style setup (vanilla-like experience). "Official" = who owns server; "Vanilla" = how it's set up.
    )
    is_modded: bool | None = None  # Has mods (derived from mod_list)
    is_crossplay: bool | None = None  # Cross-platform support
    is_console: bool | None = None  # Console support
    is_pc: bool | None = None  # PC support (canonical)
    # TODO (Sprint 3+): Remove is_PC alias - use is_pc only
    is_PC: bool | None = None  # Deprecated alias (auto-populated from is_pc)

    @model_validator(mode="after")
    def populate_legacy_fields(self) -> "DirectoryServer":
        """
        Auto-populate legacy field aliases from canonical fields.

        This ensures backwards compatibility while using canonical field names.
        Legacy fields are populated automatically if not explicitly set.
        """
        # Auto-populate players_max from players_capacity
        if self.players_max is None and self.players_capacity is not None:
            self.players_max = self.players_capacity

        # Auto-populate uptime_24h from uptime_percent (convert 0-100 to 0-1)
        if self.uptime_24h is None and self.uptime_percent is not None:
            self.uptime_24h = self.uptime_percent / 100.0

        # Auto-populate rank from rank_position
        if self.rank is None and self.rank_position is not None:
            self.rank = self.rank_position

        # Auto-populate is_PC from is_pc
        if self.is_PC is None and self.is_pc is not None:
            self.is_PC = self.is_pc

        return self


class DirectoryResponse(BaseSchema):
    """
    Directory list response.

    Wraps DirectoryServer list with cursor pagination metadata.
    """

    data: list[DirectoryServer]
    limit: int
    cursor: str | None = None  # Opaque cursor for next page
    next_cursor: str | None = None  # Opaque cursor for next page (if more results)

    # Total matching servers for current filters (only set when cursor is None / first page)
    total: int | None = None

    # Optional echo for debugging / client UI (reflects actual applied values)
    rank_by: RankBy | None = None
    order: SortOrder | None = None
    view: DirectoryView | None = None


class ClusterInfo(BaseSchema):
    """Cluster information for filter facets."""

    slug: str
    name: str


class NumericRange(BaseSchema):
    """Min/max range for numeric filters."""

    min: float | None = None
    max: float | None = None


class DirectoryFiltersResponse(BaseSchema):
    """
    Filter metadata response.

    Returns available filter options and defaults for UI.
    Frontend uses this to populate filter dropdowns/toggles.
    """

    # Available filter options (using Literal types for type safety)
    rank_by: list[RankBy] = Field(description="Available rank_by options")
    rulesets: list[Ruleset] = Field(description="Available ruleset values")
    game_modes: list[GameMode] = Field(description="Available game_mode values")
    statuses: list[ServerStatus] = Field(description="Available status values")
    maps: list[str] = Field(description="Available map names")
    clusters: list[ClusterInfo] = Field(
        default_factory=list, description="Available clusters"
    )

    # Numeric ranges (known keys for type safety)
    ranges: dict[Literal["players", "uptime", "quality"], NumericRange] = Field(
        description="Min/max ranges for numeric filters (players, uptime, quality)"
    )

    # UI defaults (loose typing to allow any value type)
    defaults: dict[str, object] = Field(
        description="Default filter values for UI initial state"
    )


class DirectoryCluster(BaseSchema):
    """
    Directory cluster response schema.

    Minimal cluster information for public directory.
    """

    id: str
    name: str
    slug: str
    visibility: ClusterVisibility
    created_at: datetime
    updated_at: datetime
    server_count: int = 0  # Number of servers in this cluster (optional, for future)


class DirectoryClustersResponse(BaseSchema):
    """
    Directory clusters list response.

    Wraps DirectoryCluster list with cursor pagination metadata.
    """

    data: list[DirectoryCluster]
    limit: int
    cursor: str | None = None  # Opaque cursor for current page
    next_cursor: str | None = None  # Opaque cursor for next page (if more results)

    # Optional echo for debugging / client UI
    sort_by: str | None = None
    order: SortOrder | None = None
