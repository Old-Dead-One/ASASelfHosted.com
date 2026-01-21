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
 */
function getAuthToken(): string | null {
    // TODO: Implement proper token storage when Supabase Auth is integrated
    // For now, check localStorage for dev token
    if (import.meta.env.DEV) {
        return localStorage.getItem('dev_auth_token')
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
    const token = options.token || getAuthToken()
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
        // Clear any stored tokens on 401
        if (import.meta.env.DEV) {
            localStorage.removeItem('dev_auth_token')
        }
        // Return structured error for UI to handle
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
