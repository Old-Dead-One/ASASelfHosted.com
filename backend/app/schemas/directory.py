"""
Directory schemas.

Pydantic models for directory_view responses.
This is the single source of truth for directory data contracts.
All API responses should use these schemas.
"""

from datetime import datetime
from typing import Literal

from app.schemas.base import BaseSchema


# Type aliases matching database enums
ServerStatus = Literal["online", "offline", "unknown"]
StatusSource = Literal["manual", "agent"]
GameMode = Literal["pvp", "pve"]
ServerType = Literal["vanilla", "boosted"]
ClusterVisibility = Literal["public", "unlisted"]


class DirectoryServer(BaseSchema):
    """
    Directory server response schema.

    This matches the directory_view output exactly.
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
    join_password: str | None = None  # Gated by favorites
    join_instructions_pc: str | None = None
    join_instructions_console: str | None = None

    # Server configuration
    mod_list: list[str] | None = None
    rates: str | None = None
    wipe_info: str | None = None
    pvp_enabled: bool = False
    vanilla: bool = False

    # Status (effective status from servers table)
    effective_status: ServerStatus
    status_source: StatusSource | None = None
    last_seen_at: datetime | None = None
    confidence: str | None = None  # RYG logic in Sprint 2

    # Timestamps
    created_at: datetime
    updated_at: datetime

    # Cluster info (if associated)
    cluster_id: str | None = None
    cluster_name: str | None = None
    cluster_slug: str | None = None
    cluster_visibility: ClusterVisibility | None = None

    # Owner info
    owner_display_name: str | None = None

    # Aggregates
    favorite_count: int = 0

    # Badge flags (computed in directory_view)
    is_verified: bool = False
    is_new: bool = False
    is_stable: bool = False
    game_mode: GameMode
    server_type: ServerType


class DirectoryResponse(BaseSchema):
    """
    Directory list response.

    Wraps DirectoryServer list with pagination metadata.
    """

    data: list[DirectoryServer]
    total: int
    page: int = 1
    page_size: int = 50
