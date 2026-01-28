/**
 * Forgot password page.
 *
 * Allows users to request a password reset email.
 */

import { useState, FormEvent } from 'react'
import { Link } from 'react-router-dom'
import { supabase, isSupabaseConfigured } from '@/lib/supabase'
import { Button } from '@/components/ui/Button'

export function ForgotPasswordPage() {
    const [email, setEmail] = useState('')
    const [error, setError] = useState<string | null>(null)
    const [success, setSuccess] = useState(false)
    const [loading, setLoading] = useState(false)

    const handleSubmit = async (e: FormEvent) => {
        e.preventDefault()
        setError(null)
        setSuccess(false)
        setLoading(true)

        try {
            if (isSupabaseConfigured() && supabase) {
                const { error: resetError } = await supabase.auth.resetPasswordForEmail(
                    email,
                    {
                        redirectTo: `${window.location.origin}/reset-password`,
                    }
                )
                if (resetError) throw resetError
                setSuccess(true)
            } else {
                // Dev mode: just show success message
                setSuccess(true)
            }
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to send reset email')
        } finally {
            setLoading(false)
        }
    }

    if (success) {
        return (
            <div className="flex items-center justify-center min-h-[calc(100vh-200px)] py-12 px-4">
                <div className="w-full max-w-md">
                    <div className="card-elevated p-8 text-center">
                        <h1 className="text-2xl font-bold text-foreground mb-2">
                            Check your email
                        </h1>
                        <p className="text-sm text-muted-foreground mb-6">
                            We've sent a password reset link to <strong>{email}</strong>
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
                    <h1 className="text-2xl font-bold text-foreground mb-2">
                        Reset Password
                    </h1>
                    <p className="text-sm text-muted-foreground mb-6">
                        Enter your email address and we'll send you a link to reset your
                        password.
                    </p>

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

                        <Button
                            type="submit"
                            variant="primary"
                            className="w-full min-h-[44px]"
                            disabled={loading}
                        >
                            {loading ? 'Sending...' : 'Send Reset Link'}
                        </Button>
                    </form>

                    <div className="mt-6 text-center text-sm text-muted-foreground">
                        Remember your password?{' '}
                        <Link to="/login" className="text-primary hover:text-accent">
                            Sign in
                        </Link>
                    </div>
                </div>
            </div>
        </div>
    )
}
