/**
 * API client configuration and utilities.
 *
 * All API calls go through this module.
 * Provides consistent error handling and request formatting.
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5173'

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
 * Fetch wrapper with consistent error handling.
 *
 * All API calls should use this function.
 * Transforms backend error responses into APIErrorResponse exceptions.
 */
export async function apiRequest<T>(
    endpoint: string,
    options?: RequestInit
): Promise<T> {
    const url = `${API_BASE_URL}${endpoint}`

    const response = await fetch(url, {
        ...options,
        headers: {
            'Content-Type': 'application/json',
            ...options?.headers,
        },
    })

    const data = await response.json()

    // Backend always returns errors in { error: { ... } } format
    if (!response.ok || 'error' in data) {
        if ('error' in data) {
            throw new APIErrorResponse(data.error)
        }
        // Fallback for non-JSON errors
        throw new APIErrorResponse({
            code: 'HTTP_ERROR',
            message: `HTTP ${response.status}: ${response.statusText}`,
        })
    }

    return data as T
}
