/**
 * Server detail page.
 *
 * Displays detailed information about a single server.
 */

import { useServer } from '@/hooks/useServers'

interface ServerPageProps {
    serverId: string
}

export function ServerPage({ serverId }: ServerPageProps) {
    const { data: server, isLoading, error } = useServer(serverId)

    if (isLoading) {
        return <div>Loading server...</div>
    }

    if (error) {
        return <div>Error loading server</div>
    }

    if (!server) {
        return <div>Server not found</div>
    }

    // TODO: Implement server detail UI
    return (
        <div>
            <h1>{server.name}</h1>
            <p>{server.description}</p>
        </div>
    )
}
