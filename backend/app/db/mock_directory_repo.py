"""
Mock directory repository for Sprint 1.

Returns mock data matching DirectoryServer schema.
This allows frontend development without Supabase.
"""

from datetime import datetime, timedelta, timezone
from typing import Literal, Sequence

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
    ClusterInfo,
    NumericRange,
    VerificationMode,
    Platform,
)

_NOW = datetime.now(timezone.utc)

# Mock servers matching DirectoryServer schema exactly
# 6-10 servers with variation: PvE/PvP, clustered/non-clustered, passworded, different statuses, different maps
MOCK_SERVERS: list[DirectoryServer] = [
    DirectoryServer(
        id="srv-001",
        name="Sun Bros | The Island",
        description="Vanilla-ish rates, chill PvE cluster. Great for new players learning the game.",
        map_name="The Island",
        join_address="play.sunbros.ark:7777",
        join_instructions_pc="Direct Connect: play.sunbros.ark:7777",
        join_instructions_console="Add server: play.sunbros.ark:7777",
        rates="1x XP, 1x Harvest, 1x Taming",
        wipe_info="Monthly wipes on first Sunday",
        effective_status="online",
        status_source="agent",
        last_seen_at=_NOW - timedelta(minutes=2),
        confidence="green",
        created_at=_NOW - timedelta(days=45),
        updated_at=_NOW - timedelta(minutes=2),
        cluster_id="cluster-001",
        cluster_name="Sun Bros Cluster",
        cluster_slug="sun-bros",
        cluster_visibility="public",
        favorite_count=23,
        players_current=45,
        players_capacity=70,
        players_max=70,  # Deprecated alias
        quality_score=88.5,
        uptime_24h=0.98,
        rank_delta_24h=2,
        is_verified=True,
        is_new=False,
        is_stable=True,
        ruleset="vanilla",  # Pure vanilla, no mods
        game_mode="pve",
        server_type="vanilla",  # Deprecated
        platforms=["steam", "xbox"],
        is_official_plus=False,
        is_modded=False,
        is_crossplay=True,
        is_console=True,
        is_pc=True,
        uptime_percent=98.0,
    ),
    DirectoryServer(
        id="srv-002",
        name="Sun Bros | Scorched Earth",
        description="Scorched Earth map in the Sun Bros cluster. Same rates as The Island.",
        map_name="Scorched Earth",
        join_address="play.sunbros.ark:7787",
        join_instructions_pc="Direct Connect: play.sunbros.ark:7787",
        join_instructions_console="Add server: play.sunbros.ark:7787",
        rates="1x XP, 1x Harvest, 1x Taming",
        wipe_info="Monthly wipes on first Sunday",
        effective_status="online",
        status_source="agent",
        last_seen_at=_NOW - timedelta(minutes=5),
        confidence="green",
        created_at=_NOW - timedelta(days=45),
        updated_at=_NOW - timedelta(minutes=5),
        cluster_id="cluster-001",
        cluster_name="Sun Bros Cluster",
        cluster_slug="sun-bros",
        cluster_visibility="public",
        favorite_count=12,
        players_current=28,
        players_capacity=70,
        players_max=70,  # Deprecated alias
        quality_score=85.0,
        uptime_24h=0.97,
        rank_delta_24h=-1,
        is_verified=True,
        is_new=False,
        is_stable=True,
        ruleset="vanilla",  # Pure vanilla, no mods
        game_mode="pve",
        server_type="vanilla",  # Deprecated
        platforms=["steam", "xbox"],
        is_official_plus=False,
        is_modded=False,
        is_crossplay=True,
        is_console=True,
        is_pc=True,
        uptime_percent=98.0,
    ),
    DirectoryServer(
        id="srv-003",
        name="Thunder Dome PvP",
        description="High-stakes PvP server. Boosted rates, weekly wipes. Not for the faint of heart.",
        map_name="The Island",
        join_address="thunderdome.arkpvp.net:7777",
        join_instructions_pc="Direct Connect: thunderdome.arkpvp.net:7777",
        join_instructions_console="Add server: thunderdome.arkpvp.net:7777",
        mod_list=["S+ Structures", "Dino Storage v2"],
        rates="5x XP, 3x Harvest, 10x Taming",
        wipe_info="Weekly wipes every Friday",
        effective_status="online",
        status_source="manual",
        last_seen_at=_NOW - timedelta(hours=1),
        confidence="yellow",
        created_at=_NOW - timedelta(days=120),
        updated_at=_NOW - timedelta(hours=1),
        cluster_id=None,
        cluster_name=None,
        cluster_slug=None,
        cluster_visibility=None,
        favorite_count=67,
        players_current=184,
        players_capacity=188,
        players_max=188,  # Deprecated alias
        quality_score=92.5,
        uptime_24h=0.99,
        rank_delta_24h=3,
        is_verified=False,
        is_new=False,
        is_stable=True,
        ruleset="boosted",  # Significant rate changes (5x XP, 10x Taming)
        game_mode="pvp",
        server_type="boosted",  # Deprecated
        platforms=["steam"],
        is_official_plus=False,
        is_modded=True,  # Has mods
        is_crossplay=False,
        is_console=False,
        is_pc=True,
        uptime_percent=99.0,
    ),
    DirectoryServer(
        id="srv-004",
        name="Newbie Haven",
        description="Learning-friendly server with helpful admins and community guides. Perfect for first-time players.",
        map_name="The Island",
        join_address="newbie.arklearn.com:7777",
        join_instructions_pc="Direct Connect: newbie.arklearn.com:7777",
        join_instructions_console="Add server: newbie.arklearn.com:7777",
        mod_list=["S+ Structures", "Awesome Spyglass"],
        rates="2x XP, 2x Harvest, 3x Taming",
        wipe_info="No wipes planned",
        effective_status="online",
        status_source="agent",
        last_seen_at=_NOW - timedelta(minutes=15),
        confidence="green",
        created_at=_NOW - timedelta(days=7),
        updated_at=_NOW - timedelta(minutes=15),
        cluster_id=None,
        cluster_name=None,
        cluster_slug=None,
        cluster_visibility=None,
        favorite_count=89,
        players_current=156,
        players_capacity=200,
        players_max=200,  # Deprecated alias
        quality_score=95.0,
        uptime_24h=1.0,
        rank_delta_24h=5,
        is_verified=True,
        is_new=True,
        is_stable=False,
        ruleset="vanilla_qol",  # Minor rate changes (2x) + QoL mods
        game_mode="pve",
        server_type="boosted",  # Deprecated
        platforms=["steam", "xbox", "playstation"],
        is_official_plus=False,
        is_modded=True,
        is_crossplay=True,
        is_console=True,
        is_pc=True,
        uptime_percent=100.0,
    ),
    DirectoryServer(
        id="srv-005",
        name="Lost Ark Cluster",
        description="Multi-map cluster with all official maps. Cross-server transfers enabled.",
        map_name="Aberration",
        join_address="aberration.lostark.cluster:7777",
        join_instructions_pc="Direct Connect: aberration.lostark.cluster:7777",
        join_instructions_console="Add server: aberration.lostark.cluster:7777",
        mod_list=["S+ Structures", "Dino Storage v2", "Automated Ark", "Ark Eternal"],
        rates="1.5x XP, 1.5x Harvest, 2x Taming",
        wipe_info="Seasonal wipes",
        effective_status="offline",
        status_source="agent",
        last_seen_at=_NOW - timedelta(hours=3),
        confidence="red",
        created_at=_NOW - timedelta(days=200),
        updated_at=_NOW - timedelta(hours=3),
        cluster_id="cluster-002",
        cluster_name="Lost Ark Cluster",
        cluster_slug="lost-ark",
        cluster_visibility="public",
        favorite_count=145,
        players_current=0,
        players_capacity=100,
        players_max=100,  # Deprecated alias
        quality_score=75.0,
        uptime_24h=0.45,
        rank_delta_24h=-5,
        is_verified=True,
        is_new=False,
        is_stable=False,
        ruleset="modded",  # Major gameplay mods (Ark Eternal, Automated Ark) with minor rate tweaks
        game_mode="pvpve",  # Mix of PvP and PvE
        server_type="boosted",  # Deprecated
        platforms=["steam"],
        is_official_plus=False,
        is_modded=True,
        is_crossplay=False,
        is_console=False,
        is_pc=True,
        uptime_percent=45.0,
    ),
    DirectoryServer(
        id="srv-006",
        name="Hardcore Vanilla",
        description="True vanilla experience. No mods, no boosted rates. Old-school Ark.",
        map_name="The Island",
        join_address="vanilla.arkclassic.net:7777",
        join_instructions_pc="Direct Connect: vanilla.arkclassic.net:7777",
        join_instructions_console="Add server: vanilla.arkclassic.net:7777",
        rates="1x XP, 1x Harvest, 1x Taming",
        wipe_info="Never wiped",
        effective_status="unknown",
        status_source=None,
        last_seen_at=None,
        confidence=None,
        created_at=_NOW - timedelta(days=365),
        updated_at=_NOW - timedelta(days=30),
        cluster_id=None,
        cluster_name=None,
        cluster_slug=None,
        cluster_visibility=None,
        favorite_count=34,
        players_current=None,
        players_capacity=None,
        players_max=None,  # Deprecated alias
        is_verified=False,
        is_new=False,
        is_stable=True,
        ruleset="vanilla",  # Pure vanilla, no mods
        game_mode="pve",
        server_type="vanilla",  # Deprecated
        platforms=["steam"],
        is_official_plus=True,
        is_modded=False,
        is_crossplay=False,
        is_console=False,
        is_pc=True,
        uptime_percent=None,
    ),
    DirectoryServer(
        id="srv-007",
        name="Ragnarok Adventure",
        description="Large map server with boosted rates. Active community and events.",
        map_name="Ragnarok",
        join_address="rag.arkadventure.io:7777",
        join_instructions_pc="Direct Connect: rag.arkadventure.io:7777",
        join_instructions_console="Add server: rag.arkadventure.io:7777",
        mod_list=["S+ Structures", "Castles, Keeps, and Forts"],
        rates="4x XP, 4x Harvest, 6x Taming",
        wipe_info="Quarterly wipes",
        effective_status="online",
        status_source="agent",
        last_seen_at=_NOW - timedelta(minutes=8),
        confidence="green",
        created_at=_NOW - timedelta(days=90),
        updated_at=_NOW - timedelta(minutes=8),
        cluster_id=None,
        cluster_name=None,
        cluster_slug=None,
        cluster_visibility=None,
        favorite_count=156,
        players_current=142,
        players_capacity=150,
        players_max=150,  # Deprecated alias
        quality_score=90.0,
        uptime_24h=0.96,
        rank_delta_24h=1,
        is_verified=True,
        is_new=False,
        is_stable=True,
        ruleset="boosted",  # Significant rate changes (4x XP, 6x Taming)
        game_mode="pvpve",  # Mix of PvP and PvE
        server_type="boosted",  # Deprecated
        platforms=["steam", "xbox"],
        is_official_plus=False,
        is_modded=True,
        is_crossplay=True,
        is_console=True,
        is_pc=True,
        uptime_percent=96.0,
    ),
    DirectoryServer(
        id="srv-008",
        name="Extinction PvP Arena",
        description="PvP-focused Extinction server. Fast-paced combat, regular tournaments.",
        map_name="Extinction",
        join_address="extinction.arkarena.com:7777",
        join_instructions_pc="Direct Connect: extinction.arkarena.com:7777",
        join_instructions_console="Add server: extinction.arkarena.com:7777",
        mod_list=["S+ Structures", "PvP Tools"],
        rates="10x XP, 5x Harvest, 15x Taming",
        wipe_info="Bi-weekly wipes",
        effective_status="online",
        status_source="manual",
        last_seen_at=_NOW - timedelta(minutes=30),
        confidence="yellow",
        created_at=_NOW - timedelta(days=60),
        updated_at=_NOW - timedelta(minutes=30),
        cluster_id=None,
        cluster_name=None,
        cluster_slug=None,
        cluster_visibility=None,
        favorite_count=203,
        players_current=198,
        players_capacity=200,
        players_max=200,  # Deprecated alias
        quality_score=94.0,
        uptime_24h=0.98,
        rank_delta_24h=-2,
        is_verified=False,
        is_new=False,
        is_stable=True,
        ruleset="boosted",  # Very significant rate changes (10x XP, 15x Taming)
        game_mode="pvp",
        server_type="boosted",  # Deprecated
        platforms=["steam"],
        is_official_plus=False,
        is_modded=True,
        is_crossplay=False,
        is_console=False,
        is_pc=True,
        uptime_percent=98.0,
    ),
    DirectoryServer(
        id="srv-009",
        name="Genesis Learning Server",
        description="New player friendly Genesis server. Tutorials and guides available.",
        map_name="Genesis Part 1",
        join_address="genesis.arklearn.com:7777",
        join_instructions_pc="Direct Connect: genesis.arklearn.com:7777",
        join_instructions_console="Add server: genesis.arklearn.com:7777",
        mod_list=["S+ Structures", "Awesome Spyglass", "Dino Tracker"],
        rates="2x XP, 2x Harvest, 3x Taming",
        wipe_info="No wipes",
        effective_status="online",
        status_source="agent",
        last_seen_at=_NOW - timedelta(minutes=1),
        confidence="green",
        created_at=_NOW - timedelta(days=14),
        updated_at=_NOW - timedelta(minutes=1),
        cluster_id=None,
        cluster_name=None,
        cluster_slug=None,
        cluster_visibility=None,
        favorite_count=45,
        players_current=78,
        players_capacity=100,
        players_max=100,  # Deprecated alias
        quality_score=87.5,
        uptime_24h=0.94,
        rank_delta_24h=4,
        is_verified=True,
        is_new=True,
        is_stable=False,
        ruleset="vanilla_qol",  # Minor rate changes (2x) + QoL mods
        game_mode="pve",
        server_type="boosted",  # Deprecated
        platforms=["steam", "playstation"],
        is_official_plus=False,
        is_modded=True,
        is_crossplay=True,
        is_console=True,
        is_pc=True,
        uptime_percent=94.0,
    ),
    DirectoryServer(
        id="srv-010",
        name="Valguero Exploration",
        description="Explore Valguero with a friendly community. Casual PvE gameplay.",
        map_name="Valguero",
        join_address="valguero.arkexplore.net:7777",
        join_instructions_pc="Direct Connect: valguero.arkexplore.net:7777",
        join_instructions_console="Add server: valguero.arkexplore.net:7777",
        mod_list=["S+ Structures"],
        rates="2x XP, 2x Harvest, 2x Taming",
        wipe_info="Rare wipes, only for major updates",
        effective_status="online",
        status_source="agent",
        last_seen_at=_NOW - timedelta(minutes=12),
        confidence="green",
        created_at=_NOW - timedelta(days=180),
        updated_at=_NOW - timedelta(minutes=12),
        cluster_id=None,
        cluster_name=None,
        cluster_slug=None,
        cluster_visibility=None,
        favorite_count=78,
        players_current=None,
        players_capacity=None,
        players_max=None,  # Deprecated alias
        is_verified=True,
        is_new=False,
        is_stable=True,
        ruleset="vanilla_qol",  # Minor rate changes (2x) + QoL mod (S+ Structures)
        game_mode="pve",
        server_type="boosted",  # Deprecated
        platforms=["steam", "xbox"],
        is_official_plus=False,
        is_modded=True,
        is_crossplay=True,
        is_console=True,
        is_pc=True,
        uptime_percent=97.0,
    ),
]


class MockDirectoryRepository(DirectoryRepository):
    """
    Mock directory repository for Sprint 1.
    
    Returns mock data matching DirectoryServer schema.
    Allows frontend development without Supabase.
    """

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
        List servers with filtering and pagination.
        
        Simple mock implementation - filters and paginates in memory.
        """
        servers = list(MOCK_SERVERS)

        # Apply search filter (trim and validate query)
        if q:
            q_lower = q.strip().lower()
            if q_lower:
                servers = [
                    s
                    for s in servers
                    if q_lower in s.name.lower()
                    or (s.description and q_lower in s.description.lower())
                    or (s.map_name and q_lower in s.map_name.lower())
                    or (s.cluster_name and q_lower in s.cluster_name.lower())
                ]

        # Apply status filter
        if status:
            servers = [s for s in servers if s.effective_status == status]

        # Apply mode filter
        # Note: mode refers to verification mode (is_verified), NOT status_source
        # mode="manual" = unverified listings, mode="verified" = verified listings
        # This is separate from status_source which indicates how status was determined (manual vs agent)
        if mode == "manual":
            servers = [s for s in servers if not s.is_verified]
        elif mode == "verified":
            servers = [s for s in servers if s.is_verified]

        # Apply core server trait filters
        # Note: If both ruleset and server_type are provided, ruleset takes precedence.
        if ruleset:
            servers = [s for s in servers if s.ruleset == ruleset]
        elif server_type:  # Only apply server_type if ruleset not provided
            servers = [s for s in servers if s.server_type == server_type]
        if game_mode:
            servers = [s for s in servers if s.game_mode == game_mode]
        if map_name:
            map_lower = map_name.strip().lower()
            servers = [
                s
                for s in servers
                if s.map_name and map_lower in s.map_name.lower()
            ]
        if cluster:
            cluster_lower = cluster.strip().lower()
            servers = [
                s
                for s in servers
                if (s.cluster_slug and cluster_lower in s.cluster_slug.lower())
                or (s.cluster_name and cluster_lower in s.cluster_name.lower())
            ]
        if cluster_visibility:
            servers = [s for s in servers if s.cluster_visibility == cluster_visibility]
        if cluster_id:
            servers = [s for s in servers if s.cluster_id == cluster_id]

        # Apply player filters
        if players_current_min is not None:
            servers = [
                s
                for s in servers
                if s.players_current is not None and s.players_current >= players_current_min
            ]
        if players_current_max is not None:
            servers = [
                s
                for s in servers
                if s.players_current is not None and s.players_current <= players_current_max
            ]

        # Apply numeric range filters
        if uptime_min is not None:
            servers = [
                s
                for s in servers
                if s.uptime_percent is not None and s.uptime_percent >= uptime_min
            ]
        if quality_min is not None:
            servers = [
                s
                for s in servers
                if s.quality_score is not None and s.quality_score >= quality_min
            ]

        # Apply tri-state filters
        # Helper to normalize tri-state: "any" -> None, "true" -> True, "false" -> False
        def _normalize_tristate(ts: TriState) -> bool | None:
            if ts == "any":
                return None
            return ts == "true"

        official_plus_val = _normalize_tristate(official_plus)
        if official_plus_val is not None:
            # Tri-state: unknown (None) does not match true or false
            servers = [
                s
                for s in servers
                if s.is_official_plus is not None and s.is_official_plus == official_plus_val
            ]

        modded_val = _normalize_tristate(modded)
        if modded_val is not None:
            # Note: modded filter checks "has mods installed" (is_modded or derived from mod_list)
            # This is NOT the same as ruleset="modded" (which is a gameplay classification)
            # For example, vanilla_qol servers can have QoL mods but are not "modded" by ruleset
            # Derive is_modded from mod_list if not explicitly set
            servers = [
                s
                for s in servers
                if (
                    (s.is_modded is not None and s.is_modded == modded_val)
                    or (s.is_modded is None and (len(s.mod_list) > 0) == modded_val)
                )
            ]

        crossplay_val = _normalize_tristate(crossplay)
        if crossplay_val is not None:
            # Tri-state: unknown (None) does not match true or false
            servers = [
                s
                for s in servers
                if s.is_crossplay is not None and s.is_crossplay == crossplay_val
            ]

        console_val = _normalize_tristate(console)
        if console_val is not None:
            # Tri-state: unknown (None) does not match true or false
            servers = [
                s
                for s in servers
                if s.is_console is not None and s.is_console == console_val
            ]

        pc_val = _normalize_tristate(pc)
        if pc_val is not None:
            # Tri-state: unknown (None) does not match true or false
            servers = [
                s
                for s in servers
                if s.is_pc is not None and s.is_pc == pc_val
            ]

        # Apply multi-select filters (OR semantics)
        if maps:
            maps_set = {m.lower() for m in maps}
            servers = [
                s for s in servers if s.map_name and s.map_name.lower() in maps_set
            ]

        if mods:
            # Exact match on mod names (case-insensitive)
            mods_set = {m.lower() for m in mods}
            servers = [
                s
                for s in servers
                if any(mod.lower() in mods_set for mod in s.mod_list)
            ]

        if platforms:
            # Convert to strings and normalize to lowercase for comparison
            platforms_set = {str(p).lower() for p in platforms}
            servers = [
                s
                for s in servers
                if any(str(plat).lower() in platforms_set for plat in s.platforms)
            ]

        # Ranking/sorting
        # Always add a stable tiebreaker (id) so rank is deterministic.
        reverse = order == "desc"

        def _safe_num(v, default=0):
            return v if isinstance(v, (int, float)) else default

        if rank_by == "updated":
            servers.sort(key=lambda s: (s.updated_at, s.created_at, s.id), reverse=reverse)
        elif rank_by == "new":
            # Sort by created_at DESC (newest listings first)
            servers.sort(key=lambda s: (s.created_at, s.id), reverse=reverse)
        elif rank_by == "favorites":
            # Fallback to updated if favorites not available
            servers.sort(key=lambda s: (_safe_num(s.favorite_count), s.updated_at, s.id), reverse=reverse)
        elif rank_by == "players":
            # Fallback to updated if players not available
            servers.sort(key=lambda s: (_safe_num(s.players_current), s.updated_at, s.id), reverse=reverse)
        elif rank_by == "quality":
            # Fallback to updated if quality not available
            servers.sort(key=lambda s: (_safe_num(s.quality_score), s.updated_at, s.id), reverse=reverse)
        elif rank_by == "uptime":
            # Sort by uptime_percent (canonical, 0-100 scale)
            # Fallback to updated if uptime not available
            servers.sort(key=lambda s: (_safe_num(s.uptime_percent), s.updated_at, s.id), reverse=reverse)
        else:
            # Future-proof fallback
            servers.sort(key=lambda s: (s.updated_at, s.created_at, s.id), reverse=True)

        # Calculate pagination
        total = len(servers)
        start = (page - 1) * page_size
        end = start + page_size
        paginated_servers = servers[start:end]

        # Assign rank + rank_by on returned objects only (don't mutate global list)
        # Global rank within sorted/filtered dataset:
        #   rank = absolute index + 1
        results: list[DirectoryServer] = []
        for idx, s in enumerate(paginated_servers, start=start):
            rank_pos = idx + 1
            # Use canonical uptime_percent if present, otherwise derive from uptime_24h
            # Don't overwrite if it already exists
            uptime_percent = (
                s.uptime_percent
                if s.uptime_percent is not None
                else (s.uptime_24h * 100.0 if s.uptime_24h is not None else None)
            )
            
            # Pydantic BaseModel copy depends on your BaseSchema config.
            # If BaseSchema is Pydantic v2, use model_copy(update=...).
            # If v1, use copy(update=...).
            try:
                s2 = s.model_copy(
                    update={
                        "rank": rank_pos,  # Legacy alias
                        "rank_position": rank_pos,  # Canonical field
                        "rank_by": rank_by,
                        "uptime_percent": uptime_percent,
                    }
                )
            except AttributeError:
                s2 = s.copy(
                    update={
                        "rank": rank_pos,
                        "rank_position": rank_pos,
                        "rank_by": rank_by,
                        "uptime_percent": uptime_percent,
                    }
                )
            results.append(s2)

        return results, total

    async def get_filters(self) -> DirectoryFiltersResponse:
        """
        Get filter metadata for UI.
        
        Derives available filter options, ranges, and defaults from mock data.
        """
        # Extract distinct values from mock servers
        maps_set: set[str] = set()
        clusters_dict: dict[str, str] = {}  # slug -> name
        rulesets_set: set[str] = set()
        game_modes_set: set[str] = set()
        statuses_set: set[str] = set()
        
        players_values: list[int] = []
        uptime_values: list[float] = []
        quality_values: list[float] = []
        
        for server in MOCK_SERVERS:
            if server.map_name:
                maps_set.add(server.map_name)
            if server.cluster_slug and server.cluster_name:
                clusters_dict[server.cluster_slug] = server.cluster_name
            if server.ruleset:
                rulesets_set.add(server.ruleset)
            if server.game_mode:
                game_modes_set.add(server.game_mode)
            statuses_set.add(server.effective_status)
            
            if server.players_current is not None:
                players_values.append(server.players_current)
            if server.uptime_percent is not None:
                uptime_values.append(server.uptime_percent)
            if server.quality_score is not None:
                quality_values.append(server.quality_score)
        
        # Build clusters list
        clusters_list = [
            ClusterInfo(slug=slug, name=name)
            for slug, name in sorted(clusters_dict.items())
        ] if clusters_dict else None
        
        # Calculate ranges
        ranges = {
            "players": NumericRange(
                min=float(min(players_values)) if players_values else None,
                max=float(max(players_values)) if players_values else None,
            ),
            "uptime": NumericRange(
                min=float(min(uptime_values)) if uptime_values else None,
                max=float(max(uptime_values)) if uptime_values else None,
            ),
            "quality": NumericRange(
                min=float(min(quality_values)) if quality_values else None,
                max=float(max(quality_values)) if quality_values else None,
            ),
        }
        
        # Get rank_by options (hardcoded for mock metadata - matches RankBy Literal)
        rank_by_options = ["updated", "new", "favorites", "players", "quality", "uptime"]
        
        return DirectoryFiltersResponse(
            rank_by=rank_by_options,
            rulesets=sorted(list(rulesets_set)),
            game_modes=sorted(list(game_modes_set)),
            statuses=sorted(list(statuses_set)),
            maps=sorted(list(maps_set)),
            clusters=clusters_list,
            ranges=ranges,
            defaults={
                "rank_by": "updated",
                "page_size": 50,
                "status": None,
                "mode": None,
            },
        )

    async def get_facets(self) -> dict[str, list[str]]:
        """
        Get available filter facets from mock data.
        
        Extracts distinct values for maps, mods, platforms, server types, game modes, and statuses.
        """
        facets: dict[str, set[str]] = {
            "maps": set(),
            "mods": set(),
            "platforms": set(),
            "server_types": set(),
            "game_modes": set(),
            "statuses": set(),
        }

        for server in MOCK_SERVERS:
            if server.map_name:
                facets["maps"].add(server.map_name)
            for mod in server.mod_list:
                facets["mods"].add(mod)
            for platform in server.platforms:
                facets["platforms"].add(platform)
            if server.server_type:
                facets["server_types"].add(server.server_type)
            if server.game_mode:
                facets["game_modes"].add(server.game_mode)
            facets["statuses"].add(server.effective_status)

        # Convert sets to sorted lists for consistent output
        return {
            "maps": sorted(list(facets["maps"])),
            "mods": sorted(list(facets["mods"])),
            "platforms": sorted(list(facets["platforms"])),
            "server_types": sorted(list(facets["server_types"])),
            "game_modes": sorted(list(facets["game_modes"])),
            "statuses": sorted(list(facets["statuses"])),
        }

    async def get_server(self, server_id: str) -> DirectoryServer | None:
        """Get server by ID."""
        return next((s for s in MOCK_SERVERS if s.id == server_id), None)
