/**
 * Server card component.
 *
 * Displays server information in a card format.
 * Uses DirectoryServer type from directory_view.
 */

import { Link } from 'react-router-dom'
import { Badge } from '@/components/ui/Badge'
import { StatusBadge } from '@/components/ui/StatusBadge'
import type { DirectoryServer } from '@/types'

interface ServerCardProps {
    server: DirectoryServer
}

export function ServerCard({ server }: ServerCardProps) {
    const favoriteCount = server.favorite_count ?? 0
    const favoriteLabel = favoriteCount === 1 ? '1 favorite' : `${favoriteCount} favorites`

    return (
        <div className="card-tek p-6 hover:border-primary/40 transition-colors flex flex-col h-full">
            {/* Header */}
            <div className="flex items-start justify-between gap-4 mb-3">
                <div className="flex-1 min-w-0">
                    <h3 className="text-lg font-semibold text-foreground truncate">
                        {server.name}
                    </h3>
                    {server.cluster_name && (
                        <p className="text-sm text-muted-foreground mt-1">
                            Cluster: {server.cluster_name}
                        </p>
                    )}
                </div>
                <StatusBadge status={server.effective_status ?? 'unknown'} />
            </div>

            {/* Description */}
            {server.description && (
                <p className="text-sm text-muted-foreground mb-4 line-clamp-2">
                    {server.description}
                </p>
            )}

            {/* Server Info */}
            <div className="flex flex-wrap gap-2 mb-4">
                {server.map_name && (
                    <span className="text-xs text-muted-foreground font-mono">
                        {server.map_name}
                    </span>
                )}
                {server.game_mode && <Badge type={server.game_mode} />}
                {server.ruleset && <Badge type={server.ruleset} />}
            </div>

            {/* Badges */}
            <div className="flex flex-wrap gap-2 mb-4">
                {server.is_verified && <Badge type="verified" />}
                {server.is_new && <Badge type="new" />}
                {server.is_stable && <Badge type="stable" />}
            </div>

            {/* Spacer to push footer to bottom */}
            <div className="flex-1" />

            {/* Footer */}
            <div className="flex items-center justify-between pt-4 border-t border-input/60 mt-4">
                <div className="text-xs text-muted-foreground">{favoriteLabel}</div>
                <Link
                    to={`/servers/${server.id}`}
                    className="text-sm text-primary hover:text-accent font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-ring rounded px-1"
                    aria-label={`View details for ${server.name}`}
                >
                    View Details →
                </Link>
            </div>
        </div>
    )
}
