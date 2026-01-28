/**
 * Tests for useServers hook.
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { renderHook, waitFor } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { useServers, useServer } from './useServers'
import type { DirectoryResponse, DirectoryServer } from '@/types'
import type { ServerFilters } from '@/components/servers/ServerFilters'

// Mock the API client
vi.mock('@/lib/api', () => ({
    apiRequest: vi.fn(),
}))

import { apiRequest } from '@/lib/api'

// Helper to create wrapper with QueryClient
function createWrapper() {
    const queryClient = new QueryClient({
        defaultOptions: {
            queries: {
                retry: false,
                gcTime: 0,
            },
        },
    })

    return ({ children }: { children: React.ReactNode }) => (
        <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
    )
}

// Helper to create mock server
function createMockServer(overrides?: Partial<DirectoryServer>): DirectoryServer {
    return {
        id: 'server-1',
        name: 'Test Server',
        description: 'Test description',
        map_name: 'The Island',
        join_address: '123.456.789.0:7777',
        join_instructions_pc: null,
        join_instructions_console: null,
        mod_list: [],
        rates: null,
        wipe_info: null,
        effective_status: 'online',
        status_source: 'agent',
        last_seen_at: new Date().toISOString(),
        confidence: 'green',
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
        cluster_id: null,
        cluster_name: null,
        cluster_slug: null,
        cluster_visibility: null,
        favorite_count: 0,
        players_current: 10,
        players_capacity: 50,
        players_max: 50,
        quality_score: null,
        uptime_24h: null,
        uptime_percent: null,
        rank: null,
        rank_position: null,
        rank_by: null,
        rank_delta_24h: null,
        game_mode: 'pvp',
        ruleset: 'boosted',
        is_verified: true,
        is_new: false,
        is_stable: true,
        platforms: ['steam'],
        server_type: null,
        is_official_plus: null,
        is_modded: null,
        is_crossplay: null,
        is_console: null,
        is_pc: null,
        is_PC: null,
        ...(overrides || {}),
    } as DirectoryServer
}

describe('useServers', () => {
    beforeEach(() => {
        vi.clearAllMocks()
    })

    it('fetches servers with default limit', async () => {
        const mockResponse: DirectoryResponse = {
            data: [createMockServer()],
            limit: 25,
            cursor: null,
            next_cursor: null,
            rank_by: null,
            order: null,
            view: null,
        }

        vi.mocked(apiRequest).mockResolvedValue(mockResponse)

        const { result } = renderHook(() => useServers(), {
            wrapper: createWrapper(),
        })

        await waitFor(() => {
            expect(result.current.isLoading).toBe(false)
        })

        expect(result.current.servers).toHaveLength(1)
        expect(result.current.servers[0].name).toBe('Test Server')
        expect(apiRequest).toHaveBeenCalledWith(
            expect.stringContaining('limit=25')
        )
    })

    it('applies custom limit from filters', async () => {
        const mockResponse: DirectoryResponse = {
            data: [createMockServer()],
            limit: 50,
            cursor: null,
            next_cursor: null,
            rank_by: null,
            order: null,
            view: null,
        }

        vi.mocked(apiRequest).mockResolvedValue(mockResponse)

        const filters: ServerFilters = { limit: 50 }
        const { result } = renderHook(() => useServers(filters), {
            wrapper: createWrapper(),
        })

        await waitFor(() => {
            expect(result.current.isLoading).toBe(false)
        })

        expect(apiRequest).toHaveBeenCalledWith(
            expect.stringContaining('limit=50')
        )
    })

    it('applies search filter', async () => {
        const mockResponse: DirectoryResponse = {
            data: [],
            limit: 25,
            cursor: null,
            next_cursor: null,
            rank_by: null,
            order: null,
            view: null,
        }

        vi.mocked(apiRequest).mockResolvedValue(mockResponse)

        const filters: ServerFilters = { q: 'test search' }
        renderHook(() => useServers(filters), {
            wrapper: createWrapper(),
        })

        await waitFor(() => {
            expect(apiRequest).toHaveBeenCalled()
        })

        expect(apiRequest).toHaveBeenCalledWith(
            expect.stringContaining('q=test+search')
        )
    })

    it('applies status filter', async () => {
        const mockResponse: DirectoryResponse = {
            data: [],
            limit: 25,
            cursor: null,
            next_cursor: null,
            rank_by: null,
            order: null,
            view: null,
        }

        vi.mocked(apiRequest).mockResolvedValue(mockResponse)

        const filters: ServerFilters = { status: 'online' }
        renderHook(() => useServers(filters), {
            wrapper: createWrapper(),
        })

        await waitFor(() => {
            expect(apiRequest).toHaveBeenCalled()
        })

        expect(apiRequest).toHaveBeenCalledWith(
            expect.stringContaining('status=online')
        )
    })

    it('applies multiple filters', async () => {
        const mockResponse: DirectoryResponse = {
            data: [],
            limit: 25,
            cursor: null,
            next_cursor: null,
            rank_by: null,
            order: null,
            view: null,
        }

        vi.mocked(apiRequest).mockResolvedValue(mockResponse)

        const filters: ServerFilters = {
            status: 'online',
            game_mode: 'pvp',
            ruleset: 'boosted',
            rank_by: 'favorites',
            order: 'desc',
        }

        renderHook(() => useServers(filters), {
            wrapper: createWrapper(),
        })

        await waitFor(() => {
            expect(apiRequest).toHaveBeenCalled()
        })

        const callUrl = vi.mocked(apiRequest).mock.calls[0][0] as string
        expect(callUrl).toContain('status=online')
        expect(callUrl).toContain('game_mode=pvp')
        expect(callUrl).toContain('ruleset=boosted')
        expect(callUrl).toContain('rank_by=favorites')
        expect(callUrl).toContain('order=desc')
    })

    it('handles pagination with cursor', async () => {
        const firstPage: DirectoryResponse = {
            data: [createMockServer({ id: 'server-1' })],
            limit: 25,
            cursor: null,
            next_cursor: 'cursor-123',
            rank_by: null,
            order: null,
            view: null,
        }

        const secondPage: DirectoryResponse = {
            data: [createMockServer({ id: 'server-2' })],
            limit: 25,
            cursor: 'cursor-123',
            next_cursor: null,
            rank_by: null,
            order: null,
            view: null,
        }

        vi.mocked(apiRequest)
            .mockResolvedValueOnce(firstPage)
            .mockResolvedValueOnce(secondPage)

        const { result } = renderHook(() => useServers(), {
            wrapper: createWrapper(),
        })

        await waitFor(() => {
            expect(result.current.isLoading).toBe(false)
        })

        expect(result.current.servers).toHaveLength(1)
        expect(result.current.hasNextPage).toBe(true)

        // Fetch next page
        await result.current.fetchNextPage()

        await waitFor(() => {
            expect(result.current.servers).toHaveLength(2)
        })

        expect(result.current.hasNextPage).toBe(false)
    })

    it('hides load more when search is active', async () => {
        const mockResponse: DirectoryResponse = {
            data: [createMockServer()],
            limit: 25,
            cursor: null,
            next_cursor: 'cursor-123',
            rank_by: null,
            order: null,
            view: null,
        }

        vi.mocked(apiRequest).mockResolvedValue(mockResponse)

        const filters: ServerFilters = { q: 'test' }
        const { result } = renderHook(() => useServers(filters), {
            wrapper: createWrapper(),
        })

        await waitFor(() => {
            expect(result.current.isLoading).toBe(false)
        })

        // Even though next_cursor exists, hasNextPage should be false when searching
        expect(result.current.hasNextPage).toBe(false)
    })

    it('handles error state', async () => {
        const error = new Error('API Error')
        vi.mocked(apiRequest).mockRejectedValue(error)

        const { result } = renderHook(() => useServers(), {
            wrapper: createWrapper(),
        })

        await waitFor(() => {
            expect(result.current.isError).toBe(true)
        })

        expect(result.current.error).toBe(error)
        expect(result.current.servers).toHaveLength(0)
    })

    it('flattens pages into single servers array', async () => {
        const page1: DirectoryResponse = {
            data: [
                createMockServer({ id: 'server-1' }),
                createMockServer({ id: 'server-2' }),
            ],
            limit: 25,
            cursor: null,
            next_cursor: 'cursor-123',
            rank_by: null,
            order: null,
            view: null,
        }

        const page2: DirectoryResponse = {
            data: [createMockServer({ id: 'server-3' })],
            limit: 25,
            cursor: 'cursor-123',
            next_cursor: null,
            rank_by: null,
            order: null,
            view: null,
        }

        vi.mocked(apiRequest)
            .mockResolvedValueOnce(page1)
            .mockResolvedValueOnce(page2)

        const { result } = renderHook(() => useServers(), {
            wrapper: createWrapper(),
        })

        await waitFor(() => {
            expect(result.current.isLoading).toBe(false)
        })

        expect(result.current.servers).toHaveLength(2)

        await result.current.fetchNextPage()

        await waitFor(() => {
            expect(result.current.servers).toHaveLength(3)
        })
    })
})

describe('useServer', () => {
    beforeEach(() => {
        vi.clearAllMocks()
    })

    it('fetches single server by ID', async () => {
        const mockServer = createMockServer({ id: 'server-123' })
        vi.mocked(apiRequest).mockResolvedValue(mockServer)

        const { result } = renderHook(() => useServer('server-123'), {
            wrapper: createWrapper(),
        })

        await waitFor(() => {
            expect(result.current.isLoading).toBe(false)
        })

        expect(result.current.data).toEqual(mockServer)
        expect(apiRequest).toHaveBeenCalledWith('/api/v1/directory/servers/server-123')
    })

    it('does not fetch when serverId is empty', () => {
        const { result } = renderHook(() => useServer(''), {
            wrapper: createWrapper(),
        })

        expect(result.current.isLoading).toBe(false)
        expect(result.current.data).toBeUndefined()
        expect(apiRequest).not.toHaveBeenCalled()
    })

    it('handles error when server not found', async () => {
        const error = new Error('Server not found')
        vi.mocked(apiRequest).mockRejectedValue(error)

        const { result } = renderHook(() => useServer('invalid-id'), {
            wrapper: createWrapper(),
        })

        await waitFor(() => {
            expect(result.current.isError).toBe(true)
        })

        expect(result.current.error).toBe(error)
    })
})
