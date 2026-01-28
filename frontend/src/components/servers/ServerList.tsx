/**
 * Server list component.
 *
 * Displays servers from directory with cursor pagination and "Load more".
 */

import { useServers } from '@/hooks/useServers'
import { ServerCard } from './ServerCard'
import { ServerRow } from './ServerRow'
import { Button } from '@/components/ui/Button'
import { ErrorMessage } from '@/components/ui/ErrorMessage'
import type { ServerFilters } from './ServerFilters'

interface ServerListProps {
    filters?: ServerFilters
}

export function ServerList({ filters }: ServerListProps) {
    const {
        servers,
        isLoading,
        error,
        refetch,
        hasNextPage,
        fetchNextPage,
        isFetchingNextPage,
    } = useServers(filters)

    const view = filters?.view ?? 'compact'
    const isCardView = view === 'card'

    if (isLoading) {
        if (isCardView) {
            return (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {[...Array(6)].map((_, i) => (
                        <div
                            key={i}
                            className="h-64 card-tek animate-pulse"
                        >
                            <div className="p-4 space-y-4">
                                <div className="h-6 bg-muted rounded w-3/4" />
                                <div className="h-4 bg-muted rounded w-full" />
                                <div className="h-4 bg-muted rounded w-5/6" />
                                <div className="flex gap-2 mt-4">
                                    <div className="h-6 bg-muted rounded w-20" />
                                    <div className="h-6 bg-muted rounded w-16" />
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            )
        }
        return (
            <div className="space-y-1.5">
                {[...Array(6)].map((_, i) => (
                    <div
                        key={i}
                        className="h-10 rounded-md border border-input bg-background-elevated animate-pulse"
                    >
                        <div className="py-2 px-3 flex items-center gap-3">
                            <div className="h-5 w-14 bg-muted rounded" />
                            <div className="flex-1 h-5 bg-muted rounded w-1/3" />
                            <div className="h-5 w-16 bg-muted rounded" />
                        </div>
                    </div>
                ))}
            </div>
        )
    }

    if (error) {
        return (
            <div className="py-8">
                <ErrorMessage
                    error={error}
                    title="Failed to load servers"
                    onRetry={() => refetch()}
                />
            </div>
        )
    }

    if (!servers.length) {
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
        <div className="space-y-6">
            {isCardView ? (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {servers.map((server) => (
                        <ServerCard key={server.id} server={server} />
                    ))}
                </div>
            ) : (
                <div className="space-y-1.5">
                    {servers.map((server) => (
                        <ServerRow key={server.id} server={server} />
                    ))}
                </div>
            )}
            {hasNextPage && (
                <div className="flex justify-center pt-4">
                    <Button
                        type="button"
                        variant="secondary"
                        onClick={() => fetchNextPage()}
                        disabled={isFetchingNextPage}
                        className="min-h-[44px]"
                        aria-label="Load more servers"
                    >
                        {isFetchingNextPage ? 'Loading…' : 'Load more'}
                    </Button>
                </div>
            )}
        </div>
    )
}
