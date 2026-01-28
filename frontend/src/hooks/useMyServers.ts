/**
 * Hook for owner dashboard server list.
 *
 * Fetches current user's servers from GET /api/v1/servers.
 * Requires authentication.
 */

import { useQuery, useQueryClient } from '@tanstack/react-query'
import { listMyServers } from '@/lib/api'
import { useAuth } from '@/contexts/AuthContext'
import type { DirectoryServer } from '@/types'

/** List response shape matches DirectoryResponse (page-based). */
interface MyServersResponse {
    data: DirectoryServer[]
    total: number
    page: number
    page_size: number
}

export function useMyServers() {
    const { isAuthenticated, loading: authLoading } = useAuth()
    
    return useQuery({
        queryKey: ['my-servers'],
        queryFn: async () => {
            const res = await listMyServers()
            return res as unknown as MyServersResponse
        },
        enabled: isAuthenticated && !authLoading, // Only run when authenticated
        staleTime: 30_000,
    })
}

export function useInvalidateMyServers() {
    const qc = useQueryClient()
    return () => qc.invalidateQueries({ queryKey: ['my-servers'] })
}
