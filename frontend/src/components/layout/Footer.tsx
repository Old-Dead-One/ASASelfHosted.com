/**
 * Footer component.
 *
 * Site footer with links and information.
 * Uses style-guide theme tokens and focus rings.
 */

export function Footer() {
    const linkClass =
        'text-muted-foreground hover:text-foreground transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-ring/60 focus-visible:ring-offset-2 focus-visible:ring-offset-background rounded px-1 py-0.5'

    return (
        <footer className="border-t border-input bg-muted mt-auto" role="contentinfo">
            <div className="mx-auto w-full max-w-screen-xl px-4 sm:px-6 lg:px-8 py-6">
                <div className="flex flex-col md:flex-row justify-between items-center gap-4">
                    <p className="text-sm text-muted-foreground">
                        ASASelfHosted — Self-hosted ASA server registry
                    </p>
                    <div className="flex gap-6 text-sm">
                        <a href="/about" className={linkClass}>
                            About
                        </a>
                        <a
                            href="#"
                            aria-disabled="true"
                            className={`${linkClass} opacity-50 cursor-not-allowed`}
                        >
                            Terms
                        </a>
                        <a
                            href="#"
                            aria-disabled="true"
                            className={`${linkClass} opacity-50 cursor-not-allowed`}
                        >
                            Privacy
                        </a>
                    </div>
                </div>
            </div>
        </footer>
    )
}
