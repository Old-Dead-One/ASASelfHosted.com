/**
 * Tests for DashboardPage component.
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { BrowserRouter } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { DashboardPage } from './DashboardPage'

// Mock the auth context
vi.mock('@/contexts/AuthContext', () => ({
    useAuth: vi.fn(),
}))

// Mock the useMyServers hook
vi.mock('@/hooks/useMyServers', () => ({
    useMyServers: vi.fn(),
    useInvalidateMyServers: vi.fn(),
}))

// Mock the API functions (ServerForm uses listMyClusters + resolveMods)
vi.mock('@/lib/api', () => ({
    createServer: vi.fn(),
    updateServer: vi.fn(),
    deleteServer: vi.fn(),
    listMyClusters: vi.fn().mockResolvedValue([]),
    resolveMods: vi.fn().mockResolvedValue({ data: [], missing: [] }),
    APIErrorResponse: class APIErrorResponse extends Error {
        code: string
        constructor(error: { code: string; message: string }) {
            super(error.message)
            this.code = error.code
        }
    },
}))

import { useAuth } from '@/contexts/AuthContext'
import { useMyServers, useInvalidateMyServers } from '@/hooks/useMyServers'
import { createServer, updateServer, deleteServer, APIErrorResponse } from '@/lib/api'

const mockUseAuth = vi.mocked(useAuth)
const mockUseMyServers = vi.mocked(useMyServers)
const mockUseInvalidateMyServers = vi.mocked(useInvalidateMyServers)
const mockInvalidate = vi.fn()

// Helper to create mock server (include is_pc, rulesets, etc. so edit form can submit)
function createMockServer(overrides?: any) {
    return {
        id: 'server-1',
        name: 'Test Server',
        description: 'Test description',
        effective_status: 'online',
        map_name: 'The Island',
        game_mode: 'pvp',
        ruleset: 'vanilla',
        rulesets: ['vanilla'],
        cluster_id: '',
        join_address: '',
        join_password: '',
        join_instructions_pc: '',
        join_instructions_console: '',
        mod_list: [],
        rates: '',
        wipe_info: '',
        is_pc: true,
        is_console: false,
        is_crossplay: false,
        ...overrides,
    }
}

// Wrapper with Router and QueryClient
function createWrapper() {
    const queryClient = new QueryClient({
        defaultOptions: {
            queries: { retry: false, gcTime: 0 },
        },
    })

    return ({ children }: { children: React.ReactNode }) => (
        <BrowserRouter>
            <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
        </BrowserRouter>
    )
}

describe('DashboardPage', () => {
    beforeEach(() => {
        vi.clearAllMocks()
        mockUseAuth.mockReturnValue({
            isAuthenticated: true,
            user: { id: 'user-1', email: 'test@example.com' } as any,
            signIn: vi.fn(),
            signUp: vi.fn(),
            signOut: vi.fn(),
            loading: false,
            userId: 'user-1',
        })
        mockUseInvalidateMyServers.mockReturnValue(mockInvalidate)
    })

    it('renders dashboard with user email', () => {
        mockUseMyServers.mockReturnValue({
            data: { data: [], total: 0, page: 1, page_size: 25 },
            isLoading: false,
            error: null,
            refetch: vi.fn(),
        } as any)

        render(<DashboardPage />, { wrapper: createWrapper() })

        expect(screen.getByText('Dashboard')).toBeInTheDocument()
        expect(screen.getByText(/test@example.com/i)).toBeInTheDocument()
    })

    it('shows loading state', () => {
        mockUseMyServers.mockReturnValue({
            data: undefined,
            isLoading: true,
            error: null,
            refetch: vi.fn(),
        } as any)

        render(<DashboardPage />, { wrapper: createWrapper() })

        expect(screen.getByText(/loading your servers/i)).toBeInTheDocument()
    })

    it('shows error state', () => {
        const error = new Error('Failed to load')
        mockUseMyServers.mockReturnValue({
            data: undefined,
            isLoading: false,
            error,
            refetch: vi.fn(),
        } as any)

        render(<DashboardPage />, { wrapper: createWrapper() })

        expect(screen.getByText(/failed to load servers/i)).toBeInTheDocument()
    })

    it('shows empty state when no servers', () => {
        mockUseMyServers.mockReturnValue({
            data: { data: [], total: 0, page: 1, page_size: 25 },
            isLoading: false,
            error: null,
            refetch: vi.fn(),
        } as any)

        render(<DashboardPage />, { wrapper: createWrapper() })

        expect(screen.getByText(/no servers yet/i)).toBeInTheDocument()
        expect(screen.getByRole('button', { name: /add new server/i })).toBeInTheDocument()
    })

    it('displays list of servers', () => {
        const servers = [
            createMockServer({ id: 'server-1', name: 'Server 1' }),
            createMockServer({ id: 'server-2', name: 'Server 2' }),
        ]

        mockUseMyServers.mockReturnValue({
            data: { data: servers, total: 2, page: 1, page_size: 25 },
            isLoading: false,
            error: null,
            refetch: vi.fn(),
        } as any)

        render(<DashboardPage />, { wrapper: createWrapper() })

        expect(screen.getByText('Server 1')).toBeInTheDocument()
        expect(screen.getByText('Server 2')).toBeInTheDocument()
    })

    it('shows create form when add server is clicked', async () => {
        const user = userEvent.setup()
        mockUseMyServers.mockReturnValue({
            data: { data: [], total: 0, page: 1, page_size: 25 },
            isLoading: false,
            error: null,
            refetch: vi.fn(),
        } as any)

        render(<DashboardPage />, { wrapper: createWrapper() })

        const addButton = screen.getByRole('button', { name: /add new server/i })
        await user.click(addButton)

        expect(screen.getByText(/create new server/i)).toBeInTheDocument()
        expect(screen.getByLabelText(/server name/i)).toBeInTheDocument()
    })

    it('creates a new server', async () => {
        const user = userEvent.setup()
        vi.mocked(createServer).mockResolvedValue({} as any)

        mockUseMyServers.mockReturnValue({
            data: { data: [], total: 0, page: 1, page_size: 25 },
            isLoading: false,
            error: null,
            refetch: vi.fn(),
        } as any)

        render(<DashboardPage />, { wrapper: createWrapper() })

        await user.click(screen.getByRole('button', { name: /add new server/i }))

        // Required fields so Create Server button is enabled
        await user.type(screen.getByLabelText(/server name/i), 'New Server')
        await user.type(screen.getByLabelText(/^map/i), 'The Island')
        await user.selectOptions(screen.getByLabelText(/game mode/i), 'pvp')
        await user.click(screen.getByRole('radio', { name: /pc only/i }))
        await user.click(screen.getByRole('button', { name: 'Vanilla' }))
        await user.click(screen.getByLabelText(/confirm self-hosted/i))
        await user.type(screen.getByLabelText(/description/i), 'Server description')

        await user.click(screen.getByRole('button', { name: /create server/i }))

        await waitFor(() => {
            expect(createServer).toHaveBeenCalledWith(
                expect.objectContaining({
                    name: 'New Server',
                    description: 'Server description',
                })
            )
            expect(mockInvalidate).toHaveBeenCalled()
        })
    })

    it('handles create server error gracefully', async () => {
        const user = userEvent.setup()
        const error = new APIErrorResponse({ code: 'NOT_IMPLEMENTED', message: 'Not yet implemented' })
        vi.mocked(createServer).mockRejectedValue(error)

        mockUseMyServers.mockReturnValue({
            data: { data: [], total: 0, page: 1, page_size: 25 },
            isLoading: false,
            error: null,
            refetch: vi.fn(),
        } as any)

        render(<DashboardPage />, { wrapper: createWrapper() })

        await user.click(screen.getByRole('button', { name: /add new server/i }))
        await user.type(screen.getByLabelText(/server name/i), 'New Server')
        await user.type(screen.getByLabelText(/^map/i), 'The Island')
        await user.selectOptions(screen.getByLabelText(/game mode/i), 'pvp')
        await user.click(screen.getByRole('radio', { name: /pc only/i }))
        await user.click(screen.getByRole('button', { name: 'Vanilla' }))
        await user.click(screen.getByLabelText(/confirm self-hosted/i))
        await user.click(screen.getByRole('button', { name: /create server/i }))

        await waitFor(
            () => {
                expect(screen.getByText(/not yet available/i)).toBeInTheDocument()
            },
            { timeout: 5000 }
        )
    })

    it('shows edit form when edit is clicked', async () => {
        const user = userEvent.setup()
        const server = createMockServer({ id: 'server-1', name: 'Test Server' })

        mockUseMyServers.mockReturnValue({
            data: { data: [server], total: 1, page: 1, page_size: 25 },
            isLoading: false,
            error: null,
            refetch: vi.fn(),
        } as any)

        render(<DashboardPage />, { wrapper: createWrapper() })

        const editButton = screen.getByRole('button', { name: /edit/i })
        await user.click(editButton)

        expect(screen.getByText(/edit server/i)).toBeInTheDocument()
        expect(screen.getByDisplayValue('Test Server')).toBeInTheDocument()
    })

    it('updates a server', async () => {
        const user = userEvent.setup()
        const server = createMockServer({ id: 'server-1', name: 'Old Name' })
        vi.mocked(updateServer).mockResolvedValue({} as any)

        mockUseMyServers.mockReturnValue({
            data: { data: [server], total: 1, page: 1, page_size: 25 },
            isLoading: false,
            error: null,
            refetch: vi.fn(),
        } as any)

        render(<DashboardPage />, { wrapper: createWrapper() })

        await user.click(screen.getByRole('button', { name: /edit/i }))

        await waitFor(() => {
            expect(screen.getByDisplayValue('Old Name')).toBeInTheDocument()
        })

        const nameInput = screen.getByDisplayValue('Old Name')
        await user.clear(nameInput)
        await user.type(nameInput, 'New Name')

        const saveButton = await screen.findByRole('button', { name: /save changes/i })
        await user.click(saveButton)

        await waitFor(
            () => {
                expect(updateServer).toHaveBeenCalled()
                const call = vi.mocked(updateServer).mock.calls[0]
                expect(call[0]).toBe('server-1')
                expect(call[1]).toMatchObject({
                    name: 'New Name',
                    description: 'Test description',
                })
                expect(mockInvalidate).toHaveBeenCalled()
            },
            { timeout: 5000 }
        )
    })

    it('shows delete confirmation dialog', async () => {
        const user = userEvent.setup()
        const server = createMockServer({ id: 'server-1', name: 'Test Server' })

        mockUseMyServers.mockReturnValue({
            data: { data: [server], total: 1, page: 1, page_size: 25 },
            isLoading: false,
            error: null,
            refetch: vi.fn(),
        } as any)

        render(<DashboardPage />, { wrapper: createWrapper() })

        await user.click(screen.getByRole('button', { name: /edit/i }))
        const deleteButton = screen.getByRole('button', { name: /delete server/i })
        await user.click(deleteButton)

        expect(screen.getByText(/delete server\?/i)).toBeInTheDocument()
        expect(screen.getByText(/test server/i)).toBeInTheDocument()
    })

    it('deletes a server on confirmation', async () => {
        const user = userEvent.setup()
        const server = createMockServer({ id: 'server-1', name: 'Test Server' })
        vi.mocked(deleteServer).mockResolvedValue({ success: true } as any)

        mockUseMyServers.mockReturnValue({
            data: { data: [server], total: 1, page: 1, page_size: 25 },
            isLoading: false,
            error: null,
            refetch: vi.fn(),
        } as any)

        render(<DashboardPage />, { wrapper: createWrapper() })

        await user.click(screen.getByRole('button', { name: /edit/i }))
        await user.click(screen.getByRole('button', { name: /delete server/i }))

        const dialog = screen.getByRole('dialog')
        const confirmButton = within(dialog).getByRole('button', { name: /confirm delete server/i })
        await user.click(confirmButton)

        await waitFor(
            () => {
                expect(deleteServer).toHaveBeenCalledWith('server-1')
            },
            { timeout: 3000 }
        )

        expect(mockInvalidate).toHaveBeenCalled()
    })

    it('cancels delete confirmation', async () => {
        const user = userEvent.setup()
        const server = createMockServer({ id: 'server-1', name: 'Test Server' })

        mockUseMyServers.mockReturnValue({
            data: { data: [server], total: 1, page: 1, page_size: 25 },
            isLoading: false,
            error: null,
            refetch: vi.fn(),
        } as any)

        render(<DashboardPage />, { wrapper: createWrapper() })

        await user.click(screen.getByRole('button', { name: /edit/i }))
        await user.click(screen.getByRole('button', { name: /delete server/i }))
        const dialog = screen.getByRole('dialog')
        await user.click(within(dialog).getByRole('button', { name: /cancel/i }))

        expect(deleteServer).not.toHaveBeenCalled()
        expect(screen.queryByRole('dialog')).not.toBeInTheDocument()
    })

    it('cancels create form', async () => {
        const user = userEvent.setup()
        mockUseMyServers.mockReturnValue({
            data: { data: [], total: 0, page: 1, page_size: 25 },
            isLoading: false,
            error: null,
            refetch: vi.fn(),
        } as any)

        render(<DashboardPage />, { wrapper: createWrapper() })

        await user.click(screen.getByRole('button', { name: /add new server/i }))
        await user.click(screen.getByRole('button', { name: /cancel/i }))

        expect(screen.queryByText(/create new server/i)).not.toBeInTheDocument()
    })

    it('cancels edit form', async () => {
        const user = userEvent.setup()
        const server = createMockServer({ id: 'server-1', name: 'Test Server' })

        mockUseMyServers.mockReturnValue({
            data: { data: [server], total: 1, page: 1, page_size: 25 },
            isLoading: false,
            error: null,
            refetch: vi.fn(),
        } as any)

        render(<DashboardPage />, { wrapper: createWrapper() })

        await user.click(screen.getByRole('button', { name: /edit/i }))
        await user.click(screen.getByRole('button', { name: /cancel/i }))

        expect(screen.queryByText(/edit server/i)).not.toBeInTheDocument()
    })
})
