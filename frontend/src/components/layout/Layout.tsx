/**
 * Layout component.
 *
 * Main layout wrapper with header and footer.
 * Uses Outlet from react-router-dom for nested routes.
 */

import { Outlet } from 'react-router-dom'
import { Header } from './Header'
import { Footer } from './Footer'

export function Layout() {
    return (
        <div className="min-h-screen flex flex-col bg-background">
            <a
                href="#main-content"
                className="sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4 focus:z-50 focus:px-4 focus:py-2 focus:bg-primary focus:text-primary-foreground focus:rounded-md focus:ring-2 focus:ring-ring"
            >
                Skip to main content
            </a>
            <Header />
            <main id="main-content" className="flex-1" role="main">
                <div className="mx-auto w-full max-w-screen-xl px-4 sm:px-6 lg:px-8">
                    <Outlet />
                </div>
            </main>
            <Footer />
        </div>
    )
}
