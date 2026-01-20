/**
 * Badge component.
 *
 * Displays computed badges (verified, new, stable, pvp/pve, vanilla/boosted).
 * Badges are computed, never purchased.
 */

import { cn } from '@/lib/utils'
import type { BadgeType } from '@/types'

interface BadgeProps {
    type: BadgeType
    className?: string
}

const badgeConfig: Record<BadgeType, { label: string; variant: string }> = {
    verified: {
        label: 'Verified',
        variant: 'bg-primary text-primary-foreground',
    },
    new: {
        label: 'New',
        variant: 'bg-accent text-accent-foreground',
    },
    stable: {
        label: 'Stable',
        variant: 'bg-success text-success-foreground',
    },
    pvp: {
        label: 'PvP',
        variant: 'bg-destructive/20 text-destructive border border-destructive/30',
    },
    pve: {
        label: 'PvE',
        variant: 'bg-success/20 text-success border border-success/30',
    },
    vanilla: {
        label: 'Vanilla',
        variant: 'bg-muted text-muted-foreground',
    },
    boosted: {
        label: 'Boosted',
        variant: 'bg-warning/20 text-warning border border-warning/30',
    },
    newbie_friendly: {
        label: 'Newbie Friendly',
        variant: 'bg-accent/20 text-accent-foreground border border-accent/30',
    },
    learning_friendly: {
        label: 'Learning Friendly',
        variant: 'bg-accent/20 text-accent-foreground border border-accent/30',
    },
}

export function Badge({ type, className }: BadgeProps) {
    const config = badgeConfig[type]

    return (
        <span
            className={cn(
                'inline-flex items-center px-2 py-0.5 rounded text-xs font-medium',
                config.variant,
                className
            )}
        >
            {config.label}
        </span>
    )
}
