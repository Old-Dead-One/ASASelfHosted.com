/**
 * About page.
 *
 * Explains what ASA Self-Hosted is, what we do and don't do, verification, consent, and independence.
 * Styled consistently with trust and legal pages.
 */

export function AboutPage() {
    return (
        <div className="py-8 px-4 max-w-3xl mx-auto">
            <h1 className="text-3xl font-bold text-foreground mb-2">
                About
            </h1>
            <p className="text-sm text-muted-foreground mb-6">
                ASA Self-Hosted
            </p>

            <section className="space-y-4 mb-8">
                <h2 className="text-xl font-semibold text-foreground">
                    What ASA Self-Hosted Is
                </h2>
                <p className="text-muted-foreground">
                    ASA Self-Hosted is an independent, vendor-neutral directory and registry for <strong>self-hosted Ark: Survival Ascended servers and clusters</strong>.
                </p>
                <p className="text-muted-foreground">
                    It exists to solve a long-standing gap in the ASA ecosystem: reliable discovery, visibility, and trust for servers that are <strong>not</strong> hosted through an &quot;official&quot; provider.
                </p>
                <p className="text-muted-foreground">
                    ASA Self-Hosted provides a public directory where self-hosted servers can be listed manually, alongside optional verification and automation for server owners who want stronger identity guarantees and clearer status reporting.
                </p>
            </section>

            <section className="space-y-4 mb-8">
                <h2 className="text-xl font-semibold text-foreground">
                    What We Do
                </h2>
                <p className="text-muted-foreground">
                    ASA Self-Hosted focuses on three things:
                </p>
                <ol className="list-decimal pl-6 space-y-2 text-muted-foreground">
                    <li><strong>Discovery</strong> — Helping players find servers that actually exist, are reachable, and are accurately described.</li>
                    <li><strong>Trust</strong> — Making it possible to verify that server data comes from the server it claims to represent—without endorsements, pay-to-win placement, or hidden incentives.</li>
                    <li><strong>Control</strong> — Ensuring server owners and players remain in control of their data through explicit, in-game consent.</li>
                </ol>
            </section>

            <section className="space-y-4 mb-8">
                <h2 className="text-xl font-semibold text-foreground">
                    What We Don&apos;t Do
                </h2>
                <p className="text-muted-foreground">
                    ASA Self-Hosted does <strong>not</strong>:
                </p>
                <ul className="list-disc pl-6 space-y-1 text-muted-foreground">
                    <li>Host game servers</li>
                    <li>Control gameplay, moderation, or community rules</li>
                    <li>Guarantee uptime, population, or quality</li>
                    <li>Sell rankings or featured placement</li>
                    <li>Collect player data by default</li>
                </ul>
                <p className="text-muted-foreground">
                    The platform exists to provide visibility—not control.
                </p>
            </section>

            <section className="space-y-4 mb-8">
                <h2 className="text-xl font-semibold text-foreground">
                    Verification, Not Endorsement
                </h2>
                <p className="text-muted-foreground">
                    Verification on ASA Self-Hosted confirms <strong>server identity</strong>, not quality or safety.
                </p>
                <p className="text-muted-foreground">
                    A verified server has proven that:
                </p>
                <ul className="list-disc pl-6 space-y-1 text-muted-foreground">
                    <li>It controls the cryptographic keys it claims to use</li>
                    <li>Its status updates and heartbeats come from the same source</li>
                </ul>
                <p className="text-muted-foreground">
                    Verification does <strong>not</strong> mean:
                </p>
                <ul className="list-disc pl-6 space-y-1 text-muted-foreground">
                    <li>The server is &quot;better&quot;</li>
                    <li>The server is moderated</li>
                    <li>The server is endorsed</li>
                </ul>
                <p className="text-muted-foreground">
                    Servers may list with or without verification.
                </p>
            </section>

            <section className="space-y-4 mb-8">
                <h2 className="text-xl font-semibold text-foreground">
                    Consent &amp; Privacy by Design
                </h2>
                <p className="text-muted-foreground">
                    ASA Self-Hosted is built around a consent-first model:
                </p>
                <ul className="list-disc pl-6 space-y-1 text-muted-foreground">
                    <li>No sensitive data is collected by default</li>
                    <li>Player data requires explicit, in-game authorization</li>
                    <li>Consent is revocable at any time</li>
                    <li>The platform cannot enable permissions remotely</li>
                </ul>
                <p className="text-muted-foreground">
                    If you did not explicitly grant permission in-game, ASA Self-Hosted does not have your data.
                </p>
            </section>

            <section className="space-y-4 mb-8">
                <h2 className="text-xl font-semibold text-foreground">
                    Independence
                </h2>
                <p className="text-muted-foreground">
                    ASA Self-Hosted is not affiliated with Wildcard, Nitrado, Epic Games, or any other hosting provider.
                </p>
                <p className="text-muted-foreground">
                    It exists to give self-hosted servers the infrastructure they should have had from the beginning—without forcing commercial hosting.
                </p>
            </section>

            <section className="space-y-4">
                <h2 className="text-xl font-semibold text-foreground">
                    Long-Term Direction
                </h2>
                <p className="text-muted-foreground">
                    ASA Self-Hosted is designed as a long-term platform, not a short-lived listing site.
                </p>
                <p className="text-muted-foreground">
                    Future capabilities may include:
                </p>
                <ul className="list-disc pl-6 space-y-1 text-muted-foreground">
                    <li>Richer cluster views</li>
                    <li>Data-driven insights</li>
                    <li>Optional automation for server owners</li>
                </ul>
                <p className="text-muted-foreground">
                    The core directory will remain public and accessible.
                </p>
            </section>
        </div>
    )
}
