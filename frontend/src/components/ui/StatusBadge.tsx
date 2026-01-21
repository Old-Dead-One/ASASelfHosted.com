/**
 * Status badge component.
 *
 * Displays server status (online/offline/unknown) with appropriate styling.
 * Tolerant of null/bad data - defaults to 'unknown'.
 */

import { cn } from '@/lib/utils'
import type { ServerStatus } from '@/types'

interface StatusBadgeProps {
    status?: ServerStatus | null
    className?: string
    // Future: tone override for confidence levels (e.g., yellow for degraded online)
    // tone?: 'neutral' | 'warning'
}

export function StatusBadge({ status, className }: StatusBadgeProps) {
    const safeStatus: ServerStatus = status ?? 'unknown'

    const variants: Record<ServerStatus, string> = {
        online: 'bg-success text-success-foreground',
        offline: 'bg-destructive text-destructive-foreground',
        unknown: 'bg-muted text-muted-foreground',
    }

    const labels: Record<ServerStatus, string> = {
        online: 'Online',
        offline: 'Offline',
        unknown: 'Unknown',
    }

    return (
        <span
            className={cn(
                'inline-flex items-center gap-1.5 px-2 py-1 rounded text-xs font-medium',
                variants[safeStatus],
                className
            )}
        >
            <span
                className={cn(
                    'w-1.5 h-1.5 rounded-full',
                    safeStatus === 'online' && 'bg-success-foreground',
                    safeStatus === 'offline' && 'bg-destructive-foreground',
                    safeStatus === 'unknown' && 'bg-muted-foreground'
                )}
            />
            {labels[safeStatus]}
        </span>
    )
}
