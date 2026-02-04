/**
 * Dashboard server row component.
 *
 * Compact row for "Your Servers" row view. Same visual style as ServerRow
 * but with owner actions (View, Edit, Clone).
 */

import { Link } from 'react-router-dom'
import { StatusBadge } from '@/components/ui/StatusBadge'
import { Button } from '@/components/ui/Button'
import type { DirectoryServer, ServerStatus } from '@/types'

type DashboardServer = Pick<
    DirectoryServer,
    | 'id'
    | 'name'
    | 'description'
    | 'effective_status'
    | 'map_name'
    | 'game_mode'
    | 'ruleset'
    | 'rulesets'
    | 'cluster_id'
    | 'join_address'
    | 'join_password'
    | 'join_instructions_pc'
    | 'join_instructions_console'
    | 'discord_url'
    | 'website_url'
    | 'mod_list'
    | 'rates'
    | 'wipe_info'
    | 'is_pc'
    | 'is_console'
    | 'is_crossplay'
>

interface DashboardServerRowProps {
    server: DashboardServer
    onEdit: (server: DashboardServer) => void
    onClone: (server: DashboardServer) => void
}

export function DashboardServerRow({ server, onEdit, onClone }: DashboardServerRowProps) {
    const status = (server.effective_status ?? 'unknown') as ServerStatus

    return (
        <div className="rounded-md border border-input bg-background-elevated shadow-sm py-2 px-3 hover:border-primary/30 transition-colors">
            <div className="flex items-center gap-3 flex-nowrap">
                <div className="shrink-0">
                    <StatusBadge status={status} />
                </div>
                <div className="flex-1 min-w-0 flex items-center gap-2">
                    <h3 className="text-sm font-semibold text-foreground truncate">
                        {server.name}
                    </h3>
                    {server.map_name && (
                        <span className="font-mono text-xs text-muted-foreground">{server.map_name}</span>
                    )}
                    {server.game_mode && (
                        <span className="text-xs px-2 py-0.5 rounded bg-muted text-muted-foreground">
                            {server.game_mode}
                        </span>
                    )}
                    {server.ruleset && (
                        <span className="text-xs px-2 py-0.5 rounded bg-muted text-muted-foreground">
                            {server.ruleset}
                        </span>
                    )}
                    {server.description && (
                        <span className="text-xs text-muted-foreground truncate max-w-[240px] hidden sm:inline">
                            · {server.description}
                        </span>
                    )}
                </div>
                <div className="shrink-0 flex items-center gap-1 text-xs">
                    <Link
                        to={`/servers/${server.id}`}
                        className="text-primary hover:text-accent font-medium whitespace-nowrap focus:outline-none focus:ring-2 focus:ring-ring rounded px-1"
                        aria-label={`View ${server.name}`}
                    >
                        View
                    </Link>
                    <Button
                        type="button"
                        variant="ghost"
                        size="sm"
                        className="h-7 px-2 text-xs"
                        onClick={() => onEdit(server)}
                    >
                        Edit
                    </Button>
                    <Button
                        type="button"
                        variant="ghost"
                        size="sm"
                        className="h-7 px-2 text-xs"
                        onClick={() => onClone(server)}
                    >
                        Clone
                    </Button>
                </div>
            </div>
        </div>
    )
}
