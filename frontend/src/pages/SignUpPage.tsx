/**
 * Sign up page.
 *
 * Handles user registration (Supabase Auth or dev bypass).
 */

import { useState, FormEvent } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '@/contexts/AuthContext'
import { Button } from '@/components/ui/Button'

export function SignUpPage() {
    const [email, setEmail] = useState('')
    const [password, setPassword] = useState('')
    const [confirmPassword, setConfirmPassword] = useState('')
    const [error, setError] = useState<string | null>(null)
    const [loading, setLoading] = useState(false)
    const [showConfirmation, setShowConfirmation] = useState(false)
    const { signUp } = useAuth()

    const handleSubmit = async (e: FormEvent) => {
        e.preventDefault()
        setError(null)

        if (password !== confirmPassword) {
            setError('Passwords do not match')
            return
        }

        if (password.length < 8) {
            setError('Password must be at least 8 characters')
            return
        }

        setLoading(true)

        try {
            await signUp(email, password)
            // Check if email confirmation is required
            // Supabase may require email confirmation depending on project settings
            // If confirmation is required, show confirmation message instead of redirecting
            setShowConfirmation(true)
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to sign up')
        } finally {
            setLoading(false)
        }
    }

    if (showConfirmation) {
        return (
            <div className="flex items-center justify-center min-h-[calc(100vh-200px)] py-12 px-4">
                <div className="w-full max-w-md">
                    <div className="card-elevated p-8 text-center">
                        <h1 className="text-2xl font-bold text-foreground mb-2">
                            Check your email
                        </h1>
                        <p className="text-sm text-muted-foreground mb-4">
                            We've sent a confirmation link to <strong>{email}</strong>.
                            Please click the link to verify your account.
                        </p>
                        <p className="text-sm text-muted-foreground mb-6">
                            Once you click the confirmation link in your email, you'll be able to sign in and start listing your servers.
                        </p>
                        <Link
                            to="/login"
                            className="text-sm text-primary hover:text-accent"
                        >
                            Back to sign in
                        </Link>
                    </div>
                </div>
            </div>
        )
    }

    return (
        <div className="flex items-center justify-center min-h-[calc(100vh-200px)] py-12 px-4">
            <div className="w-full max-w-md">
                <div className="card-elevated p-8">
                    <h1 className="text-2xl font-bold text-foreground mb-2">Sign Up</h1>
                    <p className="text-sm text-muted-foreground mb-6">
                        Create an account to list your servers
                    </p>

                    {/* TODO: Sprint 7 - Steam OAuth Integration
                     * Add Steam sign up button here:
                     * - Use Supabase Auth OAuth provider for Steam
                     * - Handle OAuth callback and user creation
                     * - Store Steam user ID in user_metadata
                     * See: https://supabase.com/docs/guides/auth/social-login/auth-steam
                     */}
                    {/* <div className="mb-4">
                        <button
                            type="button"
                            onClick={handleSteamSignUp}
                            className="w-full py-2 px-4 bg-[#1b2838] text-white rounded-md hover:bg-[#1b2838]/90 transition-colors flex items-center justify-center gap-2"
                        >
                            <svg className="w-5 h-5" viewBox="0 0 24 24" fill="currentColor">
                                <path d="M12 0C5.373 0 0 5.373 0 12s5.373 12 12 12 12-5.373 12-12S18.627 0 12 0zm5.568 8.16l-1.414 1.414-2.12-2.12-1.415 1.415 2.121 2.121-2.121 2.121-1.415-1.415-2.12 2.12-1.415-1.414 2.121-2.121L8.16 9.568l1.415-1.415 2.12 2.12 1.414-1.414-2.12-2.12L12 4.697l2.121 2.121 2.121-2.121L16.95 6.04l-2.12 2.12z"/>
                            </svg>
                            Sign up with Steam
                        </button>
                    </div>

                    <div className="relative mb-4">
                        <div className="absolute inset-0 flex items-center">
                            <div className="w-full border-t border-border"></div>
                        </div>
                        <div className="relative flex justify-center text-xs uppercase">
                            <span className="bg-card px-2 text-muted-foreground">Or</span>
                        </div>
                    </div> */}

                    {error && <div className="mb-4 form-error">{error}</div>}

                    <form onSubmit={handleSubmit} className="space-y-4">
                        <div>
                            <label htmlFor="email" className="label-tek">Email</label>
                            <input
                                id="email"
                                type="email"
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                                required
                                autoComplete="email"
                                className="input-tek min-h-[44px]"
                                placeholder="you@example.com"
                            />
                        </div>

                        <div>
                            <label htmlFor="password" className="label-tek">Password</label>
                            <input
                                id="password"
                                type="password"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                required
                                minLength={8}
                                autoComplete="new-password"
                                className="input-tek min-h-[44px]"
                                placeholder="••••••••"
                            />
                            <p className="mt-1 text-xs text-muted-foreground">
                                Must be at least 8 characters
                            </p>
                        </div>

                        <div>
                            <label htmlFor="confirmPassword" className="label-tek">Confirm Password</label>
                            <input
                                id="confirmPassword"
                                type="password"
                                value={confirmPassword}
                                onChange={(e) => setConfirmPassword(e.target.value)}
                                required
                                autoComplete="new-password"
                                className="input-tek min-h-[44px]"
                                placeholder="••••••••"
                            />
                        </div>

                        <Button
                            type="submit"
                            variant="primary"
                            className="w-full min-h-[44px]"
                            disabled={loading}
                            aria-label="Sign up"
                        >
                            {loading ? 'Creating account...' : 'Sign Up'}
                        </Button>
                    </form>

                    <div className="mt-6 text-center text-sm text-muted-foreground">
                        Already have an account?{' '}
                        <Link to="/login" className="text-primary hover:text-accent">
                            Sign in
                        </Link>
                    </div>
                </div>
            </div>
        </div>
    )
}
