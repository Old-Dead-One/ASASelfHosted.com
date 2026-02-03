/**
 * Terms of Service — legal trust page.
 *
 * Styled consistently with Verification, Consent, and Privacy pages.
 */

import { Link } from 'react-router-dom'

export function TermsPage() {
    return (
        <div className="py-8 px-4 max-w-3xl mx-auto">
            <h1 className="text-3xl font-bold text-foreground mb-2">
                Terms of Service
            </h1>
            <p className="text-sm text-muted-foreground mb-6">
                ASA Self-Hosted · Effective date: [set on deploy]
            </p>

            <section className="mb-8 p-4 rounded-lg border-2 border-primary/30 bg-primary/5">
                <h2 className="text-xl font-semibold text-foreground mb-3">
                    TL;DR
                </h2>
                <p className="text-muted-foreground mb-3">
                    ASA Self-Hosted is a directory, not a host.
                </p>
                <ul className="list-disc pl-6 space-y-1 text-muted-foreground mb-3">
                    <li>We list servers — we don&apos;t run or control them.</li>
                    <li>Verification proves a server&apos;s identity, not its quality or safety.</li>
                    <li>Data is not collected by default.</li>
                    <li>Player data requires explicit, in-game consent.</li>
                    <li>If you didn&apos;t run a consent command in-game, we don&apos;t have your data.</li>
                    <li>You can revoke consent at any time, and it takes effect immediately.</li>
                    <li>Rankings and visibility are not for sale.</li>
                </ul>
                <p className="text-muted-foreground">
                    By using the platform, you agree to these terms and to use the service responsibly.
                </p>
            </section>

            <section className="space-y-4 mb-8">
                <h2 className="text-xl font-semibold text-foreground">
                    1. Acceptance of Terms
                </h2>
                <p className="text-muted-foreground">
                    By accessing or using ASA Self-Hosted (the &quot;Platform&quot;), you agree to these Terms of Service (&quot;Terms&quot;).
                </p>
                <p className="text-muted-foreground">
                    If you do not agree to these Terms, do not use the Platform.
                </p>
            </section>

            <section className="space-y-4 mb-8">
                <h2 className="text-xl font-semibold text-foreground">
                    2. What ASA Self-Hosted Is (and Is Not)
                </h2>
                <p className="text-muted-foreground">
                    ASA Self-Hosted is an independent, vendor-neutral directory and registry for self-hosted Ark: Survival Ascended servers and clusters.
                </p>
                <p className="text-muted-foreground">The Platform provides:</p>
                <ul className="list-disc pl-6 space-y-1 text-muted-foreground">
                    <li>Server listings and discovery</li>
                    <li>Optional verification of server identity</li>
                    <li>Optional tooling for server owners</li>
                    <li>Optional player-facing features when consent is granted</li>
                </ul>
                <p className="text-muted-foreground">The Platform <strong>does not</strong>:</p>
                <ul className="list-disc pl-6 space-y-1 text-muted-foreground">
                    <li>Host game servers</li>
                    <li>Operate or control game servers</li>
                    <li>Guarantee server availability, quality, or moderation</li>
                    <li>Act on behalf of Wildcard, Nitrado, Epic Games, or any other vendor</li>
                </ul>
            </section>

            <section className="space-y-4 mb-8">
                <h2 className="text-xl font-semibold text-foreground">
                    3. Accounts
                </h2>
                <h3 className="text-lg font-medium text-foreground mt-4">
                    3.1 Eligibility
                </h3>
                <p className="text-muted-foreground">
                    You must be legally capable of entering into agreements in your jurisdiction to create an account.
                </p>
                <p className="text-muted-foreground">Accounts may be used by:</p>
                <ul className="list-disc pl-6 space-y-1 text-muted-foreground">
                    <li>Players</li>
                    <li>Server owners</li>
                    <li>Cluster owners</li>
                </ul>
                <p className="text-muted-foreground">
                    There is no separate &quot;owner&quot; or &quot;player&quot; account type. Capabilities are determined by actions you take on the Platform.
                </p>
                <h3 className="text-lg font-medium text-foreground mt-4">
                    3.2 Account Responsibility
                </h3>
                <p className="text-muted-foreground">You are responsible for:</p>
                <ul className="list-disc pl-6 space-y-1 text-muted-foreground">
                    <li>Maintaining the security of your account</li>
                    <li>All activity that occurs under your account</li>
                </ul>
                <p className="text-muted-foreground">You must not:</p>
                <ul className="list-disc pl-6 space-y-1 text-muted-foreground">
                    <li>Share accounts in a way that compromises security</li>
                    <li>Attempt to access accounts or data you do not own</li>
                </ul>
            </section>

            <section className="space-y-4 mb-8">
                <h2 className="text-xl font-semibold text-foreground">
                    4. Server Listings
                </h2>
                <h3 className="text-lg font-medium text-foreground mt-4">
                    4.1 Listing Servers
                </h3>
                <p className="text-muted-foreground">
                    Server owners may create and manage server listings.
                </p>
                <p className="text-muted-foreground">By listing a server, you represent that:</p>
                <ul className="list-disc pl-6 space-y-1 text-muted-foreground">
                    <li>You have the authority to list that server</li>
                    <li>The information you provide is accurate to the best of your knowledge</li>
                </ul>
                <p className="text-muted-foreground">
                    Servers may be listed with or without verification.
                </p>
                <h3 className="text-lg font-medium text-foreground mt-4">
                    4.2 Verification
                </h3>
                <p className="text-muted-foreground">
                    Verification confirms <strong>server identity</strong>, not quality, safety, or endorsement.
                </p>
                <p className="text-muted-foreground">Verification:</p>
                <ul className="list-disc pl-6 space-y-1 text-muted-foreground">
                    <li>Is optional</li>
                    <li>Is controlled by the server owner</li>
                    <li>Does not grant featured placement or ranking advantages</li>
                </ul>
                <p className="text-muted-foreground">
                    Details are explained on the <Link to="/verification" className="text-primary hover:text-accent transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-ring rounded px-0.5">Verification</Link> page.
                </p>
                <h3 className="text-lg font-medium text-foreground mt-4">
                    4.3 Removal of Listings
                </h3>
                <p className="text-muted-foreground">
                    ASA Self-Hosted reserves the right to remove or disable listings that:
                </p>
                <ul className="list-disc pl-6 space-y-1 text-muted-foreground">
                    <li>Are demonstrably fraudulent or impersonating another server</li>
                    <li>Violate these Terms</li>
                    <li>Are used to abuse the Platform</li>
                </ul>
                <p className="text-muted-foreground">
                    Removal of a listing does not require prior notice.
                </p>
            </section>

            <section className="space-y-4 mb-8">
                <h2 className="text-xl font-semibold text-foreground">
                    5. Consent &amp; Data Collection
                </h2>
                <p className="text-muted-foreground">
                    ASA Self-Hosted follows a <strong>consent-first design</strong>.
                </p>
                <p className="text-muted-foreground">Key principles:</p>
                <ul className="list-disc pl-6 space-y-1 text-muted-foreground">
                    <li>Data is not collected by default</li>
                    <li>Sensitive data requires explicit, in-game consent</li>
                    <li>Both server owner and player consent may be required</li>
                </ul>
                <p className="text-muted-foreground">
                    If you did not explicitly grant permission in-game, the Platform does not have your data.
                </p>
                <p className="text-muted-foreground">
                    Details are explained on the <Link to="/consent" className="text-primary hover:text-accent transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-ring rounded px-0.5">Consent</Link> and <Link to="/privacy" className="text-primary hover:text-accent transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-ring rounded px-0.5">Privacy by Design</Link> pages.
                </p>
            </section>

            <section className="space-y-4 mb-8">
                <h2 className="text-xl font-semibold text-foreground">
                    6. Player Conduct
                </h2>
                <p className="text-muted-foreground">
                    When using the Platform, you agree not to:
                </p>
                <ul className="list-disc pl-6 space-y-1 text-muted-foreground">
                    <li>Attempt to bypass verification or consent mechanisms</li>
                    <li>Submit false or misleading server information</li>
                    <li>Abuse APIs, endpoints, or rate limits</li>
                    <li>Interfere with the operation or security of the Platform</li>
                    <li>Use the Platform for unlawful purposes</li>
                </ul>
            </section>

            <section className="space-y-4 mb-8">
                <h2 className="text-xl font-semibold text-foreground">
                    7. Platform Availability
                </h2>
                <p className="text-muted-foreground">
                    ASA Self-Hosted is provided on an <strong>as-is, best-effort basis</strong>.
                </p>
                <p className="text-muted-foreground">We do not guarantee:</p>
                <ul className="list-disc pl-6 space-y-1 text-muted-foreground">
                    <li>Continuous availability</li>
                    <li>Error-free operation</li>
                    <li>That the Platform will meet all use cases</li>
                </ul>
                <p className="text-muted-foreground">
                    Planned or unplanned downtime may occur.
                </p>
            </section>

            <section className="space-y-4 mb-8">
                <h2 className="text-xl font-semibold text-foreground">
                    8. Third-Party Services
                </h2>
                <p className="text-muted-foreground">
                    ASA Self-Hosted may integrate with or reference third-party services (such as Discord links or game platforms).
                </p>
                <p className="text-muted-foreground">We are not responsible for:</p>
                <ul className="list-disc pl-6 space-y-1 text-muted-foreground">
                    <li>Third-party services</li>
                    <li>Content hosted outside the Platform</li>
                    <li>Downtime or policy changes by third parties</li>
                </ul>
            </section>

            <section className="space-y-4 mb-8">
                <h2 className="text-xl font-semibold text-foreground">
                    9. Intellectual Property
                </h2>
                <p className="text-muted-foreground">
                    The Platform, including its code, branding, and documentation, is owned by ASA Self-Hosted unless otherwise stated.
                </p>
                <p className="text-muted-foreground">You may not:</p>
                <ul className="list-disc pl-6 space-y-1 text-muted-foreground">
                    <li>Copy or resell the Platform</li>
                    <li>Use branding without permission</li>
                    <li>Misrepresent affiliation or endorsement</li>
                </ul>
                <p className="text-muted-foreground">
                    Server names, mod names, and game content remain the property of their respective owners.
                </p>
            </section>

            <section className="space-y-4 mb-8">
                <h2 className="text-xl font-semibold text-foreground">
                    10. Disclaimer of Warranties
                </h2>
                <p className="text-muted-foreground">
                    The Platform is provided <strong>&quot;as is&quot;</strong> and <strong>&quot;as available.&quot;</strong>
                </p>
                <p className="text-muted-foreground">
                    To the fullest extent permitted by law, ASA Self-Hosted disclaims all warranties, express or implied, including:
                </p>
                <ul className="list-disc pl-6 space-y-1 text-muted-foreground">
                    <li>Merchantability</li>
                    <li>Fitness for a particular purpose</li>
                    <li>Non-infringement</li>
                </ul>
            </section>

            <section className="space-y-4 mb-8">
                <h2 className="text-xl font-semibold text-foreground">
                    11. Limitation of Liability
                </h2>
                <p className="text-muted-foreground">
                    To the fullest extent permitted by law, ASA Self-Hosted shall not be liable for:
                </p>
                <ul className="list-disc pl-6 space-y-1 text-muted-foreground">
                    <li>Loss of data</li>
                    <li>Loss of revenue</li>
                    <li>Server downtime</li>
                    <li>Gameplay outcomes</li>
                    <li>Actions taken by server owners or players</li>
                </ul>
                <p className="text-muted-foreground">
                    Use of the Platform is at your own risk.
                </p>
            </section>

            <section className="space-y-4 mb-8">
                <h2 className="text-xl font-semibold text-foreground">
                    12. Changes to the Platform or Terms
                </h2>
                <p className="text-muted-foreground">
                    ASA Self-Hosted may:
                </p>
                <ul className="list-disc pl-6 space-y-1 text-muted-foreground">
                    <li>Modify the Platform</li>
                    <li>Update these Terms</li>
                </ul>
                <p className="text-muted-foreground">
                    Material changes will be reflected by updating the effective date.
                </p>
                <p className="text-muted-foreground">
                    Continued use of the Platform constitutes acceptance of updated Terms.
                </p>
            </section>

            <section className="space-y-4 mb-8">
                <h2 className="text-xl font-semibold text-foreground">
                    13. Termination
                </h2>
                <p className="text-muted-foreground">
                    ASA Self-Hosted may suspend or terminate access to the Platform if:
                </p>
                <ul className="list-disc pl-6 space-y-1 text-muted-foreground">
                    <li>These Terms are violated</li>
                    <li>Use poses a security or legal risk</li>
                    <li>Abuse or exploitation is detected</li>
                </ul>
                <p className="text-muted-foreground">
                    Termination may occur with or without notice.
                </p>
            </section>

            <section className="space-y-4 mb-8">
                <h2 className="text-xl font-semibold text-foreground">
                    14. Governing Law
                </h2>
                <p className="text-muted-foreground">
                    These Terms are governed by the laws of the applicable jurisdiction in which ASA Self-Hosted operates, without regard to conflict of law principles.
                </p>
            </section>

            <section className="space-y-4">
                <h2 className="text-xl font-semibold text-foreground">
                    15. Contact
                </h2>
                <p className="text-muted-foreground">
                    Questions about these Terms may be directed through the Platform&apos;s contact mechanisms or official channels.
                </p>
            </section>
        </div>
    )
}
