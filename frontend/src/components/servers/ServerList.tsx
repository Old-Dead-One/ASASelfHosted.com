/**
 * Server list component.
 *
 * Displays a list of servers using ServerCard components.
 * Consumes DirectoryServer data from directory_view.
 */

import { useServers } from '@/hooks/useServers'
import { ServerCard } from './ServerCard'

export function ServerList() {
    const { data, isLoading, error, refetch } = useServers()
    const servers = data?.data ?? []

    if (isLoading) {
        return (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {[...Array(6)].map((_, i) => (
                    <div
                        key={i}
                        className="h-64 rounded-lg border border-border bg-card animate-pulse"
                    >
                        <div className="p-4 space-y-4">
                            <div className="h-6 bg-muted rounded w-3/4"></div>
                            <div className="h-4 bg-muted rounded w-full"></div>
                            <div className="h-4 bg-muted rounded w-5/6"></div>
                            <div className="flex gap-2 mt-4">
                                <div className="h-6 bg-muted rounded w-20"></div>
                                <div className="h-6 bg-muted rounded w-16"></div>
                            </div>
                        </div>
                    </div>
                ))}
            </div>
        )
    }

    if (error) {
        return (
            <div className="text-center py-12">
                <p className="text-destructive font-medium">Error loading servers</p>
                {import.meta.env.DEV && error instanceof Error && (
                    <p className="text-sm text-muted-foreground mt-2">{error.message}</p>
                )}
                <button
                    onClick={() => refetch()}
                    className="mt-4 px-4 py-2 text-sm font-medium text-primary-foreground bg-primary rounded-md hover:bg-primary/90 transition-colors"
                >
                    Retry
                </button>
            </div>
        )
    }

    if (!servers || servers.length === 0) {
        return (
            <div className="text-center py-12">
                <p className="text-muted-foreground font-medium">No servers found</p>
                <p className="text-sm text-muted-foreground mt-2">
                    Try clearing your filters or broadening your search.
                </p>
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
