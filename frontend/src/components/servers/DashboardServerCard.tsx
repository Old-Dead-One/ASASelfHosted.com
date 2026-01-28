/**
 * Server card for owner dashboard.
 *
 * Shows name, description, status, and actions (View, Edit, Delete).
 * Uses style-guide card-tek surface and Button for actions.
 */

import { Link } from 'react-router-dom'
import { StatusBadge } from '@/components/ui/StatusBadge'
import { Button } from '@/components/ui/Button'
import type { DirectoryServer, ServerStatus } from '@/types'

interface DashboardServerCardProps {
    server: Pick<
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
        | 'mod_list'
        | 'rates'
        | 'wipe_info'
        | 'is_pc'
        | 'is_console'
        | 'is_crossplay'
    >
    onEdit: (server: DashboardServerCardProps['server']) => void
    onDelete: (server: DashboardServerCardProps['server']) => void
}

export function DashboardServerCard({ server, onEdit, onDelete }: DashboardServerCardProps) {
    const status = (server.effective_status ?? 'unknown') as ServerStatus

    return (
        <div className="card-tek w-full min-w-0 p-3 hover:border-primary/30 transition-colors h-full flex flex-col min-h-[260px]">
            <div className="flex flex-col flex-1 gap-2">
                <div className="min-w-0 flex-1">
                    <div className="flex items-center gap-2 mb-1">
                        <h3 className="text-base font-semibold text-foreground truncate">
                            {server.name}
                        </h3>
                        <StatusBadge status={status} />
                    </div>
                    {server.description && (
                        <p className="text-sm text-muted-foreground line-clamp-2 mb-1.5">
                            {server.description}
                        </p>
                    )}
                    <div className="flex flex-wrap gap-1.5 mb-2">
                        {server.map_name && (
                            <span className="text-xs text-muted-foreground font-mono">
                                {server.map_name}
                            </span>
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
                    </div>
                </div>
                {/* Spacer to push actions to bottom */}
                <div className="flex-1" />
                <div className="flex items-center gap-2 shrink-0 pt-2 border-t border-input/60">
                    <Link
                        to={`/servers/${server.id}`}
                        className="text-sm text-primary hover:text-accent font-medium transition-colors"
                    >
                        View
                    </Link>
                    <Button type="button" variant="ghost" size="sm" onClick={() => onEdit(server)} className="h-auto py-1 px-2 text-sm">
                        Edit
                    </Button>
                    <Button type="button" variant="danger" size="sm" onClick={() => onDelete(server)} className="h-auto py-1 px-2 text-sm">
                        Delete
                    </Button>
                </div>
            </div>
        </div>
    )
}
