/**
 * Tests for ServerCard component.
 */

import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import { ServerCard } from './ServerCard'
import type { DirectoryServer } from '@/types'

// Helper to create mock server data
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
function ServerCardWrapper({ server }: { server: DirectoryServer }) {
    return (
        <BrowserRouter>
            <ServerCard server={server} />
        </BrowserRouter>
    )
}

describe('ServerCard', () => {
    it('renders server name', () => {
        const server = createMockServer()
        render(<ServerCardWrapper server={server} />)

        expect(screen.getByText('Test Server')).toBeInTheDocument()
    })

    it('renders server description', () => {
        const server = createMockServer()
        render(<ServerCardWrapper server={server} />)

        expect(screen.getByText('A test server description')).toBeInTheDocument()
    })

    it('renders map name', () => {
        const server = createMockServer()
        render(<ServerCardWrapper server={server} />)

        expect(screen.getByText('The Island')).toBeInTheDocument()
    })

    it('renders cluster name when present', () => {
        const server = createMockServer({ cluster_name: 'Test Cluster' })
        render(<ServerCardWrapper server={server} />)

        expect(screen.getByText(/Cluster: Test Cluster/)).toBeInTheDocument()
    })

    it('does not render cluster name when absent', () => {
        const server = createMockServer({ cluster_name: null })
        render(<ServerCardWrapper server={server} />)

        expect(screen.queryByText(/Cluster:/)).not.toBeInTheDocument()
    })

    it('renders status badge', () => {
        const server = createMockServer({ effective_status: 'online' })
        render(<ServerCardWrapper server={server} />)

        expect(screen.getByText('Online')).toBeInTheDocument()
    })

    it('renders game mode badge', () => {
        const server = createMockServer({ game_mode: 'pvp' })
        render(<ServerCardWrapper server={server} />)

        expect(screen.getByText('PvP')).toBeInTheDocument()
    })

    it('renders ruleset badge', () => {
        const server = createMockServer({ ruleset: 'boosted' })
        render(<ServerCardWrapper server={server} />)

        expect(screen.getByText('Boosted')).toBeInTheDocument()
    })

    it('renders verified badge when server is verified', () => {
        const server = createMockServer({ is_verified: true })
        render(<ServerCardWrapper server={server} />)

        expect(screen.getByText('Verified')).toBeInTheDocument()
    })

    it('renders new badge when server is new', () => {
        const server = createMockServer({ is_new: true })
        render(<ServerCardWrapper server={server} />)

        expect(screen.getByText('New')).toBeInTheDocument()
    })

    it('renders stable badge when server is stable', () => {
        const server = createMockServer({ is_stable: true })
        render(<ServerCardWrapper server={server} />)

        expect(screen.getByText('Stable')).toBeInTheDocument()
    })

    it('renders favorite count', () => {
        const server = createMockServer({ favorite_count: 5 })
        render(<ServerCardWrapper server={server} />)

        expect(screen.getByText('5 favorites')).toBeInTheDocument()
    })

    it('renders singular favorite count', () => {
        const server = createMockServer({ favorite_count: 1 })
        render(<ServerCardWrapper server={server} />)

        expect(screen.getByText('1 favorite')).toBeInTheDocument()
    })

    it('renders zero favorites', () => {
        const server = createMockServer({ favorite_count: 0 })
        render(<ServerCardWrapper server={server} />)

        expect(screen.getByText('0 favorites')).toBeInTheDocument()
    })

    it('renders view details link with correct href', () => {
        const server = createMockServer({ id: 'server-123' })
        render(<ServerCardWrapper server={server} />)

        const link = screen.getByRole('link', { name: /view details/i })
        expect(link).toHaveAttribute('href', '/servers/server-123')
    })

    it('renders view details link with accessible label', () => {
        const server = createMockServer({ name: 'My Server' })
        render(<ServerCardWrapper server={server} />)

        const link = screen.getByRole('link', { name: /view details for my server/i })
        expect(link).toBeInTheDocument()
    })

    it('does not render description when absent', () => {
        const server = createMockServer({ description: null })
        render(<ServerCardWrapper server={server} />)

        // Description should not be rendered
        expect(screen.queryByText(/description/i)).not.toBeInTheDocument()
    })

    it('does not render map name when absent', () => {
        const server = createMockServer({ map_name: null })
        render(<ServerCardWrapper server={server} />)

        expect(screen.queryByText(/The Island/)).not.toBeInTheDocument()
    })
})
