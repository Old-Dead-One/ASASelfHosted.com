/**
 * API client configuration and utilities.
 *
 * All API calls go through this module.
 * Provides consistent error handling and request formatting.
 *
 * NOTE:
 * Frontend runs on :3000
 * Backend API runs on :5173
 * Override with VITE_API_BASE_URL in other environments.
 */

const API_BASE_URL =
    import.meta.env.VITE_API_BASE_URL || 'http://localhost:5173'

/**
 * Temporary session cache for immediate use after sign-in.
 * 
 * When a user signs in, we store the session here for immediate API calls.
 * After a few seconds, we clear it and rely on Supabase's stored session.
 * This handles the timing issue where Supabase hasn't fully stored the session yet.
 */
let cachedSession: { access_token: string; expires_at?: number } | null = null
let cacheExpiry: number = 0
const CACHE_DURATION_MS = 5000 // 5 seconds - enough time for Supabase to store session

/**
 * Cache a session token for immediate use.
 * Called after signInWithPassword to provide immediate token access.
 */
export function cacheAuthSession(session: { access_token: string; expires_at?: number } | null) {
    cachedSession = session
    if (session) {
        cacheExpiry = Date.now() + CACHE_DURATION_MS
    } else {
        cacheExpiry = 0
    }
}

/**
 * Clear the cached session (called after onAuthStateChange confirms session is stored).
 */
export function clearCachedSession() {
    cachedSession = null
    cacheExpiry = 0
}

/**
 * Standard API error response format.
 * Backend always returns errors in this structure.
 */
export interface APIError {
    error: {
        code: string
        message: string
        details?: Record<string, string>
    }
}

/**
 * Custom error class for API errors.
 * Allows catching and handling API errors specifically.
 */
export class APIErrorResponse extends Error {
    code: string
    details?: Record<string, string>

    constructor(error: APIError['error']) {
        super(error.message)
        this.name = 'APIErrorResponse'
        this.code = error.code
        this.details = error.details
    }
}

/**
 * Safely parse JSON response body.
 * Returns null for empty bodies or non-JSON responses.
 */
function safeParseJSON(text: string): any {
    if (!text) return null
    try {
        return JSON.parse(text)
    } catch {
        return null
    }
}

/**
 * Get auth token from storage (localStorage or sessionStorage).
 * 
 * Returns token string if available, null otherwise.
 * 
 * Priority:
 * 1. Supabase session token (if Supabase is configured)
 * 2. Dev auth token (local development)
 */
async function getAuthToken(): Promise<string | null> {
    // Check cached session first (for immediate use after sign-in)
    if (cachedSession && Date.now() < cacheExpiry) {
        return cachedSession.access_token
    }

    // Clear expired cache
    if (Date.now() >= cacheExpiry && cachedSession) {
        clearCachedSession()
    }

    // Try Supabase Auth - use shared client if available
    const supabaseUrl = import.meta.env.VITE_SUPABASE_URL
    const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY

    if (supabaseUrl && supabaseAnonKey) {
        try {
            const { supabase } = await import('@/lib/supabase')
            if (supabase) {
                const { data: { session }, error } = await supabase.auth.getSession()
                if (error) {
                    if (import.meta.env.DEV) {
                        console.warn('[api] Session check error:', error.message)
                    }
                }

                let activeSession = session
                // Refresh if expired or within 60s of expiry (access token can be rejected by backend)
                if (activeSession?.expires_at) {
                    const expiresAtMs = activeSession.expires_at * 1000
                    const nowMs = Date.now()
                    if (nowMs >= expiresAtMs - 60_000) {
                        const { data: refreshed } = await supabase.auth.refreshSession()
                        if (refreshed?.session) {
                            activeSession = refreshed.session
                        }
                    }
                }
                if (activeSession?.access_token) {
                    return activeSession.access_token
                } else {
                    if (import.meta.env.DEV) {
                        console.warn('[api] No session token available from Supabase - session exists but no access_token')
                    }
                }
            } else {
                if (import.meta.env.DEV) {
                    console.warn('[api] Supabase client is null despite config being present')
                }
            }
        } catch (err) {
            if (import.meta.env.DEV) {
                console.error('[api] Auth token check failed:', err)
            }
        }
    }

    // Fall back to dev auth token (local development)
    // NOTE: This should only be used if Supabase is not configured
    // If Supabase IS configured but session is missing, we should return null
    if (import.meta.env.DEV) {
        const devToken = localStorage.getItem('dev_auth_token')
        if (devToken) {
            // Only use dev token if Supabase is NOT configured
            if (!supabaseUrl || !supabaseAnonKey) {
                return devToken
            } else {
                if (import.meta.env.DEV) {
                    console.warn('[api] Supabase is configured but session not found. NOT using dev token to avoid confusion.')
                }
            }
        }
    }

    return null
}

/**
 * Get dev user ID from localStorage (local dev bypass).
 * 
 * Returns user ID string if available, null otherwise.
 */
function getDevUserId(): string | null {
    if (import.meta.env.DEV) {
        return localStorage.getItem('dev_user_id')
    }
    return null
}

/**
 * Fetch wrapper with consistent error handling.
 *
 * All API calls should use this function.
 * Transforms backend error responses into APIErrorResponse exceptions.
 * 
 * Handles:
 * - 401: Treated as logged out (no token or invalid token)
 * - 403: Permission denied (valid auth but not allowed)
 * - Other errors: Standard API error format
 */
export async function apiRequest<T>(
    endpoint: string,
    options: RequestInit & { token?: string } = {}
): Promise<T> {
    const url = `${API_BASE_URL}${endpoint}`

    const headers: Record<string, string> = {
        Accept: 'application/json',
        ...(options.headers as Record<string, string> || {}),
    }

    if (options.body) {
        headers['Content-Type'] = 'application/json'
    }

    // Add auth token if available
    const token = options.token ?? (await getAuthToken())
    const hadToken = !!token
    if (token) {
        headers['Authorization'] = `Bearer ${token}`
    }

    // Add dev user header if in local dev mode
    if (import.meta.env.DEV) {
        const devUserId = getDevUserId()
        if (devUserId) {
            headers['X-Dev-User'] = devUserId
        }
    }

    const response = await fetch(url, {
        ...options,
        headers,
    })

    const text = await response.text()
    const data = safeParseJSON(text)

    // Handle 401 (authentication required)
    if (response.status === 401) {
        if (import.meta.env.DEV) {
            console.warn(
                `[api] 401 Unauthorized on ${endpoint}. Token sent: ${hadToken}. ` +
                'If signed in, try: sign out and back in to refresh your session.'
            )
        }
        if (data?.error) {
            throw new APIErrorResponse(data.error)
        }
        throw new APIErrorResponse({
            code: 'UNAUTHORIZED',
            message: 'Authentication required',
        })
    }

    // Handle 403 (permission denied)
    if (response.status === 403) {
        if (data?.error) {
            throw new APIErrorResponse(data.error)
        }
        throw new APIErrorResponse({
            code: 'FORBIDDEN',
            message: 'Permission denied',
        })
    }

    // Backend error shape
    if (!response.ok || (data && 'error' in data)) {
        if (data?.error) {
            throw new APIErrorResponse(data.error)
        }

        throw new APIErrorResponse({
            code: 'HTTP_ERROR',
            message: `HTTP ${response.status}: ${response.statusText}`,
        })
    }

    return data as T
}

// =============================================================================
// Me / Terms acceptance (legal audit)
// =============================================================================

export interface TermsAcceptance {
    terms_accepted_at: string | null
    server_listing_terms_accepted_at: string | null
}

export async function getTermsAcceptance(): Promise<TermsAcceptance> {
    return apiRequest<TermsAcceptance>('/api/v1/me/terms-acceptance')
}

export async function acceptTerms(acceptanceType: 'account' | 'server_listing'): Promise<{ ok: boolean }> {
    return apiRequest<{ ok: boolean }>('/api/v1/me/terms-acceptance', {
        method: 'POST',
        body: JSON.stringify({ acceptance_type: acceptanceType }),
    })
}

// =============================================================================
// Favorites API
// All require authentication. Use apiRequest which sends Bearer token.
// =============================================================================

export async function addFavorite(serverId: string): Promise<{ success: boolean }> {
    return apiRequest<{ success: boolean }>(`/api/v1/servers/${serverId}/favorites`, {
        method: 'POST',
    })
}

export async function removeFavorite(serverId: string): Promise<{ success: boolean }> {
    return apiRequest<{ success: boolean }>(`/api/v1/servers/${serverId}/favorites`, {
        method: 'DELETE',
    })
}

// =============================================================================
// Cluster Management (owner dashboard)
// All require authentication. Use apiRequest which sends Bearer token.
// =============================================================================

export interface Cluster {
    id: string
    name: string
    slug: string
    owner_user_id: string
    visibility: 'public' | 'unlisted'
    key_version: number
    public_fingerprint?: string | null
    public_key_ed25519?: string | null
    heartbeat_grace_seconds?: number | null
    rotated_at?: string | null
    created_at: string
    updated_at: string
}

export interface KeyPairResponse {
    cluster_id: string
    key_version: number
    public_key: string
    private_key: string
    warning: string
}

export async function listMyClusters(): Promise<Cluster[]> {
    return apiRequest<Cluster[]>('/api/v1/clusters/')
}

export async function getCluster(clusterId: string): Promise<Cluster> {
    return apiRequest<Cluster>(`/api/v1/clusters/${clusterId}`)
}

export async function createCluster(payload: {
    name: string
    slug?: string
    visibility?: 'public' | 'unlisted'
}): Promise<Cluster> {
    return apiRequest<Cluster>('/api/v1/clusters/', {
        method: 'POST',
        body: JSON.stringify(payload),
    })
}

export async function updateCluster(
    clusterId: string,
    payload: {
        name?: string
        slug?: string
        visibility?: 'public' | 'unlisted'
    }
): Promise<Cluster> {
    return apiRequest<Cluster>(`/api/v1/clusters/${clusterId}`, {
        method: 'PUT',
        body: JSON.stringify(payload),
    })
}

export async function generateClusterKeys(clusterId: string): Promise<KeyPairResponse> {
    return apiRequest<KeyPairResponse>(`/api/v1/clusters/${clusterId}/generate-keys`, {
        method: 'POST',
    })
}

// =============================================================================
// Server CRUD (owner dashboard)
// All require authentication. Use apiRequest which sends Bearer token.
// =============================================================================

/** List current user's servers. GET /api/v1/servers returns DirectoryResponse shape. */
export async function listMyServers(): Promise<{
    data: Array<Record<string, unknown>>
    total: number
    page: number
    page_size: number
}> {
    return apiRequest<{
        data: Array<Record<string, unknown>>
        total: number
        page: number
        page_size: number
    }>('/api/v1/servers/')
}

/** Get server by ID. Public or owner view depending on auth. */
export async function getServer(serverId: string): Promise<Record<string, unknown>> {
    return apiRequest<Record<string, unknown>>(`/api/v1/servers/${serverId}`)
}

/** Create server. Backend accepts full ServerCreateRequest shape. */
export async function createServer(payload: Record<string, unknown>): Promise<Record<string, unknown>> {
    return apiRequest<Record<string, unknown>>('/api/v1/servers/', {
        method: 'POST',
        body: JSON.stringify(payload),
    })
}

/** Update server. Backend accepts partial ServerUpdateRequest shape. */
export async function updateServer(
    serverId: string,
    payload: Record<string, unknown>
): Promise<Record<string, unknown>> {
    return apiRequest<Record<string, unknown>>(`/api/v1/servers/${serverId}`, {
        method: 'PUT',
        body: JSON.stringify(payload),
    })
}

/** Delete server. */
export async function deleteServer(serverId: string): Promise<{ success: boolean }> {
    return apiRequest<{ success: boolean }>(`/api/v1/servers/${serverId}`, {
        method: 'DELETE',
    })
}

// =============================================================================
// Mods Resolution
// =============================================================================

export interface ResolvedMod {
    mod_id: number
    name: string
    slug: string | null
    source: 'catalog' | 'curseforge' | 'user'
}

export interface ModResolveResponse {
    data: ResolvedMod[]
    missing: number[]
}

/** Resolve mod IDs to names. */
export async function resolveMods(modIds: number[]): Promise<ModResolveResponse> {
    return apiRequest<ModResolveResponse>('/api/v1/mods/resolve', {
        method: 'POST',
        body: JSON.stringify({ mod_ids: modIds }),
    })
}

/** Search mods by name prefix (autocomplete). */
export async function searchMods(query: string, limit = 20): Promise<ResolvedMod[]> {
    return apiRequest<ResolvedMod[]>(`/api/v1/mods/search?q=${encodeURIComponent(query)}&limit=${limit}`)
}
