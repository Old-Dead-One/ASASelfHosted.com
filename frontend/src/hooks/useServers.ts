/**
 * Hook for server data fetching.
 *
 * Uses TanStack Query for caching and state management.
 * Consumes DirectoryServer type from directory_view.
 */

import { useQuery } from '@tanstack/react-query'
import { apiRequest } from '@/lib/api'
import type { DirectoryServer } from '@/types'

export function useServers() {
    return useQuery({
        queryKey: ['servers'],
        queryFn: async () => {
            const response = await apiRequest<{ data: DirectoryServer[]; total: number }>(
                '/api/v1/servers'
            )
            return response.data
        },
    })
}

export function useServer(serverId: string) {
    return useQuery({
        queryKey: ['servers', serverId],
        queryFn: async () => {
            const response = await apiRequest<{ data: DirectoryServer }>(
                `/api/v1/servers/${serverId}`
            )
            return response.data
        },
        enabled: !!serverId,
    })
}
