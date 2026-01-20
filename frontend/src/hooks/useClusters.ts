/**
 * Hook for cluster data fetching.
 */

import { useQuery } from '@tanstack/react-query'
import { apiRequest } from '@/lib/api'
import type { Cluster } from '@/types'

export function useClusters() {
    return useQuery({
        queryKey: ['clusters'],
        queryFn: async () => {
            const response = await apiRequest<{ data: Cluster[] }>('/api/v1/clusters')
            return response.data
        },
    })
}
