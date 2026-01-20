/**
 * Type definitions for the application.
 *
 * Shared types used across the frontend.
 */

// API Error types (matching backend)
export interface APIError {
    error: {
        code: string
        message: string
        details?: Record<string, string>
    }
}

// ============================================================================
// DIRECTORY SERVER CONTRACT
// This is the single source of truth for directory data from directory_view
// All frontend components should use this type
// ============================================================================

export type ServerStatus = 'online' | 'offline' | 'unknown'
export type StatusSource = 'manual' | 'agent'
export type GameMode = 'pvp' | 'pve'
export type ServerType = 'vanilla' | 'boosted'

export interface DirectoryServer {
    // Core identity
    id: string
    name: string
    description: string | null
    map_name: string | null

    // Join information
    join_address: string | null
    join_password: string | null // Gated by favorites
    join_instructions_pc: string | null
    join_instructions_console: string | null

    // Server configuration
    mod_list: string[] | null
    rates: string | null
    wipe_info: string | null
    pvp_enabled: boolean
    vanilla: boolean

    // Status (effective status from servers table)
    effective_status: ServerStatus
    status_source: StatusSource | null
    last_seen_at: string | null
    confidence: string | null // RYG logic in Sprint 2

    // Timestamps
    created_at: string
    updated_at: string

    // Cluster info (if associated)
    cluster_id: string | null
    cluster_name: string | null
    cluster_slug: string | null
    cluster_visibility: 'public' | 'unlisted' | null

    // Owner info
    owner_display_name: string | null

    // Aggregates
    favorite_count: number

    // Badge flags (computed in directory_view)
    is_verified: boolean
    is_new: boolean
    is_stable: boolean
    game_mode: GameMode
    server_type: ServerType
}

// ============================================================================
// LEGACY TYPES (to be migrated to DirectoryServer)
// ============================================================================

// Server types (legacy - use DirectoryServer instead)
export interface Server {
    id: string
    name: string
    description: string | null
    verification_status: 'unverified' | 'pending' | 'verified' | 'revoked' | 'expired'
    // TODO: Migrate to DirectoryServer
}

// Cluster types
export interface Cluster {
    id: string
    name: string
    slug: string
    visibility: 'public' | 'unlisted'
    // TODO: Add all cluster fields
}

// Verification types
export interface VerificationStatus {
    server_id: string
    status: string
    verified_at: string | null
}

// Consent types
export interface Consent {
    id: string
    consent_type: string
    resource_id: string
    granted_at: string
    expires_at: string | null
    revoked_at: string | null
}

// Badge types (computed, never purchased)
export type BadgeType =
    | 'verified'
    | 'new'
    | 'stable'
    | 'pvp'
    | 'pve'
    | 'vanilla'
    | 'boosted'
    | 'newbie_friendly'
    | 'learning_friendly'
