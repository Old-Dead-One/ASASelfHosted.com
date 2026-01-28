/**
 * Hook for server data fetching.
 *
 * Uses TanStack Query for caching and state management.
 * Connects to GET /api/v1/directory/servers (cursor pagination).
 */

import { useInfiniteQuery, useQuery, keepPreviousData } from '@tanstack/react-query'
import { apiRequest } from '@/lib/api'
import type { DirectoryResponse, DirectoryServer } from '@/types'
import type { ServerFilters } from '@/components/servers/ServerFilters'

const DEFAULT_LIMIT = 25

function buildParams(filters?: ServerFilters, cursor?: string | null): URLSearchParams {
    const params = new URLSearchParams()
    const limit = filters?.limit ?? DEFAULT_LIMIT
    params.set('limit', String(limit))
    if (cursor) params.set('cursor', cursor)
    if (filters?.q?.trim()) params.set('q', filters.q.trim())
    if (filters?.status) params.set('status', filters.status)
    if (filters?.mode) params.set('mode', filters.mode)
    if (filters?.game_mode) params.set('game_mode', filters.game_mode)
    if (filters?.ruleset) params.set('ruleset', filters.ruleset)
    if (filters?.is_cluster) params.set('is_cluster', filters.is_cluster)
    if (filters?.rank_by) params.set('rank_by', filters.rank_by ?? 'updated')
    if (filters?.order) params.set('order', filters.order ?? 'desc')
    if (filters?.view) params.set('view', filters.view)
    return params
}

export function useServers(filters?: ServerFilters) {
    const query = useInfiniteQuery({
        queryKey: ['servers', filters],
        queryFn: async ({ pageParam }) => {
            const params = buildParams(filters, pageParam ?? undefined)
            const url = `/api/v1/directory/servers?${params.toString()}`
            return apiRequest<DirectoryResponse>(url)
        },
        initialPageParam: null as string | null,
        getNextPageParam: (lastPage) => lastPage.next_cursor ?? undefined,
        refetchInterval: 60_000,
        placeholderData: keepPreviousData,
    })

    const servers: DirectoryServer[] = query.data?.pages.flatMap((p) => p.data) ?? []
    const hasNextPage = !!query.hasNextPage
    /** Cursor pagination is not supported when using search (q). Hide "Load more" when searching. */
    const canLoadMore = hasNextPage && !filters?.q?.trim()

    return {
        ...query,
        servers,
        hasNextPage: canLoadMore,
        fetchNextPage: query.fetchNextPage,
    }
}

export function useServer(serverId: string) {
    return useQuery({
        queryKey: ['servers', serverId],
        queryFn: async () => {
            return apiRequest<DirectoryServer>(`/api/v1/directory/servers/${serverId}`)
        },
        enabled: !!serverId,
        staleTime: 30_000,
    })
}
