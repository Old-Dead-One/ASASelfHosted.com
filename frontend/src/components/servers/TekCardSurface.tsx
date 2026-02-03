/**
 * Shared tek-styled card surface for server cards.
 *
 * Single source of truth for the tek look: border, wall, seam, and content layer.
 * Used by ServerCard (directory, Spotlight) and DashboardServerCard so styling is not duplicated.
 */

import type { ReactNode } from 'react'

interface TekCardSurfaceProps {
    /** Card content; omit for skeleton/placeholder cards */
    children?: ReactNode
    /** Outer wrapper: layout/sizing (e.g. min-h-[260px], w-full) */
    className?: string
    /** Inner content area: padding and flex (e.g. p-6, p-3) */
    contentClassName?: string
}

const OUTER_BASE =
    'relative overflow-hidden rounded-lg tek-border transition-colors flex flex-col h-full min-w-0 hover:border-primary/40'

export function TekCardSurface({
    children = null,
    className = '',
    contentClassName = 'p-6',
}: TekCardSurfaceProps) {
    return (
        <div className={`${OUTER_BASE} ${className}`.trim()}>
            <div className="absolute inset-0 bg-tek-wall" aria-hidden />
            <div className="absolute inset-0 tek-seam opacity-70 pointer-events-none" aria-hidden />
            <div
                className={`relative flex flex-col flex-1 bg-background/65 backdrop-blur-[1px] ${contentClassName}`.trim()}
            >
                {children}
            </div>
        </div>
    )
}
