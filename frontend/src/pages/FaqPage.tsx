/**
 * FAQ page.
 *
 * Frequently asked questions about ASA Self-Hosted, verification, consent, and data.
 * Styled consistently with trust and legal pages.
 */

import { Link } from 'react-router-dom'

export function FaqPage() {
    return (
        <div className="py-8 px-4 max-w-3xl mx-auto">
            <h1 className="text-3xl font-bold text-foreground mb-2">
                FAQ
            </h1>
            <p className="text-sm text-muted-foreground mb-6">
                Frequently Asked Questions
            </p>

            <section className="space-y-4 mb-8">
                <h2 className="text-xl font-semibold text-foreground">
                    What is ASA Self-Hosted?
                </h2>
                <p className="text-muted-foreground">
                    ASA Self-Hosted is a public directory and registry for self-hosted Ark: Survival Ascended servers and clusters. It helps players discover servers and helps owners present accurate, verifiable information.
                </p>
            </section>

            <section className="space-y-4 mb-8">
                <h2 className="text-xl font-semibold text-foreground">
                    Is ASA Self-Hosted official?
                </h2>
                <p className="text-muted-foreground">
                    No. ASA Self-Hosted is independent and not affiliated with Wildcard, Nitrado, Epic Games, or any other vendor.
                </p>
            </section>

            <section className="space-y-4 mb-8">
                <h2 className="text-xl font-semibold text-foreground">
                    Does ASA Self-Hosted host servers?
                </h2>
                <p className="text-muted-foreground">
                    No. ASA Self-Hosted does not host, control, or manage game servers. Server owners run their own infrastructure.
                </p>
            </section>

            <section className="space-y-4 mb-8">
                <h2 className="text-xl font-semibold text-foreground">
                    What does &quot;Verified&quot; mean?
                </h2>
                <p className="text-muted-foreground">
                    Verification means the server&apos;s identity has been cryptographically confirmed. It proves that status updates come from the claimed server and that the server controls the keys it uses. It does <strong>not</strong> guarantee quality, uptime, moderation, or population.
                </p>
            </section>

            <section className="space-y-4 mb-8">
                <h2 className="text-xl font-semibold text-foreground">
                    Is verification required?
                </h2>
                <p className="text-muted-foreground">
                    No. Servers can be listed without verification. Verification is optional and controlled by the server owner.
                </p>
            </section>

            <section className="space-y-4 mb-8">
                <h2 className="text-xl font-semibold text-foreground">
                    Does verification affect rankings or placement?
                </h2>
                <p className="text-muted-foreground">
                    No. Rankings and visibility are data-driven. They are not purchasable and are not influenced by payment.
                </p>
            </section>

            <section className="space-y-4 mb-8">
                <h2 className="text-xl font-semibold text-foreground">
                    Do you collect player data?
                </h2>
                <p className="text-muted-foreground">
                    Not by default. Player data is collected only when the server owner enables eligibility <strong>and</strong> the player explicitly grants permission <strong>in-game</strong>. If you did not run a consent command in-game, ASA Self-Hosted does not have your data.
                </p>
            </section>

            <section className="space-y-4 mb-8">
                <h2 className="text-xl font-semibold text-foreground">
                    What player data can be collected (with consent)?
                </h2>
                <p className="text-muted-foreground">
                    At a high level, and only if enabled: aggregate player counts, optional session duration, optional hashed identifiers, optional public profile display. Chat logs, inventory, tribe data, EOS data, and character saves are never collected.
                </p>
            </section>

            <section className="space-y-4 mb-8">
                <h2 className="text-xl font-semibold text-foreground">
                    Can I revoke consent?
                </h2>
                <p className="text-muted-foreground">
                    Yes. Consent can be revoked at any time with an in-game command. Revocation takes effect immediately and stops further collection and display.
                </p>
            </section>

            <section className="space-y-4 mb-8">
                <h2 className="text-xl font-semibold text-foreground">
                    Is this a paid service?
                </h2>
                <p className="text-muted-foreground">
                    The core directory is free. Some optional features may require subscriptions in the future, but rankings and visibility are never sold.
                </p>
            </section>

            <section className="space-y-4 mb-8">
                <h2 className="text-xl font-semibold text-foreground">
                    Can you remove a server listing?
                </h2>
                <p className="text-muted-foreground">
                    Yes. Listings may be removed if they are fraudulent, impersonating another server, or abusing the platform. Removal does not imply endorsement or judgment of gameplay.
                </p>
            </section>

            <section className="space-y-4 mb-8">
                <h2 className="text-xl font-semibold text-foreground">
                    How do I report incorrect information?
                </h2>
                <p className="text-muted-foreground">
                    Use the platform&apos;s <Link to="/contact" className="text-primary hover:text-accent transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-ring rounded px-0.5">contact</Link> mechanisms or reporting tools where available. Not all reports result in removal, but they are reviewed.
                </p>
            </section>

            <section className="space-y-4 mb-8">
                <h2 className="text-xl font-semibold text-foreground">
                    How do I request my data?
                </h2>
                <p className="text-muted-foreground">
                    You can submit a data rights request using the contact methods listed on the site or through the <Link to="/data-rights" className="text-primary hover:text-accent transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-ring rounded px-0.5">Data Rights Request</Link> page. If no data was collected, there may be nothing to retrieve or delete.
                </p>
            </section>

            <section className="space-y-4 mb-8">
                <h2 className="text-xl font-semibold text-foreground">
                    How do I delete my account?
                </h2>
                <p className="text-muted-foreground">
                    You can permanently delete your account and all associated data (profile, servers, clusters, favorites) from the <Link to="/data-rights" className="text-primary hover:text-accent transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-ring rounded px-0.5">Data Rights Request</Link> page. Sign in, then use the &quot;Delete my account&quot; section. You must confirm that you understand the action is <strong>permanent and cannot be reversed</strong>. After deletion you will be signed out. If you cannot sign in or prefer not to use self-service, you can <Link to="/contact" className="text-primary hover:text-accent transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-ring rounded px-0.5">contact us</Link> to request account deletion.
                </p>
            </section>

            <section className="space-y-4">
                <h2 className="text-xl font-semibold text-foreground">
                    Why does ASA Self-Hosted exist?
                </h2>
                <p className="text-muted-foreground">
                    Because self-hosted servers deserve reliable discovery and trust infrastructure—without platform lock-in, pay-to-win placement, or silent data collection.
                </p>
            </section>
        </div>
    )
}
