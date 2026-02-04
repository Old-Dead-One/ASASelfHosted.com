/**
 * Data Rights Request — legal page.
 *
 * Explains how to request access, correction, or deletion of personal data.
 * Includes self-service account deletion (permanent, irreversible).
 */

import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '@/contexts/AuthContext'
import { deleteMyAccount, APIErrorResponse } from '@/lib/api'
import { Button } from '@/components/ui/Button'

export function DataRightsPage() {
    const { isAuthenticated, signOut } = useAuth()
    const navigate = useNavigate()
    const [confirmPermanent, setConfirmPermanent] = useState(false)
    const [showSecondConfirm, setShowSecondConfirm] = useState(false)
    const [deleteLoading, setDeleteLoading] = useState(false)
    const [deleteError, setDeleteError] = useState<string | null>(null)

    const handleDeleteClick = () => {
        if (!confirmPermanent) return
        setDeleteError(null)
        setShowSecondConfirm(true)
    }

    const handleDeleteAccount = async () => {
        if (!confirmPermanent) return
        setDeleteError(null)
        setShowSecondConfirm(false)
        setDeleteLoading(true)
        try {
            await deleteMyAccount()
            await signOut()
            navigate('/', { replace: true })
        } catch (err) {
            setDeleteLoading(false)
            const message = err instanceof APIErrorResponse ? err.message : 'Account deletion failed. Please try again or contact support.'
            setDeleteError(message)
        }
    }

    return (
        <div className="py-8 px-4 max-w-3xl mx-auto">
            <h1 className="text-3xl font-bold text-foreground mb-2">
                Data Rights Request
            </h1>
            <p className="text-sm text-muted-foreground mb-6">
                ASA Self-Hosted respects your right to access and control your personal data.
            </p>

            <section className="space-y-4 mb-8">
                <p className="text-muted-foreground">
                    Depending on your location, you may request:
                </p>
                <ul className="list-disc pl-6 space-y-1 text-muted-foreground">
                    <li>Access to personal data we hold about you</li>
                    <li>Correction of inaccurate data</li>
                    <li>Deletion of personal data</li>
                    <li>Withdrawal of consent</li>
                </ul>
                <p className="text-muted-foreground">
                    If data was never collected, there may be nothing to retrieve or delete.
                </p>
            </section>

            <section className="space-y-4 mb-8">
                <h2 className="text-xl font-semibold text-foreground">
                    How to Submit a Request
                </h2>
                <p className="text-muted-foreground">
                    For access or correction, submit requests via the <Link to="/contact" className="text-primary hover:text-accent transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-ring rounded px-0.5">Contact</Link> page. Account deletion can be done below (when signed in) or by contacting us.
                </p>
                <p className="text-sm text-muted-foreground">
                    Our retention periods, purge mechanics, backup posture, and account deletion are documented in our Data Lifecycle policy; see the Privacy Policy for a summary.
                </p>
            </section>

            <section className="space-y-4 mb-8">
                <h2 className="text-xl font-semibold text-foreground">
                    Delete my account
                </h2>
                <p className="text-muted-foreground">
                    You may permanently delete your account and all associated data (profile, servers, clusters, favorites, and related records). This action <strong>cannot be reversed</strong>. Your data will be removed and you will be signed out.
                </p>
                {!isAuthenticated ? (
                    <p className="text-sm text-muted-foreground">
                        <Link to="/login" className="text-primary hover:text-accent underline focus:outline-none focus-visible:ring-2 focus-visible:ring-ring rounded">Sign in</Link> to delete your account, or <Link to="/contact" className="text-primary hover:text-accent underline focus:outline-none focus-visible:ring-2 focus-visible:ring-ring rounded">contact us</Link> to request deletion.
                    </p>
                ) : (
                    <div className="rounded-lg border border-input bg-background-elevated/60 p-4 space-y-4">
                        <p className="text-sm font-medium text-destructive">
                            This is permanent and cannot be reversed. All your account data will be deleted.
                        </p>
                        <label className="flex items-start gap-2 cursor-pointer">
                            <input
                                type="checkbox"
                                checked={confirmPermanent}
                                onChange={(e) => setConfirmPermanent(e.target.checked)}
                                className="mt-1 rounded border-input"
                                aria-describedby="delete-warning"
                            />
                            <span id="delete-warning" className="text-sm text-foreground">
                                I understand that my account and all associated data will be permanently deleted and cannot be recovered.
                            </span>
                        </label>
                        {deleteError && (
                            <p className="text-sm text-destructive" role="alert">
                                {deleteError}
                            </p>
                        )}
                        <Button
                            type="button"
                            variant="danger"
                            disabled={!confirmPermanent || deleteLoading}
                            onClick={handleDeleteClick}
                            aria-describedby="delete-warning"
                        >
                            {deleteLoading ? 'Deleting…' : 'Permanently delete my account'}
                        </Button>
                    </div>
                )}
            </section>

            {showSecondConfirm && isAuthenticated && (
                <div
                    className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50"
                    role="dialog"
                    aria-modal="true"
                    aria-labelledby="delete-account-confirm-title"
                >
                    <div className="rounded-xl border border-input bg-background-elevated p-6 shadow-lg shadow-black/40 max-w-md w-full">
                        <h2 id="delete-account-confirm-title" className="text-lg font-semibold text-foreground mb-2">
                            Delete your account?
                        </h2>
                        <p className="text-muted-foreground text-sm mb-4">
                            This is your last chance. Your account and all associated data will be permanently deleted and cannot be recovered. You will be signed out immediately.
                        </p>
                        <div className="flex gap-2 justify-end">
                            <Button
                                type="button"
                                variant="secondary"
                                onClick={() => setShowSecondConfirm(false)}
                                disabled={deleteLoading}
                            >
                                Cancel
                            </Button>
                            <Button
                                type="button"
                                variant="danger"
                                onClick={handleDeleteAccount}
                                disabled={deleteLoading}
                            >
                                {deleteLoading ? 'Deleting…' : 'Yes, delete my account'}
                            </Button>
                        </div>
                    </div>
                </div>
            )}

            <section className="space-y-4">
                <h2 className="text-xl font-semibold text-foreground">
                    What We Can and Cannot Do
                </h2>
                <p className="text-muted-foreground">
                    We can act only on data processed by ASA Self-Hosted.
                </p>
                <p className="text-muted-foreground">We cannot access or delete:</p>
                <ul className="list-disc pl-6 space-y-1 text-muted-foreground">
                    <li>Game server data</li>
                    <li>In-game data stored by server owners</li>
                    <li>Data controlled by third-party platforms</li>
                </ul>
            </section>
        </div>
    )
}
