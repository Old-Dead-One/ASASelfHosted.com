/**
 * Data Rights Request — legal page.
 *
 * Explains how to request access, correction, or deletion of personal data.
 * Styled consistently with Privacy Policy and other legal pages.
 */

import { Link } from 'react-router-dom'

export function DataRightsPage() {
    return (
        <div className="py-8 px-4 max-w-3xl mx-auto">
            <h1 className="text-3xl font-bold text-foreground mb-2">
                Data Rights Request
            </h1>
            <p className="text-sm text-muted-foreground mb-6">
                ASA Self-Hosted respects your right to access and control your personal data.
            </p>

            <section className="space-y-4 mb-8">
                <p className="text-muted-foreground">
                    Depending on your location, you may request:
                </p>
                <ul className="list-disc pl-6 space-y-1 text-muted-foreground">
                    <li>Access to personal data we hold about you</li>
                    <li>Correction of inaccurate data</li>
                    <li>Deletion of personal data</li>
                    <li>Withdrawal of consent</li>
                </ul>
                <p className="text-muted-foreground">
                    If data was never collected, there may be nothing to retrieve or delete.
                </p>
            </section>

            <section className="space-y-4 mb-8">
                <h2 className="text-xl font-semibold text-foreground">
                    How to Submit a Request
                </h2>
                <p className="text-muted-foreground">
                    Please submit requests via the <Link to="/contact" className="text-primary hover:text-accent transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-ring rounded px-0.5">Contact</Link> page. Contact form and email will be wired up before initial release.
                </p>
                <p className="text-muted-foreground">
                    To protect your privacy, we may ask you to verify your identity before processing a request.
                </p>
            </section>

            <section className="space-y-4">
                <h2 className="text-xl font-semibold text-foreground">
                    What We Can and Cannot Do
                </h2>
                <p className="text-muted-foreground">
                    We can act only on data processed by ASA Self-Hosted.
                </p>
                <p className="text-muted-foreground">We cannot access or delete:</p>
                <ul className="list-disc pl-6 space-y-1 text-muted-foreground">
                    <li>Game server data</li>
                    <li>In-game data stored by server owners</li>
                    <li>Data controlled by third-party platforms</li>
                </ul>
            </section>
        </div>
    )
}
