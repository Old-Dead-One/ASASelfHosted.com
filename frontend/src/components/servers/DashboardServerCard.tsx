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
    onClone: (server: DashboardServerCardProps['server']) => void
}

export function DashboardServerCard({ server, onEdit, onClone }: DashboardServerCardProps) {
    const status = (server.effective_status ?? 'unknown') as ServerStatus

    return (
        <div className="relative overflow-hidden rounded-lg tek-border w-full min-w-0 hover:border-primary/30 transition-colors h-full flex flex-col min-h-[260px]">
            <div className="absolute inset-0 bg-tek-wall" aria-hidden />
            <div className="absolute inset-0 tek-seam opacity-70 pointer-events-none" aria-hidden />
            <div className="relative p-3 bg-background/65 backdrop-blur-[1px] flex flex-col flex-1">
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
                    <div className="flex items-center justify-center shrink-0 pt-2 border-t border-input/60">
                        <div className="inline-flex items-center rounded-md border border-input/60 overflow-hidden shadow-sm">
                            <Link
                                to={`/servers/${server.id}`}
                                className="px-3 py-1.5 text-sm font-medium text-primary hover:text-accent hover:bg-muted/25 transition-colors border-r border-input/60 focus:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-1"
                            >
                                View
                            </Link>
                            <Button
                                type="button"
                                variant="ghost"
                                size="sm"
                                onClick={() => onEdit(server)}
                                className="h-auto py-1.5 px-3 text-sm rounded-none border-r border-input/60 hover:bg-muted/25"
                            >
                                Edit
                            </Button>
                            <Button
                                type="button"
                                variant="ghost"
                                size="sm"
                                onClick={() => onClone(server)}
                                className="h-auto py-1.5 px-3 text-sm rounded-none hover:bg-muted/25"
                            >
                                Clone
                            </Button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    )
}
