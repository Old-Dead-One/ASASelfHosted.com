import React from 'react'
import ReactDOM from 'react-dom/client'
import { QueryClientProvider } from '@tanstack/react-query'
import App from './App.tsx'
import { queryClient } from './lib/query-client'
import './index.css'

// Dynamic import for DevTools - only loaded in development, not in production bundle
const Devtools = import.meta.env.DEV
    ? React.lazy(() =>
        import('@tanstack/react-query-devtools').then((m) => ({
            default: m.ReactQueryDevtools,
        }))
    )
    : null

// Sentry initialization removed for now
// To enable Sentry:
// 1. Install: npm install @sentry/react
// 2. Add VITE_SENTRY_DSN to .env
// 3. Uncomment and configure Sentry.init() below
//
// if (import.meta.env.VITE_SENTRY_DSN) {
//   import('@sentry/react').then((Sentry) => {
//     Sentry.init({
//       dsn: import.meta.env.VITE_SENTRY_DSN,
//       integrations: [
//         Sentry.browserTracingIntegration(),
//         Sentry.replayIntegration(),
//       ],
//       tracesSampleRate: 1.0,
//       replaysSessionSampleRate: 0.1,
//       replaysOnErrorSampleRate: 1.0,
//     })
//   })
// }

ReactDOM.createRoot(document.getElementById('root')!).render(
    <React.StrictMode>
        <QueryClientProvider client={queryClient}>
            <App />
            {Devtools && (
                <React.Suspense fallback={null}>
                    <Devtools initialIsOpen={false} />
                </React.Suspense>
            )}
        </QueryClientProvider>
    </React.StrictMode>
)
