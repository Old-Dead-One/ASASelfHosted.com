/**
 * Spotlight carousel component.
 *
 * Displays a carousel of featured servers with prev/next arrows.
 * Can be used for various spotlight categories (Newbie-Friendly, New Servers, Hot, etc.).
 * Server selection logic to be implemented.
 */

import { useRef } from 'react'
import { useQuery } from '@tanstack/react-query'
import { apiRequest } from '@/lib/api'
import { ServerCard } from './ServerCard'
import { Button } from '@/components/ui/Button'
import type { DirectoryResponse } from '@/types'

const CARD_WIDTH_PX = 320
const GAP_PX = 16
const SCROLL_AMOUNT = CARD_WIDTH_PX + GAP_PX

export function SpotlightCarousel() {
    const scrollRef = useRef<HTMLDivElement>(null)
    const { data, isLoading, error } = useQuery({
        queryKey: ['servers', 'spotlight'],
        queryFn: async () => {
            const params = new URLSearchParams()
            params.set('ruleset', 'boosted')
            params.set('mode', 'verified')
            params.set('limit', '10')
            params.set('rank_by', 'quality')
            params.set('order', 'desc')
            return apiRequest<DirectoryResponse>(`/api/v1/directory/servers?${params.toString()}`)
        },
        staleTime: 60_000,
    })

    const servers = data?.data ?? []

    const scroll = (dir: 'left' | 'right') => {
        const el = scrollRef.current
        if (!el) return
        el.scrollBy({ left: dir === 'left' ? -SCROLL_AMOUNT : SCROLL_AMOUNT, behavior: 'smooth' })
    }

    if (isLoading) {
        return (
            <div className="flex gap-4 overflow-x-auto pb-4 scrollbar-hide">
                {[...Array(3)].map((_, i) => (
                    <div key={i} className="flex-shrink-0 w-80 h-64 card-tek animate-pulse" />
                ))}
            </div>
        )
    }

    if (error || servers.length === 0) {
        return (
            <div className="text-center py-8 text-muted-foreground">
                <p>No spotlight servers found.</p>
                <p className="text-sm mt-1">Try the full directory below.</p>
            </div>
        )
    }

    return (
        <div className="relative">
            {servers.length > 1 && (
                <>
                    <Button
                        type="button"
                        variant="secondary"
                        size="sm"
                        aria-label="Previous"
                        className="absolute left-0 top-1/2 -translate-y-1/2 z-10 w-10 h-10 rounded-full p-0 shadow-md"
                        onClick={() => scroll('left')}
                    >
                        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden>
                            <path d="M15 18l-6-6 6-6" />
                        </svg>
                    </Button>
                    <Button
                        type="button"
                        variant="secondary"
                        size="sm"
                        aria-label="Next"
                        className="absolute right-0 top-1/2 -translate-y-1/2 z-10 w-10 h-10 rounded-full p-0 shadow-md"
                        onClick={() => scroll('right')}
                    >
                        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden>
                            <path d="m9 18 6-6-6-6" />
                        </svg>
                    </Button>
                </>
            )}
            <div
                ref={scrollRef}
                className="flex gap-4 overflow-x-auto pb-4 scrollbar-hide pl-14 pr-14"
            >
                {servers.map((server) => (
                    <div key={server.id} className="flex-shrink-0 w-80">
                        <ServerCard server={server} />
                    </div>
                ))}
            </div>
        </div>
    )
}
