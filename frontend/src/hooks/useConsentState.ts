/**
 * Hook for current user's consent state (Sprint 8 – trust UX).
 * Fetches GET /api/v1/me/consent-state when authenticated.
 */

import { useQuery } from '@tanstack/react-query'
import { getConsentState, type ConsentState } from '@/lib/api'
import { useAuth } from '@/contexts/AuthContext'

export type { ConsentState }

export function useConsentState() {
    const { isAuthenticated, loading: authLoading } = useAuth()

    return useQuery({
        queryKey: ['consent-state'],
        queryFn: getConsentState,
        enabled: isAuthenticated && !authLoading,
        staleTime: 60_000,
    })
}
