/**
 * Tests for ErrorMessage component.
 */

import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { ErrorMessage } from './ErrorMessage'
import { APIErrorResponse } from '@/lib/api'

describe('ErrorMessage', () => {
    it('renders error message from Error instance', () => {
        const error = new Error('Something went wrong')
        render(<ErrorMessage error={error} />)

        expect(screen.getByText('Something went wrong')).toBeInTheDocument()
        expect(screen.getByRole('alert')).toBeInTheDocument()
    })

    it('renders custom title when provided', () => {
        const error = new Error('Test error')
        render(<ErrorMessage error={error} title="Custom Title" />)

        expect(screen.getByText('Custom Title')).toBeInTheDocument()
        expect(screen.getByText('Test error')).toBeInTheDocument()
    })

    it('renders retry button when onRetry is provided', async () => {
        const user = userEvent.setup()
        const error = new Error('Test error')
        const onRetry = vi.fn()

        render(<ErrorMessage error={error} onRetry={onRetry} />)

        const retryButton = screen.getByRole('button', { name: /retry/i })
        expect(retryButton).toBeInTheDocument()

        await user.click(retryButton)
        expect(onRetry).toHaveBeenCalledOnce()
    })

    it('does not render retry button when onRetry is not provided', () => {
        const error = new Error('Test error')
        render(<ErrorMessage error={error} />)

        expect(screen.queryByRole('button')).not.toBeInTheDocument()
    })

    it('handles APIErrorResponse with UNAUTHORIZED code', () => {
        const error = new APIErrorResponse({ code: 'UNAUTHORIZED', message: 'Auth required' })
        render(<ErrorMessage error={error} />)

        expect(screen.getByText('Please sign in to continue.')).toBeInTheDocument()
    })

    it('handles APIErrorResponse with FORBIDDEN code', () => {
        const error = new APIErrorResponse({ code: 'FORBIDDEN', message: 'No access' })
        render(<ErrorMessage error={error} />)

        expect(screen.getByText("You don't have permission to perform this action.")).toBeInTheDocument()
    })

    it('handles APIErrorResponse with NOT_FOUND code', () => {
        const error = new APIErrorResponse({ code: 'NOT_FOUND', message: 'Not found' })
        render(<ErrorMessage error={error} />)

        expect(screen.getByText('The requested resource was not found.')).toBeInTheDocument()
    })

    it('handles APIErrorResponse with DOMAIN_VALIDATION_ERROR code', () => {
        const error = new APIErrorResponse({
            code: 'DOMAIN_VALIDATION_ERROR',
            message: 'Invalid input data',
        })
        render(<ErrorMessage error={error} />)

        expect(screen.getByText('Invalid input data')).toBeInTheDocument()
    })

    it('handles generic APIErrorResponse', () => {
        const error = new APIErrorResponse({ code: 'HTTP_ERROR', message: 'Server error' })
        render(<ErrorMessage error={error} />)

        expect(screen.getByText('Server error')).toBeInTheDocument()
    })

    it('handles unknown error type', () => {
        const error = { someProperty: 'value' }
        render(<ErrorMessage error={error} />)

        expect(screen.getByText('An unexpected error occurred. Please try again.')).toBeInTheDocument()
    })

    it('applies custom className', () => {
        const error = new Error('Test')
        const { container } = render(<ErrorMessage error={error} className="custom-class" />)

        expect(container.firstChild).toHaveClass('custom-class')
    })
})
