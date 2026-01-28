/**
 * Tests for LoginPage component.
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { BrowserRouter } from 'react-router-dom'
import { LoginPage } from './LoginPage'

// Mock the useAuth hook
vi.mock('@/contexts/AuthContext', () => ({
    useAuth: vi.fn(),
}))

// Mock useNavigate and useLocation
vi.mock('react-router-dom', async () => {
    const actual = await vi.importActual('react-router-dom')
    return {
        ...actual,
        useNavigate: () => vi.fn(),
        useLocation: () => ({ state: null }),
    }
})

import { useAuth } from '@/contexts/AuthContext'

const mockSignIn = vi.fn()
const mockUseAuth = vi.mocked(useAuth)

// Wrapper with Router
function LoginPageWrapper() {
    return (
        <BrowserRouter>
            <LoginPage />
        </BrowserRouter>
    )
}

describe('LoginPage', () => {
    beforeEach(() => {
        vi.clearAllMocks()
        mockUseAuth.mockReturnValue({
            isAuthenticated: false,
            user: null,
            signIn: mockSignIn,
            signUp: vi.fn(),
            signOut: vi.fn(),
            loading: false,
            userId: null,
        })
    })

    it('renders login form', () => {
        render(<LoginPageWrapper />)

        expect(screen.getByRole('heading', { name: 'Sign In' })).toBeInTheDocument()
        expect(screen.getByLabelText(/^email$/i)).toBeInTheDocument()
        expect(screen.getByLabelText(/^password$/i)).toBeInTheDocument()
        expect(screen.getByRole('button', { name: /^sign in$/i })).toBeInTheDocument()
    })

    it('renders forgot password link', () => {
        render(<LoginPageWrapper />)

        const forgotLink = screen.getByRole('link', { name: /forgot password/i })
        expect(forgotLink).toBeInTheDocument()
        expect(forgotLink).toHaveAttribute('href', '/forgot-password')
    })

    it('renders sign up link', () => {
        render(<LoginPageWrapper />)

        const signUpLink = screen.getByRole('link', { name: /sign up/i })
        expect(signUpLink).toBeInTheDocument()
        expect(signUpLink).toHaveAttribute('href', '/signup')
    })

    it('updates email input', async () => {
        const user = userEvent.setup()
        render(<LoginPageWrapper />)

        const emailInput = screen.getByLabelText(/^email$/i)
        await user.type(emailInput, 'test@example.com')

        expect(emailInput).toHaveValue('test@example.com')
    })

    it('updates password input', async () => {
        const user = userEvent.setup()
        render(<LoginPageWrapper />)

        const passwordInput = screen.getByLabelText(/^password$/i)
        await user.type(passwordInput, 'password123')

        expect(passwordInput).toHaveValue('password123')
    })

    it('calls signIn on form submit', async () => {
        const user = userEvent.setup()
        mockSignIn.mockResolvedValue(undefined)

        render(<LoginPageWrapper />)

        await user.type(screen.getByLabelText(/^email$/i), 'test@example.com')
        await user.type(screen.getByLabelText(/^password$/i), 'password123')

        const submitButton = screen.getByRole('button', { name: /sign in/i })
        await user.click(submitButton)

        await waitFor(() => {
            expect(mockSignIn).toHaveBeenCalledWith('test@example.com', 'password123')
        })
    })

    it('shows loading state during submission', async () => {
        const user = userEvent.setup()
        let resolveSignIn: () => void
        const signInPromise = new Promise<void>((resolve) => {
            resolveSignIn = resolve
        })
        mockSignIn.mockReturnValue(signInPromise)

        render(<LoginPageWrapper />)

        await user.type(screen.getByLabelText(/^email$/i), 'test@example.com')
        await user.type(screen.getByLabelText(/^password$/i), 'password123')

        const submitButton = screen.getByRole('button', { name: /^sign in$/i })
        await user.click(submitButton)

        // Button text changes to "Signing in..." when loading
        await waitFor(() => {
            const loadingButton = screen.getByText('Signing in...')
            expect(loadingButton).toBeInTheDocument()
            expect(loadingButton).toBeDisabled()
        })

        resolveSignIn!()
        await waitFor(() => {
            expect(screen.getByText('Sign In')).toBeInTheDocument()
        })
    })

    it('displays error message on sign in failure', async () => {
        const user = userEvent.setup()
        const error = new Error('Invalid credentials')
        mockSignIn.mockRejectedValue(error)

        render(<LoginPageWrapper />)

        await user.type(screen.getByLabelText(/^email$/i), 'test@example.com')
        await user.type(screen.getByLabelText(/^password$/i), 'wrongpassword')

        const submitButton = screen.getByRole('button', { name: /sign in/i })
        await user.click(submitButton)

        await waitFor(() => {
            expect(screen.getByText('Invalid credentials')).toBeInTheDocument()
        })
    })

    it('displays generic error message for non-Error failures', async () => {
        const user = userEvent.setup()
        mockSignIn.mockRejectedValue('Unknown error')

        render(<LoginPageWrapper />)

        await user.type(screen.getByLabelText(/^email$/i), 'test@example.com')
        await user.type(screen.getByLabelText(/^password$/i), 'password123')

        const submitButton = screen.getByRole('button', { name: /sign in/i })
        await user.click(submitButton)

        await waitFor(() => {
            expect(screen.getByText('Failed to sign in')).toBeInTheDocument()
        })
    })

    it('clears error message on new submission', async () => {
        const user = userEvent.setup()
        mockSignIn
            .mockRejectedValueOnce(new Error('First error'))
            .mockResolvedValueOnce(undefined)

        render(<LoginPageWrapper />)

        const emailInput = screen.getByLabelText(/^email$/i)
        const passwordInput = screen.getByLabelText(/^password$/i)

        // First submission - fails
        await user.type(emailInput, 'test@example.com')
        await user.type(passwordInput, 'wrong')
        await user.click(screen.getByRole('button', { name: /sign in/i }))

        await waitFor(() => {
            expect(screen.getByText('First error')).toBeInTheDocument()
        })

        // Second submission - succeeds (error should clear)
        await user.clear(emailInput)
        await user.clear(passwordInput)
        await user.type(emailInput, 'test@example.com')
        await user.type(passwordInput, 'correct')
        await user.click(screen.getByRole('button', { name: /sign in/i }))

        await waitFor(() => {
            expect(screen.queryByText('First error')).not.toBeInTheDocument()
        })
    })

    it('requires email and password fields', () => {
        render(<LoginPageWrapper />)

        const emailInput = screen.getByLabelText(/^email$/i)
        const passwordInput = screen.getByLabelText(/^password$/i)

        expect(emailInput).toBeRequired()
        expect(passwordInput).toBeRequired()
    })
})
