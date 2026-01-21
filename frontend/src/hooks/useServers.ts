/**
 * Hook for server data fetching.
 *
 * Uses TanStack Query for caching and state management.
 * Consumes DirectoryServer type from directory_view.
 */

import { useQuery, keepPreviousData } from '@tanstack/react-query'
import { apiRequest } from '@/lib/api'
import type { DirectoryResponse, DirectoryServer } from '@/types'

export function useServers() {
    return useQuery({
        queryKey: ['servers'],
        queryFn: async () => {
            return apiRequest<DirectoryResponse>('/api/v1/directory/servers')
        },
        refetchInterval: 60_000, // 60 seconds - aligns with heartbeat cadence
        placeholderData: keepPreviousData, // Prevent flash of empty on refetch
    })
}

export function useServer(serverId: string) {
    return useQuery({
        queryKey: ['servers', serverId],
        queryFn: async () => {
            return apiRequest<DirectoryServer>(
                `/api/v1/directory/servers/${serverId}`
            )
        },
        enabled: !!serverId,
        staleTime: 30_000, // 30 seconds - no need for real-time updates on detail page
    })
}
