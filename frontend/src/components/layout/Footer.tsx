/**
 * Footer component.
 *
 * Site footer with links and information.
 * Uses style-guide theme tokens and focus rings.
 */

import { Link } from 'react-router-dom'

export function Footer() {
    const linkClass =
        'text-muted-foreground hover:text-foreground transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-ring/60 focus-visible:ring-offset-2 focus-visible:ring-offset-background rounded px-1 py-0.5'

    return (
        <footer className="fixed bottom-0 left-0 right-0 z-10 border-t border-input bg-muted" role="contentinfo">
            <div className="mx-auto w-full max-w-screen-xl px-4 sm:px-6 lg:px-8 py-6">
                <div className="flex flex-col md:flex-row justify-between items-center gap-4">
                    <p className="text-sm text-muted-foreground">
                        ASASelfHosted — Self-hosted ASA server registry
                    </p>
                    <div className="flex gap-6 text-sm">
                        <Link to="/verification" className={linkClass}>
                            Verification
                        </Link>
                        <Link to="/consent" className={linkClass}>
                            Consent
                        </Link>
                        <Link to="/privacy" className={linkClass}>
                            Privacy
                        </Link>
                        <Link to="/terms" className={linkClass}>
                            Terms
                        </Link>
                        <Link to="/privacy-policy" className={linkClass}>
                            Legal
                        </Link>
                        <Link to="/contact" className={linkClass}>
                            Contact
                        </Link>
                    </div>
                </div>
            </div>
        </footer>
    )
}
