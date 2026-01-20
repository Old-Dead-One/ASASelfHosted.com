/**
 * Status badge component.
 *
 * Displays server status (online/offline/unknown) with appropriate styling.
 */

import { cn } from '@/lib/utils'
import type { ServerStatus } from '@/types'

interface StatusBadgeProps {
    status: ServerStatus
    className?: string
}

export function StatusBadge({ status, className }: StatusBadgeProps) {
    const variants = {
        online: 'bg-success text-success-foreground',
        offline: 'bg-destructive text-destructive-foreground',
        unknown: 'bg-muted text-muted-foreground',
    }

    const labels = {
        online: 'Online',
        offline: 'Offline',
        unknown: 'Unknown',
    }

    return (
        <span
            className={cn(
                'inline-flex items-center px-2 py-1 rounded text-xs font-medium',
                variants[status],
                className
            )}
        >
            <span
                className={cn(
                    'w-1.5 h-1.5 rounded-full mr-1.5',
                    status === 'online' && 'bg-success-foreground',
                    status === 'offline' && 'bg-destructive-foreground',
                    status === 'unknown' && 'bg-muted-foreground'
                )}
            />
            {labels[status]}
        </span>
    )
}
