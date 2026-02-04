/**
 * Public cluster detail page.
 *
 * Shows cluster info and list of servers in that cluster.
 */

import { useMemo, useState } from 'react'
import { Link, useParams, Navigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { getDirectoryClusterBySlug } from '@/lib/api'
import { useServers } from '@/hooks/useServers'
import { ServerCard } from '@/components/servers/ServerCard'
import { ServerRow } from '@/components/servers/ServerRow'
import { LoadingSpinner } from '@/components/ui/LoadingSpinner'
import { ErrorMessage } from '@/components/ui/ErrorMessage'
import type { DirectoryView } from '@/types'

export function ClusterPage() {
    const { slug } = useParams<{ slug: string }>()
    const [view, setView] = useState<DirectoryView>('compact')

    const clusterQuery = useQuery({
        queryKey: ['directory-cluster-slug', slug],
        queryFn: () => getDirectoryClusterBySlug(slug!),
        enabled: !!slug,
        staleTime: 60_000,
    })

    const filters = useMemo(() => ({ cluster: slug ?? '', limit: 50, view }), [slug, view])
    const { servers, isLoading: serversLoading, error: serversError, total } = useServers(filters)

    if (!slug) {
        return <Navigate to="/clusters" replace />
    }

    const cluster = clusterQuery.data
    const clusterLoading = clusterQuery.isLoading

    if (clusterLoading || !cluster) {
        if (clusterQuery.isError) {
            return (
                <div className="py-8">
                    <ErrorMessage
                        error={clusterQuery.error instanceof Error ? clusterQuery.error : new Error(String(clusterQuery.error))}
                        title="Cluster not found"
                    />
                    <p className="text-center mt-4">
                        <Link to="/clusters" className="text-primary hover:text-accent underline">← Back to clusters</Link>
                    </p>
                </div>
            )
        }
        return (
            <div className="flex justify-center py-12">
                <LoadingSpinner />
            </div>
        )
    }

    return (
        <div className="py-8">
            <p className="text-sm text-muted-foreground mb-4">
                <Link to="/clusters" className="text-primary hover:text-accent underline focus:outline-none focus-visible:ring-2 focus-visible:ring-ring rounded">
                    ← Back to clusters
                </Link>
            </p>

            <div className="mb-6">
                <h1 className="text-3xl font-bold text-foreground mb-1">
                    {cluster.name}
                </h1>
                <p className="text-muted-foreground font-mono text-sm mb-2">
                    /{cluster.slug}
                </p>
                <p className="text-muted-foreground">
                    {cluster.server_count} {cluster.server_count === 1 ? 'server' : 'servers'} in this cluster
                </p>
            </div>

            {serversError && (
                <div className="mb-4">
                    <ErrorMessage
                        error={serversError instanceof Error ? serversError : new Error(String(serversError))}
                        title="Failed to load servers"
                    />
                </div>
            )}

            {serversLoading ? (
                <div className="flex justify-center py-12">
                    <LoadingSpinner />
                </div>
            ) : (
                <>
                    <div className="flex items-center justify-between gap-2 mb-4">
                        <span className="text-sm text-muted-foreground">
                            {total !== undefined ? `${total} ${total === 1 ? 'server' : 'servers'}` : null}
                        </span>
                        <button
                            type="button"
                            onClick={() => setView((v) => (v === 'compact' ? 'card' : 'compact'))}
                            className="text-sm text-primary hover:text-accent underline focus:outline-none focus-visible:ring-2 focus-visible:ring-ring rounded"
                        >
                            View: {view === 'compact' ? 'Card' : 'Row'}
                        </button>
                    </div>

                    {servers.length === 0 ? (
                        <p className="text-muted-foreground py-8 text-center">
                            No servers in this cluster yet.
                        </p>
                    ) : view === 'card' ? (
                        <ul className="grid gap-4 grid-cols-1 md:grid-cols-2">
                            {servers.map((server) => (
                                <li key={server.id}>
                                    <ServerCard server={server} />
                                </li>
                            ))}
                        </ul>
                    ) : (
                        <ul className="space-y-1">
                            {servers.map((server) => (
                                <li key={server.id}>
                                    <ServerRow server={server} />
                                </li>
                            ))}
                        </ul>
                    )}
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
