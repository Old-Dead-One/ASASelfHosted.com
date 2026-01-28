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
import { useMyServers, useInvalidateMyServers } from '@/hooks/useMyServers'
import {
    createServer,
    updateServer,
    deleteServer,
    APIErrorResponse,
} from '@/lib/api'
import { Button } from '@/components/ui/Button'
import { ErrorMessage } from '@/components/ui/ErrorMessage'
import { LoadingSpinner } from '@/components/ui/LoadingSpinner'
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
    const body: Record<string, unknown> = {
        name: data.name.trim(),
        description: data.description?.trim() || null,
        cluster_id: data.cluster_id?.trim() || null,
        map_name: data.map_name?.trim() || null,
        join_address: data.join_address?.trim() || null,
        join_password: data.join_password?.trim() || null,
        join_instructions_pc: data.join_instructions_pc?.trim() || null,
        join_instructions_console: data.join_instructions_console?.trim() || null,
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
    const body: Record<string, unknown> = {
        name: data.name.trim(),
        description: data.description?.trim() || null,
        cluster_id: data.cluster_id?.trim() || null,
        map_name: data.map_name?.trim() || null,
        join_address: data.join_address?.trim() || null,
        join_password: data.join_password?.trim() || null,
        join_instructions_pc: data.join_instructions_pc?.trim() || null,
        join_instructions_console: data.join_instructions_console?.trim() || null,
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

function serverToFormData(s: DashboardServer): Partial<ServerFormData> {
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
        name: s.name,
        description: s.description ?? '',
        map_name: s.map_name ?? '',
        join_address: s.join_address ?? '',
        join_password: s.join_password ?? '',
        join_instructions_pc: s.join_instructions_pc ?? '',
        join_instructions_console: s.join_instructions_console ?? '',
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
    const invalidate = useInvalidateMyServers()

    const [showCreateForm, setShowCreateForm] = useState(false)
    const [editingServer, setEditingServer] = useState<DashboardServer | null>(null)
    const [deleteConfirm, setDeleteConfirm] = useState<DashboardServer | null>(null)
    const [crudError, setCrudError] = useState<string | null>(null)

    const servers = (myServers?.data ?? []) as DashboardServer[]
    const showList = !showCreateForm && !editingServer

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
                throw err
            }
        },
        [invalidate]
    )

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

    return (
        <div className="py-8">
            <div className="mb-4">
                <div className="mb-2">
                    <h1 className="text-3xl font-bold text-foreground">Dashboard</h1>
                </div>
                <p className="text-muted-foreground">
                    Welcome back, {user?.email ?? 'User'}. <br /> Manage your servers here.
                </p>
            </div>

            {crudError && (
                <div className="mb-6">
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
                        Create New Server
                    </h2>
                    <p className="text-sm text-muted-foreground mb-6">
                        Only name and description are saved for now. More fields when the backend
                        supports them.
                    </p>
                    <ServerForm
                        onSubmit={handleCreateServer}
                        onCancel={() => {
                            setShowCreateForm(false)
                            setCrudError(null)
                        }}
                    />
                </div>
            )}

            {editingServer && (
                <div className="rounded-xl border border-input bg-background-elevated p-4 shadow-lg shadow-black/40 mb-8">
                    <h2 className="text-xl font-semibold text-foreground mb-6">
                        Edit Server
                    </h2>
                    <ServerForm
                        initialData={serverToFormData(editingServer)}
                        onSubmit={handleUpdateServer}
                        onCancel={() => {
                            setEditingServer(null)
                            setCrudError(null)
                        }}
                        submitLabel="Save Changes"
                    />
                </div>
            )}

            {showList && (
                <div className="card-elevated p-4">
                    <h2 className="text-xl font-semibold text-foreground mb-4">Your Servers</h2>
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
                            {/* Carousel with Add Server card + server cards; -mx-4 trims outer padding so arrows sit closer to edges */}
                            <div className="-mx-4">
                                <DashboardServersCarousel
                                    servers={servers}
                                    onAddServer={() => setShowCreateForm(true)}
                                    onEdit={setEditingServer}
                                    onDelete={setDeleteConfirm}
                                />
                            </div>
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

            <section
                className="rounded-xl border border-input bg-background-elevated p-4 shadow-lg shadow-black/40 mt-8"
                aria-labelledby="agent-setup-heading"
            >
                <h2 id="agent-setup-heading" className="text-xl font-semibold text-foreground mb-4">
                    Agent verification setup
                </h2>
                <p className="text-muted-foreground mb-4">
                    To get verified status and automatic updates, use the local-host agent (or ASA
                    Server API plugin) to send heartbeats:
                </p>
                <ol className="list-decimal list-inside space-y-2 text-muted-foreground mb-4">
                    <li>Install the ASA Server API plugin (or run the local-host agent) on your server.</li>
                    <li>Generate an Ed25519 key pair (public + private).</li>
                    <li>Add your public key to this server’s listing (coming in a later update).</li>
                    <li>Configure the agent to send heartbeats to the API with signatures.</li>
                </ol>
                <p className="text-sm text-muted-foreground">
                    Status can be set manually above until agent verification is connected. Detailed
                    setup docs will be added when agent verification is fully wired.
                </p>
            </section>
        </div>
    )
}
