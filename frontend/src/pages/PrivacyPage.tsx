/**
 * Privacy by Design — trust page.
 *
 * Explains how privacy is enforced technically and by design.
 * Separate from Consent Explained; see also Privacy Policy for legal posture.
 */

export function PrivacyPage() {
    return (
        <div className="py-8 px-4 max-w-3xl mx-auto">
            <h1 className="text-3xl font-bold text-foreground mb-6">
                Privacy by Design
            </h1>

            <section className="mb-8 p-4 rounded-lg border-2 border-primary/30 bg-primary/5">
                <h2 className="text-xl font-semibold text-foreground mb-3">
                    TL;DR
                </h2>
                <p className="text-muted-foreground mb-3">
                    ASA Self-Hosted is designed to know <strong>as little as possible</strong>, even when consent is granted.
                </p>
                <ul className="list-disc pl-6 space-y-1 text-muted-foreground mb-3">
                    <li>Only aggregate and opt-in data may be collected (with consent).</li>
                    <li>We never collect: chat logs, inventory, tribe data, EOS session data, character saves.</li>
                    <li>Privacy is enforced by in-game auth, time-limited commands, and local consent state.</li>
                    <li>This page explains how we enforce it; a separate Privacy Policy covers legal posture.</li>
                </ul>
                <p className="text-muted-foreground">
                    The platform cannot expand data collection without new, explicit in-game consent.
                </p>
            </section>

            <section className="space-y-4 mb-8">
                <h2 className="text-xl font-semibold text-foreground">
                    Principle
                </h2>
                <p className="text-muted-foreground">
                    ASA Self-Hosted is designed to collect <strong>as little player data as possible</strong>, even when consent is granted.
                </p>
                <p className="text-muted-foreground">
                    Privacy is enforced through:
                </p>
                <ul className="list-disc pl-6 space-y-1 text-muted-foreground">
                    <li>Explicit consent requirements</li>
                    <li>Data minimization</li>
                    <li>Technical constraints that limit scope</li>
                </ul>
            </section>

            <section className="space-y-4 mb-8">
                <h2 className="text-xl font-semibold text-foreground">
                    What may be collected (with consent)
                </h2>
                <p className="text-muted-foreground">
                    Only at a high level, and only when explicitly enabled:
                </p>
                <ul className="list-disc pl-6 space-y-1 text-muted-foreground">
                    <li>Aggregate player counts</li>
                    <li>Optional player session duration (opt-in)</li>
                    <li>Optional hashed identifiers (opt-in)</li>
                    <li>Optional public profile display (opt-in)</li>
                </ul>
                <p className="text-muted-foreground">
                    No data is collected without the required consents.
                </p>
            </section>

            <section className="space-y-4 mb-8">
                <h2 className="text-xl font-semibold text-foreground">
                    What is never collected
                </h2>
                <p className="text-muted-foreground">
                    ASA Self-Hosted does not collect:
                </p>
                <ul className="list-disc pl-6 space-y-1 text-muted-foreground">
                    <li>Chat logs</li>
                    <li>Inventory contents</li>
                    <li>Tribe data</li>
                    <li>EOS session data</li>
                    <li>Character save files</li>
                </ul>
                <p className="text-muted-foreground">
                    These categories are outside the platform&apos;s scope by design.
                </p>
            </section>

            <section className="space-y-4 mb-8">
                <h2 className="text-xl font-semibold text-foreground">
                    How privacy is enforced
                </h2>
                <p className="text-muted-foreground">
                    Privacy is enforced through:
                </p>
                <ul className="list-disc pl-6 space-y-1 text-muted-foreground">
                    <li>In-game authorization requirements</li>
                    <li>Time-limited consent commands</li>
                    <li>Locally stored consent state</li>
                    <li>Cryptographic verification of permissions</li>
                </ul>
                <p className="text-muted-foreground">
                    The platform cannot expand data collection without new, explicit in-game consent.
                </p>
            </section>

            <section className="space-y-2 text-sm text-muted-foreground">
                <h2 className="text-lg font-semibold text-foreground">
                    Relationship to the Privacy Policy
                </h2>
                <p>
                    This page explains <strong>how privacy is enforced technically and by design</strong>.
                </p>
                <p>
                    A separate Privacy Policy defines the platform&apos;s legal posture.
                </p>
                <p>
                    Both documents must agree, and neither may contradict the other.
                </p>
            </section>
        </div>
    )
}
