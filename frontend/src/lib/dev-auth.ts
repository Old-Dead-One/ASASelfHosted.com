/**
 * Dev auth utilities.
 *
 * Local development auth toggle that mirrors backend bypass.
 * Allows testing "logged in" UX without Supabase.
 */

const DEV_AUTH_ENABLED_KEY = 'dev_auth_enabled'
const DEV_USER_ID_KEY = 'dev_user_id'

/**
 * Check if dev auth is enabled.
 */
export function isDevAuthEnabled(): boolean {
    if (!import.meta.env.DEV) return false
    return localStorage.getItem(DEV_AUTH_ENABLED_KEY) === 'true'
}

/**
 * Enable dev auth with optional user ID.
 */
export function enableDevAuth(userId: string = 'local-dev'): void {
    if (!import.meta.env.DEV) return
    localStorage.setItem(DEV_AUTH_ENABLED_KEY, 'true')
    localStorage.setItem(DEV_USER_ID_KEY, userId)
    localStorage.setItem('dev_auth_token', 'dev-bypass-token') // Dummy token for consistency
}

/**
 * Disable dev auth.
 */
export function disableDevAuth(): void {
    if (!import.meta.env.DEV) return
    localStorage.removeItem(DEV_AUTH_ENABLED_KEY)
    localStorage.removeItem(DEV_USER_ID_KEY)
    localStorage.removeItem('dev_auth_token')
}

/**
 * Get current dev user ID.
 */
export function getDevUserId(): string | null {
    if (!import.meta.env.DEV) return null
    return localStorage.getItem(DEV_USER_ID_KEY)
}
