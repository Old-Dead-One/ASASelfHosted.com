/**
 * Server list component.
 *
 * Displays a list of servers using ServerCard components.
 * Consumes DirectoryServer data from directory_view.
 */

import { useServers } from '@/hooks/useServers'
import { ServerCard } from './ServerCard'

export function ServerList() {
    const { data: servers, isLoading, error } = useServers()

    if (isLoading) {
        return (
            <div className="text-center py-12">
                <p className="text-muted-foreground">Loading servers...</p>
            </div>
        )
    }

    if (error) {
        return (
            <div className="text-center py-12">
                <p className="text-destructive">Error loading servers</p>
                {error instanceof Error && (
                    <p className="text-sm text-muted-foreground mt-2">{error.message}</p>
                )}
            </div>
        )
    }

    if (!servers || servers.length === 0) {
        return (
            <div className="text-center py-12">
                <p className="text-muted-foreground">No servers found</p>
            </div>
        )
    }

    return (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {servers.map((server) => (
                <ServerCard key={server.id} server={server} />
            ))}
        </div>
    )
}
