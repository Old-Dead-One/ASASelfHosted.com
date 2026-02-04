/**
 * Pinned cluster card (shown near servers list).
 *
 * Uses Tek card styling but with a cluster-accent color.
 */

import { useState } from 'react'
import { Button } from '@/components/ui/Button'
import { TekCardSurface } from '@/components/servers/TekCardSurface'
import type { Cluster } from '@/lib/api'

interface PinnedClusterCardProps {
    cluster: Cluster
    clustersUsed?: number
    clustersLimit?: number
    onManage: () => void
}

export function PinnedClusterCard({ cluster, clustersUsed, clustersLimit, onManage }: PinnedClusterCardProps) {
    const [copied, setCopied] = useState(false)
    const clusterLink =
        typeof window !== 'undefined'
            ? `${window.location.origin}/clusters/${cluster.slug}`
            : `/clusters/${cluster.slug}`

    return (
        <TekCardSurface
            className="w-full min-w-0 min-h-[260px] border-amber-500/35 hover:border-amber-400/60"
            contentClassName="p-3"
            style={{ ['--ring' as any]: 'var(--warning)' }}
        >
            <div className="flex flex-col flex-1 gap-2">
                <div className="min-w-0 flex-1">
                    <div className="flex items-center gap-2 mb-1">
                        <h3 className="text-base font-semibold text-foreground truncate">{cluster.name}</h3>
                        <span className="text-xs px-2 py-0.5 rounded bg-amber-500/10 text-amber-200 border border-amber-500/25 capitalize">
                            {cluster.visibility}
                        </span>
                    </div>

                    <p className="text-sm text-foreground/90 truncate">Cluster link</p>
                    <div className="flex items-center gap-2 mt-0.5">
                        <p className="text-xs text-muted-foreground truncate">{clusterLink}</p>
                        <Button
                            type="button"
                            variant="ghost"
                            size="sm"
                            className="h-6 px-1.5 text-xs shrink-0"
                            onClick={async () => {
                                try {
                                    await navigator.clipboard.writeText(clusterLink)
                                    setCopied(true)
                                    window.setTimeout(() => setCopied(false), 1500)
                                } catch {
                                    // no-op; user can select manually
                                }
                            }}
                            title="Copy full cluster link"
                        >
                            {copied ? 'Copied!' : 'Copy'}
                        </Button>
                    </div>

                    {clustersUsed != null && clustersLimit != null && (
                        <p className="text-xs text-muted-foreground mt-2">
                            <span className="font-medium text-amber-400">{clustersUsed}</span> of{' '}
                            <span className="font-medium text-amber-400">{clustersLimit}</span> used
                        </p>
                    )}
                </div>

                <div className="shrink-0 pt-2 border-t border-input/60 flex justify-center">
                    <Button
                        type="button"
                        variant="secondary"
                        size="sm"
                        className="border-amber-500/35 hover:border-amber-400/55 hover:bg-amber-500/10"
                        onClick={onManage}
                    >
                        Manage cluster
                    </Button>
                </div>
            </div>
        </TekCardSurface>
    )
}

