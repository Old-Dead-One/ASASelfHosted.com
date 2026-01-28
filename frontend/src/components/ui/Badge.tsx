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

// Shared variant styles to reduce duplication
const accentOutline = 'bg-accent/20 text-primary border border-primary'
const dangerOutline = 'bg-destructive/20 text-destructive border border-destructive'
const successOutline = 'bg-success/20 text-success border border-success'

const badgeConfig: Record<BadgeType, { label: string; variant: string }> = {
    verified: { label: 'Verified', variant: 'bg-primary text-primary-foreground border border-primary-foreground' },
    new: { label: 'New', variant: 'bg-accent text-accent-foreground border border-accent-foreground' },
    stable: { label: 'Stable', variant: 'bg-success text-success-foreground border border-success-foreground' },

    pvp: { label: 'PvP', variant: dangerOutline },
    pve: { label: 'PvE', variant: successOutline },
    pvpve: { label: 'PvPvE', variant: accentOutline },

    vanilla: { label: 'Vanilla', variant: 'bg-muted text-muted-foreground border border-muted-foreground' },
    vanilla_qol: { label: 'Vanilla QoL', variant: 'bg-muted text-muted-foreground border border-muted-foreground' },
    boosted: { label: 'Boosted', variant: accentOutline },
    modded: { label: 'Modded', variant: accentOutline },

    newbie_friendly: { label: 'Newbie Friendly', variant: accentOutline },
    learning_friendly: { label: 'Learning Friendly', variant: accentOutline },
}

export function Badge({ type, className }: BadgeProps) {
    // Safe fallback for unknown badge types (backend might add new types before frontend updates)
    const config =
        badgeConfig[type] ?? { label: type, variant: 'bg-muted text-muted-foreground' }

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
