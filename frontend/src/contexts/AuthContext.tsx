/**
 * Authentication context.
 *
 * Provides auth state and methods throughout the app.
 * Supports both Supabase Auth (production) and dev auth bypass (local).
 */

import React, { createContext, useContext, useEffect, useState, useCallback } from 'react'
import { supabase, isSupabaseConfigured } from '@/lib/supabase'
import { enableDevAuth, disableDevAuth, isDevAuthEnabled, getDevUserId } from '@/lib/dev-auth'
import { cacheAuthSession, clearCachedSession } from '@/lib/api'
import type { User } from '@supabase/supabase-js'

interface AuthContextType {
    user: User | null
    loading: boolean
    signIn: (email: string, password: string) => Promise<void>
    signUp: (email: string, password: string) => Promise<void>
    signOut: () => Promise<void>
    isAuthenticated: boolean
    userId: string | null
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: React.ReactNode }) {
    const [user, setUser] = useState<User | null>(null)
    const [loading, setLoading] = useState(true)

    // Initialize auth state
    useEffect(() => {
        if (isSupabaseConfigured() && supabase) {
            // Supabase Auth: Get initial session
            supabase.auth.getSession().then(({ data: { session } }) => {
                setUser(session?.user ?? null)
                setLoading(false)
            })

            // Listen for auth changes
            const {
                data: { subscription },
            } = supabase.auth.onAuthStateChange((event, session) => {
                setUser(session?.user ?? null)

                // Clear cached session once Supabase has confirmed the session is stored
                // This happens after SIGNED_IN event, so we can rely on Supabase storage
                if (event === 'SIGNED_IN' && session) {
                    // Clear cache after a short delay to ensure transition is smooth
                    setTimeout(() => {
                        clearCachedSession()
                    }, 1000)
                } else if (event === 'SIGNED_OUT') {
                    clearCachedSession()
                }
            })

            return () => subscription.unsubscribe()
        } else {
            // Dev auth bypass: Check localStorage
            if (isDevAuthEnabled()) {
                // Create a mock user object for dev mode
                const devUserId = getDevUserId() || 'local-dev'
                setUser({
                    id: devUserId,
                    email: `${devUserId}@local.dev`,
                    app_metadata: {},
                    user_metadata: {},
                    aud: 'authenticated',
                    created_at: new Date().toISOString(),
                } as User)
            }
            setLoading(false)
        }
    }, [])

    const signIn = useCallback(async (email: string, password: string) => {
        if (isSupabaseConfigured() && supabase) {
            const { data, error } = await supabase.auth.signInWithPassword({
                email,
                password,
            })
            if (error) throw error

            // Cache the session for immediate API calls
            // This handles the timing issue where Supabase hasn't fully stored the session yet
            if (data.session) {
                cacheAuthSession({
                    access_token: data.session.access_token,
                    expires_at: data.session.expires_at,
                })
            }

            // Set user immediately
            setUser(data.user)

            // Note: onAuthStateChange will fire and clear the cache after Supabase stores the session
            // This ensures smooth transition from cached session to Supabase storage
        } else {
            // Dev auth bypass
            enableDevAuth(email.split('@')[0] || 'dev-user')
            const devUserId = getDevUserId() || 'dev-user'
            setUser({
                id: devUserId,
                email,
                app_metadata: {},
                user_metadata: {},
                aud: 'authenticated',
                created_at: new Date().toISOString(),
            } as User)
        }
    }, [])

    const signUp = useCallback(async (email: string, password: string) => {
        if (isSupabaseConfigured() && supabase) {
            const { data, error } = await supabase.auth.signUp({
                email,
                password,
            })
            if (error) throw error
            setUser(data.user)
        } else {
            // Dev auth bypass: same as sign in
            await signIn(email, password)
        }
    }, [signIn])

    const signOut = useCallback(async () => {
        if (isSupabaseConfigured() && supabase) {
            await supabase.auth.signOut()
            setUser(null)
        } else {
            // Dev auth bypass
            disableDevAuth()
            setUser(null)
        }
    }, [])

    const userId = user?.id ?? null
    const isAuthenticated = user !== null

    return (
        <AuthContext.Provider
            value={{
                user,
                loading,
                signIn,
                signUp,
                signOut,
                isAuthenticated,
                userId,
            }}
        >
            {children}
        </AuthContext.Provider>
    )
}

export function useAuth() {
    const context = useContext(AuthContext)
    if (context === undefined) {
        throw new Error('useAuth must be used within an AuthProvider')
    }
    return context
}
