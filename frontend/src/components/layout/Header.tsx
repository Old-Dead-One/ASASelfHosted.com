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
                            ASASelfHosted
                        </a>
                        <span className="text-xs text-muted-foreground font-mono border border-gridline bg-panel px-2 py-0.5 rounded">
                            Registry
                        </span>
                    </div>
                    <div className="flex items-center gap-4">
                        {/* TODO: Add search bar */}
                        <a
                            href="/about"
                            className="text-sm text-muted-foreground hover:text-foreground transition-colors"
                        >
                            About
                        </a>
                        <button className="text-sm text-muted-foreground hover:text-foreground transition-colors">
                            Sign in
                        </button>
                    </div>
                </nav>
            </div>
        </header>
    )
}
