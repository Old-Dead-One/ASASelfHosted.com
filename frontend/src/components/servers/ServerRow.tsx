/**
 * Server row component.
 *
 * Displays server information in a compact row format.
 * Uses DirectoryServer type from directory_view.
 */

import { Link } from 'react-router-dom'
import { Badge } from '@/components/ui/Badge'
import { StatusBadge } from '@/components/ui/StatusBadge'
import type { DirectoryServer } from '@/types'

interface ServerRowProps {
    server: DirectoryServer
}

export function ServerRow({ server }: ServerRowProps) {
    const favoriteCount = server.favorite_count ?? 0
    const favoriteLabel = favoriteCount === 1 ? '1' : `${favoriteCount}`

    return (
        <div className="rounded-md border border-input bg-background-elevated shadow-sm py-2 px-3 hover:border-primary/30 transition-colors">
            <div className="flex items-center gap-3">
                {/* Status */}
                <div className="shrink-0">
                    <StatusBadge status={server.effective_status ?? 'unknown'} />
                </div>

                {/* Main Content - single tight line */}
                <div className="flex-1 min-w-0 flex items-center gap-2 flex-wrap">
                    <h3 className="text-sm font-semibold text-foreground truncate">
                        {server.name}
                    </h3>
                    {server.is_verified && <Badge type="verified" />}
                    {server.is_new && <Badge type="new" />}
                    {server.is_stable && <Badge type="stable" />}
                    {server.map_name && (
                        <span className="font-mono text-xs text-muted-foreground">{server.map_name}</span>
                    )}
                    {server.game_mode && <Badge type={server.game_mode} />}
                    {server.ruleset && <Badge type={server.ruleset} />}
                    {server.cluster_name && (
                        <span className="text-xs text-muted-foreground">· {server.cluster_name}</span>
                    )}
                    {server.description && (
                        <span className="text-xs text-muted-foreground truncate max-w-[280px] hidden sm:inline">
                            · {server.description}
                        </span>
                    )}
                </div>

                {/* Right Side Info */}
                <div className="shrink-0 flex items-center gap-3 text-xs">
                    {server.players_current !== null && server.players_capacity !== null && (
                        <span className="text-foreground font-medium tabular-nums">
                            {server.players_current}/{server.players_capacity}
                        </span>
                    )}
                    <span className="text-muted-foreground">{favoriteLabel} fav</span>
                    <Link
                        to={`/servers/${server.id}`}
                        className="text-primary hover:text-accent font-medium transition-colors whitespace-nowrap focus:outline-none focus:ring-2 focus:ring-ring rounded px-1"
                        aria-label={`View details for ${server.name}`}
                    >
                        View →
                    </Link>
                </div>
            </div>
        </div>
    )
}
