/**
 * Header component.
 *
 * Main site header with navigation.
 * Uses style-guide tokens (border-input, bg-background-elevated) and Button for actions.
 */

import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '@/contexts/AuthContext'
import { Button } from '@/components/ui/Button'

export function Header() {
    const { isAuthenticated, signOut, user } = useAuth()
    const navigate = useNavigate()

    const handleSignOut = async () => {
        await signOut()
        navigate('/')
    }

    return (
        <header className="border-b border-input bg-background-elevated" role="banner">
            <div className="mx-auto w-full max-w-screen-xl px-4 sm:px-6 lg:px-8 py-1.5">
                <nav className="flex items-center justify-between" aria-label="Main navigation">
                    <div className="flex items-center gap-2">
                        <Link
                            to="/"
                            className="text-xl font-semibold text-foreground hover:text-primary transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-ring/60 focus-visible:ring-offset-2 focus-visible:ring-offset-background rounded-md leading-tight"
                            aria-label="ASASelfHosted home"
                        >
                            ASASelfHosted
                        </Link>
                        <span className="text-xs text-muted-foreground font-mono border border-input bg-muted px-2 py-0.5 rounded hidden sm:inline leading-tight">
                            Registry
                        </span>
                    </div>
                    <div className="flex items-center gap-2">
                        <Link
                            to="/servers"
                            className="text-sm text-muted-foreground hover:text-foreground transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-ring/60 focus-visible:ring-offset-2 focus-visible:ring-offset-background rounded-md px-2 py-1 flex items-center leading-tight"
                            aria-label="Servers"
                        >
                            Servers
                        </Link>
                        <Link
                            to="/clusters"
                            className="text-sm text-muted-foreground hover:text-foreground transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-ring/60 focus-visible:ring-offset-2 focus-visible:ring-offset-background rounded-md px-2 py-1 flex items-center leading-tight"
                            aria-label="Clusters"
                        >
                            Clusters
                        </Link>
                        {isAuthenticated ? (
                            <>
                                <Link
                                    to="/dashboard"
                                    className="text-sm text-muted-foreground hover:text-foreground transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-ring/60 focus-visible:ring-offset-2 focus-visible:ring-offset-background rounded-md px-2 py-1 flex items-center leading-tight"
                                    aria-label="Dashboard"
                                >
                                    <span className="hidden sm:inline">Dashboard</span>
                                    <span className="sm:hidden">Dash</span>
                                </Link>
                                <Link
                                    to="/about"
                                    className="text-sm text-muted-foreground hover:text-foreground transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-ring/60 focus-visible:ring-offset-2 focus-visible:ring-offset-background rounded-md px-2 py-1 flex items-center leading-tight"
                                    aria-label="About"
                                >
                                    About
                                </Link>
                                <Link
                                    to="/faq"
                                    className="text-sm text-muted-foreground hover:text-foreground transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-ring/60 focus-visible:ring-offset-2 focus-visible:ring-offset-background rounded-md px-2 py-1 flex items-center leading-tight"
                                    aria-label="FAQ"
                                >
                                    FAQ
                                </Link>
                                <span className="text-xs text-muted-foreground hidden md:inline truncate max-w-[220px]" title={user?.email ?? undefined}>
                                    {user?.email}
                                </span>
                                <Button
                                    type="button"
                                    variant="ghost"
                                    size="sm"
                                    onClick={handleSignOut}
                                    aria-label="Sign out"
                                    className="h-auto py-1 px-2 text-sm"
                                >
                                    <span className="hidden sm:inline">Sign out</span>
                                    <span className="sm:hidden">Out</span>
                                </Button>
                            </>
                        ) : (
                            <>
                                <Link
                                    to="/about"
                                    className="text-sm text-muted-foreground hover:text-foreground transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-ring/60 focus-visible:ring-offset-2 focus-visible:ring-offset-background rounded-md px-2 py-1 flex items-center leading-tight"
                                    aria-label="About"
                                >
                                    About
                                </Link>
                                <Link
                                    to="/faq"
                                    className="text-sm text-muted-foreground hover:text-foreground transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-ring/60 focus-visible:ring-offset-2 focus-visible:ring-offset-background rounded-md px-2 py-1 flex items-center leading-tight"
                                    aria-label="FAQ"
                                >
                                    FAQ
                                </Link>
                                <Link
                                    to="/login"
                                    className="text-sm text-muted-foreground hover:text-foreground transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-ring/60 focus-visible:ring-offset-2 focus-visible:ring-offset-background rounded-md px-2 py-1 flex items-center leading-tight"
                                    aria-label="Sign in"
                                >
                                    Sign in
                                </Link>
                                <Link
                                    to="/signup"
                                    className="inline-flex items-center justify-center rounded-md font-medium text-sm px-3 py-1.5 bg-primary text-primary-foreground border border-ring/25 shadow-sm shadow-black/40 hover:shadow-md hover:shadow-black/50 hover:-translate-y-px hover:border-ring/40 transition focus:outline-none focus-visible:ring-2 focus-visible:ring-ring/60 focus-visible:ring-offset-2 focus-visible:ring-offset-background"
                                    aria-label="Sign up"
                                >
                                    Sign up
                                </Link>
                            </>
                        )}
                    </div>
                </nav>
            </div>
        </header>
    )
}
