/**
 * Error message component.
 *
 * Displays user-friendly error messages with optional retry action.
 */

import { APIErrorResponse } from '@/lib/api'

interface ErrorMessageProps {
    error: unknown
    title?: string
    onRetry?: () => void
    className?: string
}

function getErrorMessage(error: unknown): string {
    if (error instanceof APIErrorResponse) {
        // Handle specific error codes
        if (error.code === 'UNAUTHORIZED') {
            return 'Please sign in to continue.'
        }
        if (error.code === 'FORBIDDEN') {
            return "You don't have permission to perform this action."
        }
        if (error.code === 'NOT_FOUND') {
            return 'The requested resource was not found.'
        }
        if (error.code === 'DOMAIN_VALIDATION_ERROR') {
            return error.message || 'Invalid input. Please check your data and try again.'
        }
        // Generic API error
        return error.message || 'An error occurred. Please try again.'
    }
    if (error instanceof Error) {
        return error.message
    }
    return 'An unexpected error occurred. Please try again.'
}

export function ErrorMessage({ error, title, onRetry, className }: ErrorMessageProps) {
    const message = getErrorMessage(error)

    return (
        <div
            className={`bg-destructive/10 border border-destructive/30 rounded-lg p-4 ${className ?? ''}`}
            role="alert"
        >
            <div className="flex items-start gap-3">
                <div className="flex-1">
                    {title && (
                        <h3 className="text-sm font-semibold text-destructive mb-1">{title}</h3>
                    )}
                    <p className="text-sm text-destructive">{message}</p>
                </div>
                {onRetry && (
                    <button
                        type="button"
                        onClick={onRetry}
                        className="text-sm text-destructive hover:text-destructive/80 font-medium transition-colors shrink-0"
                    >
                        Retry
                    </button>
                )}
            </div>
        </div>
    )
}
