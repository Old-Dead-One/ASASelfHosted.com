/**
 * Consent Explained — trust page.
 *
 * Explains that data collection requires explicit, in-game consent.
 * Content must match platform and plugin behavior; no future promises.
 * Sprint 8: consent state indicator and assurance copy.
 */

import { useConsentState } from '@/hooks/useConsentState'
import { useAuth } from '@/contexts/AuthContext'

export function ConsentPage() {
    const { isAuthenticated } = useAuth()
    const { data: consentState } = useConsentState()

    return (
        <div className="py-8 px-4 max-w-3xl mx-auto">
            <h1 className="text-3xl font-bold text-foreground mb-6">
                Consent Explained
            </h1>

            <p className="text-muted-foreground mb-6 font-medium">
                Nothing is collected until you complete consent in-game. The platform cannot enable permissions remotely or collect data by default.
            </p>

            {isAuthenticated && consentState && (
                <p className="text-sm text-muted-foreground mb-6" title="Inactive = no data collected; Partial = server eligible, player consent pending; Active = both agreed.">
                    Your consent state: <span className="font-medium capitalize">{consentState.consent_state}</span>
                </p>
            )}

            <section className="mb-8 p-4 rounded-lg border-2 border-primary/30 bg-primary/5">
                <h2 className="text-xl font-semibold text-foreground mb-3">
                    TL;DR
                </h2>
                <p className="text-muted-foreground mb-3">
                    ASA Self-Hosted can only collect data when a server is eligible <strong>and</strong> when players have explicitly agreed. Both must consent.
                </p>
                <ul className="list-disc pl-6 space-y-1 text-muted-foreground mb-3">
                    <li>If you did not grant permission in-game, we do not have your data.</li>
                    <li>Consent requires a generated console command run <strong>in-game</strong> (time-limited).</li>
                    <li>You can revoke consent at any time; it takes effect immediately.</li>
                    <li>The platform cannot enable permissions remotely or collect data by default.</li>
                </ul>
                <p className="text-muted-foreground">
                    Consent is enforced by software and cryptography, not policy alone.
                </p>
            </section>

            <section className="space-y-4 mb-8">
                <h2 className="text-xl font-semibold text-foreground">
                    Summary
                </h2>
                <p className="text-muted-foreground">
                    ASA Self-Hosted can only collect data when a server is eligible <strong>and</strong> when players have explicitly agreed.
                </p>
                <p className="text-muted-foreground">
                    Both the server owner and the player must consent.<br />
                    The platform cannot collect data on its own.
                </p>
                <blockquote className="pl-4 border-l-4 border-primary/50 text-foreground italic">
                    If you did not explicitly grant permission in-game, we do not have your data.
                </blockquote>
                <p className="text-muted-foreground">
                    Consent on ASA Self-Hosted is enforced by software and cryptography, not policy alone.
                </p>
            </section>

            <section className="space-y-4 mb-8">
                <h2 className="text-xl font-semibold text-foreground">
                    Why consent exists
                </h2>
                <p className="text-muted-foreground">
                    ASA Self-Hosted is designed so that data collection is <strong>never the default</strong>.
                </p>
                <p className="text-muted-foreground">
                    Consent exists to ensure that:
                </p>
                <ul className="list-disc pl-6 space-y-1 text-muted-foreground">
                    <li>Server owners control what their servers allow</li>
                    <li>Players control what data about themselves may be collected</li>
                    <li>The platform cannot silently expand scope</li>
                </ul>
            </section>

            <section className="space-y-4 mb-8">
                <h2 className="text-xl font-semibold text-foreground">
                    Dual-consent model
                </h2>
                <p className="text-muted-foreground">
                    Data collection requires agreement from <strong>both</strong> parties:
                </p>
                <h3 className="text-lg font-medium text-foreground mt-4">
                    Server owner consent
                </h3>
                <p className="text-muted-foreground">
                    Controls whether the server is eligible for any data collection at all (for example: heartbeats, optional player statistics).
                </p>
                <h3 className="text-lg font-medium text-foreground mt-4">
                    Player consent
                </h3>
                <p className="text-muted-foreground">
                    Controls whether any personal or session data about that player is collected.
                </p>
                <p className="text-muted-foreground font-medium">
                    Both must agree for collection to occur.<br />
                    If either says no, nothing is collected.
                </p>
            </section>

            <section className="space-y-4 mb-8">
                <h2 className="text-xl font-semibold text-foreground">
                    In-game authorization
                </h2>
                <p className="text-muted-foreground">
                    Consent is <strong>not</strong> granted by clicking a checkbox or visiting the website.
                </p>
                <p className="text-muted-foreground">
                    For player data, consent requires a <strong>generated console command</strong> that the player runs <strong>in-game</strong>.
                </p>
                <p className="text-muted-foreground">Key properties:</p>
                <ul className="list-disc pl-6 space-y-1 text-muted-foreground">
                    <li>Commands are time-limited</li>
                    <li>Commands must be executed during an active game session</li>
                    <li>The platform cannot grant consent on a user&apos;s behalf</li>
                </ul>
                <p className="text-muted-foreground">
                    If you did not run a consent command in-game, the platform does not have your data.
                </p>
            </section>

            <section className="space-y-4 mb-8">
                <h2 className="text-xl font-semibold text-foreground">
                    Revocation and enforcement
                </h2>
                <p className="text-muted-foreground">
                    Consent can be revoked at any time.
                </p>
                <p className="text-muted-foreground">When consent is revoked:</p>
                <ul className="list-disc pl-6 space-y-1 text-muted-foreground">
                    <li>Revocation takes effect immediately</li>
                    <li>Data stops being collected</li>
                    <li>Data stops being displayed</li>
                </ul>
                <p className="text-muted-foreground">
                    There is no retroactive or &quot;temporary&quot; buffering of data after revocation.
                </p>
            </section>

            <section className="mb-8 p-4 rounded-lg border-2 border-amber-500/50 bg-amber-500/5">
                <h2 className="text-xl font-semibold text-foreground mb-3">
                    What we cannot do
                </h2>
                <p className="text-muted-foreground mb-3">ASA Self-Hosted cannot:</p>
                <ul className="list-disc pl-6 space-y-1 text-muted-foreground">
                    <li>Enable permissions remotely</li>
                    <li>Collect data pending consent</li>
                    <li>Infer consent from UI actions (such as visiting the site)</li>
                    <li>Collect data by default</li>
                    <li>Bypass in-game authorization</li>
                </ul>
                <p className="text-muted-foreground mt-3">
                    These are technical constraints, not policy preferences.
                </p>
            </section>
        </div>
    )
}
