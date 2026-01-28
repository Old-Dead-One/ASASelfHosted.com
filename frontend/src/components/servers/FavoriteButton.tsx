/**
 * Favorite button component.
 *
 * Shows favorite count for all users; toggle only when authenticated.
 */

import { useState } from 'react'
import { useAuth } from '@/contexts/AuthContext'
import { addFavorite, removeFavorite } from '@/lib/api'
import { Button } from '@/components/ui/Button'

interface FavoriteButtonProps {
    serverId: string
    isFavorited?: boolean
    favoriteCount?: number
}

export function FavoriteButton({
    serverId,
    isFavorited: initialIsFavorited,
    favoriteCount: initialCount,
}: FavoriteButtonProps) {
    const { isAuthenticated } = useAuth()
    const [isFavorited, setIsFavorited] = useState(initialIsFavorited ?? false)
    const [favoriteCount, setFavoriteCount] = useState(initialCount ?? 0)
    const [loading, setLoading] = useState(false)

    if (!isAuthenticated) {
        return (
            <span className="text-sm text-muted-foreground" aria-hidden="true">
                {favoriteCount} {favoriteCount === 1 ? 'favorite' : 'favorites'}
            </span>
        )
    }

    const handleToggle = async () => {
        if (loading) return
        
        setLoading(true)
        const previousFavorited = isFavorited
        const previousCount = favoriteCount
        
        // Optimistic update
        setIsFavorited(!isFavorited)
        setFavoriteCount(prev => isFavorited ? prev - 1 : prev + 1)
        
        try {
            if (previousFavorited) {
                await removeFavorite(serverId)
            } else {
                await addFavorite(serverId)
            }
        } catch (error) {
            // Revert on error
            setIsFavorited(previousFavorited)
            setFavoriteCount(previousCount)
            console.error('Failed to toggle favorite:', error)
        } finally {
            setLoading(false)
        }
    }

    return (
        <Button
            type="button"
            variant="secondary"
            size="sm"
            onClick={handleToggle}
            disabled={loading}
            className="flex items-center gap-2"
            aria-label={isFavorited ? 'Remove from favorites' : 'Add to favorites'}
        >
            <span className={isFavorited ? 'text-destructive' : 'text-muted-foreground'} aria-hidden>
                {isFavorited ? '♥' : '♡'}
            </span>
            {favoriteCount > 0 && <span className="text-sm">{favoriteCount}</span>}
        </Button>
    )
}
