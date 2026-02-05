/**
 * Owner dashboard page.
 *
 * Displays user's servers and allows CRUD operations.
 * Connects to GET/POST/PUT/DELETE /api/v1/servers.
 */

import { useState, useCallback } from 'react'
import { useAuth } from '@/contexts/AuthContext'
import { ServerForm, type ServerFormData, type PlatformChoice } from '@/components/servers/ServerForm'
import { DashboardServersCarousel } from '@/components/servers/DashboardServersCarousel'
import { DashboardServerRow } from '@/components/servers/DashboardServerRow'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import { useMyServers, useInvalidateMyServers } from '@/hooks/useMyServers'
import { useLimits } from '../hooks/useLimits'
import { useConsentState } from '@/hooks/useConsentState'
import {
    API_BASE_URL,
    HEARTBEAT_PATH,
    createServer,
    updateServer,
    deleteServer,
    getTermsAcceptance,
    acceptTerms,
    listMyClusters,
    createCluster,
    updateCluster,
    deleteCluster,
    generateClusterKeys,
    getMyFavorites,
    removeFavorite,
    assignAllServersToCluster,
    APIErrorResponse,
    type Cluster,
    type KeyPairResponse,
} from '@/lib/api'
import { Link } from 'react-router-dom'
import { Button } from '@/components/ui/Button'
import { ErrorMessage } from '@/components/ui/ErrorMessage'
import { LoadingSpinner } from '@/components/ui/LoadingSpinner'
import { TermsAcceptanceModal } from '@/components/TermsAcceptanceModal'
import type { DirectoryServer, Ruleset } from '@/types'

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

function isNotImplementedError(err: unknown): boolean {
    if (err instanceof APIErrorResponse) {
        const m = err.message.toLowerCase()
        return m.includes('not yet implemented') || m.includes('not implemented')
    }
    return false
}

function platformToFlags(platform: PlatformChoice | ''): { is_pc: boolean; is_console: boolean; is_crossplay: boolean } | undefined {
    if (!platform) return undefined
    if (platform === 'pc') return { is_pc: true, is_console: false, is_crossplay: false }
    if (platform === 'console') return { is_pc: false, is_console: true, is_crossplay: false }
    if (platform === 'crossplay') return { is_pc: true, is_console: true, is_crossplay: true }
    return undefined
}

function formDataToCreatePayload(data: ServerFormData): Record<string, unknown> {
    const modList = data.mod_list
        ? data.mod_list.split(',').map((m) => m.trim()).filter((m) => m.length > 0)
        : null
    const platformFlags = platformToFlags(data.platform)
    const joinInstructions = data.join_instructions?.trim() || null
    const body: Record<string, unknown> = {
        name: data.name.trim(),
        description: data.description?.trim() || null,
        cluster_id: data.cluster_id?.trim() || null,
        map_name: data.map_name?.trim() || null,
        join_address: data.join_address?.trim() || null,
        join_password: data.join_password?.trim() || null,
        join_instructions_pc: joinInstructions,
        join_instructions_console: joinInstructions,
        discord_url: data.discord_url?.trim() || null,
        website_url: data.website_url?.trim() || null,
        mod_list: modList && modList.length > 0 ? modList : null,
        rates: data.rates?.trim() || null,
        wipe_info: data.wipe_info?.trim() || null,
        game_mode: data.game_mode || null,
        rulesets: data.rulesets && data.rulesets.length > 0 ? data.rulesets : null,
        effective_status: data.effective_status || null,
    }
    if (platformFlags) {
        body.is_pc = platformFlags.is_pc
        body.is_console = platformFlags.is_console
        body.is_crossplay = platformFlags.is_crossplay
    }
    return body
}

function formDataToUpdatePayload(data: ServerFormData): Record<string, unknown> {
    const modList = data.mod_list
        ? data.mod_list.split(',').map((m) => m.trim()).filter((m) => m.length > 0)
        : null
    const platformFlags = platformToFlags(data.platform)
    const joinInstructions = data.join_instructions?.trim() || null
    const body: Record<string, unknown> = {
        name: data.name.trim(),
        description: data.description?.trim() || null,
        cluster_id: data.cluster_id?.trim() || null,
        map_name: data.map_name?.trim() || null,
        join_address: data.join_address?.trim() || null,
        join_password: data.join_password?.trim() || null,
        join_instructions_pc: joinInstructions,
        join_instructions_console: joinInstructions,
        discord_url: data.discord_url?.trim() || null,
        website_url: data.website_url?.trim() || null,
        mod_list: modList && modList.length > 0 ? modList : null,
        rates: data.rates?.trim() || null,
        wipe_info: data.wipe_info?.trim() || null,
        game_mode: data.game_mode || null,
        rulesets: data.rulesets && data.rulesets.length > 0 ? data.rulesets : null,
        effective_status: data.effective_status || null,
    }
    if (platformFlags) {
        body.is_pc = platformFlags.is_pc
        body.is_console = platformFlags.is_console
        body.is_crossplay = platformFlags.is_crossplay
    }
    return body
}

function serverToFormData(s: DashboardServer, excludeNameAddressAndMap = false): Partial<ServerFormData> {
    const modListString = s.mod_list && s.mod_list.length > 0 ? s.mod_list.join(', ') : ''
    const rulesets = (s as { rulesets?: string[] }).rulesets && (s as { rulesets?: string[] }).rulesets!.length > 0
        ? (s as { rulesets: string[] }).rulesets
        : (s.ruleset ? [s.ruleset] : [])
    let platform: PlatformChoice | '' = ''
    if (s.is_pc && s.is_console) platform = 'crossplay'
    else if (s.is_pc) platform = 'pc'
    else if (s.is_console) platform = 'console'

    return {
        is_self_hosted_confirmed: true,
        name: excludeNameAddressAndMap ? '' : s.name,
        description: s.description ?? '',
        map_name: excludeNameAddressAndMap ? '' : (s.map_name ?? ''),
        join_address: excludeNameAddressAndMap ? '' : (s.join_address ?? ''),
        join_password: s.join_password ?? '',
        join_instructions: s.join_instructions_pc || s.join_instructions_console || '',
        discord_url: s.discord_url ?? '',
        website_url: s.website_url ?? '',
        mod_list: modListString,
        rates: s.rates ?? '',
        wipe_info: s.wipe_info ?? '',
        game_mode: s.game_mode ?? '',
        ruleset: s.ruleset ?? '',
        rulesets: rulesets as Ruleset[],
        effective_status: s.effective_status ?? '',
        cluster_id: s.cluster_id ?? '',
        platform,
    }
}

export function DashboardPage() {
    const { user, isAuthenticated } = useAuth()
    const { data: myServers, isLoading, error, refetch } = useMyServers()
    const { data: limits } = useLimits()
    const { data: consentState } = useConsentState()
    const invalidate = useInvalidateMyServers()
    const atServerLimit = limits ? limits.servers_used >= limits.servers_limit : false
    const atClusterLimit = limits ? limits.clusters_used >= limits.clusters_limit : false

    const [showCreateForm, setShowCreateForm] = useState(false)
    const [editingServer, setEditingServer] = useState<DashboardServer | null>(null)
    const [cloningServer, setCloningServer] = useState<DashboardServer | null>(null)
    const [deleteConfirm, setDeleteConfirm] = useState<DashboardServer | null>(null)
    const [crudError, setCrudError] = useState<string | null>(null)
    const [showServerListingTermsModal, setShowServerListingTermsModal] = useState(false)
    const [serverListingTermsAgreed, setServerListingTermsAgreed] = useState(false)
    const [serverListingTermsLoading, setServerListingTermsLoading] = useState(false)
    const [keyResult, setKeyResult] = useState<KeyPairResponse | null>(null)
    const [keyGeneratingClusterId, setKeyGeneratingClusterId] = useState<string | null>(null)
    const [serversView, setServersView] = useState<'carousel' | 'row'>('carousel')
    const [showCreateClusterForm, setShowCreateClusterForm] = useState(false)
    const [editingCluster, setEditingCluster] = useState<Cluster | null>(null)
    const [deleteClusterConfirm, setDeleteClusterConfirm] = useState<Cluster | null>(null)
    const [assignAllConfirm, setAssignAllConfirm] = useState<Cluster | null>(null)
    const [assignAllPreview, setAssignAllPreview] = useState<import('@/lib/api').AssignAllServersResponse | null>(null)
    const [assignAllOnlyUnclustered, setAssignAllOnlyUnclustered] = useState(false)
    const [assignAllLoading, setAssignAllLoading] = useState(false)
    const [clusterFormName, setClusterFormName] = useState('')
    const [clusterFormSlug, setClusterFormSlug] = useState('')
    const [clusterFormVisibility, setClusterFormVisibility] = useState<'public' | 'unlisted'>('public')
    const [copiedLabel, setCopiedLabel] = useState<string | null>(null)
    const clusterUrlPrefix =
        typeof window !== 'undefined' ? `${window.location.origin}/clusters/` : '/clusters/'

    const copyToClipboard = useCallback((label: string, text: string) => {
        navigator.clipboard.writeText(text).then(
            () => {
                setCopiedLabel(label)
                setTimeout(() => setCopiedLabel(null), 2000)
            },
            () => { }
        )
    }, [])

    const queryClient = useQueryClient()
    const { data: clusters = [] } = useQuery({
        queryKey: ['my-clusters'],
        queryFn: listMyClusters,
        enabled: isAuthenticated,
        staleTime: 60_000,
    })
    const primaryCluster = (clusters as Cluster[]).length > 0 ? (clusters as Cluster[])[0] : null
    const { data: favoritesData } = useQuery({
        queryKey: ['my-favorites'],
        queryFn: getMyFavorites,
        enabled: isAuthenticated,
        staleTime: 30_000,
    })
    const favorites = favoritesData?.data ?? []

    const servers = (myServers?.data ?? []) as DashboardServer[]
    const showList = !showCreateForm && !editingServer && !cloningServer

    // Check if error is due to authentication (user is logged in but token invalid)
    const isAuthError = error instanceof Error && (
        error.message.includes('Authentication required') ||
        error.message.includes('Please sign in') ||
        error.message.includes('UNAUTHORIZED')
    ) && isAuthenticated

    const handleCreateServer = useCallback(
        async (data: ServerFormData) => {
            setCrudError(null)
            try {
                await createServer(formDataToCreatePayload(data))
                invalidate()
                setShowCreateForm(false)
                setCloningServer(null)
            } catch (err) {
                if (isNotImplementedError(err)) {
                    setCrudError(
                        'Server creation is not yet available. The backend will support it soon.'
                    )
                    return
                }
                // Check if it's an auth error
                if (err instanceof Error && (
                    err.message.includes('Authentication required') ||
                    err.message.includes('UNAUTHORIZED')
                )) {
                    setCrudError('Authentication required. Please sign in to perform this action.')
                    return
                }
                if (err instanceof APIErrorResponse && err.code === 'server_limit_reached') {
                    setCrudError(err.message)
                    return
                }
                throw err
            }
        },
        [invalidate]
    )

    const handleAddClusterClick = useCallback(() => {
        setShowCreateClusterForm(true)
        setEditingCluster(null)
        setClusterFormName('')
        setClusterFormSlug('')
        setClusterFormVisibility('public')
        setCrudError(null)
        // Jump user to the clusters section so the inline form is visible.
        window.setTimeout(() => {
            document.getElementById('clusters-heading')?.scrollIntoView({ behavior: 'smooth', block: 'start' })
        }, 0)
    }, [])

    const handleManageClusterClick = useCallback(() => {
        if (!primaryCluster) return
        setEditingCluster(primaryCluster)
        setClusterFormName(primaryCluster.name)
        setClusterFormSlug(primaryCluster.slug)
        setClusterFormVisibility(primaryCluster.visibility)
        setCrudError(null)
        window.setTimeout(() => {
            document.getElementById('clusters-heading')?.scrollIntoView({ behavior: 'smooth', block: 'start' })
        }, 0)
    }, [primaryCluster])

    const handleUpdateServer = useCallback(
        async (data: ServerFormData) => {
            if (!editingServer) return
            setCrudError(null)
            try {
                await updateServer(editingServer.id, formDataToUpdatePayload(data))
                invalidate()
                setEditingServer(null)
            } catch (err) {
                if (isNotImplementedError(err)) {
                    setCrudError(
                        'Server updates are not yet available. The backend will support it soon.'
                    )
                    return
                }
                // Check if it's an auth error
                if (err instanceof Error && (
                    err.message.includes('Authentication required') ||
                    err.message.includes('UNAUTHORIZED')
                )) {
                    setCrudError('Authentication required. Please sign in to perform this action.')
                    return
                }
                throw err
            }
        },
        [editingServer, invalidate]
    )

    const handleDeleteServer = useCallback(
        async (server: DashboardServer) => {
            setCrudError(null)
            try {
                await deleteServer(server.id)
                invalidate()
                setDeleteConfirm(null)
                setEditingServer(null)
            } catch (err) {
                if (isNotImplementedError(err)) {
                    setCrudError(
                        'Server deletion is not yet available. The backend will support it soon.'
                    )
                    return
                }
                // Check if it's an auth error
                if (err instanceof Error && (
                    err.message.includes('Authentication required') ||
                    err.message.includes('UNAUTHORIZED')
                )) {
                    setCrudError('Authentication required. Please sign in to perform this action.')
                    return
                }
                throw err
            }
        },
        [invalidate]
    )

    const handleCloneServer = useCallback(
        (server: DashboardServer) => {
            setCrudError(null)
            setEditingServer(null)
            setCloningServer(server)
            setShowCreateForm(true)
        },
        []
    )

    const invalidateClustersAndLimits = useCallback(() => {
        queryClient.invalidateQueries({ queryKey: ['my-clusters'] })
        queryClient.invalidateQueries({ queryKey: ['limits'] })
    }, [queryClient])

    const handleCreateCluster = useCallback(async () => {
        setCrudError(null)
        const name = clusterFormName.trim()
        const slug = clusterFormSlug.trim()
        if (!name || !slug) return
        try {
            await createCluster({
                name,
                slug,
                visibility: clusterFormVisibility,
            })
            invalidateClustersAndLimits()
            setShowCreateClusterForm(false)
            setClusterFormName('')
            setClusterFormSlug('')
            setClusterFormVisibility('public')
        } catch (err) {
            if (err instanceof APIErrorResponse && err.code === 'cluster_limit_reached') {
                setCrudError(err.message)
                return
            }
            setCrudError(err instanceof Error ? err.message : 'Failed to create cluster.')
        }
    }, [clusterFormName, clusterFormSlug, clusterFormVisibility, invalidateClustersAndLimits])

    const handleUpdateCluster = useCallback(async () => {
        if (!editingCluster) return
        setCrudError(null)
        const name = clusterFormName.trim()
        const slug = clusterFormSlug.trim()
        if (!name || !slug) return
        try {
            await updateCluster(editingCluster.id, {
                name,
                slug,
                visibility: clusterFormVisibility,
            })
            invalidateClustersAndLimits()
            setEditingCluster(null)
            setClusterFormName('')
            setClusterFormSlug('')
            setClusterFormVisibility('public')
        } catch (err) {
            setCrudError(err instanceof Error ? err.message : 'Failed to update cluster.')
        }
    }, [editingCluster, clusterFormName, clusterFormSlug, clusterFormVisibility, invalidateClustersAndLimits])

    const handleDeleteCluster = useCallback(async () => {
        if (!deleteClusterConfirm) return
        setCrudError(null)
        try {
            await deleteCluster(deleteClusterConfirm.id)
            invalidateClustersAndLimits()
            setDeleteClusterConfirm(null)
            setEditingCluster(null)
        } catch (err) {
            setCrudError(err instanceof Error ? err.message : 'Failed to delete cluster.')
        }
    }, [deleteClusterConfirm, invalidateClustersAndLimits])

    const openAssignAllConfirm = useCallback(
        async (cluster: Cluster) => {
            setCrudError(null)
            setAssignAllConfirm(cluster)
            setAssignAllPreview(null)
            setAssignAllOnlyUnclustered(false)
            setAssignAllLoading(true)
            try {
                const preview = await assignAllServersToCluster(cluster.id, { dry_run: true })
                setAssignAllPreview(preview)
            } catch {
                setCrudError('Failed to preview server assignment. Please try again.')
            } finally {
                setAssignAllLoading(false)
            }
        },
        []
    )

    const handleAddServerClick = useCallback(() => {
        setCloningServer(null)
        setCrudError(null)
        if (atServerLimit) return
        if (servers.length === 0) {
            getTermsAcceptance()
                .then((r) => {
                    if (r.server_listing_terms_accepted_at) {
                        setShowCreateForm(true)
                    } else {
                        setServerListingTermsAgreed(false)
                        setShowServerListingTermsModal(true)
                    }
                })
                .catch(() => setShowCreateForm(true))
        } else {
            setShowCreateForm(true)
        }
    }, [servers.length, atServerLimit])

    const handleServerListingTermsContinue = useCallback(async () => {
        if (!serverListingTermsAgreed) return
        setServerListingTermsLoading(true)
        try {
            await acceptTerms('server_listing')
            setShowServerListingTermsModal(false)
            setServerListingTermsAgreed(false)
            setShowCreateForm(true)
        } catch {
            setCrudError('Could not record terms acceptance. Please try again.')
        } finally {
            setServerListingTermsLoading(false)
        }
    }, [serverListingTermsAgreed])

    return (
        <div className="py-8">
            <div className="mb-4 text-center">
                <h1 className="text-4xl font-bold text-foreground">
                    Dashboard
                </h1>
                <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
                    Welcome back, {user?.email ?? 'User'}.
                </p>
                {consentState && (
                    <p className="text-sm text-muted-foreground mt-1" title="Data collection status: Inactive = no data collected; Partial = server eligible, player consent pending; Active = both agreed. Disabled actions may be due to consent or eligibility—see Consent page for details.">
                        Data collection: <span className="font-medium capitalize">{consentState.consent_state}</span>
                    </p>
                )}
            </div>

            {crudError && (
                <div className="mb-4">
                    <ErrorMessage
                        error={new Error(crudError)}
                        title="Action unavailable"
                    />
                    {crudError.includes('Authentication required') && (
                        <div className="mt-4 p-4 bg-warning/20 border border-warning rounded-md">
                            <p className="text-sm text-warning-foreground mb-2">
                                <strong>Authentication Required:</strong> Please sign in to perform this action.
                            </p>
                            <p className="text-xs text-warning-foreground">
                                If you just signed up, try signing out and back in to refresh your session.
                            </p>
                        </div>
                    )}
                </div>
            )}

            {showCreateForm && (
                <div className="rounded-xl border border-input bg-background-elevated p-4 shadow-lg shadow-black/40 mb-8">
                    <h2 className="text-xl font-semibold text-foreground mb-2">
                        {cloningServer ? 'Clone Server' : 'Create New Server'}
                    </h2>
                    {cloningServer && (
                        <p className="text-sm text-muted-foreground mb-4">
                            Cloning from &quot;{cloningServer.name}&quot;. Please provide a new server name, map name, and join address.
                        </p>
                    )}
                    <ServerForm
                        initialData={cloningServer ? serverToFormData(cloningServer, true) : undefined}
                        onSubmit={handleCreateServer}
                        onCancel={() => {
                            setShowCreateForm(false)
                            setCloningServer(null)
                            setCrudError(null)
                        }}
                    />
                </div>
            )}

            {editingServer && (
                <div className="rounded-xl border border-input bg-background-elevated p-4 shadow-lg shadow-black/40">
                    <h2 className="text-xl font-semibold text-foreground mb-4">
                        Edit Server
                    </h2>
                    <ServerForm
                        serverId={editingServer.id}
                        initialData={serverToFormData(editingServer)}
                        onSubmit={handleUpdateServer}
                        onCancel={() => {
                            setEditingServer(null)
                            setCrudError(null)
                        }}
                        onDelete={() => setDeleteConfirm(editingServer)}
                        submitLabel="Save Changes"
                    />
                </div>
            )}

            {showList && (
                <>
                    {favorites.length > 0 ? (
                        <div className="card-elevated p-3 mb-4">
                            <h2 className="text-lg font-semibold text-foreground mb-2">Your Favorites</h2>
                            <ul className="flex flex-wrap items-center gap-x-3 gap-y-1 text-sm">
                                {favorites.map((fav) => (
                                    <li key={fav.id} className="flex items-center gap-1.5">
                                        <Link
                                            to={`/servers/${fav.id}`}
                                            className="text-primary hover:text-accent font-medium focus:outline-none focus-visible:ring-2 focus-visible:ring-ring rounded"
                                        >
                                            {fav.name}
                                        </Link>
                                        <Button
                                            type="button"
                                            variant="ghost"
                                            size="sm"
                                            className="h-6 px-1.5 text-xs text-muted-foreground hover:text-foreground"
                                            onClick={async () => {
                                                try {
                                                    await removeFavorite(fav.id)
                                                    queryClient.invalidateQueries({ queryKey: ['my-favorites'] })
                                                } catch {
                                                    setCrudError('Failed to remove favorite. Please try again.')
                                                }
                                            }}
                                        >
                                            Remove
                                        </Button>
                                    </li>
                                ))}
                            </ul>
                        </div>
                    ) : (
                        <div className="card-elevated p-3 mb-4">
                            <h2 className="text-lg font-semibold text-foreground mb-1">Favorites</h2>
                            <p className="text-muted-foreground text-sm">
                                No favorites yet. <Link to="/" className="text-primary hover:text-accent underline focus:outline-none focus-visible:ring-2 focus-visible:ring-ring rounded">Browse the directory</Link> to add servers.
                            </p>
                        </div>
                    )}
                </>
            )}

            {showList && (
                <div className="card-elevated px-4 pt-4 pb-2">
                    <div className="flex items-center justify-between gap-4">
                        <h2 className="text-xl font-semibold text-foreground">Your Servers</h2>
                        {!isLoading && !error && (
                            <div className="flex items-center gap-2 shrink-0 mb-2">
                                <span className="text-sm text-muted-foreground whitespace-nowrap">View:</span>
                                <Button
                                    type="button"
                                    variant="secondary"
                                    size="sm"
                                    onClick={() => setServersView((v) => (v === 'carousel' ? 'row' : 'carousel'))}
                                    className="min-h-[36px]"
                                    aria-label={`Switch to ${serversView === 'carousel' ? 'row' : 'carousel'} view`}
                                >
                                    {serversView === 'carousel' ? 'Row' : 'Carousel'}
                                </Button>
                            </div>
                        )}
                    </div>
                    {isLoading ? (
                        <div className="py-12 text-center">
                            <LoadingSpinner size="lg" className="mx-auto mb-4" />
                            <p className="text-muted-foreground">Loading your servers…</p>
                        </div>
                    ) : (error && !isAuthError) ? (
                        <div className="w-full py-8">
                            <ErrorMessage
                                error={error}
                                title="Failed to load servers"
                                onRetry={() => refetch()}
                            />
                        </div>
                    ) : (
                        <>
                            {/* Show "No servers yet" message when empty, but still show carousel with Add Server card */}
                            {servers.length === 0 && (
                                <div className="w-full text-center mb-6">
                                    <p className="text-lg text-muted-foreground mb-2">
                                        No servers yet
                                    </p>
                                    <p className="text-sm text-muted-foreground mb-4">
                                        Your servers will appear here once you create them. Get started by adding your first server listing.
                                    </p>
                                    {isAuthError && (
                                        <div className="mb-4 p-3 bg-warning/20 border border-warning rounded-md text-left max-w-2xl mx-auto">
                                            <p className="text-xs text-warning-foreground mb-1">
                                                <strong>Authentication Error:</strong> Unable to load your servers.
                                            </p>
                                            <p className="text-xs text-warning-foreground">
                                                Try signing out and back in to refresh your session.
                                            </p>
                                        </div>
                                    )}
                                </div>
                            )}
                            {serversView === 'carousel' ? (
                                <div className="-mx-4">
                                    <DashboardServersCarousel
                                        servers={servers}
                                        onAddServer={handleAddServerClick}
                                        onAddCluster={handleAddClusterClick}
                                        onEdit={setEditingServer}
                                        onClone={handleCloneServer}
                                        addServerDisabled={atServerLimit}
                                        addServerDisabledReason={atServerLimit ? `Server limit reached (${limits?.servers_used ?? 0} of ${limits?.servers_limit ?? 0}). Delete a server to add another.` : undefined}
                                        serversUsed={limits?.servers_used}
                                        serversLimit={limits?.servers_limit}
                                        clustersUsed={limits?.clusters_used}
                                        clustersLimit={limits?.clusters_limit}
                                        cluster={primaryCluster}
                                        onManageCluster={primaryCluster ? handleManageClusterClick : undefined}
                                    />
                                </div>
                            ) : (
                                <div className="space-y-1.5">
                                    {!atServerLimit && (
                                        <div className="w-full rounded-md border-2 border-dashed border-input bg-background-elevated/60 overflow-hidden">
                                            <button
                                                type="button"
                                                onClick={handleAddServerClick}
                                                className="w-full py-3 px-3 text-sm text-muted-foreground hover:border-primary/40 hover:text-foreground hover:bg-muted/20 transition-colors text-left focus:outline-none focus-visible:ring-2 focus-visible:ring-ring"
                                            >
                                                <span className="flex items-center justify-between gap-3">
                                                    <span className="flex items-center gap-2">
                                                        <span className="w-6 h-6 rounded-full border-2 border-primary/50 text-primary flex items-center justify-center shrink-0" aria-hidden>
                                                            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="w-3.5 h-3.5">
                                                                <line x1="12" y1="5" x2="12" y2="19" />
                                                                <line x1="5" y1="12" x2="19" y2="12" />
                                                            </svg>
                                                        </span>
                                                        <span className="font-medium">Add server</span>
                                                    </span>
                                                    {limits != null && (
                                                        <span className="text-xs">
                                                            <span className="font-medium text-primary/90">{limits.servers_used}</span> of{' '}
                                                            <span className="font-medium text-primary/90">{limits.servers_limit}</span> used
                                                        </span>
                                                    )}
                                                </span>
                                            </button>
                                            {!primaryCluster && (
                                                <>
                                                    <div className="h-px bg-input/70" aria-hidden />
                                                    <button
                                                        type="button"
                                                        onClick={handleAddClusterClick}
                                                        className="w-full py-3 px-3 text-sm text-muted-foreground hover:bg-amber-500/10 transition-colors text-left focus:outline-none focus-visible:ring-2 focus-visible:ring-ring"
                                                    >
                                                        <span className="flex items-center justify-between gap-3">
                                                            <span className="flex items-center gap-2">
                                                                <span className="w-6 h-6 rounded-full border-2 border-amber-500/45 text-amber-400 flex items-center justify-center shrink-0" aria-hidden>
                                                                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="w-3.5 h-3.5">
                                                                        <line x1="12" y1="5" x2="12" y2="19" />
                                                                        <line x1="5" y1="12" x2="19" y2="12" />
                                                                    </svg>
                                                                </span>
                                                                <span className="font-medium">Add cluster</span>
                                                            </span>
                                                            {limits != null && (
                                                                <span className="text-xs">
                                                                    <span className="font-medium text-amber-400">{limits.clusters_used}</span> of{' '}
                                                                    <span className="font-medium text-amber-400">{limits.clusters_limit}</span> used
                                                                </span>
                                                            )}
                                                        </span>
                                                    </button>
                                                </>
                                            )}
                                        </div>
                                    )}
                                    {servers.map((server) => (
                                        <DashboardServerRow
                                            key={server.id}
                                            server={server}
                                            onEdit={setEditingServer}
                                            onClone={handleCloneServer}
                                        />
                                    ))}
                                </div>
                            )}
                            <p className="text-xs text-muted-foreground text-center pt-2">
                                Need more servers or clusters? You can request a higher limit for your use case —{' '}
                                <Link
                                    to="/contact"
                                    className="text-primary hover:text-accent underline focus:outline-none focus-visible:ring-2 focus-visible:ring-ring rounded"
                                >
                                    contact us
                                </Link>
                                .
                                <span className="block mt-1">
                                    Limits are per account and do not reset monthly. Delete a server or cluster to free a slot.
                                </span>
                            </p>
                        </>
                    )}
                </div>
            )}

            {deleteConfirm && (
                <div
                    className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50"
                    role="dialog"
                    aria-modal="true"
                    aria-labelledby="delete-dialog-title"
                >
                    <div className="card-elevated p-6 max-w-md w-full">
                        <h2 id="delete-dialog-title" className="text-lg font-semibold text-foreground mb-2">
                            Delete server?
                        </h2>
                        <p className="text-muted-foreground mb-6">
                            “{deleteConfirm.name}” will be removed from the directory. This cannot
                            be undone.
                        </p>
                        <div className="flex gap-2 justify-end">
                            <Button
                                type="button"
                                variant="secondary"
                                onClick={() => setDeleteConfirm(null)}
                                className="min-h-[44px]"
                                aria-label="Cancel deletion"
                            >
                                Cancel
                            </Button>
                            <Button
                                type="button"
                                variant="danger"
                                onClick={() => handleDeleteServer(deleteConfirm)}
                                className="min-h-[44px]"
                                aria-label="Confirm delete server"
                            >
                                Delete
                            </Button>
                        </div>
                    </div>
                </div>
            )}

            {deleteClusterConfirm && (
                <div
                    className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50"
                    role="dialog"
                    aria-modal="true"
                    aria-labelledby="delete-cluster-dialog-title"
                >
                    <div className="card-elevated p-6 max-w-md w-full">
                        <h2 id="delete-cluster-dialog-title" className="text-lg font-semibold text-foreground mb-2">
                            Delete cluster?
                        </h2>
                        <p className="text-muted-foreground mb-6">
                            “{deleteClusterConfirm.name}” will be removed. Servers in this cluster will keep their data but will no longer be linked to a cluster. This cannot be undone.
                        </p>
                        <div className="flex gap-2 justify-end">
                            <Button
                                type="button"
                                variant="secondary"
                                onClick={() => setDeleteClusterConfirm(null)}
                                className="min-h-[44px]"
                                aria-label="Cancel cluster deletion"
                            >
                                Cancel
                            </Button>
                            <Button
                                type="button"
                                variant="danger"
                                onClick={() => handleDeleteCluster()}
                                className="min-h-[44px]"
                                aria-label="Confirm delete cluster"
                            >
                                Delete
                            </Button>
                        </div>
                    </div>
                </div>
            )}

            <TermsAcceptanceModal
                open={showServerListingTermsModal}
                agreed={serverListingTermsAgreed}
                onAgreedChange={setServerListingTermsAgreed}
                onContinue={handleServerListingTermsContinue}
                onCancel={() => {
                    setShowServerListingTermsModal(false)
                    setServerListingTermsAgreed(false)
                }}
                continueLabel="I agree — continue to add server"
                loading={serverListingTermsLoading}
            />

            {/* Your Clusters: create, edit, delete, and link to key generation below */}
            <section
                className="rounded-xl border border-input bg-background-elevated p-4 shadow-lg shadow-black/40 mt-4"
                aria-labelledby="clusters-heading"
            >
                <h2 id="clusters-heading" className="text-xl font-semibold text-foreground mb-2">
                    Your Clusters
                </h2>
                {limits != null && (
                    <p className="text-xs text-muted-foreground mb-2">
                        <span className="font-medium text-primary/90">{limits.clusters_used}</span> of{' '}
                        <span className="font-medium text-primary/90">{limits.clusters_limit}</span> clusters used
                    </p>
                )}

                {(showCreateClusterForm || editingCluster) && (
                    <div className="rounded-lg border border-input bg-background/60 p-4 mb-4">
                        <h3 className="text-base font-medium text-foreground mb-3">
                            {editingCluster ? 'Edit cluster' : 'Create cluster'}
                        </h3>
                        <div className="space-y-3 max-w-md">
                            <div>
                                <label htmlFor="cluster-name" className="label-tek">Name</label>
                                <input
                                    id="cluster-name"
                                    type="text"
                                    value={clusterFormName}
                                    onChange={(e) => setClusterFormName(e.target.value)}
                                    placeholder="My Cluster"
                                    className="input-tek w-full"
                                />
                            </div>
                            <div>
                                <label htmlFor="cluster-slug" className="label-tek">Cluster link</label>
                                <div className="flex flex-wrap items-center gap-2 mb-1">
                                    <p className="text-xs text-muted-foreground">
                                        Choose your cluster page URL on ASASelfHosted:
                                    </p>
                                    <code className="bg-muted px-1 py-0.5 rounded font-mono text-[11px] break-all">
                                        {clusterUrlPrefix}{clusterFormSlug.trim() || '<url-name>'}
                                    </code>
                                    <Button
                                        type="button"
                                        variant="ghost"
                                        size="sm"
                                        className="h-6 px-1.5 text-xs"
                                        disabled={!clusterFormSlug.trim()}
                                        onClick={() => copyToClipboard('cluster-link-form', `${clusterUrlPrefix}${clusterFormSlug.trim()}`)}
                                        title={clusterFormSlug.trim() ? 'Copy full cluster link' : 'Enter a URL name to copy'}
                                    >
                                        {copiedLabel === 'cluster-link-form' ? 'Copied!' : 'Copy link'}
                                    </Button>
                                </div>
                                <input
                                    id="cluster-slug"
                                    type="text"
                                    value={clusterFormSlug}
                                    onChange={(e) => setClusterFormSlug(e.target.value.toLowerCase().replace(/\s+/g, '-'))}
                                    placeholder="url-name (lowercase, hyphens)"
                                    className="input-tek w-full"
                                />
                                <p className="text-xs text-muted-foreground mt-1">
                                    Use lowercase letters, numbers, and hyphens. Example: <code className="bg-muted px-1 py-0.5 rounded font-mono text-[11px]">my-pve-cluster</code>
                                </p>
                            </div>
                            <div>
                                <label htmlFor="cluster-visibility" className="label-tek">Visibility</label>
                                <select
                                    id="cluster-visibility"
                                    value={clusterFormVisibility}
                                    onChange={(e) => setClusterFormVisibility(e.target.value as 'public' | 'unlisted')}
                                    className="input-tek"
                                >
                                    <option value="public">Public (listed in directory)</option>
                                    <option value="unlisted">Unlisted (only with link)</option>
                                </select>
                            </div>
                            <div className="flex gap-2">
                                <Button
                                    type="button"
                                    onClick={editingCluster ? handleUpdateCluster : handleCreateCluster}
                                    disabled={!clusterFormName.trim() || !clusterFormSlug.trim()}
                                >
                                    {editingCluster ? 'Save' : 'Create'}
                                </Button>
                                <Button
                                    type="button"
                                    variant="secondary"
                                    onClick={() => {
                                        setShowCreateClusterForm(false)
                                        setEditingCluster(null)
                                        setClusterFormName('')
                                        setClusterFormSlug('')
                                        setClusterFormVisibility('public')
                                        setCrudError(null)
                                    }}
                                >
                                    Cancel
                                </Button>
                            </div>
                        </div>
                    </div>
                )}

                {!showCreateClusterForm && !editingCluster && (
                    <>
                        {!atClusterLimit && (
                            <Button
                                type="button"
                                variant="secondary"
                                size="sm"
                                className="mb-4"
                                onClick={() => {
                                    setShowCreateClusterForm(true)
                                    setClusterFormName('')
                                    setClusterFormSlug('')
                                    setClusterFormVisibility('public')
                                }}
                            >
                                Create cluster
                            </Button>
                        )}
                        {(clusters as Cluster[]).length === 0 ? (
                            <p className="text-sm text-muted-foreground">
                                No clusters yet. Create one to group servers; then a <strong>Generate key</strong> button will appear here and in &quot;Agent verification setup&quot; below for that cluster.
                            </p>
                        ) : (
                            <ul className="space-y-2">
                                {(clusters as Cluster[]).map((cluster) => (
                                    <li
                                        key={cluster.id}
                                        className="rounded-lg border border-input bg-background/60 p-3 space-y-2"
                                    >
                                        <div className="flex flex-wrap items-center gap-2">
                                            <span className="font-medium text-foreground">{cluster.name}</span>
                                            <span className="text-xs text-muted-foreground">({cluster.slug})</span>
                                            <span className="text-xs text-muted-foreground capitalize">{cluster.visibility}</span>
                                        </div>
                                        <div className="flex flex-wrap items-center gap-x-3 gap-y-1 text-xs">
                                            <span className="text-muted-foreground">Cluster ID</span>
                                            <Button type="button" variant="ghost" size="sm" className="h-6 px-1.5 text-xs" onClick={() => copyToClipboard(`cid-${cluster.id}`, cluster.id)}>
                                                {copiedLabel === `cid-${cluster.id}` ? 'Copied!' : 'Copy'}
                                            </Button>
                                            <span className="text-muted-foreground">Link</span>
                                            <Button
                                                type="button"
                                                variant="ghost"
                                                size="sm"
                                                className="h-6 px-1.5 text-xs"
                                                onClick={() => copyToClipboard(`clink-${cluster.id}`, `${clusterUrlPrefix}${cluster.slug}`)}
                                                title="Copy full cluster link"
                                            >
                                                {copiedLabel === `clink-${cluster.id}` ? 'Copied!' : 'Copy'}
                                            </Button>
                                            <span className="text-muted-foreground">Key v{cluster.key_version}</span>
                                            <Button type="button" variant="ghost" size="sm" className="h-6 px-1.5 text-xs" onClick={() => copyToClipboard(`kv-${cluster.id}`, String(cluster.key_version))}>
                                                {copiedLabel === `kv-${cluster.id}` ? 'Copied!' : 'Copy'}
                                            </Button>
                                            {cluster.public_key_ed25519 && (
                                                <>
                                                    <span className="text-muted-foreground">Public key</span>
                                                    <Button type="button" variant="ghost" size="sm" className="h-6 px-1.5 text-xs" onClick={() => copyToClipboard(`pk-${cluster.id}`, cluster.public_key_ed25519!)}>
                                                        {copiedLabel === `pk-${cluster.id}` ? 'Copied!' : 'Copy'}
                                                    </Button>
                                                </>
                                            )}
                                        </div>
                                        <div className="flex flex-wrap items-center gap-2">
                                            <span className="text-xs text-muted-foreground">Key:</span>
                                            <Button
                                                type="button"
                                                variant="secondary"
                                                size="sm"
                                                disabled={keyGeneratingClusterId === cluster.id}
                                                onClick={async () => {
                                                    setKeyGeneratingClusterId(cluster.id)
                                                    setKeyResult(null)
                                                    try {
                                                        const res = await generateClusterKeys(cluster.id)
                                                        setKeyResult(res)
                                                        queryClient.invalidateQueries({ queryKey: ['my-clusters'] })
                                                    } catch {
                                                        setCrudError('Failed to generate keys. Please try again.')
                                                    } finally {
                                                        setKeyGeneratingClusterId(null)
                                                    }
                                                }}
                                                title={cluster.public_key_ed25519 ? 'Generate a new key pair (previous private key will stop working)' : 'Generate Ed25519 key pair for agent authentication'}
                                            >
                                                {cluster.public_key_ed25519 ? 'Rotate key' : 'Generate key'}
                                            </Button>
                                            <Button
                                                type="button"
                                                variant="secondary"
                                                size="sm"
                                                onClick={() => openAssignAllConfirm(cluster)}
                                                title="Assign all of your servers to this cluster"
                                            >
                                                Set for all servers
                                            </Button>
                                            <Button
                                                type="button"
                                                variant="ghost"
                                                size="sm"
                                                onClick={() => {
                                                    setEditingCluster(cluster)
                                                    setClusterFormName(cluster.name)
                                                    setClusterFormSlug(cluster.slug)
                                                    setClusterFormVisibility(cluster.visibility)
                                                }}
                                            >
                                                Edit
                                            </Button>
                                            <Button
                                                type="button"
                                                variant="danger"
                                                size="sm"
                                                className="ml-auto"
                                                onClick={() => setDeleteClusterConfirm(cluster)}
                                            >
                                                Delete
                                            </Button>
                                        </div>
                                    </li>
                                ))}
                            </ul>
                        )}
                    </>
                )}
            </section>

            {assignAllConfirm && (
                <div
                    className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50"
                    role="dialog"
                    aria-modal="true"
                    aria-labelledby="assign-all-dialog-title"
                >
                    <div className="card-elevated p-6 max-w-md w-full">
                        <h2 id="assign-all-dialog-title" className="text-lg font-semibold text-foreground mb-2">
                            Set cluster for all servers?
                        </h2>
                        <p className="text-muted-foreground mb-4">
                            This will assign your servers to <strong>{assignAllConfirm.name}</strong>.
                        </p>
                        <div className="rounded-md border border-input bg-background/60 p-3 text-sm text-muted-foreground mb-4">
                            {assignAllLoading && <p>Loading preview…</p>}
                            {!assignAllLoading && assignAllPreview && (
                                <ul className="space-y-1">
                                    <li><strong className="text-foreground">{assignAllPreview.total_owner_servers}</strong> total servers</li>
                                    <li><strong className="text-foreground">{assignAllPreview.already_in_cluster}</strong> already in this cluster</li>
                                    <li><strong className="text-foreground">{assignAllPreview.unclustered}</strong> unclustered</li>
                                    <li><strong className="text-foreground">{assignAllPreview.in_other_cluster}</strong> in another cluster</li>
                                    <li className="pt-1"><strong className="text-foreground">{assignAllPreview.would_change}</strong> would change</li>
                                </ul>
                            )}
                        </div>

                        <label className="flex items-center gap-2 text-sm text-foreground mb-6">
                            <input
                                type="checkbox"
                                checked={assignAllOnlyUnclustered}
                                onChange={(e) => setAssignAllOnlyUnclustered(e.target.checked)}
                                className="h-4 w-4 rounded border-input bg-background shadow-sm focus:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-1"
                            />
                            Only assign servers that have no cluster
                        </label>

                        <div className="flex gap-2 justify-end">
                            <Button
                                type="button"
                                variant="secondary"
                                onClick={() => {
                                    setAssignAllConfirm(null)
                                    setAssignAllPreview(null)
                                    setAssignAllOnlyUnclustered(false)
                                }}
                                className="min-h-[44px]"
                            >
                                Cancel
                            </Button>
                            <Button
                                type="button"
                                variant="primary"
                                disabled={assignAllLoading}
                                onClick={async () => {
                                    setAssignAllLoading(true)
                                    setCrudError(null)
                                    try {
                                        await assignAllServersToCluster(assignAllConfirm.id, { only_unclustered: assignAllOnlyUnclustered })
                                        invalidate()
                                        invalidateClustersAndLimits()
                                        setAssignAllConfirm(null)
                                        setAssignAllPreview(null)
                                        setAssignAllOnlyUnclustered(false)
                                    } catch {
                                        setCrudError('Failed to assign servers. Please try again.')
                                    } finally {
                                        setAssignAllLoading(false)
                                    }
                                }}
                                className="min-h-[44px]"
                            >
                                Apply
                            </Button>
                        </div>
                    </div>
                </div>
            )}

            <section
                className="rounded-xl border border-input bg-background-elevated p-4 shadow-lg shadow-black/40 mt-4"
                aria-labelledby="agent-setup-heading"
                title="Heartbeats are only accepted for self-hosted servers. Player data will require in-game consent when that feature is implemented."
            >
                <h2 id="agent-setup-heading" className="text-xl font-semibold text-foreground mb-4">
                    Agent verification setup
                </h2>
                <p className="text-muted-foreground mb-4">
                    To verify your server and auto-update your server status, use the local-host agent (or ASA
                    Server API plugin) to send heartbeats. Generate <strong>cluster</strong> keys in <strong>&quot;Your Clusters&quot;</strong> above (each cluster has a Generate/Rotate key button). For per-server keys, use the <strong>Agent key</strong> section on the Create/Edit server page.
                </p>

                <div className="rounded-lg border border-input bg-background/60 p-3 mb-4 space-y-2">
                    <p className="text-sm font-medium text-foreground mb-2">For agent config (copy these)</p>
                    <div className="flex flex-wrap items-center gap-x-4 gap-y-2 text-sm">
                        <span className="text-muted-foreground">API Base:</span>
                        <code className="bg-muted px-1.5 py-0.5 rounded font-mono text-xs break-all">{API_BASE_URL}</code>
                        <Button type="button" variant="ghost" size="sm" className="h-7 text-xs" onClick={() => copyToClipboard('api-base', API_BASE_URL)}>
                            {copiedLabel === 'api-base' ? 'Copied!' : 'Copy'}
                        </Button>
                    </div>
                    <div className="flex flex-wrap items-center gap-x-4 gap-y-2 text-sm">
                        <span className="text-muted-foreground">Heartbeat URL:</span>
                        <code className="bg-muted px-1.5 py-0.5 rounded font-mono text-xs break-all">{API_BASE_URL}{HEARTBEAT_PATH}</code>
                        <Button type="button" variant="ghost" size="sm" className="h-7 text-xs" onClick={() => copyToClipboard('heartbeat-url', `${API_BASE_URL}${HEARTBEAT_PATH}`)}>
                            {copiedLabel === 'heartbeat-url' ? 'Copied!' : 'Copy'}
                        </Button>
                    </div>
                </div>

                {keyResult && (
                    <div className="mb-4 p-4 rounded-lg border-2 border-primary/50 bg-primary/5">
                        <p className="text-sm font-medium text-foreground mb-2">Private key (copy now — we won&apos;t show this again)</p>
                        <div className="flex flex-wrap items-center gap-2">
                            <code className="flex-1 min-w-0 text-xs break-all bg-muted px-2 py-2 rounded">
                                {keyResult.private_key}
                            </code>
                            <Button
                                type="button"
                                variant="secondary"
                                size="sm"
                                onClick={() => navigator.clipboard.writeText(keyResult.private_key)}
                            >
                                Copy
                            </Button>
                        </div>
                        <p className="text-sm text-muted-foreground mt-2">{keyResult.warning}</p>
                        <p className="text-sm text-foreground mt-1">Key saved. Use this private key in your agent.</p>
                        <Button
                            type="button"
                            variant="ghost"
                            size="sm"
                            className="mt-2"
                            onClick={() => setKeyResult(null)}
                        >
                            Dismiss
                        </Button>
                    </div>
                )}

                <p className="text-sm text-muted-foreground mb-2">
                    Cluster keys: the public key is stored on your cluster; put the private key in your agent config. Server keys (from Edit server) override the cluster key for that server. Point the agent at the heartbeat URL above. Status can be set manually until agent verification is connected.
                </p>
                <p className="text-sm text-primary/90 font-medium">
                    Nothing is collected until you complete in-game consent (when implemented). Heartbeats are only accepted for self-hosted servers.
                </p>
            </section>

            <section
                className="rounded-xl border border-input bg-background-elevated p-4 shadow-lg shadow-black/40 mt-4"
                aria-labelledby="privacy-consent-heading"
            >
                <h2 id="privacy-consent-heading" className="text-xl font-semibold text-foreground mb-2">
                    Privacy &amp; Consent (In-Game)
                </h2>
                <p className="text-muted-foreground text-sm mb-2">
                    Data collection requires consent in-game. The platform cannot enable permissions remotely or collect data by default.
                </p>
                <p className="text-sm mb-2">
                    <Link to="/consent" className="text-primary hover:text-accent underline focus:outline-none focus-visible:ring-2 focus-visible:ring-ring rounded">
                        Consent page
                    </Link>
                    — how consent works and your current consent state.
                </p>
                <p className="text-xs text-muted-foreground">
                    Advanced controls (e.g. revoke scope, export) — Coming soon.
                </p>
                <p className="text-xs text-muted-foreground mt-3 pt-3 border-t border-input/60">
                    Need to delete your account? <Link to="/data-rights" className="text-primary hover:text-accent underline focus:outline-none focus-visible:ring-2 focus-visible:ring-ring rounded">Data Rights page</Link>.
                </p>
            </section>
        </div>
    )
}
