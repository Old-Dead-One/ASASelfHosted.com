/**
 * Reset password page.
 *
 * Handles password reset from email link (Supabase Auth callback).
 */

import { useState, FormEvent, useEffect } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { supabase, isSupabaseConfigured } from '@/lib/supabase'
import { Button } from '@/components/ui/Button'

export function ResetPasswordPage() {
    const [password, setPassword] = useState('')
    const [confirmPassword, setConfirmPassword] = useState('')
    const [error, setError] = useState<string | null>(null)
    const [loading, setLoading] = useState(false)
    const navigate = useNavigate()

    // Check for password reset token in URL
    useEffect(() => {
        if (isSupabaseConfigured() && supabase) {
            // Supabase handles the token via URL hash
            // This page is reached after user clicks email link
            const hashParams = new URLSearchParams(window.location.hash.substring(1))
            const accessToken = hashParams.get('access_token')
            const type = hashParams.get('type')

            if (type === 'recovery' && accessToken) {
                // Token is valid, user can reset password
                // Supabase session will be set automatically
            } else {
                // No valid token, redirect to forgot password
                navigate('/forgot-password')
            }
        }
    }, [navigate])

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
            if (isSupabaseConfigured() && supabase) {
                const { error: updateError } = await supabase.auth.updateUser({
                    password: password,
                })
                if (updateError) throw updateError
                // Password updated successfully, redirect to login
                navigate('/login', { replace: true })
            } else {
                // Dev mode: just redirect
                navigate('/login', { replace: true })
            }
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to reset password')
        } finally {
            setLoading(false)
        }
    }

    return (
        <div className="flex items-center justify-center min-h-[calc(100vh-200px)] py-12 px-4">
            <div className="w-full max-w-md">
                <div className="card-elevated p-8">
                    <h1 className="text-2xl font-bold text-foreground mb-2">
                        Reset Password
                    </h1>
                    <p className="text-sm text-muted-foreground mb-6">
                        Enter your new password below.
                    </p>

                    {error && <div className="mb-4 form-error">{error}</div>}

                    <form onSubmit={handleSubmit} className="space-y-4">
                        <div>
                            <label htmlFor="password" className="label-tek">New Password</label>
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
                            <label htmlFor="confirmPassword" className="label-tek">Confirm New Password</label>
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
                        >
                            {loading ? 'Resetting...' : 'Reset Password'}
                        </Button>
                    </form>

                    <div className="mt-6 text-center text-sm text-muted-foreground">
                        <Link to="/login" className="text-primary hover:text-accent">
                            Back to sign in
                        </Link>
                    </div>
                </div>
            </div>
        </div>
    )
}
