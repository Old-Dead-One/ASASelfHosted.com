/**
 * Verification badge component.
 *
 * Displays verification status badge for servers.
 */

interface VerificationBadgeProps {
    status: 'unverified' | 'pending' | 'verified' | 'revoked' | 'expired'
}

export function VerificationBadge({ status }: VerificationBadgeProps) {
    // TODO: Implement verification badge UI
    return <span>{status}</span>
}
