/**
 * Home page component.
 *
 * Main landing page with server listings and carousel.
 */

import { useState } from 'react'
import { ServerList } from '@/components/servers/ServerList'
import { ServerFilters, type ServerFilters as ServerFiltersType } from '@/components/servers/ServerFilters'
import { NewbieCarousel } from '@/components/servers/NewbieCarousel'
import { Button } from '@/components/ui/Button'
import type { DirectoryView } from '@/types'

export function HomePage() {
    const [filters, setFilters] = useState<ServerFiltersType>({ view: 'compact', limit: 25 })

    return (
        <div className="py-8">
            {/* Hero Section */}
            <div className="mb-12 text-center">
                <h1 className="text-4xl font-bold text-foreground mb-4">
                    ASASelfHosted
                </h1>
                <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
                    Public registry for self-hosted Ark: Survival Ascended servers
                </p>
            </div>

            {/* Newbie Carousel */}
            <section aria-labelledby="newbie-heading" className="mb-12">
                <h2 id="newbie-heading" className="text-2xl font-semibold text-foreground mb-6">
                    Newbie-Friendly Servers
                </h2>
                <NewbieCarousel />
            </section>

            {/* Server Directory */}
            <section aria-labelledby="directory-heading" className="mb-8">
                <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6">
                    <h2 id="directory-heading" className="text-2xl font-semibold text-foreground">
                        Server Directory
                    </h2>
                    <div className="flex items-center gap-2 sm:gap-4 flex-wrap">
                        <div className="flex items-center gap-2">
                            <label htmlFor="per-page" className="text-sm text-muted-foreground whitespace-nowrap">
                                <span className="hidden sm:inline">Per page:</span>
                                <span className="sm:hidden">Limit:</span>
                            </label>
                            <select
                                id="per-page"
                                value={filters.limit ?? 25}
                                onChange={(e) => {
                                    const limit = Number(e.target.value)
                                    setFilters({ ...filters, limit })
                                }}
                                className="input-tek min-h-[44px] w-auto min-w-[4rem]"
                                aria-label="Servers per page"
                            >
                                <option value={25}>25</option>
                                <option value={50}>50</option>
                                <option value={100}>100</option>
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
                                className="min-h-[44px]"
                                aria-label={`Switch to ${(filters.view ?? 'compact') === 'compact' ? 'card' : 'row'} view`}
                            >
                                {(filters.view ?? 'compact') === 'compact' ? 'Card' : 'Row'}
                            </Button>
                        </div>
                    </div>
                </div>
                <ServerFilters filters={filters} onFiltersChange={setFilters} />
                <ServerList filters={filters} />
            </section>
        </div>
    )
}
