/**
 * Server card component.
 *
 * Displays server information in a card format.
 * Uses DirectoryServer type from directory_view.
 */

import { Badge } from '@/components/ui/Badge'
import { StatusBadge } from '@/components/ui/StatusBadge'
import type { DirectoryServer } from '@/types'

interface ServerCardProps {
    server: DirectoryServer
}

export function ServerCard({ server }: ServerCardProps) {
    return (
        <div className="bg-card border border-border rounded-lg p-6 hover:border-primary/50 transition-colors">
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
                <StatusBadge status={server.effective_status} />
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
                {server.pvp_enabled ? (
                    <Badge type="pvp" />
                ) : (
                    <Badge type="pve" />
                )}
                {server.vanilla ? (
                    <Badge type="vanilla" />
                ) : (
                    <Badge type="boosted" />
                )}
            </div>

            {/* Badges */}
            <div className="flex flex-wrap gap-2 mb-4">
                {server.is_verified && <Badge type="verified" />}
                {server.is_new && <Badge type="new" />}
                {server.is_stable && <Badge type="stable" />}
            </div>

            {/* Footer */}
            <div className="flex items-center justify-between pt-4 border-t border-gridline">
                <div className="text-xs text-muted-foreground">
                    {server.favorite_count} {server.favorite_count === 1 ? 'favorite' : 'favorites'}
                </div>
                <button className="text-sm text-primary hover:text-accent font-medium transition-colors">
                    View Details →
                </button>
            </div>
        </div>
    )
}
