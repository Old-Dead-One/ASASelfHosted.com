/**
 * Footer component.
 *
 * Site footer with links and information.
 */

export function Footer() {
    return (
        <footer className="border-t border-border bg-panel mt-auto">
            <div className="container mx-auto px-4 py-6">
                <div className="flex flex-col md:flex-row justify-between items-center gap-4">
                    <p className="text-sm text-muted-foreground">
                        ASASelfHosted — Self-hosted ASA server registry
                    </p>
                    <div className="flex gap-6 text-sm">
                        <a
                            href="/about"
                            className="text-muted-foreground hover:text-foreground transition-colors"
                        >
                            About
                        </a>
                        <a
                            href="#"
                            aria-disabled="true"
                            className="text-muted-foreground hover:text-foreground transition-colors opacity-50 cursor-not-allowed"
                        >
                            Terms
                        </a>
                        <a
                            href="#"
                            aria-disabled="true"
                            className="text-muted-foreground hover:text-foreground transition-colors opacity-50 cursor-not-allowed"
                        >
                            Privacy
                        </a>
                    </div>
                </div>
            </div>
        </footer>
    )
}
