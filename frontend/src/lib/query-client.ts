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
            staleTime: 30 * 1000, // 30s freshness
            gcTime: 5 * 60 * 1000, // 5 min cache
            throwOnError: false, // Let UI decide how to show failures
            retry: (failureCount, error: any) => {
                // Don't retry 4xx errors (validation/auth errors)
                if (error?.code?.startsWith?.('4')) return false
                return failureCount < 1
            },
            refetchOnWindowFocus: import.meta.env.PROD,
            networkMode: 'online', // Explicit network mode for flaky connections
        },
    },
})
