/**
 * Supabase client configuration.
 *
 * Handles both production (Supabase Auth) and local dev (bypass) modes.
 */

import { createClient, SupabaseClient } from '@supabase/supabase-js'

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY

/**
 * Supabase client instance.
 *
 * In production: Uses real Supabase Auth
 * In local dev without Supabase: Returns null (dev auth bypass used instead)
 */
export const supabase: SupabaseClient | null =
    supabaseUrl && supabaseAnonKey
        ? createClient(supabaseUrl, supabaseAnonKey)
        : null

/**
 * Check if Supabase is configured.
 */
export function isSupabaseConfigured(): boolean {
    return supabase !== null
}
