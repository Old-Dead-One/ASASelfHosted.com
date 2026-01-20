/**
 * TanStack Query client configuration.
 *
 * Provides default query client with sensible defaults.
 * All data fetching should use TanStack Query.
 */

import { QueryClient } from '@tanstack/react-query'

export const queryClient = new QueryClient({
    defaultOptions: {
        queries: {
            // Stale time: data is considered fresh for 30 seconds
            staleTime: 30 * 1000,
            // Cache time: unused data stays in cache for 5 minutes
            gcTime: 5 * 60 * 1000,
            // Retry failed requests once
            retry: 1,
            // Refetch on window focus in production
            refetchOnWindowFocus: import.meta.env.PROD,
        },
    },
})
