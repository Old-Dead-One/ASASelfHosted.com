/**
 * Home page component.
 *
 * Main landing page with server listings and carousel.
 */

import { ServerList } from '@/components/servers/ServerList'

export function HomePage() {
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

            {/* 
              Planned: New Player / Learning-Friendly Server Carousel
              Criteria: boosted, guides enabled, friendly tags, verified uptime
            */}

            {/* Server Directory */}
            <section aria-labelledby="directory-heading" className="mb-8">
                <div className="flex items-center justify-between mb-6">
                    <h2 id="directory-heading" className="text-2xl font-semibold text-foreground">
                        Server Directory
                    </h2>
                    {/* TODO: Add search and filters */}
                </div>
                <ServerList />
            </section>
        </div>
    )
}
