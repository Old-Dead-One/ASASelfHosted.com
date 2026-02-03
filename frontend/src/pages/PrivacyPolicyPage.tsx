/**
 * Privacy Policy — legal page.
 *
 * Styled consistently with Terms, Verification, Consent, and Privacy pages.
 * Linked from footer as "Legal".
 */

import { Link } from 'react-router-dom'

export function PrivacyPolicyPage() {
    return (
        <div className="py-8 px-4 max-w-3xl mx-auto">
            <h1 className="text-3xl font-bold text-foreground mb-2">
                Privacy Policy
            </h1>
            <p className="text-sm text-muted-foreground mb-6">
                ASA Self-Hosted · Effective date: [set on deploy]
            </p>
            <p className="text-sm text-muted-foreground mb-6">
                This Privacy Policy should be read together with the Consent and Privacy pages, which explain how these principles are enforced technically.
            </p>

            <section className="space-y-4 mb-8">
                <h2 className="text-xl font-semibold text-foreground">
                    1. Introduction
                </h2>
                <p className="text-muted-foreground">
                    ASA Self-Hosted (&quot;we,&quot; &quot;us,&quot; or &quot;the Platform&quot;) respects your privacy.
                </p>
                <p className="text-muted-foreground">This Privacy Policy explains:</p>
                <ul className="list-disc pl-6 space-y-1 text-muted-foreground">
                    <li>What information we may collect</li>
                    <li>How that information is used</li>
                    <li>Your rights regarding your data</li>
                </ul>
                <p className="text-muted-foreground">
                    This policy applies to your use of the ASA Self-Hosted website, services, and related tooling.
                </p>
            </section>

            <section className="space-y-4 mb-8">
                <h2 className="text-xl font-semibold text-foreground">
                    2. Scope &amp; Role
                </h2>
                <p className="text-muted-foreground">
                    ASA Self-Hosted is a directory and registry for self-hosted Ark: Survival Ascended servers.
                </p>
                <p className="text-muted-foreground">
                    We do not host game servers, control gameplay, or operate third-party services.
                </p>
                <p className="text-muted-foreground">Depending on the context, ASA Self-Hosted may act as a data controller for account-related information and a data processor for limited, consented server or player data, solely as instructed through explicit in-game authorization.</p>
            </section>

            <section className="space-y-4 mb-8">
                <h2 className="text-xl font-semibold text-foreground">
                    3. Information We Collect
                </h2>
                <h3 className="text-lg font-medium text-foreground mt-4">
                    3.1 Information Collected by Default
                </h3>
                <p className="text-muted-foreground">
                    When you create an account or use the Platform, we may collect:
                </p>
                <ul className="list-disc pl-6 space-y-1 text-muted-foreground">
                    <li>Account identifiers (such as email address)</li>
                    <li>Authentication and session metadata</li>
                    <li>Basic usage information necessary to operate the service (such as request timestamps and error logs), not behavioral tracking or profiling.</li>
                </ul>
                <h3 className="text-lg font-medium text-foreground mt-4">
                    3.2 Information Collected With Explicit Consent
                </h3>
                <p className="text-muted-foreground">
                    Additional data may be collected <strong>only when explicitly enabled</strong> and <strong>only after in-game authorization</strong>, including:
                </p>
                <ul className="list-disc pl-6 space-y-1 text-muted-foreground">
                    <li>Aggregate server player counts</li>
                    <li>Optional player session duration</li>
                    <li>Optional hashed identifiers</li>
                    <li>Optional public profile display data</li>
                </ul>
                <p className="text-muted-foreground">
                    If you did not explicitly grant permission in-game, this data is not collected.
                </p>
            </section>

            <section className="space-y-4 mb-8">
                <h2 className="text-xl font-semibold text-foreground">
                    4. Information We Do Not Collect
                </h2>
                <p className="text-muted-foreground">
                    ASA Self-Hosted does <strong>not</strong> collect:
                </p>
                <ul className="list-disc pl-6 space-y-1 text-muted-foreground">
                    <li>Chat logs</li>
                    <li>Inventory contents</li>
                    <li>Tribe data</li>
                    <li>Character save files</li>
                    <li>Epic Online Services (EOS) session data</li>
                </ul>
                <p className="text-muted-foreground">
                    These categories are outside the Platform&apos;s scope.
                </p>
            </section>

            <section className="space-y-4 mb-8">
                <h2 className="text-xl font-semibold text-foreground">
                    5. How We Use Information
                </h2>
                <p className="text-muted-foreground">Information is used to:</p>
                <ul className="list-disc pl-6 space-y-1 text-muted-foreground">
                    <li>Operate and maintain the Platform</li>
                    <li>Display directory listings and server status</li>
                    <li>Provide optional features you have enabled</li>
                    <li>Ensure platform security and integrity</li>
                </ul>
                <p className="text-muted-foreground">
                    We do not sell personal data.
                </p>
            </section>

            <section className="space-y-4 mb-8">
                <h2 className="text-xl font-semibold text-foreground">
                    6. Consent &amp; Revocation
                </h2>
                <p className="text-muted-foreground">
                    Certain data collection requires explicit, in-game consent.
                </p>
                <p className="text-muted-foreground">Consent:</p>
                <ul className="list-disc pl-6 space-y-1 text-muted-foreground">
                    <li>Is optional</li>
                    <li>Is time-bound</li>
                    <li>May be revoked at any time</li>
                </ul>
                <p className="text-muted-foreground">When consent is revoked:</p>
                <ul className="list-disc pl-6 space-y-1 text-muted-foreground">
                    <li>Revocation does not trigger retroactive collection or backfilling of data</li>
                    <li>Data collection stops immediately</li>
                    <li>Data is no longer displayed</li>
                </ul>
                <p className="text-muted-foreground">
                    Details of consent enforcement are described on the <Link to="/consent" className="text-primary hover:text-accent transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-ring rounded px-0.5">Consent</Link> and <Link to="/privacy" className="text-primary hover:text-accent transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-ring rounded px-0.5">Privacy</Link> pages.
                </p>
            </section>

            <section className="space-y-4 mb-8">
                <h2 className="text-xl font-semibold text-foreground">
                    7. Data Sharing
                </h2>
                <p className="text-muted-foreground">
                    We do not share personal data with third parties except:
                </p>
                <ul className="list-disc pl-6 space-y-1 text-muted-foreground">
                    <li>When required to operate the Platform (e.g., infrastructure providers)</li>
                    <li>When required by law</li>
                </ul>
                <p className="text-muted-foreground">
                    Any service providers are bound by confidentiality and data protection obligations.
                </p>
            </section>

            <section className="space-y-4 mb-8">
                <h2 className="text-xl font-semibold text-foreground">
                    8. Data Retention
                </h2>
                <p className="text-muted-foreground">
                    We retain data only as long as necessary to:
                </p>
                <ul className="list-disc pl-6 space-y-1 text-muted-foreground">
                    <li>Provide the Platform</li>
                    <li>Comply with legal obligations</li>
                    <li>Resolve disputes</li>
                    <li>Enforce agreements</li>
                </ul>
                <p className="text-muted-foreground">
                    Retention periods vary by data type and consent status.
                </p>
            </section>

            <section className="space-y-4 mb-8">
                <h2 className="text-xl font-semibold text-foreground">
                    9. Your Rights
                </h2>
                <p className="text-muted-foreground">
                    Depending on your jurisdiction, you may have rights including:
                </p>
                <ul className="list-disc pl-6 space-y-1 text-muted-foreground">
                    <li>Access to your data</li>
                    <li>Correction of inaccurate data</li>
                    <li>Deletion of your data</li>
                    <li>Restriction or objection to processing</li>
                    <li>Request a copy of personal data we hold, where applicable</li>
                </ul>
                <p className="text-muted-foreground">
                    See Section 13 (How to contact) and the <Link to="/data-rights" className="text-primary hover:text-accent transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-ring rounded px-0.5">Data Rights Request</Link> page.
                </p>
            </section>

            <section className="space-y-4 mb-8">
                <h2 className="text-xl font-semibold text-foreground">
                    10. Security
                </h2>
                <p className="text-muted-foreground">
                    We use reasonable technical and organizational measures to protect information, including:
                </p>
                <ul className="list-disc pl-6 space-y-1 text-muted-foreground">
                    <li>Access controls</li>
                    <li>Encryption where appropriate</li>
                    <li>Separation of privileges</li>
                </ul>
                <p className="text-muted-foreground">
                    No system is completely secure, and we cannot guarantee absolute security.
                </p>
            </section>

            <section className="space-y-4 mb-8">
                <h2 className="text-xl font-semibold text-foreground">
                    11. International Users
                </h2>
                <p className="text-muted-foreground">
                    Your information may be processed in jurisdictions different from your own.
                </p>
                <p className="text-muted-foreground">
                    By using the Platform, you consent to such processing where permitted by law.
                </p>
            </section>

            <section className="space-y-4 mb-8">
                <h2 className="text-xl font-semibold text-foreground">
                    12. Changes to This Policy
                </h2>
                <p className="text-muted-foreground">
                    We may update this Privacy Policy from time to time.
                </p>
                <p className="text-muted-foreground">
                    Material changes will be reflected by updating the effective date.
                </p>
                <p className="text-muted-foreground">
                    Where required by law, we will provide additional notice of material changes to this policy.
                </p>
                <p className="text-muted-foreground">
                    Continued use of the Platform constitutes acceptance of the updated policy.
                </p>
            </section>

            <section className="space-y-4 mb-8">
                <h2 className="text-xl font-semibold text-foreground">
                    13. How to Contact
                </h2>
                <p className="text-muted-foreground">
                    For questions about this policy, data rights requests (access, correction, deletion), or other inquiries, use the <Link to="/contact" className="text-primary hover:text-accent transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-ring rounded px-0.5">Contact</Link> page. For a dedicated flow to submit a data rights request, see the <Link to="/data-rights" className="text-primary hover:text-accent transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-ring rounded px-0.5">Data Rights Request</Link> page. We may need to verify your identity before fulfilling a data-rights request.
                </p>
            </section>

            <section className="space-y-4 mb-8">
                <h2 className="text-xl font-semibold text-foreground">
                    14. Data Protection Rights (GDPR &amp; CCPA)
                </h2>
                <p className="text-muted-foreground">
                    Depending on your location, you may have specific rights regarding your personal data.
                </p>
                <h3 className="text-lg font-medium text-foreground mt-4">
                    14.1 GDPR (European Union)
                </h3>
                <p className="text-muted-foreground">
                    If you are located in the European Union, you may have the right to:
                </p>
                <ul className="list-disc pl-6 space-y-1 text-muted-foreground">
                    <li>Access the personal data we hold about you</li>
                    <li>Request correction of inaccurate or incomplete data</li>
                    <li>Request deletion of your personal data</li>
                    <li>Withdraw consent where processing is based on consent</li>
                    <li>Object to or restrict certain processing</li>
                </ul>
                <p className="text-muted-foreground">
                    These rights apply only to personal data we actually collect.
                    If data was never collected, there is nothing to access or delete.
                </p>
                <h3 className="text-lg font-medium text-foreground mt-4">
                    14.2 CCPA (California, United States)
                </h3>
                <p className="text-muted-foreground">
                    If you are a California resident, you may have the right to:
                </p>
                <ul className="list-disc pl-6 space-y-1 text-muted-foreground">
                    <li>Know what personal data we collect and how it is used</li>
                    <li>Request deletion of personal data</li>
                    <li>Opt out of the sale of personal data</li>
                </ul>
                <p className="text-muted-foreground">
                    ASA Self-Hosted does <strong>not</strong> sell personal data.
                </p>
                <p className="text-muted-foreground">
                    You will not be discriminated against for exercising your rights.
                </p>
                <p className="text-muted-foreground">
                    To exercise these rights, see Section 13 (How to contact).
                </p>
                <h3 className="text-lg font-medium text-foreground mt-4">
                    14.3 Limitations
                </h3>
                <p className="text-muted-foreground">
                    Your rights apply only to personal data processed by ASA Self-Hosted.
                </p>
                <p className="text-muted-foreground">We cannot access or modify data stored by:</p>
                <ul className="list-disc pl-6 space-y-1 text-muted-foreground">
                    <li>Game servers</li>
                    <li>Hosting providers</li>
                    <li>Third-party platforms</li>
                </ul>
            </section>
        </div>
    )
}
