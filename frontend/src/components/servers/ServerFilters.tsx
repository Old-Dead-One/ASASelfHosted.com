/**
 * Server filters component.
 *
 * Provides UI for filtering servers by various criteria.
 */

import { useState, FormEvent, useEffect } from 'react'
import type { ServerStatus, VerificationMode, GameMode, Ruleset, SortOrder, RankBy, DirectoryView, TriState } from '@/types'
import { Button } from '@/components/ui/Button'

export interface ServerFilters {
    q?: string
    status?: ServerStatus
    mode?: VerificationMode
    game_mode?: GameMode
    ruleset?: Ruleset
    rank_by?: RankBy
    order?: SortOrder
    /** Page size (directory limit). Default 25. */
    limit?: number
    /** View mode: 'compact' (row) or 'card'. Default 'compact'. */
    view?: DirectoryView
    /** Filter by cluster association (any/true/false). true = has cluster, false = no cluster */
    is_cluster?: TriState
}

interface ServerFiltersProps {
    filters: ServerFilters
    onFiltersChange: (filters: ServerFilters) => void
}

export function ServerFilters({ filters, onFiltersChange }: ServerFiltersProps) {
    const [isOpen, setIsOpen] = useState(false)
    const [localFilters, setLocalFilters] = useState<ServerFilters>(filters)

    useEffect(() => {
        setLocalFilters(filters)
    }, [filters])

    const handleSubmit = (e: FormEvent) => {
        e.preventDefault()
        onFiltersChange(localFilters)
    }

    const handleReset = () => {
        const resetFilters: ServerFilters = {}
        setLocalFilters(resetFilters)
        onFiltersChange(resetFilters)
    }

    const hasActiveFilters = !!(
        filters.q ||
        filters.status ||
        filters.mode ||
        filters.game_mode ||
        filters.ruleset ||
        filters.is_cluster
    )

    return (
        <div className="mb-6">
            <div className="flex items-center justify-between mb-4">
                <Button
                    type="button"
                    variant="ghost"
                    size="sm"
                    onClick={() => setIsOpen(!isOpen)}
                    className="min-h-[44px]"
                    aria-expanded={isOpen}
                    aria-controls="filters-panel"
                >
                    {isOpen ? 'Hide Filters' : 'Show Filters'}
                </Button>
                {hasActiveFilters && (
                    <Button
                        type="button"
                        variant="ghost"
                        size="sm"
                        onClick={handleReset}
                        className="text-xs min-h-[44px]"
                        aria-label="Clear all filters"
                    >
                        Clear all
                    </Button>
                )}
            </div>

            {isOpen && (
                <form
                    id="filters-panel"
                    onSubmit={handleSubmit}
                    className="card-elevated p-4 space-y-3"
                >
                    {/* Search */}
                    <div>
                        <label htmlFor="search" className="label-tek">Search</label>
                        <input
                            id="search"
                            type="text"
                            value={localFilters.q || ''}
                            onChange={(e) => setLocalFilters({ ...localFilters, q: e.target.value || undefined })}
                            placeholder="Search servers..."
                            className="input-tek"
                        />
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3">
                        {/* Status Filter */}
                        <div>
                        <label htmlFor="status" className="label-tek">
                            Status
                        </label>
                            <select
                                id="status"
                                value={localFilters.status || ''}
                                onChange={(e) =>
                                    setLocalFilters({
                                        ...localFilters,
                                        status: (e.target.value || undefined) as ServerStatus | undefined,
                                    })
                                }
                                className="input-tek"
                            >
                                <option value="">All</option>
                                <option value="online">Online</option>
                                <option value="offline">Offline</option>
                                <option value="unknown">Unknown</option>
                            </select>
                        </div>

                        {/* Verification Mode */}
                        <div>
                            <label htmlFor="mode" className="label-tek">
                                Verification
                            </label>
                            <select
                                id="mode"
                                value={localFilters.mode || ''}
                                onChange={(e) =>
                                    setLocalFilters({
                                        ...localFilters,
                                        mode: (e.target.value || undefined) as VerificationMode | undefined,
                                    })
                                }
                                className="input-tek"
                            >
                                <option value="">All</option>
                                <option value="manual">Manual</option>
                                <option value="verified">Verified</option>
                            </select>
                        </div>

                        {/* Game Mode */}
                        <div>
                            <label htmlFor="game_mode" className="label-tek">
                                Game Mode
                            </label>
                            <select
                                id="game_mode"
                                value={localFilters.game_mode || ''}
                                onChange={(e) =>
                                    setLocalFilters({
                                        ...localFilters,
                                        game_mode: (e.target.value || undefined) as GameMode | undefined,
                                    })
                                }
                                className="input-tek"
                            >
                                <option value="">All</option>
                                <option value="pvp">PvP</option>
                                <option value="pve">PvE</option>
                                <option value="pvpve">PvPvE</option>
                            </select>
                        </div>

                        {/* Ruleset */}
                        <div>
                            <label htmlFor="ruleset" className="label-tek">
                                Ruleset
                            </label>
                            <select
                                id="ruleset"
                                value={localFilters.ruleset || ''}
                                onChange={(e) =>
                                    setLocalFilters({
                                        ...localFilters,
                                        ruleset: (e.target.value || undefined) as Ruleset | undefined,
                                    })
                                }
                                className="input-tek"
                            >
                                <option value="">All</option>
                                <option value="vanilla">Vanilla</option>
                                <option value="vanilla_qol">Vanilla QoL</option>
                                <option value="boosted">Boosted</option>
                                <option value="modded">Modded</option>
                            </select>
                        </div>

                        {/* Cluster Filter */}
                        <div>
                            <label htmlFor="is_cluster" className="label-tek">
                                Cluster
                            </label>
                            <select
                                id="is_cluster"
                                value={localFilters.is_cluster || 'any'}
                                onChange={(e) =>
                                    setLocalFilters({
                                        ...localFilters,
                                        is_cluster: (e.target.value === 'any' ? undefined : e.target.value) as TriState | undefined,
                                    })
                                }
                                className="input-tek"
                            >
                                <option value="any">All</option>
                                <option value="true">Has Cluster</option>
                                <option value="false">Standalone</option>
                            </select>
                        </div>
                    </div>

                    {/* Sort */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                        <div>
                            <label htmlFor="rank_by" className="label-tek">
                                Sort By
                            </label>
                            <select
                                id="rank_by"
                                value={localFilters.rank_by || 'updated'}
                                onChange={(e) =>
                                    setLocalFilters({
                                        ...localFilters,
                                        rank_by: (e.target.value || 'updated') as RankBy,
                                    })
                                }
                                className="input-tek"
                            >
                                <option value="updated">Last Updated</option>
                                <option value="new">Newest</option>
                                <option value="favorites">Most Favorited</option>
                                <option value="players">Most Players</option>
                                <option value="quality">Quality Score</option>
                                <option value="uptime">Uptime</option>
                            </select>
                        </div>

                        <div>
                            <label htmlFor="order" className="label-tek">
                                Order
                            </label>
                            <select
                                id="order"
                                value={localFilters.order || 'desc'}
                                onChange={(e) =>
                                    setLocalFilters({
                                        ...localFilters,
                                        order: (e.target.value || 'desc') as SortOrder,
                                    })
                                }
                                className="input-tek"
                            >
                                <option value="desc">Descending</option>
                                <option value="asc">Ascending</option>
                            </select>
                        </div>
                    </div>

                    <div className="flex gap-2 pt-1">
                        <Button type="submit" variant="primary" size="sm" className="min-h-[44px]">
                            Apply Filters
                        </Button>
                        <Button type="button" variant="secondary" size="sm" onClick={handleReset} className="min-h-[44px]" aria-label="Reset all filters">
                            Reset
                        </Button>
                    </div>
                </form>
            )}
        </div>
    )
}
