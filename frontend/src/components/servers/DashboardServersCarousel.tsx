/**
 * Dashboard servers carousel component.
 *
 * Displays a horizontal scrolling carousel of server cards plus an "Add Server" card.
 * The Add Server card is always shown first. Includes prev/next arrow controls.
 */

import { useRef } from 'react'
import { DashboardServerCard } from './DashboardServerCard'
import { AddServerCard } from './AddServerCard'
import { Button } from '@/components/ui/Button'
import type { DirectoryServer } from '@/types'

/* At xl: use 208px cards + 12px gaps so 5×208 + 4×12 = 1088, leaving both borders visible with pl-1 pr-1 */
const CARD_WIDTH_XL_PX = 208
const GAP_PX = 12
const SCROLL_AMOUNT_XL = CARD_WIDTH_XL_PX + GAP_PX

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

interface DashboardServersCarouselProps {
    servers: DashboardServer[]
    onAddServer: () => void
    onEdit: (server: DashboardServer) => void
    onClone: (server: DashboardServer) => void
}

export function DashboardServersCarousel({
    servers,
    onAddServer,
    onEdit,
    onClone,
}: DashboardServersCarouselProps) {
    const scrollRef = useRef<HTMLDivElement>(null)
    const totalItems = 1 + servers.length

    const scroll = (dir: 'left' | 'right') => {
        const el = scrollRef.current
        if (!el) return
        el.scrollBy({ left: dir === 'left' ? -SCROLL_AMOUNT_XL : SCROLL_AMOUNT_XL, behavior: 'smooth' })
    }

    return (
        <div>
            <div className="flex items-center gap-0">
                {/* Left arrow: in flow so it sits in the gutter, not on the cards */}
                {totalItems > 1 && (
                    <Button
                        type="button"
                        variant="ghost"
                        size="sm"
                        aria-label="Previous"
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
                    className="flex-1 min-w-0 flex gap-4 overflow-x-auto pb-4 pl-1 pr-1 scrollbar-hide snap-x snap-mandatory"
                    style={{ scrollPaddingLeft: 8, scrollPaddingRight: 8 }}
                >
                    <div className="flex-shrink-0 w-80 xl:w-[216px] h-full snap-start">
                        <AddServerCard onClick={onAddServer} />
                    </div>
                    {servers.map((server) => (
                        <div key={server.id} className="flex-shrink-0 w-80 xl:w-[216px] h-full snap-start">
                            <DashboardServerCard
                                server={server}
                                onEdit={onEdit}
                                onClone={onClone}
                            />
                        </div>
                    ))}
                </div>

                {/* Right arrow: in flow so it sits in the gutter, not on the cards */}
                {totalItems > 1 && (
                    <Button
                        type="button"
                        variant="ghost"
                        size="sm"
                        aria-label="Next"
                        className="flex-shrink-0 w-8 h-12 min-w-8 min-h-0 p-0 rounded-none border-0 shadow-none text-muted-foreground hover:text-foreground hover:bg-transparent self-center"
                        onClick={() => scroll('right')}
                    >
                        <svg xmlns="http://www.w3.org/2000/svg" width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden className="flex-shrink-0">
                            <path d="m9 18 6-6-6-6" />
                        </svg>
                    </Button>
                )}
            </div>

            {totalItems > 3 && (
                <div className="flex justify-center gap-2 mt-2">
                    {[...Array(Math.min(totalItems, 5))].map((_, i) => (
                        <div key={i} className="w-1.5 h-1.5 rounded-full bg-muted-foreground/30" aria-hidden />
                    ))}
                    {totalItems > 5 && (
                        <span className="text-xs text-muted-foreground ml-1">+{totalItems - 5} more</span>
                    )}
                </div>
            )}
        </div>
    )
}
