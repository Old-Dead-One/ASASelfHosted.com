/**
 * Spotlight carousel component.
 *
 * Single-row horizontal carousel of 8 featured servers with arrow navigation and auto-scroll.
 * Content is duplicated so the carousel wraps around infinitely (scroll right flows to start).
 * Selection criteria (locked): verified, boosted, ranked by quality desc.
 * Criteria: mode=verified, ruleset=boosted, rank_by=quality, order=desc, limit=8 (see docs/TODO.md).
 */

import { useRef, useEffect, useState, useCallback } from 'react'
import { useQuery } from '@tanstack/react-query'
import { apiRequest } from '@/lib/api'
import { ServerCard } from './ServerCard'
import { TekCardSurface } from './TekCardSurface'
import { Button } from '@/components/ui/Button'
import type { DirectoryResponse } from '@/types'

/* Two cards visible at max width; cards resize with viewport; scroll one card at a time */
const GAP_PX = 24
const AUTO_SCROLL_INTERVAL_MS = 5000
const FALLBACK_SCROLL_PX = 540 + GAP_PX
const WRAP_THRESHOLD_PX = 10

export function SpotlightCarousel() {
    const scrollRef = useRef<HTMLDivElement>(null)
    const autoScrollRef = useRef<ReturnType<typeof setInterval> | null>(null)
    const scrollAmountRef = useRef(FALLBACK_SCROLL_PX)
    const isWrappingRef = useRef(false)
    const [isPaused, setIsPaused] = useState(false)

    const { data, isLoading, error } = useQuery({
        queryKey: ['servers', 'spotlight'],
        queryFn: async () => {
            const params = new URLSearchParams()
            params.set('ruleset', 'boosted')
            params.set('mode', 'verified')
            params.set('limit', '8')
            params.set('rank_by', 'quality')
            params.set('order', 'desc')
            return apiRequest<DirectoryResponse>(`/api/v1/directory/servers?${params.toString()}`)
        },
        staleTime: 60_000,
    })

    const servers = data?.data ?? []
    /* Duplicate list so we can wrap: [A,B,C,...] -> [A,B,C,...,A,B,C,...] */
    const duplicatedServers = servers.length > 0 ? [...servers, ...servers] : []

    /* Measure first card width so we scroll by one card + gap (responsive) */
    useEffect(() => {
        const el = scrollRef.current
        if (!el || duplicatedServers.length === 0) return
        const firstCard = el.firstElementChild
        const update = () => {
            if (firstCard) {
                const w = (firstCard as HTMLElement).offsetWidth
                scrollAmountRef.current = w + GAP_PX
            }
        }
        update()
        const ro = new ResizeObserver(update)
        ro.observe(el)
        return () => ro.disconnect()
    }, [duplicatedServers.length])

    /* When scroll passes into the duplicated half, snap back to the first half (infinite wrap) */
    const handleScroll = useCallback(() => {
        const el = scrollRef.current
        if (!el || isWrappingRef.current || duplicatedServers.length === 0) return
        const half = el.scrollWidth / 2
        if (el.scrollLeft >= half - WRAP_THRESHOLD_PX) {
            isWrappingRef.current = true
            el.scrollLeft = el.scrollLeft - half
            isWrappingRef.current = false
        }
    }, [duplicatedServers.length])

    useEffect(() => {
        const el = scrollRef.current
        if (!el || duplicatedServers.length === 0) return
        el.addEventListener('scroll', handleScroll, { passive: true })
        return () => el.removeEventListener('scroll', handleScroll)
    }, [duplicatedServers.length, handleScroll])

    const scroll = useCallback((dir: 'left' | 'right') => {
        const el = scrollRef.current
        if (!el || duplicatedServers.length === 0) return
        const amount = scrollAmountRef.current
        const half = el.scrollWidth / 2
        if (dir === 'left' && el.scrollLeft <= WRAP_THRESHOLD_PX) {
            /* At start: jump to equivalent position in second half (shows last cards), then scroll left */
            isWrappingRef.current = true
            el.scrollLeft = half - el.clientWidth
            isWrappingRef.current = false
            el.scrollBy({ left: -amount, behavior: 'smooth' })
        } else {
            el.scrollBy({ left: dir === 'left' ? -amount : amount, behavior: 'smooth' })
        }
    }, [duplicatedServers.length])

    useEffect(() => {
        if (duplicatedServers.length <= 1 || isPaused) return
        autoScrollRef.current = setInterval(() => {
            const el = scrollRef.current
            if (!el) return
            el.scrollBy({ left: scrollAmountRef.current, behavior: 'smooth' })
        }, AUTO_SCROLL_INTERVAL_MS)
        return () => {
            if (autoScrollRef.current) {
                clearInterval(autoScrollRef.current)
                autoScrollRef.current = null
            }
        }
    }, [duplicatedServers.length, isPaused])

    if (isLoading) {
        return (
            <div className="card-elevated p-4">
                <h2 className="text-xl font-semibold text-foreground mb-4">Spotlight</h2>
                <div className="flex gap-6 overflow-hidden">
                    {[...Array(4)].map((_, i) => (
                        <TekCardSurface key={i} className="flex-shrink-0 w-[540px] min-h-[200px] max-h-[280px] animate-pulse" contentClassName="p-6" />
                    ))}
                </div>
            </div>
        )
    }

    if (error || servers.length === 0) {
        return (
            <div className="card-elevated p-4">
                <h2 className="text-xl font-semibold text-foreground mb-4">Spotlight</h2>
                <div className="text-center py-8 text-muted-foreground">
                    <p>No spotlight servers found.</p>
                    <p className="text-sm mt-1">Try the full directory below.</p>
                </div>
            </div>
        )
    }

    return (
        <div className="card-elevated p-4">
            <h2 className="text-xl font-semibold text-foreground mb-4">Spotlight</h2>
            <div
                className="flex items-center gap-0"
                onMouseEnter={() => setIsPaused(true)}
                onMouseLeave={() => setIsPaused(false)}
            >
                {servers.length > 1 && (
                    <Button
                        type="button"
                        variant="ghost"
                        size="sm"
                        aria-label="Previous spotlight"
                        className="flex-shrink-0 w-8 h-12 min-w-8 min-h-0 p-0 rounded-none border-0 shadow-none text-muted-foreground hover:text-foreground hover:bg-transparent self-center"
                        onClick={() => scroll('left')}
                    >
                        <svg xmlns="http://www.w3.org/2000/svg" width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden className="flex-shrink-0">
                            <path d="M15 18l-6-6 6-6" />
                        </svg>
                    </Button>
                )}

                <div
                    ref={scrollRef}
                    className="flex-1 min-w-0 flex gap-6 overflow-x-auto pb-4 pl-1 pr-1 scrollbar-hide snap-x snap-mandatory"
                    style={{ scrollPaddingLeft: 8, scrollPaddingRight: 8 }}
                    aria-label="Spotlight servers"
                >
                    {duplicatedServers.map((server, index) => (
                        <div key={index} className="flex-shrink-0 min-w-[260px] w-[min(540px,calc(50vw-24px))] min-h-[200px] max-h-[280px] overflow-hidden snap-start">
                            <ServerCard server={server} badgesInRow />
                        </div>
                    ))}
                </div>

                {servers.length > 1 && (
                    <Button
                        type="button"
                        variant="ghost"
                        size="sm"
                        aria-label="Next spotlight"
                        className="flex-shrink-0 w-8 h-12 min-w-8 min-h-0 p-0 rounded-none border-0 shadow-none text-muted-foreground hover:text-foreground hover:bg-transparent self-center"
                        onClick={() => scroll('right')}
                    >
                        <svg xmlns="http://www.w3.org/2000/svg" width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden className="flex-shrink-0">
                            <path d="m9 18 6-6-6-6" />
                        </svg>
                    </Button>
                )}
            </div>
        </div>
    )
}
