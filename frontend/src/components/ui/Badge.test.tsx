/**
 * Tests for Badge component.
 */

import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { Badge } from './Badge'
import type { BadgeType } from '@/types'

describe('Badge', () => {
    const badgeTypes: BadgeType[] = [
        'verified',
        'new',
        'stable',
        'pvp',
        'pve',
        'pvpve',
        'vanilla',
        'vanilla_qol',
        'boosted',
        'modded',
        'newbie_friendly',
        'learning_friendly',
    ]

    it.each(badgeTypes)('renders %s badge with correct label', (type) => {
        render(<Badge type={type} />)
        const badge = screen.getByText(new RegExp(type === 'pvpve' ? 'PvPvE' : type === 'vanilla_qol' ? 'Vanilla QoL' : type === 'newbie_friendly' ? 'Newbie Friendly' : type === 'learning_friendly' ? 'Learning Friendly' : type.charAt(0).toUpperCase() + type.slice(1), 'i'))
        expect(badge).toBeInTheDocument()
    })

    it('renders verified badge with correct styling', () => {
        const { container } = render(<Badge type="verified" />)
        const badge = container.firstChild as HTMLElement

        expect(badge).toHaveTextContent('Verified')
        expect(badge).toHaveClass('bg-primary', 'text-primary-foreground')
    })

    it('renders pvp badge with danger styling', () => {
        const { container } = render(<Badge type="pvp" />)
        const badge = container.firstChild as HTMLElement

        expect(badge).toHaveTextContent('PvP')
        expect(badge).toHaveClass('bg-destructive/20', 'text-destructive')
    })

    it('renders pve badge with success styling', () => {
        const { container } = render(<Badge type="pve" />)
        const badge = container.firstChild as HTMLElement

        expect(badge).toHaveTextContent('PvE')
        expect(badge).toHaveClass('bg-success/20', 'text-success')
    })

    it('applies custom className', () => {
        const { container } = render(<Badge type="verified" className="custom-class" />)
        const badge = container.firstChild as HTMLElement

        expect(badge).toHaveClass('custom-class')
    })

    it('handles unknown badge type gracefully', () => {
        // TypeScript will complain, but runtime should handle it
        render(<Badge type={'unknown_type' as BadgeType} />)
        const badge = screen.getByText('unknown_type')
        expect(badge).toBeInTheDocument()
        expect(badge).toHaveClass('bg-muted', 'text-muted-foreground')
    })
})
