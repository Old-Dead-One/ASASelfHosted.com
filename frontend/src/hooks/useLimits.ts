/**
 * Hook for per-user limits (Sprint 9 – dashboard "X of Y servers").
 * Fetches GET /api/v1/me/limits when authenticated.
 */

import { useQuery } from '@tanstack/react-query'
import { getLimits } from '@/lib/api'
import { useAuth } from '@/contexts/AuthContext'

export function useLimits() {
    const { isAuthenticated, loading: authLoading } = useAuth()

    return useQuery({
        queryKey: ['limits'],
        queryFn: getLimits,
        enabled: isAuthenticated && !authLoading,
        staleTime: 60_000,
    })
}
