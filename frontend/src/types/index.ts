/**
 * Type definitions for the application.
 *
 * Shared types used across the frontend.
 *
 * Note: APIError is defined in lib/api.ts (single source of truth)
 */

// ============================================================================
// DIRECTORY SERVER CONTRACT
// This is the single source of truth for directory data from directory_view
// All frontend components should use this type
// Matches backend schema/directory.py exactly
// ============================================================================

export type ServerStatus = 'online' | 'offline' | 'unknown'
export type StatusSource = 'manual' | 'agent'
export type VerificationMode = 'manual' | 'verified'
export type GameMode = 'pvp' | 'pve' | 'pvpve'
export type Ruleset = 'vanilla' | 'vanilla_qol' | 'boosted' | 'modded'
// TODO (Sprint 3+): Remove ServerType - replaced by Ruleset for clearer classification
export type ServerType = 'vanilla' | 'boosted' // Deprecated: use ruleset instead
export type Confidence = 'red' | 'yellow' | 'green'
export type ClusterVisibility = 'public' | 'unlisted'
export type Platform = 'steam' | 'xbox' | 'playstation' | 'windows_store' | 'epic'

// Directory rank/sort contract (extensible)
export type RankBy = 'updated' | 'new' | 'favorites' | 'players' | 'quality' | 'uptime'
export type SortOrder = 'asc' | 'desc'
export type DirectoryView = 'card' | 'compact'

// Tri-state filter type (any = no filter, true = include only, false = exclude)
export type TriState = 'any' | 'true' | 'false'

export interface DirectoryServer {
    // Core identity
    id: string
    name: string
    description: string | null
    map_name: string | null

    // Join information
    join_address: string | null
    join_password: string | null  // Server password (public, visible to all players)
    join_instructions_pc: string | null
    join_instructions_console: string | null
    discord_url: string | null
    website_url: string | null

    // Server configuration
    mod_list: string[] // Always a list, never null
    rates: string | null
    wipe_info: string | null

    // Status (effective status from servers table)
    effective_status: ServerStatus
    status_source: StatusSource | null
    last_seen_at: string | null // ISO datetime
    confidence: Confidence | null // RYG logic in Sprint 2

    // Timestamps (ISO datetime strings)
    created_at: string // ISO datetime
    updated_at: string // ISO datetime

    // Cluster info (if associated)
    cluster_id: string | null
    cluster_name: string | null
    cluster_slug: string | null
    cluster_visibility: ClusterVisibility | null

    // Owner info removed from public directory for privacy
    // Add back later with explicit user visibility controls if needed

    // Aggregates
    favorite_count: number

    // Player stats (optional; real values will come from agents/heartbeats later)
    players_current: number | null
    players_capacity: number | null // Maximum player capacity
    // TODO (Sprint 3+): Remove players_max alias - use players_capacity only
    players_max: number | null // Deprecated alias for players_capacity

    // Scoring (optional; real values arrive Sprint 2+)
    quality_score: number | null // e.g. 0-100
    uptime_24h: number | null // e.g. 0.0-1.0 (legacy alias)
    uptime_percent: number | null // e.g. 0.0-100.0 (canonical field)

    // Ranking (computed by backend for the chosen rank_by)
    // rank is global within the sorted dataset (not page-local)
    rank: number | null // Legacy alias
    rank_position: number | null // Canonical field
    rank_by: RankBy | null
    // Trending indicator (NOT a filter). Positive = moved up (better rank).
    // rank_delta_24h = prev_rank - current_rank
    rank_delta_24h: number | null

    // Badge flags (computed in directory_view)
    is_verified: boolean
    is_new: boolean
    is_stable: boolean

    // Classification
    ruleset: Ruleset | null
    rulesets?: string[] // Multi-value when supported (migration 015); at most one of vanilla/vanilla_qol/modded; boosted optional
    // TODO (Sprint 3+): Remove server_type - fully replaced by ruleset
    server_type: ServerType | null // Deprecated: use ruleset instead

    // Game mode (mutually exclusive: pvp, pve, or pvpve)
    game_mode: GameMode | null

    // Platform and feature flags (computed in directory_view)
    platforms: Platform[] // Known platform universe for type safety
    is_official_plus: boolean | null // Vanilla-style setup (vanilla-like experience; "Official" refers to who owns the server)
    is_modded: boolean | null // Has mods (derived from mod_list). Note: This checks for installed mods, not ruleset classification
    is_crossplay: boolean | null // Cross-platform support
    is_console: boolean | null // Console support
    is_pc: boolean | null // PC support (canonical)
    // TODO (Sprint 3+): Remove is_PC alias - use is_pc only
    is_PC: boolean | null // Deprecated alias (auto-populated from is_pc by backend)
}

export interface DirectoryResponse {
    data: DirectoryServer[]
    limit: number
    cursor: string | null
    next_cursor: string | null

    /** Total servers matching current filters (only set on first page). */
    total?: number

    // Optional echo for debugging / client UI (reflects actual applied values)
    rank_by: RankBy | null
    order: SortOrder | null
    view: DirectoryView | null
}

// Badge types (UI-only, may include values not in API contract)
// Some badges are derived from API fields (verified, new, stable, pvp/pve, vanilla/boosted)
// Others are UI-derived (newbie_friendly, learning_friendly) and not part of the directory contract
export type BadgeType =
    | 'verified'
    | 'new'
    | 'stable'
    | 'pvp'
    | 'pve'
    | 'pvpve'
    | 'vanilla'
    | 'vanilla_qol'
    | 'boosted'
    | 'modded'
    | 'newbie_friendly' // UI-only, not in API contract
    | 'learning_friendly' // UI-only, not in API contract

// ============================================================================
// OTHER DOMAIN TYPES
// ============================================================================

// Cluster types (minimal for MVP)
export interface Cluster {
    id: string
    name: string
    slug: string
    visibility: 'public' | 'unlisted'
    owner_user_id: string
}

// Public directory cluster (GET /api/v1/directory/clusters)
export interface DirectoryCluster {
    id: string
    name: string
    slug: string
    visibility: ClusterVisibility
    created_at: string
    updated_at: string
    server_count: number
}

export interface DirectoryClustersResponse {
    data: DirectoryCluster[]
    limit: number
    cursor: string | null
    next_cursor: string | null
    sort_by?: string
    order?: string
}
