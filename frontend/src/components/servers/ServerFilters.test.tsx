/**
 * Tests for ServerFilters component.
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { ServerFilters } from './ServerFilters'

describe('ServerFilters', () => {
    const mockOnFiltersChange = vi.fn()

    beforeEach(() => {
        mockOnFiltersChange.mockClear()
    })

    it('renders with filters panel open by default', () => {
        render(<ServerFilters filters={{}} onFiltersChange={mockOnFiltersChange} />)

        expect(screen.getByText('Hide Filters')).toBeInTheDocument()
        expect(screen.getByLabelText(/search/i)).toBeInTheDocument()
    })

    it('toggles filters panel visibility', async () => {
        const user = userEvent.setup()
        render(<ServerFilters filters={{}} onFiltersChange={mockOnFiltersChange} />)

        const toggleButton = screen.getByRole('button', { name: /hide filters/i })
        expect(screen.getByLabelText(/search/i)).toBeInTheDocument()

        await user.click(toggleButton)
        expect(screen.getByRole('button', { name: /show filters/i })).toBeInTheDocument()
        expect(screen.queryByLabelText(/search/i)).not.toBeInTheDocument()
    })

    it('shows clear all button when filters are active', () => {
        render(
            <ServerFilters
                filters={{ q: 'test', status: 'online' }}
                onFiltersChange={mockOnFiltersChange}
            />
        )

        expect(screen.getByRole('button', { name: /clear all/i })).toBeInTheDocument()
    })

    it('does not show clear all button when no filters are active', () => {
        render(<ServerFilters filters={{}} onFiltersChange={mockOnFiltersChange} />)

        expect(screen.queryByRole('button', { name: /clear all/i })).not.toBeInTheDocument()
    })

    it('updates search filter on input change', async () => {
        const user = userEvent.setup()
        render(<ServerFilters filters={{}} onFiltersChange={mockOnFiltersChange} />)

        const searchInput = screen.getByLabelText(/search/i)
        await user.type(searchInput, 'test server')

        expect(searchInput).toHaveValue('test server')
    })

    it('submits filters on form submit', async () => {
        const user = userEvent.setup()
        render(<ServerFilters filters={{}} onFiltersChange={mockOnFiltersChange} />)

        const searchInput = screen.getByLabelText(/search/i)
        await user.type(searchInput, 'test')

        const submitButton = screen.getByRole('button', { name: /apply filters/i })
        await user.click(submitButton)

        expect(mockOnFiltersChange).toHaveBeenCalledWith({ q: 'test' })
    })

    it('updates status filter', async () => {
        const user = userEvent.setup()
        render(<ServerFilters filters={{}} onFiltersChange={mockOnFiltersChange} />)

        const statusSelect = screen.getByLabelText(/status/i)
        await user.selectOptions(statusSelect, 'online')

        const submitButton = screen.getByRole('button', { name: /apply filters/i })
        await user.click(submitButton)

        expect(mockOnFiltersChange).toHaveBeenCalledWith({ status: 'online' })
    })

    it('updates verification mode filter', async () => {
        const user = userEvent.setup()
        render(<ServerFilters filters={{}} onFiltersChange={mockOnFiltersChange} />)

        const modeSelect = screen.getByLabelText(/verification/i)
        await user.selectOptions(modeSelect, 'verified')

        const submitButton = screen.getByRole('button', { name: /apply filters/i })
        await user.click(submitButton)

        expect(mockOnFiltersChange).toHaveBeenCalledWith({ mode: 'verified' })
    })

    it('updates game mode filter', async () => {
        const user = userEvent.setup()
        render(<ServerFilters filters={{}} onFiltersChange={mockOnFiltersChange} />)

        const gameModeSelect = screen.getByLabelText(/game mode/i)
        await user.selectOptions(gameModeSelect, 'pvp')

        const submitButton = screen.getByRole('button', { name: /apply filters/i })
        await user.click(submitButton)

        expect(mockOnFiltersChange).toHaveBeenCalledWith({ game_mode: 'pvp' })
    })

    it('updates ruleset filter', async () => {
        const user = userEvent.setup()
        render(<ServerFilters filters={{}} onFiltersChange={mockOnFiltersChange} />)

        const rulesetSelect = screen.getByLabelText(/ruleset/i)
        await user.selectOptions(rulesetSelect, 'boosted')

        const submitButton = screen.getByRole('button', { name: /apply filters/i })
        await user.click(submitButton)

        expect(mockOnFiltersChange).toHaveBeenCalledWith({ ruleset: 'boosted' })
    })

    it('updates sort by filter', async () => {
        const user = userEvent.setup()
        render(<ServerFilters filters={{}} onFiltersChange={mockOnFiltersChange} />)

        const rankBySelect = screen.getByLabelText(/sort by/i)
        await user.selectOptions(rankBySelect, 'favorites')

        const submitButton = screen.getByRole('button', { name: /apply filters/i })
        await user.click(submitButton)

        expect(mockOnFiltersChange).toHaveBeenCalledWith({ rank_by: 'favorites' })
    })

    it('updates order filter', async () => {
        const user = userEvent.setup()
        render(<ServerFilters filters={{}} onFiltersChange={mockOnFiltersChange} />)

        const orderSelect = screen.getByLabelText(/order/i)
        await user.selectOptions(orderSelect, 'asc')

        const submitButton = screen.getByRole('button', { name: /apply filters/i })
        await user.click(submitButton)

        expect(mockOnFiltersChange).toHaveBeenCalledWith({ order: 'asc' })
    })

    it('resets all filters when reset button is clicked', async () => {
        const user = userEvent.setup()
        render(
            <ServerFilters
                filters={{ q: 'test', status: 'online', game_mode: 'pvp' }}
                onFiltersChange={mockOnFiltersChange}
            />
        )

        const resetButton = screen.getByRole('button', { name: /reset all filters/i })
        await user.click(resetButton)

        expect(mockOnFiltersChange).toHaveBeenCalledWith({})
    })

    it('resets all filters when clear all button is clicked', async () => {
        const user = userEvent.setup()
        render(
            <ServerFilters
                filters={{ q: 'test', status: 'online' }}
                onFiltersChange={mockOnFiltersChange}
            />
        )

        const clearAllButton = screen.getByRole('button', { name: /clear all/i })
        await user.click(clearAllButton)

        expect(mockOnFiltersChange).toHaveBeenCalledWith({})
    })

    it('syncs local state with props changes', () => {
        const { rerender } = render(
            <ServerFilters filters={{ q: 'initial' }} onFiltersChange={mockOnFiltersChange} />
        )

        expect(screen.getByLabelText(/search/i)).toHaveValue('initial')

        rerender(
            <ServerFilters filters={{ q: 'updated' }} onFiltersChange={mockOnFiltersChange} />
        )

        expect(screen.getByLabelText(/search/i)).toHaveValue('updated')
    })

    it('has correct default values for sort and order', () => {
        render(<ServerFilters filters={{}} onFiltersChange={mockOnFiltersChange} />)

        const rankBySelect = screen.getByLabelText(/sort by/i) as HTMLSelectElement
        const orderSelect = screen.getByLabelText(/order/i) as HTMLSelectElement

        expect(rankBySelect.value).toBe('updated')
        expect(orderSelect.value).toBe('desc')
    })

    it('handles multiple filters at once', async () => {
        const user = userEvent.setup()
        render(<ServerFilters filters={{}} onFiltersChange={mockOnFiltersChange} />)

        // Set multiple filters
        await user.type(screen.getByLabelText(/search/i), 'test')
        await user.selectOptions(screen.getByLabelText(/status/i), 'online')
        await user.selectOptions(screen.getByLabelText(/game mode/i), 'pve')
        await user.selectOptions(screen.getByLabelText(/ruleset/i), 'boosted')

        const submitButton = screen.getByRole('button', { name: /apply filters/i })
        await user.click(submitButton)

        expect(mockOnFiltersChange).toHaveBeenCalledWith({
            q: 'test',
            status: 'online',
            game_mode: 'pve',
            ruleset: 'boosted',
        })
    })

    it('clears search when empty string is entered', async () => {
        const user = userEvent.setup()
        render(<ServerFilters filters={{ q: 'test' }} onFiltersChange={mockOnFiltersChange} />)

        const searchInput = screen.getByLabelText(/search/i)
        await user.clear(searchInput)

        const submitButton = screen.getByRole('button', { name: /apply filters/i })
        await user.click(submitButton)

        expect(mockOnFiltersChange).toHaveBeenCalledWith({})
    })
})
