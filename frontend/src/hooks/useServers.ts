/**
 * Hook for server data fetching.
 *
 * Uses TanStack Query for caching and state management.
 * Connects to GET /api/v1/directory/servers (cursor pagination).
 *
 * Modes:
 * - paged: true  → one page at a time, Previous/Next page (replace list)
 * - paged: false → infinite "Load more" (append pages)
 */

import { useCallback, useEffect, useRef, useState } from 'react'
import { useInfiniteQuery, useQuery, keepPreviousData } from '@tanstack/react-query'
import { apiRequest } from '@/lib/api'
import type { DirectoryResponse, DirectoryServer } from '@/types'
import type { ServerFilters } from '@/components/servers/ServerFilters'

const DEFAULT_LIMIT = 24

export interface UseServersOptions {
    /** If true, show one page at a time with Previous/Next (replace list). If false, append with "Load more". */
    paged?: boolean
}

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
    if (filters?.platform) {
        if (filters.platform === 'pc') {
            params.set('pc', 'true')
            params.set('console', 'false')
        } else if (filters.platform === 'console') {
            params.set('console', 'true')
            params.set('pc', 'false')
        } else if (filters.platform === 'crossplay') {
            params.set('crossplay', 'true')
        }
    }
    if (filters?.rank_by) params.set('rank_by', filters.rank_by ?? 'updated')
    if (filters?.order) params.set('order', filters.order ?? 'desc')
    if (filters?.view) params.set('view', filters.view)
    return params
}

export function useServers(filters?: ServerFilters, options?: UseServersOptions) {
    const paged = options?.paged ?? true

    const [currentCursor, setCurrentCursor] = useState<string | null>(null)
    const [cursorStack, setCursorStack] = useState<(string | null)[]>([])
    const totalFromFirstPage = useRef<number | undefined>(undefined)

    useEffect(() => {
        setCurrentCursor(null)
        setCursorStack([])
        totalFromFirstPage.current = undefined
    }, [filters])

    const singlePageQuery = useQuery({
        queryKey: ['servers', filters, currentCursor],
        queryFn: async () => {
            const params = buildParams(filters, currentCursor)
            const url = `/api/v1/directory/servers?${params.toString()}`
            return apiRequest<DirectoryResponse>(url)
        },
        refetchInterval: 60_000,
        placeholderData: keepPreviousData,
        enabled: paged,
    })

    const nextPage = useCallback(() => {
        const nextCursor = singlePageQuery.data?.next_cursor
        if (nextCursor) {
            setCursorStack((prev) => [...prev, currentCursor])
            setCurrentCursor(nextCursor)
        }
    }, [currentCursor, singlePageQuery.data?.next_cursor])

    const prevPage = useCallback(() => {
        if (cursorStack.length === 0) return
        const prev = cursorStack[cursorStack.length - 1]
        setCursorStack((prevStack) => prevStack.slice(0, -1))
        setCurrentCursor(prev)
    }, [cursorStack])

    const infiniteQuery = useInfiniteQuery({
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
        enabled: !paged,
    })

    if (paged) {
        if (currentCursor === null && singlePageQuery.data?.total !== undefined) {
            totalFromFirstPage.current = singlePageQuery.data.total
        }
        const limit = filters?.limit ?? DEFAULT_LIMIT
        const total = currentCursor === null ? singlePageQuery.data?.total : totalFromFirstPage.current
        const totalPages = total !== undefined ? Math.ceil(total / limit) : undefined
        const pageNumber = cursorStack.length + 1

        return {
            ...singlePageQuery,
            servers: (singlePageQuery.data?.data ?? []) as DirectoryServer[],
            total,
            hasNextPage: !!singlePageQuery.data?.next_cursor && !filters?.q?.trim(),
            hasPreviousPage: cursorStack.length > 0,
            nextPage,
            prevPage,
            pageNumber,
            totalPages,
            fetchNextPage: nextPage,
            isFetchingNextPage: false,
        }
    }

    const servers: DirectoryServer[] = infiniteQuery.data?.pages.flatMap((p) => p.data) ?? []
    const hasNextPage = !!infiniteQuery.hasNextPage && !filters?.q?.trim()
    const total = infiniteQuery.data?.pages[0]?.total

    return {
        ...infiniteQuery,
        servers,
        hasNextPage,
        fetchNextPage: infiniteQuery.fetchNextPage,
        total,
        hasPreviousPage: false,
        nextPage: () => {},
        prevPage: () => {},
        pageNumber: 1,
        totalPages: undefined,
        isFetchingNextPage: infiniteQuery.isFetchingNextPage,
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
