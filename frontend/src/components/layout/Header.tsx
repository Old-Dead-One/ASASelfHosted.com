/**
 * Header component.
 *
 * Main site header with navigation.
 * Classic registry foundation with tactical sci-fi accents.
 */

export function Header() {
    return (
        <header className="border-b border-border bg-card">
            <div className="container mx-auto px-4 py-4">
                <nav className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                        <a
                            href="/"
                            className="text-xl font-semibold text-foreground hover:text-primary transition-colors"
                        >
                            ASASelfHosted.com
                        </a>
                        <span className="text-xs text-muted-foreground font-mono">
                            Registry
                        </span>
                    </div>
                    <div className="flex items-center gap-4">
                        {/* TODO: Add search bar */}
                        {/* TODO: Add sign in button */}
                        <a
                            href="/about"
                            className="text-sm text-muted-foreground hover:text-foreground transition-colors"
                        >
                            About
                        </a>
                    </div>
                </nav>
            </div>
        </header>
    )
}
