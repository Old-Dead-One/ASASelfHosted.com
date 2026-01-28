/**
 * Login page.
 *
 * Handles user authentication (Supabase Auth or dev bypass).
 */

import { useState, FormEvent } from 'react'
import { useNavigate, useLocation, Link } from 'react-router-dom'
import { useAuth } from '@/contexts/AuthContext'
import { Button } from '@/components/ui/Button'

export function LoginPage() {
    const [email, setEmail] = useState('')
    const [password, setPassword] = useState('')
    const [error, setError] = useState<string | null>(null)
    const [loading, setLoading] = useState(false)
    const { signIn } = useAuth()
    const navigate = useNavigate()
    const location = useLocation()

    const from = (location.state as { from?: Location })?.from?.pathname || '/'

    const handleSubmit = async (e: FormEvent) => {
        e.preventDefault()
        setError(null)
        setLoading(true)

        try {
            await signIn(email, password)
            // Small delay to ensure session cache is set and ready for API calls
            await new Promise(resolve => setTimeout(resolve, 50))
            navigate(from, { replace: true })
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to sign in')
        } finally {
            setLoading(false)
        }
    }

    return (
        <div className="flex items-center justify-center min-h-[calc(100vh-200px)] py-12 px-4">
            <div className="w-full max-w-md">
                <div className="card-elevated p-8">
                    <h1 className="text-2xl font-bold text-foreground mb-2">Sign In</h1>
                    <p className="text-sm text-muted-foreground mb-6">
                        Sign in to manage your servers
                    </p>

                    {error && <div className="mb-4 form-error">{error}</div>}

                    {/* TODO: Sprint 7 - Steam OAuth Integration
                     * Add Steam login button here:
                     * - Use Supabase Auth OAuth provider for Steam
                     * - Handle OAuth callback and session creation
                     * - Store Steam user ID in user_metadata
                     * See: https://supabase.com/docs/guides/auth/social-login/auth-steam
                     */}
                    {/* <div className="mb-4">
                        <button
                            type="button"
                            onClick={handleSteamLogin}
                            className="w-full py-2 px-4 bg-[#1b2838] text-white rounded-md hover:bg-[#1b2838]/90 transition-colors flex items-center justify-center gap-2"
                        >
                            <svg className="w-5 h-5" viewBox="0 0 24 24" fill="currentColor">
                                <path d="M12 0C5.373 0 0 5.373 0 12s5.373 12 12 12 12-5.373 12-12S18.627 0 12 0zm5.568 8.16l-1.414 1.414-2.12-2.12-1.415 1.415 2.121 2.121-2.121 2.121-1.415-1.415-2.12 2.12-1.415-1.414 2.121-2.121L8.16 9.568l1.415-1.415 2.12 2.12 1.414-1.414-2.12-2.12L12 4.697l2.121 2.121 2.121-2.121L16.95 6.04l-2.12 2.12z"/>
                            </svg>
                            Sign in with Steam
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

                    <form onSubmit={handleSubmit} className="space-y-4">
                        <div>
                            <label htmlFor="email" className="label-tek">
                                Email
                            </label>
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
                            <div className="flex items-center justify-between mb-0.5">
                                <label htmlFor="password" className="label-tek mb-0">
                                    Password
                                </label>
                                <Link
                                    to="/forgot-password"
                                    className="text-xs text-primary hover:text-accent"
                                >
                                    Forgot password?
                                </Link>
                            </div>
                            <input
                                id="password"
                                type="password"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                required
                                autoComplete="current-password"
                                className="input-tek min-h-[44px]"
                                placeholder="••••••••"
                            />
                        </div>

                        <Button
                            type="submit"
                            variant="primary"
                            className="w-full min-h-[44px]"
                            disabled={loading}
                            aria-label="Sign in"
                        >
                            {loading ? 'Signing in...' : 'Sign In'}
                        </Button>
                    </form>

                    <div className="mt-6 text-center text-sm text-muted-foreground">
                        Don't have an account?{' '}
                        <Link to="/signup" className="text-primary hover:text-accent">
                            Sign up
                        </Link>
                    </div>
                </div>
            </div>
        </div>
    )
}
