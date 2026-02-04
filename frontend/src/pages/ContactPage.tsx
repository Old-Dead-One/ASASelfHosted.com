/**
 * Contact page.
 *
 * Mailto and support email. Linked from Privacy Policy (Section 13), Data Rights, FAQ, Footer, Terms.
 * Handling flow documented in docs/CONTACT.md.
 */

const SUPPORT_EMAIL = 'support@asaselfhosted.com'

export function ContactPage() {
    return (
        <div className="py-8 px-4 max-w-3xl mx-auto">
            <h1 className="text-3xl font-bold text-foreground mb-2">
                Contact
            </h1>
            <p className="text-sm text-muted-foreground mb-6">
                Get in touch with ASA Self-Hosted.
            </p>
            <section className="space-y-4">
                <p className="text-muted-foreground">
                    For questions about the Privacy Policy, data rights requests (access, correction, deletion), or other inquiries, contact us by email.
                </p>
                <p className="text-muted-foreground">
                    <a
                        href={`mailto:${SUPPORT_EMAIL}`}
                        className="text-primary hover:text-accent underline focus:outline-none focus-visible:ring-2 focus-visible:ring-ring rounded"
                    >
                        {SUPPORT_EMAIL}
                    </a>
                </p>
                <p className="text-sm text-muted-foreground">
                    We may need to verify your identity before fulfilling a data-rights request. Where messages go, who reviews them, and retention are described in our contact handling documentation.
                </p>
            </section>
        </div>
    )
}
