/**
 * Tests for LoadingSpinner component.
 */

import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { LoadingSpinner } from './LoadingSpinner'

describe('LoadingSpinner', () => {
    it('renders with default size', () => {
        const { container } = render(<LoadingSpinner />)
        const spinner = container.firstChild as HTMLElement

        expect(spinner).toBeInTheDocument()
        expect(spinner).toHaveClass('w-6', 'h-6', 'border-2')
        expect(spinner).toHaveAttribute('role', 'status')
        expect(spinner).toHaveAttribute('aria-label', 'Loading')
    })

    it('renders with small size', () => {
        const { container } = render(<LoadingSpinner size="sm" />)
        const spinner = container.firstChild as HTMLElement

        expect(spinner).toHaveClass('w-4', 'h-4', 'border-2')
    })

    it('renders with large size', () => {
        const { container } = render(<LoadingSpinner size="lg" />)
        const spinner = container.firstChild as HTMLElement

        expect(spinner).toHaveClass('w-8', 'h-8', 'border-3')
    })

    it('includes screen reader text', () => {
        render(<LoadingSpinner />)
        expect(screen.getByText('Loading...')).toBeInTheDocument()
        expect(screen.getByText('Loading...')).toHaveClass('sr-only')
    })

    it('applies custom className', () => {
        const { container } = render(<LoadingSpinner className="custom-class" />)
        const spinner = container.firstChild as HTMLElement

        expect(spinner).toHaveClass('custom-class')
    })
})
