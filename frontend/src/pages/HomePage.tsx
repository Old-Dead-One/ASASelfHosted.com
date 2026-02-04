/**
 * Home page component.
 *
 * Main landing page with server listings and carousel.
 */

import { useState } from 'react'
import { ServerList } from '@/components/servers/ServerList'
import { ServerFilters, type ServerFilters as ServerFiltersType } from '@/components/servers/ServerFilters'
import { SpotlightCarousel } from '@/components/servers/SpotlightCarousel'
import { Button } from '@/components/ui/Button'
import { useServers } from '@/hooks/useServers'
import type { DirectoryView } from '@/types'

export function HomePage({ showSpotlight = true }: { showSpotlight?: boolean } = {}) {
    const [filters, setFilters] = useState<ServerFiltersType>({ view: 'compact', limit: 24 })
    const { total } = useServers(filters)

    return (
        <div className="py-8">
            <div className="mb-4 text-center">
                <h1 className="text-4xl font-bold text-foreground mb-4">
                    ASASelfHosted
                </h1>
                <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
                    Public registry for self-hosted Ark: Survival Ascended servers
                </p>
            </div>
            {/* Spotlight Carousel — above directory */}
            {showSpotlight && (
                <section className="mb-4" aria-label="Spotlight servers">
                    <SpotlightCarousel />
                </section>
            )}
            {/* Server Directory */}
            <section aria-labelledby="directory-heading" className="mb-4">
                <ServerFilters filters={filters} onFiltersChange={setFilters} />
                <div className="flex items-center justify-between gap-2 sm:gap-4 flex-wrap mb-4">
                    <div className="flex items-center gap-2 sm:gap-4 flex-wrap">
                        <div className="flex items-center gap-2">
                            <label htmlFor="per-page" className="text-sm text-muted-foreground whitespace-nowrap">
                                Per page:
                            </label>
                            <select
                                id="per-page"
                                value={filters.limit ?? 24}
                                onChange={(e) => {
                                    const limit = Number(e.target.value)
                                    setFilters({ ...filters, limit })
                                }}
                                className="input-tek min-h-[40px] w-auto min-w-[4rem]"
                                aria-label="Servers per page"
                            >
                                <option value={24}>24</option>
                                <option value={30}>30</option>
                                <option value={36}>36</option>
                            </select>
                        </div>
                        <div className="flex items-center gap-2">
                            <span className="text-sm text-muted-foreground whitespace-nowrap">View:</span>
                            <Button
                                type="button"
                                variant="secondary"
                                size="sm"
                                onClick={() => {
                                    const currentView = filters.view ?? 'compact'
                                    const newView: DirectoryView = currentView === 'compact' ? 'card' : 'compact'
                                    setFilters({ ...filters, view: newView })
                                }}
                                className="min-h-[40px]"
                                aria-label={`Switch to ${(filters.view ?? 'compact') === 'compact' ? 'card' : 'row'} view`}
                            >
                                {(filters.view ?? 'compact') === 'compact' ? 'Card' : 'Row'}
                            </Button>
                        </div>
                    </div>
                    {total !== undefined && (
                        <span className="text-sm text-muted-foreground whitespace-nowrap" aria-live="polite">
                            {total} {total === 1 ? 'server' : 'servers'}
                        </span>
                    )}
                </div>
                <ServerList filters={filters} />
            </section>
        </div>
    )
}
