/**
 * Terms of Service acceptance modal.
 *
 * Shown at account creation and when adding first server.
 * User must check the box to enable Continue; we record acceptance in the DB for legal audit.
 */

import { Link } from 'react-router-dom'

interface TermsAcceptanceModalProps {
    open: boolean
    agreed: boolean
    onAgreedChange: (value: boolean) => void
    onContinue: () => void
    onCancel?: () => void
    continueLabel?: string
    loading?: boolean
}

export function TermsAcceptanceModal({
    open,
    agreed,
    onAgreedChange,
    onContinue,
    onCancel,
    continueLabel = 'Continue',
    loading = false,
}: TermsAcceptanceModalProps) {
    if (!open) return null

    return (
        <div
            className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50"
            role="dialog"
            aria-modal="true"
            aria-labelledby="terms-modal-title"
        >
            <div className="bg-background border border-input rounded-xl shadow-xl max-w-lg w-full max-h-[90vh] overflow-y-auto p-6">
                <h2 id="terms-modal-title" className="text-xl font-semibold text-foreground mb-3">
                    Before continuing, please review and accept the Terms of Service.
                </h2>

                <p className="text-sm font-medium text-foreground mb-2">Key points:</p>
                <ul className="list-disc pl-6 space-y-1 text-sm text-muted-foreground mb-4">
                    <li>ASA Self-Hosted lists servers but does not run or control them.</li>
                    <li>Verification confirms server identity, not quality or safety.</li>
                    <li>Data is not collected by default.</li>
                    <li>Player data requires explicit, in-game consent.</li>
                    <li>If you did not grant permission in-game, we do not have your data.</li>
                </ul>

                <p className="text-sm text-muted-foreground mb-4">
                    You must agree to the Terms of Service to continue.
                </p>

                <label className="flex items-start gap-3 cursor-pointer mb-6">
                    <input
                        type="checkbox"
                        checked={agreed}
                        onChange={(e) => onAgreedChange(e.target.checked)}
                        className="mt-1 h-4 w-4 rounded border-input bg-background shadow-sm focus:ring-2 focus:ring-ring focus:ring-offset-2"
                        aria-describedby="terms-checkbox-desc"
                    />
                    <span id="terms-checkbox-desc" className="text-sm text-foreground">
                        I agree to the Terms of Service and understand how consent and data collection work.
                    </span>
                </label>

                <div className="flex flex-wrap gap-3">
                    <button
                        type="button"
                        onClick={onContinue}
                        disabled={!agreed || loading}
                        className="px-4 py-2 rounded-md bg-primary text-primary-foreground font-medium disabled:opacity-50 disabled:cursor-not-allowed hover:bg-primary/90 focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2"
                    >
                        {loading ? 'Saving…' : continueLabel}
                    </button>
                    {onCancel && (
                        <button
                            type="button"
                            onClick={onCancel}
                            disabled={loading}
                            className="px-4 py-2 rounded-md border border-input bg-muted/50 text-foreground font-medium hover:bg-muted focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2"
                        >
                            Cancel
                        </button>
                    )}
                </div>

                <p className="mt-4 text-xs text-muted-foreground">
                    Full text: <Link to="/terms" className="text-primary hover:text-accent underline" target="_blank" rel="noopener noreferrer">Terms of Service</Link>
                </p>
            </div>
        </div>
    )
}
