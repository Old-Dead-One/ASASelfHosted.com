/**
 * Public clusters list page.
 *
 * Lists public clusters from the directory with cursor pagination.
 */

import { useState, useCallback } from 'react'
import { Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { listDirectoryClusters } from '@/lib/api'
import { Button } from '@/components/ui/Button'
import { LoadingSpinner } from '@/components/ui/LoadingSpinner'
import { ErrorMessage } from '@/components/ui/ErrorMessage'
import type { DirectoryCluster } from '@/types'

const PAGE_SIZE = 24

export function ClustersPage() {
    const [cursor, setCursor] = useState<string | null>(null)
    const [cursorStack, setCursorStack] = useState<(string | null)[]>([])

    const { data, isLoading, error, isFetching } = useQuery({
        queryKey: ['directory-clusters', cursor],
        queryFn: () =>
            listDirectoryClusters({
                limit: PAGE_SIZE,
                cursor: cursor ?? undefined,
                sort_by: 'updated',
                order: 'desc',
            }),
        staleTime: 60_000,
    })

    const clusters = (data?.data ?? []) as DirectoryCluster[]
    const nextCursor = data?.next_cursor ?? null
    const hasNext = !!nextCursor
    const hasPrev = cursorStack.length > 0

    const nextPage = useCallback(() => {
        if (nextCursor) {
            setCursorStack((s) => [...s, cursor])
            setCursor(nextCursor)
        }
    }, [nextCursor, cursor])

    const prevPage = useCallback(() => {
        if (cursorStack.length > 0) {
            const prev = cursorStack[cursorStack.length - 1]
            setCursorStack((s) => s.slice(0, -1))
            setCursor(prev)
        }
    }, [cursorStack])

    return (
        <div className="py-8">
            <div className="mb-6 text-center">
                <h1 className="text-4xl font-bold text-foreground mb-2">
                    Clusters
                </h1>
                <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
                    Browse public server clusters. Each cluster groups multiple servers (e.g. one per map).
                </p>
            </div>

            {error && (
                <div className="mb-4">
                    <ErrorMessage
                        error={error instanceof Error ? error : new Error(String(error))}
                        title="Failed to load clusters"
                    />
                </div>
            )}

            {isLoading ? (
                <div className="flex justify-center py-12">
                    <LoadingSpinner />
                </div>
            ) : (
                <>
                    {clusters.length === 0 ? (
                        <p className="text-center text-muted-foreground py-8">
                            No public clusters yet.
                        </p>
                    ) : (
                        <ul className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 mb-8">
                            {clusters.map((cluster) => (
                                <li key={cluster.id}>
                                    <Link
                                        to={`/clusters/${encodeURIComponent(cluster.slug)}`}
                                        className="block rounded-xl border border-input bg-background-elevated p-4 shadow-lg shadow-black/40 hover:border-primary/40 hover:bg-muted/20 transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-ring"
                                    >
                                        <h2 className="text-lg font-semibold text-foreground mb-1">
                                            {cluster.name}
                                        </h2>
                                        <p className="text-sm text-muted-foreground font-mono mb-2">
                                            /{cluster.slug}
                                        </p>
                                        <p className="text-sm text-muted-foreground">
                                            {cluster.server_count} {cluster.server_count === 1 ? 'server' : 'servers'}
                                        </p>
                                    </Link>
                                </li>
                            ))}
                        </ul>
                    )}

                    <div className="flex items-center justify-center gap-4">
                        <Button
                            type="button"
                            variant="secondary"
                            onClick={prevPage}
                            disabled={!hasPrev || isFetching}
                            aria-label="Previous page"
                        >
                            Previous
                        </Button>
                        <Button
                            type="button"
                            variant="secondary"
                            onClick={nextPage}
                            disabled={!hasNext || isFetching}
                            aria-label="Next page"
                        >
                            Next
                        </Button>
                    </div>
                </>
            )}

            <p className="text-center text-sm text-muted-foreground mt-8">
                <Link to="/" className="text-primary hover:text-accent underline focus:outline-none focus-visible:ring-2 focus-visible:ring-ring rounded">
                    ← Back to directory
                </Link>
            </p>
        </div>
    )
}
