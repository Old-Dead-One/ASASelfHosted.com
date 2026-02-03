/**
 * Tests for ServerRow component.
 */

import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import { ServerRow } from './ServerRow'
import type { DirectoryServer } from '@/types'

// Helper to create mock server data (reused from ServerCard.test.tsx)
function createMockServer(overrides?: Partial<DirectoryServer>): DirectoryServer {
    return {
        id: 'test-server-1',
        name: 'Test Server',
        description: 'A test server description',
        map_name: 'The Island',
        join_address: '123.456.789.0:7777',
        join_password: null,
        join_instructions_pc: null,
        join_instructions_console: null,
        discord_url: null,
        website_url: null,
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
        favorite_count: 5,
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
        server_type: null,
        is_verified: true,
        is_new: false,
        is_stable: true,
        platforms: ['steam'],
        is_official_plus: null,
        is_modded: null,
        is_crossplay: null,
        is_console: null,
        is_pc: null,
        is_PC: null,
        ...overrides,
    }
}

// Wrapper component for Router context
function ServerRowWrapper({ server }: { server: DirectoryServer }) {
    return (
        <BrowserRouter>
            <ServerRow server={server} />
        </BrowserRouter>
    )
}

describe('ServerRow', () => {
    it('renders server name', () => {
        const server = createMockServer()
        render(<ServerRowWrapper server={server} />)

        expect(screen.getByText('Test Server')).toBeInTheDocument()
    })

    it('renders status badge', () => {
        const server = createMockServer({ effective_status: 'online' })
        render(<ServerRowWrapper server={server} />)

        expect(screen.getByText('Online')).toBeInTheDocument()
    })

    it('renders game mode badge', () => {
        const server = createMockServer({ game_mode: 'pvp' })
        render(<ServerRowWrapper server={server} />)

        expect(screen.getByText('PvP')).toBeInTheDocument()
    })

    it('renders ruleset badge', () => {
        const server = createMockServer({ ruleset: 'boosted' })
        render(<ServerRowWrapper server={server} />)

        expect(screen.getByText('Boosted')).toBeInTheDocument()
    })

    it('renders verified badge when server is verified', () => {
        const server = createMockServer({ is_verified: true })
        render(<ServerRowWrapper server={server} />)

        expect(screen.getByText('Verified')).toBeInTheDocument()
    })

    it('renders map name', () => {
        const server = createMockServer({ map_name: 'The Island' })
        render(<ServerRowWrapper server={server} />)

        expect(screen.getByText('The Island')).toBeInTheDocument()
    })

    it('renders cluster name when present', () => {
        const server = createMockServer({ cluster_name: 'Test Cluster' })
        render(<ServerRowWrapper server={server} />)

        // Cluster name is rendered with a "· " prefix
        expect(screen.getByText(/· Test Cluster/)).toBeInTheDocument()
    })

    it('renders description', () => {
        const server = createMockServer({ description: 'Test description' })
        render(<ServerRowWrapper server={server} />)

        // Description is rendered with a "· " prefix and may be hidden on small screens
        expect(screen.getByText(/· Test description/)).toBeInTheDocument()
    })

    it('renders player count', () => {
        const server = createMockServer({ players_current: 10, players_capacity: 50 })
        render(<ServerRowWrapper server={server} />)

        // Player count is rendered as "10/50"
        expect(screen.getByText('10/50')).toBeInTheDocument()
    })

    it('renders favorite count', () => {
        const server = createMockServer({ favorite_count: 5 })
        render(<ServerRowWrapper server={server} />)

        // Favorite count is rendered as "5 fav"
        expect(screen.getByText(/5 fav/)).toBeInTheDocument()
    })

    it('renders view link with correct href', () => {
        const server = createMockServer({ id: 'server-123' })
        render(<ServerRowWrapper server={server} />)

        const link = screen.getByRole('link', { name: /view/i })
        expect(link).toHaveAttribute('href', '/servers/server-123')
    })

    it('renders view link with accessible label', () => {
        const server = createMockServer({ name: 'My Server' })
        render(<ServerRowWrapper server={server} />)

        const link = screen.getByRole('link', { name: /view details for my server/i })
        expect(link).toBeInTheDocument()
    })

    it('handles null player counts', () => {
        const server = createMockServer({ players_current: null, players_capacity: null })
        render(<ServerRowWrapper server={server} />)

        // Should not crash, player count may not be displayed
        expect(screen.getByText('Test Server')).toBeInTheDocument()
    })
})
