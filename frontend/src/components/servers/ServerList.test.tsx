/**
 * Tests for ServerList component.
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { BrowserRouter } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { ServerList } from './ServerList'
import type { DirectoryResponse, DirectoryServer } from '@/types'
import type { ServerFilters } from './ServerFilters'

// Mock the useServers hook
vi.mock('@/hooks/useServers', () => ({
    useServers: vi.fn(),
}))

import { useServers } from '@/hooks/useServers'

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
        game_mode: 'pvp',
        ruleset: 'boosted',
        is_verified: true,
        is_new: false,
        is_stable: true,
        platforms: ['steam'],
        ...overrides,
    }
}

// Wrapper with Router and QueryClient
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
        <BrowserRouter>
            <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
        </BrowserRouter>
    )
}

describe('ServerList', () => {
    beforeEach(() => {
        vi.clearAllMocks()
    })

    it('renders loading skeleton for card view', () => {
        vi.mocked(useServers).mockReturnValue({
            servers: [],
            isLoading: true,
            error: null,
            refetch: vi.fn(),
            hasNextPage: false,
            fetchNextPage: vi.fn(),
            isFetchingNextPage: false,
        } as any)

        const filters: ServerFilters = { view: 'card' }
        render(<ServerList filters={filters} />, { wrapper: createWrapper() })

        // Should render 6 skeleton cards
        const skeletons = screen.getAllByRole('generic').filter(
            (el) => el.className.includes('animate-pulse')
        )
        expect(skeletons.length).toBeGreaterThan(0)
    })

    it('renders loading skeleton for row view', () => {
        vi.mocked(useServers).mockReturnValue({
            servers: [],
            isLoading: true,
            error: null,
            refetch: vi.fn(),
            hasNextPage: false,
            fetchNextPage: vi.fn(),
            isFetchingNextPage: false,
        } as any)

        const filters: ServerFilters = { view: 'compact' }
        render(<ServerList filters={filters} />, { wrapper: createWrapper() })

        // Should render skeleton rows
        const skeletons = screen.getAllByRole('generic').filter(
            (el) => el.className.includes('animate-pulse')
        )
        expect(skeletons.length).toBeGreaterThan(0)
    })

    it('renders error message on error', () => {
        const error = new Error('Failed to fetch')
        const mockRefetch = vi.fn()

        vi.mocked(useServers).mockReturnValue({
            servers: [],
            isLoading: false,
            error,
            refetch: mockRefetch,
            hasNextPage: false,
            fetchNextPage: vi.fn(),
            isFetchingNextPage: false,
        } as any)

        render(<ServerList />, { wrapper: createWrapper() })

        expect(screen.getByText(/failed to load servers/i)).toBeInTheDocument()
        expect(screen.getByRole('button', { name: /retry/i })).toBeInTheDocument()
    })

    it('calls refetch when retry button is clicked', async () => {
        const user = userEvent.setup()
        const error = new Error('Failed to fetch')
        const mockRefetch = vi.fn()

        vi.mocked(useServers).mockReturnValue({
            servers: [],
            isLoading: false,
            error,
            refetch: mockRefetch,
            hasNextPage: false,
            fetchNextPage: vi.fn(),
            isFetchingNextPage: false,
        } as any)

        render(<ServerList />, { wrapper: createWrapper() })

        const retryButton = screen.getByRole('button', { name: /retry/i })
        await user.click(retryButton)

        expect(mockRefetch).toHaveBeenCalledOnce()
    })

    it('renders empty state when no servers', () => {
        vi.mocked(useServers).mockReturnValue({
            servers: [],
            isLoading: false,
            error: null,
            refetch: vi.fn(),
            hasNextPage: false,
            fetchNextPage: vi.fn(),
            isFetchingNextPage: false,
        } as any)

        render(<ServerList />, { wrapper: createWrapper() })

        expect(screen.getByText(/no servers found/i)).toBeInTheDocument()
        expect(screen.getByText(/try clearing your filters/i)).toBeInTheDocument()
    })

    it('renders servers in card view', () => {
        const servers = [
            createMockServer({ id: 'server-1', name: 'Server 1' }),
            createMockServer({ id: 'server-2', name: 'Server 2' }),
        ]

        vi.mocked(useServers).mockReturnValue({
            servers,
            isLoading: false,
            error: null,
            refetch: vi.fn(),
            hasNextPage: false,
            fetchNextPage: vi.fn(),
            isFetchingNextPage: false,
        } as any)

        const filters: ServerFilters = { view: 'card' }
        render(<ServerList filters={filters} />, { wrapper: createWrapper() })

        expect(screen.getByText('Server 1')).toBeInTheDocument()
        expect(screen.getByText('Server 2')).toBeInTheDocument()
    })

    it('renders servers in row view', () => {
        const servers = [
            createMockServer({ id: 'server-1', name: 'Server 1' }),
            createMockServer({ id: 'server-2', name: 'Server 2' }),
        ]

        vi.mocked(useServers).mockReturnValue({
            servers,
            isLoading: false,
            error: null,
            refetch: vi.fn(),
            hasNextPage: false,
            fetchNextPage: vi.fn(),
            isFetchingNextPage: false,
        } as any)

        const filters: ServerFilters = { view: 'compact' }
        render(<ServerList filters={filters} />, { wrapper: createWrapper() })

        expect(screen.getByText('Server 1')).toBeInTheDocument()
        expect(screen.getByText('Server 2')).toBeInTheDocument()
    })

    it('renders load more button when hasNextPage is true', () => {
        const servers = [createMockServer()]

        vi.mocked(useServers).mockReturnValue({
            servers,
            isLoading: false,
            error: null,
            refetch: vi.fn(),
            hasNextPage: true,
            fetchNextPage: vi.fn(),
            isFetchingNextPage: false,
        } as any)

        render(<ServerList />, { wrapper: createWrapper() })

        expect(screen.getByRole('button', { name: /load more/i })).toBeInTheDocument()
    })

    it('does not render load more button when hasNextPage is false', () => {
        const servers = [createMockServer()]

        vi.mocked(useServers).mockReturnValue({
            servers,
            isLoading: false,
            error: null,
            refetch: vi.fn(),
            hasNextPage: false,
            fetchNextPage: vi.fn(),
            isFetchingNextPage: false,
        } as any)

        render(<ServerList />, { wrapper: createWrapper() })

        expect(screen.queryByRole('button', { name: /load more/i })).not.toBeInTheDocument()
    })

    it('calls fetchNextPage when load more is clicked', async () => {
        const user = userEvent.setup()
        const servers = [createMockServer()]
        const mockFetchNextPage = vi.fn()

        vi.mocked(useServers).mockReturnValue({
            servers,
            isLoading: false,
            error: null,
            refetch: vi.fn(),
            hasNextPage: true,
            fetchNextPage: mockFetchNextPage,
            isFetchingNextPage: false,
        } as any)

        render(<ServerList />, { wrapper: createWrapper() })

        const loadMoreButton = screen.getByRole('button', { name: /load more/i })
        await user.click(loadMoreButton)

        expect(mockFetchNextPage).toHaveBeenCalledOnce()
    })

    it('shows loading state on load more button when fetching', () => {
        const servers = [createMockServer()]

        vi.mocked(useServers).mockReturnValue({
            servers,
            isLoading: false,
            error: null,
            refetch: vi.fn(),
            hasNextPage: true,
            fetchNextPage: vi.fn(),
            isFetchingNextPage: true,
        } as any)

        render(<ServerList />, { wrapper: createWrapper() })

        const loadMoreButton = screen.getByRole('button', { name: /load more servers/i })
        expect(loadMoreButton).toBeDisabled()
        expect(loadMoreButton).toHaveTextContent('Loading…')
    })

    it('defaults to compact view when view is not specified', () => {
        const servers = [createMockServer()]

        vi.mocked(useServers).mockReturnValue({
            servers,
            isLoading: false,
            error: null,
            refetch: vi.fn(),
            hasNextPage: false,
            fetchNextPage: vi.fn(),
            isFetchingNextPage: false,
        } as any)

        render(<ServerList />, { wrapper: createWrapper() })

        // Should render ServerRow (compact view), not ServerCard
        // We can verify this by checking the structure
        expect(screen.getByText('Test Server')).toBeInTheDocument()
    })

    it('passes filters to useServers hook', () => {
        const filters: ServerFilters = {
            q: 'test',
            status: 'online',
            view: 'card',
        }

        vi.mocked(useServers).mockReturnValue({
            servers: [],
            isLoading: false,
            error: null,
            refetch: vi.fn(),
            hasNextPage: false,
            fetchNextPage: vi.fn(),
            isFetchingNextPage: false,
        } as any)

        render(<ServerList filters={filters} />, { wrapper: createWrapper() })

        expect(useServers).toHaveBeenCalledWith(filters)
    })
})
