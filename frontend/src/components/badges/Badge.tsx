/**
 * Badge component.
 *
 * Displays computed badges (verified, active, newbie_friendly, etc.).
 * Badges are computed, never purchased.
 */

import type { BadgeType } from '@/types'

interface BadgeProps {
    type: BadgeType
}

export function Badge({ type }: BadgeProps) {
    // TODO: Implement badge UI
    return <span>{type}</span>
}
