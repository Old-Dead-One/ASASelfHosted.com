/**
 * Tests for SignUpPage component.
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { BrowserRouter } from 'react-router-dom'
import { SignUpPage } from './SignUpPage'

// Mock the useAuth hook
vi.mock('@/contexts/AuthContext', () => ({
    useAuth: vi.fn(),
}))

import { useAuth } from '@/contexts/AuthContext'

const mockSignUp = vi.fn()
const mockUseAuth = vi.mocked(useAuth)

// Wrapper with Router
function SignUpPageWrapper() {
    return (
        <BrowserRouter>
            <SignUpPage />
        </BrowserRouter>
    )
}

describe('SignUpPage', () => {
    beforeEach(() => {
        vi.clearAllMocks()
        mockUseAuth.mockReturnValue({
            isAuthenticated: false,
            user: null,
            signIn: vi.fn(),
            signUp: mockSignUp,
            signOut: vi.fn(),
            loading: false,
            userId: null,
        })
    })

    it('renders sign up form', () => {
        render(<SignUpPageWrapper />)

        expect(screen.getByRole('heading', { name: 'Sign Up' })).toBeInTheDocument()
        expect(screen.getByLabelText(/^email$/i)).toBeInTheDocument()
        expect(screen.getByLabelText(/^password$/i)).toBeInTheDocument()
        expect(screen.getByLabelText(/confirm password/i)).toBeInTheDocument()
        expect(screen.getByRole('button', { name: /^sign up$/i })).toBeInTheDocument()
    })

    it('renders sign in link', () => {
        render(<SignUpPageWrapper />)

        const signInLink = screen.getByRole('link', { name: /sign in/i })
        expect(signInLink).toBeInTheDocument()
        expect(signInLink).toHaveAttribute('href', '/login')
    })

    it('updates form inputs', async () => {
        const user = userEvent.setup()
        render(<SignUpPageWrapper />)

        const emailInput = screen.getByLabelText(/^email$/i)
        const passwordInput = screen.getByLabelText(/^password$/i)
        const confirmPasswordInput = screen.getByLabelText(/confirm password/i)

        await user.type(emailInput, 'test@example.com')
        await user.type(passwordInput, 'password123')
        await user.type(confirmPasswordInput, 'password123')

        expect(emailInput).toHaveValue('test@example.com')
        expect(passwordInput).toHaveValue('password123')
        expect(confirmPasswordInput).toHaveValue('password123')
    })

    it('validates password match', async () => {
        const user = userEvent.setup()
        render(<SignUpPageWrapper />)

        await user.type(screen.getByLabelText(/^email$/i), 'test@example.com')
        await user.type(screen.getByLabelText(/^password$/i), 'password123')
        await user.type(screen.getByLabelText(/confirm password/i), 'different')

        const submitButton = screen.getByRole('button', { name: /sign up/i })
        await user.click(submitButton)

        await waitFor(() => {
            expect(screen.getByText('Passwords do not match')).toBeInTheDocument()
        })

        expect(mockSignUp).not.toHaveBeenCalled()
    })

    it('validates password length', async () => {
        const user = userEvent.setup()
        render(<SignUpPageWrapper />)

        await user.type(screen.getByLabelText(/^email$/i), 'test@example.com')
        await user.type(screen.getByLabelText(/^password$/i), 'short')
        await user.type(screen.getByLabelText(/confirm password/i), 'short')

        const submitButton = screen.getByRole('button', { name: /sign up/i })
        await user.click(submitButton)

        await waitFor(() => {
            expect(screen.getByText('Password must be at least 8 characters')).toBeInTheDocument()
        })

        expect(mockSignUp).not.toHaveBeenCalled()
    })

    it('calls signUp on valid form submission', async () => {
        const user = userEvent.setup()
        mockSignUp.mockResolvedValue(undefined)

        render(<SignUpPageWrapper />)

        await user.type(screen.getByLabelText(/^email$/i), 'test@example.com')
        await user.type(screen.getByLabelText(/^password$/i), 'password123')
        await user.type(screen.getByLabelText(/confirm password/i), 'password123')

        const submitButton = screen.getByRole('button', { name: /sign up/i })
        await user.click(submitButton)

        await waitFor(() => {
            expect(mockSignUp).toHaveBeenCalledWith('test@example.com', 'password123')
        })
    })

    it('shows confirmation message after successful signup', async () => {
        const user = userEvent.setup()
        mockSignUp.mockResolvedValue(undefined)

        render(<SignUpPageWrapper />)

        await user.type(screen.getByLabelText(/^email$/i), 'test@example.com')
        await user.type(screen.getByLabelText(/^password$/i), 'password123')
        await user.type(screen.getByLabelText(/confirm password/i), 'password123')

        const submitButton = screen.getByRole('button', { name: /sign up/i })
        await user.click(submitButton)

        await waitFor(() => {
            expect(screen.getByText('Check your email')).toBeInTheDocument()
            expect(screen.getByText(/test@example.com/i)).toBeInTheDocument()
        })
    })

    it('shows loading state during submission', async () => {
        const user = userEvent.setup()
        let resolveSignUp: () => void
        const signUpPromise = new Promise<void>((resolve) => {
            resolveSignUp = resolve
        })
        mockSignUp.mockReturnValue(signUpPromise)

        render(<SignUpPageWrapper />)

        await user.type(screen.getByLabelText(/^email$/i), 'test@example.com')
        await user.type(screen.getByLabelText(/^password$/i), 'password123')
        await user.type(screen.getByLabelText(/confirm password/i), 'password123')

        const submitButton = screen.getByRole('button', { name: /^sign up$/i })
        await user.click(submitButton)

        // Button text changes to "Creating account..." when loading
        await waitFor(() => {
            const loadingButton = screen.getByText('Creating account...')
            expect(loadingButton).toBeInTheDocument()
            expect(loadingButton).toBeDisabled()
        })

        resolveSignUp!()
        await waitFor(() => {
            expect(screen.getByRole('button', { name: /^sign up$/i })).toBeInTheDocument()
        })
    })

    it('displays error message on sign up failure', async () => {
        const user = userEvent.setup()
        const error = new Error('Email already exists')
        mockSignUp.mockRejectedValue(error)

        render(<SignUpPageWrapper />)

        await user.type(screen.getByLabelText(/^email$/i), 'existing@example.com')
        await user.type(screen.getByLabelText(/^password$/i), 'password123')
        await user.type(screen.getByLabelText(/confirm password/i), 'password123')

        const submitButton = screen.getByRole('button', { name: /sign up/i })
        await user.click(submitButton)

        await waitFor(() => {
            expect(screen.getByText('Email already exists')).toBeInTheDocument()
        })
    })

    it('clears error message on new submission', async () => {
        const user = userEvent.setup()
        mockSignUp
            .mockRejectedValueOnce(new Error('First error'))
            .mockResolvedValueOnce(undefined)

        render(<SignUpPageWrapper />)

        const emailInput = screen.getByLabelText(/^email$/i)
        const passwordInput = screen.getByLabelText(/^password$/i)
        const confirmPasswordInput = screen.getByLabelText(/confirm password/i)

        // First submission - fails
        await user.type(emailInput, 'test@example.com')
        await user.type(passwordInput, 'password123')
        await user.type(confirmPasswordInput, 'password123')
        await user.click(screen.getByRole('button', { name: /sign up/i }))

        await waitFor(() => {
            expect(screen.getByText('First error')).toBeInTheDocument()
        })

        // Second submission - succeeds (error should clear)
        await user.clear(emailInput)
        await user.clear(passwordInput)
        await user.clear(confirmPasswordInput)
        await user.type(emailInput, 'new@example.com')
        await user.type(passwordInput, 'password123')
        await user.type(confirmPasswordInput, 'password123')
        await user.click(screen.getByRole('button', { name: /sign up/i }))

        await waitFor(() => {
            expect(screen.queryByText('First error')).not.toBeInTheDocument()
        })
    })

    it('requires all form fields', () => {
        render(<SignUpPageWrapper />)

        const emailInput = screen.getByLabelText(/^email$/i)
        const passwordInput = screen.getByLabelText(/^password$/i)
        const confirmPasswordInput = screen.getByLabelText(/confirm password/i)

        expect(emailInput).toBeRequired()
        expect(passwordInput).toBeRequired()
        expect(confirmPasswordInput).toBeRequired()
    })

    it('accepts password with exactly 8 characters', async () => {
        const user = userEvent.setup()
        mockSignUp.mockResolvedValue(undefined)

        render(<SignUpPageWrapper />)

        await user.type(screen.getByLabelText(/^email$/i), 'test@example.com')
        await user.type(screen.getByLabelText(/^password$/i), '12345678')
        await user.type(screen.getByLabelText(/confirm password/i), '12345678')

        const submitButton = screen.getByRole('button', { name: /sign up/i })
        await user.click(submitButton)

        await waitFor(() => {
            expect(mockSignUp).toHaveBeenCalled()
        })

        expect(screen.queryByText(/password must be at least/i)).not.toBeInTheDocument()
    })
})
