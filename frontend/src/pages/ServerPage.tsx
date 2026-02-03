/**
 * Server detail page.
 *
 * Displays detailed information about a single server.
 */

import { useState, useEffect, useRef } from 'react'
import { useParams, Navigate, Link } from 'react-router-dom'
import { useAuth } from '@/contexts/AuthContext'
import { useServer } from '@/hooks/useServers'
import { Badge } from '@/components/ui/Badge'
import { StatusBadge } from '@/components/ui/StatusBadge'
import { FavoriteButton } from '@/components/servers/FavoriteButton'
import { ErrorMessage } from '@/components/ui/ErrorMessage'
import { resolveMods, type ResolvedMod } from '@/lib/api'

// Padding size system: xs, sm (default), md, lg, xl, xxl
// xs: p-2 (8px), sm: p-3 (12px), md: p-4 (16px), lg: p-6 (24px), xl: p-8 (32px), xxl: p-12 (48px)
const CARD_PADDING = 'p-3' // Default: sm

function CopyableAddress({
    value,
    label,
    className,
}: {
    value: string
    label: string
    className?: string
}) {
    const [copied, setCopied] = useState(false)
    const timeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null)

    // Cleanup timeout on unmount
    useEffect(() => {
        return () => {
            if (timeoutRef.current) {
                clearTimeout(timeoutRef.current)
            }
        }
    }, [])

    const copy = async () => {
        // Clear any existing timeout
        if (timeoutRef.current) {
            clearTimeout(timeoutRef.current)
        }

        try {
            await navigator.clipboard.writeText(value)
            setCopied(true)
            timeoutRef.current = setTimeout(() => {
                setCopied(false)
                timeoutRef.current = null
            }, 2000)
        } catch {
            // Fallback for older browsers
            const textArea = document.createElement('textarea')
            textArea.value = value
            textArea.style.position = 'fixed'
            textArea.style.opacity = '0'
            document.body.appendChild(textArea)
            textArea.select()
            try {
                document.execCommand('copy')
                setCopied(true)
                timeoutRef.current = setTimeout(() => {
                    setCopied(false)
                    timeoutRef.current = null
                }, 2000)
            } catch {
                /* ignore */
            } finally {
                document.body.removeChild(textArea)
            }
        }
    }

    return (
        <div className={className}>
            <div className="flex items-center justify-between gap-2">
                <dt className="text-sm font-medium text-muted-foreground">{label}</dt>
                <button
                    type="button"
                    onClick={copy}
                    className="text-xs text-primary hover:text-accent transition-colors focus:outline-none focus:ring-2 focus:ring-ring rounded px-1 min-h-[32px]"
                    aria-label={`Copy ${label.toLowerCase()}`}
                    aria-live="polite"
                >
                    {copied ? 'Copied!' : 'Copy'}
                </button>
            </div>
            <dd className="text-sm text-foreground font-mono bg-muted p-1.5 rounded break-all">
                {value}
            </dd>
        </div>
    )
}

export function ServerPage() {
    const { serverId } = useParams<{ serverId: string }>()
    const { isAuthenticated } = useAuth()
    const { data: server, isLoading, error } = useServer(serverId || '')
    const [resolvedMods, setResolvedMods] = useState<Map<number, ResolvedMod>>(new Map())
    const [resolvingMods, setResolvingMods] = useState(false)

    // Resolve mod IDs to names when server data loads
    useEffect(() => {
        if (!server?.mod_list || server.mod_list.length === 0) {
            setResolvedMods(new Map())
            return
        }

        // Parse mod IDs from string array
        const modIds = server.mod_list
            .map((id) => {
                const parsed = parseInt(id.trim(), 10)
                return isNaN(parsed) || parsed <= 0 ? null : parsed
            })
            .filter((id): id is number => id !== null)

        if (modIds.length === 0) {
            setResolvedMods(new Map())
            return
        }

        // Resolve mod IDs to names
        setResolvingMods(true)
        resolveMods(modIds)
            .then((response) => {
                const modMap = new Map<number, ResolvedMod>()
                response.data.forEach((mod) => {
                    modMap.set(mod.mod_id, mod)
                })
                setResolvedMods(modMap)
            })
            .catch(() => {
                // Silently fail - mods will just show as IDs
                setResolvedMods(new Map())
            })
            .finally(() => {
                setResolvingMods(false)
            })
    }, [server?.mod_list])

    if (!serverId) {
        return <Navigate to="/404" replace />
    }

    if (isLoading) {
        return (
            <div className="py-8">
                <div className="mb-6">
                    <div className="h-4 w-24 bg-muted rounded animate-pulse" />
                </div>
                <div className="animate-pulse space-y-6">
                    <div className="space-y-3">
                        <div className="h-8 bg-muted rounded w-1/2" />
                        <div className="h-4 bg-muted rounded w-1/3" />
                        <div className="flex gap-2">
                            <div className="h-6 w-20 bg-muted rounded" />
                            <div className="h-6 w-16 bg-muted rounded" />
                        </div>
                    </div>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <div className="h-48 bg-muted rounded-lg" />
                        <div className="h-48 bg-muted rounded-lg" />
                    </div>
                </div>
            </div>
        )
    }

    if (error) {
        return (
            <div className="py-8">
                <div className="mb-6">
                    <Link
                        to="/"
                        className="text-sm text-muted-foreground hover:text-foreground transition-colors"
                    >
                        ← Back to directory
                    </Link>
                </div>
                <ErrorMessage
                    error={error}
                    title="Failed to load server"
                    onRetry={() => window.location.reload()}
                />
            </div>
        )
    }

    if (!server) {
        return (
            <div className="py-8">
                <div className="mb-6">
                    <Link
                        to="/"
                        className="text-sm text-muted-foreground hover:text-foreground transition-colors"
                    >
                        ← Back to directory
                    </Link>
                </div>
                <div className="text-center py-12">
                    <h1 className="text-2xl font-bold text-foreground mb-2">Server not found</h1>
                    <p className="text-muted-foreground mb-4">
                        The server you're looking for doesn't exist or has been removed.
                    </p>
                    <Link
                        to="/"
                        className="text-sm text-primary hover:text-accent transition-colors"
                    >
                        Browse all servers →
                    </Link>
                </div>
            </div>
        )
    }

    return (
        <div className="py-8">
            <div className="mb-6">
                <Link
                    to="/"
                    className="text-sm text-muted-foreground hover:text-foreground transition-colors focus:outline-none focus:ring-2 focus:ring-ring rounded px-2 py-1 inline-block min-h-[44px] flex items-center"
                    aria-label="Back to server directory"
                >
                    ← Back to directory
                </Link>
            </div>
            {/* Header */}
            <div className="mb-4">
                <div className="flex items-start justify-between gap-3 mb-3">
                    <div className="flex-1">
                        <div className="flex items-center gap-2 mb-1">
                            <h1 className="text-2xl font-bold text-foreground">{server.name}</h1>
                            <FavoriteButton
                                serverId={server.id}
                                favoriteCount={server.favorite_count}
                            />
                        </div>
                        {server.cluster_name && (
                            <p className="text-sm text-muted-foreground">
                                Cluster: {server.cluster_name}
                            </p>
                        )}
                    </div>
                    <div className="flex items-center gap-2 flex-wrap justify-end">
                        <StatusBadge status={server.effective_status ?? 'unknown'} />
                        {server.is_verified && <Badge type="verified" />}
                        {server.is_new && <Badge type="new" />}
                        {server.is_stable && <Badge type="stable" />}
                        {server.game_mode && <Badge type={server.game_mode} />}
                        {server.ruleset && <Badge type={server.ruleset} />}
                    </div>
                </div>

                {server.description && (
                    <p className="text-sm text-muted-foreground mb-2">{server.description}</p>
                )}
            </div>

            {/* Two-column card grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                <div className="relative overflow-hidden rounded-lg tek-border">
                    <div className="absolute inset-0 bg-tek-wall" aria-hidden />
                    <div className="absolute inset-0 tek-seam opacity-70 pointer-events-none" aria-hidden />
                    <div className={`relative ${CARD_PADDING} bg-background/65 backdrop-blur-[1px] flex flex-col h-full`}>
                        <h2 className="text-base font-semibold text-foreground mb-2">Server Details</h2>
                        <div className="grid grid-cols-1 md:grid-cols-[1fr_1.5fr] gap-4 flex-1 min-h-0">
                            <div>
                                <dl className="space-y-1">
                                    {server.map_name ? (
                                        <>
                                            <dt className="text-sm font-medium text-muted-foreground">Map</dt>
                                            <dd className="text-sm text-foreground font-mono">
                                                {server.map_name}
                                            </dd>
                                        </>
                                    ) : (
                                        <>
                                            <dt className="text-sm font-medium text-muted-foreground">Map</dt>
                                            <dd className="text-sm text-muted-foreground italic">Not specified</dd>
                                        </>
                                    )}
                                    {server.players_current !== null || server.players_capacity !== null ? (
                                        <>
                                            <dt className="text-sm font-medium text-muted-foreground">
                                                Players
                                            </dt>
                                            <dd className="text-sm text-foreground">
                                                {server.players_current !== null ? server.players_current : '?'}
                                                {server.players_capacity !== null &&
                                                    ` / ${server.players_capacity}`}
                                            </dd>
                                        </>
                                    ) : (
                                        <>
                                            <dt className="text-sm font-medium text-muted-foreground">
                                                Players
                                            </dt>
                                            <dd className="text-sm text-muted-foreground italic">Not available</dd>
                                        </>
                                    )}
                                    {server.uptime_percent !== null ? (
                                        <>
                                            <dt className="text-sm font-medium text-muted-foreground">
                                                Uptime (24h)
                                            </dt>
                                            <dd className="text-sm text-foreground">
                                                {server.uptime_percent.toFixed(1)}%
                                            </dd>
                                        </>
                                    ) : (
                                        <>
                                            <dt className="text-sm font-medium text-muted-foreground">
                                                Uptime (24h)
                                            </dt>
                                            <dd className="text-sm text-muted-foreground italic">Not available</dd>
                                        </>
                                    )}
                                    {server.quality_score !== null ? (
                                        <>
                                            <dt className="text-sm font-medium text-muted-foreground">
                                                Quality Score
                                            </dt>
                                            <dd className="text-sm text-foreground">
                                                {server.quality_score.toFixed(1)}
                                            </dd>
                                        </>
                                    ) : (
                                        <>
                                            <dt className="text-sm font-medium text-muted-foreground">
                                                Quality Score
                                            </dt>
                                            <dd className="text-sm text-muted-foreground italic">Not available</dd>
                                        </>
                                    )}
                                    {server.rates ? (
                                        <>
                                            <dt className="text-sm font-medium text-muted-foreground">Rates</dt>
                                            <dd className="text-sm text-foreground">{server.rates}</dd>
                                        </>
                                    ) : (
                                        <>
                                            <dt className="text-sm font-medium text-muted-foreground">Rates</dt>
                                            <dd className="text-sm text-muted-foreground italic">Not specified</dd>
                                        </>
                                    )}
                                    {server.wipe_info ? (
                                        <>
                                            <dt className="text-sm font-medium text-muted-foreground">Wipe Info</dt>
                                            <dd className="text-sm text-foreground whitespace-pre-line">
                                                {server.wipe_info}
                                            </dd>
                                        </>
                                    ) : (
                                        <>
                                            <dt className="text-sm font-medium text-muted-foreground">Wipe Info</dt>
                                            <dd className="text-sm text-muted-foreground italic">Not specified</dd>
                                        </>
                                    )}
                                    <div>
                                        <dt className="text-sm font-medium text-muted-foreground">Created At</dt>
                                        <dd className="text-sm text-foreground">
                                            {new Date(server.created_at).toLocaleString()}
                                        </dd>
                                    </div>
                                    <div>
                                        <dt className="text-sm font-medium text-muted-foreground">Updated At</dt>
                                        <dd className="text-sm text-foreground">
                                            {new Date(server.updated_at).toLocaleString()}
                                        </dd>
                                    </div>
                                </dl>
                            </div>
                            <div className="flex flex-col min-h-0 max-h-full">
                                <h3 className="text-sm font-semibold text-foreground mb-2">
                                    Mod List
                                    {resolvingMods && (
                                        <span className="ml-2 text-xs text-muted-foreground">(resolving...)</span>
                                    )}
                                </h3>
                                <div className="flex-1 overflow-y-auto overflow-x-auto min-h-0 max-h-full">
                                    {server.mod_list && server.mod_list.length > 0 ? (
                                        <ul className="list-disc list-inside space-y-1">
                                            {server.mod_list.map((modStr, idx) => {
                                                const modId = parseInt(modStr.trim(), 10)
                                                const resolvedMod = !isNaN(modId) && modId > 0 ? resolvedMods.get(modId) : null

                                                return (
                                                    <li key={idx} className="text-xs text-foreground font-mono whitespace-nowrap">
                                                        {resolvedMod ? resolvedMod.name : modStr}
                                                    </li>
                                                )
                                            })}
                                        </ul>
                                    ) : (
                                        <p className="text-xs text-muted-foreground italic">No mods listed</p>
                                    )}
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                {(server.join_address || server.join_password || server.discord_url || server.website_url || server.join_instructions_pc || server.join_instructions_console || server.is_pc !== null || server.is_console !== null || server.is_crossplay !== null) && (
                    <div className="relative overflow-hidden rounded-lg tek-border">
                        <div className="absolute inset-0 bg-tek-wall" aria-hidden />
                        <div className="absolute inset-0 tek-seam opacity-70 pointer-events-none" aria-hidden />
                        <div className={`relative ${CARD_PADDING} bg-background/65 backdrop-blur-[1px]`}>
                            <h2 className="text-base font-semibold text-foreground mb-2">
                                Join Instructions
                            </h2>
                            {(server.is_pc !== null || server.is_console !== null || server.is_crossplay !== null) && (
                                <div className="mb-3">
                                    <dt className="text-sm font-medium text-muted-foreground mb-1">Platform</dt>
                                    <dd className="text-sm text-foreground">
                                        {(() => {
                                            // Determine platform display: PC Only, Console Only, or Crossplay
                                            if (server.is_pc && server.is_console) {
                                                return 'Crossplay'
                                            } else if (server.is_pc) {
                                                return 'PC Only'
                                            } else if (server.is_console) {
                                                return 'Console Only'
                                            } else {
                                                return 'Not specified'
                                            }
                                        })()}
                                    </dd>
                                </div>
                            )}
                            {(server.discord_url || server.website_url) && (
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mb-3">
                                    {server.discord_url && (
                                        <div>
                                            <dt className="text-sm font-medium text-muted-foreground mb-0.5">Discord</dt>
                                            <dd className="text-sm">
                                                <a
                                                    href={server.discord_url}
                                                    target="_blank"
                                                    rel="noopener noreferrer"
                                                    className="text-primary hover:text-accent transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-ring rounded px-0.5 break-all"
                                                >
                                                    {server.discord_url}
                                                </a>
                                            </dd>
                                        </div>
                                    )}
                                    {server.website_url && (
                                        <div>
                                            <dt className="text-sm font-medium text-muted-foreground mb-0.5">Website</dt>
                                            <dd className="text-sm">
                                                <a
                                                    href={server.website_url}
                                                    target="_blank"
                                                    rel="noopener noreferrer"
                                                    className="text-primary hover:text-accent transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-ring rounded px-0.5 break-all"
                                                >
                                                    {server.website_url}
                                                </a>
                                            </dd>
                                        </div>
                                    )}
                                </div>
                            )}
                            {(server.join_address || (server.join_password && isAuthenticated)) && (
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mb-3">
                                    {server.join_address && (
                                        <div>
                                            <CopyableAddress value={server.join_address} label="Server Address" />
                                        </div>
                                    )}
                                    {server.join_password && isAuthenticated && (
                                        <div>
                                            <CopyableAddress value={server.join_password} label="Join Password" />
                                        </div>
                                    )}
                                </div>
                            )}
                            {(server.join_instructions_pc || server.join_instructions_console) && (
                                <div>
                                    <dt className="text-sm font-medium text-muted-foreground mb-1">
                                        Join Instructions
                                    </dt>
                                    <dd className="text-sm text-foreground whitespace-pre-line">
                                        {server.join_instructions_pc || server.join_instructions_console}
                                    </dd>
                                </div>
                            )}
                        </div>
                    </div>
                )}

                {/* Status & Monitoring */}
                <div className="relative overflow-hidden rounded-lg tek-border">
                    <div className="absolute inset-0 bg-tek-wall" aria-hidden />
                    <div className="absolute inset-0 tek-seam opacity-70 pointer-events-none" aria-hidden />
                    <div className={`relative ${CARD_PADDING} bg-background/65 backdrop-blur-[1px]`}>
                        <h2 className="text-base font-semibold text-foreground mb-2">Monitoring</h2>
                        <dl className="space-y-1">
                            {server.status_source ? (
                                <>
                                    <dt className="text-sm font-medium text-muted-foreground">Source</dt>
                                    <dd className="text-sm text-foreground capitalize">{server.status_source}</dd>
                                </>
                            ) : (
                                <>
                                    <dt className="text-sm font-medium text-muted-foreground">Source</dt>
                                    <dd className="text-sm text-muted-foreground italic">Not available</dd>
                                </>
                            )}
                            {server.confidence ? (
                                <>
                                    <dt className="text-sm font-medium text-muted-foreground">Confidence</dt>
                                    <dd className="text-sm text-foreground capitalize">{server.confidence}</dd>
                                </>
                            ) : (
                                <>
                                    <dt className="text-sm font-medium text-muted-foreground">Confidence</dt>
                                    <dd className="text-sm text-muted-foreground italic">Not available</dd>
                                </>
                            )}
                            {server.last_seen_at ? (
                                <>
                                    <dt className="text-sm font-medium text-muted-foreground">Last Update</dt>
                                    <dd className="text-sm text-foreground">
                                        {new Date(server.last_seen_at).toLocaleString()}
                                    </dd>
                                </>
                            ) : (
                                <>
                                    <dt className="text-sm font-medium text-muted-foreground">Last Update</dt>
                                    <dd className="text-sm text-muted-foreground italic">Never</dd>
                                </>
                            )}
                        </dl>
                    </div>
                </div>

                {/* Ranking */}
                {(server.rank_position !== null || server.rank_by !== null || server.rank_delta_24h !== null) && (
                    <div className="relative overflow-hidden rounded-lg tek-border">
                        <div className="absolute inset-0 bg-tek-wall" aria-hidden />
                        <div className="absolute inset-0 tek-seam opacity-70 pointer-events-none" aria-hidden />
                        <div className={`relative ${CARD_PADDING} bg-background/65 backdrop-blur-[1px]`}>
                            <h2 className="text-base font-semibold text-foreground mb-2">Ranking</h2>
                            <dl className="space-y-1">
                                {server.rank_position !== null ? (
                                    <>
                                        <dt className="text-sm font-medium text-muted-foreground">Rank Position</dt>
                                        <dd className="text-sm text-foreground">#{server.rank_position}</dd>
                                    </>
                                ) : (
                                    <>
                                        <dt className="text-sm font-medium text-muted-foreground">Rank Position</dt>
                                        <dd className="text-sm text-muted-foreground italic">Not ranked</dd>
                                    </>
                                )}
                                {server.rank_by ? (
                                    <>
                                        <dt className="text-sm font-medium text-muted-foreground">Ranked By</dt>
                                        <dd className="text-sm text-foreground capitalize">{server.rank_by}</dd>
                                    </>
                                ) : (
                                    <>
                                        <dt className="text-sm font-medium text-muted-foreground">Ranked By</dt>
                                        <dd className="text-sm text-muted-foreground italic">Not specified</dd>
                                    </>
                                )}
                                {server.rank_delta_24h !== null ? (
                                    <>
                                        <dt className="text-sm font-medium text-muted-foreground">Rank Change (24h)</dt>
                                        <dd className={`text-sm ${server.rank_delta_24h > 0 ? 'text-green-500' : server.rank_delta_24h < 0 ? 'text-red-500' : ''}`}>
                                            {server.rank_delta_24h > 0 ? '+' : ''}{server.rank_delta_24h}
                                        </dd>
                                    </>
                                ) : (
                                    <>
                                        <dt className="text-sm font-medium text-muted-foreground">Rank Change (24h)</dt>
                                        <dd className="text-sm text-muted-foreground italic">Not available</dd>
                                    </>
                                )}
                            </dl>
                        </div>
                    </div>
                )}

                {/* Cluster Info */}
                {server.cluster_id && (
                    <div className="relative overflow-hidden rounded-lg tek-border">
                        <div className="absolute inset-0 bg-tek-wall" aria-hidden />
                        <div className="absolute inset-0 tek-seam opacity-70 pointer-events-none" aria-hidden />
                        <div className={`relative ${CARD_PADDING} bg-background/65 backdrop-blur-[1px]`}>
                            <h2 className="text-base font-semibold text-foreground mb-2">Cluster Information</h2>
                            <dl className="space-y-1">
                                <div>
                                    <dt className="text-sm font-medium text-muted-foreground">Cluster ID</dt>
                                    <dd className="text-sm text-foreground font-mono text-xs break-all">
                                        {server.cluster_id}
                                    </dd>
                                </div>
                                {server.cluster_name ? (
                                    <>
                                        <dt className="text-sm font-medium text-muted-foreground">Cluster Name</dt>
                                        <dd className="text-sm text-foreground">{server.cluster_name}</dd>
                                    </>
                                ) : (
                                    <>
                                        <dt className="text-sm font-medium text-muted-foreground">Cluster Name</dt>
                                        <dd className="text-sm text-muted-foreground italic">Not specified</dd>
                                    </>
                                )}
                                {server.cluster_slug ? (
                                    <>
                                        <dt className="text-sm font-medium text-muted-foreground">Cluster Slug</dt>
                                        <dd className="text-sm text-foreground font-mono">{server.cluster_slug}</dd>
                                    </>
                                ) : (
                                    <>
                                        <dt className="text-sm font-medium text-muted-foreground">Cluster Slug</dt>
                                        <dd className="text-sm text-muted-foreground italic">Not specified</dd>
                                    </>
                                )}
                                {server.cluster_visibility ? (
                                    <>
                                        <dt className="text-sm font-medium text-muted-foreground">Cluster Visibility</dt>
                                        <dd className="text-sm text-foreground capitalize">{server.cluster_visibility}</dd>
                                    </>
                                ) : (
                                    <>
                                        <dt className="text-sm font-medium text-muted-foreground">Cluster Visibility</dt>
                                        <dd className="text-sm text-muted-foreground italic">Not specified</dd>
                                    </>
                                )}
                            </dl>
                        </div>
                    </div>
                )}
            </div>
        </div>
    )
}
